# Restore Ingressos + Approval Gate (Summary)

## Origem das features (historico)
- **Base ingressos + onboarding diretoria**: commit `f59b8f7` (frontend + backend).
- **Gate de aprovacao**: **nao encontrado** no historico do frontend (sem UI de "pendente").
- **Regra "matricula + diretoria"**: nao encontrada no historico; reimplementada com base na demanda atual.

## O que foi ajustado/recuperado
- **Cadastro BB** agora exige **matricula + diretoria** (frontend + backend).
- **Status de aprovacao** passa a ser registrado como `PENDENTE` para novos usuarios BB.
- **Gate de aprovacao** aplicado nas rotas de ingressos (backend), bloqueando solicitacoes quando `status_aprovacao != APROVADO`.
- **UI** mostra mensagem de pendencia quando o usuario BB nao esta aprovado.
- **UI** bloqueia acesso aos ingressos quando nao ha matricula informada.

## Arquivos principais alterados
- Backend:
  - `backend/app/schemas/usuario.py` (regras de BB + campos de leitura)
  - `backend/app/routers/usuarios.py` (cadastro BB com matricula + diretoria)
  - `backend/app/routers/ingressos.py` (gate de aprovacao + matricula)
  - `backend/app/models/models.py` (diretoria_id calculado)
  - `backend/tests/test_auth_login.py`
  - `backend/tests/test_ingressos_endpoints.py`
  - `backend/tests/test_usuarios_create_endpoints.py`
- Frontend:
  - `frontend/src/pages/Register.tsx` (matricula + diretoria obrigatorias)
  - `frontend/src/pages/IngressosPortal.tsx` (mensagem pendente/aprovacao)
  - `frontend/src/services/auth.ts` (campos no usuario logado)

## Decisoes inferidas (nao encontradas no historico)
- **Login BB pendente**: liberado para permitir feedback na UI; bloqueio ocorre em `/ingressos`.
- **Regra BB**: exige matricula + diretoria no cadastro.

## Como validar localmente
Backend:
- `python -m pytest -q`

Fluxos minimos:
1) Usuario BB cadastra com matricula + diretoria:
   - status_aprovacao = PENDENTE
   - acesso a `/ingressos` bloqueado com mensagem de aprovacao
2) Usuario BB aprovado (status_aprovacao=APROVADO):
   - acesso a `/ingressos` liberado
