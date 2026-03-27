---
doc_id: "TASK-3.md"
user_story_id: "US-5-04-UI-EMISSAO-OPERACIONAL"
task_id: "T3"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "frontend/src/pages/IngressosPortal.tsx"
  - "frontend/src/components/ingressos/"
tdd_aplicavel: false
---

# TASK-3 - Fluxo de emissao ate sucesso com estado `qr_emitido`

## objetivo

Implementar o fluxo em que o operador conclui a emissao para um destinatario (campos minimos acordados com a API), chama o cliente T1, e a UI reflecte **sucesso** com estado coerente com `qr_emitido`, mostrando apenas **referencia ao identificador** ou artefacto previsto pelo contrato (sem expor dados desnecessarios nem payload completo do QR em claro se a politica/UI assim o exigir).

## precondicoes

- T1 e T2 concluidas.
- Contrato de resposta da emissao suficiente para distinguir sucesso e para exibir identificador ou referencia segura (US-5-02/US-5-03).

## orquestracao

- `depends_on`: ["T2"] *(entrada e RBAC na superficie prontos)*.
- `parallel_safe`: false.
- `write_scope`: `IngressosPortal.tsx` e componentes novos sob `frontend/src/components/ingressos/` *(criar pasta se nao existir)*.

## arquivos_a_ler_ou_tocar

- `frontend/src/pages/IngressosPortal.tsx`
- `frontend/src/services/ingressos.ts` e/ou `frontend/src/services/ingressos_admin.ts`
- Padroes de formulario e feedback de sucesso/erro ja usados no frontend (MUI ou equivalente)
- `README.md` desta US

## passos_atomicos

1. Implementar formulario ou passos minimos para colectar dados exigidos pela API de emissao (validacao client-side apenas onde nao duplicar regras de negocio do backend).
2. Integrar chamada ao servico de emissao (T1): loading, desabilitar submissoes repetidas durante o pedido, tratar erros de negocio e autorizacao.
3. No sucesso, apresentar confirmacao explicita alinhada ao estado `qr_emitido` (texto/icone/estado visual) e referencia ao identificador unico ou token opaco permitido pelo contrato.
4. Garantir que a UI **nao** inclui funcionalidade de scanner ou validacao de uso unico no portao.

## comandos_permitidos

- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`

## resultado_esperado

Fluxo utilizavel de ponta a ponta na UI para uma emissao bem-sucedida, com feedback claro e minimo vazamento de dados.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run typecheck`
- Teste manual: caminho feliz com categoria interna com QR configurada (ambiente de integracao quando backend estiver pronto).

## stop_conditions

- Parar se a API nao devolver forma estavel de representar `qr_emitido` ou identificador na UI — alinhar contrato com US-5-02 antes de simular estados.
