from dataclasses import dataclass


@dataclass
class GenericUser:
    fedid: str
    id: str
    familyName: str
    title: str
    givenName: str
    permissions: list[str]


class GenericPermissions:
    @staticmethod
    def proposal(proposalReference: str) -> str:
        return proposalReference

    @staticmethod
    def shipment(shipmentId: int) -> int:
        return shipmentId
