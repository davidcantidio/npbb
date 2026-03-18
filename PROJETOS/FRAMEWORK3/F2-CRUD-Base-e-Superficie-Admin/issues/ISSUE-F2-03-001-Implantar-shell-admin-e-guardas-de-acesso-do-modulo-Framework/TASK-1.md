---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F2-03-001-Implantar-shell-admin-e-guardas-de-acesso-do-modulo-Framework"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: false
---

# TASK-1 - Definir recorte de acesso do modulo admin

## objetivo

fechar a regra minima de autenticacao e acesso do modulo Framework

## precondicoes

- `ISSUE-F1-03-002` concluida

## arquivos_a_ler_ou_tocar

- `frontend/src/store/auth.tsx`
- `frontend/src/components/ProtectedRoute.tsx`
- `frontend/src/app/AppRoutes.tsx`
- `backend/app/core/auth.py`

## passos_atomicos

1. mapear como o repositorio distingue usuarios autenticados
2. definir criterio minimo de acesso ao modulo `framework`
3. registrar a decisao como contrato do modulo admin

## comandos_permitidos

- `rg -n "tipo_usuario|ProtectedRoute|auth" frontend/src backend/app`

## resultado_esperado

Regra minima de acesso do admin aprovada.

## testes_ou_validacoes_obrigatorias

- revisao contra o PRD e o auth atual

## stop_conditions

- parar se a decisao exigir RBAC mais avancado do que o PRD cobre
