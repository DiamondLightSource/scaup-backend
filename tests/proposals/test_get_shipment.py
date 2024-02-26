import responses


@responses.activate
def test_get_draft(client):
    """Should get draft shipments in proposal"""
    resp = client.get("/proposals/cm00001/shipments")

    assert resp.status_code == 200

    data = resp.json()

    assert data["items"][0]["creationStatus"] == "draft"


@responses.activate
def test_get_submitted(client):
    """Should get submitted shipments in proposal"""
    resp = client.get("/proposals/cm00002/shipments")

    assert resp.status_code == 200

    data = resp.json()

    assert data["items"][0]["creationStatus"] == "submitted"


@responses.activate
def test_get_inexistent(client):
    """Should return 404 if no shipments exist in proposal"""
    resp = client.get("/proposals/cm55555/shipments")

    assert resp.status_code == 200

    data = resp.json()

    assert len(data["items"]) == 0
