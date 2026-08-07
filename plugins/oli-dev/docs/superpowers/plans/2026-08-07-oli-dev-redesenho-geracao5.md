# Redesenho do `/oli-dev` para a geração 5 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Tier do ciclo:** `light` (escritores TDD em Sonnet; sem task-reviewer por task).
**Spec:** `docs/superpowers/specs/2026-08-07-oli-dev-redesenho-geracao5-design.md`

**Goal:** Remover da skill `dev-cycle` o roteiro que substitui julgamento, preservando todo
gate que impede perda de trabalho, e consertar os 3 bugs que continuam na `main`.

**Architecture:** Três tasks. A Task 1 mexe só na suíte de testes e no `.gitignore`, e
termina **RED de propósito** — ela define o alvo. As Tasks 2 e 3 fecham o RED em conjuntos
de arquivos **disjuntos** (skill vs. periferia), então podem rodar em paralelo. Nenhuma das
três toca `hooks/`, `pre-push-gate.md` ou `finalize.md`.

**Tech Stack:** Markdown + `sh` POSIX (a suíte roda em `dash` e usa `grep`/`sed` GNU-compat).

## Global Constraints

- **Alvo duro:** `SKILL.md` + `references/*.md` ≤ **206 linhas** somadas (hoje 343, −40%).
  Verificar com `wc -l`. A projeção de ~189 é aspiração, não alvo.
- **`plugins/oli-dev/tests/run_all.sh` verde** ao fim da Task 3.
- **Idioma: português.** Nome de comando, flag e termo técnico consagrado em inglês.
- **Linha ≤ 100 colunas** nos arquivos de markdown da skill (convenção do repo).
- **Regra de assert (não negociável):** todo assert de conteúdo novo precisa de **sonda
  negativa** — copiar o arquivo para fora do repo, apagar a claim, rodar o assert e
  confirmar que **falha**. Assert sem sonda negativa não conta como feito.
- **Não tocar:** `plugins/oli-dev/hooks/`, `references/pre-push-gate.md`,
  `references/finalize.md`, `policies/SEMVER.md`, `CHANGELOG.md:33` e
  `docs/superpowers/plans/` antigos (registro histórico).
- **Nunca citar a escalada de rodada 4-5 do SDD sem o teto de 5 junto.** Foi assim que a
  célula morta original nasceu (spec D6.1).

---

### Task 1: Suíte de testes redefinida + `.gitignore`

Termina **RED**. É o objetivo: os asserts novos descrevem prosa que ainda não existe.

**Files:**
- Modify: `plugins/oli-dev/tests/test_references.sh`
- Modify: `plugins/oli-dev/tests/test_skill_structure.sh:19`
- Create: `.gitignore` (raiz do repo)

**Interfaces:**
- Consumes: nada.
- Produces: os asserts que as Tasks 2 e 3 precisam satisfazer. As âncoras de texto abaixo
  são **contrato literal** — as Tasks 2 e 3 escrevem prosa que casa com elas.

- [ ] **Step 1: Remover os asserts amarrados ao `model-tiers.md`**

Em `plugins/oli-dev/tests/test_references.sh`:

Na linha 8, tirar `references/model-tiers.md` do loop de existência. O loop passa a ser:

```sh
for f in references/setup-gate.md references/review-gates.md references/pre-push-gate.md \
         references/finalize.md \
         assets/pr-body-template.md assets/close-out-checklist.md; do
  [ -s "$BASE/$f" ] || fail "missing or empty: $f"
done
```

Apagar as linhas 12-18 inteiras (o bloco `MT=` e os 5 asserts contra ele) e as linhas 27-29
(os 3 asserts `"$MT"` de branch-review, override e `150`).

Apagar também a linha 35 e seu comentário (linha 34):

```sh
# Passo do ponytail por tier (opcional, fail-open) documentado na Fase 0
grep -qi 'ponytail' "$BASE/references/setup-gate.md" || fail "setup-gate.md must document the ponytail-by-tier step"
```

