import requests
from fastapi import HTTPException, status
from lims_utils.logging import app_logger

from ..models.containers import ContainerExternal
from ..models.inner_db.tables import (
    AvailableTable,
    Container,
    Sample,
    Shipment,
    TopLevelContainer,
)
from ..models.samples import SampleExternal
from ..models.shipments import ShipmentExternal
from ..models.top_level_containers import TopLevelContainerExternal
from ..utils.models import OrmBaseModel
from .config import Config

TYPE_TO_SHIPPING_SERVICE_TYPE = {
    "sample": "CRYO_EM_GRID",
    "grid": "CRYO_EM_GRID",
    "gridBox": "CRYO_EM_GRID_BOX_",
    "puck": "UNI_PUCK",
    "dewar": "CRYOGENIC_DRY_SHIPPER",
    "falconTube": "FALCON_TUBE_50ML",
}


class ExternalObject:
    """Object representing a link to the ISPyB instance of the object"""

    item_body: OrmBaseModel = OrmBaseModel()
    external_link_prefix = ""
    external_key = ""
    url = ""

    def __init__(self, item: AvailableTable, item_id: int | str, root_id: int | None):
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
                self.external_key = "dewarId"
            case Sample():
                self.url = f"/containers/{item_id}/samples"
                self.external_link_prefix = "/samples/"
                self.item_body = SampleExternal.model_validate(item)
                self.external_key = "blSampleId"
            case _:
                raise NotImplementedError()


# TODO: possibly replace this with middleware, or httpx client instances
class ExternalRequest:
    @staticmethod
    def request(
        token,
        base_url=Config.ispyb_api,
        module="/sample-handling",
        *args,
        **kwargs,
    ):
        """Wrapper for request object. Since the URL is validated before any
        auth actions happen, we cannot wrap this in a custom auth implementation,
        we must do all the preparation work before the actual request."""

        kwargs["url"] = f"{base_url}{module}{kwargs['url']}"
        kwargs["method"] = kwargs.get("method", "GET")
        kwargs["headers"] = {"Authorization": f"Bearer {token}"}

        return requests.request(**kwargs, verify=False)


class Expeye:
    @classmethod
    def upsert(
        cls,
        token: str,
        item: AvailableTable,
        parent_id: int | str,
        root_id: int | None = None,
    ):
        """Insert existing item in ISPyB or patch it

        Args:
            item: Item to be pushed
            parent_id: External ID of the item's parent
            root_id: ID of the root of the item tree, such as a session ID

        Returns:
            External link and external ID"""

        ext_obj = ExternalObject(item, parent_id, root_id)
        method = "POST"

        if item.externalId:
            ext_obj.url = f"{ext_obj.external_link_prefix}{item.externalId}"
            method = "PATCH"

        response = ExternalRequest.request(
            token,
            method=method,
            url=ext_obj.url,
            json=ext_obj.item_body.model_dump(mode="json"),
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
            "link": "".join(
                [Config.ispyb_api, ext_obj.external_link_prefix, str(external_id)]
            ),
        }
