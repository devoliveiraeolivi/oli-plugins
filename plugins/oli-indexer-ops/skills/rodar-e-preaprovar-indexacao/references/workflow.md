# Workflow diário: criar, executar e pré-aprovar

## 1. Resolver escopo

- Registre repo/worktree/commit e confirme que o código a executar é o desejado.
- Resolva filtros de processo por campos seguros (`--natureza`, `--assunto`, `--cliente`, `--grupo` ou CNJs explícitos).
- Liste jobs abertos existentes. Nunca use `--allow-multiple` por conveniência.

## 2. Prévia de criação

Descubra sem escrever:

```bash
uv run python scripts/ops/run_batch.py --create-only --dry-run --natureza "Execução Fiscal" --limit-create <N>
```

Apresente processos candidatos, duplicados/pulados e quantidade. Se o pedido atual já autorizou criar e o snapshot continua igual, prossiga; mudança material de escopo exige confirmação.

## 3. Criar e conferir

Use os mesmos filtros da prévia, sem `--dry-run`, preferencialmente com `--create-only`. Em seguida, leia OPS e registre IDs/CNJs criados. Cardinalidade divergente interrompe o fluxo.

## 4. Baseline de custo

Antes de executar, registre `llm_runs` por job e horário de início. Custo final é delta dessa janela, nunca soma histórica indiscriminada. Separe operações sem telemetria.

## 5. Executar

- Para jobs já criados, execute somente os CNJs/IDs resolvidos e use concorrência 1 por padrão.
- Adquira lease pelo caminho oficial; um executor ativo impede segundo run.
- Monitore heartbeat e fases. Silêncio de chamada longa não autoriza retry.
- Fallback de modelo deve ser reportado e separado da comparação de preço.
- Se o app cair, confira processo local, heartbeat, staging e status antes de retomar. Não faça recall automático.

Exemplo para jobs pendentes de CNJs explícitos:

```bash
uv run python scripts/ops/run_batch.py --run-only --concurrency 1 --cnj "<cnj1>,<cnj2>"
```

## 6. Pós-execução

- Aguarde drenagem de `llm_runs` e calcule chamadas, tokens e custo por operação/modelo.
- Confira `jobs.status`, lease nulo, `indexacoes` do job, cobertura e relatório.
- Não trate `awaiting_approval` como falha; é o terminal esperado antes da análise humana.

## 7. Pré-aprovação

Comece por `$preaprovar-indexacoes` e então roteie pelo perfil resolvido:

- `tributario/execucao_fiscal` → `$preaprovar-execucoes-fiscais`.
- `tributario/conhecimento` + natureza `Ação Restituição` ou `MS - Restituição` → `$preaprovar-restituicoes-tributarias`.
- `tributario/agravo_instrumento` → `$preaprovar-agravos-tributarios`.
- perfis administrativos → `$preaprovar-processos-administrativos`, quando disponível.
- outro perfil sem skill → protocolo comum, sem parecer `APTO`.

Publique o relatório e eventual patch proposto pelo `reviewctl save`, faça readback do control
plane e entregue IDs/hash/versão. Nunca aplique o patch nem aprove o job; essas ações aguardam
a decisão do usuário no oli-app.

## 8. Falhas e retomada

- Falha antes de LLM: pode ser retomada após causa resolvida, desde que não haja executor/lease ativo.
- Falha durante/depois de LLM: primeiro confira persistência e telemetria; não repita a fase cegamente.
- Correção determinística de staging exige autorização, filtro por job/IDs/status, snapshot before e readback.
- Recall ou delete é uma nova operação destrutiva/custosa e exige autorização explícita.
