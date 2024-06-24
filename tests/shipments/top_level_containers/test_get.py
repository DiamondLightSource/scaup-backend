def test_get(client):
    """Should get top level containers"""
    resp = client.get("/shipments/1/topLevelContainers")

    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 1
