#!/usr/bin/env sh
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
BASE="$HERE/../skills/dev-cycle"
fail() { echo "FAIL: $1" >&2; exit 1; }

for f in references/setup-gate.md references/review-gates.md references/pre-push-gate.md \
         references/finalize.md \
         assets/pr-body-template.md assets/close-out-checklist.md; do
  [ -s "$BASE/$f" ] || fail "missing or empty: $f"
done
# Review gates reference the tier matrix AND still document the Opus conductor/adjudication
# (the honest invariant — NOT the old blanket "todos os subagentes em Opus")
grep -qi 'tier' "$BASE/references/review-gates.md" || fail "review-gates.md must reference the model tier"
grep -qi 'opus' "$BASE/references/review-gates.md" || fail "review-gates.md must document the Opus conductor/adjudication"
grep -qi 'security-review' "$BASE/references/review-gates.md" || fail "review-gates.md missing security sub-gate"
# Um caça-bug por artefato: o /simplify é condicional ao tamanho do diff. Guarda contra
# re-adicionar a camada incondicional numa edição futura.
grep -qi '150' "$BASE/references/review-gates.md" || fail "review-gates.md must state the /simplify diff threshold"
grep -qi 'MERGED' "$BASE/references/finalize.md" || fail "finalize.md must gate on MERGED state"
grep -qi 'pyproject\|package.json' "$BASE/references/pre-push-gate.md" || fail "pre-push-gate.md missing stack detection"
grep -qi 'main' "$BASE/references/setup-gate.md" || fail "setup-gate.md must require branch from main"
SK="$BASE/SKILL.md"
RG="$BASE/references/review-gates.md"
CMD="$HERE/../commands/oli-dev.md"
# Um caça-bug por artefato: o override do SDD migrou de model-tiers.md (deletado) p/ SKILL.md
grep -qi 'sem review final de branch' "$SK" || fail "SKILL.md must state the branch-review removal"
grep -qi 'override deliberado'        "$SK" || fail "SKILL.md must flag the SDD override explicitly"
# Princípio 5 — ancorado no conteúdo, nunca no número do item
grep -qi 'não presuma o que não dá pra verificar' "$SK" || fail "SKILL.md must keep principle 5 (verify, don't assume)"
# verify da F5 é incondicional — mesma linha, senão o grep não cruza linhas
grep -qiE 'verify.*sempre' "$RG" || fail "review-gates.md must state verify runs always"
# O default é enxuto — trava contra uma reescrita futura reverter em silêncio
grep -qi 'default não roda task-reviewer' "$CMD" || fail "command must state the default skips the per-task reviewer"
echo "PASS test_references"
