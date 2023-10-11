def pascal_to_title(original_str: str):
    """Convert a pascal-cased string to a capitalised title"""

    new_strs: list[str] = []
    new_str = ""

    for char in original_str:
        if char.isupper():
            new_strs.append(new_str.capitalize())
            new_str = ""

        new_str += char

    new_strs.append(new_str.capitalize())

    return " ".join(new_strs)
