---
doc_id: "TASK-4.md"
user_story_id: "US-5-04-UI-EMISSAO-OPERACIONAL"
task_id: "T4"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T3"
parallel_safe: false
write_scope:
  - "frontend/src/pages/IngressosPortal.tsx"
  - "frontend/src/components/ingressos/"
tdd_aplicavel: false
---

# TASK-4 - Preview e layout basico da categoria na emissao

## objetivo

Quando o backend expuser **metadados de layout** da categoria (ou URL de preview segura) coerentes com a emissao, a UI deve apresentar **preview ou documento** com **layout basico** da categoria no momento da emissao ou imediatamente apos sucesso, conforme segundo Given/When/Then da US — sem implementar “template avancado” reservado a backlog.

## precondicoes

- T3 concluida: fluxo de emissao e estado de sucesso existentes.
- Contrato da API ou entidade de categoria documenta quais campos de layout/cor/logo/texto estao disponiveis para o cliente (US-5-02/US-5-03 ou FEATURE-3); se o backend ainda nao expuser metadados, esta task limita-se a extensao preparada com `stop_conditions`.

## orquestracao

- `depends_on`: ["T3"].
- `parallel_safe`: false.
- `write_scope`: `IngressosPortal.tsx` e `frontend/src/components/ingressos/`; assets estaticos apenas se ja existir convencao no repo.

## arquivos_a_ler_ou_tocar

- Componentes criados ou alterados em T3
- `frontend/src/pages/IngressosPortal.tsx`
- Resposta da API de emissao ou endpoint auxiliar de categoria *(conforme contrato real)*
- PRD sec. 2.6 *(design coerente com o produto)*

## passos_atomicos

1. Mapear campos de layout basico disponiveis na resposta de emissao ou em fetch complementar autorizado pelo contrato.
2. Implementar componente de preview (ex. cartao resumo, cabecalho com nome do evento/categoria, cores) usando apenas dados permitidos; fallback claro quando metadados ausentes.
3. Garantir que o preview nao exibe PII extra nem payload QR integral em claro contra politica LGPD/PRD.
4. Documentar no codigo ou na task seguinte qualquer limitacao (“template avancado” fora de escopo) se o produto solicitar mais do que o contrato oferece.

## comandos_permitidos

- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`

## resultado_esperado

Utilizador ve alinhamento visual basico com a categoria quando os metadados existem; caso contrario, fluxo permanece funcional sem erro gritante.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run typecheck`
- Teste manual com categoria que forneca metadados e com categoria sem metadados (degradacao graciosa).

## stop_conditions

- Parar se nao houver qualquer campo de layout no contrato — registar dependencia em FEATURE-3/API e nao inventar endpoints.
