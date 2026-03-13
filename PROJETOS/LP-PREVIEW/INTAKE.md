ANÁLISE DO CONTEXTO
─────────────────────────────────────────
Claro e preenchível diretamente:
- O preview da página de configuração de formulário de leads / landing page
  precisa mudar de layout horizontal para vertical
- O preview deve ficar posicionado à direita da tela
- A visualização deve ser mobile-first (simulando viewport de dispositivo móvel)

Inferível como hipótese:
- intake_kind: "refactor" → hipótese: mudança de comportamento visual em
  funcionalidade existente, sem alteração de dados ou contrato de API
- delivery_surface: "frontend-web" → hipótese: impacto restrito à camada de UI
- business_domain: "landing-pages" → hipótese: inclui também o módulo de leads
  se o componente de preview for compartilhado
- change_type: "refactor" → hipótese: nenhuma feature nova, apenas
  reorganização de layout do preview existente
- criticality: "baixa" → hipótese: não afeta fluxo de dados nem publicação

Ausente — preciso que o PM responda:
1. Qual o nome canônico do projeto? (ex: NPBB, AFLPD, outro)
2. A mudança cobre os dois contextos (configuração de formulário de leads
   E configuração de landing page) ou apenas um deles?
3. O que é "horizontal" hoje — o preview fica abaixo do formulário, ao lado
   esquerdo, ou em painel separado em linha?
4. O preview mobile-first deve simular um dispositivo específico
   (ex: frame de celular, largura fixa de 375px) ou apenas reformatar
   o conteúdo em proporção vertical sem frame visual?
5. Existe algum componente de preview já nomeado no codebase
   (ex: <LandingPreview />, <FormPreview />) que você queira referenciar
   como componente afetado?
─────────────────────────────────────────
→ Responda as perguntas acima para eu continuar.
→ "pular [N]" para deixar campo como nao_definido e avançar.
