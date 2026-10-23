import pytest
import responses
from sqlalchemy import select, update

from scaup.models.inner_db.tables import Container, Sample
from scaup.utils.config import Config
from scaup.utils.database import inner_db


@responses.activate
def test_push(client):
    """Should push shipment to ISPyB"""
    resp = client.post("/shipments/97/push")

    assert resp.status_code == 200


@pytest.mark.no_sample_response
@responses.activate
def test_push_unassigned(client):
    """Should push unassigned samples"""
    expeye_resp = responses.post(f"{Config.ispyb_api.url}/samples", json={"blSampleId": 1})
    resp = client.post("/shipments/1/push")

    assert resp.status_code == 200

    assert expeye_resp.calls[0].request.body == (
        b'{"comments": null, "source": "eBIC-Scaup", "subLocation": null, "location": null, "name": "Sample_02"'
        b', "crystal": null, "diffractionPlan": null}'
    )


@responses.activate
def test_push_external_id(client):
    """Should push shipment to ISPyB and update external ID."""
    resp = client.post("/shipments/97/push")

    assert resp.status_code == 200

    assert inner_db.session.scalar(select(Container.externalId).filter_by(id=648)) == 13
    assert inner_db.session.scalar(select(Sample.externalId).filter_by(id=434)) == 14


@pytest.mark.no_sample_response
@responses.activate
def test_push_mx(client):
    """Should push shipment with MX fields to ISPyB"""
    expeye_resp = responses.post(f"{Config.ispyb_api.url}/containers/13/samples", json={"blSampleId": 1})

    inner_db.session.execute(
        update(Sample)
        .filter(Sample.id == 434)
        .values(
            {
                "details": {
                    "proteinAcronym": "aFPG",
                    "sampleGroup": "a",
                    "anomalous": "Au",
                    "barcode": "",
                    "comment": "foobar",
                    "status": "",
                    "experimentKind": "MESH",
                    "energy": 300,
                    "screeningMethod": "all",
                    "userPath": "",
                    "spacegroup": "P 1 1 1",
                    "unitCell": "",
                    "unitCell_a": 3,
                    "unitCell_b": 3,
                    "unitCell_c": 3,
                    "unitCell_alpha": 3,
                    "unitCell_beta": 3,
                    "unitCell_gamma": 3,
                    "smilesCode": "aa",
                    "numberToCollect": "1",
                }
            }
        )
    )

    resp = client.post("/shipments/97/push")

    assert resp.status_code == 200

    assert '"cellA": 3, "cellB": 3, "cellC": 3' in str(expeye_resp.calls[0].request.body)


@responses.activate
def test_push_no_shipment(client):
    """Should return 404 for inexistent shipment"""
    resp = client.post("/shipments/9999/push")

    assert resp.status_code == 404
