NPBB — Sistema de gestão de eventos, ativações, leads e questionários
====================================================================

Este repositório reúne protótipos, backend em FastAPI e material de documentação do projeto NPBB.

Estrutura do repositório
------------------------
- backend/ — API FastAPI e modelos de domínio.
- frontend/ — código do front (Vite/React).
- docs/ — documentos e materiais de referência.
- Infra/ — arquivos de infraestrutura (ex.: docker-compose.yml).
- scripts/ — automações e scripts de suporte.

Requisitos
----------
- Python 3.10+ (backend)
- Node.js 18+ e npm (frontend)
- Docker opcional para orquestração local

Backend: como rodar
-------------------
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate      # Windows
# source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Endpoint de saúde: `GET /health` (retorna `{"status": "ok"}`).

Frontend: como rodar
--------------------
```bash
cd frontend
npm install
npm run dev
```
O Vite exibirá a URL local no terminal (geralmente http://localhost:5173).

Docker (opcional)
-----------------
```bash
docker compose up --build
```
Ajuste portas/variáveis no `Infra/docker-compose.yml` conforme necessário.

Documentação
------------
Materiais de apoio e notas estão em `docs/`. Use as pastas internas para encontrar telas, mapeamentos e referências do produto.
