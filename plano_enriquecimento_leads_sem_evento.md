# Plano técnico: enriquecimento de leads existentes sem exigir evento no arquivo

## 1. Resumo

Objetivo: permitir o processamento de arquivos de leads cujo propósito não é cadastrar novos registros nem criar novos vínculos de evento, mas sim complementar ou atualizar leads já existentes no banco.

Princípio operacional:

- o evento já existe no banco como contexto do lead;
- o arquivo não precisa repetir esse contexto;
- o sistema deve localizar o lead existente por chave estável;
- o sistema deve atualizar apenas registros com match confiável;
- o sistema não deve criar `Lead` nem `LeadEvento` nesse modo.

Recomendação principal: criar um modo explícito de **enriquecimento de leads existentes** dentro do pipeline atual `bronze -> silver -> gold`, com o menor desvio possível do fluxo já existente.

---

## 2. Diagnóstico do problema

Hoje o pipeline assume que todo lote de leads representa importação/cadastro orientado a evento. Isso aparece principalmente no Gold:

- o lote costuma estar ancorado em `batch.evento_id`;
- o matching favorece contexto canônico do evento;
- o fluxo admite criação de novos `Lead`;
- o fluxo chama criação/garantia de `LeadEvento`.

Esse desenho faz sentido para cadastro/importação inicial, mas não para enriquecimento.

No cenário de enriquecimento:

- o lead já existe;
- o lead já está vinculado a evento(s);
- o arquivo pode vir sem coluna de evento;
- exigir `evento_id` força o operador a reconstruir um dado que o sistema já possui.

Isso gera dependência artificial, aumenta risco operacional e dificulta um caso legítimo de uso.

---

## 3. Diretriz de solução

Não tratar esse caso como “importação de novos leads”.

Tratar como um fluxo separado semanticamente:

- **fluxo A: importação/cadastro**
  - exige `evento_id`;
  - pode criar `Lead`;
  - pode criar `LeadEvento`;
  - usa evento como âncora de dedupe e vínculo.

- **fluxo B: enriquecimento de leads existentes**
  - não exige `evento_id`;
  - não cria `Lead`;
  - não cria `LeadEvento`;
  - apenas localiza `Lead` existente e aplica merge controlado.

---

## 4. Solução recomendada com menor impacto

### 4.1 Estratégia

Adicionar um novo modo operacional no pipeline atual, por exemplo:

- `origem_lote="enriquecimento"`, ou
- `enrichment_only=true`

Recomendação: preferir uma flag explícita de comportamento, mesmo que internamente também se reflita em `origem_lote`.

### 4.2 Comportamento do novo modo

Quando o lote estiver em modo de enriquecimento:

- `evento_id` deixa de ser obrigatório na criação do batch;
- Bronze permanece inalterado;
- Silver permanece praticamente inalterado;
- Gold entra em branch específico de enriquecimento:
  - lê o CSV consolidado;
  - gera payload normalizado por linha;
  - tenta localizar um `Lead` já existente;
  - se houver match único, aplica merge;
  - se não houver match, rejeita a linha;
  - se houver ambiguidade, rejeita a linha;
  - nunca cria `Lead`;
  - nunca chama `ensure_lead_event`;
  - nunca insere `LeadEvento`.

### 4.3 Política de merge

Adotar como padrão:

- `fill_missing`

Ou seja:

- campos já preenchidos no banco não são sobrescritos;
- campos vazios/nulos no banco podem ser preenchidos pelo arquivo;
- valores vazios do arquivo nunca limpam dados existentes.

Isso reduz drasticamente risco de regressão e sobrescrita indevida.

---

## 5. Regras de matching recomendadas

O modo enriquecimento deve ser conservador.

### 5.1 Ordem de chaves

Prioridade sugerida:

1. `id_salesforce`, quando existir e estiver preenchido.
2. `cpf`, quando existir e houver unicidade prática.
3. `cpf + email`, quando ambos existirem.
4. `email`, apenas quando produzir match único.
5. `telefone`, apenas como critério auxiliar, nunca como chave isolada principal.

### 5.2 Regras operacionais

- Só atualizar quando houver **exatamente um** `Lead` candidato.
- Se houver **zero** candidatos: rejeitar a linha com motivo `lead_not_found`.
- Se houver **mais de um** candidato: rejeitar a linha com motivo `ambiguous_match`.
- `nome` não pode ser chave primária de matching.
- `evento_nome` do arquivo, se existir, não deve ser obrigatório nem determinante nesse modo.

### 5.3 Normalização antes do match

Normalizar antes de consultar:

- CPF: remover máscara, espaços e lixo textual;
- email: trim + lowercase;
- telefone: padronizar dígitos;
- strings vazias: tratar como nulo.

---

## 6. Validações necessárias

### 6.1 Validações por linha

- cada linha precisa ter pelo menos uma chave confiável de lookup;
- linhas sem chave suficiente devem ser rejeitadas;
- linhas com match ambíguo devem ser rejeitadas;
- linhas que apontam para mais de um lead não podem ser atualizadas parcialmente.

### 6.2 Validações de lote

- o lote deve informar explicitamente que está em modo enriquecimento;
- o sistema deve bloquear insert de `Lead` nesse modo;
- o sistema deve bloquear criação de `LeadEvento` nesse modo;
- opcional: falhar o lote inteiro se a taxa de match ficar abaixo de um limiar mínimo.

### 6.3 Validação de segurança

Adicionar uma proteção para impedir comportamento híbrido:

- se `enrichment_only=true`, qualquer tentativa de criação de novo lead deve virar erro/rejeição, nunca fallback silencioso para insert.

---

## 7. Impacto esperado no código

## 7.1 Backend HTTP / criação do batch

