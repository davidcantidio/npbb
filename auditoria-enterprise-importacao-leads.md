# AUDITORIA ENTERPRISE — FLUXO DE IMPORTAÇÃO DE LEADS

**Sistema auditado:** fluxo de importação de leads em `/leads/importar`  
**Nível do documento:** Enterprise  
**Tipo:** Auditoria crítica funcional, técnica, operacional, UX, segurança e governança  
**Data:** 2026-04-20  
**Status:** Final  
**Escopo avaliado:** frontend, backend, pipeline de processamento, mapeamento, observabilidade, segurança e governança operacional

---

## 1. Resumo executivo

Esta auditoria avaliou criticamente o fluxo de importação de leads implementado em `/leads/importar`, considerando não apenas a interface visível ao usuário, mas também a arquitetura, os contratos entre frontend e backend, os mecanismos de processamento, a resiliência operacional e a governança do processo.

A conclusão é que o fluxo atual possui **bom nível de sofisticação técnica**, com mecanismos relevantes de preview, mapeamento, pipeline, retomada, polling, hints de metadados, batch e ETL. Porém, essa sofisticação foi concentrada em uma experiência única e excessivamente carregada, criando um sistema que, embora poderoso, apresenta riscos relevantes de:

- confusão operacional;
- erro humano em massa;
- inconsistência entre fluxos;
- fragilidade de UX;
- rastreabilidade assimétrica;
- dependência excessiva de estado local;
- sinais de gargalo e processamento longo;
- possíveis brechas de autorização por identificação de lote, a depender da proteção efetiva do backend e/ou RLS.

Em termos enterprise, o principal diagnóstico é:

> O fluxo atual está funcionalmente avançado, porém ainda não está suficientemente consolidado como produto operacional governável, previsível, seguro e ergonomicamente sustentável para crescer com escala e volume.

---

## 2. Objetivo da auditoria

O objetivo desta auditoria é:

1. mapear o fluxo atual ponta a ponta;
2. identificar fragilidades concretas e potenciais;
3. avaliar impacto no negócio, na operação e na experiência do usuário;
4. propor melhorias práticas, específicas e acionáveis;
5. priorizar a implementação dos achados;
6. estabelecer diretrizes de governança para execução segura das correções.

---

## 3. Escopo avaliado

A auditoria considerou os seguintes eixos:

### 3.1 Experiência do usuário
- clareza da interface;
- legibilidade do fluxo;
- esforço manual;
- ambiguidade;
- feedback de progresso, sucesso, warning e erro;
- risco de interpretação errada.

### 3.2 Fluxo funcional
- etapas do processo;
- sequência de estados;
- requisitos mínimos;
- regras de avanço;
- batch versus single;
- ETL versus Bronze/Silver/Gold.

### 3.3 Qualidade e integridade dos dados
- riscos de mapeamento insuficiente;
- deduplicação;
- metadados reaproveitados;
- acoplamento com evento, ativação e agência;
- consistência do preview;
- risco de contaminação de cadastros mestres.

### 3.4 Performance e escalabilidade
- sinais de timeout;
- polling;
- retomada;
- chunking;
- custo de leitura e persistência;
- indícios de operação próxima do limite.

### 3.5 Robustez técnica
- resiliência a falhas;
- retomada;
- idempotência parcial;
- persistência de contexto;
- estados transitórios;
- manutenção futura.

### 3.6 Segurança e governança
- autorização;
- rastreabilidade;
- auditabilidade;
- segregação por usuário;
- trilha de decisão;
- controle de mudanças.

---

## 4. Base técnica considerada

A auditoria foi fundamentada na leitura da implementação do fluxo, incluindo os principais módulos do frontend e backend relacionados à importação.

