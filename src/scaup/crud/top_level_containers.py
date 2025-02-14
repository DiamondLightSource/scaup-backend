from fastapi import HTTPException, status
from sqlalchemy import func, insert, select

from ..models.inner_db.tables import Shipment, TopLevelContainer
from ..models.top_level_containers import OptionalTopLevelContainer, TopLevelContainerIn
from ..utils.crud import assert_not_booked, edit_item
from ..utils.database import inner_db, paginate
from ..utils.external import ExternalRequest
from ..utils.session import retry_if_exists


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
    if params.code:
        _check_fields(params, token, shipmentId)
    elif params.type == "dewar" and autocreate:
        # Automatically register dewar if no code is provided
        # The range is 0999 to 9900 because these are DLS-BI barcodes guaranteed to be available to our application
        last_dewar = inner_db.session.scalar(
            select(TopLevelContainer.code)
            .filter(TopLevelContainer.code > DEWAR_PREFIX + "0999", TopLevelContainer.code < DEWAR_PREFIX + "9900")
            .order_by(TopLevelContainer.code.desc())
        )

        dewar_number = int(last_dewar.split("-")[2]) if last_dewar is not None else 999
        new_code = f"{DEWAR_PREFIX}{dewar_number + 1:04}"

        proposal_reference = inner_db.session.scalar(
            select(func.concat(Shipment.proposalCode, Shipment.proposalNumber)).filter(Shipment.id == shipmentId)
        )

        ext_resp = ExternalRequest.request(
            token,
            method="POST",
            url=f"/proposals/{proposal_reference}/dewar-registry",
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

    inner_db.session.commit()
    return container


def edit_top_level_container(topLevelContainerId: int, params: OptionalTopLevelContainer, token: str):
    _check_fields(params, token, topLevelContainerId)
    return edit_item(TopLevelContainer, params, topLevelContainerId, token)


def get_top_level_containers(shipmentId: int, limit: int, page: int):
    query = select(TopLevelContainer).filter(TopLevelContainer.shipmentId == shipmentId).join(Shipment)

    return paginate(query, limit, page, slow_count=False, scalar=False)
