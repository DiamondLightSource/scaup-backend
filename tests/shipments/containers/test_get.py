def test_get(client):
    """Should get container details"""
    resp = client.get("/containers/1")

    assert resp.status_code == 200

    data = resp.json()
    assert data["type"] == "puck"


def test_get_internal(client):
    """Should get container details (for container which is stored internally)"""
    resp = client.get("/containers/788")

    assert resp.status_code == 200

    data = resp.json()
    assert data["internalStorageContainer"] == 221
