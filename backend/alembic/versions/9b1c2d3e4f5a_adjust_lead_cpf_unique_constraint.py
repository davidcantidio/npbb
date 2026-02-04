"""Adjust lead cpf unique constraint name.

Revision ID: 9b1c2d3e4f5a
Revises: 5f2b8c9a1d4e
Create Date: 2026-02-04
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9b1c2d3e4f5a"
down_revision = "5f2b8c9a1d4e"
branch_labels = None
depends_on = None


def _drop_cpf_unique(bind) -> None:
    inspector = sa.inspect(bind)
    uniques = inspector.get_unique_constraints("lead")
    cpf_constraint = None
    for item in uniques:
        if item.get("column_names") == ["cpf"]:
            cpf_constraint = item.get("name")
            break
    if bind.dialect.name == "sqlite":
        if not cpf_constraint:
            # Fallback: localizar indice unico pelo PRAGMA.
            res = bind.execute(sa.text("PRAGMA index_list('lead')")).fetchall()
            for row in res:
                idx_name = row[1]
                is_unique = row[2]
                if not is_unique:
                    continue
                cols = bind.execute(sa.text(f"PRAGMA index_info('{idx_name}')")).fetchall()
                if [col[2] for col in cols] == ["cpf"]:
                    cpf_constraint = idx_name
                    break
        if not cpf_constraint:
            return
        with op.batch_alter_table("lead") as batch_op:
            batch_op.drop_constraint(cpf_constraint, type_="unique")
    else:
        if not cpf_constraint:
            return
        op.drop_constraint(cpf_constraint, "lead", type_="unique")


def upgrade() -> None:
    bind = op.get_bind()
    _drop_cpf_unique(bind)
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("lead") as batch_op:
            batch_op.create_unique_constraint("uq_lead_cpf", ["cpf"])
    else:
        op.create_unique_constraint("uq_lead_cpf", "lead", ["cpf"])


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("lead") as batch_op:
            batch_op.drop_constraint("uq_lead_cpf", type_="unique")
    else:
        op.drop_constraint("uq_lead_cpf", "lead", type_="unique")

    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("lead") as batch_op:
            batch_op.create_unique_constraint("uq_lead_cpf", ["cpf"])
    else:
        op.create_unique_constraint("uq_lead_cpf", "lead", ["cpf"])
