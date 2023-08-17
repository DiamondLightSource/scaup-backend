def test_create(client):
    """Should create sample when provided with valid shipment ID and protein/compound
    info"""
    pass


def test_create_no_name(client):
    """Should automatically generate name if not provided in request"""
    pass


def test_create_invalid_shipment(client):
    """Should not create new sample when provided with inexistent shipment"""
    pass


def test_create_invalid_protein(client):
    """Should not create new sample when provided with inexistent sample protein/
    compound"""
    pass
