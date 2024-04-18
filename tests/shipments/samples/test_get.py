def test_get(client):
    """Should get all samples in shipment"""

    resp = client.get(
        "/shipments/1/samples",
    )

    assert resp.status_code == 200

    data = resp.json()

    assert data["total"] == 3
    assert len(data["items"]) == 3


def test_get_with_parent(client):
    """Should get samples, samples should include parent container in attributes"""

    resp = client.get(
        "/shipments/1/samples",
    )

    assert resp.status_code == 200

    data = resp.json()

    assert data["items"][0]["parent"] == "Grid Box 02"
