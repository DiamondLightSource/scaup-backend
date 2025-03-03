from datetime import date, datetime
from typing import Sequence

import qrcode
from fastapi import HTTPException, Response, status
from fpdf import FPDF
from fpdf.fonts import FontFace
from sqlalchemy import Row, select
from sqlalchemy.orm import contains_eager

from ..assets.paths import (
    CUT_HERE,
    DEJAVU_SANS,
    DEJAVU_SANS_BOLD,
    DIAMOND_LOGO,
    THIS_SIDE_UP,
)
from ..models.inner_db.tables import (
    PreSession,
    Sample,
    Shipment,
    TopLevelContainer,
)
from ..utils.database import inner_db
from ..utils.external import ExternalRequest
from ..utils.generic import pascal_to_title

headings_style = FontFace(emphasis=None)
bold_style = FontFace(emphasis="BOLD")

UNITS = {
    "pixelSize": " Å/px",
    "totalDose": " e-/Å²",
    "dosePerFrame": " e⁻/Å²",
    "tiltSpan": "°",
    "startAngle": "°",
    "tiltStep": "°",
}


def _add_unit(key: str, val: str | bool | int | float):
    """Convert value to string and append unit if applicable"""
    new_val = val if type(val) is not bool else "Yes" if val else "No"
    if key in UNITS and val != "":
        return f"{new_val}{UNITS[key]}"
    return new_val


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
            (
                "Proposal",
                f"{dewar.proposalCode}{dewar.proposalNumber}-{dewar.visitNumber or "?"}",
            ),
            ("Sample Collection", dewar.name),
            ("Code", dewar.code),
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

            with self.table(
                borders_layout="HORIZONTAL_LINES", headings_style=headings_style
            ) as pdf_table:
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
        url=f"/proposals/{data[0].proposalCode}{data[0].proposalNumber}/sessions/{data[0].visitNumber}",
    )

    current_session = expeye_response.json()

    # Microauth should have already checked that the session exists
    assert "beamLineName" in current_session

    pdf = TrackingLabelPages(
        current_session["beamLineName"], current_session["beamLineOperator"]
    )
    for dewar in data:
        pdf.add_dewar(dewar)

    return pdf.output()


class ReportPDF(FPDF):
    def __init__(self, shipment: Shipment):
        super().__init__(orientation="landscape")
        self.shipment = shipment
        self.add_font(fname=DEJAVU_SANS)
        self.add_font(fname=DEJAVU_SANS_BOLD, family="dejavusans", style="B")
        self.set_font("DejaVuSans", size=10)

    def header(self):
        self.set_font("DejaVuSans", style="B", size=18)
        self.cell(
            text=(
                f"{self.shipment.name} ({self.shipment.proposalCode}{self.shipment.proposalNumber}"
                + f"-{self.shipment.visitNumber})"
            ),
            w=0,
        )
        self.image(DIAMOND_LOGO, x="R", y=7, h=12)
        self.line(y1=20, y2=21, x1=5, x2=self.w - 5)
        self.ln(21)

    def footer(self):
        self.set_xy(5, -8)
        self.cell(text=f"Printed on {datetime.now().strftime("%d/%m/%Y %H:%M")}")

    def add_table(
        self,
        table_contents: Sequence[tuple[str, ...]],
        width: int = 100,
        caption: str = "Table",
        col_widths: tuple | None = None
    ):
        self.set_font("DejaVuSans", style="B", size=10)
        self.cell(w=width, text=caption, new_x="START", new_y="NEXT", h=10.5)
        self.set_font("DejaVuSans", style="", size=9)
        with self.table(width=width, first_row_as_headings=False, align="L", col_widths=col_widths) as table:
            for data_row in table_contents:
                row = table.row()
                for datum in data_row:
                    row.cell(datum)


def generate_report(shipment_id: int, token: str):
    shipment = inner_db.session.scalar(
        select(Shipment).filter(Shipment.id == shipment_id)
    )

    expeye_response = ExternalRequest.request(
        token=token,
        url=f"/proposals/{shipment.proposalCode}{shipment.proposalNumber}/sessions/{shipment.visitNumber}",
    )

    if expeye_response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    ispyb_session = expeye_response.json()

    session_table = [
        ("Start Date", ispyb_session["startDate"]),
        ("End Date", ispyb_session["endDate"]),
        ("Local Contact", ispyb_session["beamLineOperator"]),
        ("TEM", ispyb_session["beamLineName"]),
        ("Camera", ""),
        ("Software", ""),
    ]

    grids = inner_db.session.scalars(
        select(Sample)
        .join(Sample.container)
        .filter(Sample.shipmentId == shipment_id)
        .options(contains_eager(Sample.container))
        .order_by(Sample.container, Sample.location)
    )

    # TODO: rethink this once we're using user-provided templates
    grids_table = [
        ("Gridbox", "Position", "Autoloader Slot", "Foil", "Hole", "Comments"),
        *[("",) * 6] * 12,
    ]

    current_row = 1

    for grid in grids:
        if not hasattr(grid, "container"):
            continue
        grids_table[current_row] = (
            str(grid.container.name),
            str(grid.location),
            str(grid.subLocation),
            str(grid.details["foil"]),
            str(grid.details["hole"]),
            str(grid.comments),
        )
        current_row += 1

    pre_session = inner_db.session.scalar(
        select(PreSession).filter(PreSession.shipmentId == shipment_id)
    )

    if pre_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pre-session found in sample collection",
        )

    # TODO: rethink this once we're using user-provided templates
    pre_session_table = [
        (pascal_to_title(key), _add_unit(key, value))
        for key, value in pre_session.details.items()
    ]

    pdf = ReportPDF(shipment)
    pdf.add_page()

    pdf.set_xy(x=5, y=20)
    pdf.add_table(session_table, width=100, caption="Session")

    pdf.set_xy(x=110, y=20)
    pdf.add_table(grids_table, width=182, caption="Grids", col_widths=(2,1,2,3,1,2))

    pdf.set_xy(x=5, y=70)
    pdf.add_table(pre_session_table, width=100, caption="Data Collection Parameters")

    headers = {
        "Content-Disposition": (
            "inline;"
            + f'filename="report-{shipment.proposalCode}{shipment.proposalNumber}-{shipment.visitNumber}.pdf"'
        )
    }
    return Response(
        bytes(pdf.output()),
        headers=headers,
        media_type="application/pdf",
    )
