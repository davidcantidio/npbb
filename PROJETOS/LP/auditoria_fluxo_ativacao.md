# Relatório de Auditoria – Fase 1 (Fundação)  
**Projeto:** LP – QR por Ativação  
**Versão do PRD:** v1.0 – março/2026  
**Data da auditoria:** Março/2026

## Resumo Executivo

A implementação da Fase 1 cobre os principais itens funcionais descritos no PRD, incluindo modelos de dados, migrações, endpoints de criação/listagem de ativações, landing pages públicas e geração de QR Code único por ativação.

**Principais problemas identificados:**

- **Divergência grave de contrato API**: endpoint de submissão de lead implementado como `/landing/ativacoes/{id}/submit` em vez de `/leads/` (conforme PRD §8.2)
- **Ausência de campo obrigatório**: `lead_reconhecido` não está presente na resposta de submissão
- **Arquivos monolíticos** violando SPEC-ANTI-MONOLITO:
  - `models.py` → 1364 linhas (> 600 – bloqueante)
  - `ativacao.py` → 421 linhas (> 400 – alerta)
- **Cobertura de testes insuficiente** em pontos críticos: validação de CPF, bloqueio de duplicidade, migrações e endpoint de submissão com `ativacao_id`
- **LGPD** – CPF armazenado em claro nas tabelas (sem evidência de criptografia em repouso)

**Veredito:** **HOLD**

Recomenda-se correção das não conformidades de alta e média severidade antes de avançar para o próximo gate.

## Escopo Auditado

- Modelos: `Ativacao`, `ConversaoAtivacao`, `LeadReconhecimentoToken`
- Migrações Alembic (tabelas + índices compostos)
- Endpoints REST:
  - CRUD de ativações: `/eventos/{evento_id}/ativacoes`
  - Landing pública: `/eventos/{evento_id}/ativacoes/{ativacao_id}/landing`
  - Submissão de lead: `/landing/ativacoes/{id}/submit`
- Serviços: geração de QR Code (`build_qr_code_svg`), URLs públicas (`hydrate_ativacao_public_urls`)
- Testes unitários/integração existentes em `backend/tests/`

## Conformidades

- Modelos e índices criados conforme PRD §6
- Índice composto `(ativacao_id, cpf)` presente
- Token de reconhecimento armazenado como hash (boa prática LGPD)
- Endpoint GET `/.../landing` retorna `lead_reconhecido` corretamente quando há token válido
- Geração de QR Code único por ativação (URL + QR SVG)
- Autorização JWT nos endpoints de gestão (operador)

## Não Conformidades

| ID       | Descrição                                                                 | Severidade | Comentário |
|----------|------------------------------------------------------------------------------------------------------------------------|------------|------------|
| F1-NAO01 | Ausência do campo `lead_reconhecido` na resposta de submissão de lead                                          | **HIGH**   | Desvio direto do contrato PRD §8.2 |
| F1-NAO02 | Endpoint de submissão implementado como `/landing/.../submit` ao invés de `/leads/`                            | **HIGH**   | Divergência de contrato / rastreabilidade |
| F1-NAO03 | Arquivo `models.py` com 1364 linhas (threshold bloqueante >600)                                                | **MEDIUM** | Violação SPEC-ANTI-MONOLITO |
| F1-NAO04 | Arquivo `ativacao.py` com 421 linhas (threshold alerta >400)                                                   | **MEDIUM** | Violação SPEC-ANTI-MONOLITO |
| F1-NAO05 | Ausência de testes para validação de CPF (dígito verificador)                                                  | **MEDIUM** | Risco de regressão |
| F1-NAO06 | Ausência de testes para bloqueio de CPF duplicado em ativação única                                            | **MEDIUM** | Risco funcional crítico |
| F1-NAO07 | Ausência de testes para endpoint de submissão (`/landing/.../submit`)                                          | **MEDIUM** | Risco de regressão |
| F1-NAO08 | Ausência de testes automatizados de migração (campos e índices)                                                | **MEDIUM** | Risco em deploy/rollback |
| F1-RISCO01 | CPF armazenado em claro nas tabelas `lead` e `conversao_ativacao` (sem criptografia em repouso evidente)      | **MEDIUM** | Não conformidade LGPD recomendada |

## Análise de Complexidade Estrutural

| Arquivo                        | Linhas lógicas | Status               | Observação                              |
|--------------------------------|----------------|----------------------|-----------------------------------------|
| `backend/app/models/models.py` | 1364           | **BLOCK** (>600)     | Monolítico – deve ser particionado      |
| `backend/app/routers/ativacao.py` | 421         | **WARN**  (>400)     | Recomenda-se dividir responsabilidades  |
| `backend/app/routers/landing_public.py` | 361   | OK                   | Dentro dos limites                      |
| `submit_public_lead` (service) | ~70            | Aviso leve           | Próximo do limite warn (>60)            |

## Riscos Antecipados

- Regressão no fluxo CPF-first (Fase 2) por falta de testes de validação/duplicidade
- Dificuldade de manutenção e maior incidência de bugs devido a arquivos monolíticos
- Problemas de integração com front-end ou sistemas externos por divergência de contrato API
- Exposição maior de dados pessoais (CPF em claro) – risco LGPD

## Decisão

**Veredito:** **HOLD**

**Justificativa:**  
Não conformidades funcionais críticas (contrato API + campo obrigatório) e estruturais bloqueantes (monolitismo) impedem a aprovação da Fase 1 no estado atual.

## Follow-ups Bloqueantes

- **F1-NAO01** – Incluir `lead_reconhecido: bool` na resposta do endpoint de submissão
- **F1-NAO02** – Refatorar `models.py` (dividir em múltiplos arquivos de modelo)
- **F1-NAO03** – Criar testes automatizados para:
  - Validação de CPF válido/inválido
  - Bloqueio de CPF duplicado em ativação `checkin_unico = true`

## Follow-ups Não Bloqueantes / Recomendações

- **F1-RAST01** – Alinhar e documentar a URL de submissão real vs. contrato PRD
- **F1-RISCO01** – Avaliar e, se possível, implementar criptografia em repouso ou tokenização do CPF
- Aumentar cobertura de testes de integração para migrações e endpoint de submissão

**Próximo passo sugerido:** Corrigir itens bloqueantes → reenviar para auditoria de revalidação (F1 R02).