---
name: consultar-oli-indexer
description: Consultar OPS e DATA do oli-indexer para diagnóstico, rastreabilidade, auditoria e preparação de execução. A skill é somente leitura; qualquer escrita ou execução exige pedido explícito separado.
---

# Consultar OLI Indexer

Use os dados do indexador sem confundir as duas instâncias Supabase nem transformar uma consulta em autorização de escrita.

Antes da primeira consulta da tarefa, leia [references/schema.md](references/schema.md). Para comandos repetíveis, use `scripts/oli_db.py`; ele só implementa `GET` e não contém verbos de mutação.

## Regras

- Trabalhe a partir do checkout local de `oli-indexador` e carregue credenciais
  pelo `Config.load_with_vault()` do projeto. O repositório histórico
  `oli-indexer` não é runtime nem fonte operacional. Nunca imprima chaves,
  tokens, URLs assinadas ou o conteúdo do `.env`.
- OPS contém fila, resultados do job e telemetria; DATA contém processo, folhas, indexações, prompts e estado persistido. Relacione por `jobs.id → indexacoes.job_id` e `jobs.search_key → numero_processo`.
- Se o usuário não indicar job/CNJ, liste o universo candidato e informe a quantidade. Para um parecer, bloqueie processos com mais de um job aberto até identificar o vigente.
- Paginação e ordenação devem ser determinísticas. Não conclua “não existe” após ler apenas a primeira página do PostgREST.
- Leia textos integrais somente quando necessários à análise e limite-os ao job/faixa de folhas em escopo. Não despeje OCR ou dados pessoais extensos na resposta.
- Prompt e análise integrais também são opt-in. Por padrão, reporte hashes, versões, chaves e contagens; abra conteúdo apenas quando a pergunta exigir.
- Google Sheets não é staging nem fonte de verdade. Qualquer instrução atual que mande corrigir ou consultar Sheets é resíduo a reportar como defeito.
- A consulta pode produzir comandos ou um plano de correção, mas não autoriza `PATCH`, `POST`, `DELETE`, RPC de enqueue, pipeline, recall, conclusão ou aprovação.

## Saída

Sempre identifique a origem de cada dado (`OPS.jobs`, `OPS.llm_runs`, `DATA.indexacoes`, `DATA.folhas` ou `DATA.processos`), o horário do snapshot e filtros usados. Diferencie fato lido, inferência e dado não disponível.