### Frontend
- `frontend/src/pages/leads/ImportacaoPage.tsx`
- `frontend/src/pages/leads/importacao/ImportacaoUploadStep.tsx`
- `frontend/src/pages/leads/MapeamentoPage.tsx`
- `frontend/src/pages/leads/BatchMapeamentoPage.tsx`
- `frontend/src/pages/leads/PipelineStatusPage.tsx`
- `frontend/src/pages/leads/importacao/batch/useBatchUploadDraft.ts`
- `frontend/src/services/leads_import.ts`

### Backend
- `backend/app/routers/leads.py`
- `backend/app/services/lead_batch_intake_service.py`
- `backend/app/services/lead_pipeline_service.py`
- `backend/app/services/lead_mapping.py`

---

## 5. Visão geral do fluxo atual

O endpoint `/leads/importar` não representa um único fluxo simples. Ele funciona como um **shell operacional multifluxo**, concentrando:

- upload simples Bronze;
- upload batch Bronze;
- preview;
- mapeamento individual;
- mapeamento unificado batch;
- pipeline Gold;
- fluxo ETL alternativo;
- quick create de evento;
- criação ad hoc de ativação;
- ajustes operacionais relacionados a agência/evento.

### 5.1 Principais caminhos existentes

#### A. Bronze → Silver → Gold
1. seleção de arquivo;
2. preenchimento de metadados;
3. envio para Bronze;
4. preview;
5. mapeamento;
6. promoção para Silver;
7. disparo de pipeline Gold;
8. acompanhamento de status e relatório.

#### B. Batch Bronze
1. seleção de múltiplos arquivos;
2. metadados por linha;
3. intake por arquivo;
4. mapeamento batch ou individual;
5. acompanhamento por lote;
6. avanço progressivo entre lotes.

#### C. ETL
1. escolha de arquivo e evento;
2. geração de preview ETL;
3. eventual correção de cabeçalho;
4. eventual seleção manual da coluna de CPF;
5. commit ETL;
6. polling do job;
7. resultado final ou parcial.

### 5.2 Diagnóstico estrutural do fluxo

O fluxo atual é tecnicamente rico, porém **excessivamente concentrado em uma única superfície operacional**. Isso cria tensão entre:

- flexibilidade técnica;
- clareza de produto;
- previsibilidade de UX;
- governança operacional.

---

## 6. Achados principais da auditoria

---

### Achado 1 — Concentração excessiva de modelos mentais em uma única tela

**Descrição**  
A rota principal de importação reúne múltiplos fluxos conceitualmente distintos: Bronze, batch, mapeamento, pipeline, ETL, quick-create de evento e ativação. Essa concentração aumenta o poder do shell, mas degrada a inteligibilidade para o usuário.

**Impacto**
- curva de aprendizado alta;
- decisões erradas de fluxo;
- aumento de suporte;
- risco operacional.

**Severidade**  
Alta

**Probabilidade**  
Alta

**Recomendação**
- separar o fluxo em experiências explícitas:
  - Importação padrão
  - Importação em lote
  - Importação ETL avançada
- manter o shell técnico internamente, mas não como linguagem de produto.

---

### Achado 2 — Exposição de vocabulário técnico demais ao usuário final

**Descrição**  
Termos como “Bronze”, “Pipeline Gold”, “ETL”, “shell canônico”, “commit” e “stalled” estão próximos demais da superfície operacional.

**Impacto**
- baixa compreensão do estado real;
- aumento de erro humano;
- dependência de treinamento e suporte.

**Severidade**  
Alta

**Probabilidade**  
Alta

**Recomendação**
- substituir rótulos técnicos por linguagem orientada a negócio;
- reservar nomenclatura de engenharia para modo avançado, observabilidade e suporte.

---

### Achado 3 — Inconsistência de rastreabilidade entre fluxo Bronze e fluxo ETL

**Descrição**  
O fluxo Bronze trabalha com lote auditável, pipeline e consulta de status. O fluxo ETL, por sua vez, usa job/polling, mas a própria UI indica que o contrato atual não expõe `batch_id` equivalente.

