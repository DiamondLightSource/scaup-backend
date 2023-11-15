def test_get(client):
    """Should get unassigned items in shipment"""
    resp = client.get("/shipments/1/unassigned")

    assert resp.status_code == 200

    data = resp.json()

    assert len(data["samples"]) == 1
    assert len(data["gridBoxes"]) == 2
    assert len(data["containers"]) == 1


def test_get_nested(client):
    """Should get nested unassigned items"""
    resp = client.get("/shipments/1/unassigned")

    assert resp.status_code == 200

    data = resp.json()

    assert len(data["gridBoxes"][0]["children"]) == 1


def test_get_inexistent(client):
    """Should return 404 for inexistent shipment"""
    resp = client.get("/shipments/9999/unassigned")

    assert resp.status_code == 404
