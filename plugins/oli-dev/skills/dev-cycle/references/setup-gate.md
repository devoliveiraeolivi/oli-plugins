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

O default é enxuto. `full` soma **uma** camada: o task-reviewer por task, em Opus. **Nada mais
muda** — nenhum papel, nenhum modelo, nenhum gate. Escritores TDD em **Sonnet** nos dois.

`light` é aceito como **alias do default**, por compatibilidade. Cuidado: aceitar `light` como
token de tier é justamente o que faz `/oli-dev light mode toggle` virar ideia `"mode toggle"`.
Por isso, **ecoe a interpretação** — *"tier=X, ideia='…'"* — sempre que a 1ª palavra for `light`
ou `full`. Truncar em silêncio é o modo de falha; o eco o torna visível.

O SDD diz *"never skip the task review"*; dispensá-lo no default é **override deliberado**. A
rede que sobra: TDD, `/code-review` (F5), F6. O `full` recupera a aderência-à-spec por task.

**Piso de segurança (gate, não sugestão).** Mudança que toca contrato, enforcement ou superfície
sensível (auth, secrets, SQL/RPC, rede, cripto): recomende `full` e **peça ack explícito** antes
de seguir no default. Com o default enxuto, ninguém digita nada para cair no caminho sem
task-reviewer — sem o ack, uma mudança de auth roda sem aderência-à-spec por task e em silêncio.

**Piso de modelo: Sonnet.** Mais barato gasta 2–3× mais turnos em multi-step, e TDD é multi-step.
