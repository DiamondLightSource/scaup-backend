"""Add unique constraints to location fields

Revision ID: 5968a694dd6a
Revises: e74dc941aa16
Create Date: 2024-10-08 10:21:06.516853

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5968a694dd6a'
down_revision: Union[str, None] = 'e74dc941aa16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('uq_name_shipment', 'Container', type_='unique')
    op.create_unique_constraint('Container_unique_location', 'Container', ['location', 'parentId'])
    op.create_unique_constraint('Container_unique_name', 'Container', ['name', 'shipmentId'])
    op.create_unique_constraint('Sample_unique_sublocation', 'Sample', ['subLocation', 'shipmentId'])
    op.create_unique_constraint('Sample_unique_location', 'Sample', ['location', 'containerId'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('Sample_unique_location', 'Sample', type_='unique')
    op.drop_constraint('Sample_unique_sublocation', 'Sample', type_='unique')
    op.drop_constraint('Container_unique_name', 'Container', type_='unique')
    op.drop_constraint('Container_unique_location', 'Container', type_='unique')
    op.create_unique_constraint('uq_name_shipment', 'Container', ['name', 'shipmentId'])
    # ### end Alembic commands ###
