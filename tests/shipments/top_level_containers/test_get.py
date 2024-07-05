def test_get(client):
    """Should get top level containers"""
    resp = client.get("/shipments/1/topLevelContainers")

    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 1


def test_get_parent_status(client):
    """Should get status of parent shipment"""
    resp = client.get("/shipments/89/topLevelContainers")

    assert resp.status_code == 200
    assert resp.json()["items"][0]["status"] == "Booked"
