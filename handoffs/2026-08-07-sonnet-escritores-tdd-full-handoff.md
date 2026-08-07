# Handoff — Sonnet como modelo padrão dos escritores TDD (Fase 4), nos dois tiers

**Data:** 2026-08-07. **Origem:** sessão no repo `oli-devops` (discussão sobre
alocação de modelo no `/oli-dev` — Opus/Sonnet/Fable). Este doc é autocontido —
uma sessão futura no `oli-plugins` executa sem precisar da conversa original.

**Tipo:** ciclo `/oli-dev` normal nesse repo (o plugin modifica a si mesmo —
mesmo padrão dos specs/plans já em `plugins/oli-dev/docs/superpowers/`).

## Por que este handoff existe

Hoje `model-tiers.md` fixa o escritor TDD (Fase 4) em **Opus no tier `full`** e
**Sonnet no tier `light`** — a única diferença de modelo entre os dois tiers.
Motivo do pedido: reduzir uso de Opus, sem abrir mão de rigor. A leitura da
própria doc já aponta a saída: o escritor **nunca foi um papel de julgamento**
nesse design — quem julga (staff-reviewer F2, adjudicação do conductor)
já é Opus **nos dois tiers**, e a saída do escritor é conferida por teste
(vermelho→verde), não por opinião de modelo. Logo, reservar Opus pro escritor
só no `full` não tem justificativa própria — é sobra do desenho anterior.

## LER PRIMEIRO (fonte da verdade)

1. `plugins/oli-dev/skills/dev-cycle/references/model-tiers.md` — a matriz atual
   (seção "A matriz", linha ~39-53) e o princípio "tier troca camada, não modelo"
   (linha ~5).
2. `plugins/oli-dev/skills/dev-cycle/SKILL.md` — Princípio 4 (linha ~29-37) e Fase 4
   (linha ~61) citam o modelo do escritor por tier.
3. `plugins/oli-dev/docs/superpowers/specs/2026-06-30-oli-dev-model-tiers-design.md` —
   design original: só 2 papéis são model-controláveis pelo conductor (escritores F4,
   staff-reviewer F2); `/code-review`/`/simplify`/`verify`/`/security-review` têm
   fleet/modelo próprio, fora do alcance do tier.
4. `CHANGELOG.md` — já tem `[Unreleased]` com mudanças do redesenho anterior de tier
   (staff-reviewer voltou pra Opus nos dois tiers; fix-subagents e task-reviewers
   passaram a seguir o tier). Esta mudança **soma** a esse `[Unreleased]`, não abre
   um novo. Repo ainda não tagueou depois de `oli-dev-v1.0.0` — não presumir release
   imediato.
5. `plugins/oli-dev/tests/test_references.sh` e `plugins/oli-dev/evals/evals.json` —
   travam a matriz atual como invariante testável; vão precisar de update.

## Escopo — o que muda

**Escritor TDD (Fase 4) = Sonnet no `full` e no `light`.** Deixa de ser a
diferença de modelo entre tiers.

O que **continua** diferenciando `full` de `light` depois da mudança:
- `full` roda o **task-reviewer por task** (Opus) — `light` não roda.
- Conductor, staff-reviewer (F2) e adjudicação seguem Opus nos dois tiers, sem
  mudança.
- `/code-review`, `/simplify`, `verify`, `/security-review` seguem fora do
  alcance do tier, sem mudança.

## Decisão em aberto — resolver no brainstorm/staff-review, não presumir

O **fix-subagent** (corrige quando o task-reviewer aponta erro, Fase 4) hoje
segue o tier: Opus no `full`, Sonnet no `light`. Como o task-reviewer não roda
no `light`, não está claro no design atual o que dispara um fix-subagent nesse
tier (achado de outra origem? nunca dispara?). Duas leituras possíveis:
- (a) fix-subagent é mecânico como o escritor (corrige código apontado, não
  julga) → deveria virar Sonnet nos dois tiers, junto com o escritor.
- (b) fix-subagent só existe hoje atrelado ao task-reviewer (que é Opus no
  `full`) → manter Opus no `full` por ora, sem mudar.

Este handoff **não decide isso** — é para a Fase 1 (brainstorm) ou Fase 2
(staff-reviewer) resolver com leitura do código/skill atual, não por inferência.

## Restrições de processo

- Rodar via `/oli-dev <ideia>` neste repo (não `light` — a mudança altera um
  invariante coberto por teste/eval, mesma classe de risco do redesenho
  anterior de tier).
- Fase 6 (gate) é o `tests/run_all.sh` do próprio plugin, não pytest genérico.
- CHANGELOG: adicionar ao `[Unreleased]` já existente (não criar seção nova);
  ao taguear, o bump esperado é **MINOR** (aditivo/retrocompatível — mesmo
  raciocínio do redesenho anterior, que foi v1.1.1→v1.2.0 MINOR) — mas só
  decidir o bump na hora de taguear, considerando tudo que já está acumulado
  em `[Unreleased]`.
- Não mexe em hook ID nem em `policies/ENFORCEMENT.md` — não é matéria de
  MAJOR.
