from sqlalchemy import select

from scaup.models.inner_db.tables import Shipment
from scaup.utils.database import inner_db


def test_post(client):
    ("""Should get shipment details as tree of generic items""",)
    resp = client.post(
        "/shipments/118/update-status",
        params={"token": ""},
        json={
            "status": "New Status",
            "origin_url": "https://fake.com",
            "journey_type": "out",
            "pickup_confirmation_code": "1",
            "tracking_number": "1",
            "pickup_confirmation_timestamp": 1,
        },
    )

    assert resp.status_code == 200

    new_status = inner_db.session.scalar(select(Shipment.status).filter(Shipment.id == 118))

    assert new_status == "New Status"
