# Manual NPBB

Este manual junta o essencial do projeto em um lugar só.

Objetivo: ajudar alguém a ligar o sistema, usar as funções principais e destravar problemas comuns sem precisar caçar informação em vários arquivos.

Se você tem pouco tempo ou se distrai com facilidade, siga nesta ordem:

1. Leia "Mapa rápido".
2. Faça "Primeiro uso no Windows".
3. Use "Rotinas do dia a dia".
4. Se algo falhar, vá em "Problemas comuns".

## Mapa rápido

Pense no NPBB assim:

- `backend` é a parte que faz o trabalho por trás.
- `frontend` é a parte que você vê na tela.
- `Supabase` é o banco online, onde os dados ficam salvos.
- `docs` é a pasta com explicações mais detalhadas.

Em linguagem simples:

- Se a tela não abre, o problema costuma estar no `frontend`.
- Se a tela abre, mas nada carrega, o problema costuma estar no `backend` ou no banco.
- Se um arquivo não importa, o problema costuma estar no arquivo ou no mapeamento de colunas.

## O que você precisa antes de começar

Você precisa de:

- Python 3.12
- Node.js 18 ou superior
- acesso ao projeto Supabase do NPBB
- o repositório `C:\Users\NPBB\npbb`

Se estiver no Windows, este é o caminho mais importante:

- backend: `C:\Users\NPBB\npbb\backend`
- frontend: `C:\Users\NPBB\npbb\frontend`

## Primeiro uso no Windows

Esta é a versão mais simples para ligar o projeto localmente.

### Passo 1. Preparar o backend

Abra o PowerShell e rode:

```powershell
cd C:\Users\NPBB\npbb\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Agora abra o arquivo `backend\.env` e preencha os valores do banco.

Exemplo fictício:

```env
DATABASE_URL="postgresql+psycopg2://postgres.projeto-exemplo:senha123@servidor-exemplo:6543/postgres"
DIRECT_URL="postgresql+psycopg2://postgres.projeto-exemplo:senha123@servidor-direto:5432/postgres"
SECRET_KEY="troque-isto"
FRONTEND_ORIGIN="http://localhost:5173"
```

O que isso quer dizer, sem complicar:

- `DATABASE_URL`: conexão que o sistema usa no dia a dia.
- `DIRECT_URL`: conexão direta, usada mais para manutenção.
- `SECRET_KEY`: chave interna do sistema.
- `FRONTEND_ORIGIN`: endereço da tela local.

### Passo 2. Subir o backend

Ainda no PowerShell:

```powershell
cd C:\Users\NPBB\npbb
.\scripts\dev_backend.ps1
```

Se esse script não existir no seu clone ou se o PowerShell bloquear a execução, use este plano B:

```powershell
cd C:\Users\NPBB\npbb
$env:PYTHONPATH = "$(Get-Location);$(Get-Location)\backend"
backend\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --app-dir backend
```

O que você deve esperar:

- uma API rodando em `http://localhost:8000`
- a rota `http://localhost:8000/health` deve responder com algo como `{"status":"ok"}`

Se isso acontecer, o motor do sistema está no ar.

Se o PowerShell disser que scripts `.ps1` estão bloqueados, rode uma vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### Passo 3. Preparar o frontend

Abra outro PowerShell:

```powershell
cd C:\Users\NPBB\npbb\frontend
npm install
Copy-Item .env.example .env
npm run dev
```

O que você deve esperar:

- a tela abrir em `http://localhost:5173`

Se a tela abrir, o sistema local está pronto para uso.

## Exemplo fictício: ligando tudo do zero

Imagine este caso:

- Pessoa: Ana
- Evento: `Feira de Inverno 2026`
- Objetivo: subir o sistema para importar uma lista de leads

O caminho da Ana seria:

