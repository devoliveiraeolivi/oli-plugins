# Changelog — oli-plugins

Segue [Keep a Changelog](https://keepachangelog.com/) e SemVer por plugin
(ver [policies/SEMVER.md](policies/SEMVER.md)).

## oli-dev

### [Unreleased]

#### Changed

- **Tier `light` explicita TODOS os papéis despachados da Fase 4**
  (`references/model-tiers.md` + SKILL.md): além dos escritores TDD, os
  **task-reviewers** e **fix-subagents** do subagent-driven-development também
  seguem o tier (`light` = Sonnet) — fecha a ambiguidade entre o SKILL.md
  ("subagentes", plural) e a matriz (só "escritores"). **Exceção nova e
  explícita: o review final de branch é sempre Opus** nos dois tiers (última
  rede antes da Fase 5; guidance do SDD manda o review de branch para o modelo
  mais capaz). Haiku fica documentado como fora do tier por decisão (custo de
  turnos em trabalho multi-step), não por limitação.

### [oli-dev-v1.0.0] — 2026-07-04

Primeira release do plugin como projeto independente, extraído do `oli-devops`
com histórico preservado (`git filter-repo`). Sem mudança de comportamento em
relação ao último estado no `oli-devops`.

- Maestro do ciclo de desenvolvimento OLI: worktree → brainstorm → review staff
  cético → plano → escrita TDD por subagente (tier full/light) → code-review/
  simplify/verify (+security-review condicional) → pre-push gate → PR → finalize.
- Instalação via `/plugin marketplace add devoliveiraeolivi/oli-plugins`.
