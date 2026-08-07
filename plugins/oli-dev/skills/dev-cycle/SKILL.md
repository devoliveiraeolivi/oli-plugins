---
name: dev-cycle
description: Use ao construir uma feature/mudança nova no ecossistema OLI — conduz o ciclo completo (worktree da main, brainstorm, review staff cético, plano, escrita TDD por subagente, review code/simplify/verify, pre-push gate, PR, finalize pós-merge), com um caça-bug por artefato e tier `full`/`light` trocando camadas de review. Invocada por `/oli-dev [light] <ideia>` e `/oli-dev finalize`.
---

# dev-cycle — maestro do ciclo de desenvolvimento OLI

## When to Use

- `/oli-dev [light] <ideia>` → ciclo completo (Fases 0–7), termina em PR aberta. Tier `full` (default) ou `light` (menos camadas de review) — ver `references/model-tiers.md`.
- `/oli-dev finalize` → só a Fase 8 (close-out + limpeza), depois que a PR foi mergeada.
- Ative também quando o usuário descreve uma feature nova e pede para "construir/implementar".

NÃO use para: hotfix trivial de 1 linha já aprovado, perguntas, ou tarefas sem código.

## Prerequisites

- Plugin **superpowers** instalado (esta skill o invoca). Se faltar, avise e pare.
- Loop principal em **Opus 5** (verificado na Fase 0).
- Repo alvo é um git repo com `main` e remoto configurado.

## Princípios de processo (gates duros — invioláveis)

1. Uma branch por ciclo, **da `main`**. Sem PRs stacked por padrão.
2. **Worktree sempre, da `main`.** Nunca trabalhar direto numa branch no dir principal.
3. **Nunca deletar branch** — nem continuar empurrando nela — sem `gh pr view <n> --json state`.
   Se a PR está `MERGED`, commits/pushes na branch viram órfãos; o hook `branch-state-guard.sh`
   bloqueia isso de forma determinística (push/commit), e a Fase 0 recusa retomar numa branch mergeada.
4. **Um caça-bug por artefato — o tier troca camada, não modelo.**
   Passe de LLM sobre o mesmo código é o custo real do ciclo; review do review rende
   concordância e churn. Então: spec → staff-reviewer (F2); diff → `/code-review` (F5).
   **Sem review final de branch na Fase 4** — a F5 cobre o mesmo diff com fleet maior
   (override deliberado do SDD; não re-adicione). O conductor é **sempre Opus 5** (Fase 0 checa),
   e todo papel de julgamento também: staff-reviewer (F2) e adjudicação, nos dois tiers.
   O `light` **só derruba camada** (sem task-reviewer por task) — nenhum papel muda de modelo
   por tier. Escritores TDD são sempre `model: "sonnet"`. `/code-review` roda fleet próprio
   (fora do tier).
   Effort alto nos reviews. Ver `references/model-tiers.md`.
5. **Não presuma o que não dá pra verificar — pergunte, se for material.** Vale em todas as fases:
   se um fato carrega o design e a fonte é memória, inferência ou "deve ser assim", pare e confirme
   com o usuário antes de escrever spec, plano ou código. Fonte verificada = arquivo:linha no repo,
   output de comando, doc do `oli-platform`, ou confirmação explícita do usuário.
   **Não trave por detalhe:** se a premissa é barata de reverter ou tem default óbvio, assuma o
   default, registre como premissa na spec e siga — pergunta só quando errar custa retrabalho.
   Caso mais comum: **banco de dados** — schema, tabelas, colunas, RPCs, policies e dados
   existentes nunca se inferem de nome de campo. E todo SQL que altera schema ou dados
   (DDL, migration, backfill) vai como bloco explícito para o usuário rodar/aprovar
   manualmente; a skill não executa SQL por conta própria.
