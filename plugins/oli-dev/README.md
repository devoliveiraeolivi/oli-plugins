# oli-dev

Maestro do ciclo de desenvolvimento OLI. Um plugin fino que **conduz** as fases do ciclo
encadeando skills do **superpowers** com gates opinativos.

## Requisitos
- **superpowers** instalado (este plugin invoca suas skills). Sem ele, a skill avisa e para.
- **Loop principal em Opus 5.** Uma skill é markdown e não troca o modelo da sessão; a Fase 0
  verifica e bloqueia até você confirmar. Todo papel de **julgamento** roda em Opus nos dois tiers
  (conductor, staff-reviewer, adjudicação); o **tier** troca **camadas de review** — e só os
  escritores TDD trocam de modelo no `light`.

## Instalação
```
/plugin marketplace add devoliveiraeolivi/oli-plugins
/plugin install oli-dev
```

## Uso
- `/oli-dev <ideia da feature>` → ciclo completo (Fases 0–7), termina em PR aberta. Tier `full` (default).
- `/oli-dev light <ideia>` → tier `light`: **menos camadas** (sem task-reviewer por task) + escritores TDD
  em **Sonnet 5**. Julgamento segue em Opus; `/code-review`/`verify`/pre-push inalterados.
  Ver `skills/dev-cycle/references/model-tiers.md`.
  Com o plugin **ponytail** presente, o tier light também ativa `/ponytail lite` na Fase 0 (opcional, fail-open).
- `/oli-dev finalize` → close-out + limpeza pós-merge (Fase 8), depois que a PR foi mergeada.

## O que ele faz
worktree da main → brainstorm → review staff cético → plano → escrita TDD por subagente
→ code-review/simplify/verify (+security-review condicional) → pre-push gate → PR → finalize.

**Um caça-bug por artefato:** spec → staff-reviewer (F2), diff → `/code-review` (F5). Não há review
final de branch na F4 (a F5 cobre o mesmo diff com fleet maior) e o `/simplify` só roda em diff
> ~150 linhas. Passes de LLM numa mudança de 4 tasks: `full` ~10 · `light` ~6.

## Gates duros (invioláveis)
1. Uma branch por ciclo, da `main`, sem stacked. 2. Worktree sempre, da `main`.
3. Nunca deletar branch sem `gh pr view --json state == MERGED`. 4. Conductor e todo papel de
julgamento sempre Opus; o tier mexe em camada, não em modelo de review.

## Hook de pre-push
`hooks/pre-push-gate.sh` é um backstop PreToolUse: em `git push`, detecta a stack
(`pyproject.toml`→python, `package.json`→node) e bloqueia (exit 2) se lint/test/typecheck falhar.
Stack desconhecida ou ferramenta ausente não bloqueia.

## Testes do plugin
`sh plugins/oli-dev/tests/run_all.sh` → `ALL GREEN`.
