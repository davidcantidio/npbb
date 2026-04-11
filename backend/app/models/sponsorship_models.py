"""Módulo de patrocínio: contratos, cláusulas, contrapartidas, entregas e evidências."""

from datetime import date, datetime, timezone
from enum import Enum
from typing import List, Optional

from sqlalchemy import CheckConstraint, Column, DateTime, Index, Text
from sqlmodel import Field, Relationship

from app.db.metadata import SQLModel


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ContractStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class OwnerType(str, Enum):
    PERSON = "person"
    INSTITUTION = "institution"


class PeriodType(str, Enum):
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    CONTRACT_TERM = "contract_term"
    CUSTOM = "custom"


class ResponsibilityType(str, Enum):
    INDIVIDUAL = "individual"
    COLLECTIVE = "collective"


class RequirementStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    FULFILLED = "fulfilled"
    EXPIRED = "expired"


class OccurrenceStatus(str, Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    DELIVERED = "delivered"
    VALIDATED = "validated"
    REJECTED = "rejected"


class EvidenceType(str, Enum):
    LINK = "link"
    FILE = "file"
    TEXT = "text"
    SOCIAL_POST = "social_post"
    IMAGE = "image"
    OTHER = "other"


class DraftReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EDITED = "edited"


# ---------------------------------------------------------------------------
# 1. SponsoredPerson
# ---------------------------------------------------------------------------


class SponsoredPerson(SQLModel, table=True):
    __tablename__ = "sponsored_person"

    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str = Field(max_length=200)
    cpf: Optional[str] = Field(default=None, max_length=14, unique=True)
    email: Optional[str] = Field(default=None, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=40)
    role: str = Field(max_length=80)
    notes: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    created_at: datetime = Field(default_factory=now_utc)
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc),
    )

    group_memberships: List["GroupMember"] = Relationship(back_populates="person")


# ---------------------------------------------------------------------------
# 2. SponsoredInstitution
# ---------------------------------------------------------------------------


class SponsoredInstitution(SQLModel, table=True):
    __tablename__ = "sponsored_institution"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    cnpj: Optional[str] = Field(default=None, max_length=18, unique=True)
    email: Optional[str] = Field(default=None, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=40)
    notes: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    created_at: datetime = Field(default_factory=now_utc)
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc),
    )

    group_memberships: List["GroupMember"] = Relationship(back_populates="institution")


# ---------------------------------------------------------------------------
# 3. SocialProfile
# ---------------------------------------------------------------------------


class SocialProfile(SQLModel, table=True):
    __tablename__ = "social_profile"
    __table_args__ = (
        Index("ix_social_profile_owner", "owner_type", "owner_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    owner_type: OwnerType
    owner_id: int
    platform: str = Field(max_length=60)
    handle: str = Field(max_length=120)
    url: Optional[str] = Field(default=None, max_length=500)
    is_primary: bool = Field(default=False)

    created_at: datetime = Field(default_factory=now_utc)


# ---------------------------------------------------------------------------
# 4. SponsorshipGroup
# ---------------------------------------------------------------------------


class SponsorshipGroup(SQLModel, table=True):
    __tablename__ = "sponsorship_group"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    created_at: datetime = Field(default_factory=now_utc)
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc),
    )

    members: List["GroupMember"] = Relationship(back_populates="group")
    contracts: List["SponsorshipContract"] = Relationship(back_populates="group")


# ---------------------------------------------------------------------------
# 5. GroupMember
# ---------------------------------------------------------------------------


