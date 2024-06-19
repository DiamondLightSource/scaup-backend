"""make name/shipment id unique compositvely

Revision ID: 1daa99b93377
Revises: 
Create Date: 2024-03-27 15:54:27.323444

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1daa99b93377"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint("uq_name_shipment", "Container", ["name", "shipmentId"])


def downgrade() -> None:
    op.drop_constraint("uq_name_shipment", "Container")
