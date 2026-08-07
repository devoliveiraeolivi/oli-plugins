---
name: dev-cycle
description: Use ao construir uma feature/mudança nova no ecossistema OLI — conduz o ciclo completo (worktree da main, brainstorm, review staff cético, plano, escrita TDD por subagente, review code/simplify/verify, pre-push gate, PR, finalize pós-merge), com um caça-bug por artefato. Invocada por `/oli-dev <ideia>` (default enxuto), `/oli-dev full <ideia>` (soma o task-reviewer por task) e `/oli-dev finalize`.
---

# dev-cycle — maestro do ciclo de desenvolvimento OLI

## When to Use

- `/oli-dev <ideia>` → ciclo completo (Fases 0–7), termina em PR aberta. Default enxuto.
- `/oli-dev full <ideia>` → soma o task-reviewer por task (`references/setup-gate.md`).
- `/oli-dev finalize` → só a Fase 8 (close-out + limpeza), depois da PR mergeada.
- Ative também quando o usuário descreve uma feature nova e pede para construir/implementar.

NÃO use para: hotfix trivial de 1 linha já aprovado, perguntas, ou tarefas sem código.

## Prerequisites

- Plugin **superpowers** instalado (esta skill o invoca); repo alvo com `main` e remoto.
- Loop principal em **Opus 5**. A Fase 0 verifica os dois e para se faltar.

## Princípios de processo (gates duros — invioláveis)

1. Uma branch por ciclo, **da `main`**. Sem PRs stacked por padrão.
2. **Worktree sempre, da `main`.** Nunca trabalhar direto numa branch no dir principal.
3. **Nunca deletar branch** — nem seguir empurrando nela — sem `gh pr view <n> --json state`.
   PR `MERGED` → commits ali viram órfãos. O hook `branch-state-guard.sh` bloqueia; a Fase 0
   recusa retomar numa branch mergeada.
4. **Um caça-bug por artefato.** Passe de LLM sobre o mesmo código é o custo real do ciclo, e
   review do review rende concordância e churn. Spec → staff-reviewer (F2); diff →
   `/code-review` (F5). **Sem review final de branch na Fase 4** — a F5 cobre o mesmo diff
   (**override deliberado** do SDD; não re-adicione por deferência à skill invocada). Papel de
   julgamento roda em **Opus**: conductor, staff-reviewer, adjudicação. Escritores TDD em Sonnet.
5. **Não presuma o que não dá pra verificar — pergunte, se for material.** Fato que carrega o
   design e vem de memória ou inferência: pare e confirme. Fonte verificada = arquivo:linha,
   output de comando, doc do `oli-platform`, ou o usuário. Premissa barata de reverter: assuma,
   registre na spec e siga. **Banco nunca se infere** — schema, tabelas, RPCs e policies se
   checam; e todo SQL de schema ou dados vai como bloco para o usuário rodar, não executado aqui.
6. **O conductor coordena.** Investigação, coleta e teste vão para subagentes — paralelos quando
   independentes. Exceção: gate cuja evidência é o output em si (Fase 6, `verify`) o conductor
   roda e cola — evidência de primeira mão não se delega.

## Workflow

Um todo por fase. Modo `<ideia>` = Fases 0–7; modo `finalize` = Fase 8. Carregue o
`references/*.md` da fase **quando ela começa** (progressive disclosure).

- **Fase 0 — SETUP** → `references/setup-gate.md`. Opus, deps, tier, worktree da `main`, resume.
- **Fase 1 — BRAINSTORM** → `superpowers:brainstorming`. Spec em `docs/superpowers/specs/`, com
  o Princípio 5 valendo em cada premissa material. Commit.
- **Fase 2 — REVIEW pré-código** → `references/review-gates.md`. Commit.
- **Fase 3 — PLANO** → `superpowers:writing-plans`. **Grave o tier no cabeçalho do plano** — o
  resume da Fase 0 depende disso. Commit.
- **Fase 4 — ESCRITA** → `superpowers:subagent-driven-development`; cada task em TDD, escritores
  com `model: "sonnet"`. Task-reviewer por task só no `full`. Checkpoint commit por task.
- **Fase 5 — REVIEW pós-código** → `references/review-gates.md`.
- **Fase 6 — PRE-PUSH gate** → `references/pre-push-gate.md`. Bloqueia se falhar, com evidência.
- **Fase 7 — PUSH + PR** → `commit-commands:commit-push-pr`. Base = `main`; o push leva o prefixo
  `OLI_DEV_GATE_OK=1` (o gate já rodou na F6). Usa `assets/pr-body-template.md`. Termina aqui.
- **Fase 8 — FINALIZE** (`/oli-dev finalize`) → `references/finalize.md`.

## Verification

**Evidência é output real, nunca alegação.** Fase não fecha com "rodei e passou" — fecha com o
que o comando imprimiu, colado. O que não deu pra verificar entra rotulado `⚠️ não verificado`:
não vira afirmação, e não vira silêncio. Detalhe em `references/review-gates.md`.
