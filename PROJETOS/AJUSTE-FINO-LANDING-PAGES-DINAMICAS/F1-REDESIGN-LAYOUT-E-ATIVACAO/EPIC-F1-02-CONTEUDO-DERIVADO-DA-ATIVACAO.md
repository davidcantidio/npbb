# EPIC-F1-02 — Conteúdo Derivado da Ativação
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** AJUSTE-FINO-LANDING-PAGES-DINAMICAS | **fase:** F1 | **status:** 🔲

---
## 1. Resumo do Épico
Alimentar os elementos de texto da landing page (título do formulário, subtítulo de
contexto, callout de orientação e texto do CTA) com dados reais da ativação e do
evento, substituindo textos genéricos do template. Tornar o bloco "Sobre o evento"
condicional — visível apenas quando descrição disponível.

**Resultado de Negócio Mensurável:** Cada landing page exibe conteúdo contextualizado
à ativação específica (nome, descrição, orientação), aumentando a relevância percebida
pelo lead e a taxa de conversão do formulário.

## 2. Contexto Arquitetural
- Componente: `frontend/src/components/landing/LandingPageView.tsx`
- Dados disponíveis no payload: `data.ativacao` (tipo `LandingAtivacaoInfo`), `data.evento`, `data.template`
- Cadeia de fallback definida no PRD seção 3.2:
  - Título: `ativacao.nome` → `evento.nome`
  - Subtítulo: `ativacao.descricao` → `evento.descricao_curta`
  - Callout: `ativacao.mensagem_qrcode` (exibido somente se presente)
  - CTA: `evento.cta_personalizado` → `template.cta_text`
- Tipo `LandingAtivacaoInfo` deve ser definido/atualizado em `frontend/src/types/` ou `landing_public.ts`
- Tipo `LandingPageData` deve incluir campo `ativacao?: LandingAtivacaoInfo | null`

## 3. Riscos e Armadilhas
- Se `data.ativacao` for `null` ou `undefined` (landing sem ativação vinculada), todos os fallbacks devem funcionar sem erro
- `mensagem_qrcode` pode conter HTML ou caracteres especiais — renderizar como texto puro (sem `dangerouslySetInnerHTML`)
- Bloco "Sobre o evento" condicional: verificar que a remoção não causa colapso de layout
- Tipos TypeScript devem ser atualizados antes dos componentes para evitar erros de compilação

## 4. Definition of Done do Épico
- [ ] Tipo `LandingAtivacaoInfo` definido com campos `id`, `nome`, `descricao?`, `mensagem_qrcode?`
- [ ] Tipo `LandingPageData` inclui campo `ativacao?: LandingAtivacaoInfo | null`
- [ ] Título do formulário usa `data.ativacao?.nome ?? data.evento.nome` (não mais `template.cta_text`)
- [ ] Subtítulo usa `data.ativacao?.descricao ?? data.evento.descricao_curta`
- [ ] Callout `<Alert>` exibido acima dos campos quando `data.ativacao?.mensagem_qrcode` presente
- [ ] CTA resolve `data.evento.cta_personalizado ?? data.template.cta_text`
- [ ] Bloco "Sobre o evento" visível apenas quando descrição disponível
- [ ] Nenhum campo de `template` renderizado como texto na view pública
- [ ] Fallbacks funcionam corretamente quando `data.ativacao` é `null`

---
## Issues

### AFLPD-F1-02-001 — Definir tipos TypeScript para ativação na landing
**tipo:** feature | **sp:** 2 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Criar o tipo `LandingAtivacaoInfo` e estender `LandingPageData` com o campo
`ativacao` conforme especificação do PRD seção 6.1. Esses tipos são pré-requisito
para todas as alterações de componente neste épico.

**Plano TDD:**
- **Red:** Escrever teste de tipo que instancia `LandingPageData` com campo `ativacao` e verifica compilação TypeScript.
- **Green:** Adicionar tipos `LandingAtivacaoInfo` e campo `ativacao` em `LandingPageData` no arquivo de tipos da landing.
- **Refactor:** Consolidar tipos de landing em um único módulo se estiverem espalhados.

