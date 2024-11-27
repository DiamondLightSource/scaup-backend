import re

from sample_handling.utils.config import Config

session_regex = re.compile(f"{Config.ispyb_api}/proposals/(.*)/sessions/(.*)")

protein_regex = re.compile(f"{Config.ispyb_api}/proteins/([0-9].*)")
lab_contact_regex = re.compile(f"{Config.ispyb_api}/contacts/([0-9].*)")
registered_dewar_regex = re.compile(f"{Config.ispyb_api}/proposals/(.*)/dewar-registry/(.*)")
creation_regex = re.compile(
    f"{Config.ispyb_api}/(containers|proposals|dewars|shipments|proposals)/(.*)/(dewars|samples|containers|shipments)"
)
proposal_regex = re.compile(f"{Config.auth.endpoint}/permission/proposal/(.*)")


def get_match(pattern: re.Pattern[str], url: str | None, index=1):
    match = re.match(pattern, url or "")

    assert match is not None
    return match.group(index)