1. Abrir um PowerShell para o backend.
2. Rodar `.\scripts\dev_backend.ps1`.
3. Abrir outro PowerShell para o frontend.
4. Rodar `npm run dev`.
5. Entrar em `http://localhost:5173`.
6. Fazer login.
7. Ir para a tela de leads.
8. Importar a planilha da campanha.

Se a tela abriu e os dados apareceram, ela terminou o básico com sucesso.

## Rotinas do dia a dia

Esta seção é para uso normal do sistema.

## 1. Fazer login

O que fazer:

1. Abra a tela do sistema.
2. Informe e-mail e senha.
3. Entre.

Se deu certo:

- você consegue navegar pelas telas
- chamadas da API deixam de retornar erro de autenticação

Se deu errado:

- confira e-mail e senha
- veja se o backend está realmente rodando

## 2. Importar leads

Use esta rotina quando chegar uma planilha de contatos.

O que fazer:

1. Faça login.
2. Acesse `/leads`.
3. Clique em `Importar XLSX`.
4. Escolha um arquivo `.csv` ou `.xlsx`.
5. Revise o mapeamento das colunas.
6. Ajuste referências, se o sistema pedir.
7. Clique em `Importar`.
8. Confira a tabela de leads na mesma tela.

O que você deve observar:

- os nomes das colunas precisam bater com o sentido dos dados
- depois da importação, a lista recarrega

Exemplo fictício:

- arquivo: `leads_feira_inverno_2026.xlsx`
- coluna `Nome completo` vai para nome
- coluna `Celular` vai para telefone
- coluna `Cidade do evento` vai para cidade

Se depois da importação a pessoa "Bruno Costa" aparece na lista, a rotina funcionou.

## 3. Importar dados de publicidade

Use esta rotina quando chegar uma planilha de investimento, campanha ou mídia.

O que fazer:

1. Faça login.
2. Acesse `/publicidade`.
3. Clique em `Importar CSV/XLSX`.
4. Revise as sugestões.
5. Ajuste o mapeamento, se necessário.
6. Se quiser testar antes, rode um `dry-run`.
7. Quando estiver seguro, faça a importação real.

Em palavras simples:

- `dry-run` é um ensaio
- ele mostra o que aconteceria, sem gravar de verdade

Exemplo fictício:

- arquivo: `midia_feira_inverno_2026.xlsx`
- campanha: `Instagram - Semana 1`
- custo: `R$ 2.500,00`

Se o `dry-run` disser que as linhas válidas foram reconhecidas, você está no caminho certo.

## 4. Ver o dashboard de leads

Use esta rotina quando quiser uma visão resumida dos resultados.

O que fazer:

1. Faça login.
2. Acesse `/dashboard/leads`.
3. Ajuste filtros como data, evento, cidade ou estado.
4. Leia os números e gráficos.

Exemplo fictício:

- evento: `Feira de Inverno 2026`
- período: `01/06/2026` até `30/06/2026`

O que você pode descobrir:

- quantos leads entraram
- de quais cidades vieram
- como a captação evoluiu ao longo do tempo

## 5. Gerar relatório DOCX

Use esta rotina quando precisar de um relatório em arquivo Word.

Comando:

```powershell
cd C:\Users\NPBB\npbb\backend
python scripts\generate_tmj_report.py --evento-nome "Festival TMJ 2025" --data-inicio 2025-01-01 --data-fim 2025-12-31
```

O que você deve esperar:

- um arquivo `.docx` gerado na pasta de relatórios

Em linguagem simples:

- o sistema pega dados resumidos
- monta um documento
- aponta lacunas se faltarem dados

## 6. Fazer um ensaio completo do pipeline

Isto é útil quando você quer testar o fluxo inteiro sem depender de dados reais.

Comando:

```powershell
cd C:\Users\NPBB\npbb\backend
python scripts\dry_run_tmj_pipeline.py --out-dir reports/tmj2025/dry_run
```

O que sai no final:

- relatório de checagem
- relatório de cobertura
- arquivo Word de teste
- manifesto do que foi gerado

Em palavras simples:

