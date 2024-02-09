def test_get(client):
    """Should get all samples in shipment"""

    resp = client.get(
        "/shipments/1/samples",
    )

    assert resp.status_code == 200

    data = resp.json()

    assert data["total"] == 3
    assert len(data["items"]) == 3
