# Protocolo do gate técnico pós-extração

## 0. Capacidade antes de autoridade

Antes de escrever, reúna evidência dos quatro componentes da mesma versão:

1. worker/CLI com `apply_extraction_native_text_repair_v2`, série/head explícitos
   e `begin_extraction_indexing`;
2. DATA `0141_extraction_treatment_budget_data` aplicada, com smoke confirmando
   RPC v1 revogada, v2 restrita a `service_role` e ledger
   `extraction_treatment_mutations`;
3. OPS `0142_extraction_gate_fencing_ops` aplicada, com smoke confirmando
   release/start antigos revogados, claim restrito a `service_role` e CAS único;
4. commit do worker implantado compatível com os contratos das duas migrations.

Um arquivo local, PR aberta ou linha `❌` no ledger não prova aplicação. Exija
recibo de migration, smoke e readback do ambiente alvo. Se um componente faltar
ou divergir, continue somente leitura, emita `BLOQUEADO_POR_CAPACIDADE` e liste
o gate ausente. Não aceite relatório, não aprove/aplique patch e não faça
fallback para `apply_extraction_native_text_repair`, `release_extraction_input`
ou `mark_extraction_indexing_started`.

## 1. Descoberta somente leitura

1. Resolva exatamente um `job_id` com `queue=indexing`,
   `status=awaiting_extraction_review` e `approved_at` nulo.
2. Congele `numero_processo`, `updated_at`, `extraction_review_series_id`,
   `extraction_review_head_report_id`, checkpoint/source digests, report aceito,
   PDF logical source/hash/bytes/page count, páginas e owners.
3. Confirme revisão sem lease: `worker_id` e `heartbeat_at` nulos.
4. Leia `DATA.folhas` com paginação determinística; não use apenas
   `max(numero_pagina)` como prova de cobertura.
5. Valide os bytes congelados: `%PDF`, `%%EOF`, abertura e contagem PyMuPDF.
   MIME, URL e Range isolados não provam um PDF íntegro.
6. Não exponha URL assinada nem texto jurídico integral; relate hashes,
   comprimentos, páginas e cardinalidades. Registre zero LLM/external calls.

## 2. Régua integral

- Cobertura: cada página dentro do teto está materializada ou tem compactação
  certificada; base à frente exige prova explícita.
- Identidade: uma row por página, processo/job/`id_externo`/`updated_at`
  coerentes e nada fora do intervalo.
- Texto: diferencie vazio não verificado de `[PÁGINA EM BRANCO]`; conteúdo curto
  ou duplicado é revisão, nunca reparo por inferência.
- Proveniência: método e envelope/carimbos entram no hash; não tipifique atos,
  assinantes ou papéis pelo nome/texto.
- Fonte: PDF novo, reconstruído, multipart, truncado ou com digest/contagem
  divergente é blocker, não tratamento local.

Catálogo mínimo:

| Código | Classe | Resultado inicial | Tratamento v1 |
|---|---|---|---|
| `PAGE_MISSING` | `text_extraction` | blocker | nenhum |
| `TEXT_EMPTY_UNVERIFIED` | `text_extraction` | blocker | nenhum |
| `VERIFIED_BLANK` | `text_extraction` | info | nenhum |
| `NATIVE_TEXT_MISSING` | `text_extraction` | review_required | `page.native_text.repair/v1` se todos os CAS fecharem |
| `TEXT_TOO_SHORT` / `CONSECUTIVE_TEXT_DUPLICATE` | `text_extraction` | review_required | nenhum |
| `CERTIFIED_COMPACTED_BACKLOG` / `LEGITIMATE_BASE_AHEAD_BACKLOG` | `normal_backlog` | info | nenhum |
| `PAGE_DUPLICATED` / `PAGE_OUT_OF_RANGE` | `technical_metadata` | blocker | nenhum |
| `PDF_HEADER_INVALID` / `PDF_EOF_MISSING` / `PDF_PAGE_COUNT_DRIFT` | `source_pdf` | blocker | nenhum |

Use `fit`, `fit_with_notes`, `review_required` ou `blocked`. Finding
`review_required` só deixa `observed` com evidência explícita. Blocker nunca é
aceito.

## 3. Comandos tipados e orçamento

Execute a partir do commit implantado compatível e com cache isolado:

```bash
UV_CACHE_DIR=/private/tmp/oli-indexer-uv-cache-extraction-review \
  uv run extraction-reviewctl draft \
  --job-id <UUID> --generated-by codex/preaprovar-extracoes \
  --output /caminho/seguro/report.json

uv run extraction-reviewctl validate --document /caminho/seguro/report.json
uv run extraction-reviewctl save-report --report /caminho/seguro/report.json \
  --expected-current-report-id <HEAD_UUID>
```

O patch contém uma operação e o literal `page.native_text.repair/v1`:

```bash
uv run extraction-reviewctl save-patch --patch /caminho/seguro/patch.json
uv run extraction-reviewctl approve-patch \
  --patch /caminho/seguro/patch.json --patch-id <UUID> \
  --approved-by codex/preaprovar-extracoes
uv run extraction-reviewctl apply-native-repair \
  --patch /caminho/seguro/patch.json --patch-id <UUID> \
  --worker-id codex/preaprovar-extracoes
```

Antes da DATA, a run OPS precisa fechar job/source/página/tratamento, mesma
fonte congelada, head corrente e orçamento. Marque
`mark_extraction_review_patch_mutation_started`; só então chame
`apply_extraction_native_text_repair_v2` e releia a row.

Uma falha comprovadamente anterior a `mutation_started_at` permite exatamente
uma segunda run ligada por `--retry-of-run-id <RUN_1_UUID>`. Falha posterior à
marca, resposta perdida ou sucesso esgotam o orçamento; não repita
automaticamente. Nunca use SQL livre como substituto.

## 4. Readback, sucessor e release

Após mutação:

1. leia a row DATA e `extraction_treatment_mutations`; confira `run_id`,
   `request_id`, tratamento, hashes, cardinalidade e `applied_updated_at`;
2. leia a run/eventos OPS; confira tentativa, `retry_of_run_id`, marca e estado;
3. confirme que texto oficial, método e carimbos não mudaram;
4. recapture PDF + folhas; novo digest supersede série/report/patch anteriores;
5. gere e salve parecer sucessor; nunca aceite o report anterior à mutação.

Sem patch, releia head/checkpoint/fonte imediatamente antes do aceite:

```bash
uv run extraction-reviewctl accept \
  --report /caminho/seguro/report.json --report-id <UUID> \
  --accepted-by codex/preaprovar-extracoes
```

O claim oficial é o único caminho de retomada. Logo antes da Indexing, o worker
recaptura tudo e `begin_extraction_indexing` falha diante de drift, série/head
divergente, blocker, patch pendente, run concorrente, mutação posterior ou lease
diferente. O aceite técnico não é aprovação humana.

## 5. Canário e fechamento

Não escolha canário por ordem de fila. Um canário inequívoco exige identidade,
fonte, tamanho, estado e risco compatíveis com o pedido. Se houver mais de um
candidato plausível, apresente-os sem executar e peça seleção.

Pare sem escrever diante de capacidade não comprovada, fonte nova/reconstruída,
multipart, bytes/contagem divergentes, backlog sem prova, owner ambíguo,
cardinalidade diferente de 1, OCR/Vision, custo externo, stale CAS ou orçamento
esgotado. Relate separadamente os gates de código, migration, deploy, smoke,
canário, aceite técnico, Indexing e aprovação humana final.
