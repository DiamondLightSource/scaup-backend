import json


def protein_callback(request):
    # Return valid response for proteinId 4407 and 5000, return 404 for all else
    protein_id = request.path_url.split("/")[2]

    if protein_id == "4407":
        return (200, {}, json.dumps({"name": "Protein_01"}))

    if protein_id == "5000":
        return (200, {}, json.dumps({"name": "-nv^]id name"}))

    return (404, {}, "")
