def test_delete_with_parent(client):
    """Should fail if sample is referenced in SampleParentChild"""

    resp = client.delete(
        "/samples/1877",
    )

    assert resp.status_code == 409
