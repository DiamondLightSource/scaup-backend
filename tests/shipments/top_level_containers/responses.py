import json


def registered_dewar_callback(request):
    # Return valid response for dewar with facility code DLS-EM-0000, return 404 for all else
    dewar_code = request.path_url.split("/")[3]

    if dewar_code == "DLS-EM-0000":
        return (200, {}, json.dumps({}))

    return (404, {}, "")


def lab_contact_callback(request):
    # Return valid response for lab contact 1, return 404 for all else

    lab_contact = request.path_url.split("/")[2]

    if lab_contact == "1":
        return (200, {}, json.dumps({}))

    return (404, {}, "")
