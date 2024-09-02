import json

from requests import PreparedRequest

from ..test_utils.regex import creation_regex, get_match

item_type_to_id = {
    "containers": "containerId",
    "dewars": "dewarId",
    "shipments": "shippingId",
    "samples": "blSampleId",
}


def generic_creation_callback(request: PreparedRequest):
    item_id = get_match(creation_regex, request.url, 2)
    item_type = get_match(creation_regex, request.url, 3)

    if (item_id.isdigit() and int(item_id) >= 10) or (item_id in ["cm1", "cm3"] and item_type == "shipments"):
        new_id = int(item_id) + 1 if item_id.isdigit() else 10
        return (201, {}, json.dumps({item_type_to_id[item_type]: new_id}))

    return (404, {}, "")
