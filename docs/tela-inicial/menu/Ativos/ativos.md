# Listagem de Leads

## 1. Nome da Tela
**Listagem de Leads**  
Tela responsável por exibir, filtrar, buscar e gerenciar os leads cadastrados ou recebidos via formulários integrados.

---

## 2. Referência Visual
Print: `./print.png`  
(estado: listagem com dados; sem estados vazios, erro ou modal exibidos)

---

## 3. Estrutura da Tela (Componentes Visíveis)

### 3.1 Navegação
- Menu lateral com opções:
  - Dashboard
  - Leads (seção atual)
  - Eventos
  - Cupons
- Logo do Banco do Brasil no topo do menu.

### 3.2 Header Superior
- Ícones:
  - Menu sanduíche (expande/contrai menu lateral)
  - Fullscreen
  - Atualizar
  - Modo escuro
- Perfil do usuário:
  - Nome: BancoBrasil
  - Permissão: Admin
- Breadcrumb:
  - Dashboard > Leads

### 3.3 Filtros e Ações da Lista
- Barra superior da listagem:
  - Campo de busca: “Buscar por…”
  - Botão **Atualizar**
  - Botão **Filtrar**
  - Botão **Exportar**

### 3.4 Conteúdo Principal — Tabela
A tabela exibe colunas:

1. **Id**  
2. **Nome**


### O que é diferente no nosso prjeto
No lugar interagir com lead, vamos monitorar e cadastrar a distribuição de ativos, ou seja, ingressos para evento. de acordo com a modelagem do banco de dados que eu enviei. Teremos as colunas: Evento