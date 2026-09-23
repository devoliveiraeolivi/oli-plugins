# Protocolo de Conclusion pós-aprovação

## 1. Censo read-only

Registre snapshot timestamp e pagine deterministicamente `OPS.jobs` com:

```text
queue=indexing
status=awaiting_approval
approved_at IS NOT NULL
```

Para cada alvo, leia job ID, `numero_processo`, `approved_at`, worker/heartbeat,
input/output, checkpoint de Validation, parecer corrente e patches/runs ativos.
Exclua lease ativo, aprovação ausente, snapshot divergente, gate stale ou mais
de um job aberto sem resolução explícita.

Não use `approved_by`, `report_html`, `success` histórico ou posição na fila
como prova de aprovação.

## 2. Congelamento e dry-run

Congele:

- job IDs e CNJs;
- `approved_at` exato;
- status e lease;
- checkpoint/digest da Validation e parecer aplicável;
- cardinalidade e total de folhas esperados;
- repo SHA local e plugin version;
- baseline de `OPS.llm_runs`.

A invocação standalone materializa
`../orquestrar-indexacoes/references/intent.md` como `orchestration-intent/v1`;
ela não usa uma intenção informal. `expected_jobs` é a cardinalidade exata e
`expected_pages` cobre todo o lote. Acima de 2.500 folhas, a intenção precisa
registrar autorização explícita; até esse limite, não invente ceilings de LLM,
reviewer, embedding, Vision, custo ou tempo.

O parecer/checkpoint é fresco somente se a cabeça corrente não foi
superseded, os digests coincidem com o estado vivo, ele sucede a última mutação
material e não há patch/run ativo incompatível. Registre o SHA do checkout
local de `oli-indexador`; imagem OCI ou digest de container não é requisito do
worker.

Use o runner integrado e capture saída estruturada:

```bash
uv run python scripts/ops/run_batch.py \
  --dry-run --run-approved \
  --concurrency 1 \
  --job-id <job-id-1> --job-id <job-id-2> \
  --cnj "<cnj1>,<cnj2>" \
  --json-output <arquivo.json>
```

O dry-run deve selecionar exatamente o conjunto congelado. Job extra, ausente,
reordenamento não explicado ou cardinalidade diferente bloqueia a execução.
Se um alvo for inelegível, não reduza o lote por conta própria; um novo conjunto
exige nova intenção/autoridade. Se a versão ativa do runner não aceitar job ID
exato, pare sem executar.

## 3. Execução

Antes do efeito real, o claim/RPC precisa comparar e consumir atomicamente job
ID, `status=awaiting_approval`, `approved_at` exato, checkpoint/digest e
ausência de lease congelados. Repetir o mesmo comando sem esse CAS não fecha a
janela TOCTOU; enquanto o runtime não oferecer essa precondição, pare depois do
dry-run.

Não acrescente flags `--max-*` à execução. As chamadas e embeddings previstos
pela Conclusion estão cobertos pela autorização do processo; o readback de
`OPS.llm_runs` serve para recibo e reconciliação, sem transformar ausência de
telemetria em custo zero.

Com o claim/CAS comprovado, repita o mesmo comando sem `--dry-run`.
Não altere filtros, limite, concorrência ou runtime entre preview e
execução. Um executor ativo impede segundo run.

Não use `--reindex-only`: desde o contrato atual, ele não casa com o caminho
approved-only. Não use `--allow-multiple` para contornar duplicidade.

## 4. Resposta incerta e retry

Em timeout, desconexão, processo interrompido ou PostgreSQL `57014`:

1. não repita o comando;
2. releia job, lease, heartbeat, `error_code`, DATA e Salesforce;
3. determine se houve commit parcial ou se a aprovação foi consumida;
4. só retome um job/CNJ exato se continuar aprovado, sem lease e sem evidência
   de persistência já concluída;
5. registre a tentativa sucessora ligada ao mesmo run ID.

Embeddings degradados ou outro erro não crítico devem ser reportados sem
mascarar o estado canônico.

