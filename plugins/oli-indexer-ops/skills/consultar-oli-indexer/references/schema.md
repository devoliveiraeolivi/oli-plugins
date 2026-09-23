# Mapa operacional do OLI Indexer

Leia este arquivo antes de consultar o banco. Confirme colunas no código atual quando houver drift.

## Instâncias

### OPS (`config.supabase_jobs`)

- `jobs`: fila multiuso. Para indexação, sempre filtre `queue=eq.indexing`.
  - `id`: job UUID.
  - `search_key`: CNJ/número do processo.
  - `status`: `pending`, `running`, `awaiting_approval`, `completed` ou `failed`.
  - `input`: recalls, deletes, filtros, instruções e opções do job.
  - `output`: perfil/área resolvidos, preparação e métricas publicadas.
  - `approved_at`/`approved_by`: aprovação humana. Nunca alterar em pré-aprovação.
  - `worker_id`/`heartbeat_at`: lease. `running` sem processo local não basta para concluir que está órfão; confira heartbeat e executor.
  - `report_html` e `llm_results`: relatório e verticais produzidos pela Validation.
  - `validation_published_at`: checkpoint durável da Validation da execução corrente; ausente
    bloqueia criação/aplicação de patch.
- `indexing_review_reports`: snapshots imutáveis de `review-report/v1`. A row corrente é a
  única com `superseded_at` vazio.
- `indexing_review_patches`: revisões imutáveis de `review-patch/v1` ou `review-patch/v2`; relacione por
  `report_id`/`job_id` e use `patch_key` + `version` para a série legível.
- `indexing_review_patch_runs`: tentativas de aplicação e auditoria before/after/readback.
  `queued`/`running` são ativos; `verified`, `failed`, `failed_partial` e `stale` são terminais.
- `llm_runs`: chamadas LLM. Filtre `contexto->>job_id`, registre janela temporal e some `cost_usd`, tokens e chamadas por `operacao`/`model`.
  - `template_hash`, `grafo_id`, `no_id`, `andamento_ref` e `params_snapshot` formam a trilha de configuração da chamada.

### DATA (`config.supabase`)

- `processos`: estado canônico do processo, metadados e análises persistidas após Conclusion. Não confundir com o resultado transitório do job aguardando aprovação.
- `indexacoes`: andamentos do job e históricos.
  - Para o staging corrente, filtre `job_id` exato e registre `status_validacao`.
  - Em relatório de processo completo, preserve sempre o `job_id` proprietário de cada row.
    O par `(job_id, id_externo)` é o alvo de patch; nunca atribua a uma row histórica o id do
    job corrente.
  - `folha_inicio`/`folha_fim` definem cobertura; `id_externo` é identidade, não derive identidade da folha.
  - `integra` é fonte preferencial da linha quando disponível; sua ausência não é erro se `folhas` cobre a faixa.
- `folhas`: texto e envelope por página.
  - `numero_processo` + `numero_pagina` identificam a folha.
  - `texto` e `texto_pymupdf` são fontes materiais.
  - `carimbo_*` descreve o envelope eletrônico e pode ser apenas o wrapper de virtualização.
  - `mapeamento_*` descreve origem, referência e relações processuais versionadas.
- `prompts`: fonte runtime por chave exata `(app, area, operacao, perfil)`; compare SHA-256 com `llm_runs.template_hash` e `flows-src/`.
- `prompts_history`: snapshots arquivados por `prompt_id`; use quando o hash do job não casa com a row atual.
- `cascata_estado` e `eventos_processo`: checkpoints/eventos persistidos de EF, não substitutos da fonte material.
- `indexing_review_patch_fences`: fence técnica do runner. Não edite nem use como relatório;
  ela existe para impedir worker antigo de escrever após supersessão/retry.
- `indexing_review_indexacao_lineage`: índice imutável de merge/split por run e saída; use para
  rastrear `output_id → source_ids`. Não substitui o patch nem a fonte material.

## Prioridade de evidência

1. Texto material em `indexacoes.integra` ou `folhas`.
2. Taxonomia, prompts, dispatch e código do commit auditado.
3. `indexacoes` do job vigente.
4. `jobs.report_html` e `jobs.llm_results`.
5. Históricos em `processos`/`indexacoes` como comparação, nunca como substituto da fonte.

## Protocolo de leitura

1. Registre repositório, worktree, branch, commit e horário.
2. Resolva job/CNJ e rejeite ambiguidade.
3. Leia o job em OPS.
4. Leia contagem, status e cobertura de `indexacoes`.
5. Leia metadados de `folhas`; abra texto apenas nas faixas necessárias.
6. Leia `llm_runs` por delta da execução, não pelo acumulado histórico sem janela.
7. Faça readback após qualquer mutação posteriormente autorizada.

## Utilitário somente leitura

Execute a partir do repositório com o ambiente `uv`:

```bash
uv run python <plugin-root>/skills/consultar-oli-indexer/scripts/oli_db.py --repo . pending --perfil execucao_fiscal
uv run python <plugin-root>/skills/consultar-oli-indexer/scripts/oli_db.py --repo . pending --summary
uv run python <plugin-root>/skills/consultar-oli-indexer/scripts/oli_db.py --repo . snapshot --job-id <uuid>
uv run python <plugin-root>/skills/consultar-oli-indexer/scripts/oli_db.py --repo . processo --cnj <cnj> --include-analyses
uv run python <plugin-root>/skills/consultar-oli-indexer/scripts/oli_db.py --repo . indexacoes --job-id <uuid> --from-page 88 --to-page 98 --include-content
uv run python <plugin-root>/skills/consultar-oli-indexer/scripts/oli_db.py --repo . folhas --cnj <cnj> --from-page 88 --to-page 98 --include-text
uv run python <plugin-root>/skills/consultar-oli-indexer/scripts/oli_db.py --repo . prompts --area tributario --perfil execucao_fiscal --operation processo.indexacao --history
uv run python <plugin-root>/skills/consultar-oli-indexer/scripts/oli_db.py --repo . analises --job-id <uuid> --since <ISO-8601> --include-rows
uv run python <plugin-root>/skills/consultar-oli-indexer/scripts/oli_db.py --repo . validation --job-id <uuid>
uv run python <plugin-root>/skills/consultar-oli-indexer/scripts/oli_db.py --repo . costs --job-id <uuid> --since <ISO-8601>
```

Acrescente `--include-errors` somente para diagnosticar chamadas falhas; a saída
inclui categoria, tentativa e a mensagem já truncada pelo produtor, nunca o
prompt ou a resposta integral.

Use `pending --summary` para obter a distribuição completa por perfil/natureza e os
bloqueios operacionais sem despejar cada job. `review_publish_eligible` exige o checkpoint
durável de Validation; `report_html` isolado não substitui `validation_published_at`.
