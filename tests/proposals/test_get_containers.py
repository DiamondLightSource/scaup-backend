def test_get(client):
    """Should get session containers"""
    resp = client.get("/proposals/cm00001/sessions/1/containers")

    containers = resp.json()
    assert resp.status_code == 200
    assert len(containers["items"]) == 5


def test_get_internal(client):
    """Should only get session containers that are internal containers"""
    resp = client.get("/proposals/bi23047/sessions/100/containers?isInternal=true")

    containers = resp.json()
    assert resp.status_code == 200
    assert len(containers["items"]) == 1


def test_filter_by_type(client):
    """Should only get session containers that match provided type"""
    resp = client.get("/proposals/cm00001/sessions/1/containers?type=gridBox")

    containers = resp.json()
    assert resp.status_code == 200
    assert len(containers["items"]) == 3
