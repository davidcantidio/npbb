"""Modelos ORM (SQLModel) do domínio de patrocínios.

Persistem entidades expostas pela API ``/sponsorship``: pessoas e instituições
patrocinadas, perfis sociais, grupos, membros, contratos, cláusulas, requisitos
de contrapartida, ocorrências, responsáveis, entregas, evidências e rascunhos de
extração de contrato. Enums descrevem status e tipos usados nas regras de
negócio e validações na camada de serviço.
"""

from datetime import date, datetime, timezone
from enum import Enum
from typing import List, Optional

from sqlalchemy import CheckConstraint, Column, DateTime, Index, Text
from sqlmodel import Field, Relationship

from app.db.metadata import SQLModel


def now_utc() -> datetime:
    """Retorna o instante atual em UTC com fuso explícito.

    Args:
        Nenhum.

    Returns:
        ``datetime`` com ``tzinfo`` definido para UTC.
    """
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ContractStatus(str, Enum):
    """Ciclo de vida lógico do contrato de patrocínio.

    Attributes:
        ACTIVE: Contrato em vigor ou operacionalmente ativo.
        INACTIVE: Contrato fora de vigor mas não arquivado.
        ARCHIVED: Contrato arquivado para consulta histórica.
    """

    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class OwnerType(str, Enum):
    """Tipo de entidade dona de um perfil social polimórfico.

    Attributes:
        PERSON: Pessoa física patrocinada.
        INSTITUTION: Instituição patrocinada.
    """

    PERSON = "person"
    INSTITUTION = "institution"


class PeriodType(str, Enum):
    """Granularidade de período para requisitos recorrentes.

    Attributes:
        WEEK: Recorrência semanal.
        MONTH: Recorrência mensal.
        YEAR: Recorrência anual.
        CONTRACT_TERM: Alinhado à vigência total do contrato.
        CUSTOM: Regra customizada descrita em texto.
    """

    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    CONTRACT_TERM = "contract_term"
    CUSTOM = "custom"


class ResponsibilityType(str, Enum):
    """Como a responsabilidade pela ocorrência é distribuída.

    Attributes:
        INDIVIDUAL: Exatamente um responsável operacional.
        COLLECTIVE: Dois ou mais responsáveis operacionais.
    """

    INDIVIDUAL = "individual"
    COLLECTIVE = "collective"


class RequirementStatus(str, Enum):
    """Estado macro do requisito de contrapartida.

    Attributes:
        PLANNED: Planejado, ainda não em execução efetiva.
        IN_PROGRESS: Em andamento.
        FULFILLED: Cumprido ou encerrado com sucesso.
        EXPIRED: Expirado sem cumprimento satisfatório.
    """

    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    FULFILLED = "fulfilled"
    EXPIRED = "expired"


class OccurrenceStatus(str, Enum):
    """Estado de uma ocorrência pontual de requisito.

    Attributes:
        PENDING: Aguardando ação ou entrega.
        IN_REVIEW: Em análise interna.
        DELIVERED: Entrega registrada, aguardando validação.
        VALIDATED: Aceita e auditada.
        REJECTED: Rejeitada (exige motivo).
    """

    PENDING = "pending"
    IN_REVIEW = "in_review"
    DELIVERED = "delivered"
    VALIDATED = "validated"
    REJECTED = "rejected"


class EvidenceType(str, Enum):
    """Formato da evidência de cumprimento anexada à entrega.

    Attributes:
        LINK: URL ou referência web.
        FILE: Arquivo armazenado internamente.
        TEXT: Texto livre.
        SOCIAL_POST: Publicação em rede social.
        IMAGE: Imagem (screenshot ou mídia).
        OTHER: Outro tipo não padronizado.
    """

    LINK = "link"
    FILE = "file"
    TEXT = "text"
    SOCIAL_POST = "social_post"
    IMAGE = "image"
    OTHER = "other"


class DraftReviewStatus(str, Enum):
    """Estado de revisão humana de um rascunho extraído de contrato.

    Attributes:
        PENDING: Aguardando revisão.
        APPROVED: Aprovado para promoção ou uso.
        REJECTED: Descartado na revisão.
        EDITED: Ajustado manualmente após extração automática.
    """

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EDITED = "edited"


# ---------------------------------------------------------------------------
# 1. SponsoredPerson
# ---------------------------------------------------------------------------


