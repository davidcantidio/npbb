"""Schemas Pydantic para o módulo de patrocínios (API ``/sponsorship``).

Organização por domínio:

* Pessoa física e instituição patrocinadas
* Perfil social (dono polimórfico)
* Grupo de patrocínio e membros
* Contrato, cláusula e requisito de contrapartida
* Ocorrência de requisito, responsável, entrega e evidência

Cada recurso segue o padrão ``Base`` / ``Create`` / ``Update`` / ``Read`` quando
aplicável. Schemas ``Read`` usam ``from_attributes`` para montagem a partir de
modelos ORM.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Pessoa física
# ---------------------------------------------------------------------------


class SponsoredPersonBase(BaseModel):
    """Campos comuns de pessoa patrocinada (entrada e leitura base).

    Attributes:
        full_name: Nome completo da pessoa.
        cpf: CPF opcional (único quando informado).
        email: E-mail de contato opcional.
        phone: Telefone opcional.
        role: Função ou papel da pessoa no contexto do patrocínio.
        notes: Observações livres opcionais.
    """

    full_name: str = Field(..., max_length=200)
    cpf: Optional[str] = Field(default=None, max_length=14)
    email: Optional[str] = Field(default=None, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=40)
    role: str = Field(..., max_length=80)
    notes: Optional[str] = None


class SponsoredPersonCreate(SponsoredPersonBase):
    """Payload de criação de pessoa patrocinada.

    Attributes:
        Mesmos atributos declarados em ``SponsoredPersonBase`` (herança direta;
        sem campos extras nesta classe).
    """

    pass


class SponsoredPersonUpdate(BaseModel):
    """Payload de atualização parcial de pessoa patrocinada.

    Attributes:
        full_name: Novo nome completo, se informado.
        cpf: Novo CPF, se informado.
        email: Novo e-mail, se informado.
        phone: Novo telefone, se informado.
        role: Novo papel, se informado.
        notes: Novas observações, se informado.
    """

    full_name: Optional[str] = Field(default=None, max_length=200)
    cpf: Optional[str] = Field(default=None, max_length=14)
    email: Optional[str] = Field(default=None, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=40)
    role: Optional[str] = Field(default=None, max_length=80)
    notes: Optional[str] = None


class SponsoredPersonRead(SponsoredPersonBase):
    """Resposta de leitura de pessoa patrocinada com métricas agregadas.

    Attributes:
        id: Identificador persistido.
        created_at: Data/hora de criação.
        updated_at: Data/hora da última atualização, se houver.
        groups_count: Quantidade de grupos associados.
        contracts_count: Quantidade de contratos alcançados via grupos.
        social_profiles_count: Quantidade de perfis sociais do dono.
        full_name: Nome completo (herdado da base).
        cpf: CPF (herdado da base).
        email: E-mail (herdado da base).
        phone: Telefone (herdado da base).
        role: Papel (herdado da base).
        notes: Observações (herdado da base).
    """

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    groups_count: int = 0
    contracts_count: int = 0
    social_profiles_count: int = 0

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Instituição
# ---------------------------------------------------------------------------


class SponsoredInstitutionBase(BaseModel):
    """Campos comuns de instituição patrocinada.

    Attributes:
        name: Razão social ou nome fantasia.
        cnpj: CNPJ opcional (único quando informado).
        email: E-mail de contato opcional.
        phone: Telefone opcional.
        notes: Observações livres opcionais.
    """

    name: str = Field(..., max_length=200)
    cnpj: Optional[str] = Field(default=None, max_length=18)
    email: Optional[str] = Field(default=None, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=40)
    notes: Optional[str] = None


class SponsoredInstitutionCreate(SponsoredInstitutionBase):
    """Payload de criação de instituição patrocinada.

    Attributes:
        Mesmos atributos declarados em ``SponsoredInstitutionBase`` (herança
        direta; sem campos extras nesta classe).
    """

    pass


class SponsoredInstitutionUpdate(BaseModel):
    """Payload de atualização parcial de instituição patrocinada.

    Attributes:
        name: Novo nome, se informado.
        cnpj: Novo CNPJ, se informado.
        email: Novo e-mail, se informado.
        phone: Novo telefone, se informado.
        notes: Novas observações, se informado.
    """

    name: Optional[str] = Field(default=None, max_length=200)
    cnpj: Optional[str] = Field(default=None, max_length=18)
    email: Optional[str] = Field(default=None, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=40)
    notes: Optional[str] = None


class SponsoredInstitutionRead(SponsoredInstitutionBase):
    """Resposta de leitura de instituição com métricas agregadas.

    Attributes:
        id: Identificador persistido.
        created_at: Data/hora de criação.
        updated_at: Data/hora da última atualização, se houver.
        groups_count: Quantidade de grupos associados.
        contracts_count: Quantidade de contratos alcançados via grupos.
        social_profiles_count: Quantidade de perfis sociais do dono.
        name: Nome (herdado da base).
        cnpj: CNPJ (herdado da base).
        email: E-mail (herdado da base).
        phone: Telefone (herdado da base).
        notes: Observações (herdado da base).
    """

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    groups_count: int = 0
    contracts_count: int = 0
    social_profiles_count: int = 0

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Perfil social
# ---------------------------------------------------------------------------


class SocialProfileBase(BaseModel):
    """Campos comuns de perfil em rede social vinculado a um dono.

    Attributes:
        owner_type: Tipo de dono (pessoa ou instituição), como string ou enum.
        owner_id: ID do dono na tabela correspondente.
        platform: Nome da plataforma (ex.: Instagram).
        handle: Identificador ou @ na plataforma.
        url: URL completa opcional do perfil.
        is_primary: Se este perfil é o principal do dono.
    """

    owner_type: str
    owner_id: int
    platform: str = Field(..., max_length=60)
    handle: str = Field(..., max_length=120)
    url: Optional[str] = Field(default=None, max_length=500)
    is_primary: bool = False


class SocialProfileCreate(SocialProfileBase):
    """Payload de criação de perfil social.

    Attributes:
        Mesmos atributos declarados em ``SocialProfileBase`` (herança direta;
        sem campos extras nesta classe).
    """

    pass


class SocialProfileUpdate(BaseModel):
    """Payload de atualização parcial de perfil social.

    Attributes:
        platform: Nova plataforma, se informada.
        handle: Novo handle, se informado.
        url: Nova URL, se informada.
        is_primary: Novo flag de principal, se informado.
    """

    platform: Optional[str] = Field(default=None, max_length=60)
    handle: Optional[str] = Field(default=None, max_length=120)
    url: Optional[str] = Field(default=None, max_length=500)
    is_primary: Optional[bool] = None


class SocialProfileRead(SocialProfileBase):
    """Resposta de leitura de perfil social.

    Attributes:
        id: Identificador persistido.
        created_at: Data/hora de criação.
        owner_type: Tipo de dono (herdado da base).
        owner_id: ID do dono (herdado da base).
        platform: Plataforma (herdado da base).
        handle: Handle (herdado da base).
        url: URL (herdado da base).
        is_primary: Flag principal (herdado da base).
    """

    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Grupo
# ---------------------------------------------------------------------------


class SponsorshipGroupBase(BaseModel):
    """Campos comuns de grupo de patrocínio.

    Attributes:
        name: Nome do grupo.
        description: Descrição opcional.
    """

    name: str = Field(..., max_length=200)
    description: Optional[str] = None


class SponsorshipGroupCreate(SponsorshipGroupBase):
    """Payload de criação de grupo sem vínculo inicial a dono.

    Attributes:
        Mesmos atributos declarados em ``SponsorshipGroupBase`` (herança
        direta; sem campos extras nesta classe).
    """

    pass


class OwnerLinkedGroupCreate(SponsorshipGroupBase):
    """Payload de criação de grupo já vinculado a pessoa ou instituição membra.

    Attributes:
        role_in_group: Papel do dono no novo grupo (opcional).
        name: Nome do grupo (herdado da base).
        description: Descrição (herdado da base).
    """

    role_in_group: Optional[str] = Field(default=None, max_length=120)


class SponsorshipGroupUpdate(BaseModel):
    """Payload de atualização parcial de grupo.

    Attributes:
        name: Novo nome, se informado.
        description: Nova descrição, se informada.
    """

    name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = None


class SponsorshipGroupRead(SponsorshipGroupBase):
    """Resposta de leitura de grupo com contagens agregadas.

    Attributes:
        id: Identificador persistido.
        created_at: Data/hora de criação.
        updated_at: Data/hora da última atualização, se houver.
        members_count: Quantidade de membros no grupo.
        contracts_count: Quantidade de contratos do grupo.
        name: Nome (herdado da base).
        description: Descrição (herdado da base).
    """

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    members_count: int = 0
    contracts_count: int = 0

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Membro do grupo
# ---------------------------------------------------------------------------


class GroupMemberBase(BaseModel):
    """Campos comuns de membro de grupo (pessoa OU instituição).

    Attributes:
        group_id: Grupo ao qual o membro pertence.
        person_id: ID da pessoa membra, se aplicável.
        institution_id: ID da instituição membra, se aplicável.
        role_in_group: Papel opcional dentro do grupo.
    """

    group_id: int
    person_id: Optional[int] = None
    institution_id: Optional[int] = None
    role_in_group: Optional[str] = Field(default=None, max_length=120)


class GroupMemberCreate(GroupMemberBase):
    """Payload de criação de membro.

    Attributes:
        Mesmos atributos declarados em ``GroupMemberBase`` (herança direta;
        sem campos extras nesta classe).
    """

    pass


class GroupMemberUpdate(BaseModel):
    """Payload de atualização parcial de membro.

    Attributes:
        role_in_group: Novo papel, se informado.
        person_id: Novo vínculo de pessoa, se informado (mutuamente exclusivo
            com instituição conforme regras da API).
        institution_id: Novo vínculo de instituição, se informado.
    """

    role_in_group: Optional[str] = Field(default=None, max_length=120)
    person_id: Optional[int] = None
    institution_id: Optional[int] = None


class GroupMemberRead(BaseModel):
    """Resposta de leitura de membro de grupo.

    Attributes:
        id: Identificador persistido.
        group_id: Grupo associado.
        person_id: Pessoa membra, se houver.
        institution_id: Instituição membra, se houver.
        role_in_group: Papel no grupo.
        joined_at: Data/hora de entrada no grupo.
        left_at: Data/hora de saída, se aplicável.
    """

    id: int
    group_id: int
    person_id: Optional[int] = None
    institution_id: Optional[int] = None
    role_in_group: Optional[str]
    joined_at: datetime
    left_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Contrato
# ---------------------------------------------------------------------------


class SponsorshipContractBase(BaseModel):
    """Campos comuns de contrato de patrocínio.

    Attributes:
        contract_number: Número ou código único do contrato.
        group_id: Grupo dono do contrato.
        start_date: Data de início da vigência.
        end_date: Data de fim da vigência.
        status: Status textual (ex.: active, inactive, archived).
        file_storage_key: Chave de armazenamento do arquivo, se houver.
        original_filename: Nome original do arquivo enviado.
        file_checksum: Hash de integridade do arquivo.
        uploaded_at: Momento do upload do arquivo.
        replaced_by_contract_id: ID do contrato substituto, em cadeia de
            versões.
    """

    contract_number: str = Field(..., max_length=80)
    group_id: int
    start_date: date
    end_date: date
    status: Optional[str] = "active"
    file_storage_key: Optional[str] = Field(default=None, max_length=500)
    original_filename: Optional[str] = Field(default=None, max_length=255)
    file_checksum: Optional[str] = Field(default=None, max_length=128)
    uploaded_at: Optional[datetime] = None
    replaced_by_contract_id: Optional[int] = None


class SponsorshipContractCreate(SponsorshipContractBase):
    """Payload de criação de contrato.

    Attributes:
        Mesmos atributos declarados em ``SponsorshipContractBase`` (herança
        direta; sem campos extras nesta classe).
    """

    pass


class SponsorshipContractUpdate(BaseModel):
    """Payload de atualização parcial de contrato.

    Attributes:
        status: Novo status, se informado.
        end_date: Nova data de término, se informada.
        file_storage_key: Nova chave de armazenamento, se informada.
        original_filename: Novo nome de arquivo, se informado.
        file_checksum: Novo checksum, se informado.
        uploaded_at: Novo instante de upload, se informado.
        replaced_by_contract_id: Novo vínculo de substituição, se informado.
    """

    status: Optional[str] = None
    end_date: Optional[date] = None
    file_storage_key: Optional[str] = Field(default=None, max_length=500)
    original_filename: Optional[str] = Field(default=None, max_length=255)
    file_checksum: Optional[str] = Field(default=None, max_length=128)
    uploaded_at: Optional[datetime] = None
    replaced_by_contract_id: Optional[int] = None


class SponsorshipContractRead(BaseModel):
    """Resposta de leitura de contrato com auditoria e contagens.

    Attributes:
        id: Identificador persistido.
        contract_number: Número do contrato.
        group_id: Grupo dono.
        start_date: Início da vigência.
        end_date: Fim da vigência.
        status: Status atual.
        file_storage_key: Chave de armazenamento do arquivo.
        original_filename: Nome original do arquivo.
        file_checksum: Checksum do arquivo.
        uploaded_at: Momento do upload.
        replaced_by_contract_id: Contrato substituto, se houver.
        created_by_user_id: Usuário que criou o registro, se rastreado.
        created_at: Data/hora de criação.
        updated_at: Data/hora da última atualização.
        clauses_count: Quantidade de cláusulas.
        requirements_count: Quantidade de requisitos de contrapartida.
    """

    id: int
    contract_number: str
    group_id: int
    start_date: date
    end_date: date
    status: str
    file_storage_key: Optional[str] = None
    original_filename: Optional[str] = None
    file_checksum: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    replaced_by_contract_id: Optional[int] = None
    created_by_user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    clauses_count: int = 0
    requirements_count: int = 0

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Cláusula
# ---------------------------------------------------------------------------


class ContractClauseBase(BaseModel):
    """Campos comuns de cláusula contratual.

    Attributes:
        contract_id: Contrato ao qual a cláusula pertence.
        clause_identifier: Código curto identificador da cláusula.
        title: Título opcional.
        clause_text: Texto integral opcional.
        display_order: Ordem de exibição na UI ou documentos.
        page_reference: Referência de página no PDF ou documento fonte.
    """

    contract_id: int
    clause_identifier: str = Field(..., max_length=40)
    title: Optional[str] = Field(default=None, max_length=300)
    clause_text: Optional[str] = None
    display_order: int = 0
    page_reference: Optional[str] = Field(default=None, max_length=40)


class ContractClauseCreate(ContractClauseBase):
    """Payload de criação de cláusula.

    Attributes:
        Mesmos atributos declarados em ``ContractClauseBase`` (herança direta;
        sem campos extras nesta classe).
    """

    pass


class ContractClauseUpdate(BaseModel):
    """Payload de atualização parcial de cláusula.

    Attributes:
        title: Novo título, se informado.
        clause_text: Novo texto, se informado.
        display_order: Nova ordem, se informada.
        page_reference: Nova referência de página, se informada.
    """

    title: Optional[str] = Field(default=None, max_length=300)
    clause_text: Optional[str] = None
    display_order: Optional[int] = None
    page_reference: Optional[str] = Field(default=None, max_length=40)


class ContractClauseRead(BaseModel):
    """Resposta de leitura de cláusula.

    Attributes:
        id: Identificador persistido.
        contract_id: Contrato associado.
        clause_identifier: Código da cláusula.
        title: Título.
        clause_text: Texto.
        display_order: Ordem de exibição.
        page_reference: Referência de página.
        created_at: Data/hora de criação.
    """

    id: int
    contract_id: int
    clause_identifier: str
    title: Optional[str] = None
    clause_text: Optional[str] = None
    display_order: int
    page_reference: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Requisito de contrapartida
# ---------------------------------------------------------------------------


class CounterpartRequirementBase(BaseModel):
    """Campos comuns de requisito de contrapartida vinculado a cláusula.

    Attributes:
        contract_id: Contrato de escopo.
        clause_id: Cláusula que fundamenta o requisito.
        requirement_type: Tipo ou categoria do requisito.
        description: Descrição detalhada da obrigação.
        is_recurring: Se o requisito se repete ao longo do tempo.
        period_type: Tipo de período (se recorrente).
        period_rule_description: Texto explicando a regra de período.
        expected_occurrences: Número esperado de ocorrências, se aplicável.
        recurrence_start_date: Início da recorrência.
        recurrence_end_date: Fim da recorrência.
        responsibility_type: individual ou collective.
        status: Status do requisito (ex.: planned, fulfilled).
    """

    contract_id: int
    clause_id: int
    requirement_type: str = Field(..., max_length=120)
    description: str
    is_recurring: bool = False
    period_type: Optional[str] = None
    period_rule_description: Optional[str] = None
    expected_occurrences: Optional[int] = None
    recurrence_start_date: Optional[date] = None
    recurrence_end_date: Optional[date] = None
    responsibility_type: str = "individual"
    status: str = "planned"


class CounterpartRequirementCreate(CounterpartRequirementBase):
    """Payload de criação de requisito de contrapartida.

    Attributes:
        Mesmos atributos declarados em ``CounterpartRequirementBase`` (herança
        direta; sem campos extras nesta classe).
    """

    pass


class CounterpartRequirementUpdate(BaseModel):
    """Payload de atualização parcial de requisito.

    Attributes:
        requirement_type: Novo tipo, se informado.
        description: Nova descrição, se informada.
        is_recurring: Novo flag de recorrência, se informado.
        period_type: Novo tipo de período, se informado.
        period_rule_description: Nova regra textual, se informada.
        expected_occurrences: Nova expectativa de ocorrências, se informada.
        recurrence_start_date: Novo início, se informado.
        recurrence_end_date: Novo fim, se informado.
        responsibility_type: Novo tipo de responsabilidade, se informado.
        status: Novo status, se informado.
    """

    requirement_type: Optional[str] = Field(default=None, max_length=120)
    description: Optional[str] = None
    is_recurring: Optional[bool] = None
    period_type: Optional[str] = None
    period_rule_description: Optional[str] = None
    expected_occurrences: Optional[int] = None
    recurrence_start_date: Optional[date] = None
    recurrence_end_date: Optional[date] = None
    responsibility_type: Optional[str] = None
    status: Optional[str] = None


class CounterpartRequirementRead(BaseModel):
    """Resposta de leitura de requisito com contagem de ocorrências.

    Attributes:
        id: Identificador persistido.
        contract_id: Contrato associado.
        clause_id: Cláusula associada.
        requirement_type: Tipo do requisito.
        description: Descrição.
        is_recurring: Flag de recorrência.
        period_type: Tipo de período.
        period_rule_description: Regra de período.
        expected_occurrences: Ocorrências esperadas.
        recurrence_start_date: Início da recorrência.
        recurrence_end_date: Fim da recorrência.
        responsibility_type: Tipo de responsabilidade.
        status: Status atual.
        created_at: Data/hora de criação.
        updated_at: Data/hora da última atualização.
        occurrences_count: Quantidade de ocorrências registradas.
    """

    id: int
    contract_id: int
    clause_id: int
    requirement_type: str
    description: str
    is_recurring: bool
    period_type: Optional[str] = None
    period_rule_description: Optional[str] = None
    expected_occurrences: Optional[int] = None
    recurrence_start_date: Optional[date] = None
    recurrence_end_date: Optional[date] = None
    responsibility_type: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    occurrences_count: int = 0

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Ocorrência de requisito
# ---------------------------------------------------------------------------


class RequirementOccurrenceBase(BaseModel):
    """Campos comuns de ocorrência de cumprimento de requisito.

    Attributes:
        requirement_id: Requisito pai.
        period_label: Rótulo do período (ex.: trimestre ou ano-mês).
        due_date: Data limite opcional.
        responsibility_type: individual ou collective para esta ocorrência.
        status: Status (ex.: pending, delivered, validated).
        internal_notes: Notas internas opcionais.
    """

    requirement_id: int
    period_label: Optional[str] = Field(default=None, max_length=80)
    due_date: Optional[date] = None
    responsibility_type: str = "individual"
    status: str = "pending"
    internal_notes: Optional[str] = None


class RequirementOccurrenceCreate(RequirementOccurrenceBase):
    """Payload de criação de ocorrência.

    Attributes:
        Mesmos atributos declarados em ``RequirementOccurrenceBase`` (herança
        direta; sem campos extras nesta classe).
    """

    pass


class RequirementOccurrenceUpdate(BaseModel):
    """Payload de atualização parcial de ocorrência.

    Attributes:
        status: Novo status, se informado.
        period_label: Novo rótulo, se informado.
        due_date: Nova data limite, se informada.
        responsibility_type: Novo tipo de responsabilidade, se informado.
        internal_notes: Novas notas internas, se informadas.
        rejection_reason: Motivo de rejeição quando status for rejeitado.
    """

    status: Optional[str] = None
    period_label: Optional[str] = Field(default=None, max_length=80)
    due_date: Optional[date] = None
    responsibility_type: Optional[str] = None
    internal_notes: Optional[str] = None
    rejection_reason: Optional[str] = None


class RequirementOccurrenceRead(BaseModel):
    """Resposta de leitura de ocorrência com validação e rejeição.

    Attributes:
        id: Identificador persistido.
        requirement_id: Requisito associado.
        period_label: Rótulo do período.
        due_date: Data limite.
        responsibility_type: Tipo de responsabilidade.
        status: Status atual.
        validated_by_user_id: Usuário que validou, se status validado.
        validated_at: Momento da validação.
        rejection_reason: Motivo da rejeição, se houver.
        internal_notes: Notas internas.
        created_at: Data/hora de criação.
        updated_at: Data/hora da última atualização.
    """

    id: int
    requirement_id: int
    period_label: Optional[str] = None
    due_date: Optional[date] = None
    responsibility_type: str
    status: str
    validated_by_user_id: Optional[int] = None
    validated_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    internal_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Responsável por ocorrência
# ---------------------------------------------------------------------------


class OccurrenceResponsibleBase(BaseModel):
    """Campos comuns de responsável por ocorrência (membro do grupo).

    Attributes:
        occurrence_id: Ocorrência associada.
        member_id: Membro do grupo responsável.
        is_primary: Se é o responsável principal.
        role_description: Descrição opcional do papel nesta ocorrência.
    """

    occurrence_id: int
    member_id: int
    is_primary: bool = False
    role_description: Optional[str] = Field(default=None, max_length=200)


class OccurrenceResponsibleCreate(OccurrenceResponsibleBase):
    """Payload de criação de responsável pela ocorrência.

    Attributes:
        Mesmos atributos declarados em ``OccurrenceResponsibleBase`` (herança
        direta; sem campos extras nesta classe).
    """

    pass


class OccurrenceResponsibleRead(BaseModel):
    """Resposta de leitura de responsável por ocorrência.

    Attributes:
        id: Identificador persistido.
        occurrence_id: Ocorrência associada.
        member_id: Membro responsável.
        is_primary: Flag de principal.
        role_description: Descrição do papel.
    """

    id: int
    occurrence_id: int
    member_id: int
    is_primary: bool
    role_description: Optional[str] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Entrega
# ---------------------------------------------------------------------------


class DeliveryBase(BaseModel):
    """Campos comuns de entrega vinculada a ocorrência.

    Attributes:
        occurrence_id: Ocorrência cumprida ou em cumprimento.
        description: Descrição da entrega.
        observations: Observações adicionais opcionais.
    """

    occurrence_id: int
    description: str
    observations: Optional[str] = None


class DeliveryCreate(DeliveryBase):
    """Payload de criação de entrega.

    Attributes:
        Mesmos atributos declarados em ``DeliveryBase`` (herança direta; sem
        campos extras nesta classe).
    """

    pass


class DeliveryUpdate(BaseModel):
    """Payload de atualização parcial de entrega.

    Attributes:
        description: Nova descrição, se informada.
        observations: Novas observações, se informadas.
    """

    description: Optional[str] = None
    observations: Optional[str] = None


class DeliveryRead(BaseModel):
    """Resposta de leitura de entrega.

    Attributes:
        id: Identificador persistido.
        occurrence_id: Ocorrência associada.
        description: Descrição.
        observations: Observações.
        delivered_at: Momento em que foi marcada como entregue, se houver.
        created_by_user_id: Usuário criador, se rastreado.
        created_at: Data/hora de criação.
        updated_at: Data/hora da última atualização.
    """

    id: int
    occurrence_id: int
    description: str
    observations: Optional[str] = None
    delivered_at: Optional[datetime] = None
    created_by_user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Evidência de entrega
# ---------------------------------------------------------------------------


class DeliveryEvidenceBase(BaseModel):
    """Campos comuns de evidência anexada a uma entrega.

    Attributes:
        delivery_id: Entrega documentada.
        evidence_type: Tipo de evidência (link, arquivo, texto, etc.).
        url: URL pública opcional.
        file_storage_key: Chave de armazenamento interno opcional.
        description: Descrição livre opcional.
        platform: Plataforma de origem (ex.: rede social).
        external_id: Identificador externo opcional (id do post).
        posted_at: Momento da publicação ou captura.
    """

    delivery_id: int
    evidence_type: str
    url: Optional[str] = Field(default=None, max_length=1000)
    file_storage_key: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = None
    platform: Optional[str] = Field(default=None, max_length=60)
    external_id: Optional[str] = Field(default=None, max_length=200)
    posted_at: Optional[datetime] = None


class DeliveryEvidenceCreate(DeliveryEvidenceBase):
    """Payload de criação de evidência.

    Attributes:
        Mesmos atributos declarados em ``DeliveryEvidenceBase`` (herança
        direta; sem campos extras nesta classe).
    """

    pass


class DeliveryEvidenceRead(BaseModel):
    """Resposta de leitura de evidência de entrega.

    Attributes:
        id: Identificador persistido.
        delivery_id: Entrega associada.
        evidence_type: Tipo da evidência.
        url: URL.
        file_storage_key: Chave de armazenamento.
        description: Descrição.
        platform: Plataforma.
        external_id: ID externo.
        posted_at: Momento da publicação.
        created_at: Data/hora de criação do registro.
    """

    id: int
    delivery_id: int
    evidence_type: str
    url: Optional[str] = None
    file_storage_key: Optional[str] = None
    description: Optional[str] = None
    platform: Optional[str] = None
    external_id: Optional[str] = None
    posted_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
