# RFC: Migracao de Autenticacao para Cookie HttpOnly

## Status
- Proposta
- Data: 2026-02-24
- Escopo desta RFC: trilha de arquitetura e rollout gradual, sem cutover imediato.

## Contexto
A autenticacao atual no frontend usa `access_token` em `localStorage`, com envio via header `Authorization`. Esse modelo e funcional, mas aumenta risco de exfiltracao por XSS e exige logica de refresh/logout no cliente para manter sessao valida.

## Objetivo
Migrar gradualmente para sessao baseada em cookie `HttpOnly` mantendo compatibilidade operacional e sem downtime.

## Nao objetivos
- Nao executar cutover nesta iteracao.
- Nao remover imediatamente o header bearer legado.
- Nao alterar contratos funcionais de rotas do produto.

## Modelo proposto
- `Set-Cookie` no login com:
  - `HttpOnly`
  - `Secure` (obrigatorio em producao)
  - `SameSite=Lax` (ou `Strict` para cenarios internos sem integracoes cross-site)
  - `Path=/`
  - `Max-Age`/`Expires` alinhado a politica de sessao
- Cookie de refresh separado opcional com janela maior e rotacao.
- Frontend deixa de persistir token em `localStorage` no modo novo.

## Estrategia CSRF
- Adotar padrao double-submit token ou token CSRF em header custom:
  - Backend emite cookie nao-HttpOnly de CSRF (ex.: `csrf_token`).
  - Frontend envia o valor em header `X-CSRF-Token` em requests mutativas (`POST/PUT/PATCH/DELETE`).
- Validacao obrigatoria no backend para requests autenticadas por cookie.

## Mudancas necessarias no backend
1. Login (`POST /auth/login`): emitir cookie(s) de sessao e payload de usuario.
2. Refresh (`POST /auth/refresh`): rotacionar sessao/cookie e invalidar token anterior.
3. Logout (`POST /auth/logout`): invalidar sessao server-side e expirar cookie.
4. Middlewares:
   - suporte a autenticacao por cookie;
   - validacao CSRF;
   - CORS com `credentials=true` apenas para origens confiaveis.
5. Observabilidade:
   - auditoria de sessao (criacao/refresh/revogacao);
   - metrica de falha CSRF e de refresh.

## Mudancas necessarias no frontend
1. Cliente HTTP:
   - habilitar `credentials: "include"` no `fetchWithAuth` para modo cookie.
2. Auth store:
   - remover dependencia de `localStorage` em modo cookie;
   - usar `GET /auth/me` como fonte de sessao ativa.
3. Tratamento de erro:
   - `401` implica logout limpo e redirecionamento.
4. Feature flag:
   - `VITE_AUTH_MODE=bearer|cookie` para rollout gradual e rollback rapido.

## Plano de rollout gradual
1. Fase 1 - Compatibilidade dual:
   - backend aceita bearer e cookie;
   - frontend segue bearer por padrao.
2. Fase 2 - Piloto:
   - ativar modo cookie para grupo interno controlado.
3. Fase 3 - Expansao:
   - aumentar base, monitorar erros CSRF, latencia e taxa de login.
4. Fase 4 - Cutover:
   - cookie vira padrao;
   - bearer mantido temporariamente como fallback.
5. Fase 5 - Descomissionamento:
   - remover bearer apos janela de estabilidade definida.

## Plano de rollback
- Trocar `VITE_AUTH_MODE` para `bearer` no frontend.
- Manter backend dual-stack durante todo rollout.
- Revalidar login/refresh/logout e auditoria de seguranca apos rollback.

## Riscos e mitigacoes
- Risco: falha de CSRF em mutacoes legitimas.
  - Mitigacao: telemetria de falha por rota e rollout por cohort.
- Risco: CORS/credentials mal configurado.
  - Mitigacao: allowlist estrita de origem + testes de integracao.
- Risco: quebra em clientes legados.
  - Mitigacao: janela dual-stack e fallback por feature flag.

## Criterios de aceite da trilha
- Documento aprovado por frontend e backend.
- Ambiente staging com modo dual funcionando.
- Observabilidade minima implantada (taxa 401/403 CSRF, refresh success rate).
- Plano de cutover e rollback revisado antes de producao.
