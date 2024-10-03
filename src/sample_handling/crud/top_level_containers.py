from datetime import date

import qrcode
from fastapi import HTTPException, status
from fpdf import FPDF
from fpdf.fonts import FontFace
from sqlalchemy import Row, func, insert, select

from ..assets.paths import CUT_HERE, DIAMOND_LOGO, THIS_SIDE_UP
from ..models.inner_db.tables import Shipment, TopLevelContainer
from ..models.top_level_containers import OptionalTopLevelContainer, TopLevelContainerIn
from ..utils.crud import assert_not_booked, edit_item
from ..utils.database import inner_db, paginate, unravel
from ..utils.external import ExternalRequest
from ..utils.session import insert_context

headings_style = FontFace(emphasis=None)
bold_style = FontFace(emphasis="BOLD")


def _check_fields(
    params: TopLevelContainerIn | OptionalTopLevelContainer,
    token: str,
    item_id: int | None = None,
):
    if item_id is None:
        return

    query = select(func.concat(Shipment.proposalCode, Shipment.proposalNumber))

    if isinstance(params, TopLevelContainerIn):
        # Used on creation, when we don't have a top level container ID to join against yet
        query = query.filter(Shipment.id == item_id)
    else:
        if params.code is None:
            # Perform no facility code check if code is not present
            return

        query = query.select_from(TopLevelContainer).filter(TopLevelContainer.id == item_id).join(Shipment)

    proposal_reference = inner_db.session.scalar(query)

    if proposal_reference is not None:
        code_response = ExternalRequest.request(
            token=token,
            url=f"/proposals/{proposal_reference}/dewar-registry/{params.code}",
        )

        if code_response.status_code == 200:
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Invalid facility code provided",
    )


@assert_not_booked
def create_top_level_container(shipmentId: int | None, params: TopLevelContainerIn, token: str):
    with insert_context():
        if params.code:
            _check_fields(params, token, shipmentId)

        if not params.name:
            params.name = params.code

        container = inner_db.session.scalar(
            insert(TopLevelContainer).returning(TopLevelContainer),
            {"shipmentId": shipmentId, **params.model_dump(exclude_unset=True)},
        )

        inner_db.session.commit()
        return container


def edit_top_level_container(topLevelContainerId: int, params: OptionalTopLevelContainer, token: str):
    _check_fields(params, token, topLevelContainerId)
    return edit_item(TopLevelContainer, params, topLevelContainerId, token)


def get_top_level_containers(shipmentId: int, limit: int, page: int):
    query = (
        select(*unravel(TopLevelContainer), Shipment.status.label("status"))
        .filter(TopLevelContainer.shipmentId == shipmentId)
        .join(Shipment)
    )

    return paginate(query, limit, page, slow_count=False)


class TrackingLabelPages(FPDF):
    def __init__(self, location: str, local_contact: str):
        super().__init__()
        self.set_font("helvetica", size=14)
        self.location = location
        self.local_contact = local_contact

    def add_dewar(self, dewar: Row):
        if dewar.barCode is None or dewar.externalId is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shipment out of sync with ISPyB",
            )

        qr_img = qrcode.make(dewar.barCode, error_correction=1)
        img = qr_img.get_image()

        table = (
            ("Proposal", f"{dewar.proposalCode}{dewar.proposalNumber}-{dewar.visitNumber or "?"}"),
            ("Shipment", dewar.name),
            ("Label", dewar.code),
            ("Instrument", self.location),
            ("Local Contact", self.local_contact),
            ("Printed", str(date.today())),
        )

        self.add_page()
        self.image(CUT_HERE, x="L", y=140, w=194)

        for offset in [10, 155]:
            self.image(DIAMOND_LOGO, x="L", y=7 + offset, h=15)
            self.image(THIS_SIDE_UP, x="R", y=7 + offset, w=30)
            self.image(img, x=74, y=offset, h=60, w=60)
            self.set_y(55 + offset)

            with self.table(borders_layout="HORIZONTAL_LINES", headings_style=headings_style) as pdf_table:
                for row in table:
                    pdf_row = pdf_table.row()
                    for i, datum in enumerate(row):
                        pdf_row.cell(datum, style=bold_style if i == 0 else None)


def get_shipping_labels(shipment_id: int, token: str):
    data = inner_db.session.execute(
        select(
            TopLevelContainer.externalId,
            TopLevelContainer.barCode,
            TopLevelContainer.code,
            Shipment.name,
            Shipment.proposalCode,
            Shipment.proposalNumber,
            Shipment.visitNumber,
        )
        .filter(Shipment.id == shipment_id)
        .join(TopLevelContainer)
    ).all()

    if len(data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No top level containers in shipment",
        )

    expeye_response = ExternalRequest.request(
        token=token,
        module="/core",
        url=f"/proposals/{data[0].proposalCode}{data[0].proposalNumber}/sessions/{data[0].visitNumber}",
    )

    current_session = expeye_response.json()

    # Microauth should have already checked that the session exists
    assert "beamLineName" in current_session

    pdf = TrackingLabelPages(current_session["beamLineName"], current_session["beamLineOperator"])
    for dewar in data:
        pdf.add_dewar(dewar)

    return pdf.output()
