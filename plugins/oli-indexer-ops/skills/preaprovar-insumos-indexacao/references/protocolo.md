# Protocolo do gate indexing_input

## 1. Primeira passada somente leitura

1. Leia o job OPS por UUID e confirme:
   `queue=indexing`, `status=awaiting_indexing_review`, `approved_at IS NULL`,
   checkpoint presente, `validation_published_at IS NULL` e lease encerrada.
2. Congele `updated_at`, status, checkpoint digest, report head e patch head.
3. Leia process-wide todas as `DATA.indexacoes` do CNJ com paginação determinística.
4. Leia `DATA.folhas`, taxonomia e configuração efetiva do runtime.
5. Confirme que o checkpoint identifica o mesmo job, CNJ, perfil, gap, staging,
   prompts, grafo e taxonomia observados.
6. Execute os detectores comuns e a especialização aplicável.
7. Abra a íntegra de todo ato crítico e de toda anomalia. Não decida por título
   ou resumo quando a fronteira/classificação estiver em dúvida.

## 2. Checklist material

- cobertura integral do intervalo esperado;
- zero gaps, overlaps inexplicados, rows órfãs ou concorrentes;
- unidade documental correta e atomicidade preservada;
- processo, ato de juntada, `carimbo_subato`/arquivo e conteúdo interno distinguidos; anexos
  `parte_N` preservados por arquivo e pela ordem física das folhas, sem ordenar pelo sufixo;
- peça nativa, cópia, juntada e ato operativo separados quando materialmente
  distintos;
- classificação na taxonomia e compatível com a função processual;
- processo referido e eficácia no processo atual explícitos;
- relações recurso/decisão/retorno/cumprimento completas;
- nenhuma consequência sem causa anterior disponível;
- fonte integral acessível para todo ato crítico;
- zero horizontal/vertical da safra usado como fundamento do parecer;
- zero chamada e zero custo LLM novo do Indexer.

## 3. Artefatos

Crie `report.json` como `review-report/v2` com:

- `review_stage=indexing_input`;
- `snapshot.source_digest` de `review-source/indexing-input/v1`;
- `snapshot.checkpoint_digest` igual ao job;
- cobertura de páginas, rows, atos críticos, unidades, relações e ramos causais;
- `horizontal_analyses=not_applicable` e `verticals=not_applicable`;
- custo do Indexer igual a zero;
- evidência por folha e IDs externos/owners exatos.

Quando houver reparo unívoco, crie `patch.json` como `review-patch/v3`. Valide e
confira o digest ao vivo:

```bash
uv run reviewctl validate --report report.json --patch patch.json
uv run reviewctl digest --report report.json --patch patch.json
```

Sem patch, omita `--patch`. Arquivos com fontes locais ou OCR devem permanecer
fora do Git e com modo `0600`.

## 4. Save e aplicação humana

Anuncie antes da primeira escrita de controle e salve com cabeças esperadas:

```bash
uv run reviewctl save \
  --report report.json \
  --patch patch.json \
  --expected-current-report-id <uuid-ou-omitir> \
  --expected-current-patch-hash <sha-ou-omitir>
```

O estágio `indexing_input` usa a RPC tipada de save; não escreva as tabelas
diretamente. Para relações, uma única revisão deve cobrir exatamente todas as
resoluções `candidate`/`conflict` do snapshot. Decisões finais usam `accept` ou
`reject`; `pending` é reservado a ambiguidade jurídica real e impede a fila.

Não execute o comando abaixo sem o clique ou autorização humana **Aplicar patch**:

```bash
uv run reviewctl queue-input-patch \
  --patch patch.json \
  --patch-id <revision-uuid-persistido>
```

O comando usa `approve_and_queue_indexing_input_plan_v1`. O patch worker oficial
faz preflight integral, CAS, fencing e readback. Acompanhe até terminal:

- `verified`: releia DATA e prossiga para reauditoria;
- `stale`: descarte o snapshot e recomece somente leitura;
- `failed`/`failed_partial`: pare, preserve evidência e reporte `blocked`;
- `queued`/`running`: aguarde, não aceite nem dispare outro patch.

## 5. Readback e aceitação

Depois de patch exaustivo `verified`, não abra novo turno de análise. O runner
confere cada operação, recomputa o source digest e chama o aceite técnico tipado
somente quando não restar resolução pendente. A aceitação não toca `approved_at`;
apenas torna o job elegível ao claim. Divergência, stale ou escrita parcial não
aceitam o input e produzem `BLOQUEIO_TECNICO`, com evidência para reconciliação.
