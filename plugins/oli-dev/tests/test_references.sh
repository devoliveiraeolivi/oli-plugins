#!/usr/bin/env sh
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
BASE="$HERE/../skills/dev-cycle"
ROOT="$HERE/.."
fail() { echo "FAIL: $1" >&2; exit 1; }

for f in references/setup-gate.md references/review-gates.md references/pre-push-gate.md \
         references/finalize.md references/model-tiers.md \
         assets/pr-body-template.md assets/close-out-checklist.md; do
  [ -s "$BASE/$f" ] || fail "missing or empty: $f"
done
# Model tiers (full/light) documented as the single source of truth
MT="$BASE/references/model-tiers.md"
grep -qiF 'full'  "$MT" || fail "model-tiers.md must document the full tier"
grep -qiF 'light' "$MT" || fail "model-tiers.md must document the light tier"
grep -qi  'conductor' "$MT" || fail "model-tiers.md must state the conductor role"
grep -qi  'sonnet' "$MT" || fail "model-tiers.md must mention Sonnet"
grep -qi  'opus'   "$MT" || fail "model-tiers.md must mention Opus"
# Item 1 — nenhum papel troca de modelo por tier. Trava a CONDIÇÃO, não uma frase de prosa:
# nenhuma linha da matriz pode ser Opus na coluna `full` e Sonnet na coluna `light`.
# Sobrevive a reescrita do texto; falha se alguém reintroduzir um split de tier no escritor.
# \**Opus\** e [^|]* cobrem negrito e sufixo (ex.: "**Opus**", "Opus (`model: \"opus\"`)") —
# a forma nua "Opus" sem essas variações escapava do regex original.
if grep -qE '^\|.*\| *\**Opus\**[^|]*\|[^|]*Sonnet' "$MT"; then
  fail "model-tiers.md matrix still has a row that is Opus in full and Sonnet in light"
fi
# Review gates reference the tier matrix AND still document the Opus conductor/adjudication
# (the honest invariant — NOT the old blanket "todos os subagentes em Opus")
grep -qi 'tier' "$BASE/references/review-gates.md" || fail "review-gates.md must reference the model tier"
grep -qi 'opus' "$BASE/references/review-gates.md" || fail "review-gates.md must document the Opus conductor/adjudication"
grep -qi 'security-review' "$BASE/references/review-gates.md" || fail "review-gates.md missing security sub-gate"
# Um caça-bug por artefato: o review final de branch da F4 NÃO roda (a F5 cobre o mesmo diff),
# e o /simplify é condicional ao tamanho do diff. Guarda contra re-adicionar a camada por
# deferência ao SDD numa edição futura.
grep -qi 'review final de branch' "$MT" || fail "model-tiers.md must state the branch-review removal"
grep -qi 'override deliberado' "$MT" || fail "model-tiers.md must flag the SDD override explicitly"
grep -qi '150' "$MT" || fail "model-tiers.md must state the /simplify diff threshold"
grep -qi '150' "$BASE/references/review-gates.md" || fail "review-gates.md must state the /simplify diff threshold"
grep -qi 'MERGED' "$BASE/references/finalize.md" || fail "finalize.md must gate on MERGED state"
grep -qi 'pyproject\|package.json' "$BASE/references/pre-push-gate.md" || fail "pre-push-gate.md missing stack detection"
grep -qi 'main' "$BASE/references/setup-gate.md" || fail "setup-gate.md must require branch from main"
# Passo do ponytail por tier (opcional, fail-open) documentado na Fase 0
grep -qi 'ponytail' "$BASE/references/setup-gate.md" || fail "setup-gate.md must document the ponytail-by-tier step"
# Item 1 propagado — nenhum doc pode atribuir o modelo do escritor ao tier.
# São asserts de frase porque aqui não há condição estrutural como a da matriz; cada frase
# escolhida é uma AFIRMAÇÃO (claim), não estilo.
SK="$BASE/SKILL.md"
# 'faz .*downgrade de modelo' e 'downgrade de modelo:' pegam a CONSTRUÇÃO falsa (o `light` FAZ um
# downgrade). Só 'downgrade de modelo' era largo demais: model-tiers.md:8 usa o substantivo de
# forma legítima ("downgrade de modelo num gate de review economiza no lugar errado") e um SKILL.md
# que citasse esse racional geraria falso positivo.
if grep -qE 'faz .*downgrade de modelo|downgrade de modelo:' "$SK"; then
  fail "SKILL.md still frames the writer model as a tier downgrade"
fi
if grep -qE 'full.=opus' "$SK"; then
  fail "SKILL.md still pins TDD writers to Opus in the full tier"
fi
if grep -q 'trocam de modelo no' "$ROOT/README.md"; then
  fail "README.md still claims the writer model changes with the tier"
fi
if grep -q 'escritores TDD vão pra' "$ROOT/commands/oli-dev.md"; then
  fail "commands/oli-dev.md still frames the writer model as light-specific"
fi
if grep -q 'Só os escritores TDD' "$ROOT/evals/evals.json"; then
  fail "evals.json light_tier_scope still implies the downgrade is exclusive to light"
fi
# Lado positivo: a ausência das frases acima não prova que a afirmação certa foi escrita — alguém
# poderia apagar a frase inteira do escritor e a suíte ficaria verde do mesmo jeito. Trava a
# presença da afirmação nova (SKILL.md:62, Fase 4).
grep -q 'nos dois tiers' "$SK" || fail "SKILL.md must state the writer model holds in both tiers"
echo "PASS test_references"
