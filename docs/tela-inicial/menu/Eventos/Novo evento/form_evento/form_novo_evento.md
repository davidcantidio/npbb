```markdown
# FormulÃ¡rio de Evento (Cadastro / EdiÃ§Ã£o)

## 1. Nome da Tela
**FormulÃ¡rio de Evento**  
Tela usada para criar ou editar um evento.  
ContÃ©m abas que agrupam funcionalidades adicionais relacionadas ao evento e servirÃ¡ de base para o fluxo de criaÃ§Ã£o de eventos no novo sistema.

---

## 2. ReferÃªncia Visual
Print da tela (sistema original):  
`docs/tela-inicial/menu/Eventos/Novo evento/novo_evento.png`  

Estado exibido: formulÃ¡rio preenchido, aba **Evento** selecionada.

---

## 3. Estrutura da Tela (Componentes VisÃ­veis)

### 3.1 NavegaÃ§Ã£o
- Menu lateral:
  - Dashboard
  - Leads (serÃ¡ removido no nosso sistema)
  - Eventos
  - Cupons
- Logo do Banco do Brasil

### 3.2 Header Superior
- Ãcone menu sanduÃ­che
- Ãcone fullscreen
- Ãcone modo escuro
- Perfil do usuÃ¡rio (Admin)
- Breadcrumb: `Dashboard > Eventos`

### 3.3 Guias Superiores (Abas do Evento)

| Ordem | Nome da Aba              | Status no Novo Sistema                                      |
|------|--------------------------|-------------------------------------------------------------|
| 1    | **Evento**               | Aba atual / principal                                       |
| 2    | Formulário de Lead       | Mantida                                                     |
| 3    | Gamificação              | Mantida                                                     |
| 4    | Ativações                | Mantida                                                     |
| 5    | Questionário             | Mantida                                                     |
| 6    | Ingressos / Cotas        | Outra rota (gestão dedicada)                               |
| 7    | Investimentos            | Rota dedicada para edição por evento                       |
| 8    | Convidadores             | Outra rota                                                 |
| 9    | Convidados               | Outra rota                                                 |

### 3.4 Conteúdo da Aba “Evento”

#### Ordem dos campos (de cima para baixo)

| #  | Campo                     | Tipo                                   | Mapeamento no Banco                              | Observação / Novo |
|----|---------------------------|----------------------------------------|--------------------------------------------------|-------------------|
| 1  | Nome                      | Texto                                  | `evento.nome`                                    | Obrigatório       |
| 2  | Estado                    | Dropdown (UF)                          | `evento.estado`                                  | Obrigatório       |
| 3  | Local (Cidade)            | Dropdown                               | `evento.cidade`                                  | Obrigatório       |
| 4  | Diretoria                 | Dropdown                               | `evento.diretoria_id` → FK `diretoria`           | Obrigatório       |
| 5  | Agência                   | Dropdown                               | `evento.agencia_id` → FK `agencia`               | Obrigatório       |
| 6  | Divisão demandante        | Dropdown                               | `evento.divisao_demandante` (enum `divisao`)     | Obrigatório       |
| 7  | Tipo de Evento            | Dropdown                               | `evento.tipo_id` → FK `tipo_evento`              | Obrigatório       |
| 8  | Subtipo de Evento         | Dropdown dependente                    | `evento.subtipo_id` → FK `subtipo_evento`        | Obrigatório       |
| 9  | Territórios               | Multi-select com chips removíveis      | N:N → `evento_territorio`                        |                   |
| 10 | Tags livres               | Multi-select + criação dinâmica        | N:N → `evento_tag`                               |                   |
| 11 | Descrição                 | Textarea com contador (ex: 0/240)      | `evento.descricao`                               |                   |
| 12 | Data de início prevista   | Date picker                            | `evento.data_inicio_prevista`                    | Obrigatório       |
| 13 | Data final prevista       | Date picker                            | `evento.data_fim_prevista`                       | Obrigatório       |
| 14 | Encerrado                 | Switch booleano                        | Impacta `evento.status`                          |                   |
| 15 | Público projetado         | Número                                 | `evento.publico_projetado`                       |                   |
| 16 | Público realizado         | Número                                 | `evento.publico_realizado`                       |                   |

#### Campos da tabela `evento` que **não aparecem** nesta aba (tratados em outras seções)

- `data_inicio_realizada`
- `data_fim_realizada`
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

-- RelaÃ§Ãµes N:N
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

- AlteraÃ§Ã£o de qualquer campo â†’ atualiza estado interno (auto-save ao trocar aba ou clicar em â€œPrÃ³ximoâ€)
- **BotÃ£o â€œPrÃ³ximoâ€**:
  - Valida campos obrigatÃ³rios da aba Evento
  - Executa auto-save
  - Navega para aba â€œFormulÃ¡rio de Leadâ€
- **ValidaÃ§Ãµes**:
  - Data final prevista â‰¥ data inÃ­cio prevista
  - Campos obrigatÃ³rios destacados em vermelho se vazios
- **TerritÃ³rios e Tags** â†’ chips removÃ­veis; criaÃ§Ã£o/atualizaÃ§Ã£o automÃ¡tica nas tabelas de relaÃ§Ã£o

## 5. Regras de NegÃ³cio Principais

| Regra                              | Detalhe                                                                 |
|------------------------------------|-------------------------------------------------------------------------|
| Diretoria                          | ObrigatÃ³ria; usada tambÃ©m para lÃ³gica de cotas de ingressos             |
| Subtipo de Evento                  | Deve pertencer ao Tipo selecionado (trigger/validaÃ§Ã£o no backend)       |
| Tags livres                        | CriaÃ§Ã£o dinÃ¢mica + autocomplete                                        |
| Switch â€œEncerradoâ€                 | SugestÃ£o: true â†’ status = 'realizado' (a confirmar validaÃ§Ã£o)           |
| Campos de resultado (pÃºblico, datas realizadas, concorrÃªncia) | EdiÃ§Ã£o em aba/seÃ§Ã£o especÃ­fica de â€œResultadosâ€ (a definir)              |

## 6. DiferenÃ§as â€“ Sistema Original Ã— Nova VersÃ£o

| Item                     | Sistema Original                    | Nova VersÃ£o                                      |
|--------------------------|-------------------------------------|--------------------------------------------------|
| Diretoria                | NÃ£o existe                          | **Novo campo obrigatÃ³rio**                       |
| Subtipo de Evento        | NÃ£o explÃ­cito                       | Campo explÃ­cito e obrigatÃ³rio                    |
| Tags livres              | NÃ£o existe                          | **Novo** multi-select com criaÃ§Ã£o dinÃ¢mica       |
| Aba GamificaÃ§Ã£o          | Existe                              | Mantida                                          |
| Aba Ingressos / Cotas    | NÃ£o existe                          | **Nova** para gestÃ£o de ingressos                |
| TerritÃ³rios              | Multi-select simples                | Mesma UI, mas com modelagem explÃ­cita no banco   |

## 7. PendÃªncias / DÃºvidas

- Onde editar campos de resultado (datas realizadas, pÃºblico, concorrÃªncia)?
- Regra final do switch â€œEncerradoâ€ (altera status diretamente? exige datas realizadas?)
- EstratÃ©gia de salvamento: apenas â€œPrÃ³ximoâ€ com auto-save ou botÃ£o â€œSalvarâ€ global?

## 8. Backlog da Tela (Requisitos)

### Backend
- `POST /eventos`, `GET /eventos/:id`, `PUT /eventos/:id`
- ValidaÃ§Ãµes de obrigatÃ³rios, datas e compatibilidade tipo/subtipo
- Endpoints auxiliares para listas (estados, cidades, diretorias, tipos, subtipos, territÃ³rios, tags)
- CriaÃ§Ã£o dinÃ¢mica de tags

### Frontend
- Componente `<EventoForm />` com abas (Material Design 3)
- Componentes especÃ­ficos para cada campo
- ValidaÃ§Ã£o + feedback visual
- Auto-save ao trocar aba ou clicar â€œPrÃ³ximoâ€
- Mapeamento correto para payload da API (incluindo arrays de `territorios_ids` e `tags_ids`)

Pronto para ser colocado diretamente no Notion, GitHub ou documento Markdown!
```
