import copy
from datetime import datetime
from uuid import UUID

import pytest
import responses
from fastapi import HTTPException

from scaup.models.inner_db.tables import TopLevelContainer
from scaup.utils.config import Config
from scaup.utils.external import ExternalObject, _get_resource_from_ispyb

base_dewar = TopLevelContainer(
    code="DLS-EM-0001",
    id=1,
    shipmentId=1,
    type="dewar",
    name="Test_Dewar",
    barCode=UUID(bytes=b"ffffffffffffffff"),
    creationDate=datetime.now(),
)


@responses.activate
def test_new_top_level_container(client):
    """Should get session information from ISPyB and populate it in dewar before pushing it"""
    dewar = ExternalObject("token", base_dewar, 1, 5)

    assert dewar.item_body.firstExperimentId == 1
    assert dewar.item_body.dewarRegistryId == 456

@responses.activate
def test_update_top_level_container(client):
    """Should not get session ID if item has already been pushed to ISPyB"""
    external_dewar = copy.deepcopy(base_dewar)
    external_dewar.externalId = 1
    dewar = ExternalObject("token", external_dewar, 1, 5)

    assert dewar.item_body.firstExperimentId is None
    assert dewar.to_exclude == {"firstExperimentId"}

@responses.activate
def test_upstream_request_fail():
    """Should raise exception if Expeye returns invalid response"""
    responses.get(
        f"{Config.ispyb_api.url}/foo", status=404
    )

    with pytest.raises(HTTPException, match="Received invalid response from upstream service"):
        _get_resource_from_ispyb("token", "/foo")
