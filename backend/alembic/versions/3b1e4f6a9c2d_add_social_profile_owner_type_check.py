"""add_social_profile_owner_type_check

Revision ID: 3b1e4f6a9c2d
Revises: 2a9cfc2167a4
Create Date: 2026-04-11
"""

revision = "3b1e4f6a9c2d"
down_revision = "2a9cfc2167a4"
branch_labels = None
depends_on = None

from alembic import op


def upgrade() -> None:
    with op.batch_alter_table("social_profile") as batch_op:
        batch_op.create_check_constraint(
            "ck_social_profile_owner_type_domain",
            "UPPER(owner_type) IN ('PERSON', 'INSTITUTION')",
        )


def downgrade() -> None:
    with op.batch_alter_table("social_profile") as batch_op:
        batch_op.drop_constraint("ck_social_profile_owner_type_domain", type_="check")
