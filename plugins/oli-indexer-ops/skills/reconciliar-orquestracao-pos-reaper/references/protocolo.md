# Protocolo pós-reaper

## 1. Censo read-only

Congele, com paginação determinística:

- `orchestration_run_id`, job ID, `numero_processo` e cardinalidade;
- `intent_sha256`, `snapshot_sha256`, claim token e execution snapshot;
- estado do run/target e timestamps da lease;
- `OPS.jobs.status`, `worker_id`, `heartbeat_at`, `error_code` e
  `input.orchestration_run_id`;
- todas as reservas do job, incluindo estado, efeito, modelo, unidades, teto de
  custo e timestamps;
- contadores reservados, consumidos, observados e unknown do run.

Bloqueie se o reaper não estiver comprovado por
`status=failed`, `worker_id IS NULL` e `error_code=ZOMBIE_NO_HEARTBEAT`, se o
target já terminou por outro caminho, se o run/claim não casar ou se existir
mais de um alvo sem seleção explícita.

## 2. Preview

Mostre por target:

- reservas `reserved` que serão liberadas como `REAPED_BEFORE_DISPATCH`;
- reservas `started` que serão conciliadas como `REAPED_AFTER_DISPATCH` e
  `UNKNOWN`;
- deltas exatos de unidades e custo;
- estado terminal esperado `target=UNKNOWN`, `run=BLOCKED`.

Não estime resposta de provider nem converta `started` em falha conhecida. Se
o efeito atravessou a fronteira de dispatch, sua consequência é incerta.

Gere o artefato executável sem escrever:

```bash
uv run python scripts/ops/orchestrationctl.py reconcile-reaper \
  --run-id <uuid> --job-id <uuid> --claim-token <claim> \
  --intent-sha256 <sha256> --snapshot-sha256 <sha256> \
  --idempotency-key <uuid> --output <preview.json>
```

## 3. Escrita cercada

Use somente a RPC tipada
`reconcile_reaped_indexing_orchestration_target` com run ID, job ID, claim,
intent hash, snapshot hash e chave de idempotência. A função deve operar como
`SECURITY DEFINER`, com `search_path` vazio e `EXECUTE` apenas para
`service_role`.

Não edite tabelas diretamente. Conflito CAS, drift contábil ou recibo
malformado termina a tentativa sem fallback.

Depois de conferir o preview e somente com autoridade explícita, repita os
mesmos argumentos acrescentando `--expected-request-sha256 <hash-do-preview>`
e `--execute`. Preserve a mesma chave de idempotência em retry de resposta
incerta; nunca gere outra chave para o mesmo efeito lógico.

## 4. Readback obrigatório

Confirme no OPS:

- nenhuma reserva continua `reserved` ou `started` para o claim;
- cada reserva terminou exatamente em `released` ou `unknown` conforme o estado
  anterior;
- contadores reservados caíram sem ficar negativos;
- unidades iniciadas foram consumidas e o teto dos efeitos incertos entrou em
  `unknown_cost_usd`;
- target `UNKNOWN`, outcome `unknown`, run `BLOCKED`;
- documento e hash `post-reaper-reconciliation/v1` presentes;
- eventos `BUDGET_RELEASED`/`BUDGET_UNKNOWN` e `TARGET_UNKNOWN` ligados ao job.

Retry idempotente da mesma reconciliação pode confirmar o mesmo recibo; jamais
gera segundo ajuste contábil.

## 5. Saída

Reporte identidades e hashes, contagens released/unknown, delta contábil,
event sequences, estado final e o próximo gate humano. Não exponha claim token,
segredos, texto jurídico ou payload dos autos no relatório.
