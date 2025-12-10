```markdown
# Página de Detalhes do Evento

## 1. Nome da Tela
**Detalhes do Evento**  
Tela central que reúne **todas** as informações e módulos relacionados a um único evento.

---

## 2. Referência Visual
Ainda sem print do novo sistema.  
Base conceitual: tela “Visualizar Evento” do sistema original, porém totalmente reorganizada em abas modernas.

---

## 3. Estrutura da Tela

### 3.1 Navegação
- Menu lateral padrão
- Breadcrumb: `Dashboard > Eventos > Detalhes do Evento`

### 3.2 Header Superior
- Título grande: **Nome do Evento**
- Botões principais (direita):
  - **Editar Evento**
  - **Excluir Evento** (com validação)
  - **Exportar Tudo** (CSV – opcional no MVP)
  - **Voltar**

### 3.3 Abas (Tabs)

| Ordem | Nome da Aba                 | Status no Sistema                              |
|-------|-----------------------------|-----------------------------------------------|
| 1     | Informações do Evento       | Principal – sempre visível                    |
| 2     | Formulário de Lead          | Mantida (integração Salesforce)               |
| 3     | Gamificação                 | Mantida                                       |
| 4     | **Ingressos / Cotas**       | **Nova** – gestão de ingressos por diretoria |
| 5     | Ativações                   | Mantida e aprimorada                          |
| 6     | Investimentos               | Mantida                                       |
| 7     | Convidadores                | Nova                                          |
| 8     | Convidados                  | Nova – lista completa                         |
| 9     | Questionário                | Em avaliação                                  |
| 10    | Logs / Histórico            | Futuro (fase 2)                               |

---

## 4. Conteúdo Detalhado das Abas

### 4.1 Informações do Evento
Exibição completa (somente leitura + ações rápidas)

| Campo                      | Exibição                                  |
|--------------------------------|-------------------------------------------|
| Nome                           | Título grande                             |
| Diretoria                      | Destaque                                  |
| Divisão demandante             |                                           |
| Tipo / Subtipo de Evento       |                                           |
| Estado / Cidade                |                                           |
| Datas previstas                |                                           |
| Datas realizadas               | (se preenchidas)                          |
| Público projetado / realizado  |                                           |
| Concorrência                   | Sim / Não                                 |
| Status                         | Chip colorido                             |
| Thumbnail                      | Imagem ao lado                            |
| Territórios                    | Chips removíveis (visualização)           |
| Tags livres                    | Chips removíveis (visualização)           |

Ações rápidas:
- **Editar Evento** | **Mudar Status** | **+ Território / Tag** (opcional)

### 4.2 Formulário de Lead
- Configuração do formulário Salesforce
- `salesforce_form_id`
- Botão **Testar Formulário**
- Lista de leads capturados (se houver)
- Exportar CSV de leads

### 4.3 Ingressos / Cotas (Nova Aba Principal)
Cards por Diretoria

| Diretoria      | Cotas Disponíveis | Usadas | % Consumido | Ações                              |
|----------------|-------------------|--------|-------------|------------------------------------|
| DIR-SP         | 150               | 87     | 58%         | Atribuir • Ver Convidados          |
| DIR-RJ         | 80                | 80     | 100%        | Ver Convidados                     |

Ações gerais:
- Definir / ajustar cotas
- Exportar CSV de todos os convidados do evento

### 4.4 Ativações
Tabela com:
- Nome | Descrição | Valor | Leads | Status
Ações por linha: Visualizar • Editar • Excluir  
Botão: **+ Nova Ativação**

### 4.5 Investimentos
Tabela com:
- Tipo | Descrição | Valor | Data
Totais por tipo e total geral

### 4.6 Convidadores
Lista de funcionários BB que emitiram convites

| Nome         | Diretoria | CPF          | Convites Emitidos | Ação                     |
|--------------|-----------|--------------|-------------------|--------------------------|
| João Silva   | DIR-MG    | ***.123.456-** | 23                | Ver Convidados do Convidado |

### 4.7 Convidados
Lista completa de todos os convidados do evento

| Nome           | CPF            | Email            | Telefone       | Diretoria | Func. BB | Status Convite | Ações                     |
|----------------|----------------|------------------|----------------|-----------|----------|----------------|---------------------------|
| Maria Oliveira | ***.789.012-** | maria@...        | (11) 98765-... | DIR-SP    | Não      | Enviado        | Remover • Reenviar (futuro) |

Ações gerais: Busca | Exportar CSV

### 4.8 Questionário (em avaliação)
- Edição de perguntas
- Visualização de respostas
- Exportação de resultados

---

## 5. Regras de Negócio Principais

| Regra                                           | Detalhe                                                                 |
|-------------------------------------------------|-------------------------------------------------------------------------|
| Exclusão do evento                              | Só permitida se **nenhum** dos seguintes vínculos existir:<br>• Ativações<br>• Investimentos<br>• Cotas/Convidados<br>• Convites emitidos |
| Consumo de cotas                                | Remover convidado → devolve 1 ingresso à diretoria                      |
| Territórios & Tags                              | Exibidos como chips (mesmo comportamento do formulário)                 |
| Todas as abas trabalham com o mesmo `evento.id` | Carregamento sob demanda (lazy loading) recomendado                     |

---

## 6. Diferenças – Sistema Original × Nova Versão

| Funcionalidade               | Sistema Original               | Nova Versão (Nosso Sistema)                                 |
|------------------------------|--------------------------------|-------------------------------------------------------------|
| Módulos exibidos             | Evento + Ativações + Leads + Questionário | + Ingressos/Cotas + Convidadores + Convidados + Investimentos |
| Diretoria                    | Não existia                    | Obrigatória e sempre visível                                |
| Territórios / Tags           | Não existiam                   | Exibidos como chips                                         |
| QR Code                      | Usado para check-in            | Sem função operacional                                      |
| Exclusão                     | Livre                          | Bloqueada com dependências                                  |
| Estrutura                    | Telas separadas                | Tudo centralizado em abas                                   |

---

## 7. Pendências / Dúvidas

- Layout definitivo de cada aba (precisa de protótipo no Figma)
- A aba Questionário será mantida no MVP?
- A aba Formulário de Lead será fiel ao sistema antigo ou simplificada?
- Exportação geral (CSV de tudo) entra no MVP?

---

## 8. Backlog da Tela (Requisitos)

### Backend
- `GET /eventos/:id/completo` → retorna todas as relações em uma chamada (ou endpoints separados)
- Endpoints dedicados por aba:
  - `/ativacoes?evento_id=`
  - `/investimentos?evento_id=`
  - `/cotas?evento_id=`
  - `/convidados?evento_id=`
  - `/convidadores?evento_id=`
- Validação rigorosa no `DELETE /eventos/:id`

### Frontend
- Página `<EventoDetalhes />`
- Componente `<TabsEvento />` com lazy loading
- Componentes por aba:
  - `<InfoEvento />`
  - `<CotasEvento />`
  - `<AtivacoesEvento />`
  - `<InvestimentosEvento />`
  - `<ConvidadoresEvento />`
  - `<ConvidadosEvento />`
- Chips reutilizáveis para territórios e tags
- Botões de ação no header com permissões
- Feedback claro quando exclusão for bloqueada (mostrar quais vínculos impedem)

