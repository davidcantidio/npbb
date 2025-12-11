# Página de Eventos (Listagem)

## 1. Nome da Tela
**Listagem de Eventos**

Tela principal que exibe todos os eventos cadastrados, com ações rápidas de visualizar, editar e excluir.

---

## 2. Referência Visual
Print do sistema original:  
`docs/tela-inicial/menu/Eventos/eventos.png`

---

## 3. Estrutura da Tela

### 3.1 Navegação
- Menu lateral:
  - Dashboard
  - Eventos (página atual)
  - Ativos 
  - Leads
  - Cupons
- Logo Banco do Brasil

### 3.2 Header Superior
- Título: **Eventos**
- Botão **+ Novo** (abre formulário de criação)
- Ícones: menu sanduíche | fullscreen | modo escuro | atualizar | perfil (Admin)
- Breadcrumb: `Dashboard > Eventos`

### 3.3 Tabela de Eventos

| # | Coluna               | Conteúdo                                                                 | Observação no Novo Sistema                                      |
|---|---------------------|--------------------------------------------------------------------------|-----------------------------------------------------------------|
| 1 | **ID**              | Numérico sequencial                                                      |                                                                  |
| 2 | **QRCode**          | QRCode do evento (atual)                                                 |                                                                  |
| 3 | **Nome do Evento**  | Clique abre tela de Detalhes                                             |                                                                  |
| 4 | **Período**         | Formato: `DD/MM/AAAA – DD/MM/AAAA`                                       |                                                                  |
| 5 | **Cidade / UF**     | Ex.: São Paulo / SP                                                      |                                                                  |
| 6 | **Diretoria**       | *Não exibida no front atual* (campo existe no modelo)                    |                                                                  |
| 7 | **Ações**           | Ícones: Visualizar | Editar | Excluir                                     |                                                                  |

---

## 4. Comportamento da Tela

| Ação                 | Comportamento                                                                                   |
|----------------------|-------------------------------------------------------------------------------------------------|
| **+ Novo**           | Abre Formulário de Evento (aba “Evento”)                                                        |
| **Visualizar**       | Abre tela de Detalhes do Evento (somente leitura) com todas as abas                             |
| **Editar**           | Abre Formulário de Evento com todas as abas preenchidas                                         |
| **Excluir**          | Modal de confirmação<br>Bloqueia exclusão se houver vínculos (ativação, investimento, cotas, convites) |
| **Atualizar** (ícone)| Recarrega a lista                                                                               |
| Filtros (barra topo) | Filtros por Evento, Estado, Local, Data; botão “Limpar filtros”                                  |
| Paginação            | Paginação numérica na base da tabela (1..N)                                                     |

---

## 5. Regras de Negócio

- Exibição do período: datas previstas no intervalo; (realizadas não aparecem na UI atual).
- Exclusão bloqueada enquanto existirem vínculos (ativação, investimento, cotas, convites).
- Ordenação padrão: mais recente primeiro (aparente pelo ID/período).

---

## 6. Chamadas de API observadas (Playwright)

- `POST /auth/login` (autenticação)
- `GET /auth/me` (perfil)
- `GET /evento` (listagem principal, paginada)
- `GET /evento/all/cidades` (dicionário de cidades)
- `GET /evento/all/estados` (dicionário de estados)
- Ações esperadas (não clicadas nesta captura): `GET /evento/{id}`, `PUT /evento/{id}`, `DELETE /evento/{id}`; criação via `POST /evento` (botão “Novo”).

---

## 7. Diferenças — Sistema Original × Nova Versão

| Item               | Sistema Original                 | Nova Versão (atual/front observado) |
|--------------------|----------------------------------|-------------------------------------|
| QR Code            | Usado para check-in de leads     | Exibido na grid                     |
| Coluna Diretoria   | Não existe                       | Campo no modelo; não exibido na grid atual |
| Territórios / Tags | Não exibidos                     | Não aparecem na grid atual          |
| Filtros            | Nenhum                           | Filtros por Evento, Estado, Local, Data + limpar |
| Paginação          | Não mapeada                      | Paginação numérica inferior         |
| Módulos vinculados | Apenas Leads                     | Eventos + Leads + Cupons (menu lateral) |

---

## 8. Pendências / Dúvidas (resolvidas: resposta = “sim”)

- Diretoria deve aparecer na grid ou apenas em filtros? **Sim** (grid e filtros).
- Exibir datas realizadas / indicador de evento concluído? **Sim**.
- Exportação CSV da listagem será necessária? **Sim**.
- Territórios/Tags na linha (chips) entram em fase 2? **Sim** (planejar para fase 2).

---

## 9. Backlog da Tela (Requisitos)

### Backend
- `GET /evento` (com filtros opcionais)
- `GET /evento/{id}`
- `POST /evento`
- `PUT /evento/{id}`
- `DELETE /evento/{id}` → validar dependências antes de excluir
- Dicionários: `GET /evento/all/cidades`, `GET /evento/all/estados`
- Exportação: endpoint CSV (a definir) para contemplar decisão “sim”.

### Frontend
- Página `<EventosList />`
- Componentes:
  - `<EventosTable />`
  - `<EventoRow />`
  - `<ButtonNovoEvento />`
  - Filtros (Evento, Estado, Local, Data) + limpar
- Funcionalidades:
  - Botão Novo → navega para formulário
  - Ações Visualizar / Editar / Excluir com modal
  - Exibição de QRCode e Diretoria; exibir datas realizadas/indicador de concluído
  - Territórios/Tags em chips na linha (fase 2)
  - Exportação CSV da listagem
  - Paginação numérica inferior
