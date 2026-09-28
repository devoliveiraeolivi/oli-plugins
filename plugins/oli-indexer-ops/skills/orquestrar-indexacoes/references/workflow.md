# Workflow de orquestração

## 1. Preflight curto

1. Registre checkout, branch, commit e `git status` do `oli-indexador`.
2. Em checkout limpo, rode `git pull --ff-only`. Em checkout sujo, preserve as
   mudanças e use uma worktree limpa baseada em `origin/main` ou aguarde o
   usuário atualizar o checkout; nunca faça reset/stash automático.
3. Carregue o runtime com `uv run` e o `.env` local. Não procure Docker, VPS,
   Portainer, imagem ou worker remoto.
4. Resolva job ID + CNJ exatos, status/lease e contagem de folhas. Mais de um job
   aberto para o CNJ bloqueia escolha por conveniência.
5. Acima de 2.500 folhas, pare e peça autorização explícita. Até esse limite, a
   autorização para executar o processo cobre o custo normal do pipeline; não
   peça tetos artificiais de chamadas, dólares, tokens ou tempo.
6. Confirme pela configuração carregada que mapeamento LLM e reviewer embutido
   estão desligados. Não tente preencher `mapeamento_*` quando o recurso está
   desligado.
7. Trace o snapshot publicado do perfil. Para EF v5, espere o ledger
   `processo.execucao_fiscal` e seus descendentes declarados; não procure
   `eventos_ef`, cascata ou vertical oculta como fallback.
8. Materialize `orchestration-intent/v1` com o escopo e as ações exatas.

## 2. Criação opcional

Use dry-run com seleção explícita e os mesmos filtros da criação real:

```bash
uv run python scripts/ops/run_batch.py \
  --create-only --dry-run \
  --no-base-filter --soql-where "Name = '<CNJ>'" \
  --json-output .artifacts/ef-create-preview.json
```

Confira que o conjunto contém somente o processo pedido. Depois da autorização
de criação, repita sem `--dry-run` e releia `OPS.jobs`. Nunca use
`--allow-multiple` para contornar job aberto. `--cnj` filtra a fase de execução,
não a criação; por isso a criação exata usa o filtro SOQL acima. Acrescente
`--enable-extraction-review` ou `--enable-indexing-approval` somente quando o
objetivo do teste incluir esses gates; não os ligue por padrão num piloto EF que
deve seguir em uma execução até `awaiting_approval`.

## 3. Execução rápida

Para um job `pending`, rode uma vez o alvo exato:

```bash
uv run python scripts/ops/run_batch.py \
  --run-only --concurrency 1 \
  --job-id <JOB_ID> --cnj "<CNJ>" \
  --json-output .artifacts/ef-run.json
```

Não passe flags `--max-*`. Não acrescente `--allow-gap-grande`, compactação,
layout PJe, `--execution-profile`, `--orchestration-run-id` ou outro escape sem
o problema correspondente e autorização específica. O batch V1 rejeita
atestação/budget por CLI; o caminho feliz de um processo pequeno é esse único
comando até o próximo gate configurado.

Se o job pausar em gate técnico, feche o parecer pela skill própria e retome o
mesmo job, sem recriar ou reexecutar fases anteriores:

```bash
uv run python scripts/ops/run_batch.py --run-extraction-approved --concurrency 1 \
  --job-id <JOB_ID> --cnj "<CNJ>" --json-output .artifacts/ef-after-extraction.json

uv run python scripts/ops/run_batch.py --run-indexing-approved --concurrency 1 \
  --job-id <JOB_ID> --cnj "<CNJ>" --json-output .artifacts/ef-after-input.json
```

## 4. Readback mínimo

No caminho feliz, releia apenas:

- `OPS.jobs`: status, lease/heartbeat, `error_code`, perfil, checkpoint e
  `output.verticais_execucao`;
- `DATA.indexacoes`: cardinalidade, cobertura de folhas, owners e status;
- `OPS.llm_runs`: chamadas e custo conhecidos da execução, sem transformar
  telemetria ausente em zero.

Em EF v5, confirme `success` das operações publicadas e que nenhum descendente
ficou `failed` ou `blocked_dependency`. Processo relacionado sem corpus é aviso
não bloqueante quando `dependent_verticals={}`; bloqueie apenas se uma operação
ativa depender dele ou houver decisão humana relacional pendente.

## 5. Falhas e retomada

- Abra diagnóstico aprofundado somente diante de saída não zero, `error_code`,
  digest/cardinalidade divergente, conflito de lease, timeout com efeito incerto
  ou readback incompatível.
- Falha depois de efeito LLM não autoriza reinferência. Preserve recibo e
  determine o checkpoint antes de retomar.
- `stale` de patch exige comparar alvo vivo, `expect` e forma normalizada. Se a
  divergência for apenas normalização e o patch worker ainda não contiver o PR
  #156, peça o deploy de `oli-indexer-patch`; não crie revisão sucessora.
- Com o worker corrigido, retry do mesmo patch corrente é preferível quando não
  houve mutação e o alvo continua materialmente idêntico. Nova revisão só cabe
  quando o estado material ou a correção mudou.
- Não faça retry cego, recall/delete nem reprocessamento amplo.

## 6. Aprovação e deploy

Pare em `awaiting_approval` com `approved_at` vazio. O operador aprova pelo
caminho humano oficial. Depois da aprovação, use somente
`$concluir-indexacoes-aprovadas` com o job exato.

O worker local nunca exige deploy. Quando uma correção mergeada atingir
`oli-indexer-api`, `oli-indexer-patch`, `oli-gateway`, `oli-app` ou `oli-bi`,
informe exatamente qual serviço precisa de deploy e aguarde o usuário fazê-lo.
