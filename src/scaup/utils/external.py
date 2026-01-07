from datetime import datetime
from typing import List

import requests
from fastapi import HTTPException, status
from lims_utils.logging import app_logger
from sqlalchemy import func, select, update

from ..models.containers import ContainerExternal
from ..models.inner_db.tables import (
    AvailableTable,
    Container,
    Sample,
    Shipment,
    TopLevelContainer,
)
from ..models.samples import SampleExternal
from ..models.shipments import ShipmentExternal, ShipmentOut
from ..models.top_level_containers import TopLevelContainerExternal
from ..utils.database import inner_db
from ..utils.models import OrmBaseModel
from .config import Config

TYPE_TO_SHIPPING_SERVICE_TYPE = {
    "sample": "CRYO_EM_GRID",
    "grid": "CRYO_EM_GRID",
    "gridBox": "CRYO_EM_GRID_BOX",
    "puck": "UNI_PUCK",
    "dewar": "CRYOGENIC_DRY_SHIPPER_CASE",
    "falconTube": "FALCON_TUBE_50ML",
}


# TODO: possibly replace this with middleware, or httpx client instances
class ExternalRequest:
    @staticmethod
    def request(
        token,
        base_url=Config.ispyb_api.url,
        *args,
        **kwargs,
    ):
        """Wrapper for request object. Since the URL is validated before any
        auth actions happen, we cannot wrap this in a custom auth implementation,
        we must do all the preparation work before the actual request."""

        kwargs["url"] = f"{base_url}{kwargs['url']}"
        kwargs["method"] = kwargs.get("method", "GET")
        kwargs["headers"] = {"Authorization": f"Bearer {token}"}

        return requests.request(**kwargs)


def _get_resource_from_ispyb(token: str, url: str):
    response = ExternalRequest.request(token, url=url)

    if response.status_code != 200:
        app_logger.error(
            (
                f"Failed getting session information from ISPyB at URL {url}, service returned "
                f"{response.status_code}: {response.text}"
            )
        )

        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="Received invalid response from upstream service",
        )

    return response.json()


class ExternalObject:
    """Object representing a link to the ISPyB instance of the object"""

    item_body: OrmBaseModel = OrmBaseModel()
    external_link_prefix = ""
    external_key = ""
    url = ""
    to_exclude: set[str] = set()

    def __init__(
        self,
        token: str,
        item: AvailableTable,
        item_id: int | str | None,
        root_id: int | None = None,
    ):
        match item:
            case Shipment():
                self.url = f"/proposals/{item_id}/shipments"
                self.external_link_prefix = "/shipments/"
                self.item_body = ShipmentExternal.model_validate(item)
                self.external_key = "shippingId"
            case Container():
                if item.topLevelContainerId:
                    self.url = f"/dewars/{item_id}/containers"
                else:
                    self.url = f"/containers/{item_id}/containers"
                self.external_link_prefix = "/containers/"

                # This is better than destructuring the original container object twice
                self.item_body = ContainerExternal.model_validate(item)
                self.item_body.sessionId = root_id
                self.external_key = "containerId"
            case TopLevelContainer():
                self.url = f"/shipments/{item_id}/dewars"
                self.external_link_prefix = "/dewars/"
                self.item_body = TopLevelContainerExternal.model_validate(item)

                shipment = inner_db.session.execute(
                    select(
                        func.concat(Shipment.proposalCode, Shipment.proposalNumber).label("proposal"),
                        Shipment.visitNumber,
                    ).filter(Shipment.id == item.shipmentId)
                ).one()

                # When creating the dewar in ISPyB, since ISPyB has no concept of shipments belonging to sessions,
                # dewars have to be assigned to sessions instead, and this is done through the firstExperimentId
                # column, which despite the cryptic name, points to the BLSession table.
                if item.externalId is None:
                    session = _get_resource_from_ispyb(
                        token,
                        f"/proposals/{shipment.proposal}/sessions/{shipment.visitNumber}",
                    )
                    self.item_body.firstExperimentId = session["sessionId"]
                else:
                    self.to_exclude = {"firstExperimentId"}

                # We store the dewar's facility code, but not the numeric dewar registry ID that ISPyB also expects.
                # Even though the alphanumeric code is a primary key in the DewarRegistry table, the dewar table still
                # expects a numeric dewarRegistryId which is used in some systems.
                # Since the facility code can be changed by the user, we need to update this even if it was already
                # pushed to ISPyB
                dewar_reg = _get_resource_from_ispyb(
                    token, f"/proposals/{shipment.proposal}/dewar-registry/{item.code}"
                )

                self.item_body.dewarRegistryId = dewar_reg["dewarRegistryId"]
                self.external_key = "dewarId"
            case Sample():
                if item_id is None:
                    self.url = "/samples"
                else:
                    self.url = f"/containers/{item_id}/samples"

                self.external_link_prefix = "/samples/"
                self.item_body = SampleExternal.model_validate(item)
                self.external_key = "blSampleId"
            case _:
                raise NotImplementedError()


