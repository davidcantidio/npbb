ANÁLISE DO CONTEXTO
─────────────────────────────────────────
Claro e preenchível diretamente:
- O projeto roda localmente e os QR codes hoje apontam para endereço local
- O domínio de produção futuro é app.npbb.com.br
- A demanda é antecipar a geração correta do QR code com base no ambiente de destino
- A superfície afetada é o módulo de geração de QR codes dentro da Plataforma NPBB

Inferível como hipótese:
- intake_kind: `problem` → hipótese: trata-se de um problema de configuração
  de base URL, não de nova funcionalidade
- source_mode: `original` → hipótese: demanda nova, não derivada de auditoria
- O QR code usa uma URL base hardcoded ou sem suporte a variável de ambiente
  → hipótese: a correção envolve introduzir uma env var (ex: NEXT_PUBLIC_BASE_URL
  ou equivalente) consumida no momento da geração
- delivery_surface: `fullstack-module` → hipótese: há lógica de geração tanto
  no backend (persistência do link) quanto no frontend (renderização do QR)
- change_type: `correcao-estrutural` → hipótese: a mudança é pequena mas toca
  em um ponto que afeta todos os QR codes gerados na plataforma

Ausente — preciso que o PM responda:
1. O QR code é gerado no backend (o link é salvo no banco?) ou apenas no
   frontend em tempo de renderização? Ou os dois?
2. Hoje a URL base está hardcoded, vem de uma env var já existente, ou é
   inferida dinamicamente (ex: window.location)?
3. O escopo é só a URL do QR code, ou há outros lugares na plataforma onde
   a base URL aparece hardcoded e deveria ser tratada junto (ex: links em
   e-mails, webhooks, redirects)?
4. Existe algum requisito de suporte a múltiplos ambientes além de local e
   produção (ex: staging, homologação)?
5. Nome canônico do projeto para este intake — usar `NPBB` ou há um slug
   mais específico (ex: `NPBB-QRCODE`)?
─────────────────────────────────────────
→ Responda as perguntas acima para eu continuar.
→ "pular [N]" para deixar campo como nao_definido e avançar.