"""align framework current artifacts to child is_current contract

Revision ID: 84e74e67a3c1
Revises: 17e2fd99b4fe
Create Date: 2026-04-06
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "84e74e67a3c1"
down_revision = "17e2fd99b4fe"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "framework_intake",
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "framework_prd",
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.execute(
        """
        UPDATE framework_intake AS intake
        SET is_current = TRUE
        FROM framework_project AS project
        WHERE project.id = intake.project_id
          AND project.current_intake_id = intake.id
        """
    )
    op.execute(
        """
        UPDATE framework_prd AS prd
        SET is_current = TRUE
        FROM framework_project AS project
        WHERE project.id = prd.project_id
          AND project.current_prd_id = prd.id
        """
    )

    op.alter_column("framework_intake", "is_current", server_default=None)
    op.alter_column("framework_prd", "is_current", server_default=None)

    op.create_index(
        "uq_framework_intake_current_project",
        "framework_intake",
        ["project_id"],
        unique=True,
        postgresql_where=sa.text("is_current"),
        sqlite_where=sa.text("is_current = 1"),
    )
    op.create_index(
        "uq_framework_prd_current_project",
        "framework_prd",
        ["project_id"],
        unique=True,
        postgresql_where=sa.text("is_current"),
        sqlite_where=sa.text("is_current = 1"),
    )

    op.drop_column("framework_project", "current_intake_id")
    op.drop_column("framework_project", "current_prd_id")


def downgrade() -> None:
    op.add_column("framework_project", sa.Column("current_prd_id", sa.Integer(), nullable=True))
    op.add_column("framework_project", sa.Column("current_intake_id", sa.Integer(), nullable=True))

    op.execute(
        """
        UPDATE framework_project AS project
        SET current_intake_id = intake.id
        FROM framework_intake AS intake
        WHERE intake.project_id = project.id
          AND intake.is_current = TRUE
        """
    )
    op.execute(
        """
        UPDATE framework_project AS project
        SET current_prd_id = prd.id
        FROM framework_prd AS prd
        WHERE prd.project_id = project.id
          AND prd.is_current = TRUE
        """
    )

    op.drop_index("uq_framework_prd_current_project", table_name="framework_prd")
    op.drop_index("uq_framework_intake_current_project", table_name="framework_intake")

    op.drop_column("framework_prd", "is_current")
    op.drop_column("framework_intake", "is_current")
