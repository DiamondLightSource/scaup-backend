"""add creation timestamps

Revision ID: 7325165750bc
Revises: 5968a694dd6a
Create Date: 2025-01-09 17:21:00.137720

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7325165750bc"
down_revision: Union[str, None] = "5968a694dd6a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "Container",
        sa.Column(
            "creationDate",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
    )
    op.add_column(
        "Sample",
        sa.Column(
            "creationDate",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
    )
    op.add_column(
        "TopLevelContainer",
        sa.Column(
            "creationDate",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
    )

    op.execute('UPDATE "Container" SET "creationDate" = NOW()')
    op.execute('UPDATE "Sample" SET "creationDate" = NOW()')
    op.execute('UPDATE "TopLevelContainer" SET "creationDate" = NOW()')

    op.alter_column("Container", "creationDate", nullable=False)
    op.alter_column("TopLevelContainer", "creationDate", nullable=False)
    op.alter_column("Sample", "creationDate", nullable=False)


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("TopLevelContainer", "creationDate")
    op.drop_column("Sample", "creationDate")
    op.drop_column("Container", "creationDate")
    # ### end Alembic commands ###
