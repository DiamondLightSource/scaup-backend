import json

from requests import PreparedRequest

from ...test_utils.regex import get_match, lab_contact_regex, registered_dewar_regex


def registered_dewar_callback(request: PreparedRequest):
    # Return valid response for dewar with facility code DLS-EM-0000, return 404 for all else
    dewar_id = get_match(registered_dewar_regex, request.url, 2)

    if dewar_id in ["DLS-EM-0000", "DLS-EM-0001", "DLS-4", "DLS-1"]:
        return (200, {}, json.dumps({"dewarRegistryId": 456}))

    return (404, {}, "")


def lab_contact_callback(request: PreparedRequest):
    # Return valid response for lab contact 1, return 404 for all else
    lab_contact_id = get_match(lab_contact_regex, request.url)

    if lab_contact_id == "1":
        return (200, {}, json.dumps({}))

    return (404, {}, "")
