import json

item_type_to_id = {
    "containers": "containerId",
    "dewars": "dewarId",
    "shipments": "shippingId",
    "samples": "blSampleId",
}


def generic_creation_callback(request):
    item_id = request.path_url.split("/")[2]
    item_type = request.path_url.split("/")[3]

    if (item_id.isdigit() and int(item_id) >= 10) or (
        item_id == "cm00001" and item_type == "shipments"
    ):
        new_id = int(item_id) + 1 if item_id.isdigit() else 10
        return (201, {}, json.dumps({item_type_to_id[item_type]: new_id}))

    return (404, {}, "")
