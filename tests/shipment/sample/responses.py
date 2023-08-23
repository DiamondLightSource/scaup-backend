import json


def protein_callback(request):
    # Return valid response for proteinId 1, return 404 for all else
    protein_id = request.path_url.split("/")[4]

    if protein_id == "4407":
        return (200, {}, json.dumps({"name": "Protein 01"}))

    return (404, {}, "")