class GroupMember(SQLModel, table=True):
    __tablename__ = "group_member"
    __table_args__ = (
        CheckConstraint(
            "(person_id IS NOT NULL AND institution_id IS NULL) "
            "OR (person_id IS NULL AND institution_id IS NOT NULL)",
            name="ck_group_member_person_xor_institution",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="sponsorship_group.id", index=True)
    person_id: Optional[int] = Field(default=None, foreign_key="sponsored_person.id", index=True)
    institution_id: Optional[int] = Field(
        default=None, foreign_key="sponsored_institution.id", index=True
    )
    role_in_group: Optional[str] = Field(default=None, max_length=120)
    joined_at: datetime = Field(default_factory=now_utc)
    left_at: Optional[datetime] = None

    group: Optional[SponsorshipGroup] = Relationship(back_populates="members")
    person: Optional[SponsoredPerson] = Relationship(back_populates="group_memberships")
    institution: Optional[SponsoredInstitution] = Relationship(back_populates="group_memberships")
    occurrence_responsibilities: List["OccurrenceResponsible"] = Relationship(
        back_populates="member"
    )


# ---------------------------------------------------------------------------
# 6. SponsorshipContract
# ---------------------------------------------------------------------------


class SponsorshipContract(SQLModel, table=True):
    __tablename__ = "sponsorship_contract"

    id: Optional[int] = Field(default=None, primary_key=True)
    contract_number: str = Field(max_length=80, unique=True)
    group_id: int = Field(foreign_key="sponsorship_group.id", index=True)
    start_date: date
    end_date: date
    status: ContractStatus = Field(default=ContractStatus.ACTIVE)

    file_storage_key: Optional[str] = Field(default=None, max_length=500)
    original_filename: Optional[str] = Field(default=None, max_length=255)
    file_checksum: Optional[str] = Field(default=None, max_length=128)
    uploaded_at: Optional[datetime] = None

    replaced_by_contract_id: Optional[int] = Field(
        default=None, foreign_key="sponsorship_contract.id"
    )
    created_by_user_id: Optional[int] = Field(
        default=None, foreign_key="usuario.id", index=True
    )

    created_at: datetime = Field(default_factory=now_utc)
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc),
    )

    group: Optional[SponsorshipGroup] = Relationship(back_populates="contracts")
    replaced_by: Optional["SponsorshipContract"] = Relationship(
        sa_relationship_kwargs={"remote_side": "SponsorshipContract.id"},
    )
    clauses: List["ContractClause"] = Relationship(back_populates="contract")
    requirements: List["CounterpartRequirement"] = Relationship(back_populates="contract")
    extraction_drafts: List["ContractExtractionDraft"] = Relationship(back_populates="contract")


# ---------------------------------------------------------------------------
# 7. ContractClause
# ---------------------------------------------------------------------------


class ContractClause(SQLModel, table=True):
    __tablename__ = "contract_clause"

    id: Optional[int] = Field(default=None, primary_key=True)
    contract_id: int = Field(foreign_key="sponsorship_contract.id", index=True)
    clause_identifier: str = Field(max_length=40)
    title: Optional[str] = Field(default=None, max_length=300)
    clause_text: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    display_order: int = Field(default=0)
    page_reference: Optional[str] = Field(default=None, max_length=40)

    created_at: datetime = Field(default_factory=now_utc)

    contract: Optional[SponsorshipContract] = Relationship(back_populates="clauses")
    requirements: List["CounterpartRequirement"] = Relationship(back_populates="clause")


# ---------------------------------------------------------------------------
# 8. CounterpartRequirement
# ---------------------------------------------------------------------------


class CounterpartRequirement(SQLModel, table=True):
    __tablename__ = "counterpart_requirement"

    id: Optional[int] = Field(default=None, primary_key=True)
    contract_id: int = Field(foreign_key="sponsorship_contract.id", index=True)
    clause_id: int = Field(foreign_key="contract_clause.id", index=True)
    requirement_type: str = Field(max_length=120)
    description: str = Field(sa_column=Column(Text, nullable=False))

    is_recurring: bool = Field(default=False)
    period_type: Optional[PeriodType] = None
    period_rule_description: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    expected_occurrences: Optional[int] = None
    recurrence_start_date: Optional[date] = None
    recurrence_end_date: Optional[date] = None

    responsibility_type: ResponsibilityType = Field(default=ResponsibilityType.INDIVIDUAL)
    status: RequirementStatus = Field(default=RequirementStatus.PLANNED)

    created_at: datetime = Field(default_factory=now_utc)
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc),
    )

    contract: Optional[SponsorshipContract] = Relationship(back_populates="requirements")
    clause: Optional[ContractClause] = Relationship(back_populates="requirements")
    occurrences: List["RequirementOccurrence"] = Relationship(back_populates="requirement")


# ---------------------------------------------------------------------------
# 9. RequirementOccurrence
# ---------------------------------------------------------------------------


