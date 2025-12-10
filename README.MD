Aqui está o seu `README.md` completamente formatado e organizado em Markdown de forma limpa, profissional e visualmente agradável:

```markdown
# NPBB – Sistema de Gestão de Eventos, Ativações, Leads, Ingressos e Questionários

Este projeto é uma **evolução interna do Banco do Brasil** para gestão completa de:

- Eventos  
- Ativações  
- Investimentos  
- Leads (com integração Salesforce)  
- Gamificação  
- Termos de uso por ativação  
- Cupons  
- Ingressos (cotas por diretoria)  
- Convidadores e convidados  
- Questionários (estrutura + respostas)

O sistema foi construído com base em **engenharia reversa** do aplicativo oficial **BB Leads**, com melhorias significativas em modelagem de dados, experiência do usuário (UX) e governança.

---

# 🚀 Stack Tecnológica

### **Backend**
- **Python 3.11+**
- **FastAPI**
- **SQLAlchemy / SQLModel**
- **PostgreSQL**
- **Alembic** (migrações)
- **Uvicorn**
- **Pydantic v2**

### **Frontend**
- **React**
- **Material UI** (Material Design 3)
- **Vite**
- **React Router**
- **React Hook Form** (formulários)
- **Zustand** (gerenciamento de estado global)

### **Infraestrutura**
- **Docker / Docker Compose**
- **pgAdmin** (opcional)

---

# 📁 Estrutura do Projeto

```
npbb/
├── backend/
│   ├── app/
│   │   ├── models/      # Models SQLAlchemy/SQLModel
│   │   ├── schemas/     # Pydantic DTOs
│   │   ├── routes/      # Endpoints FastAPI
│   │   ├── services/    # Regras de negócio
│   │   ├── core/        # Config, banco, logs
│   │   ├── utils/       # Funções auxiliares
│   │   └── main.py      # App FastAPI
│   ├── alembic/         # Migrações do banco
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── pages/       # Rotas/páginas
│   │   ├── components/  # Componentes reutilizáveis
│   │   ├── hooks/        # Hooks personalizados
│   │   ├── store/       # Zustand stores
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
│
├── docs/
│   ├── banco/
│   │   └── schema_final.sql     # ESQUEMA COMPLETO ATUALIZADO
│   ├── telas/       # Mockups e protótipos
│   └── prd/         # Documentos de produto (PRDs)
│
├── docker-compose.yml
└── README.md
```

---

# 🗄️ Banco de Dados (PostgreSQL)

- Mais de **25 tabelas**
- Estrutura completa para:
  - Eventos e ativações
  - Gamificação
  - Termos de uso
  - Cupons
  - Leads e integração Salesforce
  - Cotas de ingressos por diretoria
  - Convites e convidados
  - Questionários (páginas, perguntas, opções e respostas)

O esquema final e atualizado está em:  
`docs/banco/schema_final.sql`

---

# ▶️ Como Rodar o Projeto (Ambiente de Desenvolvimento)

### 1. Clonar o repositório
```bash
git clone https://github.com/davidcantidio/npbb.git
cd npbb
```

### 2. Rodar com Docker (recomendado)
```bash
docker-compose up --build
```

**Serviços disponíveis:**
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- Documentação API (Swagger): http://localhost:8000/docs
- Banco de dados: `localhost:5432`

### 3. Rodar Backend manualmente

```bash
cd backend
python -m venv venv
source venv/bin/activate    # No Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### 4. Rodar Frontend manualmente

```bash
cd frontend
npm install
npm run dev
```

---

# ✨ Convenções do Projeto

### Backend
- Endpoints RESTful
- Nomenclatura em inglês
- Models com **SQLModel**
- Regras de negócio em `services/`
- Validação com **Pydantic v2**

### Frontend
- Páginas = rotas
- Componentes pequenos e reutilizáveis
- Estado global apenas quando necessário (Zustand)
- Formulários com **React Hook Form + Zod**
- Design System: **Material Design 3**

---

# 🔗 Integração com Salesforce (Leads)

Fluxo:
1. Frontend envia dados do lead
2. Backend chama API do Salesforce
3. Salesforce retorna `id_salesforce`
4. Backend salva o lead localmente + associação com ativações

> Erros na API do Salesforce impedem o salvamento local (garantia de consistência).

---

# 📊 Dashboard Inicial

- Contadores em tempo real
- Filtros reativos (data, evento, estado, cidade, diretoria)
- Gráfico principal + blocos por região/estado

Endpoint:
```http
GET /dashboard?data_inicio=&data_fim=&evento_id=&estado=&cidade=
```

---

# 🧱 Módulos Implementados / Em Desenvolvimento

### Ingressos (Cotas por Diretoria)
- CRUD de cotas por evento × diretoria
- Visualização em cards (usado vs disponível)
- Fluxo completo de convite → convidado

### Questionários Dinâmicos
- Multi-página
- Diversos tipos de perguntas
- Agregação de respostas por evento/ativação/lead

---

# 🛡️ Segurança

- JWT (em implementação)
- Rate limiting no endpoint Salesforce
- Sanitização rigorosa de campos dinâmicos (tags, territórios, etc.)

---

# 📌 Próximos Passos Sugeridos

- [ ] Completar models SQLModel com SQLModel
- [ ] Gerar migrações Alembic baseadas no `schema_final.sql`
- [ ] Implementar CRUD completo de **Eventos**
- [ ] Criar tela de criação/edição de evento (frontend)
- [ ] Desenvolver módulos **Ativação** e **Gamificação**
- [ ] Implementar **Editor de Questionários**
- [ ] Integrar com Salesforce (ambiente de homologação)

---

# 👨‍💻 Manutenção

**Projeto interno NPBB – Banco do Brasil**  
Criado e mantido por David Cantídio

Toda documentação técnica, PRDs e mockups estão em:
```
docs/
```

Qualquer dúvida: abrir issue ou PR diretamente no repositório.

**Vamos juntos construir o futuro das ativações do BB!**
```

Pronto! Agora seu `README.md` está profissional, bem estruturado e perfeito para compartilhar com equipe, stakeholders ou auditoria interna.