"""add_sponsorship_contract_module

Revision ID: 2a9cfc2167a4
Revises: f5e6d7c8b9a0
Create Date: 2026-04-10
"""

revision = "2a9cfc2167a4"
down_revision = "f5e6d7c8b9a0"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    # 1. sponsored_person
    op.create_table(
        "sponsored_person",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("cpf", sa.String(14), nullable=True),
        sa.Column("email", sa.String(200), nullable=True),
        sa.Column("phone", sa.String(40), nullable=True),
        sa.Column("role", sa.String(80), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("cpf", name="uq_sponsored_person_cpf"),
    )

    # 2. sponsored_institution
    op.create_table(
        "sponsored_institution",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("cnpj", sa.String(18), nullable=True),
        sa.Column("email", sa.String(200), nullable=True),
        sa.Column("phone", sa.String(40), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("cnpj", name="uq_sponsored_institution_cnpj"),
    )

    # 3. social_profile
    op.create_table(
        "social_profile",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("owner_type", sa.String(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("platform", sa.String(60), nullable=False),
        sa.Column("handle", sa.String(120), nullable=False),
        sa.Column("url", sa.String(500), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false_()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Index("ix_social_profile_owner", "owner_type", "owner_id"),
    )

    # 4. sponsorship_group
    op.create_table(
        "sponsorship_group",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # 5. group_member
    op.create_table(
        "group_member",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("group_id", sa.Integer(), sa.ForeignKey("sponsorship_group.id"), nullable=False, index=True),
        sa.Column("person_id", sa.Integer(), sa.ForeignKey("sponsored_person.id"), nullable=True, index=True),
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("sponsored_institution.id"), nullable=True, index=True),
        sa.Column("role_in_group", sa.String(120), nullable=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("left_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "(person_id IS NOT NULL AND institution_id IS NULL) "
            "OR (person_id IS NULL AND institution_id IS NOT NULL)",
            name="ck_group_member_person_xor_institution",
        ),
    )

    # 6. sponsorship_contract
    op.create_table(
        "sponsorship_contract",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("contract_number", sa.String(80), nullable=False),
        sa.Column("group_id", sa.Integer(), sa.ForeignKey("sponsorship_group.id"), nullable=False, index=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("file_storage_key", sa.String(500), nullable=True),
        sa.Column("original_filename", sa.String(255), nullable=True),
        sa.Column("file_checksum", sa.String(128), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("replaced_by_contract_id", sa.Integer(), sa.ForeignKey("sponsorship_contract.id"), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("usuario.id"), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("contract_number", name="uq_sponsorship_contract_contract_number"),
    )

    # 7. contract_clause
    op.create_table(
        "contract_clause",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("contract_id", sa.Integer(), sa.ForeignKey("sponsorship_contract.id"), nullable=False, index=True),
        sa.Column("clause_identifier", sa.String(40), nullable=False),
        sa.Column("title", sa.String(300), nullable=True),
        sa.Column("clause_text", sa.Text(), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("page_reference", sa.String(40), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 8. counterpart_requirement
    op.create_table(
        "counterpart_requirement",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("contract_id", sa.Integer(), sa.ForeignKey("sponsorship_contract.id"), nullable=False, index=True),
        sa.Column("clause_id", sa.Integer(), sa.ForeignKey("contract_clause.id"), nullable=False, index=True),
        sa.Column("requirement_type", sa.String(120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default=sa.false_()),
        sa.Column("period_type", sa.String(), nullable=True),
        sa.Column("period_rule_description", sa.Text(), nullable=True),
        sa.Column("expected_occurrences", sa.Integer(), nullable=True),
        sa.Column("recurrence_start_date", sa.Date(), nullable=True),
        sa.Column("recurrence_end_date", sa.Date(), nullable=True),
        sa.Column("responsibility_type", sa.String(), nullable=False, server_default="individual"),
        sa.Column("status", sa.String(), nullable=False, server_default="planned"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # 9. requirement_occurrence
    op.create_table(
        "requirement_occurrence",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("requirement_id", sa.Integer(), sa.ForeignKey("counterpart_requirement.id"), nullable=False, index=True),
        sa.Column("period_label", sa.String(80), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("responsibility_type", sa.String(), nullable=False, server_default="individual"),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("validated_by_user_id", sa.Integer(), sa.ForeignKey("usuario.id"), nullable=True, index=True),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("internal_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # 10. occurrence_responsible
    op.create_table(
        "occurrence_responsible",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("occurrence_id", sa.Integer(), sa.ForeignKey("requirement_occurrence.id"), nullable=False, index=True),
        sa.Column("member_id", sa.Integer(), sa.ForeignKey("group_member.id"), nullable=False, index=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false_()),
        sa.Column("role_description", sa.String(200), nullable=True),
    )

    # 11. delivery
    op.create_table(
        "delivery",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("occurrence_id", sa.Integer(), sa.ForeignKey("requirement_occurrence.id"), nullable=False, index=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("observations", sa.Text(), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("usuario.id"), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # 12. delivery_evidence
    op.create_table(
        "delivery_evidence",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("delivery_id", sa.Integer(), sa.ForeignKey("delivery.id"), nullable=False, index=True),
        sa.Column("evidence_type", sa.String(), nullable=False),
        sa.Column("url", sa.String(1000), nullable=True),
        sa.Column("file_storage_key", sa.String(500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("platform", sa.String(60), nullable=True),
        sa.Column("external_id", sa.String(200), nullable=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 13. contract_extraction_draft
    op.create_table(
        "contract_extraction_draft",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("contract_id", sa.Integer(), sa.ForeignKey("sponsorship_contract.id"), nullable=False, index=True),
        sa.Column("extraction_run_id", sa.String(120), nullable=False, index=True),
        sa.Column("source_page", sa.String(20), nullable=True),
        sa.Column("source_text_excerpt", sa.Text(), nullable=True),
        sa.Column("extracted_clause_identifier", sa.String(40), nullable=True),
        sa.Column("extracted_clause_text", sa.Text(), nullable=True),
        sa.Column("extracted_requirement_description", sa.Text(), nullable=True),
        sa.Column("extracted_requirement_type", sa.String(120), nullable=True),
        sa.Column("extracted_responsible_hint", sa.String(200), nullable=True),
        sa.Column("extracted_due_date_hint", sa.String(80), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("review_status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("reviewed_by_user_id", sa.Integer(), sa.ForeignKey("usuario.id"), nullable=True, index=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("contract_extraction_draft")
    op.drop_table("delivery_evidence")
    op.drop_table("delivery")
    op.drop_table("occurrence_responsible")
    op.drop_table("requirement_occurrence")
    op.drop_table("counterpart_requirement")
    op.drop_table("contract_clause")
    op.drop_table("sponsorship_contract")
    op.drop_table("group_member")
    op.drop_table("sponsorship_group")
    op.drop_table("social_profile")
    op.drop_table("sponsored_institution")
    op.drop_table("sponsored_person")
