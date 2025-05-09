"""Added internal, current columns

Revision ID: 2437fc6c6661
Revises: 170457b06efc
Create Date: 2024-07-12 15:26:38.312797

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2437fc6c6661"
down_revision: Union[str, None] = "170457b06efc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "Container",
        sa.Column(
            "isInternal",
            sa.Boolean(),
            nullable=True,
            comment="Whether this container is for internal facility storage use only",
        ),
    )
    op.add_column(
        "Container",
        sa.Column(
            "isCurrent",
            sa.Boolean(),
            nullable=True,
            comment="Whether container position is current",
        ),
    )
    op.execute('UPDATE "Container" SET "isCurrent" = false')
    op.execute('UPDATE "Container" SET "isInternal" = false')
    op.alter_column("Container", "isInternal", nullable=False)
    op.alter_column("Container", "isCurrent", nullable=False)

    op.alter_column(
        "Container", "shipmentId", existing_type=sa.INTEGER(), nullable=True
    )

    op.add_column(
        "TopLevelContainer",
        sa.Column(
            "isInternal",
            sa.Boolean(),
            nullable=True,
            comment="Whether this container is for internal facility storage use only",
        ),
    )
    op.execute('UPDATE "TopLevelContainer" SET "isInternal" = false')
    op.alter_column("TopLevelContainer", "isInternal", nullable=False)
    op.alter_column(
        "TopLevelContainer", "shipmentId", existing_type=sa.INTEGER(), nullable=True
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "TopLevelContainer", "shipmentId", existing_type=sa.INTEGER(), nullable=False
    )
    op.drop_column("TopLevelContainer", "isInternal")
    op.alter_column(
        "Container", "shipmentId", existing_type=sa.INTEGER(), nullable=False
    )
    op.drop_column("Container", "isCurrent")
    op.drop_column("Container", "isInternal")
    # ### end Alembic commands ###
