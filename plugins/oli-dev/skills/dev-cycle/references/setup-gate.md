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

Um ciclo tem **um** artefato: a spec em `docs/superpowers/specs/`, com o plano na seção
`## Plano`. Detecte: spec **com** `## Plano` → Fase 4; spec **sem** `## Plano` → Fase 2/3; nada
→ Fase 1. Ciclo antigo com arquivo separado em `docs/superpowers/plans/` conta como spec+plano
→ Fase 4. Anuncie de onde retoma e confirme **antes** de pular fase.

**Spec sem cabeçalho de tier → assuma `full`** e anuncie que assumiu. Perder o tier num resume
degrada para o lado mais seguro, nunca para o mais arriscado. Por isso a Fase 1 grava o tier.

## Tier — o que ele muda, e só isso

O default é enxuto. `full` soma **duas** camadas de review, ambas em Opus: o staff-reviewer da
spec (Fase 2) e o task-reviewer por task (Fase 4). **Nada mais muda** — nenhum outro papel,
nenhum modelo, nenhum outro gate. Escritores TDD em **Sonnet** nos dois; conductor e adjudicação
em **Opus** nos dois.

`light` é aceito como **alias do default**, por compatibilidade. Cuidado: aceitar `light` como
token de tier é justamente o que faz `/oli-dev light mode toggle` virar ideia `"mode toggle"`.
Por isso, **ecoe a interpretação** — *"tier=X, ideia='…'"* — sempre que a 1ª palavra for `light`
ou `full`. Truncar em silêncio é o modo de falha; o eco o torna visível.

O SDD diz *"never skip the task review"*; dispensá-lo no default é **override deliberado** — o
mesmo vale para o staff-reviewer da Fase 2. A rede que sobra no default: TDD, `/code-review`
(F5), `verify` e o pre-push (F6) — toda ela sobre código que já existe. O `full` recupera as duas
camadas de julgamento sobre prosa.

**Piso de segurança (gate, não sugestão).** Mudança que toca contrato, enforcement ou superfície
sensível (auth, secrets, SQL/RPC, rede, cripto): recomende `full` e **peça ack explícito** antes
de seguir no default. Com o default enxuto, ninguém digita nada para cair no caminho sem
task-reviewer **nem sem review de spec** — sem o ack, uma mudança de auth roda sem nenhuma das
duas camadas e em silêncio.

**Piso de modelo: Sonnet.** Mais barato gasta 2–3× mais turnos em multi-step, e TDD é multi-step.
