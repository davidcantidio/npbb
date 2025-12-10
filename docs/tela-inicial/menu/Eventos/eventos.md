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
  - Ativos (substitui o antigo módulo Leads)
  - Cupons
- Logo Banco do Brasil

### 3.2 Header Superior
- Título: **Eventos**
- Botão **+ Novo** (abre formulário de criação)
- Ícones: menu sanduíche | fullscreen | modo escuro | atualizar | perfil (Admin)
- Breadcrumb: `Dashboard > Eventos`

### 3.3 Tabela de Eventos

| # | Coluna               | Conteúdo                                                                 | Observação no Novo Sistema                                      |
|---|---------------------------|------------------------------------------------------------------|
| 1 | **ID**                    | Numérico sequencial                                              |
| 2 | **Identificador Visual**  | Original: QR Code<br>**MVP:** opcional – pode ser:<br>• Thumbnail<br>• Código interno<br>• Removido completamente |
| 3 | **Nome do Evento**        | Clique abre tela de Detalhes                                     |
| 4 | **Período**               | Formato: `DD/MM/AAAA – DD/MM/AAAA`<br>Se houver datas realizadas → ícone de evento concluído |
| 5 | **Cidade / UF**           | Ex.: São Paulo / SP                                              |
| 6 | **Diretoria**             | **Novo** – campo obrigatório no cadastro                        |
| 7 | **Ações**                 | Ícones: Visualizar | Editar | Excluir                              |

---

## 4. Comportamento da Tela

| Ação                 | Comportamento                                                                                   |
|----------------------|-------------------------------------------------------------------------------------------------|
| **+ Novo**           | Abre Formulário de Evento (aba “Evento”)                                                        |
| **Visualizar**       | Abre tela de Detalhes do Evento (somente leitura) com todas as abas                            |
| **Editar**           | Abre Formulário de Evento com todas as abas preenchidas                                         |
| **Excluir**          | Modal de confirmação<br>Bloqueia exclusão se houver:<br>• Ativações<br>• Investimentos<br>• Cotas de ingressos<br>• Convites emitidos |
| **Atualizar** (ícone)| Recarrega a lista                                                                               |
| Busca textual        | Filtra por Nome, Cidade ou Diretoria (a definir escopo no MVP)                                  |
| Rolagem              | Infinita ou longa (sem paginação no MVP – padrão do sistema original)                           |

---

## 5. Regras de Negócio

- Exibição do período:
  - Prioridade: datas **previstas**
  - Se existirem datas **realizadas** → exibir ícone** de evento concluído
- Exclusão bloqueada enquanto existirem vínculos ativos
- Diretoria sempre visível na listagem (campo obrigatório no novo sistema)
- Ordenação padrão: mais recente primeiro (por `data_inicio_prevista` DESC)

---

## 6. Diferenças – Sistema Original × Nova Versão

| Item                        | Sistema Original                          | Nova Versão (MVP e futuras)                              |
|-----------------------------|-------------------------------------------|-----------------------------------------------------------|
| QR Code                     | Usado para check-in de leads              | Não funcional – opcional ou removido                      |
| Coluna Diretoria            | Não existe                                | **Obrigatória e exibida**                                 |
| Territórios / Tags          | Não exibidos                              | Podem ser exibidos como chips pequenos (fase 2)           |
| Filtros                     | Nenhum                                    | MVP: busca textual<br>Fase 2: Estado, Diretoria, Tipo, Período |
| Exclusão                    | Permite excluir livremente                | Bloqueada com dependências                                |
| Módulos vinculados          | Apenas Leads                              | Ativações, Investimentos, Cotas, Convites, Convidados     |

---

## 7. Pendências / Dúvidas

- Visual final do identificador (QR Code / thumbnail / ID / nenhum)?
- Filtros avançados entram no MVP ou só na fase 2?
- Exportação CSV da listagem será necessária no MVP?
- Exibir territórios/tags como chips na própria linha da tabela?

---

## 8. Backlog da Tela (Requisitos)

### Backend
- `GET /eventos` (com busca e filtros opcionais)
- `GET /eventos/:id`
- `DELETE /eventos/:id` → validar dependências antes de excluir
- Endpoint auxiliar para verificar se evento tem vínculos (usado no modal de exclusão)

### Frontend
- Página `<EventosList />`
- Componentes:
  - `<EventosTable />`
  - `<EventoRow />`
  - `<ButtonNovoEvento />`
  - `<SearchBar />` (busca textual)
- Funcionalidades:
  - Botão Novo → navega para formulário
  - Ações Visualizar / Editar / Excluir com modal
  - Exibição condicional de thumbnail ou QR Code
  - Indicador visual de evento realizado
  - Feedback de bloqueio de exclusão com motivo

