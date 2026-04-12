"""Rotas REST do domínio de patrocínios (NPBB).

Expõe operações de criação, leitura, atualização e exclusão para pessoas e
instituições patrocinadas, perfis sociais, grupos de patrocínio, membros,
contratos, cláusulas, requisitos de contrapartida, ocorrências, responsáveis,
entregas e evidências. Todas as rotas usam o prefixo ``/sponsorship`` e exigem
usuário autenticado via ``Depends(get_current_user)`` configurado no
``APIRouter``.
"""

from __future__ import annotations

from typing import Any, Optional, cast

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import distinct as sa_distinct
from sqlalchemy import func as sa_func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.sponsorship_models import (
    ContractClause,
    ContractStatus,
    CounterpartRequirement,
    Delivery,
    DeliveryEvidence,
    EvidenceType,
    GroupMember,
    OccurrenceResponsible,
    OccurrenceStatus,
    OwnerType,
    PeriodType,
    RequirementOccurrence,
    RequirementStatus,
    ResponsibilityType,
    SocialProfile,
    SponsoredInstitution,
    SponsoredPerson,
    SponsorshipContract,
    SponsorshipGroup,
    now_utc,
)
from app.schemas.sponsorship import (
    ContractClauseCreate,
    ContractClauseRead,
    ContractClauseUpdate,
    CounterpartRequirementCreate,
    CounterpartRequirementRead,
    CounterpartRequirementUpdate,
    DeliveryCreate,
    DeliveryEvidenceCreate,
    DeliveryEvidenceRead,
    DeliveryRead,
    DeliveryUpdate,
    GroupMemberCreate,
    GroupMemberRead,
    GroupMemberUpdate,
    OwnerLinkedGroupCreate,
    OccurrenceResponsibleBase,
    OccurrenceResponsibleRead,
    RequirementOccurrenceCreate,
    RequirementOccurrenceRead,
    RequirementOccurrenceUpdate,
    SocialProfileCreate,
    SocialProfileRead,
    SocialProfileUpdate,
    SponsoredInstitutionCreate,
    SponsoredInstitutionRead,
    SponsoredInstitutionUpdate,
    SponsoredPersonCreate,
    SponsoredPersonRead,
    SponsoredPersonUpdate,
    SponsorshipContractCreate,
    SponsorshipContractRead,
    SponsorshipContractUpdate,
    SponsorshipGroupCreate,
    SponsorshipGroupRead,
    SponsorshipGroupUpdate,
)

router = APIRouter(
    prefix="/sponsorship",
    tags=["sponsorship"],
    dependencies=[Depends(get_current_user)],
)


def _db(session: Session = Depends(get_session)) -> Session:
    """Fornece a sessão de banco injetada para os handlers deste router.

    Args:
        session: Sessão SQLModel obtida via ``get_session``.

    Returns:
        Instância de ``Session`` para execução de consultas e transações.
    """
    return session


def _scalar_count(db: Session, stmt: Any) -> int:
    """Normaliza o resultado de ``select(func.count(...))`` para ``int``.

    Args:
        db: Sessão ativa do banco de dados.
        stmt: Instrução SQLAlchemy/SQLModel de contagem.

    Returns:
        Contagem inteira (0 se não houver linha ou valor nulo).
    """
    row = db.exec(stmt).first()
    if row is None:
        return 0
    if isinstance(row, (int, float)):
        return int(row)
    if isinstance(row, tuple):
        return int(row[0])
    return int(cast(Any, row)[0])


def _parse_enum(label: str, value: str, enum_cls: type) -> Any:
    """Converte texto em membro de enum, com mensagem de erro padronizada.

    Args:
        label: Nome do campo (aparece na mensagem de erro).
        value: Valor recebido na requisição.
        enum_cls: Classe ``Enum`` de destino.

    Returns:
        Membro válido de ``enum_cls``.

    Raises:
        HTTPException: Com status 400 se ``value`` não for um membro válido.
    """
    try:
        return enum_cls(value)
    except ValueError as exc:
        members = list(enum_cls)  # type: ignore[arg-type]
        allowed = ", ".join(sorted(getattr(m, "value", str(m)) for m in members))
        raise HTTPException(
            status_code=400,
            detail=f"{label} invalido: {value!r}. Valores permitidos: {allowed}.",
        ) from exc


def _normalize_optional_text(value: Any) -> Any:
    """Remove espaços de strings opcionais e trata vazio como ausência.

    Args:
        value: Valor bruto (tipicamente de payload JSON).

    Returns:
        ``None`` se for string vazia após ``strip``; caso contrário o valor
        normalizado ou o próprio ``value`` se não for ``str``.
    """
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


def _integrity_error(message: str) -> HTTPException:
    """Monta resposta HTTP 400 para violações de regra de negócio.

    Args:
        message: Texto explicativo para o cliente.

    Returns:
        Instância de ``HTTPException`` com corpo ``code``/``message``.
    """
    return HTTPException(
        status_code=400,
        detail={"code": "INTEGRITY", "message": message},
    )


def _count_occurrence_responsibles(db: Session, occ_id: int) -> int:
    """Conta responsáveis associados a uma ocorrência de requisito.

    Args:
        db: Sessão ativa do banco de dados.
        occ_id: Identificador da ocorrência.

    Returns:
        Número de registros em ``OccurrenceResponsible`` para a ocorrência.
    """
    return _scalar_count(
        db,
        select(sa_func.count(OccurrenceResponsible.id)).where(
            OccurrenceResponsible.occurrence_id == occ_id
        ),
    )


def _assert_occurrence_responsibility_integrity(
    *,
    responsibility_type: ResponsibilityType,
    responsible_count: int,
    status: OccurrenceStatus,
) -> None:
    """Garante cardinalidade de responsáveis conforme tipo e status operacional.

    Para status em revisão, entregue ou validado, exige exatamente um
    responsável se ``individual`` ou pelo menos dois se ``collective``.

    Args:
        responsibility_type: Individual ou coletivo.
        responsible_count: Quantidade atual de responsáveis.
        status: Status da ocorrência após a operação pretendida.

    Raises:
        HTTPException: Com status 400 e código ``INTEGRITY`` se a regra for
            violada.
    """
    operational_statuses = {
        OccurrenceStatus.IN_REVIEW,
        OccurrenceStatus.DELIVERED,
        OccurrenceStatus.VALIDATED,
    }
    if status not in operational_statuses:
        return
    if responsibility_type == ResponsibilityType.INDIVIDUAL and responsible_count != 1:
        raise _integrity_error(
            f"responsibility_type=individual exige exatamente 1 responsavel "
            f"(encontrados: {responsible_count})."
        )
    if responsibility_type == ResponsibilityType.COLLECTIVE and responsible_count < 2:
        raise _integrity_error(
            f"responsibility_type=collective exige 2 ou mais responsaveis "
            f"(encontrados: {responsible_count})."
        )


