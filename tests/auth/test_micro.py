import pytest
from fastapi import HTTPException

from scaup.auth.micro import _generic_table_check
from scaup.models.inner_db.tables import Container, Sample, TopLevelContainer


@pytest.mark.parametrize("table", [Sample, Container, TopLevelContainer])
def test_check(client, table):
    """Should return ID if item exists"""
    assert _generic_table_check(table, 1, "") == 1


@pytest.mark.parametrize("table", [Sample, Container, TopLevelContainer])
def test_check_inexistent(client, table):
    """Should raise exception if item does not exist"""
    with pytest.raises(HTTPException):
        _generic_table_check(table, 999, "")
