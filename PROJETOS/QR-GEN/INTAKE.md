---
doc_id:          "INTAKE-QR-GEN.md"
version:         "0.1-draft"
status:          "draft"
intake_kind:     "problem"
source_mode:     "original"
origin_audit:    "nao_aplicavel"
project:         "QR-GEN"
owner:           "PM"
created_at:      "2026-03-13"
---

# INTAKE-QR-GEN — QR Codes Gerados com URL Base de Ambiente Local

---

## 1. Problema ou Oportunidade

Os QR codes gerados pela Plataforma NPBB apontam atualmente para o endereço
local de desenvolvimento em vez do domínio de produção `app.npbb.com.br`.
Isso torna todos os QR codes gerados no ambiente local inválidos para uso
em produção, exigindo nova geração após o deploy — e cria risco de QR codes
errados chegarem ao usuário final antes que a correção seja feita.

---

## 2. Sintoma Observado

QR codes gerados durante desenvolvimento local resolvem para endereço localhost
em vez de `app.npbb.com.br`, tornando-os inutilizáveis fora da máquina do
desenvolvedor.

---

## 3. Impacto Operacional

- QR codes distribuídos (impressos, enviados, publicados) antes do go-live
  precisarão ser regerados integralmente
- Se QR codes com URL local escaparem para produção, os usuários finais
  receberão links quebrados ao escanear
- O backend persiste os links no banco — registros com URL local exigirão
  correção manual ou migração de dados

---

## 4. Evidência Técnica

A URL base usada na geração do QR code é `app.npbb.com.br` (domínio de
produção já definido), mas a geração ocorre no ambiente local sem mecanismo
de resolução de ambiente. O link resultante é persistido no banco com o valor
incorreto.

[hipótese: a URL base está hardcoded no código ou ausente de variável de
ambiente, sendo resolvida a partir do contexto local no momento da geração]

---

## 5. Componentes Afetados

- Módulo de geração de QR codes (backend — persistência do link)
- Módulo de renderização de QR codes (frontend — exibição)
- Banco de dados (registros de QR code com URL persistida)

---

## 6. Público / Operador Principal

- **Operador interno:** PM/dev gerando QR codes durante desenvolvimento
- **Usuário final:** participante de evento que escaneia o QR code para
  acessar a landing page correspondente

---

## 7. Job to Be Done Dominante

Quando o operador gera um QR code na plataforma, ele precisa ter certeza de
que o link encapsulado aponta para o ambiente correto de destino — sem
intervenção manual após o deploy.

---

## 8. Fluxo Principal Esperado

1. Operador acessa a plataforma e solicita geração de QR code para uma
   landing page
2. O sistema resolve a URL base a partir da configuração de ambiente
   (variável de ambiente ou equivalente)
3. O link completo (`<base_url>/landing/<slug>`) é montado e persistido
   no banco
4. O QR code é renderizado no frontend a partir do link persistido
5. O QR code gerado aponta para `app.npbb.com.br` em produção e para
   `localhost` apenas em desenvolvimento local — sem hardcode

---

## 9. Objetivo de Negócio e Métricas de Sucesso

**Objetivo:** garantir que QR codes gerados sejam válidos no ambiente de
destino sem intervenção manual pós-deploy.

**Métricas:**
- Zero QR codes com URL de localhost persistidos no banco após a correção
- QR codes gerados em produção resolvem corretamente para `app.npbb.com.br`
- Nenhuma regera‍ção manual necessária após go-live

---

## 10. Restrições e Não-Objetivos

**Restrições:**
- A correção não pode quebrar o fluxo de desenvolvimento local
- Registros já persistidos com URL incorreta devem ser tratados (migração
  ou limpeza) — não podem ser ignorados silenciosamente

**Não-objetivos:**
- Suporte a ambientes de staging ou homologação (fora de escopo)
- Revisão de outros pontos da plataforma onde base URL aparece
  (confirmado pelo PM como fora de escopo)
- Redesign do módulo de QR code

---

## 11. Dependências e Integrações

- Configuração de variável de ambiente no ambiente de produção
  (`app.npbb.com.br`)
- Banco de dados (revisão/migração de registros com URL local já persistida)

---

## 12. Arquitetura e Superfícies Impactadas

- `delivery_surface`: `fullstack-module`
- `business_domain`: `landing-pages`
- `product_type`: `platform-capability`
- `change_type`: `correcao-estrutural`
- `criticality`: `alta`
- `data_sensitivity`: `interna`
- Impacto: lógica de resolução de URL base no backend (geração/persistência)
  e frontend (renderização); potencial script de migração para registros
  existentes no banco

---

## 13. Riscos Relevantes

- QR codes com URL local já persistidos no banco chegarem ao go-live sem
  correção → links quebrados em produção
- Ausência de variável de ambiente configurada no servidor de produção →
  falha silenciosa ou erro em runtime
- [hipótese] Se a URL base for resolvida no frontend via `window.location`,
  a correção no backend pode não ser suficiente — frontend também precisará
  ser ajustado

---

## 14. Riscos de Não Agir

- Go-live com QR codes inválidos distribuídos para usuários finais
- Necessidade de campanha de correção/comunicação após o lançamento
- Perda de confiança operacional no módulo de QR code

---

## 15. Lacunas Conhecidas

- Não confirmado se a URL base está hardcoded ou ausente de env var
  (marcado como hipótese na seção 4 e 13)
- Não levantado o volume de registros já persistidos com URL incorreta
  no banco — necessário antes de decidir estratégia de migração

---

## 16. Checklist de Prontidão para PRD

[x] Por que isso existe — problema de URL base sem resolução de ambiente
[x] Para quem existe — operador e usuário final de QR code
[x] O que entra e o que não entra — escopo confirmado e restrito
[x] Onde a mudança toca na arquitetura — fullstack-module + banco
[x] Como o sucesso será medido — métricas definidas
[x] Restrições e riscos incontornáveis — registros persistidos + env var
[ ] Evidência técnica confirmada — hipótese sobre hardcode vs env var
    ainda não verificada no código
[ ] Volume de registros incorretos no banco — não levantado
```

---
```
RASCUNHO CONCLUÍDO
─────────────────────────────────────────
Campos preenchidos:    15/16
Hipóteses declaradas:  2
Campos nao_definido:   0
Prontidão para PRD:    bloqueado parcialmente — 2 itens [ ] no checklist,
                       mas ambos são verificáveis em 5 minutos no código/banco
                       antes de abrir o PRD; intake pode ser aprovado agora
                       com hipóteses declaradas se o PM aceitar esse risco
─────────────────────────────────────────
→ "aprovar" para gerar o arquivo
→ "ajustar [instrução]" para revisar antes de gravar
→ "bloquear" para registrar o intake como incompleto e parar aqui