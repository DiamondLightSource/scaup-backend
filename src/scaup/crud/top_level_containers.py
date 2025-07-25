from fastapi import HTTPException, status
from lims_utils.logging import app_logger
from lims_utils.models import Paged
from sqlalchemy import func, insert, select, update

from ..models.inner_db.tables import Shipment, TopLevelContainer
from ..models.top_level_containers import (
    OptionalTopLevelContainer,
    TopLevelContainerHistory,
    TopLevelContainerIn,
    TopLevelContainerOut,
)
from ..utils.config import Config
from ..utils.crud import assert_not_booked, edit_item
from ..utils.database import inner_db
from ..utils.external import ExternalRequest
from ..utils.session import retry_if_exists

DEWAR_PREFIX = "DLS-BI-1"


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
@retry_if_exists
def create_top_level_container(shipmentId: int | None, params: TopLevelContainerIn, token: str, autocreate=True):
    proposal = (
        None
        if shipmentId is None
        else inner_db.session.execute(
            select(
                func.concat(Shipment.proposalCode, Shipment.proposalNumber).label("reference"),
                Shipment.visitNumber,
            ).filter(Shipment.id == shipmentId)
        ).one()
    )

    if params.code:
        _check_fields(params, token, shipmentId)
    elif params.type == "dewar" and autocreate:
        # Automatically register dewar if no code is provided
        # The range is 0999 to 9900 because these are DLS-BI barcodes guaranteed to be available to our application
        ext_get = ExternalRequest.request(Config.ispyb_api.jwt, url=f"/dewar-registry?search={DEWAR_PREFIX}&limit=1")

        if ext_get.status_code != 200:
            app_logger.warning(
                "Error from Expeye while fetching registry entries: %s",
                ext_get.text,
            )
            raise HTTPException(
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
                detail="Invalid response while creating top level container in ISPyB",
            )

        if len(ext_get.json()["items"]) < 1:
            dewar_number = 1000
        else:
            last_dewar = int(ext_get.json()["items"][0]["facilityCode"].split("-")[2])
            dewar_number = 1000 if last_dewar < 1000 else last_dewar + 1

        new_code = f"DLS-BI-{dewar_number:04}"

        if proposal:
            ext_resp = ExternalRequest.request(
                Config.ispyb_api.jwt,
                method="POST",
                url=f"/proposals/{proposal.reference}/dewar-registry",
                json={"facilityCode": new_code},
            )

            if ext_resp.status_code != 201:
                app_logger.warning(
                    "Error from Expeye while creating dewar registry entry with code %s: %s",
                    new_code,
                    ext_resp.text,
                )
                raise HTTPException(
                    status_code=status.HTTP_424_FAILED_DEPENDENCY,
                    detail="Invalid response while creating top level container in ISPyB",
                )

        params.code = new_code

    if not params.name:
        params.name = params.code

    container = inner_db.session.scalar(
        insert(TopLevelContainer).returning(TopLevelContainer),
        {"shipmentId": shipmentId, **params.model_dump(exclude_unset=True)},
    )

    if proposal:
        bar_code = f"{proposal.reference}-{proposal.visitNumber}-{container.id:07}"

        # This is because some users expect a sequential numeric ID to make tracking how old a dewar is easier,
        # and because of historical reasons, some users are used to seeing the proposal/session number on there
        # as well, so I have to create barcodes this way.
        container = inner_db.session.scalar(
            update(TopLevelContainer).returning(TopLevelContainer).filter(TopLevelContainer.id == container.id),
            {"barCode": bar_code},
        )

    inner_db.session.commit()
    return container


def edit_top_level_container(topLevelContainerId: int, params: OptionalTopLevelContainer, token: str):
    _check_fields(params, token, topLevelContainerId)
    return edit_item(TopLevelContainer, params, topLevelContainerId, token)


def get_top_level_containers(shipmentId: int, token: str, limit: int, page: int):
    query = select(TopLevelContainer).filter(TopLevelContainer.shipmentId == shipmentId).join(Shipment)

    top_level_containers: Paged[TopLevelContainer | TopLevelContainerOut] = inner_db.paginate(
        query, limit, page, slow_count=False, scalar=False
    )

    for i, tlc in enumerate(top_level_containers.items):
        if tlc.externalId is not None:
            response = ExternalRequest.request(token=token, url=f"/dewars/{tlc.externalId}/history")

            if response.status_code == 200:
                # More than 25 items could be returned, but it is statistically unlikely
                # (less than 2.2% of dewars have 25 history items or more, and most of these
                # are commissioning proposals), so we'll disregard that for now
                new_tlc = TopLevelContainerOut.model_validate(tlc, from_attributes=True)
                new_tlc.history = [TopLevelContainerHistory.model_validate(item) for item in response.json()["items"]]

                top_level_containers.items[i] = new_tlc
            else:
                app_logger.warning(
                    "Failed to get history from ISPyB for dewar %i (external ID: %i): %s",
                    tlc.id,
                    tlc.externalId,
                    response.text,
                )

    return top_level_containers
