# EPIC-F1-05 — QR Code e Acesso via Promotor
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** BB-LANDING-PAGES-DINAMICAS | **fase:** F1 | **status:** 🔲

---
## 1. Resumo do Épico
Garantir que cada ativação tenha QR code gerado e URL alternativa para participantes que
não conseguem ler QR code, permitindo que o promotor digite/compartilhe o link.

---

## 2. Contexto Arquitetural
- A landing está vinculada à **Ativação** (ponto de captação no evento)
- Cada ativação deve ter QR code apontando para sua URL de landing
- Alternativa para acessibilidade: promotor digita/compartilha URL para o participante
- O sistema NPBB já possui `Evento.qr_code_url`; Ativação precisa de campos próprios

---

## 3. Riscos e Armadilhas
- QR code gerado com URL incorreta ou expirada
- URL alternativa muito longa para digitação manual
- Falta de sincronização entre QR e landing quando URL base muda

---

## 4. Definition of Done do Épico
- [ ] Serviço de geração de QR code gera imagem a partir da URL da landing da ativação
- [ ] Ativação possui `qr_code_url` e `url_promotor` preenchidos
- [ ] Backoffice exibe QR code e URL alternativa para cópia/compartilhamento
- [ ] Documentação operacional orienta promotor sobre uso da URL alternativa

---

## Issues

### LPD-F1-05-001 — Implementar serviço de geração de QR code
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** LPD-F1-01-004

**Descrição:**
Criar serviço que gera imagem QR code a partir da URL da landing da ativação
e persiste ou retorna a URL da imagem gerada.

**Critérios de Aceitação:**
- [ ] Serviço recebe URL da landing e retorna imagem QR (PNG/SVG) ou URL de armazenamento
- [ ] QR code é legível por leitores padrão e aponta para a URL correta
- [ ] Tamanho e margem adequados para impressão em materiais de ativação

**Tarefas:**
- [ ] T1: Integrar biblioteca de geração de QR (ex: qrcode, segno)
- [ ] T2: Definir estratégia de armazenamento (URL externa, S3, ou base64)
- [ ] T3: Implementar endpoint ou job que gera e atualiza `ativacao.qr_code_url`
- [ ] T4: Cobrir com testes unitários

**Notas técnicas:**
Priorizar armazenamento que permita URL pública estável; evitar regeneração desnecessária.

---

### LPD-F1-05-002 — Expor QR code e URL alternativa no backoffice
**tipo:** feature | **sp:** 2 | **prioridade:** alta | **status:** 🔲
**depende de:** LPD-F1-05-001

**Descrição:**
No backoffice, na tela de ativação (ou evento/ativações), exibir QR code gerado e
URL alternativa para o promotor copiar ou compartilhar com participantes.

**Critérios de Aceitação:**
- [ ] Operador visualiza QR code da ativação
- [ ] Operador visualiza `url_promotor` (URL curta ou landing completa) com botão de copiar
- [ ] Instrução clara: "Para quem não consegue ler QR code, o promotor pode digitar/compartilhar esta URL"

**Tarefas:**
- [ ] T1: Adicionar bloco de QR e URL alternativa na UI de ativação
- [ ] T2: Botão de copiar para área de transferência
- [ ] T3: Documentar fluxo no guia operacional

---

### LPD-F1-05-003 — Definir e implementar URL alternativa (acesso via promotor)
**tipo:** feature | **sp:** 2 | **prioridade:** média | **status:** 🔲
**depende de:** LPD-F1-01-004

**Descrição:**
Garantir que exista uma URL alternativa curta ou fácil de comunicar para quem não
consegue ler QR code. O promotor pode digitar no celular do participante ou enviar
por mensagem.

**Critérios de Aceitação:**
- [ ] `url_promotor` é preenchida para cada ativação (pode ser igual à landing_url inicialmente)
- [ ] Alternativa: rota `/landing-sem-qr/ativacoes/{id}` ou short link que redireciona
- [ ] URL é curta o suficiente para digitação verbal ou envio rápido

**Tarefas:**
- [ ] T1: Definir formato de `url_promotor` (landing_url, short link ou rota dedicada)
- [ ] T2: Implementar geração ou mapeamento da URL
- [ ] T3: Validar que a URL leva à mesma landing da ativação

**Notas técnicas:**
Se short link não for viável na F1, usar a própria `landing_url` e documentar que
o promotor pode digitar ou enviar o link. O importante é que a alternativa exista e
 seja explícita.

---

## 5. Notas de Implementação Globais
- O QR code e a URL alternativa devem apontar para a mesma landing da ativação
- Acessibilidade: garantir que não haja exclusão de quem não consegue ler QR code
