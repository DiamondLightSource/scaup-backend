"""Add lab contacts column to top level container table

Revision ID: b74d7e02e702
Revises: 7712d39c0cdc
Create Date: 2023-10-11 14:04:36.266882

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b74d7e02e702"
down_revision: Union[str, None] = "7712d39c0cdc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "TopLevelContainer", sa.Column("labContact", sa.Integer(), nullable=False)
    )
    op.add_column("TopLevelContainer", sa.Column("details", sa.JSON(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("TopLevelContainer", "details")
    op.drop_column("TopLevelContainer", "labContact")
    # ### end Alembic commands ###