**Impacto**
- histórico assimétrico;
- suporte mais difícil;
- auditoria inconsistente;
- governança parcial.

**Severidade**  
Alta

**Probabilidade**  
Alta

**Recomendação**
- unificar o conceito operacional de importação;
- todo processo deve gerar artefato auditável único, consultável e rastreável.

---

### Achado 4 — Indício forte de inconsistência no total de linhas exibido no preview Bronze

**Descrição**  
Há evidência de que o preview Bronze trabalha com amostra curta, enquanto o campo exibido como `total_rows` pode refletir apenas a amostra carregada, não o total real do arquivo.

**Impacto**
- falsa confiança;
- preview enganoso;
- redução da capacidade de inspeção operacional.

**Severidade**  
Alta

**Probabilidade**  
Alta

**Recomendação**
- corrigir contrato do preview para distinguir:
  - linhas totais detectadas;
  - linhas amostradas;
  - cabeçalho detectado;
  - tamanho do arquivo.

---

### Achado 5 — Mapeamento permite confirmação com contrato funcional insuficiente

**Descrição**  
O fluxo de mapeamento exige apenas que exista algum mapeamento não vazio. Isso é insuficiente para garantir valor operacional mínimo.

**Impacto**
- lotes promovidos com baixa utilidade;
- dedupe comprometido;
- risco de dados incompletos em massa;
- retrabalho futuro.

**Severidade**  
Alta

**Probabilidade**  
Média/Alta

**Recomendação**
- definir contrato mínimo obrigatório por tipo de importação;
- bloquear confirmação se o lote não atingir requisitos mínimos de identificação e uso.

---

### Achado 6 — Sinais explícitos de workload pesado e operação próxima de limite

**Descrição**  
O sistema já contém tratamento de:
- timeouts ampliados;
- polling com backoff;
- stall detection;
- reclaim de lock stale;
- chunked commit;
- heartbeat de progresso;
- otimizações específicas para Supabase/pooler.

Isso indica que o processamento já opera sob carga relevante.

**Impacto**
- sensação de lentidão;
- risco de travamento percebido;
- escalabilidade sensível;
- aumento de complexidade técnica.

**Severidade**  
Alta

**Probabilidade**  
Alta

**Recomendação**
- assumir formalmente importação como workload assíncrono de primeira classe;
- reduzir acoplamento da UX ao comportamento síncrono e a polling defensivo.

---

### Achado 7 — Dependência excessiva de estado local do frontend no modo batch

**Descrição**  
O workspace batch depende fortemente de estado local no navegador, incluindo linhas, erros, dirty flags e contexto transitório.

**Impacto**
- perda de contexto em refresh;
- fragilidade operacional;
- retomada incompleta;
- baixa confiabilidade em sessões longas.

**Severidade**  
Alta

**Probabilidade**  
Média

**Recomendação**
- persistir draft operacional de batch no backend;
- permitir retomada explícita por usuário.

---

### Achado 8 — Reaproveitamento automático de metadados por hash pode induzir erro massivo

**Descrição**  
A recuperação de metadados anteriores com base no hash do arquivo reduz atrito, mas pode causar reutilização indevida de contexto de negócio.

**Impacto**
- associação incorreta a evento;
- ativação errada;
- origem errada;
- erros silenciosos em massa.

**Severidade**  
Alta

**Probabilidade**  
Média

**Recomendação**
- tratar hint como sugestão confirmável;
- mostrar exatamente quais campos foram herdados;
- exigir confirmação explícita em campos críticos.

---

### Achado 9 — Blockers importantes são descobertos tarde

**Descrição**  
Alguns impedimentos só aparecem depois de etapas intermediárias, como colisões de cabeçalho em batch ou bloqueios por ausência de agência.

**Impacto**
- retrabalho;
- frustração;
- baixa previsibilidade.

**Severidade**  
Média/Alta

**Probabilidade**  
Média

