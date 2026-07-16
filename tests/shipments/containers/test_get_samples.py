def test_get(client):
    """Should get container samples"""
    resp = client.get("/containers/788/samples")

    assert resp.status_code == 200

    data = resp.json()
    assert len(data["items"]) == 1
