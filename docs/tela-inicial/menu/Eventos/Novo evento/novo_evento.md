```markdown
# Formulário de Evento (Cadastro / Edição)

## 1. Nome da Tela
**Formulário de Evento**  
Tela usada para criar ou editar um evento.  
Contém abas que agrupam funcionalidades adicionais relacionadas ao evento e servirá de base para o fluxo de criação de eventos no novo sistema.

---

## 2. Referência Visual
Print da tela (sistema original):  
`docs/tela-inicial/menu/Eventos/Novo evento/novo_evento.png`  

Estado exibido: formulário preenchido, aba **Evento** selecionada.

---

## 3. Estrutura da Tela (Componentes Visíveis)

### 3.1 Navegação
- Menu lateral:
  - Dashboard
  - Leads (será removido no nosso sistema)
  - Eventos
  - Cupons
- Logo do Banco do Brasil

### 3.2 Header Superior
- Ícone menu sanduíche
- Ícone fullscreen
- Ícone modo escuro
- Perfil do usuário (Admin)
- Breadcrumb: `Dashboard > Eventos`

### 3.3 Guias Superiores (Abas do Evento)

| Ordem | Nome da Aba              | Status no Novo Sistema                                      |
|------|--------------------------|-------------------------------------------------------------|
| 1    | **Evento**               | Aba atual / principal                                       |
| 2    | Formulário de Lead       | Mantida                                                     |
| 3    | Gamificação              | **Substituída** por “Ingressos / Cotas” (cotas por diretoria) |
| 4    | Ativações                | Mantida                                                     |
| 5    | Questionário             | Em avaliação                                                |

### 3.4 Conteúdo da Aba “Evento”

#### Ordem dos campos (de cima para baixo)

| #  | Campo                     | Tipo                                   | Mapeamento no Banco                              | Observação / Novo |
|----|---------------------------|----------------------------------------|--------------------------------------------------|-------------------|
| 1  | Nome                      | Texto                                  | `evento.nome`                                    | Obrigatório       |
| 2  | Estado                    | Dropdown (UF)                          | `evento.estado`                                  | Obrigatório       |
| 3  | Local (Cidade)            | Dropdown                               | `evento.cidade`                                  | Obrigatório       |
| 4  | **Diretoria**             | Dropdown                               | `evento.diretoria_id` → FK `diretoria`           | **Novo campo obrigatório** |
| 5  | Divisão demandante        | Dropdown                               | `evento.divisao_demandante` (enum `divisao`)      | Obrigatório       |
| 6  | Tipo de Evento            | Dropdown                               | `evento.tipo_id` → FK `tipo_evento`               | Obrigatório       |
| 7  | **Subtipo de Evento**     | Dropdown dependente                    | `evento.subtipo_id` → FK `subtipo_evento`         | **Explicita no formulário** |
| 8  | Territórios               | Multi-select com chips removíveis      | N:N → `evento_territorio`                         |                   |
| 9  | **Tags livres**           | Multi-select + criação dinâmica        | N:N → `evento_tag`                                | **Novo**          |
| 10 | Descrição                 | Textarea com contador (ex: 30/240)     | `evento.descricao`                               |                   |
| 11 | Data de início prevista   | Date picker                            | `evento.data_inicio_prevista`                    | Obrigatório       |
| 12 | Data final prevista       | Date picker                            | `evento.data_fim_prevista`                       | Obrigatório       |
| 13 | Encerrado                 | Switch booleano                        | Impacta `evento.status` (ex: 'realizado')        |                   |

#### Campos da tabela `evento` que **não aparecem** nesta aba (serão tratados em outras seções)

- `data_inicio_realizada`
- `data_fim_realizada`
- `publico_projetado`
- `publico_realizado`
- `concorrencia`
- `agencia_id`
- `gestor_id`
- `thumbnail`
- `qr_code_url`

### 3.5 Modelo de Banco de Dados

```sql
CREATE TABLE evento (
    id SERIAL PRIMARY KEY,
    thumbnail VARCHAR(500),
    divisao_demandante divisao,
    qr_code_url VARCHAR(500) UNIQUE,
    nome VARCHAR(100) NOT NULL,
    descricao VARCHAR(240) NOT NULL,
    data_inicio_prevista DATE,
    data_inicio_realizada DATE,
    data_fim_prevista DATE,
    data_fim_realizada DATE,
    publico_projetado INT,
    publico_realizado INT,
    concorrencia BOOLEAN NOT NULL,
    cidade VARCHAR(40) NOT NULL,
    estado VARCHAR(40) NOT NULL,
    agencia_id INT NOT NULL,
    diretoria_id INT,                     -- Novo campo
    gestor_id INT,
    tipo_id INT NOT NULL,
    subtipo_id INT,
    status status_evento NOT NULL,
    FOREIGN KEY (agencia_id) REFERENCES agencia(id),
    FOREIGN KEY (diretoria_id) REFERENCES diretoria(id),
    FOREIGN KEY (gestor_id) REFERENCES funcionario(id),
    FOREIGN KEY (tipo_id) REFERENCES tipo_evento(id),
    FOREIGN KEY (subtipo_id) REFERENCES subtipo_evento(id)
);