def _get_social_profile_owner(
    db: Session, owner_type_value: str | OwnerType, owner_id: int
) -> OwnerType:
    """Valida existência do dono (pessoa ou instituição) de um perfil social.

    Args:
        db: Sessão ativa do banco de dados.
        owner_type_value: Tipo de dono (string ou enum).
        owner_id: Identificador do dono na tabela correspondente.

    Returns:
        ``OwnerType`` resolvido após validação.

    Raises:
        HTTPException: 400 se ``owner_type`` for inválido; 404 se o dono não
            existir.
    """
    owner_type = (
        owner_type_value
        if isinstance(owner_type_value, OwnerType)
        else _parse_enum("owner_type", str(owner_type_value), OwnerType)
    )
    if owner_type == OwnerType.PERSON:
        owner = db.get(SponsoredPerson, owner_id)
        if not owner:
            raise HTTPException(status_code=404, detail="Pessoa nao encontrada")
        return owner_type

    owner = db.get(SponsoredInstitution, owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Instituicao nao encontrada")
    return owner_type


def _group_read(db: Session, group: SponsorshipGroup) -> SponsorshipGroupRead:
    """Monta leitura de grupo com contagens agregadas de membros e contratos.

    Args:
        db: Sessão ativa do banco de dados.
        group: Entidade ``SponsorshipGroup`` persistida.

    Returns:
        Schema ``SponsorshipGroupRead`` com ``members_count`` e
        ``contracts_count``.
    """
    members_count = _scalar_count(
        db, select(sa_func.count(GroupMember.id)).where(GroupMember.group_id == group.id)
    )
    contracts_count = _scalar_count(
        db,
        select(sa_func.count(SponsorshipContract.id)).where(SponsorshipContract.group_id == group.id),
    )
    return SponsorshipGroupRead.model_validate(
        {**group.model_dump(), "members_count": members_count, "contracts_count": contracts_count}
    )


def _owner_counts(db: Session, owner_type: OwnerType, owner_id: int) -> dict[str, int]:
    """Calcula contagens de grupos, contratos e perfis sociais para um dono.

    Args:
        db: Sessão ativa do banco de dados.
        owner_type: Pessoa física ou instituição.
        owner_id: Identificador do dono.

    Returns:
        Dicionário com chaves ``groups_count``, ``contracts_count`` e
        ``social_profiles_count``.
    """
    if owner_type == OwnerType.PERSON:
        membership_filter = GroupMember.person_id == owner_id
    else:
        membership_filter = GroupMember.institution_id == owner_id

    groups_count = _scalar_count(
        db,
        select(sa_func.count(sa_distinct(GroupMember.group_id))).where(membership_filter),
    )
    contracts_count = _scalar_count(
        db,
        select(sa_func.count(sa_distinct(SponsorshipContract.id)))
        .select_from(SponsorshipContract)
        .join(GroupMember, GroupMember.group_id == SponsorshipContract.group_id)
        .where(membership_filter),
    )
    social_profiles_count = _scalar_count(
        db,
        select(sa_func.count(SocialProfile.id)).where(
            SocialProfile.owner_type == owner_type,
            SocialProfile.owner_id == owner_id,
        ),
    )
    return {
        "groups_count": groups_count,
        "contracts_count": contracts_count,
        "social_profiles_count": social_profiles_count,
    }


def _list_groups_for_owner(
    db: Session, owner_type: OwnerType, owner_id: int
) -> list[SponsorshipGroupRead]:
    """Lista grupos nos quais a pessoa ou instituição é membro.

    Args:
        db: Sessão ativa do banco de dados.
        owner_type: Pessoa ou instituição.
        owner_id: Identificador do dono.

    Returns:
        Lista ordenada por nome de ``SponsorshipGroupRead`` com contagens.
    """
    if owner_type == OwnerType.PERSON:
        membership_filter = GroupMember.person_id == owner_id
    else:
        membership_filter = GroupMember.institution_id == owner_id

    stmt = (
        select(SponsorshipGroup)
        .join(GroupMember, GroupMember.group_id == SponsorshipGroup.id)
        .where(membership_filter)
        .distinct()
        .order_by(SponsorshipGroup.name)
    )
    return [_group_read(db, group) for group in db.exec(stmt).all()]


# ===========================================================================
# Pessoas patrocinadas
# ===========================================================================


@router.get("/persons", response_model=list[SponsoredPersonRead])
def list_persons(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(_db),
):
    """Lista pessoas patrocinadas com paginação e contagens agregadas.

    Requer usuário autenticado (dependência do router).

    Args:
        skip: Registros a pular (paginação).
        limit: Tamanho máximo da página.
        db: Sessão de banco.

    Returns:
        Lista de ``SponsoredPersonRead`` ordenada por nome completo.
    """
    items = db.exec(
        select(SponsoredPerson).order_by(SponsoredPerson.full_name).offset(skip).limit(limit)
    ).all()
    return [
        SponsoredPersonRead.model_validate({**item.model_dump(), **_owner_counts(db, OwnerType.PERSON, item.id)})
        for item in items
    ]


@router.get("/persons/{person_id}", response_model=SponsoredPersonRead)
def get_person(person_id: int, db: Session = Depends(_db)):
    """Obtém uma pessoa patrocinada por ID com contagens agregadas.

    Requer usuário autenticado (dependência do router).

    Args:
        person_id: Identificador da pessoa.
        db: Sessão de banco.

    Returns:
        ``SponsoredPersonRead`` com grupos, contratos e perfis sociais
        contados.

    Raises:
        HTTPException: 404 se a pessoa não existir.
    """
    item = db.get(SponsoredPerson, person_id)
    if not item:
        raise HTTPException(status_code=404, detail="Pessoa nao encontrada")
    return SponsoredPersonRead.model_validate(
        {**item.model_dump(), **_owner_counts(db, OwnerType.PERSON, item.id)}
    )


@router.post("/persons", response_model=SponsoredPersonRead, status_code=201)
def create_person(
    body: SponsoredPersonCreate,
    db: Session = Depends(_db),
):
    """Cria uma nova pessoa patrocinada.

    Requer usuário autenticado (dependência do router).

    Args:
        body: Dados de criação.
        db: Sessão de banco.

    Returns:
        Registro criado como ``SponsoredPersonRead`` (status 201).

    Raises:
        IntegrityError: Se o ``commit`` violar unicidade ou outras constraints
            do banco (ex.: CPF duplicado). Este handler não converte o erro em
            ``HTTPException``.
    """
    obj = SponsoredPerson(**body.model_dump(exclude_unset=True))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return SponsoredPersonRead.model_validate(
        {**obj.model_dump(), **_owner_counts(db, OwnerType.PERSON, obj.id)}
    )


@router.patch("/persons/{person_id}", response_model=SponsoredPersonRead)
def update_person(person_id: int, body: SponsoredPersonUpdate, db: Session = Depends(_db)):
    """Atualiza parcialmente uma pessoa patrocinada.

    Requer usuário autenticado (dependência do router).

    Args:
        person_id: Identificador da pessoa.
        body: Campos a alterar (somente os enviados são aplicados).
        db: Sessão de banco.

    Returns:
        ``SponsoredPersonRead`` após persistência.

    Raises:
        HTTPException: 404 se a pessoa não existir.
        IntegrityError: Se o ``commit`` violar constraints do banco; não há
            tratamento explícito neste endpoint.
    """
    obj = db.get(SponsoredPerson, person_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Pessoa nao encontrada")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    obj.updated_at = now_utc()
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return SponsoredPersonRead.model_validate(
        {**obj.model_dump(), **_owner_counts(db, OwnerType.PERSON, obj.id)}
    )


@router.delete("/persons/{person_id}", status_code=204)
def delete_person(person_id: int, db: Session = Depends(_db)):
    """Remove uma pessoa patrocinada.

    Requer usuário autenticado (dependência do router).

    Args:
        person_id: Identificador da pessoa.
        db: Sessão de banco.

    Returns:
        Resposta vazia com status HTTP 204 (sem corpo JSON).

    Raises:
        HTTPException: 404 se a pessoa não existir.
    """
    obj = db.get(SponsoredPerson, person_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Pessoa nao encontrada")
    db.delete(obj)
    db.commit()


@router.get("/persons/{person_id}/groups", response_model=list[SponsorshipGroupRead])
def list_person_groups(person_id: int, db: Session = Depends(_db)):
    """Lista grupos de patrocínio nos quais a pessoa é membro.

    Requer usuário autenticado (dependência do router).

    Args:
        person_id: Identificador da pessoa.
        db: Sessão de banco.

    Returns:
        Lista de ``SponsorshipGroupRead``.

    Raises:
        HTTPException: 404 se a pessoa não existir.
    """
    person = db.get(SponsoredPerson, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Pessoa nao encontrada")
    return _list_groups_for_owner(db, OwnerType.PERSON, person_id)


@router.post("/persons/{person_id}/groups", response_model=SponsorshipGroupRead, status_code=201)
def create_person_group(person_id: int, body: OwnerLinkedGroupCreate, db: Session = Depends(_db)):
    """Cria um grupo e vincula a pessoa como membro inicial.

    Requer usuário autenticado (dependência do router).

    Args:
        person_id: Pessoa que será membro do novo grupo.
        body: Nome, descrição e papel da pessoa no grupo.
        db: Sessão de banco.

    Returns:
        ``SponsorshipGroupRead`` do grupo criado (status 201).

    Raises:
        HTTPException: 404 se a pessoa não existir.
    """
    person = db.get(SponsoredPerson, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Pessoa nao encontrada")

    group = SponsorshipGroup(
        name=body.name,
        description=body.description,
    )
    db.add(group)
    db.flush()

    membership = GroupMember(
        group_id=group.id,
        person_id=person_id,
        role_in_group=body.role_in_group,
    )
    db.add(membership)
    db.commit()
    db.refresh(group)
    return _group_read(db, group)


# ===========================================================================
# Instituições patrocinadas
# ===========================================================================


@router.get("/institutions", response_model=list[SponsoredInstitutionRead])
def list_institutions(skip: int = 0, limit: int = 100, db: Session = Depends(_db)):
    """Lista instituições patrocinadas com paginação e contagens agregadas.

    Requer usuário autenticado (dependência do router).

    Args:
        skip: Registros a pular.
        limit: Tamanho máximo da página.
        db: Sessão de banco.

    Returns:
        Lista de ``SponsoredInstitutionRead`` ordenada por nome.
    """
    items = db.exec(
        select(SponsoredInstitution).order_by(SponsoredInstitution.name).offset(skip).limit(limit)
    ).all()
    return [
        SponsoredInstitutionRead.model_validate(
            {**item.model_dump(), **_owner_counts(db, OwnerType.INSTITUTION, item.id)}
        )
        for item in items
    ]


@router.get("/institutions/{inst_id}", response_model=SponsoredInstitutionRead)
def get_institution(inst_id: int, db: Session = Depends(_db)):
    """Obtém uma instituição patrocinada por ID com contagens agregadas.

    Requer usuário autenticado (dependência do router).

    Args:
        inst_id: Identificador da instituição.
        db: Sessão de banco.

    Returns:
        ``SponsoredInstitutionRead``.

    Raises:
        HTTPException: 404 se a instituição não existir.
    """
    item = db.get(SponsoredInstitution, inst_id)
    if not item:
        raise HTTPException(status_code=404, detail="Instituicao nao encontrada")
    return SponsoredInstitutionRead.model_validate(
        {**item.model_dump(), **_owner_counts(db, OwnerType.INSTITUTION, item.id)}
    )


@router.post("/institutions", response_model=SponsoredInstitutionRead, status_code=201)
def create_institution(body: SponsoredInstitutionCreate, db: Session = Depends(_db)):
    """Cria uma nova instituição patrocinada.

    Requer usuário autenticado (dependência do router).

    Args:
        body: Dados de criação.
        db: Sessão de banco.

    Returns:
        Registro criado (status 201).

    Raises:
        IntegrityError: Se o ``commit`` violar unicidade ou outras constraints
            do banco (ex.: CNPJ duplicado). Este handler não converte o erro em
            ``HTTPException``.
    """
    obj = SponsoredInstitution(**body.model_dump(exclude_unset=True))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return SponsoredInstitutionRead.model_validate(
        {**obj.model_dump(), **_owner_counts(db, OwnerType.INSTITUTION, obj.id)}
    )


@router.patch("/institutions/{inst_id}", response_model=SponsoredInstitutionRead)
def update_institution(inst_id: int, body: SponsoredInstitutionUpdate, db: Session = Depends(_db)):
    """Atualiza parcialmente uma instituição patrocinada.

    Requer usuário autenticado (dependência do router).

    Args:
        inst_id: Identificador da instituição.
        body: Campos a alterar.
        db: Sessão de banco.

    Returns:
        ``SponsoredInstitutionRead`` após persistência.

    Raises:
        HTTPException: 404 se não existir.
        IntegrityError: Se o ``commit`` violar constraints do banco; não há
            tratamento explícito neste endpoint.
    """
    obj = db.get(SponsoredInstitution, inst_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Instituicao nao encontrada")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    obj.updated_at = now_utc()
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return SponsoredInstitutionRead.model_validate(
        {**obj.model_dump(), **_owner_counts(db, OwnerType.INSTITUTION, obj.id)}
    )


@router.delete("/institutions/{inst_id}", status_code=204)
def delete_institution(inst_id: int, db: Session = Depends(_db)):
    """Remove uma instituição patrocinada.

    Requer usuário autenticado (dependência do router).

    Args:
        inst_id: Identificador da instituição.
        db: Sessão de banco.

    Returns:
        Resposta vazia com status HTTP 204 (sem corpo JSON).

    Raises:
        HTTPException: 404 se a instituição não existir.
    """
    obj = db.get(SponsoredInstitution, inst_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Instituicao nao encontrada")
    db.delete(obj)
    db.commit()


@router.get("/institutions/{inst_id}/groups", response_model=list[SponsorshipGroupRead])
def list_institution_groups(inst_id: int, db: Session = Depends(_db)):
    """Lista grupos nos quais a instituição é membro.

    Requer usuário autenticado (dependência do router).

    Args:
        inst_id: Identificador da instituição.
        db: Sessão de banco.

    Returns:
        Lista de ``SponsorshipGroupRead``.

    Raises:
        HTTPException: 404 se a instituição não existir.
    """
    institution = db.get(SponsoredInstitution, inst_id)
    if not institution:
        raise HTTPException(status_code=404, detail="Instituicao nao encontrada")
    return _list_groups_for_owner(db, OwnerType.INSTITUTION, inst_id)


@router.post(
    "/institutions/{inst_id}/groups", response_model=SponsorshipGroupRead, status_code=201
)
def create_institution_group(
    inst_id: int, body: OwnerLinkedGroupCreate, db: Session = Depends(_db)
):
    """Cria um grupo e vincula a instituição como membro inicial.

    Requer usuário autenticado (dependência do router).

    Args:
        inst_id: Instituição membro do novo grupo.
        body: Nome, descrição e papel da instituição no grupo.
        db: Sessão de banco.

    Returns:
        ``SponsorshipGroupRead`` do grupo criado (status 201).

    Raises:
        HTTPException: 404 se a instituição não existir.
    """
    institution = db.get(SponsoredInstitution, inst_id)
    if not institution:
        raise HTTPException(status_code=404, detail="Instituicao nao encontrada")

    group = SponsorshipGroup(
        name=body.name,
        description=body.description,
    )
    db.add(group)
    db.flush()

    membership = GroupMember(
        group_id=group.id,
        institution_id=inst_id,
        role_in_group=body.role_in_group,
    )
    db.add(membership)
    db.commit()
    db.refresh(group)
    return _group_read(db, group)


# ===========================================================================
# Perfis sociais
# ===========================================================================


@router.get("/social_profiles", response_model=list[SocialProfileRead])
def list_social_profiles(
    owner_type: Optional[str] = None,
    owner_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(_db),
):
    """Lista perfis sociais com filtros opcionais por dono e paginação.

    Requer usuário autenticado (dependência do router).

    Args:
        owner_type: Filtro por tipo de dono (pessoa ou instituição).
        owner_id: Filtro por ID do dono; se ambos forem informados, valida
            existência do dono.
        skip: Registros a pular.
        limit: Tamanho máximo da página.
        db: Sessão de banco.

    Returns:
        Lista de ``SocialProfileRead``.

    Raises:
        HTTPException: 400 se ``owner_type`` for inválido; 404 se o dono
            filtrado não existir.
    """
    q = select(SocialProfile)
    if owner_type:
        parsed_owner_type = _parse_enum("owner_type", owner_type, OwnerType)
        if owner_id is not None:
            _get_social_profile_owner(db, parsed_owner_type, owner_id)
        q = q.where(SocialProfile.owner_type == parsed_owner_type)
    if owner_id is not None:
        q = q.where(SocialProfile.owner_id == owner_id)
    return db.exec(q.offset(skip).limit(limit)).all()


@router.post("/social_profiles", response_model=SocialProfileRead, status_code=201)
def create_social_profile(body: SocialProfileCreate, db: Session = Depends(_db)):
    """Cria um perfil social vinculado a pessoa ou instituição existente.

    Requer usuário autenticado (dependência do router).

    Args:
        body: Dados do perfil, incluindo dono e plataforma.
        db: Sessão de banco.

    Returns:
        ``SocialProfileRead`` criado (status 201).

    Raises:
        HTTPException: 400/404 conforme validação de dono e enums.
    """
    data = body.model_dump(exclude_unset=True)
    data["owner_type"] = _get_social_profile_owner(db, str(data["owner_type"]), data["owner_id"])
    obj = SocialProfile(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/social_profiles/{profile_id}", response_model=SocialProfileRead)
def update_social_profile(
    profile_id: int, body: SocialProfileUpdate, db: Session = Depends(_db)
):
    """Atualiza parcialmente um perfil social.

    Requer usuário autenticado (dependência do router).

    Args:
        profile_id: Identificador do perfil.
        body: Campos a alterar.
        db: Sessão de banco.

    Returns:
        ``SocialProfileRead`` após persistência.

    Raises:
        HTTPException: 404 se o perfil não existir.
    """
    obj = db.get(SocialProfile, profile_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Perfil nao encontrado")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/social_profiles/{profile_id}", status_code=204)
def delete_social_profile(profile_id: int, db: Session = Depends(_db)):
    """Remove um perfil social.

    Requer usuário autenticado (dependência do router).

    Args:
        profile_id: Identificador do perfil.
        db: Sessão de banco.

    Returns:
        Resposta vazia com status HTTP 204 (sem corpo JSON).

    Raises:
        HTTPException: 404 se o perfil não existir.
    """
    obj = db.get(SocialProfile, profile_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Perfil nao encontrado")
    db.delete(obj)
    db.commit()


# ===========================================================================
# Grupos de patrocínio
# ===========================================================================


@router.get("/groups", response_model=list[SponsorshipGroupRead])
def list_groups(skip: int = 0, limit: int = 100, db: Session = Depends(_db)):
    """Lista grupos de patrocínio com contagens de membros e contratos.

    Requer usuário autenticado (dependência do router).

    Args:
        skip: Registros a pular.
        limit: Tamanho máximo da página.
        db: Sessão de banco.

    Returns:
        Lista de ``SponsorshipGroupRead`` ordenada por nome.
    """
    stmt = select(SponsorshipGroup).order_by(SponsorshipGroup.name).offset(skip).limit(limit)
    items = db.exec(stmt).all()
    return [_group_read(db, group) for group in items]


@router.get("/groups/{group_id}", response_model=SponsorshipGroupRead)
def get_group(group_id: int, db: Session = Depends(_db)):
    """Obtém um grupo de patrocínio por ID com contagens agregadas.

    Requer usuário autenticado (dependência do router).

    Args:
        group_id: Identificador do grupo.
        db: Sessão de banco.

    Returns:
        ``SponsorshipGroupRead``.

    Raises:
        HTTPException: 404 se o grupo não existir.
    """
    obj = db.get(SponsorshipGroup, group_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Grupo nao encontrado")
    return _group_read(db, obj)


@router.post("/groups", response_model=SponsorshipGroupRead, status_code=201)
def create_group(body: SponsorshipGroupCreate, db: Session = Depends(_db)):
    """Cria um grupo de patrocínio sem membros iniciais.

    Requer usuário autenticado (dependência do router).

    Args:
        body: Nome e descrição do grupo.
        db: Sessão de banco.

    Returns:
        ``SponsorshipGroupRead`` do grupo criado (status 201).
    """
    obj = SponsorshipGroup(**body.model_dump(exclude_unset=True))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _group_read(db, obj)


@router.patch("/groups/{group_id}", response_model=SponsorshipGroupRead)
def update_group(group_id: int, body: SponsorshipGroupUpdate, db: Session = Depends(_db)):
    """Atualiza parcialmente metadados do grupo de patrocínio.

    Requer usuário autenticado (dependência do router).

    Args:
        group_id: Identificador do grupo.
        body: Campos a alterar.
        db: Sessão de banco.

    Returns:
        ``SponsorshipGroupRead`` após persistência.

    Raises:
        HTTPException: 404 se o grupo não existir.
    """
    obj = db.get(SponsorshipGroup, group_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Grupo nao encontrado")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    obj.updated_at = now_utc()
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _group_read(db, obj)


@router.delete("/groups/{group_id}", status_code=204)
def delete_group(group_id: int, db: Session = Depends(_db)):
    """Remove um grupo de patrocínio.

    Requer usuário autenticado (dependência do router).

    Args:
        group_id: Identificador do grupo.
        db: Sessão de banco.

    Returns:
        Resposta vazia com status HTTP 204 (sem corpo JSON).

    Raises:
        HTTPException: 404 se o grupo não existir.
    """
    obj = db.get(SponsorshipGroup, group_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Grupo nao encontrado")
    db.delete(obj)
    db.commit()


# ===========================================================================
# Membros do grupo
# ===========================================================================


@router.get("/groups/{group_id}/members", response_model=list[GroupMemberRead])
def list_group_members(group_id: int, db: Session = Depends(_db)):
    """Lista membros (pessoa ou instituição) de um grupo.

    Requer usuário autenticado (dependência do router).

    Args:
        group_id: Identificador do grupo.
        db: Sessão de banco.

    Returns:
        Lista de ``GroupMemberRead`` do grupo. Não valida se ``group_id``
        corresponde a um grupo existente (grupo inexistente retorna lista
        vazia).
    """
    return db.exec(
        select(GroupMember).where(GroupMember.group_id == group_id)
    ).all()


@router.post("/groups/{group_id}/members", response_model=GroupMemberRead, status_code=201)
def create_group_member(group_id: int, body: GroupMemberCreate, db: Session = Depends(_db)):
    """Adiciona membro ao grupo (exatamente um entre pessoa ou instituição).

    Requer usuário autenticado (dependência do router).

    Args:
        group_id: Grupo de destino.
        body: Dados do membro; ``group_id`` é definido pela rota.
        db: Sessão de banco.

    Returns:
        ``GroupMemberRead`` criado (status 201).

    Raises:
        HTTPException: 400 se ambos ou nenhum de ``person_id``/``institution_id``
            forem informados, ou em violação de integridade.
    """
    obj_d = body.model_dump(exclude_unset=True)
    obj_d["group_id"] = group_id
    pid = obj_d.get("person_id")
    iid = obj_d.get("institution_id")
    if (pid is None) == (iid is None):
        raise HTTPException(
            status_code=400,
            detail="Informe exatamente um entre person_id ou institution_id.",
        )
    obj = GroupMember(**obj_d)
    db.add(obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        detail = str(exc.orig) if hasattr(exc, "orig") else "Violacao de constraint"
        raise HTTPException(status_code=400, detail={"code": "INTEGRITY", "message": detail})
    db.refresh(obj)
    return obj


@router.patch("/groups/{group_id}/members/{member_id}", response_model=GroupMemberRead)
def update_group_member(
    group_id: int,
    member_id: int,
    body: GroupMemberUpdate,
    db: Session = Depends(_db),
):
    """Atualiza membro do grupo preservando regra XOR pessoa/instituição.

    Requer usuário autenticado (dependência do router).

    Args:
        group_id: Identificador do grupo.
        member_id: Identificador do membro.
        body: Campos a alterar.
        db: Sessão de banco.

    Returns:
        ``GroupMemberRead`` após persistência.

    Raises:
        HTTPException: 404 se o membro não pertencer ao grupo; 400 se a
            combinação pessoa/instituição for inválida.
    """
    obj = db.get(GroupMember, member_id)
    if not obj or obj.group_id != group_id:
        raise HTTPException(status_code=404, detail="Membro nao encontrado")
    changes = body.model_dump(exclude_unset=True)
    # XOR enforcement (same as DB check constraint)
    if changes.get("person_id") is not None or changes.get("institution_id") is not None:
        pid = changes.get("person_id") or obj.person_id
        iid = changes.get("institution_id") or obj.institution_id
        if (pid is None) == (iid is None):
            raise HTTPException(
                status_code=400,
                detail="Informe exatamente um entre person_id ou institution_id.",
            )
    for k, v in changes.items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/groups/{group_id}/members/{member_id}", status_code=204)
def delete_group_member(group_id: int, member_id: int, db: Session = Depends(_db)):
    """Remove um membro do grupo.

    Requer usuário autenticado (dependência do router).

    Args:
        group_id: Identificador do grupo.
        member_id: Identificador do membro.
        db: Sessão de banco.

    Returns:
        Resposta vazia com status HTTP 204 (sem corpo JSON).

    Raises:
        HTTPException: 404 se o membro não existir no grupo.
    """
    obj = db.get(GroupMember, member_id)
    if not obj or obj.group_id != group_id:
        raise HTTPException(status_code=404, detail="Membro nao encontrado")
    db.delete(obj)
    db.commit()


# ===========================================================================
# Contratos
# ===========================================================================


@router.get(
    "/groups/{group_id}/contracts", response_model=list[SponsorshipContractRead]
)
def list_contracts(group_id: int, db: Session = Depends(_db)):
    """Lista contratos de um grupo com contagens de cláusulas e requisitos.

    Requer usuário autenticado (dependência do router).

    Args:
        group_id: Identificador do grupo.
        db: Sessão de banco.

    Returns:
        Lista de ``SponsorshipContractRead`` ordenada por número de contrato.
    """
    stmt = (
        select(SponsorshipContract)
        .where(SponsorshipContract.group_id == group_id)
        .order_by(SponsorshipContract.contract_number)
    )
    items = db.exec(stmt).all()
    reads: list[SponsorshipContractRead] = []
    for c in items:
        cc = _scalar_count(
            db, select(sa_func.count(ContractClause.id)).where(ContractClause.contract_id == c.id)
        )
        rc = _scalar_count(
            db,
            select(sa_func.count(CounterpartRequirement.id)).where(
                CounterpartRequirement.contract_id == c.id
            ),
        )
        reads.append(
            SponsorshipContractRead.model_validate(
                {**c.model_dump(), "clauses_count": cc, "requirements_count": rc}
            )
        )
    return reads


@router.get(
    "/groups/{group_id}/contracts/{contract_id}",
    response_model=SponsorshipContractRead,
)
def get_contract(group_id: int, contract_id: int, db: Session = Depends(_db)):
    """Obtém contrato do grupo com contagens de cláusulas e requisitos.

    Requer usuário autenticado (dependência do router).

    Args:
        group_id: Identificador do grupo.
        contract_id: Identificador do contrato.
        db: Sessão de banco.

    Returns:
        ``SponsorshipContractRead``.

    Raises:
        HTTPException: 404 se o contrato não existir ou não pertencer ao grupo.
    """
    obj = db.get(SponsorshipContract, contract_id)
    if not obj or obj.group_id != group_id:
        raise HTTPException(status_code=404, detail="Contrato nao encontrado")
    cc = _scalar_count(
        db, select(sa_func.count(ContractClause.id)).where(ContractClause.contract_id == obj.id)
    )
    rc = _scalar_count(
        db,
        select(sa_func.count(CounterpartRequirement.id)).where(
            CounterpartRequirement.contract_id == obj.id
        ),
    )
    return SponsorshipContractRead.model_validate(
        {**obj.model_dump(), "clauses_count": cc, "requirements_count": rc}
    )


@router.post(
    "/groups/{group_id}/contracts", response_model=SponsorshipContractRead, status_code=201
)
def create_contract(group_id: int, body: SponsorshipContractCreate, db: Session = Depends(_db)):
    """Cria contrato vinculado ao grupo.

    Requer usuário autenticado (dependência do router).

    Args:
        group_id: Grupo dono do contrato.
        body: Dados do contrato; ``group_id`` é definido pela rota.
        db: Sessão de banco.

    Returns:
        ``SponsorshipContractRead`` com contagens zeradas (status 201).

    Raises:
        HTTPException: 400 em enum inválido ou violação de integridade
            (ex.: número de contrato único).
    """
    obj_d = body.model_dump(exclude_unset=True)
    obj_d["group_id"] = group_id
    st = obj_d.get("status")
    if isinstance(st, str):
        obj_d["status"] = _parse_enum("status", st, ContractStatus)
    obj = SponsorshipContract(**obj_d)
    db.add(obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        detail = str(exc.orig) if hasattr(exc, "orig") else "Violacao de constraint"
        raise HTTPException(status_code=400, detail={"code": "INTEGRITY", "message": detail})
    db.refresh(obj)
    return SponsorshipContractRead.model_validate(
        {**obj.model_dump(), "clauses_count": 0, "requirements_count": 0}
    )


@router.patch(
    "/groups/{group_id}/contracts/{contract_id}",
    response_model=SponsorshipContractRead,
)
def update_contract(
    group_id: int, contract_id: int, body: SponsorshipContractUpdate, db: Session = Depends(_db)
):
    """Atualiza parcialmente um contrato do grupo.

    Requer usuário autenticado (dependência do router).

    Args:
        group_id: Identificador do grupo.
        contract_id: Identificador do contrato.
        body: Campos a alterar.
        db: Sessão de banco.

    Returns:
        ``SponsorshipContractRead`` com contagens atualizadas.

    Raises:
        HTTPException: 404 se o contrato não pertencer ao grupo; 400 se
            ``status`` ou outros campos forem inválidos.
    """
    obj = db.get(SponsorshipContract, contract_id)
    if not obj or obj.group_id != group_id:
        raise HTTPException(status_code=404, detail="Contrato nao encontrado")
    for k, v in body.model_dump(exclude_unset=True).items():
        if k == "status" and isinstance(v, str):
            setattr(obj, k, _parse_enum("status", v, ContractStatus))
        else:
            setattr(obj, k, v)
    obj.updated_at = now_utc()
    db.add(obj)
    db.commit()
    db.refresh(obj)
    cc = _scalar_count(
        db, select(sa_func.count(ContractClause.id)).where(ContractClause.contract_id == obj.id)
    )
    rc = _scalar_count(
        db,
        select(sa_func.count(CounterpartRequirement.id)).where(
            CounterpartRequirement.contract_id == obj.id
        ),
    )
    return SponsorshipContractRead.model_validate(
        {**obj.model_dump(), "clauses_count": cc, "requirements_count": rc}
    )


# ===========================================================================
# Cláusulas do contrato
# ===========================================================================


@router.get("/contracts/{contract_id}/clauses", response_model=list[ContractClauseRead])
def list_clauses(contract_id: int, db: Session = Depends(_db)):
    """Lista cláusulas de um contrato ordenadas por ``display_order``.

    Requer usuário autenticado (dependência do router).

    Args:
        contract_id: Identificador do contrato.
        db: Sessão de banco.

    Returns:
        Lista de ``ContractClauseRead``.
    """
    return db.exec(
        select(ContractClause)
        .where(ContractClause.contract_id == contract_id)
        .order_by(ContractClause.display_order)
    ).all()


@router.post(
    "/contracts/{contract_id}/clauses", response_model=ContractClauseRead, status_code=201
)
def create_clause(contract_id: int, body: ContractClauseCreate, db: Session = Depends(_db)):
    """Cria cláusula vinculada ao contrato.

    Requer usuário autenticado (dependência do router).

    Args:
        contract_id: Contrato de destino.
        body: Texto e metadados da cláusula.
        db: Sessão de banco.

    Returns:
        ``ContractClauseRead`` criada (status 201).
    """
    obj_d = body.model_dump(exclude_unset=True)
    obj_d["contract_id"] = contract_id
    obj = ContractClause(**obj_d)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch(
    "/contracts/{contract_id}/clauses/{clause_id}", response_model=ContractClauseRead
)
def update_clause(
    contract_id: int,
    clause_id: int,
    body: ContractClauseUpdate,
    db: Session = Depends(_db),
):
    """Atualiza cláusula existente do contrato.

    Requer usuário autenticado (dependência do router).

    Args:
        contract_id: Identificador do contrato.
        clause_id: Identificador da cláusula.
        body: Campos a alterar.
        db: Sessão de banco.

    Returns:
        ``ContractClauseRead`` após persistência.

    Raises:
        HTTPException: 404 se a cláusula não pertencer ao contrato.
    """
    obj = db.get(ContractClause, clause_id)
    if not obj or obj.contract_id != contract_id:
        raise HTTPException(status_code=404, detail="Clausula nao encontrada")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/contracts/{contract_id}/clauses/{clause_id}", status_code=204)
def delete_clause(contract_id: int, clause_id: int, db: Session = Depends(_db)):
    """Remove cláusula do contrato.

    Requer usuário autenticado (dependência do router).

    Args:
        contract_id: Identificador do contrato.
        clause_id: Identificador da cláusula.
        db: Sessão de banco.

    Returns:
        Resposta vazia com status HTTP 204 (sem corpo JSON).

    Raises:
        HTTPException: 404 se a cláusula não pertencer ao contrato.
    """
    obj = db.get(ContractClause, clause_id)
    if not obj or obj.contract_id != contract_id:
        raise HTTPException(status_code=404, detail="Clausula nao encontrada")
    db.delete(obj)
    db.commit()


# ===========================================================================
# Contrapartidas (requirements)
# ===========================================================================


@router.get(
    "/contracts/{contract_id}/requirements",
    response_model=list[CounterpartRequirementRead],
)
def list_requirements(contract_id: int, db: Session = Depends(_db)):
    """Lista requisitos de contrapartida do contrato com contagem de ocorrências.

    Requer usuário autenticado (dependência do router).

    Args:
        contract_id: Identificador do contrato.
        db: Sessão de banco.

    Returns:
        Lista de ``CounterpartRequirementRead``.
    """
    items = db.exec(
        select(CounterpartRequirement)
        .where(CounterpartRequirement.contract_id == contract_id)
    ).all()
    reads: list[CounterpartRequirementRead] = []
    for r in items:
        oc = _scalar_count(
            db,
            select(sa_func.count(RequirementOccurrence.id)).where(
                RequirementOccurrence.requirement_id == r.id
            ),
        )
        reads.append(
            CounterpartRequirementRead.model_validate({**r.model_dump(), "occurrences_count": oc})
        )
    return reads


@router.post(
    "/contracts/{contract_id}/requirements",
    response_model=CounterpartRequirementRead,
    status_code=201,
)
def create_requirement(
    contract_id: int, body: CounterpartRequirementCreate, db: Session = Depends(_db)
):
    """Cria requisito de contrapartida vinculado a cláusula do mesmo contrato.

    Requer usuário autenticado (dependência do router).

    Args:
        contract_id: Contrato de destino.
        body: Dados do requisito, incluindo ``clause_id``.
        db: Sessão de banco.

    Returns:
        ``CounterpartRequirementRead`` com ``occurrences_count`` (status 201).

    Raises:
        HTTPException: 404 se a cláusula não pertencer ao contrato; 400 se
            enums forem inválidos.
    """
    clause = db.get(ContractClause, body.clause_id)
    if not clause or clause.contract_id != contract_id:
        raise HTTPException(status_code=404, detail="Clausula nao encontrada")

    obj_d = body.model_dump(exclude_unset=True)
    obj_d["contract_id"] = contract_id
    pt = obj_d.get("period_type")
    if pt is not None and isinstance(pt, str):
        obj_d["period_type"] = _parse_enum("period_type", pt, PeriodType)
    rt = obj_d.get("responsibility_type")
    if isinstance(rt, str):
        obj_d["responsibility_type"] = _parse_enum("responsibility_type", rt, ResponsibilityType)
    st = obj_d.get("status")
    if isinstance(st, str):
        obj_d["status"] = _parse_enum("status", st, RequirementStatus)
    obj = CounterpartRequirement(**obj_d)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    oc = _scalar_count(
        db,
        select(sa_func.count(RequirementOccurrence.id)).where(
            RequirementOccurrence.requirement_id == obj.id
        ),
    )
    return CounterpartRequirementRead.model_validate({**obj.model_dump(), "occurrences_count": oc})


@router.patch(
    "/contracts/{contract_id}/requirements/{req_id}",
    response_model=CounterpartRequirementRead,
)
def update_requirement(
    contract_id: int, req_id: int, body: CounterpartRequirementUpdate, db: Session = Depends(_db)
):
    """Atualiza requisito de contrapartida do contrato.

    Requer usuário autenticado (dependência do router).

    Args:
        contract_id: Identificador do contrato.
        req_id: Identificador do requisito.
        body: Campos a alterar.
        db: Sessão de banco.

    Returns:
        ``CounterpartRequirementRead`` com contagem de ocorrências.

    Raises:
        HTTPException: 404 se o requisito não pertencer ao contrato; 400 se
            enums forem inválidos.
    """
    obj = db.get(CounterpartRequirement, req_id)
    if not obj or obj.contract_id != contract_id:
        raise HTTPException(status_code=404, detail="Requisito nao encontrado")
    for k, v in body.model_dump(exclude_unset=True).items():
        if k == "period_type" and v is not None and isinstance(v, str):
            setattr(obj, k, _parse_enum("period_type", v, PeriodType))
        elif k == "responsibility_type" and isinstance(v, str):
            setattr(obj, k, _parse_enum("responsibility_type", v, ResponsibilityType))
        elif k == "status" and isinstance(v, str):
            setattr(obj, k, _parse_enum("status", v, RequirementStatus))
        else:
            setattr(obj, k, v)
    obj.updated_at = now_utc()
    db.add(obj)
    db.commit()
    db.refresh(obj)
    oc = _scalar_count(
        db,
        select(sa_func.count(RequirementOccurrence.id)).where(
            RequirementOccurrence.requirement_id == obj.id
        ),
    )
    return CounterpartRequirementRead.model_validate({**obj.model_dump(), "occurrences_count": oc})


@router.delete("/contracts/{contract_id}/requirements/{req_id}", status_code=204)
def delete_requirement(contract_id: int, req_id: int, db: Session = Depends(_db)):
    """Remove requisito de contrapartida do contrato.

    Requer usuário autenticado (dependência do router).

    Args:
        contract_id: Identificador do contrato.
        req_id: Identificador do requisito.
        db: Sessão de banco.

    Returns:
        Resposta vazia com status HTTP 204 (sem corpo JSON).

    Raises:
        HTTPException: 404 se o requisito não pertencer ao contrato.
    """
    obj = db.get(CounterpartRequirement, req_id)
    if not obj or obj.contract_id != contract_id:
        raise HTTPException(status_code=404, detail="Requisito nao encontrado")
    db.delete(obj)
    db.commit()


# ===========================================================================
# Ocorrências
# ===========================================================================


@router.get(
    "/requirements/{req_id}/occurrences",
    response_model=list[RequirementOccurrenceRead],
)
def list_occurrences(req_id: int, db: Session = Depends(_db)):
    """Lista ocorrências de um requisito de contrapartida.

    Requer usuário autenticado (dependência do router).

    Args:
        req_id: Identificador do requisito.
        db: Sessão de banco.

    Returns:
        Lista de ``RequirementOccurrenceRead``.
    """
    return db.exec(
        select(RequirementOccurrence).where(RequirementOccurrence.requirement_id == req_id)
    ).all()


@router.post(
    "/requirements/{req_id}/occurrences",
    response_model=RequirementOccurrenceRead,
    status_code=201,
)
def create_occurrence(
    req_id: int, body: RequirementOccurrenceCreate, db: Session = Depends(_db)
):
    """Cria ocorrência vinculada ao requisito.

    Requer usuário autenticado (dependência do router).

    Args:
        req_id: Requisito de destino.
        body: Dados da ocorrência (status, tipo de responsabilidade, etc.).
        db: Sessão de banco.

    Returns:
        ``RequirementOccurrenceRead`` criada (status 201).

    Raises:
        HTTPException: 400 se enums forem inválidos.
    """
    d = body.model_dump(exclude_unset=True)
    d["requirement_id"] = req_id
    if isinstance(d.get("status"), str):
        d["status"] = _parse_enum("status", d["status"], OccurrenceStatus)
    if isinstance(d.get("responsibility_type"), str):
        d["responsibility_type"] = _parse_enum(
            "responsibility_type", d["responsibility_type"], ResponsibilityType
        )
    obj = RequirementOccurrence(**d)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch(
    "/requirements/{req_id}/occurrences/{occ_id}",
    response_model=RequirementOccurrenceRead,
)
def update_occurrence(
    req_id: int,
    occ_id: int,
    body: RequirementOccurrenceUpdate,
    db: Session = Depends(_db),
    current_user: Any = Depends(get_current_user),
):
    """Atualiza ocorrência aplicando regras de status, motivo e responsáveis.

    Exige autenticação explícita via ``get_current_user`` além da dependência
    global do router, para registrar ``validated_by_user_id`` quando o status
    passa a ``validated``.

    Args:
        req_id: Identificador do requisito.
        occ_id: Identificador da ocorrência.
        body: Campos a alterar.
        db: Sessão de banco.
        current_user: Usuário autenticado (validação).

    Returns:
        ``RequirementOccurrenceRead`` após persistência.

    Raises:
        HTTPException: 404 se a ocorrência não pertencer ao requisito; 400
            para motivo de rejeição ausente, enums inválidos ou regras de
            cardinalidade de responsáveis.
    """
    obj = db.get(RequirementOccurrence, occ_id)
    if not obj or obj.requirement_id != req_id:
        raise HTTPException(status_code=404, detail="Ocorrencia nao encontrada")
    payload = body.model_dump(exclude_unset=True)
    next_status = obj.status
    if isinstance(payload.get("status"), str):
        next_status = _parse_enum("status", payload["status"], OccurrenceStatus)

    if next_status == OccurrenceStatus.REJECTED:
        rejection_reason = _normalize_optional_text(payload.get("rejection_reason"))
        if rejection_reason is None:
            raise _integrity_error("rejection_reason e obrigatorio quando status=rejected")
        payload["rejection_reason"] = rejection_reason
    elif "rejection_reason" in payload:
        payload["rejection_reason"] = _normalize_optional_text(payload["rejection_reason"])

    for k, v in payload.items():
        if k == "status" and isinstance(v, str):
            setattr(obj, k, _parse_enum("status", v, OccurrenceStatus))
        elif k == "responsibility_type" and isinstance(v, str):
            setattr(obj, k, _parse_enum("responsibility_type", v, ResponsibilityType))
        else:
            setattr(obj, k, v)

    _assert_occurrence_responsibility_integrity(
        responsibility_type=obj.responsibility_type,
        responsible_count=_count_occurrence_responsibles(db, occ_id),
        status=next_status,
    )

    if next_status == OccurrenceStatus.VALIDATED:
        obj.validated_by_user_id = current_user.id
        obj.validated_at = now_utc()
    elif obj.status != OccurrenceStatus.VALIDATED:
        obj.validated_by_user_id = None
        obj.validated_at = None

    obj.updated_at = now_utc()
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/requirements/{req_id}/occurrences/{occ_id}", status_code=204)
def delete_occurrence(req_id: int, occ_id: int, db: Session = Depends(_db)):
    """Remove ocorrência do requisito.

    Requer usuário autenticado (dependência do router).

    Args:
        req_id: Identificador do requisito.
        occ_id: Identificador da ocorrência.
        db: Sessão de banco.

    Returns:
        Resposta vazia com status HTTP 204 (sem corpo JSON).

    Raises:
        HTTPException: 404 se a ocorrência não pertencer ao requisito.
    """
    obj = db.get(RequirementOccurrence, occ_id)
    if not obj or obj.requirement_id != req_id:
        raise HTTPException(status_code=404, detail="Ocorrencia nao encontrada")
    db.delete(obj)
    db.commit()


# ===========================================================================
# Responsáveis por ocorrência
# ===========================================================================


@router.get(
    "/occurrences/{occ_id}/responsibles",
    response_model=list[OccurrenceResponsibleRead],
)
def list_responsibles(occ_id: int, db: Session = Depends(_db)):
    """Lista responsáveis (membros do grupo) associados à ocorrência.

    Requer usuário autenticado (dependência do router).

    Args:
        occ_id: Identificador da ocorrência.
        db: Sessão de banco.

    Returns:
        Lista de ``OccurrenceResponsibleRead``.
    """
    return db.exec(
        select(OccurrenceResponsible).where(OccurrenceResponsible.occurrence_id == occ_id)
    ).all()


@router.post(
    "/occurrences/{occ_id}/responsibles",
    response_model=OccurrenceResponsibleRead,
    status_code=201,
)
def create_responsible(
    occ_id: int, body: OccurrenceResponsibleBase, db: Session = Depends(_db)
):
    """Associa membro do grupo como responsável pela ocorrência.

    Requer usuário autenticado (dependência do router).

    Args:
        occ_id: Ocorrência de destino.
        body: Identificador do membro do grupo.
        db: Sessão de banco.

    Returns:
        ``OccurrenceResponsibleRead`` criado (status 201).

    Raises:
        HTTPException: 404 se ocorrência ou membro inválidos; 400 se o membro
            não pertencer ao grupo do contrato ou se violar limite para tipo
            individual.
    """
    occ = db.get(RequirementOccurrence, occ_id)
    if not occ:
        raise HTTPException(status_code=404, detail="Ocorrencia nao encontrada")
    req = db.get(CounterpartRequirement, occ.requirement_id)
    contract = db.get(SponsorshipContract, req.contract_id)  # type: ignore[union-attr]
    member = db.get(GroupMember, body.member_id)
    if not member or member.group_id != contract.group_id:  # type: ignore[union-attr]
        raise HTTPException(
            status_code=400,
            detail="Membro nao pertence ao grupo do contrato da ocorrencia.",
        )
    current_count = _count_occurrence_responsibles(db, occ_id)
    if occ.responsibility_type == ResponsibilityType.INDIVIDUAL and current_count >= 1:
        raise _integrity_error(
            "responsibility_type=individual exige exatamente 1 responsavel; "
            "nao e permitido adicionar um segundo responsavel."
        )

    obj_d = body.model_dump(exclude_unset=True)
    obj_d["occurrence_id"] = occ_id
    obj = OccurrenceResponsible(**obj_d)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/occurrences/{occ_id}/responsibles/{resp_id}", status_code=204)
def delete_responsible(occ_id: int, resp_id: int, db: Session = Depends(_db)):
    """Remove responsável da ocorrência respeitando cardinalidade mínima.

    Requer usuário autenticado (dependência do router).

    Args:
        occ_id: Identificador da ocorrência.
        resp_id: Identificador do responsável.
        db: Sessão de banco.

    Returns:
        Resposta vazia com status HTTP 204 (sem corpo JSON).

    Raises:
        HTTPException: 404 se IDs não conferirem; 400 se a remoção violar
            regras de integridade operacional.
    """
    obj = db.get(OccurrenceResponsible, resp_id)
    if not obj or obj.occurrence_id != occ_id:
        raise HTTPException(status_code=404, detail="Responsavel nao encontrado")
    occ = db.get(RequirementOccurrence, occ_id)
    if not occ:
        raise HTTPException(status_code=404, detail="Ocorrencia nao encontrada")
    remaining_count = _count_occurrence_responsibles(db, occ_id) - 1
    _assert_occurrence_responsibility_integrity(
        responsibility_type=occ.responsibility_type,
        responsible_count=remaining_count,
        status=occ.status,
    )
    db.delete(obj)
    db.commit()


# ===========================================================================
# Entregas
# ===========================================================================


@router.get("/occurrences/{occ_id}/deliveries", response_model=list[DeliveryRead])
def list_deliveries(occ_id: int, db: Session = Depends(_db)):
    """Lista entregas registradas para a ocorrência.

    Requer usuário autenticado (dependência do router).

    Args:
        occ_id: Identificador da ocorrência.
        db: Sessão de banco.

    Returns:
        Lista de ``DeliveryRead``.
    """
    return db.exec(
        select(Delivery).where(Delivery.occurrence_id == occ_id)
    ).all()


@router.post(
    "/occurrences/{occ_id}/deliveries", response_model=DeliveryRead, status_code=201
)
def create_delivery(occ_id: int, body: DeliveryCreate, db: Session = Depends(_db)):
    """Cria entrega vinculada à ocorrência.

    Requer usuário autenticado (dependência do router).

    Args:
        occ_id: Ocorrência de destino.
        body: Dados da entrega.
        db: Sessão de banco.

    Returns:
        ``DeliveryRead`` criada (status 201).
    """
    obj = Delivery(**body.model_dump(exclude_unset=True))
    obj.occurrence_id = occ_id
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch(
    "/occurrences/{occ_id}/deliveries/{d_id}", response_model=DeliveryRead
)
def update_delivery(
    occ_id: int, d_id: int, body: DeliveryUpdate, db: Session = Depends(_db)
):
    """Atualiza entrega da ocorrência.

    Requer usuário autenticado (dependência do router).

    Args:
        occ_id: Identificador da ocorrência.
        d_id: Identificador da entrega.
        body: Campos a alterar.
        db: Sessão de banco.

    Returns:
        ``DeliveryRead`` após persistência.

    Raises:
        HTTPException: 404 se a entrega não pertencer à ocorrência.
    """
    obj = db.get(Delivery, d_id)
    if not obj or obj.occurrence_id != occ_id:
        raise HTTPException(status_code=404, detail="Entrega nao encontrada")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    obj.updated_at = now_utc()
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/occurrences/{occ_id}/deliveries/{d_id}", status_code=204)
def delete_delivery(occ_id: int, d_id: int, db: Session = Depends(_db)):
    """Remove entrega da ocorrência.

    Requer usuário autenticado (dependência do router).

    Args:
        occ_id: Identificador da ocorrência.
        d_id: Identificador da entrega.
        db: Sessão de banco.

    Returns:
        Resposta vazia com status HTTP 204 (sem corpo JSON).

    Raises:
        HTTPException: 404 se a entrega não pertencer à ocorrência.
    """
    obj = db.get(Delivery, d_id)
    if not obj or obj.occurrence_id != occ_id:
        raise HTTPException(status_code=404, detail="Entrega nao encontrada")
    db.delete(obj)
    db.commit()


# ===========================================================================
# Evidências
# ===========================================================================


@router.get("/deliveries/{d_id}/evidences", response_model=list[DeliveryEvidenceRead])
def list_evidences(d_id: int, db: Session = Depends(_db)):
    """Lista evidências anexadas a uma entrega.

    Requer usuário autenticado (dependência do router).

    Args:
        d_id: Identificador da entrega.
        db: Sessão de banco.

    Returns:
        Lista de ``DeliveryEvidenceRead``.
    """
    return db.exec(
        select(DeliveryEvidence).where(DeliveryEvidence.delivery_id == d_id)
    ).all()


@router.post(
    "/deliveries/{d_id}/evidences", response_model=DeliveryEvidenceRead, status_code=201
)
def create_evidence(d_id: int, body: DeliveryEvidenceCreate, db: Session = Depends(_db)):
    """Cria evidência vinculada à entrega.

    Requer usuário autenticado (dependência do router).

    Args:
        d_id: Entrega de destino.
        body: Tipo e conteúdo da evidência.
        db: Sessão de banco.

    Returns:
        ``DeliveryEvidenceRead`` criada (status 201).

    Raises:
        HTTPException: 400 se ``evidence_type`` for inválido.
    """
    d = body.model_dump(exclude_unset=True)
    d["delivery_id"] = d_id
    d["evidence_type"] = _parse_enum("evidence_type", str(d["evidence_type"]), EvidenceType)
    obj = DeliveryEvidence(**d)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
