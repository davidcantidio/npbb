# Plano: `PrevisaoIngresso` (Task 1 — item isolado)

Plano de implementação **somente** do item do `plan.md` da Task 1:

> Create `PrevisaoIngresso` model — planned quantity per evento + diretoria + tipo_ingresso

Referência canónica: [plan.md](plan.md) (secção Task 1 — modelo, constraint única e ficheiro `ingressos_v2_models.py`).

---

## 1. Objetivo

Persistir a **quantidade planejada** de ingressos por combinação **evento + diretoria + tipo de ingresso**, com **uma única linha** por combinação (upsert lógico na camada de API virá na Task 2).

---

## 2. Estado atual no repositório (abril 2026)

| Artefacto | Estado |
|-----------|--------|
| Enum `TipoIngresso` em `backend/app/models/models.py` | Já existe (`pista`, `pista_premium`, `camarote`). |
| Classe `PrevisaoIngresso` em `backend/app/models/ingressos_v2_models.py` | Já declarada: FKs `evento_id`, `diretoria_id`, coluna `tipo_ingresso` (mesmo enum Postgres `tipoingresso` que outros modelos v2), `quantidade`, `created_at`, `updated_at`, `UniqueConstraint(evento_id, diretoria_id, tipo_ingresso)`. |
| Export em `backend/app/models/models.py` | `PrevisaoIngresso` já importada de `ingressos_v2_models`. |
| Migração Alembic para `previsao_ingresso` | **Não encontrada** em `backend/alembic/versions/` (grep por `previsao_ingresso` só aponta o modelo). |

Conclusão: o trabalho que falta para “fechar” este item em bases reais é sobretudo **DDL (Alembic)** e **verificação**; o modelo Python já espelha o desenho do `plan.md`.

---

## 3. Escopo incluído

- Garantir que o **modelo** está alinhado com o PRD/`plan.md` (campos, constraint, índices implícitos em FKs).
- Adicionar **migração Alembic** que cria o tipo enum PostgreSQL necessário à coluna `tipo_ingresso` **se ainda não existir** no histórico de migrações (este item é o primeiro uso de `tipoingresso` no DDL do repo, salvo migração futura conjunta).
- **Não** alterar `cota_cortesia` nem `solicitacao_ingresso`.
- **Não** implementar rotas, schemas Pydantic, serviços ou UI (isso é Task 2+).

---

## 4. Escopo excluído (explícito)

- `ConfiguracaoIngressoEvento` / validação “só tipos activos no evento” — Task 2.
- Cálculo de inventário / reconciliação — Task 3.
- Testes de API — quando existir endpoint; para este item, bastam testes de migração ou smoke `CREATE TABLE` se a equipa adoptar essa prática.

---

## 5. Decisões de desenho (manter)

- **Granularidade:** uma linha = `(evento_id, diretoria_id, tipo_ingresso)` com `quantidade >= 0` (recomenda-se validação a nível de schema/serviço; o `plan.md` não exige `CheckConstraint` em DB — opcional).
- **Unicidade:** `UniqueConstraint("evento_id", "diretoria_id", "tipo_ingresso")` como no `plan.md`.
- **Timestamps:** `created_at` / `updated_at` com `now_utc` e `onupdate` na coluna `updated_at`, consistente com o resto de `ingressos_v2_models.py`.
- **Enum no Postgres:** nome de tipo **`tipoingresso`** e valores iguais a `TipoIngresso.*.value`, alinhado ao `SQLEnum` existente no modelo (`values_callable`).

---

## 6. Passos de implementação

### 6.1 Revisão do modelo (rápida)

1. Abrir `backend/app/models/ingressos_v2_models.py` e confirmar que `PrevisaoIngresso` coincide com o `plan.md` (já coincide a 9-abr-2026).
2. **Opcional (consistência com `CotaCortesia`):** adicionar `Relationship` para `Evento` e `Diretoria` com `back_populates` — implica alterar `Evento` e `Diretoria` em `models.py` para novas listas. Só fazer se a equipa quiser navegação ORM; **não é necessário** para cumprir o item da Task 1.

### 6.2 Migração Alembic

1. Executar `alembic heads` (a partir de `backend/`) e anotar o revision ID actual (pode haver múltiplos heads; fazer `merge` se for política do repo antes de nova revisão).
2. Gerar revisão **manual** ou **autogenerate**:
   - **Preferência:** revisão manual explícita para `CREATE TYPE ... AS ENUM` + `CREATE TABLE previsao_ingresso` + FKs + unique constraint + índices, para evitar surpresas com enums em Postgres.
