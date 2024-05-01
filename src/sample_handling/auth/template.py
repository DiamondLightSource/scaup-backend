from typing import Protocol, runtime_checkable

from lims_utils.models import parse_proposal


@runtime_checkable
class GenericPermissions(Protocol):
    @staticmethod
    def proposal(proposalReference: str):
        return proposalReference

    @staticmethod
    def session(proposalReference: str, visitNumber: int):
        return parse_proposal(
            proposal_reference=proposalReference, visit_number=visitNumber
        )

    @staticmethod
    def shipment(shipmentId: int) -> int:
        return shipmentId

    @staticmethod
    def sample(sampleId: int) -> int:
        return sampleId

    @staticmethod
    def container(containerId: int) -> int:
        return containerId

    @staticmethod
    def top_level_container(topLevelContainerId: int) -> int:
        return topLevelContainerId
