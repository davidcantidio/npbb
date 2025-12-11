"""${message}"""

revision = ${repr(revision_id)}
down_revision = ${repr(revision_context.down_revision_id)}
branch_labels = ${repr(revision_context.branch_labels)}
depends_on = ${repr(revision_context.depends_on)}

from alembic import op
import sqlalchemy as sa
import sqlmodel

def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
