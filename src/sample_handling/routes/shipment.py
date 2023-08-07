from fastapi import APIRouter

from ..auth import Permissions

auth = Permissions.autoproc_program

router = APIRouter(
    tags=["Shipments"],
    prefix="/shipments",
)


mock = [
    {
        "label": "Dewar",
        "id": "dewar-1",
        "data": {"type": "dewar"},
        "children": [
            {
                "label": "Falcon Tube",
                "id": "ftube",
                "data": {"type": "falconTube"},
                "children": [
                    {
                        "label": "Grid Box 1",
                        "data": {"type": "gridBox"},
                        "id": "grid-box-1",
                        "children": [
                            {
                                "label": "Sample 1",
                                "id": "sample-1",
                                "data": {
                                    "type": "sample",
                                    "position": 1,
                                    "foil": "Cu-flat",
                                    "film": "Lacey carbon",
                                    "mesh": "100",
                                    "ratio": "R 0.6/1",
                                },
                            }
                        ],
                    },
                ],
            },
            {
                "label": "Puck",
                "id": "puck",
                "data": {"type": "puck"},
                "children": [
                    {
                        "label": "Grid Box 2",
                        "data": {"type": "gridBox"},
                        "id": "grid-box-2",
                        "children": [
                            {
                                "label": "Sample 2",
                                "id": "sample-2",
                                "data": {
                                    "type": "sample",
                                    "position": 1,
                                    "foil": "Au-flat",
                                    "film": "Lacey carbon",
                                    "mesh": "200",
                                    "ratio": "R 0.6/1",
                                },
                            }
                        ],
                    },
                ],
            },
        ],
    },
]
