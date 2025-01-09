def test_get(client):
    """Should get session samples"""
    resp = client.get("/proposals/cm00001/sessions/1/samples")

    containers = resp.json()
    assert resp.status_code == 200
    assert len(containers["items"]) == 3


def test_get_internal(client):
    """Should filter out non-internal samples"""
    resp = client.get("/proposals/bi23047/sessions/100/samples?internalOnly=true")

    containers = resp.json()
    assert resp.status_code == 200
    assert len(containers["items"]) == 1

def test_exclude_internal(client):
    """Should filter out samples assigned to internal containers"""
    resp = client.get("/proposals/bi23047/sessions/100/samples?ignoreInternal=true")

    containers = resp.json()
    assert resp.status_code == 200
    assert len(containers["items"]) == 2
