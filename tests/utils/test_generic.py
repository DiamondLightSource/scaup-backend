from scaup.utils.generic import pascal_to_title


def test_convert():
    """Should convert pascal string to capitalised title"""
    assert pascal_to_title("newTitle") == "New Title"


def test_single_word():
    """Should convert single word"""
    assert pascal_to_title("title") == "Title"


def test_join_character():
    """Should use passed join character"""
    assert pascal_to_title("newTitle", "") == "NewTitle"
