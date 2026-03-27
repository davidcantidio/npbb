---
doc_id: "TASK-1.md"
user_story_id: "US-5-04-UI-EMISSAO-OPERACIONAL"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on: []
parallel_safe: false
write_scope:
  - "frontend/src/services/ingressos.ts"
  - "frontend/src/services/ingressos_admin.ts"
tdd_aplicavel: false
---

# TASK-1 - Cliente HTTP e tipos para emissao interna com QR

## objetivo

Expor em `frontend/src/services/ingressos.ts` e/ou `frontend/src/services/ingressos_admin.ts` funcoes tipadas para a operacao de **emissao** acordada na [US-5-02](../../US-5-02-SERVICO-E-API-EMISSAO/README.md), com request/response alinhados ao **contrato minimo do payload QR** da [US-5-03](../../US-5-03-CONTRATO-MINIMO-PAYLOAD-QR/README.md) (OpenAPI em `/docs` ou artefatos dessas USs), incluindo tratamento de erros HTTP coerente com o restante portal (sem vazar dados sensiveis em mensagens de UI).

## precondicoes

- [US-5-02](../../US-5-02-SERVICO-E-API-EMISSAO/README.md) e [US-5-03](../../US-5-03-CONTRATO-MINIMO-PAYLOAD-QR/README.md) concluidas (`done`) e contrato de API estavel (paths, verbos, schemas de emissao e campos expostos ao cliente).
- Leitura do contrato real (OpenAPI ou documento de contrato da feature) antes de fixar URLs, tipos e campos opcionais de preview.

## orquestracao

- `depends_on`: nenhuma task anterior nesta US.
- `parallel_safe`: false.
- `write_scope`: apenas os dois servicos de ingressos no frontend; reutilizar padroes existentes de `fetch`, `Authorization: Bearer` e helpers de erro ja usados nesses modulos.

## arquivos_a_ler_ou_tocar

- `frontend/src/services/ingressos.ts`
- `frontend/src/services/ingressos_admin.ts`
- `frontend/src/services/http.ts` *(se existir base URL ou helpers partilhados)*
- OpenAPI / rotas backend entregues pela US-5-02
- Documento de contrato minimo QR (US-5-03)

## passos_atomicos

1. Identificar endpoint(s) de emissao individual (ou fluxo minimo exposto ao operador) e resposta que inclua identificador unico, estado ou campo que permita inferir `qr_emitido`, e qualquer blob URL ou metadado de layout permitido pelo backend.
2. Definir tipos TypeScript para o corpo da requisicao e da resposta, espelhando o JSON sem inventar campos fora do contrato.
3. Implementar funcao(as) `async` que recebem `token` (e parametros de negocio acordados: evento, categoria, destinatario, etc.) e devolvem resultado tipado ou erro tratado.
4. Garantir que erros 401/403/422/409 mapeiam para mensagens ou codigos consumiveis pela UI (T2-T3) sem logar payload completo em consola em producao.

## comandos_permitidos

- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`

## resultado_esperado

Camada de servico pronta para ser consumida pelo fluxo de UI, desacoplada de componentes React, alinhada ao contrato US-5-02/US-5-03.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run typecheck` sem erros novos atribuiveis a esta alteracao.
- Revisao manual: assinaturas e paths alinhados ao OpenAPI ou documento de contrato versionado.

## stop_conditions

- Parar se endpoints ou schemas de emissao ainda nao existirem no backend (bloqueio ate US-5-02).
- Parar se o formato do payload QR ou campos de resposta divergirem entre documentacao e implementacao — alinhar com backend antes de fixar tipos.
