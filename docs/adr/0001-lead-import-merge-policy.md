# ADR-0001: Política única de merge na importação de leads

## Status

Accepted

## Context

O repositório tem três caminhos que materializam leads na tabela `lead`: import legado (`POST /leads/import`), commit ETL (`POST /leads/import/etl/commit`) e inserção após o pipeline Gold (`_inserir_leads_gold`). Quando o lead já existe (dedupe), o comportamento de fusão do payload divergia: o Gold só preenchia campos vazios; o ETL/legado sobrescrevia a maior parte dos campos com valores não nulos do ficheiro. Isto gerava semântica inconsistente de “última importação” entre fluxos e dificultava suporte e documentação.

## Decision

Adoptar uma **política única de merge não destrutivo** (“fill missing only”) para todos os fluxos:

1. Para cada par `(campo, valor)` presente no payload de importação, o sistema só escreve no `Lead` existente se:
   - o valor importado é considerado **presente** (não é `None` e, se for `str`, não é só espaços); e
   - o valor atual no registo **não** é considerado presente pela mesma regra.
2. Não há excepções por nome de campo além desta regra: email, CPF, `fonte_origem`, `nome`, `evento_nome`, endereço, etc. tratam-se todos da mesma forma.
3. A lógica vive num único módulo (`merge_lead_payload_fill_missing`) usado pelo Gold (`_merge_lead_payload_if_missing`) e por `merge_lead` na persistência partilhada ETL/legado.

## Matriz de comportamento (resumo)

| Valor actual no `Lead` | Valor no payload import | Resultado |
|------------------------|-------------------------|-----------|
| vazio / nulo / string só espaços | ausente ou nulo ou string vazia | sem alteração |
| vazio | presente | grava o valor do import |
| presente | presente (igual ou diferente) | **mantém** o valor actual |
| presente | ausente / nulo / string vazia | sem alteração (não apaga) |

“Presente” equivale à função `lead_field_has_value` partilhada no código.

## Consequences

### Positive

- Comportamento homogéneo entre Gold, ETL e legado; uma única narrativa para produto e QA.
- Menos surpresas ao reprocessar o mesmo CPF por canais diferentes.

### Negative

- Reimportar um ficheiro **não** corrige automaticamente `nome`, `evento_nome`, morada, etc. se o registo já tiver valor — é necessário editar o lead na UI ou outro processo explícito.

### Neutral

- O contador `updated` nos resumos de import pode continuar a incrementar quando uma linha corresponde a um lead existente, mesmo que nenhum campo tenha mudado após o merge.

## Alternatives Considered

**Última importação vence para campos opcionais (alinhar Gold ao ETL antigo)**  
Rejeitado: sobrescrever dados já preenchidos no Gold aumentaria risco de apagar correcções manuais sem aviso explícito.

**Política distinta por fluxo com feature flag**  
Rejeitado para esta iteração: aumenta complexidade operacional; a task pedia política única ou divergência justificada com flags — optou-se por política única sem flags.

## References

- `auditoria/deep-research-report.md` — achado “O Gold reimporta sem atualizar dados já preenchidos”
- `auditoria/task8.md`
- `docs/leads_importacao.md` — secção Upsert
- `backend/app/modules/leads_publicidade/application/lead_merge_policy.py`
