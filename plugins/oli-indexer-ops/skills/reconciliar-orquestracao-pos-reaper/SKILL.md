---
name: reconciliar-orquestracao-pos-reaper
description: Reconciliar explicitamente um target orquestrado do oli-indexer depois que o reaper comprovou ZOMBIE_NO_HEARTBEAT, fechando reservas pré-dispatch e marcando efeitos iniciados como UNKNOWN. Use só para o job/run/claim exatos; nunca retoma, repete efeito pago, desbloqueia o run ou declara persistência canônica.
---

# Reconciliar orquestração pós-reaper

Feche o ledger técnico deixado por uma lease expirada sem transformar ausência
de heartbeat em licença para retry.

Antes de qualquer escrita, leia [references/protocolo.md](references/protocolo.md)
e use `$consultar-oli-indexer` para congelar o snapshot OPS. A primeira passada
é somente leitura.

## Autoridade

- Esta skill é somente por invocação explícita. A invocação precisa identificar
  ou autorizar resolver um conjunto exato de `orchestration_run_id` + job.
- Reconciliação só é elegível quando `OPS.jobs.status=failed`, `worker_id` está
  vazio e `error_code=ZOMBIE_NO_HEARTBEAT`, enquanto o target ainda carrega o
  claim ativo correspondente.
- Não chama provider, LLM, reviewer, embedding, Vision ou worker. Não faz
  enqueue, recall/delete, retry, aprovação, unlock ou mudança de estado para
  sucesso.
- Qualquer digest, owner, status, cardinalidade ou razão de falha divergente
  bloqueia a escrita.

## Resultado

Reserva `reserved` vira `released`; reserva `started` vira `unknown` pelo teto
de custo reservado. O target termina `UNKNOWN`, o run fica `BLOCKED` e o recibo
`post-reaper-reconciliation/v1` registra apenas identidades, contadores, custos
e hashes operacionais. Texto jurídico e payload de autos não entram no OPS.

Um retry posterior exige readback externo, decisão humana explícita e nova
intenção; esta skill nunca o inicia.
