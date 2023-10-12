def test_get(client):
    """Should get shipment details as tree of generic items"""
    resp = client.get("/shipments/1")

    assert resp.status_code == 200

    data = resp.json()

    assert len(data["children"]) == 1

    dewar = data["children"][0]

    assert dewar["name"] == "Dewar 01"
    assert len(dewar["children"]) == 1

    container = dewar["children"][0]

    assert container["name"] == "Container 01"
    assert len(container["children"]) == 1

    gridBox = container["children"][0]

    assert gridBox["name"] == "Grid Box 01"
    assert len(gridBox["children"]) == 1

    sample = gridBox["children"][0]

    assert sample["name"] == "Sample 01"


def test_get_multiple(client):
    """Should get shipment details on shipment with multiple top level container
    children"""
    resp = client.get("/shipments/2")

    assert resp.status_code == 200

    data = resp.json()

    assert len(data["children"]) == 2


def test_get_inexistent(client):
    """Should get shipment details as tree of generic items"""
    resp = client.get("/shipments/9999")

    assert resp.status_code == 404