**Recomendação**
- rodar preflight logo após upload;
- informar elegibilidade do caminho antes do usuário investir esforço.

---

### Achado 10 — Feedback é tecnicamente correto, mas pouco orientado à ação

**Descrição**  
Há muitos alerts e estados, porém nem sempre com orientação operacional clara sobre o que fazer em seguida.

**Impacto**
- dependência de interpretação;
- mais tickets de suporte;
- menor autonomia.

**Severidade**  
Média

**Probabilidade**  
Alta

**Recomendação**
- padronizar mensagens no formato:
  - o que aconteceu;
  - impacto;
  - próxima ação;
  - segurança de tentar novamente.

---

### Achado 11 — Criação ad hoc de evento/ativação reduz fricção, mas pode contaminar dados mestres

**Descrição**  
A capacidade de criar entidades dentro do importador é operacionalmente útil, mas arriscada sem governança.

**Impacto**
- cadastro mestre incompleto;
- entidades provisórias permanentes;
- dívida de dados.

**Severidade**  
Média/Alta

**Probabilidade**  
Média

**Recomendação**
- manter a funcionalidade com controles:
  - marcação como provisório;
  - trilha de criação;
  - backlog de regularização posterior.

---

### Achado 12 — Potencial risco de autorização por `batch_id`

**Descrição**  
Há indício de que múltiplos endpoints aceitam `batch_id` diretamente. Pela leitura visível, a proteção explícita por dono do lote não está inequívoca nas rotas, dependendo possivelmente de RLS ou contexto transacional.

**Impacto**
- risco potencial de acesso indevido;
- exposição de arquivo bruto;
- leitura de preview/relatório alheio;
- execução indevida de pipeline.

**Severidade**  
Crítica

**Probabilidade**  
Incerta, porém suficientemente relevante para tratamento imediato.

**Recomendação**
- validar urgentemente o modelo de autorização;
- confirmar se existe proteção efetiva por usuário/tenant;
- corrigir imediatamente se houver brecha.

---

## 7. Riscos críticos

Os riscos mais perigosos do fluxo atual são:

1. **Possível falha de autorização por `batch_id`**
2. **Importação incorreta em massa por reaproveitamento indevido de metadata hint**
3. **Promoção de lotes com mapeamento funcionalmente insuficiente**
4. **Perda de contexto no modo batch por depender do navegador**
5. **Assimetria de rastreabilidade entre Bronze e ETL**
6. **Escalada de volume sem consolidação do modelo assíncrono e auditável**
7. **Exposição de complexidade técnica demais a operadores não técnicos**

---

## 8. Oportunidades de melhoria

### 8.1 Quick wins
- corrigir o total real de linhas no preview Bronze;
- simplificar linguagem da UI;
- tornar o hint explicitamente revisável;
- padronizar mensagens de ação;
- antecipar blockers;
- exibir resumo consolidado do lote antes do avanço.

### 8.2 Melhorias de médio prazo
- persistir draft batch no backend;
- separar UX ETL da UX padrão;
- impor contrato mínimo de mapeamento;
- uniformizar rastreabilidade;
- criar preflight de elegibilidade de fluxo;
- melhorar timeline operacional.

### 8.3 Melhorias estruturais
- formalizar importação como processo assíncrono de primeira classe;
- unificar lote/job/run em modelo auditável consistente;
- criar modo simples e modo avançado;
- reduzir acoplamento entre experiência de produto e termos de engenharia;
- consolidar observabilidade por importação e não apenas por estágio interno.

---

## 9. Priorização recomendada

### Prioridade 1 — Imediata
1. validar e corrigir autorização por lote/job;
2. corrigir o contrato do preview Bronze;
3. impor validação mínima obrigatória no mapeamento;
4. tratar metadata hint com confirmação explícita.

### Prioridade 2 — Curto prazo
5. simplificar a experiência e reduzir vocabulário técnico;
6. antecipar blockers via preflight;
7. melhorar mensagens operacionais e feedback;
8. reforçar rastreabilidade do ETL.

