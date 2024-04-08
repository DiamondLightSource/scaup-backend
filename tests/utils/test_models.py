from sample_handling.utils.models import BaseExternal, BaseModelWithNameValidator


class SubClassModel(BaseModelWithNameValidator):
    name: str


def test_null(client):
    """Should convert empty strings to null"""
    instance = SubClassModel(name="")

    assert instance.name is None


def test_valid(client):
    """Should not modify non-empty strings"""
    instance = SubClassModel(name="test")

    assert instance.name == "test"


def test_append_origin(client):
    """Should include origin of item in source column"""
    instance = BaseExternal(comments="test")

    assert instance.source == "eBIC-SH"
