def test_get(client):
    """Should get session samples"""
    resp = client.get("/proposals/cm00001/sessions/1/samples")

    containers = resp.json()
    assert resp.status_code == 200
    assert len(containers["items"]) == 3
