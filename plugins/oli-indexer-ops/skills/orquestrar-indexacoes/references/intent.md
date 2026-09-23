# Intenção de orquestração

Materialize `orchestration-intent/v1` antes da primeira escrita. O artefato
delimita escopo e autoridade; não cria orçamento artificial nem substitui
status, lease, checkpoint, parecer ou aprovação humana.

## Forma mínima

```json
{
  "contract_version": "orchestration-intent/v1",
  "orchestration_run_id": "uuid",
  "requested_by": "actor-ref",
  "created_at": "timestamp",
  "expires_at": "timestamp",
  "repo_sha": "git-sha",
  "runtime": "local-env",
  "scope": {
    "job_ids": [],
    "numeros_processo": [],
    "expected_jobs": 0,
    "expected_pages": 0,
    "large_scope_authorized": false
  },
  "actions": {
    "discover": true,
    "enqueue": false,
    "run": false,
    "deterministic_repair": false,
    "technical_accept": false,
    "final_preapproval": false,
    "conclude_human_approved": false
  },
  "concurrency": 1
}
```

## Regras

- Comece com ações de escrita em `false` e habilite somente os verbos pedidos.
- Materialize filtros em job IDs/CNJs e cardinalidade antes de escrever.
- `expected_pages > 2500` exige `large_scope_authorized=true` apoiado em pedido
  explícito. Até 2.500 folhas, a autorização de execução cobre as chamadas
  normais do pipeline.
- Não adicione `max_llm_calls`, teto em dólares, custo por chamada, tokens ou
  tempo. Esses limites não fazem parte da autoridade operacional atual.
- Runtime escritor é `local-env`: checkout `oli-indexador` atualizado, `uv run`
  e `.env` local. Imagem OCI, Docker e VPS não são prova nem requisito.
- `orchestration_run_id` correlaciona apenas este artefato local. O batch V1
  rejeita `--orchestration-run-id`; não passe esse argumento ao CLI.
- Releia job ID, CNJ, status, lease, checkpoint e escopo antes da execução. Alvo
  ou cardinalidade novos exigem nova intenção.
- `conclude_human_approved=true` somente autoriza avaliar jobs que também tenham
  `approved_at` confirmado ao vivo e pedido específico de Conclusion.
- Não inclua segredos, OCR, peças, prompts ou análises integrais.
- Preserve o recibo JSON de `run_batch.py`; ele é evidência local, não substitui
  o readback em OPS/DATA.

## Frescor

Um gate é fresco quando a cabeça corrente não foi superseded, seu
snapshot/checkpoint coincide com o estado vivo, o parecer sucede a última
mutação material, não há patch/run ativo e o lease foi reconciliado. A skill do
gate define os campos específicos.
