backend/
├── app/
│   ├── core/          config, security, deps
│   ├── models/        SQLModel models
│   ├── schemas/       Pydantic v2
│   ├── routers/       v1/eventos.py, v1/cotas.py, v1/dashboard.py
│   ├── services/      regras de negócio + integração Salesforce
│   ├── migrations/    Alembic
│   └── main.py
frontend/
├── src/
│   ├── components/    reutilizáveis (ChipList, KPI, TabsEvento, DataGrid)
│   ├── pages/         Dashboard, EventosList, EventoForm, EventoDetalhes, Ativos
│   ├── store/         Zustand
│   ├── services/      api.ts (axios + interceptors)
│   └── App.tsx
Infra
├── docker-compose.yml (FastAPI + PostgreSQL + Nginx)