- é um teste geral
- ele usa dados de exemplo
- serve para ver se as peças principais ainda estão funcionando juntas

## Sinais de que tudo está bem

Use esta lista rápida:

- `http://localhost:8000/health` responde `ok`
- `http://localhost:5173` abre
- você consegue fazer login
- uma importação de teste termina sem erro
- o dashboard carrega

Se esses cinco pontos estão verdes, o básico do sistema está saudável.

## Problemas comuns

Aqui está a versão curta e prática.

## Problema 1. `DATABASE_URL` não configurada

Sintoma:

- o backend reclama que não encontrou a conexão com o banco

O que fazer:

1. Abra `C:\Users\NPBB\npbb\backend\.env`
2. Preencha `DATABASE_URL`
3. Confirme se a senha e o endereço estão corretos

## Problema 2. `uvicorn` não encontrado

Sintoma:

- o backend não sobe

O que fazer:

```powershell
cd C:\Users\NPBB\npbb\backend
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Problema 3. A tela abre, mas a API não responde

Sintoma:

- frontend no ar
- backend fora do ar ou bloqueado

O que fazer:

1. Veja se `.\scripts\dev_backend.ps1` continua rodando
2. Teste `http://localhost:8000/health`
3. Confira se `FRONTEND_ORIGIN` está apontando para `http://localhost:5173`
4. Se o script PowerShell não existir, suba o backend pelo plano B com `uvicorn`

## Problema 4. Erro ao importar planilha

Sintoma:

- o arquivo sobe, mas a validação falha
- colunas não são reconhecidas

O que fazer:

1. Revise os nomes das colunas
2. Refaça o mapeamento com calma
3. Faça primeiro um teste com poucas linhas

Exemplo fictício:

- se a planilha traz `fone` e o sistema espera telefone, ajuste o mapeamento manualmente

## Problema 5. O frontend não sobe

Sintoma:

- erro ao rodar `npm run dev`

O que fazer:

```powershell
cd C:\Users\NPBB\npbb\frontend
npm install
npm run dev
```

## Problema 6. Preciso confirmar se o banco usado é o certo

Pergunta simples:

- o backend está usando o banco online do projeto ou um banco local perdido?

Como checar:

1. Abra o `.env`
2. Veja para onde `DATABASE_URL` aponta
3. Se estiver em `localhost` ou `127.0.0.1`, é banco local
4. Se estiver no host do Supabase, é o banco online

## Mini dicionário sem complicação

- API: a parte que recebe pedidos e devolve dados
- backend: o motor do sistema
- frontend: a tela do sistema
- banco: onde os dados ficam guardados
- deploy: colocar o sistema no ar
- migration: ajuste de estrutura do banco
- seed: carga inicial de dados
- dry-run: ensaio sem gravar de verdade

## Onde procurar mais detalhe

Se este manual resolver 80% do seu dia, ele já cumpriu o papel. Para os 20% mais específicos, use estes arquivos:

- visão geral: `README.MD`
- instalação completa: `docs/SETUP.md`
- fluxos principais: `docs/WORKFLOWS.md`
- problemas comuns: `docs/TROUBLESHOOTING.md`
- deploy: `docs/DEPLOY_RENDER_CLOUDFLARE.md`
- observabilidade e triagem de dados: `docs/etl/runbook_dq.md`

## Caminho recomendado para alguém novo no projeto

Se eu estivesse entrando hoje no NPBB, eu faria exatamente isso:

1. Ler este manual até o fim.
2. Subir backend e frontend localmente.
3. Testar login.
4. Fazer uma importação fictícia pequena.
5. Abrir o dashboard.
6. Só depois ir para os documentos mais técnicos.

## Última orientação

Quando bater dúvida, não tente entender o sistema inteiro de uma vez.

Faça assim:

1. descubra em qual parte está o problema
2. backend, frontend, banco ou planilha
3. resolva só aquela parte
4. teste de novo

Isso costuma ser mais rápido e muito menos cansativo.
