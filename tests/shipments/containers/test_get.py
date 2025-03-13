def test_get(client):
    """Should get container details"""
    resp = client.get("/containers/1")

    assert resp.status_code == 200

    data = resp.json()
    assert data["type"] == "puck"
