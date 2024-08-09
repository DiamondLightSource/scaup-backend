"""Add pre session table

Revision ID: faeec6295a58
Revises: b22d0b329bca
Create Date: 2024-05-29 11:12:00.040082

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "faeec6295a58"
down_revision: Union[str, None] = "b22d0b329bca"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "PreSession",
        sa.Column("preSessionId", sa.Integer(), nullable=False),
        sa.Column("shipmentId", sa.Integer(), nullable=False),
        sa.Column(
            "details", sa.JSON(), nullable=True, comment="Generic additional details"
        ),
        sa.ForeignKeyConstraint(
            ["shipmentId"],
            ["Shipment.shipmentId"],
        ),
        sa.PrimaryKeyConstraint("preSessionId"),
    )
    op.create_index(
        op.f("ix_PreSession_preSessionId"), "PreSession", ["preSessionId"], unique=False
    )
    op.create_index(
        op.f("ix_PreSession_shipmentId"), "PreSession", ["shipmentId"], unique=True
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_PreSession_shipmentId"), table_name="PreSession")
    op.drop_index(op.f("ix_PreSession_preSessionId"), table_name="PreSession")
    op.drop_table("PreSession")
    # ### end Alembic commands ###
