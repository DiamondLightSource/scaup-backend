import responses


@responses.activate
def test_get(client):
    """Should get tracking labels as a PDF"""
    resp = client.get("/shipments/117/tracking-labels")

    assert resp.status_code == 200


@responses.activate
def test_no_bar_code(client):
    """Should return 404 if bar code is not present"""
    resp = client.get("/shipments/2/tracking-labels")

    assert resp.status_code == 404