class RequirementOccurrence(SQLModel, table=True):
    __tablename__ = "requirement_occurrence"

    id: Optional[int] = Field(default=None, primary_key=True)
    requirement_id: int = Field(foreign_key="counterpart_requirement.id", index=True)
    period_label: Optional[str] = Field(default=None, max_length=80)
    due_date: Optional[date] = None

    responsibility_type: ResponsibilityType = Field(default=ResponsibilityType.INDIVIDUAL)
    status: OccurrenceStatus = Field(default=OccurrenceStatus.PENDING)

    validated_by_user_id: Optional[int] = Field(
        default=None, foreign_key="usuario.id", index=True
    )
    validated_at: Optional[datetime] = None
    rejection_reason: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    internal_notes: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )

    created_at: datetime = Field(default_factory=now_utc)
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc),
    )

    requirement: Optional[CounterpartRequirement] = Relationship(back_populates="occurrences")
    responsibles: List["OccurrenceResponsible"] = Relationship(back_populates="occurrence")
    deliveries: List["Delivery"] = Relationship(back_populates="occurrence")


# ---------------------------------------------------------------------------
# 10. OccurrenceResponsible
# ---------------------------------------------------------------------------


class OccurrenceResponsible(SQLModel, table=True):
    __tablename__ = "occurrence_responsible"

    id: Optional[int] = Field(default=None, primary_key=True)
    occurrence_id: int = Field(foreign_key="requirement_occurrence.id", index=True)
    member_id: int = Field(foreign_key="group_member.id", index=True)
    is_primary: bool = Field(default=False)
    role_description: Optional[str] = Field(default=None, max_length=200)

    occurrence: Optional[RequirementOccurrence] = Relationship(back_populates="responsibles")
    member: Optional[GroupMember] = Relationship(back_populates="occurrence_responsibilities")


# ---------------------------------------------------------------------------
# 11. Delivery
# ---------------------------------------------------------------------------


class Delivery(SQLModel, table=True):
    __tablename__ = "delivery"

    id: Optional[int] = Field(default=None, primary_key=True)
    occurrence_id: int = Field(foreign_key="requirement_occurrence.id", index=True)
    description: str = Field(sa_column=Column(Text, nullable=False))
    observations: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    delivered_at: Optional[datetime] = None

    created_by_user_id: Optional[int] = Field(
        default=None, foreign_key="usuario.id", index=True
    )

    created_at: datetime = Field(default_factory=now_utc)
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc),
    )

    occurrence: Optional[RequirementOccurrence] = Relationship(back_populates="deliveries")
    evidences: List["DeliveryEvidence"] = Relationship(back_populates="delivery")


# ---------------------------------------------------------------------------
# 12. DeliveryEvidence
# ---------------------------------------------------------------------------


class DeliveryEvidence(SQLModel, table=True):
    __tablename__ = "delivery_evidence"

    id: Optional[int] = Field(default=None, primary_key=True)
    delivery_id: int = Field(foreign_key="delivery.id", index=True)
    evidence_type: EvidenceType
    url: Optional[str] = Field(default=None, max_length=1000)
    file_storage_key: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    platform: Optional[str] = Field(default=None, max_length=60)
    external_id: Optional[str] = Field(default=None, max_length=200)
    posted_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=now_utc)

    delivery: Optional[Delivery] = Relationship(back_populates="evidences")


# ---------------------------------------------------------------------------
# 13. ContractExtractionDraft
# ---------------------------------------------------------------------------


class ContractExtractionDraft(SQLModel, table=True):
    __tablename__ = "contract_extraction_draft"

    id: Optional[int] = Field(default=None, primary_key=True)
    contract_id: int = Field(foreign_key="sponsorship_contract.id", index=True)
    extraction_run_id: str = Field(max_length=120, index=True)

    source_page: Optional[str] = Field(default=None, max_length=20)
    source_text_excerpt: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    extracted_clause_identifier: Optional[str] = Field(default=None, max_length=40)
    extracted_clause_text: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    extracted_requirement_description: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    extracted_requirement_type: Optional[str] = Field(default=None, max_length=120)
    extracted_responsible_hint: Optional[str] = Field(default=None, max_length=200)
    extracted_due_date_hint: Optional[str] = Field(default=None, max_length=80)
    confidence_score: Optional[float] = None

    review_status: DraftReviewStatus = Field(default=DraftReviewStatus.PENDING)
    reviewed_by_user_id: Optional[int] = Field(
        default=None, foreign_key="usuario.id", index=True
    )
    reviewed_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=now_utc)

    contract: Optional[SponsorshipContract] = Relationship(back_populates="extraction_drafts")
