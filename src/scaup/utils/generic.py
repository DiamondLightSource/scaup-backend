def pascal_to_title(original_str: str, join_character=" "):
    """Convert a pascal-cased string to a capitalised title"""

    new_strs: list[str] = []
    new_str = ""

    for char in original_str:
        if char.isupper():
            new_strs.append(new_str.capitalize())
            new_str = ""

        new_str += char

    new_strs.append(new_str.capitalize())

    return join_character.join(new_strs)


def lowest_missing(s: list[int]) -> int:
    """Return the lowest missing integer in a list of integers"""
    i = 0
    while i in s:
        i += 1
    return i
