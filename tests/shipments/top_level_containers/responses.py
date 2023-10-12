import json


def registered_dewar_callback(request):
    # Return valid response for proteinId 1, return 404 for all else
    proposal_reference = request.path_url.split("/")[2]
    dewar_code = request.path_url.split("/")[5]

    if dewar_code == "DLS-EM-0000" and proposal_reference == "cm00001":
        return (200, {}, json.dumps({}))

    return (404, {}, "")


def lab_contact_callback(request):
    # Return valid response for proteinId 1, return 404 for all else

    proposal_reference = request.path_url.split("/")[2]
    dewar_code = request.path_url.split("/")[4]

    if dewar_code == "1" and proposal_reference == "cm00001":
        return (200, {}, json.dumps({}))

    return (404, {}, "")
