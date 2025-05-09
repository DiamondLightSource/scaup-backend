import json

from requests import PreparedRequest

from ...test_utils.regex import get_match, protein_regex


def protein_callback(request: PreparedRequest):
    # Return valid response for proteinId 4407 and 5000, return 404 for all else
    protein_id = get_match(protein_regex, request.url)

    if protein_id == "4407":
        return (200, {}, json.dumps({"name": "Protein_01"}))

    if protein_id == "5000":
        return (200, {}, json.dumps({"name": "-nv^]id name"}))

    return (404, {}, "")
