---
name: concluir-indexacoes-aprovadas
description: Executar Conclusion somente para jobs do oli-indexer já aprovados por humano, com censo read-only, escopo exato, dry-run, concorrência 1 e readback canônico. Use apenas por invocação explícita depois da aprovação; nunca cria aprovação, amplia o lote, reindexa ou faz retry cego.
---

# Concluir indexações aprovadas

Feche o trecho posterior à aprovação humana sem confundir execução do runner
com persistência canônica.

Antes de agir, leia [references/protocolo.md](references/protocolo.md) e use
`$consultar-oli-indexer` para o censo OPS/DATA. A primeira passada é sempre
somente leitura.

Materialize a mesma `orchestration-intent/v1` descrita em
[orquestrar-indexacoes/references/intent.md](../orquestrar-indexacoes/references/intent.md),
mesmo em invocação standalone. A intenção precisa conter somente os jobs
aprovados que sobreviveram ao censo, com a contagem total de folhas. Acima de
2.500 folhas, exija autorização explícita; abaixo disso, a autorização específica
de Conclusion cobre os efeitos normais do pipeline sem tetos artificiais de
chamadas, dólares, tokens ou tempo.

## Autoridade

- A skill só pode operar quando foi invocada explicitamente e o usuário pediu
  a execução pós-aprovação para o escopo atual, ou quando existe intenção
  durável, não expirada, com `conclude_human_approved=true`.
- Em ambos os casos, cada job precisa estar em `queue=indexing`,
  `status=awaiting_approval` e ter `approved_at` não nulo no readback ao vivo.
- Nunca escreva `approved_at`/`approved_by`, aprove job, inclua pendentes ou
  execute toda a fila por conveniência.
- Não combine `--run-approved` com `--reindex-only`; não use recall/delete,
  correção ad hoc, patch pós-aprovação ou mudança de código/runtime.

## Execução

Congele job ID, `numero_processo`, `approved_at`, status, lease, hashes e
cardinalidade. Rode primeiro `--dry-run --run-approved --concurrency 1`, com
job IDs exatos, CNJs correspondentes, `orchestration_run_id` e saída JSON. O
conjunto precisa ser idêntico ao escopo autorizado. Se o runner ativo não
suportar seleção por job ID, bloqueie; CNJ isolado não substitui identidade.

O dry-run não concede uma janela de confiança. A execução real precisa fazer
claim/CAS atômico do mesmo `approved_at`, status, checkpoint digest e ausência
de lease materializados. Enquanto o runtime só voltar a consultar esses campos
sem CAS, pare depois do dry-run.

Job inelegível ou extra não autoriza executar silenciosamente o subconjunto.
Materialize nova intenção/cardinalidade e obtenha autoridade específica.

Execute uma vez, serialmente. Timeout, resposta incerta ou PostgreSQL `57014`
exigem readback antes de qualquer retry. Se ainda for seguro retomar, faça-o
para o job/CNJ exato; nunca repita o lote aberto.

Execute no checkout local de `oli-indexador`, com `uv run` e o `.env` local.
Não use Docker, VPS, Portainer ou o repositório histórico `oli-indexer`, e não
exija deploy do worker.

Antes de qualquer slice, embedding ou persistência, o runtime precisa anexar
`conclusion-effect-plan/v1`; antes dos writes canônicos, precisa anexar o
`persistence-manifest/v1` autoexplicativo e ligado ao primeiro digest. Sem os
dois recibos OPS, pare sem executar.

Conclusion pode chamar embeddings e outros serviços externos já previstos no
pipeline. Concilie esses efeitos pelo plano, manifesto e `OPS.llm_runs`; não
adicione limites monetários ou de chamadas que não tenham sido pedidos.

## Fechamento

Depois do runner, confira `OPS.jobs`, lease/heartbeat, `error_code`, ledgers,
`DATA.indexacoes`, `DATA.processos` e o estado canônico aplicável no Salesforce.
Calcule também o delta de `OPS.llm_runs`.

Saída `OK` ou `success` isolado não prova persistência. Se o job retornar a
`awaiting_approval` com `approved_at` vazio, registre um novo gate humano e
pare. Só declare `CANONICALLY_PERSISTED` quando o readback integral for
coerente.
