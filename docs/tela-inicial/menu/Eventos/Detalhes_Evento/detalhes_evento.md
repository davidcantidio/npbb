```markdown
# PÃ¡gina de Detalhes do Evento

## 1. Nome da Tela
**Detalhes do Evento**  
Tela central que reÃºne **todas** as informaÃ§Ãµes e mÃ³dulos relacionados a um Ãºnico evento e permite editar suas informações.

---

## 2. Referência Visual
Print atual capturado com Playwright (`playwright-event-detail.png`): edição do evento com abas: Evento, Formulário de Lead, Gamificação, Ativações, Questionário.

---

## 3. Estrutura da Tela

### 3.1 Navegação
- Menu lateral padrão
- Breadcrumb: `Dashboard > Eventos > Detalhes do Evento`

### 3.2 Header Superior
- Título grande: **Nome do Evento**
- Botões principais (direita):
  - **Editar Evento** (estado atual da UI)
  - **Excluir Evento** (com validação)
  - **Exportar Tudo** (CSV – opcional no MVP)
  - **Voltar**

### 3.3 Abas (Tabs)

| Ordem | Nome da Aba            | Status no Sistema                              |
|-------|------------------------|-----------------------------------------------|
| 1     | Evento                 | Principal – sempre visível                    |
| 2     | Formulário de Lead     | Mantida                                       |
| 3     | Gamificação            | Mantida                                       |
| 4     | Ativações              | Mantida e aprimorada                          |
| 5     | Questionário           | Mantida                                       |
| 6     | Ingressos / Cotas      | Não visível na captura (pode ser outra rota)  |
| 7     | Investimentos          | Não visível na captura (pode ser outra rota)  | 
| 8     | Convidadores           | Não visível na captura (pode ser outra rota)  |
| 9     | Convidados             | Não visível na captura (pode ser outra rota)  |
| 10    | Logs / Histórico       | Futuro (fase 2)                               |

---

## 4. ConteÃºdo Detalhado das Abas

### 4.1 Evento (aba Evento)
- Formulário editável com os campos:
  - Nome
  - Estado (dropdown)
  - Local (cidade)
  - Divisão demandante (dropdown)
  - Tipo de Evento (dropdown)
  - Territórios (multi-select com chips)
  - Descrição (textarea com contador 0/240)
  - Datas: início/final
  - Encerrado (checkbox)
- Navegação: botão **Próximo** (aba seguinte)

### 4.2 Formulário de Lead
- Campos: nome e descrição do formulário, seleção de tema (Surf, Padrão, BB Seguros), pré-visualização do formulário.
- Configuração de campos (checkbox): CPF, Nome, Sobrenome, Telefone, E-mail, Data de Nascimento, Endereço, Interesses, Gênero, Área de atuação.
- Botões: **Salvar e Visualizar**, **Salvar**.
- Endereços da aplicação seguem aparecendo no rodapé (landing, promotor, questionário, API).

### 4.3 Gamificação
- Form para adicionar gamificação: Nome, Descrição, Título do feedback de sucesso, Descrição do feedback de sucesso.
- Lista “Gamificações adicionadas” (tabela vazia na captura).
- Botão: **Adicionar gamificação**.
- Rodapé mantém os endereços da aplicação.

### 4.4 Ativações
- Form para adicionar ativação: Nome da ativação, Mensagem do QR Code, Mensagem (240 caracteres).
- Tipo de gamificação: dropdown (Nenhuma).
- Flags: Redirecionamento para tela de pesquisa, Check-in único por ativação, Termo de uso, Gerar Cupom.
- Botão: **Adicionar ativação**.
- Rodapé mantém os endereços da aplicação.

### 4.5 Questionário
- Aba presente mas não carregou conteúdo visível na captura (spinner “Carregando…”); requer exploração futura para mapear campos.

### 4.6 Endereços da aplicação (seção extra no rodapé)
- Endereço da landing
- Endereço para promotor
- Endereço do questionário
- Endereço da API (com link “Acessar documentação”)

---

## 5. Regras de Negócio Principais

| Regra                                           | Detalhe                                                                 |
|-------------------------------------------------|-------------------------------------------------------------------------|
| Exclusão do evento                              | Só permitida se **nenhum** dos seguintes vínculos existir:<br>• Ativações<br>• Investimentos<br>• Cotas/Convidados<br>• Convites emitidos |
| Consumo de cotas                                | Remover convidado → devolve 1 ingresso à diretoria                      |
| Territórios & Tags                              | Exibidos como chips (mesmo comportamento do formulário)                 |
| Todas as abas trabalham com o mesmo `evento.id` | Carregamento sob demanda (lazy loading) recomendado                     |

---

## 6. Chamadas de API observadas (Playwright)

- `POST /auth/login`
- `GET /auth/me`
- `GET /evento/185` (detalhe do evento teste anterior)
- `GET /evento/194` (detalhe do evento de teste solicitado)
- Dicionários auxiliares carregados na tela:
  - `GET /evento/all/cidades`
  - `GET /evento/all/estados`
  - `GET /evento/all/territorios`
  - `GET /evento/all/divisoes-demandantes`
  - `GET /evento/all/tipos-evento`
- Abas/relacionados:
  - `GET /formulario/cadastro/participante/185`
  - `GET /gameficacao/185`
  - `GET /acao?idEvento=185&pagina=1&size=1000`
- Dashboards (prováveis dependências de cabeçalho):
  - `GET /dash/leads/periodo`
  - `GET /dash/leads/estado`
  - `GET /dash/leads/cidade`
  - `GET /dash/leads?size=5`
  - `GET /dash/porcentagem/leads/evento`
  - `GET /dash/faixa/etaria`

---

## 7. Pendências / Dúvidas

- Confirmar presença/uso das abas Ingressos/Cotas, Investimentos, Convidadores, Convidados no front atual (não visíveis na captura desta rota).
- Layout definitivo de cada aba (precisa de protótipo no Figma).
- Exportação geral (CSV de tudo) entra no MVP?

---

## 8. Backlog da Tela (Requisitos)

### Backend
- `GET /evento/{id}` (detalhe)
- Endpoints por aba (já conhecidos): ativações, investimentos, cotas, convidados, convidadores, questionário, formulários de lead.
- Dicionários: cidades, estados, territórios, divisões demandantes, tipos de evento.

### Frontend
- Páginas/abas:
  - `<EventoDetalhes />` com tabs (Evento, Formulário de Lead, Gamificação, Ativações, Questionário, e futuras)
  - `<InfoEvento />`
  - Links/endereços (landing, promotor, questionário, API) com botões “Visualizar”
- Navegação entre abas com lazy loading
- Botões de ação: Editar, Excluir, Exportar Tudo (CSV), Voltar

---

## 7. PendÃªncias / DÃºvidas

- Layout definitivo de cada aba (precisa de protÃ³tipo no Figma)
- A aba QuestionÃ¡rio serÃ¡ mantida no MVP?
- A aba FormulÃ¡rio de Lead serÃ¡ fiel ao sistema antigo ou simplificada?
- ExportaÃ§Ã£o geral (CSV de tudo) entra no MVP?

---

## 8. Backlog da Tela (Requisitos)

### Backend
- `GET /eventos/:id/completo` â†’ retorna todas as relaÃ§Ãµes em uma chamada (ou endpoints separados)
- Endpoints dedicados por aba:
  - `/ativacoes?evento_id=`
  - `/investimentos?evento_id=`
  - `/cotas?evento_id=`
  - `/convidados?evento_id=`
  - `/convidadores?evento_id=`
- ValidaÃ§Ã£o rigorosa no `DELETE /eventos/:id`

### Frontend
- PÃ¡gina `<EventoDetalhes />`
- Componente `<TabsEvento />` com lazy loading
- Componentes por aba:
  - `<InfoEvento />`
  - `<CotasEvento />`
  - `<AtivacoesEvento />`
  - `<InvestimentosEvento />`
  - `<ConvidadoresEvento />`
  - `<ConvidadosEvento />`
- Chips reutilizÃ¡veis para territÃ³rios e tags
- BotÃµes de aÃ§Ã£o no header com permissÃµes
- Feedback claro quando exclusÃ£o for bloqueada (mostrar quais vÃ­nculos impedem)

