import requests
from fastapi import Depends

from ..utils.bearer import OAuth2PasswordBearerCookie
from ..utils.config import Config

oauth2_scheme = OAuth2PasswordBearerCookie(tokenUrl="token")


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


def get_item_from_expeye(request_url: str, token=Depends(oauth2_scheme)):
    return requests.get(
        f"{Config.ispyb_api}{request_url}", headers={"Authorization": f"Bearer {token}"}
    )
