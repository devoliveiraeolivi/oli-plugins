# Fase 0 — SETUP gate

**Objetivo:** começar num worktree limpo criado da `main`, com o tier resolvido, sem risco de
escrever numa branch já mergeada.

## Invariantes (não negociáveis)

- **Opus 5 no loop principal.** Se não estiver, **bloqueie** e peça `/model` (ou `/fast` no
  Opus). A skill não troca modelo e não prossegue sem confirmação.
- **Worktree criado da `main`** — nunca de outra feature branch, nunca pasta irmã do repo.
  `git fetch` e `main` atualizada antes. Prefira o **EnterWorktree nativo** (cria em
  `.claude/worktrees/`, já no `.gitignore`); sem ele, `superpowers:using-git-worktrees`.
- **Guard de branch ao retomar.** Cheque as duas coisas: estamos num **worktree linkado**
  (`git rev-parse --git-dir` ≠ `--git-common-dir`), e a PR da branch **não** está MERGED
  (`gh pr view <branch> --json state`). Branch MERGED → **barre** e crie uma branch nova da
  `main`; commits ali viram órfãos (aconteceu na PR #4 → recovery na #5). No checkout principal
  sem worktree → volte para a `main` e crie o worktree. A enforcement determinística vive em
  `hooks/branch-state-guard.sh`.
- **Deps do superpowers presentes:** brainstorming, writing-plans, subagent-driven-development,
  test-driven-development, requesting-code-review, finishing-a-development-branch,
  verification-before-completion. Faltou → avise e pare. `using-git-worktrees` só é exigida no
  fallback, quando não há EnterWorktree nativo.

## Resume / checkpoint

Detecte artefatos: spec + plano → Fase 4; só spec → Fase 2/3; nada → Fase 1. Anuncie de onde
retoma e confirme **antes** de pular fase.

**Plano sem cabeçalho de tier → assuma `full`** e anuncie que assumiu. Perder o tier num resume
degrada para o lado mais seguro, nunca para o mais arriscado. Por isso a Fase 3 grava o tier.

## Tier — o que ele muda, e só isso

O default é enxuto. `full` soma **uma** camada: o task-reviewer por task, em Opus. Todo o resto
é idêntico nos dois — conductor, staff-reviewer (F2) e adjudicação em **Opus**; escritores TDD
em **Sonnet**; `/code-review`, `verify` e o pre-push gate inalterados; e nenhum review final de
branch na Fase 4, porque a Fase 5 cobre o mesmo diff.

`light` é aceito como **alias do default**, e anunciado como tal — sem ele, uma ideia que comece
com a palavra "light" perderia a primeira palavra no parsing.

**Por que o default dispensa o task-reviewer.** O SDD diz *"never skip the task review"*;
dispensá-lo é override deliberado, e a rede que sobra é explícita: a task roda em **TDD**
(vermelho→verde é verificação por execução, não por opinião), o `/code-review` da F5 lê o diff
inteiro com contexto fresco, e a F6 roda lint+test de verdade. O que se perde é a **aderência à
spec por task** — e é para isso que o `full` existe. **Recomende `full`** quando a mudança toca
contrato, enforcement ou superfície sensível (auth, secrets, SQL/RPC, rede, cripto).

**Piso de modelo: Sonnet.** Modelos mais baratos gastam 2–3× mais turnos em trabalho multi-step,
e TDD é multi-step por natureza. Revisite só com medição.