class SponsoredPerson(SQLModel, table=True):
    """Pessoa física patrocinada pela NPBB.

    Attributes:
        id: Chave primária.
        full_name: Nome completo.
        cpf: CPF único opcional.
        email: E-mail opcional.
        phone: Telefone opcional.
        role: Papel ou função no contexto de patrocínio.
        notes: Observações em texto longo.
        created_at: Criação do registro (UTC).
        updated_at: Última atualização (UTC).
        group_memberships: Filiações a grupos de patrocínio.
    """

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
    """Instituição (pessoa jurídica) patrocinada.

    Attributes:
        id: Chave primária.
        name: Nome ou razão social.
        cnpj: CNPJ único opcional.
        email: E-mail opcional.
        phone: Telefone opcional.
        notes: Observações em texto longo.
        created_at: Criação do registro (UTC).
        updated_at: Última atualização (UTC).
        group_memberships: Filiações a grupos de patrocínio.
    """

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
    """Perfil em rede social vinculado a pessoa ou instituição (referência polimórfica).

    A existência do dono é validada na API; ``owner_type`` + ``owner_id``
    apontam para ``SponsoredPerson`` ou ``SponsoredInstitution``.

    Attributes:
        id: Chave primária.
        owner_type: Tipo de dono (enum ``OwnerType``).
        owner_id: ID do dono na tabela correspondente.
        platform: Nome da rede ou plataforma.
        handle: Identificador público (@usuario).
        url: URL completa opcional.
        is_primary: Indica se é o perfil principal do dono.
        created_at: Criação do registro (UTC).
    """

    __tablename__ = "social_profile"
    __table_args__ = (
        CheckConstraint(
            "UPPER(owner_type) IN ('PERSON', 'INSTITUTION')",
            name="ck_social_profile_owner_type_domain",
        ),
        Index("ix_social_profile_owner", "owner_type", "owner_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    owner_type: OwnerType
    owner_id: int
    platform: str = Field(max_length=60)
    handle: str = Field(max_length=120)
    url: Optional[str] = Field(default=None, max_length=500)
    is_primary: bool = Field(default=False)
    # NOTE: owner_type + owner_id is a logical polymorphic reference.
    # Existence is enforced in the API layer because the table can point to
    # different owner tables depending on owner_type.

    created_at: datetime = Field(default_factory=now_utc)


# ---------------------------------------------------------------------------
# 4. SponsorshipGroup
# ---------------------------------------------------------------------------


class SponsorshipGroup(SQLModel, table=True):
    """Grupo operacional de patrocínio (agrega membros e contratos).

    Attributes:
        id: Chave primária.
        name: Nome do grupo.
        description: Descrição opcional.
        created_at: Criação do registro (UTC).
        updated_at: Última atualização (UTC).
        members: Membros (pessoas ou instituições) do grupo.
        contracts: Contratos firmados no âmbito do grupo.
    """

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
    """Membro de um grupo: exatamente uma pessoa OU uma instituição (XOR).

    Attributes:
        id: Chave primária.
        group_id: Grupo ao qual o membro pertence.
        person_id: Pessoa membra, se aplicável.
        institution_id: Instituição membra, se aplicável.
        role_in_group: Papel textual opcional.
        joined_at: Momento de entrada no grupo.
        left_at: Momento de saída, se houver.
        group: Relação com ``SponsorshipGroup``.
        person: Relação com ``SponsoredPerson``.
        institution: Relação com ``SponsoredInstitution``.
        occurrence_responsibilities: Responsabilidades em ocorrências.
    """

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
    """Contrato de patrocínio vinculado a um grupo.

    Attributes:
        id: Chave primária.
        contract_number: Número único do contrato.
        group_id: Grupo dono do contrato.
        start_date: Início da vigência.
        end_date: Fim da vigência.
        status: Estado lógico (enum ``ContractStatus``).
        file_storage_key: Chave de armazenamento do PDF/arquivo.
        original_filename: Nome de arquivo original no upload.
        file_checksum: Hash de integridade do arquivo.
        uploaded_at: Momento do upload.
        replaced_by_contract_id: Contrato substituto em cadeia de versões.
        created_by_user_id: Usuário que criou o registro.
        created_at: Criação do registro (UTC).
        updated_at: Última atualização (UTC).
        group: Relação com ``SponsorshipGroup``.
        replaced_by: Autorreferência opcional ao contrato novo.
        clauses: Cláusulas extraídas ou cadastradas.
        requirements: Requisitos de contrapartida.
        extraction_drafts: Rascunhos de extração automática.
    """

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
    """Cláusula textual pertencente a um contrato.

    Attributes:
        id: Chave primária.
        contract_id: Contrato pai.
        clause_identifier: Código curto da cláusula.
        title: Título opcional.
        clause_text: Texto integral opcional.
        display_order: Ordem de apresentação.
        page_reference: Referência de página no documento fonte.
        created_at: Criação do registro (UTC).
        contract: Relação com ``SponsorshipContract``.
        requirements: Requisitos derivados desta cláusula.
    """

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
    """Obrigação de contrapartida derivada de uma cláusula do contrato.

    Attributes:
        id: Chave primária.
        contract_id: Contrato de escopo.
        clause_id: Cláusula de origem.
        requirement_type: Categoria textual do requisito.
        description: Descrição detalhada (texto longo).
        is_recurring: Se gera múltiplas ocorrências ao longo do tempo.
        period_type: Tipo de período quando recorrente.
        period_rule_description: Texto explicando a regra de período.
        expected_occurrences: Meta de ocorrências, se aplicável.
        recurrence_start_date: Início da janela de recorrência.
        recurrence_end_date: Fim da janela de recorrência.
        responsibility_type: Individual ou coletivo (padrão da obrigação).
        status: Estado macro do requisito.
        created_at: Criação do registro (UTC).
        updated_at: Última atualização (UTC).
        contract: Relação com ``SponsorshipContract``.
        clause: Relação com ``ContractClause``.
        occurrences: Ocorrências pontuais de cumprimento.
    """

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
    """Uma instância pontual de cumprimento de um requisito de contrapartida.

    Attributes:
        id: Chave primária.
        requirement_id: Requisito pai.
        period_label: Rótulo do período (ex.: trimestre).
        due_date: Data limite opcional.
        responsibility_type: Individual ou coletivo nesta ocorrência.
        status: Estado do fluxo operacional.
        validated_by_user_id: Usuário que validou, se ``VALIDATED``.
        validated_at: Momento da validação.
        rejection_reason: Motivo quando ``REJECTED``.
        internal_notes: Notas internas.
        created_at: Criação do registro (UTC).
        updated_at: Última atualização (UTC).
        requirement: Relação com ``CounterpartRequirement``.
        responsibles: Membros responsáveis por esta ocorrência.
        deliveries: Entregas registradas.
    """

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
    """Responsável formal por uma ocorrência (sempre um ``GroupMember``).

    Attributes:
        id: Chave primária.
        occurrence_id: Ocorrência associada.
        member_id: Membro do grupo responsável.
        is_primary: Se é o responsável principal.
        role_description: Descrição opcional do papel.
        occurrence: Relação com ``RequirementOccurrence``.
        member: Relação com ``GroupMember``.
    """

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
    """Entrega documentada para uma ocorrência de requisito.

    Attributes:
        id: Chave primária.
        occurrence_id: Ocorrência cumprida ou em cumprimento.
        description: Descrição da entrega (texto longo).
        observations: Observações adicionais.
        delivered_at: Momento em que foi considerada entregue.
        created_by_user_id: Usuário que registrou a entrega.
        created_at: Criação do registro (UTC).
        updated_at: Última atualização (UTC).
        occurrence: Relação com ``RequirementOccurrence``.
        evidences: Evidências anexadas (links, arquivos, etc.).
    """

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
    """Evidência de cumprimento (mídia, link ou metadados de post).

    Attributes:
        id: Chave primária.
        delivery_id: Entrega documentada.
        evidence_type: Tipo de evidência (enum ``EvidenceType``).
        url: URL pública opcional.
        file_storage_key: Chave de armazenamento interno.
        description: Descrição livre.
        platform: Rede ou sistema de origem.
        external_id: Identificador externo (ex.: id do post).
        posted_at: Momento da publicação ou captura.
        created_at: Criação do registro (UTC).
        delivery: Relação com ``Delivery``.
    """

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
    """Rascunho produzido por extração automática de cláusulas e requisitos.

    Usado em fluxos de revisão humana antes de promover dados ao modelo
    canônico do contrato.

    Attributes:
        id: Chave primária.
        contract_id: Contrato fonte da extração.
        extraction_run_id: Identificador da execução de extração (lote).
        source_page: Página aproximada no PDF.
        source_text_excerpt: Trecho bruto do documento.
        extracted_clause_identifier: Identificador sugerido para cláusula.
        extracted_clause_text: Texto sugerido da cláusula.
        extracted_requirement_description: Descrição sugerida de requisito.
        extracted_requirement_type: Tipo sugerido.
        extracted_responsible_hint: Dica textual de responsável.
        extracted_due_date_hint: Dica textual de prazo.
        confidence_score: Confiança numérica do modelo, se houver.
        review_status: Estado da revisão (enum ``DraftReviewStatus``).
        reviewed_by_user_id: Revisor humano.
        reviewed_at: Momento da revisão.
        created_at: Criação do registro (UTC).
        contract: Relação com ``SponsorshipContract``.
    """

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