## 5. Plano pré-efeitos e manifesto de persistência

Antes de qualquer upload em Supabase Storage, chamada de embedding ou write
canônico, anexe ao claim um `conclusion-effect-plan/v1` hash-only. Ele contém os
IDs externos exatos, aplicabilidade de slices/embeddings, as quatro fontes
canônicas e a allowlist fechada de exclusões. Recall/delete é incompatível com
esse caminho e bloqueia o claim.

Depois que links e demais valores finais estiverem preparados, mas antes do
primeiro write em DATA ou Salesforce, materialize `persistence-manifest/v1` e
ligue-o ao SHA-256 do plano pré-efeitos. Essa separação é obrigatória: o
manifesto não pode fingir conhecer URLs antes do upload, e o upload não pode
ocorrer sem uma prova anterior no OPS.

Cada fonte do manifesto registra explicitamente `identity_fields` e
`material_fields`, além das identidades, contagens e hashes. As exclusões são
exatamente:

- `DATA.indexacoes.context_embedding`;
- `DATA.indexacoes.julgador_id`;
- `DATA.julgadores`;
- `DATA.eventos_processo`;
- `Supabase Storage PDF slices`;
- `legacy duplicate cleanup outside target external_ids`.

Qualquer exclusão adicional, ausente ou reordenada é conflito de contrato. O
manifesto também fixa `terminal_ops_expectation`: `status=success`,
`error_code=null` e os mesmos campos da aprovação humana congelada.

## 6. Readback terminal

Concilie por job:

- `OPS.jobs.status`, `approved_at`, `error_code`, lease e heartbeat;
- ledgers de revisão/patch e eventos de orquestração quando disponíveis;
- `DATA.indexacoes` pelo `job_id` e cobertura;
- `DATA.processos` por `numero_processo`, inclusive análises esperadas;
- objetos/campos Salesforce escritos pela Conclusion;
- chamadas, tokens e custo em `OPS.llm_runs` depois do baseline.

Para cada job, calcule o digest canônico do manifesto e ligue-o de forma
imutável à intenção, ao `conclusion-effect-plan/v1`, checkpoint e runtime:

- status OPS esperado `success`, `error_code=null` e aprovação humana ainda
  ligada ao mesmo parecer/hash;
- IDs/ranges/status `concluido` e hashes dos valores materiais esperados em
  `DATA.indexacoes`, inclusive correções e exclusões previstas;
- campos e hashes dos valores de `DATA.processos` que o perfil/checkpoint manda
  propagar;
- `Andamento__c` esperados por `ExternalID__c`, com hash dos campos materiais,
  e campos/valores aplicáveis de
  `ProcessoContencioso__c` (incluindo data/fase apenas quando o commit cobre o
  processo inteiro).

Campo não aplicável deve ser marcado como tal; não aceite lista genérica. O
readback compara identidade, cardinalidade, valores/hashes e digest imutável
desse manifesto. Mudança posterior cria nova intenção e nova autoridade.
O servidor deve recomputar a decisão a partir de `observed_count` e
`observed_records_sha256`; não confie apenas em um booleano `matches` enviado
pelo runner. O target só pode terminar `CANONICALLY_PERSISTED` depois de
`persistence_readback_status=MATCHED` no OPS.

Compare também os valores UTF-8 exatos dos campos humanos previstos no
manifesto. Perda de acentos, normalização indevida ou substituição editorial
entre DATA e Salesforce é divergência material de readback, não detalhe a ser
silenciado. A Conclusion reporta a divergência e não corrige conteúdo jurídico
por conta própria.

Classifique o terminal:

- `CANONICALLY_PERSISTED`: todas as fontes aplicáveis convergem;
- `BLOCKED_NEEDS_HUMAN`: o job exige nova aprovação;
- `FAILED_RECONCILED`: falha comprovada e estado conhecido;
- `UNKNOWN_REQUIRES_READBACK`: ainda não há evidência suficiente.

Nunca converta unknown em sucesso por mensagem do CLI.
