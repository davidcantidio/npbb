"""merge heads after adding lead_evento migration for ISSUE-F1-01-002"""

revision = '17e2fd99b4fe'
down_revision = ('20260317_add_lead_evento', 'c0d63429d56d')
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import sqlmodel


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
