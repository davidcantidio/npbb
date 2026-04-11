"""merge heads after adding lead_evento migration for ISSUE-F1-01-002"""

revision = '17e2fd99b4fe'
# Lineariza o merge: a ramo noop `20260317_add_lead_evento` foi removida do repo
# para evitar falhas de carregamento do grafo em deploys (Render).
down_revision = 'c0d63429d56d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
