import json

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


class Expeye:
    @staticmethod
    def request(
        token,
        *args,
        **kwargs,
    ):
        """Wrapper for request object. Since the URL is validated before any
        auth actions happen, we cannot wrap this in a custom auth implementation,
        we must do all the preparation work before the actual request."""

        kwargs["url"] = f"{Config.ispyb_api}{kwargs['url']}"
        kwargs["method"] = kwargs.get("method", "GET")
        kwargs["headers"] = {"Authorization": f"Bearer {token}"}

        return requests.request(**kwargs)

    @classmethod
    def upsert(cls, token: str, item: AvailableTable, parent_id: int | str):
        """Insert existing item in ISPyB or patch it

        :param item: Item to be pushed
        :param parentId: External ID of the item's parent

        :returns: External link and external ID"""

        item_body: OrmBaseModel = OrmBaseModel()

        match item:
            case Shipment():
                url = f"/proposals/{parent_id}/shipments"
                external_link_prefix = "/shipments/"
                item_body = ShipmentExternal.model_validate(item)
                external_key = "shippingId"
            case Container():
                if item.topLevelContainerId:
                    url = f"/dewars/{parent_id}/containers"
                else:
                    url = f"/containers/{parent_id}/containers"
                external_link_prefix = "/containers/"
                item_body = ContainerExternal.model_validate(item)
                external_key = "containerId"
            case TopLevelContainer():
                url = f"/shipments/{parent_id}/dewars"
                external_link_prefix = "/dewars/"
                item_body = TopLevelContainerExternal.model_validate(item)
                external_key = "dewarId"
            case Sample():
                url = f"/containers/{parent_id}/samples"
                external_link_prefix = "/samples/"
                item_body = SampleExternal.model_validate(item)
                external_key = "blSampleId"
            case _:
                raise NotImplementedError()

        if item.externalId:
            # TODO: actually send request to ISPyB to patch it
            external_id = item.externalId
        else:
            response = cls.request(
                token,
                method="POST",
                url=url,
                json=json.loads(item_body.model_dump_json()),
            )

            if response.status_code != 201:
                detail = "No valid JSON body returned from upstream service"

                try:
                    detail = response.json().get("detail", "No detail provided")
                except requests.JSONDecodeError:
                    pass

                app_logger.error(
                    f"Failed pushing to ISPyB at URL {url}, service returned {response.status_code}: {detail}"
                )

                raise HTTPException(
                    status_code=status.HTTP_424_FAILED_DEPENDENCY,
                    detail="Received invalid response from upstream service",
                )

            external_id = response.json()[external_key]

        return {
            "externalId": external_id,
            "link": "".join([Config.ispyb_api, external_link_prefix, str(external_id)]),
        }