3. Na `upgrade()`:
   - Criar enum `tipoingresso` com os três valores, **só se não existir** (padrão seguro para reexecução em ambientes parcialmente migrados).
   - Criar tabela `previsao_ingresso` com colunas alinhadas ao SQLModel (tipos: `INTEGER` para IDs e `quantidade`, `TIMESTAMP WITH TIME ZONE` para datas, enum para `tipo_ingresso`).
   - Adicionar `FOREIGN KEY` para `evento.id` e `diretoria.id`.
   - Adicionar `UNIQUE (evento_id, diretoria_id, tipo_ingresso)`.
4. Na `downgrade()`:
   - `DROP TABLE previsao_ingresso`.
   - `DROP TYPE tipoingresso` **apenas** se nenhuma outra tabela do mesmo deploy depender desse tipo; se a migração incremental só criar `previsao_ingresso`, pode fazer drop do enum; se enums forem partilhados com outras tabelas na mesma revisão maior, o downgrade deve ser ordenado (tabelas primeiro, tipo por último).

### 6.3 Registo de metadados / Alembic

- Garantir que `env.py` inclui o modelo `PrevisaoIngresso` no target metadata (já costuma incluir `app.models` completo — confirmar se autogenerate for usado).

### 6.4 Verificação

1. `alembic upgrade head` contra uma base de desenvolvimento com dados existentes em `evento` / `diretoria`.
2. `alembic downgrade -1` e novamente `upgrade` (ciclo limpo).
3. Inserção manual ou via shell SQL: uma linha de teste com `evento_id` e `diretoria_id` válidos; segunda inserção com o mesmo trio deve falhar na unique constraint.
4. Smoke dos endpoints legados mencionados no `plan.md` (`GET /ativos`, etc.) — não devem ser afectados (sem alteração de tabelas antigas).

---

## 7. Riscos e mitigação

| Risco | Mitigação |
|-------|-----------|
| Enum Postgres com nome/colisão já criado à mão noutro ambiente | Usar `DO $$ ... IF NOT EXISTS` ou verificar `pg_type` antes de `CREATE TYPE`. |
| Múltiplos heads Alembic | Resolver merges antes de aplicar a nova revisão em CI. |
| Modelo sem migração leva a erros em runtime ao aceder à tabela | Tratar esta migração como critério de aceitação deste item. |

---

## 8. Critérios de aceitação (definição de pronto)

- [ ] Tabela `previsao_ingresso` criada em Postgres com FKs e unique `(evento_id, diretoria_id, tipo_ingresso)`.
- [ ] Tipo enum `tipoingresso` disponível e consistente com `TipoIngresso` em Python.
- [ ] Migração `upgrade` / `downgrade` validada localmente.
- [ ] Nenhuma alteração destructiva em `cota_cortesia` / `solicitacao_ingresso`.
- [ ] Classe `PrevisaoIngresso` permanece a fonte de verdade em `backend/app/models/ingressos_v2_models.py` e está exportada onde o projeto já exporta os modelos v2.

---

## 9. Referências de código existente

Modelo actual:

```72:92:backend/app/models/ingressos_v2_models.py
class PrevisaoIngresso(SQLModel, table=True):
    __tablename__ = "previsao_ingresso"
    __table_args__ = (UniqueConstraint("evento_id", "diretoria_id", "tipo_ingresso"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id", index=True)
    diretoria_id: int = Field(foreign_key="diretoria.id", index=True)
    tipo_ingresso: TipoIngresso = Field(
        sa_column=Column(
            SQLEnum(
                TipoIngresso,
                name="tipoingresso",
                values_callable=_enum_values,
            ),
            nullable=False,
            index=True,
        )
    )
    quantidade: int
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(sa_column=_updated_at_column())
```

Padrão semelhante (evento + diretoria + quantidade) no legado:

```19:30:backend/app/models/event_support_models.py
class CotaCortesia(SQLModel, table=True):
    __tablename__ = "cota_cortesia"
    __table_args__ = (UniqueConstraint("evento_id", "diretoria_id"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id")
    diretoria_id: int = Field(foreign_key="diretoria.id", index=True)
    quantidade: int

    evento: Optional["Evento"] = Relationship(back_populates="cotas")
    diretoria: Optional["Diretoria"] = Relationship(back_populates="cotas")
```
