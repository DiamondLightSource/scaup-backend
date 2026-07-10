def test_get(client):
    """Should get containers in top level container"""
    resp = client.get("/topLevelContainers/1/containers")

    assert resp.status_code == 200
    containers = resp.json()["items"]

    assert len(containers) == 2


def test_get_by_type(client):
    """Should get containers in top level container by type"""
    resp = client.get("/topLevelContainers/1/containers?type=puck")

    assert resp.status_code == 200
    containers = resp.json()["items"]

    assert len(containers) == 2
