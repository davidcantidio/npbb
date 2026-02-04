"""Add lead import fields and tables.

Revision ID: 2c7d9f3a8b1c
Revises: 1a2b3c4d5e6f
Create Date: 2026-02-04
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2c7d9f3a8b1c"
down_revision = "1a2b3c4d5e6f"
branch_labels = None
depends_on = None


def _find_cpf_unique(bind) -> str | None:
    inspector = sa.inspect(bind)
    uniques = inspector.get_unique_constraints("lead")
    for item in uniques:
        if item.get("column_names") == ["cpf"]:
            return item.get("name")
    if bind.dialect.name != "sqlite":
        return None
    res = bind.execute(sa.text("PRAGMA index_list('lead')")).fetchall()
    for row in res:
        idx_name = row[1]
        is_unique = row[2]
        if not is_unique:
            continue
        cols = bind.execute(sa.text(f"PRAGMA index_info('{idx_name}')")).fetchall()
        if [col[2] for col in cols] == ["cpf"]:
            return idx_name
    return None


def upgrade() -> None:
    bind = op.get_bind()
    cpf_constraint = _find_cpf_unique(bind)

    with op.batch_alter_table("lead") as batch_op:
        batch_op.add_column(sa.Column("evento_nome", sa.String(length=150), nullable=True))
        batch_op.add_column(sa.Column("sessao", sa.String(length=80), nullable=True))
        batch_op.add_column(sa.Column("data_compra", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("data_compra_data", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("data_compra_hora", sa.Time(), nullable=True))
        batch_op.add_column(sa.Column("opt_in", sa.String(length=80), nullable=True))
        batch_op.add_column(sa.Column("opt_in_id", sa.String(length=80), nullable=True))
        batch_op.add_column(sa.Column("opt_in_flag", sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column("metodo_entrega", sa.String(length=160), nullable=True))
        batch_op.add_column(sa.Column("endereco_rua", sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column("endereco_numero", sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column("bairro", sa.String(length=160), nullable=True))
        batch_op.add_column(sa.Column("cep", sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column("cidade", sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column("estado", sa.String(length=40), nullable=True))
        batch_op.add_column(sa.Column("genero", sa.String(length=40), nullable=True))
        batch_op.add_column(sa.Column("codigo_promocional", sa.String(length=80), nullable=True))
        batch_op.add_column(sa.Column("ingresso_tipo", sa.String(length=160), nullable=True))
        batch_op.add_column(sa.Column("ingresso_qtd", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("fonte_origem", sa.String(length=80), nullable=True))
        if cpf_constraint:
            batch_op.drop_constraint(cpf_constraint, type_="unique")
        batch_op.create_unique_constraint(
            "uq_lead_ticketing_dedupe",
            ["email", "cpf", "evento_nome", "sessao"],
        )

    op.create_table(
        "lead_conversao",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("lead.id"), nullable=False),
        sa.Column("tipo", sa.String(length=40), nullable=False),
        sa.Column("acao_nome", sa.String(length=120), nullable=True),
        sa.Column("fonte_origem", sa.String(length=80), nullable=True),
        sa.Column("evento_id", sa.Integer(), sa.ForeignKey("evento.id"), nullable=True),
        sa.Column("data_conversao_evento", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "lead_alias",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tipo", sa.String(length=40), nullable=False),
        sa.Column("valor_origem", sa.String(length=200), nullable=False),
        sa.Column("valor_normalizado", sa.String(length=200), nullable=False),
        sa.Column("canonical_value", sa.String(length=200), nullable=True),
        sa.Column("evento_id", sa.Integer(), sa.ForeignKey("evento.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tipo", "valor_normalizado", name="uq_lead_alias_tipo_valor_normalizado"),
    )

    op.create_index("ix_lead_data_compra", "lead", ["data_compra"])
    op.create_index("ix_lead_estado", "lead", ["estado"])
    op.create_index("ix_lead_cidade", "lead", ["cidade"])
    op.create_index("ix_lead_fonte_origem", "lead", ["fonte_origem"])
    op.create_index("ix_lead_conversao_lead_id", "lead_conversao", ["lead_id"])


def downgrade() -> None:
    bind = op.get_bind()

    op.drop_index("ix_lead_conversao_lead_id", table_name="lead_conversao")
    op.drop_index("ix_lead_fonte_origem", table_name="lead")
    op.drop_index("ix_lead_cidade", table_name="lead")
    op.drop_index("ix_lead_estado", table_name="lead")
    op.drop_index("ix_lead_data_compra", table_name="lead")

    op.drop_table("lead_alias")
    op.drop_table("lead_conversao")

    with op.batch_alter_table("lead") as batch_op:
        batch_op.drop_constraint("uq_lead_ticketing_dedupe", type_="unique")
        batch_op.drop_column("fonte_origem")
        batch_op.drop_column("ingresso_qtd")
        batch_op.drop_column("ingresso_tipo")
        batch_op.drop_column("codigo_promocional")
        batch_op.drop_column("genero")
        batch_op.drop_column("estado")
        batch_op.drop_column("cidade")
        batch_op.drop_column("cep")
        batch_op.drop_column("bairro")
        batch_op.drop_column("endereco_numero")
        batch_op.drop_column("endereco_rua")
        batch_op.drop_column("metodo_entrega")
        batch_op.drop_column("opt_in_flag")
        batch_op.drop_column("opt_in_id")
        batch_op.drop_column("opt_in")
        batch_op.drop_column("data_compra_hora")
        batch_op.drop_column("data_compra_data")
        batch_op.drop_column("data_compra")
        batch_op.drop_column("sessao")
        batch_op.drop_column("evento_nome")
        batch_op.create_unique_constraint("uq_lead_cpf", ["cpf"])
