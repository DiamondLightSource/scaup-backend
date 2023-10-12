import json


def registered_dewar_callback(request):
    # Return valid response for proteinId 1, return 404 for all else
    dewar_code = request.path_url.split("/")[5]

    if dewar_code == "DLS-EM-0000":
        return (200, {}, json.dumps({}))

    return (404, {}, "")


def lab_contact_callback(request):
    # Return valid response for proteinId 1, return 404 for all else
    dewar_code = request.path_url.split("/")[4]

    if dewar_code == "1":
        return (200, {}, json.dumps({}))

    return (404, {}, "")