class Expeye:
    @classmethod
    def upsert(
        cls,
        token: str,
        item: AvailableTable,
        parent_id: int | str | None,
        root_id: int | None = None,
    ):
        """Insert existing item in ISPyB or patch it

        Args:
            item: Item to be pushed
            parent_id: External ID of the item's parent
            root_id: ID of the root of the item tree, such as a session ID

        Returns:
            External link and external ID"""

        ext_obj = ExternalObject(token, item, parent_id, root_id)
        method = "POST"

        if item.externalId:
            ext_obj.url = f"{ext_obj.external_link_prefix}{item.externalId}"
            method = "PATCH"

        # There is no way of verifying orphan sample ownership in ISPyB, so we need to use SCAUP's
        # token instead to create them on behalf of SCAUP, which has permission to manipulate all samples.
        # TODO: revisit this when SCAUP creates containers, dewars and shipments for orphan samples
        response = ExternalRequest.request(
            Config.ispyb_api.jwt,
            method=method,
            url=ext_obj.url,
            json=ext_obj.item_body.model_dump(mode="json", exclude=ext_obj.to_exclude),
        )

        if response.status_code not in [201, 200]:
            detail = "No valid JSON body returned from upstream service"

            try:
                detail = response.json().get("detail", "No detail provided")
            except requests.JSONDecodeError:
                pass

            app_logger.error(
                f"Failed pushing to ISPyB at URL {ext_obj.url}, service returned {response.status_code}: {detail}"
            )

            raise HTTPException(
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
                detail="Received invalid response from upstream service",
            )

        external_id = response.json()[ext_obj.external_key]

        return {
            "externalId": external_id,
            "link": "".join([Config.ispyb_api.url, ext_obj.external_link_prefix, str(external_id)]),
        }


def update_shipment_status(shipment: ShipmentOut, token: str, commit: bool = True):
    """Update shipment status by fetching updates from ISPyB, and return updated
    shipment

    Args:
        shipments: Shipment to update status for
        token: User token

    Returns:
        Updated shipment"""
    update_delta = datetime.now(tz=shipment.lastStatusUpdate.tzinfo) - shipment.lastStatusUpdate

    age_delta = (
        datetime.now(tz=shipment.lastStatusUpdate.tzinfo) - shipment.creationDate if shipment.creationDate else None
    )

    validated_shipment = ShipmentOut.model_validate(shipment, from_attributes=True)

    if (
        not shipment.externalId
        # Check if last updated was more than 10 minutes ago
        or update_delta.total_seconds() < 600
        # Check if older than 3 months
        or not age_delta
        or age_delta.total_seconds() > 7776000
    ):
        return validated_shipment

    response = ExternalRequest.request(token=token, url=f"/shipments/{shipment.externalId}")

    if response.status_code != 200:
        app_logger.warning(
            "Failed to get status from ISPyB for shipment %i (external ID: %i): %s",
            validated_shipment.id,
            validated_shipment.externalId,
            response.text,
        )

        return validated_shipment

    external_shipment = response.json()
    new_shipment = inner_db.session.execute(
        update(Shipment)
        .returning(Shipment)
        .filter(Shipment.id == validated_shipment.id)
        .values(
            {
                "status": external_shipment["shippingStatus"],
                "lastStatusUpdate": datetime.now(tz=shipment.lastStatusUpdate.tzinfo),
            }
        )
    ).scalar_one()

    if not commit:
        inner_db.session.commit()

    return ShipmentOut.model_validate(new_shipment, from_attributes=True)


def update_shipment_statuses(shipments: List[ShipmentOut], token: str):
    """Update shipment statuses in place by fetching updates from ISPyB, and return updated
    shipment list

    Args:
        shipments: Shipments to update statuses for
        token: User token

    Returns:
        Updated shipments"""
    for i, shipment in enumerate(shipments):
        shipments[i] = update_shipment_status(shipment, token, commit=False)

    inner_db.session.commit()

    return shipments