### Prioridade 3 — Médio prazo
9. persistir draft batch no backend;
10. reorganizar navegação em fluxos separados;
11. controlar melhor criação ad hoc de entidades mestre.

### Prioridade 4 — Estrutural
12. evoluir para arquitetura assíncrona consolidada e auditável;
13. unificar o modelo operacional entre Bronze, batch e ETL;
14. consolidar governança, observabilidade e retomada enterprise.

---

## 10. Diretriz obrigatória de implementação

### 10.1 Regra mandatória de branch

**É requisito obrigatório desta auditoria que a implementação dos achados NÃO seja realizada diretamente na branch `main`.**

Toda a execução dos itens desta auditoria deverá ocorrer em uma branch dedicada, separada da branch principal, com o seguinte nome oficial:

```text
audit/leads-import-enterprise-hardening
```

### 10.2 Regras de uso da branch

A branch `audit/leads-import-enterprise-hardening` deverá ser usada para:

- implementação dos quick wins;
- correções de segurança e autorização;
- ajustes de UX e fluxo;
- refatorações de rastreabilidade;
- hardening operacional do batch e do ETL;
- criação de testes de regressão;
- documentação complementar.

### 10.3 Restrições

É expressamente vedado:

- implementar diretamente em `main`;
- fazer merge parcial sem validação dos riscos críticos;
- promover alterações sem evidência de testes;
- misturar esse trabalho com outras frentes não relacionadas ao endurecimento do importador.

### 10.4 Estratégia recomendada de merge

A branch `audit/leads-import-enterprise-hardening` deve seguir a sequência:

1. abertura da branch a partir do estado estável atual;
2. implementação por blocos priorizados;
3. validação funcional e técnica;
4. evidência de testes;
5. revisão técnica;
6. merge controlado para `main` apenas após fechamento dos riscos críticos.

---

## 11. Critérios de aceite para encerramento da auditoria

A auditoria só pode ser considerada efetivamente implementada quando houver evidência de que:

1. não existe brecha de autorização por `batch_id` ou job correlato;
2. o preview informa corretamente total real de linhas e natureza da amostra;
3. o mapeamento possui contrato mínimo obrigatório;
4. o hint de metadados não induz reaproveitamento silencioso crítico;
5. o fluxo batch é retomável com confiabilidade adequada;
6. o ETL possui rastreabilidade equivalente ao fluxo principal;
7. a interface foi simplificada para operadores;
8. blockers relevantes aparecem cedo no processo;
9. existe trilha auditável suficiente para suporte e governança;
10. todas as mudanças foram implementadas e validadas na branch:
   - `audit/leads-import-enterprise-hardening`

---

## 12. Recomendações finais

A base atual não deve ser tratada como fracasso; ela demonstra capacidade técnica relevante e já contém vários mecanismos avançados. O problema não é ausência de engenharia, e sim **acúmulo de complexidade operacional dentro de uma superfície de produto ainda pouco consolidada**.

A recomendação enterprise final é:

> endurecer o fluxo atual com foco em segurança, rastreabilidade, previsibilidade, clareza operacional e separação entre experiência simples e experiência avançada, usando a branch dedicada `audit/leads-import-enterprise-hardening` como trilho obrigatório de implementação antes de qualquer merge em `main`.

---

## 13. Anexo — síntese executiva

### Diagnóstico resumido
O fluxo é poderoso, mas excessivamente complexo, assimétrico entre caminhos e com sinais de fragilidade operacional e de governança.

### Risco dominante
Segurança/autorização por lote, seguida de qualidade de importação e erro operacional em massa.

### Melhor decisão estratégica
Não remendar somente a interface; consolidar contrato funcional, rastreabilidade e modelo operacional.

### Branch mandatória para execução
```text
audit/leads-import-enterprise-hardening
```
