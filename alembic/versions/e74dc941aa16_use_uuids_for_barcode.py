"""Use UUIDs for barcode

Revision ID: e74dc941aa16
Revises: bc8b830b4e87
Create Date: 2024-10-02 10:57:01.121646

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e74dc941aa16'
down_revision: Union[str, None] = 'bc8b830b4e87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('TopLevelContainer', 'barCode')
    op.alter_column('Shipment', 'status', server_default="Created")
    op.add_column('TopLevelContainer', sa.Column('barCode', sa.UUID(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('TopLevelContainer', 'barCode',
               existing_type=sa.UUID(),
               type_=sa.VARCHAR(length=20),
               existing_nullable=True)
    # ### end Alembic commands ###
