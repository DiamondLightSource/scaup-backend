import json


def proposal_callback(request):
    proposal_reference = request.path_url.split("/")[2]

    if proposal_reference == "cm00001":
        return (200, {}, json.dumps({}))

    return (404, {}, "")