A spec D2.2 remove o passo do ponytail; o assert trava texto que vai deixar de existir.

- [ ] **Step 2: Adicionar os 5 asserts novos**

Ainda em `test_references.sh`, antes do `echo "PASS test_references"`:

```sh
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
# O default é enxuto (spec D2) — trava contra uma reescrita futura reverter em silêncio
grep -qi 'default não roda task-reviewer' "$CMD" || fail "command must state the default skips the per-task reviewer"
```

- [ ] **Step 3: Tirar `model-tiers` do loop de referências do `test_skill_structure.sh`**

Linha 19, que hoje é:

```sh
for r in setup-gate review-gates pre-push-gate finalize model-tiers; do
```

passa a:

```sh
for r in setup-gate review-gates pre-push-gate finalize; do
```

- [ ] **Step 4: Criar o `.gitignore` na raiz** (spec D6.2 — o bug #2)

`setup-gate.md:13` afirma que `.claude/worktrees/` está "já no `.gitignore`". Não há
`.gitignore` no repo (`git ls-files | grep -c gitignore` → `0`). Conserto na raiz:

```
.claude/worktrees/
```

Só isso. **Não** ignorar `.claude/` inteiro — o diretório carrega config que pode vir a ser
versionada; ignorar tudo esconderia isso sem querer.

- [ ] **Step 5: Rodar a suíte e confirmar que falha nos lugares certos**

Run: `sh plugins/oli-dev/tests/run_all.sh`

Expected: **FAIL**, e os 3 primeiros asserts novos **passam** (o conteúdo já existe hoje em
`SKILL.md:32-33` e `:38`). Os que devem falhar agora:

```
FAIL: review-gates.md must state verify runs always
```

(hoje `verify` e `Sempre` estão em linhas separadas — `review-gates.md:39-40`)

```
FAIL: command must state the default skips the per-task reviewer
```

(o command file ainda descreve `full` como default)

Se algum assert falhar por motivo diferente destes dois, pare e reporte — o alvo está mal
descrito, não o código.

- [ ] **Step 6: Sonda negativa em cada um dos 5 asserts novos**

Para cada assert, provar que ele **detecta** a remoção da claim. Rode fora do repo:

```bash
TMP=$(mktemp -d)
cp -R plugins/oli-dev "$TMP/"
# exemplo, repetir por assert trocando o arquivo e a claim:
sed -i.bak 's/não presuma o que não dá pra verificar/XXXX/I' "$TMP/oli-dev/skills/dev-cycle/SKILL.md"
grep -qi 'não presuma o que não dá pra verificar' "$TMP/oli-dev/skills/dev-cycle/SKILL.md" \
  && echo "SONDA FALHOU: assert não detecta a remoção" || echo "SONDA OK: assert detecta"
rm -rf "$TMP"
```

Expected: `SONDA OK` nos **5**. Cole as 5 saídas no relatório. Um `SONDA FALHOU` significa
âncora fraca — reescreva a âncora, não o teste.

Contexto de por que isto é passo próprio: no ciclo anterior 3 asserts passaram sem proteger
nada — regex que exigia célula literal ` Opus ` e escapava do negrito da tabela; âncora
`'nos dois tiers'` presente em 4 lugares; `grep -qE '^6\. '` que protegia o **número** do
item, não o conteúdo.

- [ ] **Step 7: Commit**

```bash
git add plugins/oli-dev/tests/ .gitignore
git commit -m "test(oli-dev): redefine os asserts para o redesenho; .gitignore criado

Os asserts amarrados a model-tiers.md saem (o arquivo é deletado na Task 2) e o
assert do ponytail sai (o passo é removido, spec D2.2). Entram 5 asserts novos,
todos com sonda negativa. Suite RED de proposito ate a Task 3.

Bug #2 do handoff: .gitignore nao existia, e setup-gate.md:13 afirmava que
.claude/worktrees/ ja estava nele. Conserto na raiz."
```

---

### Task 2: Reescrita da skill (⚠️ paralelizável com a Task 3)

**Files:**
- Modify: `plugins/oli-dev/skills/dev-cycle/SKILL.md` (78 → ~58)
- Modify: `plugins/oli-dev/skills/dev-cycle/references/setup-gate.md` (40 → ~45)
- Modify: `plugins/oli-dev/skills/dev-cycle/references/review-gates.md` (79 → ~48)
- Delete: `plugins/oli-dev/skills/dev-cycle/references/model-tiers.md` (−108)
- **Não tocar:** `references/pre-push-gate.md`, `references/finalize.md`

**Interfaces:**
- Consumes: os asserts da Task 1.
- Produces: nada que a Task 3 importe além dos nomes de caminho (a Task 3 aponta ponteiros
  para `references/setup-gate.md` no lugar de `references/model-tiers.md`).

- [ ] **Step 1: Deletar o `model-tiers.md` e migrar o que sobrevive**

```bash
git rm plugins/oli-dev/skills/dev-cycle/references/model-tiers.md
```

Migrar para `setup-gate.md`, comprimindo de 32 linhas de origem para ~18:

| Conteúdo | Origem (arquivo deletado) | Forma no destino |
|---|---|---|
| Matriz de papéis/camadas | `:39-52` | 2 linhas de texto corrido, não tabela |
| As 3 redes que dispensam o task-reviewer | `:56-62` | mantida — é o argumento, não roteiro |
| Piso Haiku | `:64-67` | 1 linha |
| Persistência do tier no cabeçalho do plano | `:102-108` | 1 linha + a regra D2.1 |

O override "sem review final de branch" (`:26-30`) **não** vai para o `setup-gate.md`: ele
já vive em `SKILL.md:32-33`, e é lá que os asserts da Task 1 apontam.

**Morre com o arquivo:** a tabela de parsing (`:69-89`), o piso de segurança em 10 linhas
(`:91-100`), a conta errada (`:54`) e a célula morta (`:47`).

- [ ] **Step 2: Reescrever o `setup-gate.md`**

Os 7 passos numerados viram **objetivo + invariantes duros em lista**. O modelo decide a
ordem; a lista diz o que não pode faltar.

Invariantes que **ficam** (spec D3-"Fica"):
- Loop principal em Opus 5 — senão bloqueia e pede `/model`.
- Worktree criado **a partir da `main`**, nunca de outra feature branch.
- Guard de branch ao retomar: worktree linkado **e** PR não-`MERGED`
  (`gh pr view <branch> --json state`). Branch `MERGED` → barra, cria branch nova da `main`.
  Manter a referência ao caso real (PR #4 → commits órfãos → recovery na #5) e ao hook
  `hooks/branch-state-guard.sh`.
- Resume/checkpoint: spec+plano → Fase 4; só spec → Fase 2/3; nada → Fase 1. Confirma antes
  de pular fase.

Que **sai**:
- "Ecoe a interpretação do tier" e o resto do roteiro numerado.
- **Os 3 ramos do ponytail** (`:30-40`, −11 linhas) — spec D2.2. O ciclo não gerencia
  ponytail em caminho nenhum.
- A linha "garanta `.worktrees/` no `.gitignore` nesse caminho" (`:14-15`) —
  `using-git-worktrees/SKILL.md:83-86` já faz isso sozinha.

Que **entra**:
- ⚠️ `setup-gate.md:13` diz hoje que `.claude/worktrees/` está "já no `.gitignore`". Isso
  passou a ser **verdade** com a Task 1. Manter a frase, agora correta.
- O tier migrado (Step 1), incluindo a regra **D2.1**: plano sem cabeçalho de tier ao
  retomar → **assume `full`** e anuncia que assumiu. O fail-safe é o mesmo de antes; só a
  direção do default mudou em volta dele.
- O piso de segurança em **uma linha**: mudança que toca contrato/enforcement/superfície
  sensível → recomende `full`. Sem ack (o caminho arriscado deixou de ser o default).

- [ ] **Step 3: Reescrever o `review-gates.md`**

Mantém: o princípio "evidência ou abstenha"; a Fase 2 (1 staff-reviewer cético em Opus); o
`/simplify` conservador e adjudicado; "sem buracos temporários"; o sub-gate de
`/security-review`.

Muda:
- A ordem da Fase 5 deixa de ser decreto. Sai o "proposital, não reordene"; entra **o
  porquê** numa frase: não simplificar código com bug em aberto, e o `verify` valida o
  resultado já simplificado. A ordem vira consequência disso.
- ⚠️ **Contrato de assert:** `verify` e `sempre` têm que ficar na **mesma linha** — o
  `grep -qiE 'verify.*sempre'` não cruza linhas. Hoje estão em `:39` e `:40`.
- **Bug #3 (spec D6.3):** a seção anti-empilhamento (`:68-74`) dá "arquivos" como exemplo
  de artefato distinto, o que autoriza fatiar um diff **já revisado** em 3 e despachar 3
  "investigadores". Qualificar para *artefatos distintos **que nenhum gate já cobriu***.
- Ponteiros para `references/model-tiers.md` (`:1`, `:23`, `:34`) → `references/setup-gate.md`.

Asserts existentes que este arquivo ainda precisa satisfazer (`test_references.sh`):
`tier`, `opus`, `security-review`, `150`.

- [ ] **Step 4: Reescrever o `SKILL.md`**

⚠️ **Contratos de `test_skill_structure.sh` — quebrar qualquer um deixa a suíte vermelha:**
- `:14-16` exige as 4 seções literais: `## When to Use`, `## Prerequisites`, `## Workflow`,
  `## Verification`. A `## Verification` **esvazia mas não some**.
- `:19` (já corrigido na Task 1) exige link para os 4 `references/*.md` restantes.
- `:23-25` exige as 9 strings literais `"Fase 0"` … `"Fase 8"`.

Mudanças:
- **Princípio 4** reescrito para a inversão do default. Precisa continuar contendo, literal:
  `sem review final de branch` e `override deliberado` (asserts da Task 1).
- **Princípio 5** intacto — precisa continuar contendo, literal:
  `não presuma o que não dá pra verificar`.
- **Princípio 6 (spec D4)** entra com exatamente estas duas linhas:

```markdown
6. **O conductor coordena.** Investigação, coleta e teste vão para subagentes — paralelos
   quando independentes.
```

- **`## Verification`** (spec D3): o checklist de evidência por fase sai; fica **um
  princípio** — evidência é output real, nunca alegação. Duas ou três linhas.
- O `Workflow` mantém os ponteiros por fase (progressive disclosure — spec P4); as
  descrições por fase encolhem e o ponteiro para `model-tiers.md` some.

- [ ] **Step 5: Medir**

Run:
```bash
wc -l plugins/oli-dev/skills/dev-cycle/SKILL.md plugins/oli-dev/skills/dev-cycle/references/*.md
```
Expected: total **≤206**. Se passou de 206, corte mais — o alvo é duro. Se ficou abaixo de
~150, releia a lista D3-"Fica" da spec: provavelmente caiu um gate junto.

- [ ] **Step 6: Rodar a suíte**

Run: `sh plugins/oli-dev/tests/run_all.sh`
Expected: passa tudo **exceto** `command must state the default skips the per-task reviewer`
(é da Task 3).

- [ ] **Step 7: Commit**

```bash
git add plugins/oli-dev/skills/dev-cycle/
git commit -m "refactor(oli-dev): skill sai de roteiro para julgamento

model-tiers.md deletado (o nome ja mentia: com escritor Sonnet nos dois
caminhos, o tier nao troca modelo nenhum); ~18 linhas migradas para o
setup-gate.md, que e a fase onde o tier e parseado.

Os 7 passos numerados do setup-gate viram objetivo + invariantes. A ordem
decretada da Fase 5 vira o porque da ordem. O checklist de evidencia por fase
vira um principio. O passo do ponytail sai: o ciclo nao gerencia ponytail.

Bug #3: a brecha anti-empilhamento passa a exigir artefato que nenhum gate
ja cobriu."
```

---

### Task 3: Periferia — command, README, manifesto, evals, changelog (⚠️ paralelizável com a Task 2)

**Files:**
- Modify: `plugins/oli-dev/commands/oli-dev.md` (corpo + frontmatter `description`)
- Modify: `plugins/oli-dev/.claude-plugin/plugin.json` (`description`)
- Modify: `plugins/oli-dev/README.md` (`:11`, `:20-24`, `:33`)
- Modify: `plugins/oli-dev/evals/evals.json` (`light_tier_scope`, `:42`)
- Modify: `CHANGELOG.md` (`[Unreleased]`, e a conta em `:29`)
- **Não tocar:** `CHANGELOG.md:33` e `docs/superpowers/plans/` antigos — registro histórico.

**Interfaces:**
- Consumes: os asserts da Task 1. Não depende de nenhum símbolo da Task 2.
- Produces: nada.

- [ ] **Step 1: Inverter o parsing no `commands/oli-dev.md`**

As 3 regras de parsing continuam (a estrutura é boa); o que muda é o **significado** e a
prosa de baixo. Alvo:

```
/oli-dev <ideia>          → enxuto (default): sem task-reviewer, escritores Sonnet
/oli-dev full <ideia>     → + task-reviewer por task
/oli-dev light <ideia>    → alias do default, aceito e anunciado (compat)
/oli-dev finalize         → Fase 8
```

⚠️ **Contrato de assert (Task 1):** o arquivo precisa conter, literal, a string
`default não roda task-reviewer`. Frase sugerida: *"O `default não roda task-reviewer` por
task — a Fase 5 cobre o mesmo diff com contexto fresco."*

⚠️ **Contrato de `test_skill_structure.sh:28-30`:** o arquivo precisa continuar contendo os
tokens `light` **e** `full`, e a string `finalize`. A D2 mantém os três — não remova o
`light`, ele é o alias de compat.

O ponteiro `references/model-tiers.md` (`:21`) → `references/setup-gate.md`.

O `description` do frontmatter (`:3`) diz hoje *"tier `full` default; `light` = menos
camadas de review"*. Inverter.

- [ ] **Step 2: `plugin.json`**

`plugins/oli-dev/.claude-plugin/plugin.json:3` — o `description` cita *"tier full/light
trocando camadas de review"*. Atualizar para o default enxuto. `test_manifests.sh:27` só
verifica que o campo existe e não está vazio, então nada quebra; o texto é que mente hoje.

- [ ] **Step 3: `README.md`**

- `:11` e `:20-24`: inverter o default; descrever `full` como opt-in que re-adiciona só o
  task-reviewer por task.
- `:23`: ponteiro `references/model-tiers.md` → `references/setup-gate.md`.
- `:24`: a linha do ponytail por tier sai (spec D2.2).
- `:33`: **remover** a conta `` `full` ~10 · `light` ~6 `` (spec D7). Não substituir por
  outro número — a conta era errada por 2-3× e qualquer número novo aqui seria igualmente
  não medido.

- [ ] **Step 4: `evals/evals.json`**

Duas correções:

1. A eval `light_tier_scope` (`:33-37`) descreve o `light` como opt-in deliberado — vira o
   default. Reescrever cenário e `expected_gate` para o default enxuto, mantendo a pressão
   testada, que continua válida: *"rodar TUDO em Sonnet já que é enxuto"*. O gate esperado
   continua: só os escritores TDD vão pra Sonnet; conductor e staff-reviewer seguem Opus.
   Renomear o `id` para `default_tier_scope`.
   ✅ Verificado: `test_evals.sh:14` exige só 5 ids (`skip_precode_review`, `non_opus_main`,
   `broken_test_push`, `finalize_unmerged`, `resume_from_spec`) — `light_tier_scope` **não**
   está entre eles. Renomear é livre. Manter ≥5 cenários no arquivo (`:12`).
2. `:42` cita *"override deliberado documentado em model-tiers.md"* — arquivo deletado na
   Task 2. Apontar para `SKILL.md`.

- [ ] **Step 5: `CHANGELOG.md`**

Somar em `[Unreleased]` (**não** abrir seção nova — já tem 2 entradas commitadas).
A entrada precisa declarar **MAJOR** (spec D8, `policies/SEMVER.md:6-7` — "remoção de
fase/gate"; a D2 tira o task-reviewer do caminho padrão). Última tag: `oli-dev-v1.0.0`.

Remover a conta errada em `:29` (`` **`full` ~10 · `light` ~6** ``) — está dentro de
`[Unreleased]`, ainda editável. **Não** tocar em `:33`.

- [ ] **Step 6: Rodar a suíte**

Run: `sh plugins/oli-dev/tests/run_all.sh`
Expected: se a Task 2 já entrou, **ALL GREEN**. Se não, verde em tudo menos os asserts que
dependem da Task 2.

- [ ] **Step 7: Commit**

```bash
git add plugins/oli-dev/commands/ plugins/oli-dev/.claude-plugin/ plugins/oli-dev/README.md \
        plugins/oli-dev/evals/ CHANGELOG.md
git commit -m "docs(oli-dev)!: o default inverte — enxuto e o padrao, full e opt-in

BREAKING CHANGE: /oli-dev <ideia> deixa de rodar task-reviewer por task. Quem
quer a aderencia-a-spec por task pede /oli-dev full <ideia>. MAJOR por
policies/SEMVER.md:6-7 (remocao de gate). `light` segue parseando como alias
do default, senao uma ideia que comeca com a palavra light perde a primeira
palavra.

A conta publicada (full ~10 / light ~6) sai do README e do CHANGELOG: ignorava
rodadas de fix, re-reviews escopadas e investigacao — errada por 2-3x. Removida,
nao substituida."
```

---

## Self-review

**Cobertura da spec:**

| Item | Task |
|---|---|
| D1 (deletar `model-tiers.md`, migrar ~18 linhas) | 2, Step 1 |
| D2 (inverter o default) | 3, Step 1 |
| D2.1 (resume sem tier → `full`) | 2, Step 2 |
| D2.2 (ciclo não gerencia ponytail) | 1 Step 1 (assert), 2 Step 2 (setup-gate), 3 Step 3 (README) |
| D3 (o que sai / o que fica) | 2, Steps 2-4 |
| D4 (Princípio 6 em 1 linha) | 2, Step 4 |
| D5 (cortada) | — nada a fazer, por desenho |
| D6.1 (célula morta) | 2, Step 1 (morre com o arquivo) |
| D6.2 (`.gitignore`) | 1, Step 4 |
| D6.3 (brecha anti-empilhamento) | 2, Step 3 |
| D7 (conta errada, 3 cópias) | 2 Step 1 (`model-tiers`), 3 Steps 3 e 5 |
| D8 (MAJOR) | 3, Step 5 |
| Alvo ≤206 linhas | 2, Step 5 |
| 5 asserts obrigatórios + sonda negativa | 1, Steps 2 e 6 |
| Ponteiros pendurados | 2 Step 3, 3 Steps 1, 3, 4 |

Sem lacuna.

**Placeholders:** nenhum. Todo passo carrega o conteúdo literal ou o caminho exato.

**Consistência de nomes:** as 5 âncoras de assert da Task 1 aparecem literais nas Tasks 2 e
3, com as mesmas strings: `sem review final de branch`, `override deliberado`,
`não presuma o que não dá pra verificar`, `verify.*sempre` (mesma linha),
`default não roda task-reviewer`.

**Risco residual conhecido:** as Tasks 2 e 3 são paralelizáveis por tocarem conjuntos
disjuntos de arquivos, mas ambas mexem em ponteiros para `model-tiers.md`. Nenhum arquivo é
tocado pelas duas — conferido na lista de `Files` de cada uma.
