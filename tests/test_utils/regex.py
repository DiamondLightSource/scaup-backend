import re

from scaup.utils.config import Config

session_regex = re.compile(f"{Config.ispyb_api.url}/proposals/(.*)/sessions/(.*)")

protein_regex = re.compile(f"{Config.ispyb_api.url}/proteins/([0-9].*)")
lab_contact_regex = re.compile(f"{Config.ispyb_api.url}/contacts/([0-9].*)")
registered_dewar_regex = re.compile(f"{Config.ispyb_api.url}/proposals/(.*)/dewar-registry/(.*)")
registered_dewar_creation_regex = re.compile(f"{Config.ispyb_api.url}/proposals/(.*)/dewar-registry")
creation_regex = re.compile(
    f"{Config.ispyb_api.url}/(containers|proposals|dewars|shipments|proposals)/(.*)/(dewars|samples|containers|shipments)"
)
proposal_regex = re.compile(f"{Config.auth.endpoint}/permission/proposal/(.*)")


def get_match(pattern: re.Pattern[str], url: str | None, index=1):
    match = re.match(pattern, url or "")

    assert match is not None
    return match.group(index)
