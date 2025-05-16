from datetime import date, datetime
from typing import List, Sequence

import qrcode
from fastapi import HTTPException, Response, status
from fpdf import FPDF
from fpdf.fonts import FontFace
from lims_utils.logging import app_logger
from sqlalchemy import Row, select
from sqlalchemy.orm import contains_eager

from scaup.assets.text import (
    LABEL_INSTRUCTIONS_STEP_1,
    LABEL_INSTRUCTIONS_STEP_2,
    LABEL_INSTRUCTIONS_STEP_3,
    LABEL_INSTRUCTIONS_STEP_4,
)

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
from ..utils.config import Config
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


class ConsigneeAddress(object):
    """This is a class to provide a global cache for the consignee address, to prevent hitting the shipping service
    with too many redundant requests."""

    def __init__(self, consignee_cache: Sequence[str] | None = None):
        self._consignee_cache = consignee_cache

    def __call__(self, shipment_id: int, token: str):
        """Get consignee address from shipment service using shipment ID.
        Caching shouldn't be a problem unless the facility changes address/phone no./post code whilst the app
        proccess is alive.

        Args:
            shipment_id: shipment ID to get consignee for
            token: authentication token

        Returns:
            Address of consignee"""
        if self._consignee_cache:
            return self._consignee_cache

        consignee_response = ExternalRequest.request(
            base_url=Config.shipping_service.backend_url,
            token=token,
            method="GET",
            url=f"/api/shipments/{shipment_id}",
        )

        if consignee_response.status_code != 200:
            app_logger.error(
                "Failed to get consignee address for shipment %i with code %i: %s",
                shipment_id,
                consignee_response.status_code,
                consignee_response.text,
            )
            # It should not be possible for a shipment to have a "from" address and no "to" address
            # so for any given shipment request ID, it must return a valid consignee address
            raise HTTPException(
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
                detail="Failed to get consignee address from shipping service",
            )

        to_lines = [v for k, v in consignee_response.json().items() if k.startswith("consignee_") and type(v) is str]

        return to_lines


_get_consignee_address = ConsigneeAddress([])


