# Resultados de testes automatizados

Data: 2026-04-20.

## Backend direcionado

Classificacao: validado por teste.

Comando:

```powershell
cd backend
$env:PYTHONPATH='..'
$env:SECRET_KEY='ci-secret-key'
$env:TESTING='true'
python -m pytest tests/test_lead_batch_endpoints.py tests/test_leads_hardening_contract.py -q -p no:cacheprovider
```

Resultado:

```text
35 passed in 46.43s
```

Cobertura objetiva nesta execucao:

- intake de lote nao persiste novos payloads inline no banco;
- ponteiros de storage sao persistidos;
- storage local e bloqueado em producao;
- spool de upload le o arquivo em chunks;
- contrato estatico da migration de RLS central existe;
- contrato estatico de roles sem `BYPASSRLS` existe;
- gates de runtime/deploy existem e falham fechado para configuracoes inseguras.

## Frontend direcionado

Classificacao: validado por teste.

Comando:

```powershell
cd frontend
npm run test -- ImportacaoPage.test.tsx --run -t "legacy import-hint preflight|server-side intake|matching valid batch row" --reporter=verbose
```

Resultado:

```text
1 passed file, 4 passed tests, 35 skipped
```

Cobertura objetiva nesta execucao:

- o fluxo Bronze principal nao chama hash/preflight legado no browser;
- o hint aplicado vem do intake server-side;
- edicoes manuais sao preservadas no payload server-side;
- em lote, o hint server-side e aplicado apenas a linha valida correspondente.

## Frontend completo da pagina de importacao

Classificacao: validado por teste, com falha.

Comando:

```powershell
cd frontend
npm run test -- ImportacaoPage.test.tsx --run --reporter=dot
```

Resultado:

```text
16 failed, 23 passed
```

Conclusao objetiva:

- A validacao direcionada do fluxo novo passou.
- A suite completa da pagina nao esta verde e nao pode ser usada como evidencia de regressao completa resolvida.