6. **O conductor coordena — investigação e coleta de dados vão para subagentes, paralelos
   quando independentes.** O contexto do conductor é o recurso escasso do ciclo: gastá-lo lendo
   N arquivos é gastar o que decide. Antes de investigar, pergunte se dá pra despachar; antes de
   despachar 2+, se são independentes — se forem, **fan-out numa mensagem só**. Despache só sobre
   o que ninguém no ciclo leu ainda — nunca sobre artefato já coberto por um gate. O investigador
   volta com **fonte (`arquivo:linha`), não com conselho**, e é despachado com `model:`
   **explícito** (omitir herda o modelo da sessão — SDD `SKILL.md:177-179`); qual modelo, ver
   `references/model-tiers.md`. **Fica no conductor:** adjudicação **e a verificação do achado
   que a sustenta**, os gates `verify` (F5) e Fase 6, comando determinístico de uma linha, os
   artefatos que o próprio conductor vai autorar ou executar (spec da F1, plano da F3/F4), e o
   estado da própria sessão (worktree, modelo, skills disponíveis na sessão). Limite:
   `references/review-gates.md`.

## Workflow

Mantenha um todo por fase. Modo `<ideia>` = Fases 0–7; modo `finalize` = Fase 8.
Carregue o `references/*.md` da fase **quando ela começa** (progressive disclosure).

- **Fase 0 — SETUP gate** → ver `references/setup-gate.md`. Checa Opus + deps + tier (`full`/`light`) + cria worktree da main (EnterWorktree nativo preferido; fallback `using-git-worktrees`) + ponytail por tier (opcional). Resume/checkpoint: detecta spec/plano existentes e retoma da fase certa (pede confirmação antes de pular).
- **Fase 1 — BRAINSTORM** → invoca `superpowers:brainstorming`. Spec em `docs/superpowers/specs/`. Commit.
  Aplique o princípio 5: cada premissa da spec com fonte verificada ou confirmada com o usuário —
  banco (`architecture/supabase-inventory.md`) inclusive; SQL de schema/dados entra como bloco
  para aprovação manual.
- **Fase 2 — REVIEW pré-código** → ver `references/review-gates.md`. 1 `staff-reviewer` cético, **Opus nos dois tiers**. Resolve achados. Commit.
- **Fase 3 — PLANO** → invoca `superpowers:writing-plans`. Commit.
- **Fase 4 — ESCRITA** → invoca `superpowers:subagent-driven-development`; cada task em TDD. Escritores sempre em `model: "sonnet"` (nos dois tiers); task-reviewer por task só no `full`; **sem review final de branch nos dois tiers** (coberto pela Fase 5 — override deliberado do SDD). Pipeline (serial) ou Fan-out (`dispatching-parallel-agents`) conforme dependência. Checkpoint commit por task.
- **Fase 5 — REVIEW pós-código** → ver `references/review-gates.md`. `/code-review` → `/simplify` (só se diff > ~150 linhas) → `verify` (sempre); sub-gate condicional `/security-review` se o diff toca superfície sensível. Idêntica nos dois tiers (conductor adjudica em Opus; `/code-review` tem fleet próprio).
- **Fase 6 — PRE-PUSH gate** → ver `references/pre-push-gate.md`. Prefere `scripts/check.sh --fast` do repo; senão fallback ruff+mypy (ou lint+test+build p/ node). Bloqueia se falhar, com evidência.
- **Fase 7 — PUSH + PR** → `commit-commands:commit-push-pr`. Base = `main`. O push leva o prefixo `OLI_DEV_GATE_OK=1` (gate já rodou na Fase 6 → hook não re-roda). Usa `assets/pr-body-template.md`. Termina aqui.
- **Fase 8 — FINALIZE** (`/oli-dev finalize`) → ver `references/finalize.md`. Verifica `MERGED`, limpa worktree+branch, close-out (`assets/close-out-checklist.md`).

## Verification

Antes de declarar qualquer fase concluída, confirme com **evidência** (output real, nunca alegação):
- Fase 0: worktree existe e está na branch certa (`git worktree list`, `git branch --show-current`);
  se ponytail presente e tier=`light`, o nível foi confirmado com output colado.
- Fase 1: toda afirmação material da spec tem fonte (arquivo:linha, output, ou confirmação do
  usuário) — o resto vai listado como premissa assumida; SQL de schema/dados aparece como bloco
  para aprovação manual, não como passo automático.
- Fase 2/5: o staff-reviewer foi despachado em Opus, o conductor adjudicou em Opus, e os achados materiais foram resolvidos. Se o `/simplify` foi pulado, o motivo é o tamanho do diff — cole o `git diff --stat`.
- Fase 6: os comandos do gate passaram (cole o output).
- Fase 7: a PR foi criada (URL).
- Fase 8: `gh pr view --json state` == `MERGED` antes de qualquer delete; worktree removido; close-out feito.