-- Relações N:N
CREATE TABLE evento_territorio (
    id SERIAL PRIMARY KEY,
    evento_id INT NOT NULL,
    territorio_id INT NOT NULL,
    FOREIGN KEY (evento_id) REFERENCES evento(id) ON DELETE CASCADE,
    FOREIGN KEY (territorio_id) REFERENCES territorio(id),
    UNIQUE (evento_id, territorio_id)
);

CREATE TABLE evento_tag (
    id SERIAL PRIMARY KEY,
    evento_id INT NOT NULL,
    tag_id INT NOT NULL,
    FOREIGN KEY (evento_id) REFERENCES evento(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tag(id),
    UNIQUE (evento_id, tag_id)
);
```

---

## 4. Comportamento da Tela

- Alteração de qualquer campo → atualiza estado interno (auto-save ao trocar aba ou clicar em “Próximo”)
- **Botão “Próximo”**:
  - Valida campos obrigatórios da aba Evento
  - Executa auto-save
  - Navega para aba “Formulário de Lead”
- **Validações**:
  - Data final prevista ≥ data início prevista
  - Campos obrigatórios destacados em vermelho se vazios
- **Territórios e Tags** → chips removíveis; criação/atualização automática nas tabelas de relação

## 5. Regras de Negócio Principais

| Regra                              | Detalhe                                                                 |
|------------------------------------|-------------------------------------------------------------------------|
| Diretoria                          | Obrigatória; usada também para lógica de cotas de ingressos             |
| Subtipo de Evento                  | Deve pertencer ao Tipo selecionado (trigger/validação no backend)       |
| Tags livres                        | Criação dinâmica + autocomplete                                        |
| Switch “Encerrado”                 | Sugestão: true → status = 'realizado' (a confirmar validação)           |
| Campos de resultado (público, datas realizadas, concorrência) | Edição em aba/seção específica de “Resultados” (a definir)              |

## 6. Diferenças – Sistema Original × Nova Versão

| Item                     | Sistema Original                    | Nova Versão                                      |
|--------------------------|-------------------------------------|--------------------------------------------------|
| Diretoria                | Não existe                          | **Novo campo obrigatório**                       |
| Subtipo de Evento        | Não explícito                       | Campo explícito e obrigatório                    |
| Tags livres              | Não existe                          | **Novo** multi-select com criação dinâmica       |
| Aba Gamificação          | Existe                              | **Substituída** por “Ingressos / Cotas”          |
| Territórios              | Multi-select simples                | Mesma UI, mas com modelagem explícita no banco   |

## 7. Pendências / Dúvidas

- Onde editar campos de resultado (datas realizadas, público, concorrência)?
- Regra final do switch “Encerrado” (altera status diretamente? exige datas realizadas?)
- Estratégia de salvamento: apenas “Próximo” com auto-save ou botão “Salvar” global?

## 8. Backlog da Tela (Requisitos)

### Backend
- `POST /eventos`, `GET /eventos/:id`, `PUT /eventos/:id`
- Validações de obrigatórios, datas e compatibilidade tipo/subtipo
- Endpoints auxiliares para listas (estados, cidades, diretorias, tipos, subtipos, territórios, tags)
- Criação dinâmica de tags

### Frontend
- Componente `<EventoForm />` com abas (Material Design 3)
- Componentes específicos para cada campo
- Validação + feedback visual
- Auto-save ao trocar aba ou clicar “Próximo”
- Mapeamento correto para payload da API (incluindo arrays de `territorios_ids` e `tags_ids`)

Pronto para ser colocado diretamente no Notion, GitHub ou documento Markdown!
```