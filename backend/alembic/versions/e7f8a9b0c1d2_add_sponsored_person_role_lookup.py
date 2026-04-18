"""add sponsored_person_role lookup and sponsored_person.role_id

Revision ID: e7f8a9b0c1d2
Revises: d0f1a2b3c4d5
Create Date: 2026-04-16
"""

from __future__ import annotations

import unicodedata

import sqlalchemy as sa
from alembic import op

revision = "e7f8a9b0c1d2"
down_revision = "d0f1a2b3c4d5"
branch_labels = None
depends_on = None


ROLES: list[tuple[str, str, int]] = [
    ("atleta", "Atleta", 1),
    ("staff", "Staff", 2),
    ("fisioterapeuta", "Fisioterapeuta", 3),
    ("medico", "Médico", 4),
    ("tecnico", "Técnico", 5),
    ("nutricionista", "Nutricionista", 6),
    ("terapeuta", "Terapeuta", 7),
    ("fotografo", "Fotógrafo", 8),
    ("outro", "Outro", 9),
]


def _strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value.strip().lower())
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def _map_legacy_role_to_code(raw: str | None) -> str:
    if raw is None:
        return "outro"
    key = _strip_accents(str(raw))
    aliases: dict[str, str] = {
        "atleta": "atleta",
        "athlete": "atleta",
        "staff": "staff",
        "fisioterapeuta": "fisioterapeuta",
        "medico": "medico",
        "tecnico": "tecnico",
        "nutricionista": "nutricionista",
        "terapeuta": "terapeuta",
        "fotografo": "fotografo",
        "outro": "outro",
    }
    return aliases.get(key, "outro")


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if not insp.has_table("sponsored_person"):
        return

    if not insp.has_table("sponsored_person_role"):
        op.create_table(
            "sponsored_person_role",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("code", sa.String(length=40), nullable=False),
            sa.Column("label", sa.String(length=80), nullable=False),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            sa.UniqueConstraint("code", name="uq_sponsored_person_role_code"),
        )

    dialect = bind.dialect.name
    for code, label, sort_order in ROLES:
        if dialect == "postgresql":
            op.execute(
                sa.text(
                    """
                    INSERT INTO sponsored_person_role (code, label, sort_order)
                    VALUES (:code, :label, :sort_order)
                    ON CONFLICT (code) DO NOTHING
                    """
                ).bindparams(code=code, label=label, sort_order=sort_order)
            )
        else:
            op.execute(
                sa.text(
                    """
                    INSERT OR IGNORE INTO sponsored_person_role (code, label, sort_order)
                    VALUES (:code, :label, :sort_order)
                    """
                ).bindparams(code=code, label=label, sort_order=sort_order)
            )

    insp = sa.inspect(bind)
    cols = {c["name"] for c in insp.get_columns("sponsored_person")}

    if "role_id" in cols and "role" not in cols:
        return

    if "role_id" not in cols:
        op.add_column(
            "sponsored_person",
            sa.Column("role_id", sa.Integer(), nullable=True),
        )
        op.create_foreign_key(
            "fk_sponsored_person_role_id",
            "sponsored_person",
            "sponsored_person_role",
            ["role_id"],
            ["id"],
        )

    insp = sa.inspect(bind)
    cols = {c["name"] for c in insp.get_columns("sponsored_person")}

    code_to_id = {
        r["code"]: r["id"]
        for r in bind.execute(sa.text("SELECT id, code FROM sponsored_person_role")).mappings().all()
    }
    outro_id = code_to_id["outro"]

    if "role" in cols:
        rows = bind.execute(sa.text("SELECT id, role FROM sponsored_person")).mappings().all()
        for row in rows:
            pid = row["id"]
            code = _map_legacy_role_to_code(row.get("role"))
            rid = code_to_id.get(code, outro_id)
            bind.execute(
                sa.text("UPDATE sponsored_person SET role_id = :rid WHERE id = :pid").bindparams(rid=rid, pid=pid)
            )
    else:
        bind.execute(
            sa.text("UPDATE sponsored_person SET role_id = :rid WHERE role_id IS NULL").bindparams(rid=outro_id)
        )

    op.alter_column("sponsored_person", "role_id", existing_type=sa.Integer(), nullable=False)

    if "role" in cols:
        with op.batch_alter_table("sponsored_person") as batch_op:
            batch_op.drop_column("role")


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if not insp.has_table("sponsored_person"):
        return

    cols = {c["name"] for c in insp.get_columns("sponsored_person")}

    if "role" not in cols:
        op.add_column(
            "sponsored_person",
            sa.Column("role", sa.String(length=80), nullable=True),
        )

    if "role_id" in cols:
        bind.execute(
            sa.text(
                """
                UPDATE sponsored_person
                SET role = (
                    SELECT r.code FROM sponsored_person_role r WHERE r.id = sponsored_person.role_id
                )
                """
            )
        )
        op.alter_column("sponsored_person", "role", existing_type=sa.String(length=80), nullable=False)

    if "role_id" in cols:
        with op.batch_alter_table("sponsored_person") as batch_op:
            batch_op.drop_constraint("fk_sponsored_person_role_id", type_="foreignkey")
            batch_op.drop_column("role_id")

    if insp.has_table("sponsored_person_role"):
        op.drop_table("sponsored_person_role")
