# Pagina de Ativos (Cotas de ingressos)

## 1. Nome da Tela
**Ativos (Cotas de ingressos cortesia)**

Tela para exibir, acompanhar e ajustar a distribuicao de ingressos (cotas) por Diretoria e Evento.

Status no novo sistema:
- Frontend: nao implementado.
- Backend: nao implementado.

---

## 2. Referencia Visual
Print do sistema original:
`docs/tela-inicial/menu/Ativos/ativos.png`

---

## 3. Estrutura (proposta)
### 3.1 Lista de cards
Cada card representa uma combinacao **evento + diretoria**, exibindo:
- Evento
- Diretoria
- Disponibilidade (ex.: `23 / 45`)
- Indicador visual (barra de progresso ou percentual)
- Botao **Atribuir ingressos**

### 3.2 Filtros (recomendado)
- Evento
- Diretoria
- Data do evento

---

## 4. Comportamento (observado/esperado)
- Ao carregar, lista todos os cards (um por evento + diretoria com cota cadastrada).
- Botao **Atualizar** recarrega os dados.
- **Atribuir ingressos** abre um modal para atualizar a quantidade total disponivel.
- Ao salvar, o card reflete imediatamente o novo total.

---

## 5. Regras de negocio (confirmadas)
- Cada diretoria possui uma cota (quantidade total) por evento.
- **Ingressos usados = convites emitidos** (cada convite consome 1 ingresso da cota).
- Nao permitir:
  - atribuir valor negativo
  - definir total menor que o numero ja usado
- Exportacao CSV: pagina deve permitir exportar cotas/consumo.
- Cada card deve permitir acessar a lista de convidados daquela cota; remover convidado devolve 1 ingresso.

---

## 6. Endpoints (proposta / a confirmar)
- `GET /ativos` -> lista evento, diretoria, usados, disponiveis
- `POST /ativos/{evento_id}/{diretoria_id}/atribuir` -> ajusta quantidade total
- `GET /ativos/{evento_id}/{diretoria_id}` -> detalhes/historico (opcional)

---

## 7. Backlog (status)
### Backend
- [ ] Modelos/tabelas de cotas/convites (se ainda nao existirem)
- [ ] Endpoints de leitura/ajuste
- [ ] Validacoes (nao reduzir abaixo do usado)

### Frontend
- [ ] Pagina `<AtivosPage />` com grid de cards
- [ ] Modal de atribuicao de ingressos
- [ ] Filtros + exportacao CSV
