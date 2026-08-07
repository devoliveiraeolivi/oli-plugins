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
# presença da afirmação nova (SKILL.md:62, Fase 4). 'nos dois tiers' sozinho era largo demais —
# também casa SKILL.md:34,60,63 (claims sem relação com o modelo do escritor); 'Escritores sempre
# em' é exclusivo da linha 62 e amarrado à claim (confirmado por sonda, ver relatório da task).
grep -qF 'Escritores sempre em' "$SK" || fail "SKILL.md must state the writer model holds in both tiers"
# Princípio 6 — o conductor coordena; investigação/coleta vão para subagentes.
# Âncora ESTRUTURAL (o item numerado existe), não frase: sobrevive a reescrita do corpo e
# falha se alguém deletar o princípio. Mas só isso protege contra DELEÇÃO, não contra reescrita
# do corpo (achado do reviewer: trocar o corpo por "6. Use tabs, nunca espaços." passava verde) —
# por isso o assert de frase abaixo, amarrado à cláusula que faz o trabalho.
grep -qE '^6\. ' "$SK" || fail "SKILL.md must have Princípio 6 (o conductor coordena)"
# Assert de frase: trava a cláusula "o que fica no conductor" (adjudicação, verify/F6, artefatos
# que ele mesmo autora, estado da sessão) — sem ela o princípio autoriza fan-out mas não diz onde
# para. Única no SKILL.md (confirmado por `grep -cF`, ver relatório da task), sonda negativa feita.
grep -qF 'Fica no conductor' "$SK" || fail "SKILL.md Princípio 6 must keep the conductor-retains clause"
# Achado da rodada 2 (re-review): 'Fica no conductor' trava só a ETIQUETA da cláusula — o
# conteúdo depois dos dois-pontos podia virar "nada em especial, tudo pode ser delegado." e a
# suíte continuava verde. Assert amarrado ao conteúdo mais load-bearing dentro da cláusula: a
# menção a Fase 6, o gate que model-tiers.md diz que NUNCA cai em nenhum tier — se a cláusula for
# esvaziada, essa menção some junto. Sem backtick no padrão (evita SC2016 do shellcheck: backtick
# em single-quote lê como tentativa de expansão). Única no SKILL.md (`grep -c` = 1, ver
# relatório), sonda de evisceração feita.
grep -qF 'e Fase 6, comando determinístico de uma linha' "$SK" \
  || fail "SKILL.md Princípio 6 conductor-retains clause must still name the two never-skip gates"
# O limite anti-empilhamento mora no review-gates.md e precisa nomear investigação.
grep -qi 'investiga' "$BASE/references/review-gates.md" \
  || fail "review-gates.md must separate parallel investigation from stacked review"
# A matriz é a fonte única do modelo do investigador (o princípio aponta pra cá). Amarrado à
# LINHA da matriz com Sonnet — não só à palavra "investiga" solta em qualquer lugar do arquivo.
grep -qE '^\|.*[Ii]nvestiga.*\|.*Sonnet' "$MT" \
  || fail "model-tiers.md must state the investigation agent model"
echo "PASS test_references"