class TrackingLabelPages(FPDF):
    def __init__(
        self,
        location: str,
        local_contact: str,
        from_lines: List[str] | None = None,
        to_lines: List[str] | None = None,
    ):
        super().__init__()
        self.set_font("helvetica", size=14)
        self.location = location
        self.local_contact = local_contact
        self.from_lines = from_lines
        self.to_lines = to_lines

        # Only display two first local contacts, to save space
        if len(lcs := local_contact.split(",")) > 2:
            self.local_contact = f"{', '.join(lcs[:2])} + {len(lcs) - 2}"

        self.add_page()

        # Label instructions
        self.image(DIAMOND_LOGO, x="L", y=7, h=15)
        self.set_font("helvetica", size=26, style="B")
        self.cell(align="R", w=0, text="Instructions", h=15, new_x="LMARGIN")

        self.set_y(30)

        self.add_instruction_title("1. Affix to dewar")
        self.add_instruction_text(LABEL_INSTRUCTIONS_STEP_1)

        self.add_instruction_title("2. Affix to dewar case")
        self.add_instruction_text(LABEL_INSTRUCTIONS_STEP_2)

        self.add_instruction_title("3. Affix airway bill to dewar case")
        self.add_instruction_text(LABEL_INSTRUCTIONS_STEP_3)

        self.add_instruction_title("4. Request return at the end of your session")
        self.add_instruction_text(LABEL_INSTRUCTIONS_STEP_4)

    def add_instruction_title(self, text: str):
        self.set_font("helvetica", size=26, style="B")
        self.cell(
            w=0,
            text=text,
            new_x="LMARGIN",
            new_y="NEXT",
            h=26,
        )

    def add_instruction_text(self, text: str):
        self.set_font("helvetica", size=14)
        self.multi_cell(
            w=0,
            h=8,
            text=text,
            new_x="LMARGIN",
            new_y="NEXT",
        )

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
                f"{dewar.proposalCode}{dewar.proposalNumber}-{dewar.visitNumber or '?'}",
            ),
            ("Sample Collection", dewar.name),
            ("Code", dewar.code),
            ("Instrument", self.location),
            ("Local Contact", self.local_contact),
            ("Printed", str(date.today())),
        )

        if self.from_lines is None:
            self.add_page()
            self.image(CUT_HERE, x="L", y=139, w=194)

        # If we don't have an address, display both labels in a single page
        offset_values = [0, 143] if self.from_lines is None else [10, 10]

        # Tracking labels
        for i, offset in enumerate(offset_values):
            if self.from_lines is not None and self.to_lines is not None:
                l_col_size = (self.epw) / 2

                self.add_page()
                self.set_y(135)

                self.set_font("helvetica", size=14, style="B")

                self.cell(
                    w=l_col_size,
                    text="User Laboratory",
                    new_x="RIGHT",
                    new_y="TOP",
                    h=14,
                )
                self.cell(
                    w=l_col_size,
                    text="Experimental Facility",
                    new_x="LMARGIN",
                    new_y="NEXT",
                    h=14,
                )

                self.set_font("helvetica", size=12)

                # Address lines
                self.multi_cell(
                    w=l_col_size,
                    padding=4,
                    border="R",
                    h=8,
                    new_x="RIGHT",
                    new_y="TOP",
                    text="\n".join(self.from_lines),
                )
                self.multi_cell(
                    w=l_col_size,
                    padding=4,
                    h=8,
                    new_x="LEFT",
                    new_y="NEXT",
                    text="\n".join(self.to_lines),
                )

            self.image(DIAMOND_LOGO, x="L", y=7 + offset, h=15)
            self.image(THIS_SIDE_UP, x="R", y=7 + offset, w=30)
            self.image(img, x=(self.w - 60) / 2, y=offset, h=55, w=55)
            self.set_y(y=54 + offset)
            self.cell(w=0, text=str(dewar.barCode), align="C")
            self.set_y(60 + offset)

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
            Shipment.shipmentRequest,
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

    from_lines: List[str] | None = None
    to_lines: List[str] | None = None

    if data[0].shipmentRequest is not None:
        response = ExternalRequest.request(
            base_url=Config.shipping_service.backend_url,
            token=token,
            method="GET",
            url=f"/api/shipment_requests/{data[0].shipmentRequest}/shipments/TO_FACILITY",
        )

        if response.status_code == 200:
            shipment_request = response.json()

            from_lines = [line for line in shipment_request["contact"].values() if line is not None]

            to_lines = _get_consignee_address(shipment_request["shipmentId"], token)

    pdf = TrackingLabelPages(
        current_session["beamLineName"],
        current_session["beamLineOperator"],
        from_lines,
        to_lines,
    )
    for dewar in data:
        pdf.add_dewar(dewar)

    headers = {
        "Content-Disposition": (
            "inline;"
            + 'filename="'
            + f'labels-{data[0].proposalCode}{data[0].proposalNumber}-{data[0].visitNumber}-{data[0].name}.pdf"'
        )
    }
    return Response(
        bytes(pdf.output()),
        headers=headers,
        media_type="application/pdf",
    )


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
        self.cell(text=f"Printed on {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    def add_table(
        self,
        table_contents: Sequence[tuple[str, ...]],
        width: int = 100,
        caption: str = "Table",
        col_widths: tuple | None = None,
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
    shipment = inner_db.session.scalar(select(Shipment).filter(Shipment.id == shipment_id))

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

    pre_session = inner_db.session.scalar(select(PreSession).filter(PreSession.shipmentId == shipment_id))

    if pre_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pre-session found in sample collection",
        )

    # TODO: rethink this once we're using user-provided templates
    pre_session_table = [(pascal_to_title(key), _add_unit(key, value)) for key, value in pre_session.details.items()]

    pdf = ReportPDF(shipment)
    pdf.add_page()

    pdf.set_xy(x=5, y=20)
    pdf.add_table(session_table, width=100, caption="Session")

    pdf.set_xy(x=110, y=20)
    pdf.add_table(grids_table, width=182, caption="Grids", col_widths=(2, 1, 2, 3, 1, 2))

    pdf.set_xy(x=5, y=70)
    pdf.add_table(pre_session_table, width=100, caption="Data Collection Parameters")

    headers = {
        "Content-Disposition": (
            "inline;" + f'filename="report-{shipment.proposalCode}{shipment.proposalNumber}-{shipment.visitNumber}.pdf"'
        )
    }
    return Response(
        bytes(pdf.output()),
        headers=headers,
        media_type="application/pdf",
    )
