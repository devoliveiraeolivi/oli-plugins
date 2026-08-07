# Changelog — oli-plugins

Segue [Keep a Changelog](https://keepachangelog.com/) e SemVer por plugin
(ver [policies/SEMVER.md](policies/SEMVER.md)).

## oli-dev

### [Unreleased]

#### Changed

- **Opus julga, Sonnet produz e coleta.** Duas mudanças com a mesma raiz:
  - **Escritores TDD (F4) passam a Sonnet nos dois tiers** — deixam de ser a única
    diferença de modelo entre `full` e `light`. O escritor nunca foi papel de julgamento:
    a saída é conferida por execução de teste, não por opinião. Efeito: **o tier deixa de
    trocar modelo** — só troca camada (task-reviewer roda ou não). ⚠️ Premissa de design,
    não medição; reverter custa uma célula da matriz.
  - **Linha de fix-subagents corrigida nas duas colunas.** Não era papel com modelo
    próprio: o SDD retoma o próprio escritor (`subagent-driven-development/SKILL.md:322`)
    e escala ≥1 tier acima na rodada 4 (`:174-175`). No `light` nada disparava o loop (sem
    task-reviewer) — a célula era inalcançável desde o refactor anterior, que separou a
    linha e não propagou. Linha nova para a rota `BLOCKED` (`:244-250`), independente de
    review e válida nos dois tiers.
  - **Princípio 6 novo: o conductor coordena.** Investigação e coleta de dados vão para
    subagentes, paralelos quando independentes, com `model:` explícito (omitir herda o
    modelo da sessão e vaza Opus). Ficam no conductor: adjudicação e a verificação que a
    sustenta, os gates `verify` (F5) e Fase 6, comando determinístico, os artefatos que o
    próprio conductor autora, e o estado da sessão. Limite anti-empilhamento no
    `review-gates.md`: investigação paralela sobre artefatos que nenhum gate cobriu ≠
    segundo reviewer sobre o mesmo diff.
  - **Testes travam a condição, não a prosa:** nenhuma linha da matriz pode ser Opus no
    `full` e Sonnet no `light`; a cláusula do Princípio 6 é ancorada pelos dois gates que
    ela protege. Cada assert foi validado por sonda negativa (apagar a claim → assert
    falha), depois de três tentativas com âncora fraca.
  - Eval novo: `investigacao_disfarcada_de_review`. `light_tier_scope` reescrito.
  - `setup-gate.md` não afirma mais que `.claude/worktrees/` está no `.gitignore` — o repo
    não tem `.gitignore` (follow-up separado).
  - ⚠️ **Medição do próprio ciclo:** esta mudança de ~80 linhas de doc custou 22+ despachos
    de subagente e 5 rodadas de fix. A conta publicada abaixo (`full` ~10) não inclui
    rodadas de fix, re-reviews nem investigação — está errada por 2-3×. Ver
    `handoffs/2026-08-07-oli-dev-peso-do-ciclo-handoff.md`.

- **Um caça-bug por artefato — o tier passa a trocar camadas de review, não modelo
  de julgamento.** O custo/latência do ciclo vinha do número de passes de LLM sobre
  o mesmo código (~15 numa mudança de 4 tasks, nos dois tiers), não do modelo de cada
  passe. Mudanças:
  - **Base (`full` e `light`): sem review final de branch na Fase 4** — a Fase 5 roda
    `/code-review` sobre o mesmo diff com fleet maior. Era o mesmo trabalho duas vezes.
    Override deliberado do SDD, marcado como tal para não voltar por deferência.
  - **Base: `/simplify` condicional** ao diff passar de ~150 linhas alteradas; em diff
    pequeno rendia churn cosmético + adjudicação.
  - **`light` derruba camada** (sem task-reviewer por task) em vez de rebaixar modelo.
    Único downgrade que resta: escritores TDD → Sonnet (maior volume de token, menor
    exigência de julgamento, saída verificada por execução de teste).
  - **Staff-reviewer (F2) volta pra Opus nos dois tiers.** Economizar modelo em gate de
    review produz palpite com selo de "revisado" — o que `review-gates.md` já chamava de
    pior que não ter reviewer.
  - Intocados: Fase 6 (lint/test) e `verify` — os únicos gates que produzem verdade
    objetiva e custam zero token.
  - Passes de LLM numa mudança de 4 tasks: **`full` ~10 · `light` ~6** (era ~15/~15).
  - Evals novos: `redundant_branch_review`, `simplify_on_tiny_diff`.

- **Tier `light` explicita TODOS os papéis despachados da Fase 4**
  (`references/model-tiers.md` + SKILL.md): além dos escritores TDD, os
  **task-reviewers** e **fix-subagents** do subagent-driven-development também
  seguem o tier (`light` = Sonnet) — fecha a ambiguidade entre o SKILL.md
  ("subagentes", plural) e a matriz (só "escritores"). ~~Exceção nova e
  explícita: o review final de branch é sempre Opus nos dois tiers~~ —
  **superseda pela entrada acima**: o review final de branch deixou de rodar
  (a Fase 5 cobre o mesmo diff), então não há modelo a fixar. Haiku fica
  documentado como fora do tier por decisão (custo de turnos em trabalho
  multi-step), não por limitação.

### [oli-dev-v1.0.0] — 2026-07-04

Primeira release do plugin como projeto independente, extraído do `oli-devops`
com histórico preservado (`git filter-repo`). Sem mudança de comportamento em
relação ao último estado no `oli-devops`.

- Maestro do ciclo de desenvolvimento OLI: worktree → brainstorm → review staff
  cético → plano → escrita TDD por subagente (tier full/light) → code-review/
  simplify/verify (+security-review condicional) → pre-push gate → PR → finalize.
- Instalação via `/plugin marketplace add devoliveiraeolivi/oli-plugins`.
