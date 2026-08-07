# Changelog — oli-plugins

Segue [Keep a Changelog](https://keepachangelog.com/) e SemVer por plugin
(ver [policies/SEMVER.md](policies/SEMVER.md)).

## oli-dev

### [Unreleased]

#### Changed

- **MAJOR — o default deixa de rodar task-reviewer por task; `full` vira o opt-in que o
  readiciona.** Antes, `full` era o tier default (task-reviewer por task incluído) e `light` era
  o opt-in enxuto. Agora o default é o enxuto: sem task-reviewer por task (Fase 4) e escritores
  TDD em Sonnet — a Fase 5 (`/code-review`) cobre o mesmo diff com contexto fresco. `full` passa a
  significar uma coisa só: readiciona a aderência-à-spec por task, para contrato/enforcement/
  superfície sensível. `light` segue aceito como alias do default, por compatibilidade.
  Classificado como **MAJOR** (`policies/SEMVER.md`: "remoção de fase/gate") porque tira o
  task-reviewer do caminho padrão. Última tag: `oli-dev-v1.0.0`.
  - Command file, `plugin.json`, README e evals atualizados (`light_tier_scope` →
    `default_tier_scope`); `references/model-tiers.md` sai, ponteiros passam a
    `references/setup-gate.md`.

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