Ajustar o contrato do batch para permitir:

- criação de lote sem `evento_id` quando `enrichment_only=true`.

Impacto provável:

- validação do endpoint de upload do batch;
- schema de request;
- possível persistência de uma flag no `LeadBatch`.

## 7.2 Modelo `LeadBatch`

Adicionar um campo simples de modo operacional, por exemplo:

- `processing_mode: str | None`

Valores sugeridos:

- `import`
- `enrichment`

Alternativamente:

- `enrichment_only: bool`

Recomendação de menor interferência:

- `enrichment_only: bool = False`

Isso evita refatoração ampla de enums existentes.

## 7.3 `lead_pipeline_service.py`

Este será o ponto principal da mudança.

Mudanças previstas:

- detectar `enrichment_only` no batch;
- permitir execução do Gold sem `batch.evento_id` nesse branch;
- criar helper dedicado de matching estrito sem âncora de evento;
- criar helper de atualização sem insert;
- pular criação de `LeadEvento`;
- produzir métricas separadas:
  - `matched_rows`
  - `updated_rows`
  - `not_found_rows`
  - `ambiguous_rows`

## 7.4 Relatório de pipeline

Incluir no `pipeline_report`:

- quantidade de linhas com match único;
- quantidade de linhas sem match;
- quantidade de linhas ambíguas;
- amostras de rejeição com a chave usada no lookup;
- política de merge aplicada.

## 7.5 Testes

Adicionar testes focados cobrindo:

- batch enriquecimento sem `evento_id` é aceito;
- linha com `cpf` único atualiza lead existente;
- linha com `email` único atualiza lead existente;
- linha sem match não cria lead;
- linha com match ambíguo não atualiza nada;
- enriquecimento não cria `LeadEvento`;
- enriquecimento não cria `Lead`;
- merge `fill_missing` preserva campos já preenchidos.

---

## 8. Desenho de implementação recomendado

### Etapa 1: habilitar modo de lote

- adicionar flag `enrichment_only` em `LeadBatch`;
- aceitar upload sem `evento_id` quando a flag estiver ativa;
- manter validação atual intacta para fluxo normal.

### Etapa 2: branch específico no Gold

Dentro de `_inserir_leads_gold(...)`:

- se `batch.enrichment_only`:
  - usar `_inserir_leads_gold_enrichment_only(...)`
- senão:
  - manter fluxo atual.

### Etapa 3: helper dedicado

Criar helper novo, por exemplo:

- `_match_existing_lead_for_enrichment(...)`

Responsabilidade:

- resolver match estrito;
- devolver:
  - lead único encontrado;
  - ou status `not_found`;
  - ou status `ambiguous`.

### Etapa 4: update-only

Criar helper novo, por exemplo:

- `_apply_enrichment_to_existing_lead(...)`

Responsabilidade:

- aplicar `merge_lead_payload_fill_missing(...)`;
- nunca inserir novo lead;
- nunca criar vínculo de evento.

### Etapa 5: observabilidade e relatório

- registrar em log quando lote entra em modo enriquecimento;
- logar contagens finais de match/rejeição;
- refletir isso no `pipeline_report`.

---

## 9. Alternativa secundária

Alternativa possível:

- tornar `evento_id` opcional no fluxo atual e inferir o modo de operação automaticamente.

Exemplo:

- se `evento_id` veio: fluxo de importação;
- se `evento_id` não veio: fluxo enriquecimento.

Essa alternativa reduz atrito de UX, mas piora a clareza do sistema.

Problemas dessa abordagem:

- mistura duas semânticas no mesmo fluxo;
- aumenta branches implícitos;
- dificulta validação e observabilidade;
- pode confundir operadores e testes.

Por isso, não é a recomendação principal.

---

## 10. Riscos e mitigação

### Risco 1: match ambíguo

Exemplo:

- mesmo email em múltiplos leads;
- CPF inconsistente ou duplicado em legado.

Mitigação:

- só aceitar match único;
- rejeitar casos ambíguos com relatório claro.

### Risco 2: atualização do lead errado

Mitigação:

- usar chaves fortes;
- evitar telefone/nome como chave principal;
- logar qual chave gerou o match.

### Risco 3: sobrescrita indevida

Mitigação:

- política `fill_missing` por padrão;
- não sobrescrever campos já preenchidos;
- se um dia houver overwrite explícito, tratar como modo separado.

### Risco 4: uso indevido do fluxo para importar leads novos

Mitigação:

- `enrichment_only` bloqueia criação de `Lead`;
- linhas sem match são rejeitadas, nunca inseridas.

### Risco 5: perda de rastreabilidade

Mitigação:

- staging/report por linha;
- motivos de rejeição explícitos;
- contadores de lote persistidos.

---

## 11. Recomendação final

A opção de menor interferência no código é:

1. adicionar um modo explícito de **enriquecimento de leads existentes** no pipeline atual;
2. permitir batch sem `evento_id` apenas nesse modo;
3. no Gold, fazer **match estrito e update-only**;
4. bloquear criação de `Lead` e `LeadEvento`;
5. manter `fill_missing` como política padrão;
6. rejeitar linhas sem match único e confiável.

Essa abordagem:

- resolve o problema real;
- reaproveita a arquitetura atual;
- evita refatoração ampla;
- separa corretamente cadastro novo de enriquecimento;
- reduz risco operacional.

---

## 12. Ordem recomendada de implementação

1. adicionar `enrichment_only` ao `LeadBatch` e ao contrato de upload;
2. ajustar validação para não exigir `evento_id` nesse modo;
3. criar branch de enriquecimento no Gold;
4. implementar matching estrito e update-only;
5. adicionar contadores/relatório;
6. cobrir com testes de unidade e integração.