**Critérios de Aceitação:**
- Given o arquivo de tipos da landing, When compilado com `tsc --noEmit`, Then nenhum erro de tipo
- Given `LandingPageData` com `ativacao: null`, When usado em componente, Then TypeScript não reporta erro
- Given `LandingPageData` com `ativacao` preenchida, When acessando `ativacao.nome`, Then TypeScript resolve o tipo corretamente

**Tarefas:**
- [ ] T1: Localizar arquivo de tipos da landing (`landing_public.ts` ou equivalente)
- [ ] T2: Adicionar tipo `LandingAtivacaoInfo` com campos `id: number`, `nome: string`, `descricao?: string | null`, `mensagem_qrcode?: string | null`
- [ ] T3: Estender `LandingPageData` com campo `ativacao?: LandingAtivacaoInfo | null`
- [ ] T4: Verificar compilação TypeScript sem erros

**Notas técnicas:**
O campo `ativacao` é opcional e nullable para retrocompatibilidade com payloads
existentes que não possuem dados de ativação.

---
### AFLPD-F1-02-002 — Alimentar título, subtítulo, callout e CTA com dados da ativação
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** AFLPD-F1-02-001

**Descrição:**
Substituir os textos estáticos/genéricos do formulário e hero por dados derivados da
ativação e evento, seguindo a cadeia de fallback definida no PRD (seção 3.2). Adicionar
callout `<Alert severity="info">` com `mensagem_qrcode` acima dos campos quando presente.

**Plano TDD:**
- **Red:** Escrever teste que renderiza `LandingPageView` com `ativacao.nome = "Stand Skate"` e asserta que o título do formulário contém "Stand Skate".
- **Green:** Substituir título por `data.ativacao?.nome ?? data.evento.nome`, adicionar callout condicional, atualizar CTA.
- **Refactor:** Extrair lógica de resolução de fallback para função utilitária `resolveLandingContent(data)`.

**Critérios de Aceitação:**
- Given ativação com `nome = "Stand Principal"`, When landing renderizada, Then título do formulário é "Stand Principal"
- Given ativação sem `nome` (null), When landing renderizada, Then título usa `evento.nome` como fallback
- Given ativação com `mensagem_qrcode = "Escaneie para se cadastrar"`, When landing renderizada, Then alert com esse texto aparece acima dos campos do formulário
- Given ativação sem `mensagem_qrcode`, When landing renderizada, Then nenhum alert de orientação aparece
- Given evento com `cta_personalizado = "Cadastre-se agora"`, When landing renderizada, Then botão CTA exibe "Cadastre-se agora"

**Tarefas:**
- [ ] T1: Substituir título do formulário: `{data.ativacao?.nome ?? data.evento.nome}`
- [ ] T2: Substituir subtítulo/descrição: `{data.ativacao?.descricao ?? data.evento.descricao_curta}`
- [ ] T3: Adicionar callout condicional: `{data.ativacao?.mensagem_qrcode && <Alert severity="info">...}</Alert>}`
- [ ] T4: Atualizar CTA: `{data.evento.cta_personalizado ?? data.template.cta_text}`
- [ ] T5: Tornar bloco "Sobre o evento" condicional — visível apenas se descrição disponível
- [ ] T6: Testar com `ativacao` preenchida, com `ativacao: null` e com campos parciais

**Notas técnicas:**
O operador nullish coalescing (`??`) é preferido sobre `||` para evitar que strings
vazias `""` sejam tratadas como falsy. Para `mensagem_qrcode`, verificar explicitamente
presença e não-vazio antes de renderizar o `<Alert>`.

## 5. Notas de Implementação Globais
- A cadeia de fallback deve ser centralizada — considerar extrair para função `resolveLandingContent(data)`
- Testar com dados de ativação completos, parciais e ausentes (null)
- O callout de orientação deve usar `<Alert severity="info">` do MUI para consistência visual
- Nenhum campo de `template` deve aparecer como texto na view pública após estas alterações
