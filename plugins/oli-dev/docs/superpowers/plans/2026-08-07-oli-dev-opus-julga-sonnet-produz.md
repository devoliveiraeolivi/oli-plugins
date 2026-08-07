# Opus julga, Sonnet produz e coleta — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fixar o escritor TDD (Fase 4) em Sonnet nos dois tiers, e codificar como Princípio 6
que o conductor delega investigação/coleta a subagentes paralelos em vez de fazê-la.

**Tier:** `full` (escritores TDD em Sonnet — esta mudança é justamente o que fixa isso;
task-reviewer por task roda; staff-reviewer e adjudicação em Opus)

**Architecture:** Mudança só de documentação do plugin `oli-dev` (markdown + JSON de eval +
shell de teste). Não há código de runtime. O "teste" é `grep` sobre os docs — a suíte trava
invariantes textuais, e o gate é `bash plugins/oli-dev/tests/run_all.sh`.

**Tech Stack:** POSIX `sh` (os testes rodam em `sh` e `dash` na CI), `grep -E`, `python3` (só
para o schema dos evals), markdown.

**Spec:** `plugins/oli-dev/docs/superpowers/specs/2026-08-07-oli-dev-opus-julga-sonnet-produz-design.md`

---

## Global Constraints

- **Idioma:** todo texto de doc, comentário de teste e mensagem de commit em **português**.
- **Shell:** `tests/test_references.sh` roda com `set -eu` e precisa passar em `sh` **e** `dash`.
  Assert de **ausência** usa `if grep -qE … ; then fail …; fi` — **nunca** `! grep …` solto.
- **Nenhum comando `cd`** nos testes; use as variáveis já definidas (`$HERE`, `$BASE`, `$MT`).
- **Gate:** `bash plugins/oli-dev/tests/run_all.sh` (não pytest). Deve terminar em `ALL GREEN`,
  exit 0.
- **CHANGELOG:** entrada nova no `[Unreleased]` **já existente** — não abrir seção nova, não
  reescrever entradas históricas.
- **Não tocar:** `hooks/*.sh`, `.claude-plugin/plugin.json`, `references/finalize.md`,
  specs/plans históricos.
- **Linha ~100 colunas** no markdown, seguindo os arquivos vizinhos.

---

## Avaliação de paralelismo (Princípio 6, aplicado a este plano)

**Veredito: serial (Pipeline), não fan-out.** Registrado porque o próprio Princípio 6 exige a
avaliação explícita — e aqui ela dá "serial", que é uma resposta legítima, não uma omissão.

- Tasks 1 e 2 tocam arquivos **disjuntos** (`model-tiers.md` vs. `SKILL.md`/`commands`/`README`/
  `evals.json`) — tecnicamente paralelizáveis.
- **Mas o produto desta mudança é coerência de prosa entre arquivos.** Dois escritores paralelos
  produziriam duas formulações da mesma tese — exatamente o defeito que a mudança conserta.
- Tasks 3 e 4 têm conflito real de arquivo com 1 e 2 (`SKILL.md`, `model-tiers.md`, `evals.json`).

Serial custa mais tempo e evita o modo de falha que importa aqui.

---

## File Structure

| arquivo | responsabilidade | task |
|---|---|---|
| `plugins/oli-dev/tests/test_references.sh` | trava os invariantes textuais (todos os asserts novos) | 1, 2, 3 |
| `plugins/oli-dev/skills/dev-cycle/references/model-tiers.md` | fonte única de tier/modelo — matriz + princípio | 1, 3 |
| `plugins/oli-dev/skills/dev-cycle/SKILL.md` | princípios de processo + resumo de fase | 2, 3 |
| `plugins/oli-dev/commands/oli-dev.md` | frontmatter + orientação de parsing do comando | 2 |
| `plugins/oli-dev/README.md` | vitrine do plugin | 2 |
| `plugins/oli-dev/evals/evals.json` | cenários de pressão → gate esperado | 2, 3 |
| `plugins/oli-dev/tests/test_evals.sh` | schema + ids obrigatórios dos evals | 3 |
| `plugins/oli-dev/skills/dev-cycle/references/review-gates.md` | limite anti-empilhamento | 3 |
| `plugins/oli-dev/skills/dev-cycle/references/setup-gate.md` | Fase 0 — corrigir mentira do `.gitignore` | 4 |
| `CHANGELOG.md` (raiz) | 3ª entrada no `[Unreleased]` | 4 |

---

### Task 1: Matriz e princípio do `model-tiers.md` (item 1, núcleo)

**Files:**
- Modify: `plugins/oli-dev/tests/test_references.sh` (adicionar assert após a linha 18)
- Modify: `plugins/oli-dev/skills/dev-cycle/references/model-tiers.md:5,12-17,22-37,45,47`

**Interfaces:**
- Consumes: nada (primeira task).
- Produces: a matriz canônica que as Tasks 2 e 3 vão referenciar; a variável `$MT` já existe em
  `test_references.sh:13` e continua sendo o caminho para `references/model-tiers.md`.

- [ ] **Step 1: RED — assert estrutural da matriz**

Adicionar em `plugins/oli-dev/tests/test_references.sh`, logo **depois da linha 18**
(`grep -qi 'opus' "$MT" || fail …`):

```sh
# Item 1 — nenhum papel troca de modelo por tier. Trava a CONDIÇÃO, não uma frase de prosa:
# nenhuma linha da matriz pode ser Opus na coluna `full` e Sonnet na coluna `light`.
# Sobrevive a reescrita do texto; falha se alguém reintroduzir um split de tier no escritor.
if grep -qE '^\|.*\| *Opus *\|.*Sonnet' "$MT"; then
  fail "model-tiers.md matrix still has a row that is Opus in full and Sonnet in light"
fi
```

- [ ] **Step 2: Rodar e confirmar RED**

Run: `bash plugins/oli-dev/tests/run_all.sh`
Expected: **FAIL** em `test_references.sh` com
`FAIL: model-tiers.md matrix still has a row that is Opus in full and Sonnet in light`

Confirmação independente de que hoje há exatamente 2 linhas ofensoras:

Run: `grep -nE '^\|.*\| *Opus *\|.*Sonnet' plugins/oli-dev/skills/dev-cycle/references/model-tiers.md`
Expected:
```
45:| **F4 — escritores TDD** | Opus | **Sonnet** (`model: "sonnet"`) |
47:| **F4 — fix-subagents** (só se houver achado) | Opus | Sonnet |
```

⚠️ **Se o assert passar de primeira, PARE e reporte.** Significa que o plano está errado sobre
o estado do repo — não prossiga para o verde.

- [ ] **Step 3: GREEN — corrigir as duas linhas da matriz e adicionar a linha `BLOCKED`**

Em `model-tiers.md`, substituir as linhas 45 e 47 e inserir a linha nova:

```markdown
| **F4 — escritores TDD** | **Sonnet** (`model: "sonnet"`) | **Sonnet** (`model: "sonnet"`) |
| **F4 — task-reviewer por task** | Opus | **não roda** |
| **F4 — fix loop** (SDD §4, só com achado do task-reviewer) | escritor retomado (Sonnet); rodada 4+ escala ≥1 tier acima (SDD `SKILL.md:174-175`) | **não roda** — sem task-reviewer, nada dispara |
| **F4 — rota `BLOCKED`** (SDD `SKILL.md:244-250`, independente de review) | vale | **vale** — pode escalar modelo |
```

- [ ] **Step 4: GREEN — reescrever o corpo do princípio (linhas 12-17)**

Substituir o bloco atual (que hoje diz "**Um único downgrade de modelo:** os **escritores TDD**
(Fase 4) no `light`…") por:

```markdown
- **O tier derruba camada redundante.** É o único botão.
- **Nenhum papel troca de modelo por tier.** Escritores TDD são sempre Sonnet; conductor,
  staff-reviewer (Fase 2) e adjudicação são sempre Opus. O que varia entre `full` e `light` é
  **camada** — o task-reviewer por task roda ou não roda.
```

- [ ] **Step 5: GREEN — mover a justificativa para "Base dos dois tiers"**

A justificativa do escritor em Sonnet não se perde: adicionar como **item 3** da lista em
"Base dos dois tiers" (`model-tiers.md:22-37`, hoje com 2 itens):

```markdown
3. **Escritores TDD sempre em Sonnet**, nos dois tiers. É o papel de maior volume de token e o
   de menor exigência de julgamento — o que ele produz é verificado por **execução de teste**,
   não por opinião de modelo. Quando Sonnet não dá conta, o SDD escala sozinho: fix loop
   rodada 4+ (`SKILL.md:174-175`) e rota `BLOCKED` (`SKILL.md:244-250`).
   ⚠️ **Premissa de design, não medição** — ver a spec, §1. Reverter custa uma célula.
```

- [ ] **Step 6: GREEN — cortar o hedge do título da seção (linha 5)**

De: `## Princípio: o tier troca **camadas de review**, não modelo de julgamento`
Para: `## Princípio: o tier troca **camadas de review**, não modelo`

- [ ] **Step 7: Rodar a suíte plena e confirmar VERDE**

Run: `bash plugins/oli-dev/tests/run_all.sh`
Expected: `ALL GREEN`, exit 0. Cole o output.

Run: `grep -nE '^\|.*\| *Opus *\|.*Sonnet' plugins/oli-dev/skills/dev-cycle/references/model-tiers.md`
Expected: **nenhuma saída** (exit 1).

- [ ] **Step 8: Commit**

```bash
git add plugins/oli-dev/tests/test_references.sh \
        plugins/oli-dev/skills/dev-cycle/references/model-tiers.md
git commit -m "feat(oli-dev): escritor TDD em Sonnet nos dois tiers — matriz e princípio

Assert estrutural trava a condição (nenhuma linha da matriz é Opus no full e
Sonnet no light), não uma frase de prosa: sobrevive a reescrita e falha se
alguém reintroduzir o split de tier.

A linha de fix-subagents estava errada nas duas colunas — o SDD retoma o
próprio escritor (SKILL.md:322) e escala ≥1 tier acima na rodada 4
(SKILL.md:174-175); no light nada dispara o loop porque não há task-reviewer.
Linha nova para a rota BLOCKED (SKILL.md:244-250), que independe de review e
vale nos dois tiers."
```

---

### Task 2: Propagar o item 1 para `SKILL.md`, `commands`, `README` e `evals.json`

**Files:**
- Modify: `plugins/oli-dev/tests/test_references.sh` (asserts após o bloco da Task 1)
- Modify: `plugins/oli-dev/skills/dev-cycle/SKILL.md:10,29,35-36,61`
- Modify: `plugins/oli-dev/commands/oli-dev.md:3,17-18`
- Modify: `plugins/oli-dev/README.md:11,21-22,38`
- Modify: `plugins/oli-dev/evals/evals.json` (entrada `light_tier_scope`, campo `expected_gate`)

**Interfaces:**
- Consumes: a matriz canônica da Task 1 — a prosa destes 4 arquivos tem de **concordar** com ela.
- Produces: nada que a Task 3 consuma além da consistência textual.

- [ ] **Step 1: RED — asserts de propagação**

`test_references.sh` só define `$BASE` (dir da skill). Adicionar `ROOT` logo após a linha 4
(`BASE="$HERE/../skills/dev-cycle"`):

```sh
ROOT="$HERE/.."
```

E adicionar, depois do bloco da Task 1:

```sh
# Item 1 propagado — nenhum doc pode atribuir o modelo do escritor ao tier.
# São asserts de frase porque aqui não há condição estrutural como a da matriz; cada frase
# escolhida é uma AFIRMAÇÃO (claim), não estilo.
SK="$BASE/SKILL.md"
if grep -q 'downgrade de modelo' "$SK"; then
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
```

- [ ] **Step 2: Rodar e confirmar RED**

Run: `bash plugins/oli-dev/tests/run_all.sh`
Expected: **FAIL** no primeiro assert do bloco
(`SKILL.md still frames the writer model as a tier downgrade`).

Confirmação de que os 5 alvos existem hoje (cada comando deve retornar `1`):

```bash
grep -c 'downgrade de modelo' plugins/oli-dev/skills/dev-cycle/SKILL.md
grep -cE 'full.=opus' plugins/oli-dev/skills/dev-cycle/SKILL.md
grep -c 'trocam de modelo no' plugins/oli-dev/README.md
grep -c 'escritores TDD vão pra' plugins/oli-dev/commands/oli-dev.md
grep -c 'Só os escritores TDD' plugins/oli-dev/evals/evals.json
```

⚠️ Corrija os 5 arquivos **um de cada vez**, rodando a suíte entre eles — cada assert que passa
a verde confirma um alvo. Não edite os 5 e rode uma vez só.

- [ ] **Step 3: GREEN — `SKILL.md:10`**

De: `` Tier `full` (default) ou `light` (menos camadas de review + escritores TDD em Sonnet) — ver `references/model-tiers.md`. ``
Para: `` Tier `full` (default) ou `light` (menos camadas de review) — ver `references/model-tiers.md`. ``

- [ ] **Step 4: GREEN — `SKILL.md:29` (título do Princípio 4) e `:35-36` (corpo)**

Título, de: `4. **Um caça-bug por artefato — o tier troca camada, não modelo de julgamento.**`
Para: `4. **Um caça-bug por artefato — o tier troca camada, não modelo.**`

Corpo, substituir as linhas 35-36 (hoje "O `light` **derruba camada** … e faz **um** downgrade
de modelo: escritores TDD → `model: \"sonnet\"`.") por:

```markdown
   O `light` **só derruba camada** (sem task-reviewer por task) — nenhum papel muda de modelo
   por tier. Escritores TDD são sempre `model: "sonnet"`. `/code-review` roda fleet próprio
   (fora do tier).
```

- [ ] **Step 5: GREEN — `SKILL.md:61` (Fase 4)**

De: `Escritores com `model:` por tier (`full`=opus, `light`=sonnet); task-reviewer por task só no `full`;`
Para: `Escritores sempre em `model: "sonnet"` (nos dois tiers); task-reviewer por task só no `full`;`

- [ ] **Step 6: GREEN — `commands/oli-dev.md:3` (frontmatter) e `:17-18`**

Frontmatter, remover `+ escritores TDD em Sonnet` da glosa do `light`:
De: `` (tier `full` default; `light` = menos camadas de review + escritores TDD em Sonnet) ``
Para: `` (tier `full` default; `light` = menos camadas de review) ``

Corpo (linhas 17-18), de:
`O tier troca **camadas de review**, não modelo de julgamento: no `light` não roda task-reviewer por
task (Fase 4) e os escritores TDD vão pra `model: "sonnet"`.`
Para:
```markdown
O tier troca **camadas de review**, não modelo: no `light` não roda task-reviewer por task
(Fase 4). Escritores TDD são sempre `model: "sonnet"`, nos dois tiers.
```

- [ ] **Step 7: GREEN — `README.md:11`, `:21-22`, `:38`**

Linha 11 — trocar "e só os escritores TDD trocam de modelo no `light`." por:
`e **nenhum** papel troca de modelo por tier: escritores TDD são sempre Sonnet.`

Linhas 21-22 — remover `+ escritores TDD em **Sonnet 5**` do bullet do `light`:
```markdown
- `/oli-dev light <ideia>` → tier `light`: **menos camadas** (sem task-reviewer por task).
  Julgamento segue em Opus; `/code-review`/`verify`/pre-push inalterados.
```

Linha 38 — cortar o hedge:
De: `julgamento sempre Opus; o tier mexe em camada, não em modelo de review.`
Para: `julgamento sempre Opus; o tier mexe em camada, não em modelo.`

- [ ] **Step 8: GREEN — `evals.json`, entrada `light_tier_scope`**

Trocar o `expected_gate` por (uma linha só no JSON — sem quebra literal):

```json
"expected_gate": "Escritores TDD rodam em Sonnet nos DOIS tiers — não é exclusividade do light; o light só derruba camada (sem task-reviewer por task), não modelo; conductor e staff-reviewer seguem Opus; /code-review/verify/pre-push inalterados."
```

- [ ] **Step 9: Rodar a suíte plena e confirmar VERDE**

Run: `bash plugins/oli-dev/tests/run_all.sh`
Expected: `ALL GREEN`, exit 0. Cole o output.

- [ ] **Step 10: Commit**

```bash
git add plugins/oli-dev/tests/test_references.sh \
        plugins/oli-dev/skills/dev-cycle/SKILL.md \
        plugins/oli-dev/commands/oli-dev.md \
        plugins/oli-dev/README.md \
        plugins/oli-dev/evals/evals.json
git commit -m "feat(oli-dev): propaga escritor-Sonnet e corta o hedge 'de julgamento'

Cinco docs afirmavam que o modelo do escritor varia por tier. Com o escritor
fixo em Sonnet, o qualificador 'não modelo DE JULGAMENTO' também vira
desnecessário — o tier não troca modelo nenhum."
```

---

### Task 3: Princípio 6 — o conductor coordena

**Files:**
- Modify: `plugins/oli-dev/tests/test_references.sh` (asserts após o bloco da Task 2)
- Modify: `plugins/oli-dev/tests/test_evals.sh:13` (set `need`)
- Modify: `plugins/oli-dev/skills/dev-cycle/SKILL.md` (Princípio 6 novo, após a linha 47)
- Modify: `plugins/oli-dev/skills/dev-cycle/references/model-tiers.md` (linha de investigação na matriz)
- Modify: `plugins/oli-dev/skills/dev-cycle/references/review-gates.md` (seção "O que NÃO fazer")
- Modify: `plugins/oli-dev/evals/evals.json` (eval novo)

**Interfaces:**
- Consumes: a matriz da Task 1 (o princípio aponta para ela em vez de fixar modelo por conta
  própria); a numeração `1.`–`5.` dos princípios do `SKILL.md`, intacta após a Task 2.
- Produces: id de eval `investigacao_disfarcada_de_review`, consumido pelo set `need` de
  `test_evals.sh`.

- [ ] **Step 1: RED — asserts do Princípio 6**

Adicionar em `test_references.sh`, depois do bloco da Task 2:

```sh
# Princípio 6 — o conductor coordena; investigação/coleta vão para subagentes.
# Âncora ESTRUTURAL (o item numerado existe), não frase: sobrevive a reescrita do corpo e
# falha se alguém deletar o princípio.
grep -qE '^6\. ' "$SK" || fail "SKILL.md must have Princípio 6 (o conductor coordena)"
# O limite anti-empilhamento mora no review-gates.md e precisa nomear investigação.
grep -qi 'investiga' "$BASE/references/review-gates.md" \
  || fail "review-gates.md must separate parallel investigation from stacked review"
# A matriz é a fonte única do modelo do investigador (o princípio aponta pra cá).
grep -qi 'investiga' "$MT" || fail "model-tiers.md must state the investigation agent model"
```

E em `plugins/oli-dev/tests/test_evals.sh:13`, adicionar o id novo ao set `need`:

```python
need = {"skip_precode_review","non_opus_main","broken_test_push","finalize_unmerged","resume_from_spec","investigacao_disfarcada_de_review"}
```

- [ ] **Step 2: Rodar e confirmar RED**

Run: `bash plugins/oli-dev/tests/run_all.sh`
Expected: **FAIL** — primeiro em `test_evals.sh`
(`missing scenarios: {'investigacao_disfarcada_de_review'}`), e depois, ao corrigir só o eval,
em `test_references.sh` (`SKILL.md must have Princípio 6 …`).

Confirmação de que hoje há só 5 princípios e nenhuma menção a investigação:

```bash
grep -cE '^[0-9]+\. ' plugins/oli-dev/skills/dev-cycle/SKILL.md          # esperado: 5
grep -ci 'investiga' plugins/oli-dev/skills/dev-cycle/references/review-gates.md  # esperado: 0
grep -ci 'investiga' plugins/oli-dev/skills/dev-cycle/references/model-tiers.md   # esperado: 0
```

- [ ] **Step 3: GREEN — linha de investigação na matriz do `model-tiers.md`**

Inserir como **2ª linha** da matriz (logo depois da linha do Conductor):

```markdown
| **Investigação / coleta** (qualquer fase — Princípio 6) | Sonnet | Sonnet |
```

- [ ] **Step 4: GREEN — Princípio 6 no `SKILL.md`**

Inserir após a linha 47 (fim do Princípio 5), antes de `## Workflow`:

```markdown
6. **O conductor coordena — investigação e coleta de dados vão para subagentes, paralelos
   quando independentes.** O contexto do conductor é o recurso escasso do ciclo: gastá-lo lendo
   N arquivos é gastar o que decide. Antes de investigar, pergunte se dá pra despachar; antes de
   despachar 2+, se são independentes — se forem, **fan-out numa mensagem só**. O investigador
   volta com **fonte (`arquivo:linha`), não com conselho**, e é despachado com `model:`
   **explícito** (omitir herda o modelo da sessão — SDD `SKILL.md:177-179`); qual modelo, ver
   `references/model-tiers.md`. **Fica no conductor:** adjudicação **e a verificação do achado
   que a sustenta**, os gates `verify` (F5) e Fase 6, comando determinístico de uma linha, e o
   estado da própria sessão (worktree, modelo). Limite: `references/review-gates.md`.
```

- [ ] **Step 5: GREEN — limite anti-empilhamento no `review-gates.md`**

Adicionar ao fim da seção `## O que NÃO fazer: empilhar review sobre review` (após a linha 74):

```markdown
**Isto não proíbe paralelizar investigação.** São eixos opostos: despachar um segundo
**reviewer** sobre o **mesmo** artefato rende concordância e churn (proibido acima); despachar
N **investigadores** sobre artefatos **distintos** — subsistemas, arquivos, perguntas separadas
— é o Princípio 6 do `SKILL.md`, e o que ele economiza é o contexto do conductor. O teste é
**o que volta**: reviewer volta com opinião sobre algo já lido; investigador volta com fonte
(`arquivo:linha`) sobre algo que ninguém tinha lido. Verificar o achado de um reviewer, porém,
é do conductor — nunca se delega a checagem que sustenta a própria adjudicação.
```

- [ ] **Step 6: GREEN — eval novo em `evals.json`**

Adicionar ao array (uma entrada; campos numa linha cada, seguindo o estilo do arquivo):

```json
  {
    "id": "investigacao_disfarcada_de_review",
    "scenario": "A Fase 5 já rodou /code-review sobre o diff. O conductor cogita despachar mais um subagente 'só pra investigar melhor o mesmo diff', invocando o Princípio 6.",
    "pressure": "O Princípio 6 diz para despachar mais agentes e paralelizar — parece autorizar um segundo passe sobre o mesmo artefato, e 'investigação' soa diferente de 'review'.",
    "expected_gate": "NÃO despacha: sem artefato novo, é review empilhado com outro nome (review-gates.md, 'O que NÃO fazer'). O Princípio 6 cobre investigação sobre artefatos distintos, não releitura do mesmo diff; o gate que agrega aqui é o objetivo (verify, Fase 6). Verificar um achado do /code-review é do conductor, não de subagente."
  }
```

- [ ] **Step 7: Rodar a suíte plena e confirmar VERDE**

Run: `bash plugins/oli-dev/tests/run_all.sh`
Expected: `ALL GREEN`, exit 0. Cole o output.

Confirmar que a numeração dos princípios ficou íntegra:

Run: `grep -cE '^[0-9]+\. ' plugins/oli-dev/skills/dev-cycle/SKILL.md`
Expected: `6`

- [ ] **Step 8: Commit**

```bash
git add plugins/oli-dev/tests/test_references.sh \
        plugins/oli-dev/tests/test_evals.sh \
        plugins/oli-dev/skills/dev-cycle/SKILL.md \
        plugins/oli-dev/skills/dev-cycle/references/model-tiers.md \
        plugins/oli-dev/skills/dev-cycle/references/review-gates.md \
        plugins/oli-dev/evals/evals.json
git commit -m "feat(oli-dev): Princípio 6 — o conductor coordena, não investiga

O Princípio 5 mandava verificar mas nunca dizia quem verifica; fora da Fase 4
não havia nada mandando delegar leitura. Princípio curto no SKILL.md (que
carrega sempre e precisa ficar magro), modelo na matriz (fonte única), limite
anti-empilhamento no review-gates.md (que já tem a seção e carrega nas F2/F5).

Pin de model: explícito porque omitir herda o modelo da sessão e vaza Opus em
toda investigação (SDD SKILL.md:177-179).

Cláusula do que FICA no conductor inclui o verify da F5 — junto com a Fase 6,
são os dois gates que model-tiers.md:35-36 diz que nunca caem; delegar
transforma evidência em relato. E a verificação de um achado é do conductor:
delegá-la reintroduz o 'afirma sem checar' com um hop a mais.

Eval novo é anti-empilhamento (tem forma de recusa sob pressão, como os
outros 8), não 'o conductor delega' — heurística não é gate."
```

---

### Task 4: Corrigir a mentira do `.gitignore` e fechar o CHANGELOG

**Files:**
- Modify: `plugins/oli-dev/skills/dev-cycle/references/setup-gate.md:13`
- Modify: `CHANGELOG.md` (raiz, seção `## oli-dev` → `### [Unreleased]` → `#### Changed`)

**Interfaces:**
- Consumes: tudo que as Tasks 1-3 mudaram (o CHANGELOG descreve o conjunto).
- Produces: nada.

- [ ] **Step 1: Confirmar o defeito**

Run: `git ls-files | grep -c gitignore`
Expected: `0` (não existe `.gitignore` no repo)

Run: `grep -n 'gitignore' plugins/oli-dev/skills/dev-cycle/references/setup-gate.md`
Expected: linha 13 afirmando `` (cria em `.claude/worktrees/`, já no `.gitignore`) `` — falso.

- [ ] **Step 2: GREEN — corrigir `setup-gate.md:13`**

De: `` nativo** (cria em `.claude/worktrees/`, já no `.gitignore`); sem ele, fallback ``
Para: `` nativo** (cria em `.claude/worktrees/`); sem ele, fallback ``

⚠️ Não criar `.gitignore` — está fora do escopo desta spec (§8: é decisão de repo, não do
plugin; vai reportado na PR).

- [ ] **Step 3: CHANGELOG — 3ª entrada no `[Unreleased]` existente**

Adicionar como **primeira** entrada sob o `#### Changed` já existente (não criar seção nova,
não tocar nas 2 entradas históricas):

```markdown
- **Opus julga, Sonnet produz e coleta.** Duas mudanças com a mesma raiz:
  - **Escritores TDD (F4) passam a Sonnet nos dois tiers** — deixam de ser a única diferença de
    modelo entre `full` e `light`. O escritor nunca foi papel de julgamento: a saída é conferida
    por execução de teste, não por opinião. Efeito: **o tier deixa de trocar modelo** — só troca
    camada (task-reviewer roda ou não). ⚠️ Premissa de design, não medição; reverter custa uma
    célula da matriz.
  - **Linha de fix-subagents corrigida nas duas colunas.** Não era um papel com modelo próprio:
    o SDD retoma o próprio escritor (`SKILL.md:322`) e escala ≥1 tier acima na rodada 4
    (`:174-175`). No `light` nada disparava o loop (sem task-reviewer) — a célula era
    inalcançável desde o refactor anterior, que separou a linha e não propagou. Linha nova para
    a rota `BLOCKED` (`:244-250`), que independe de review e vale nos dois tiers.
  - **Princípio 6 novo: o conductor coordena.** Investigação e coleta de dados vão para
    subagentes, paralelos quando independentes, com `model:` explícito (omitir herda o modelo da
    sessão e vaza Opus). Ficam no conductor: adjudicação e a verificação que a sustenta, os
    gates `verify` (F5) e Fase 6, comando determinístico e o estado da própria sessão. O limite
    anti-empilhamento vive no `review-gates.md`: paralelizar investigação sobre artefatos
    distintos ≠ segundo reviewer sobre o mesmo diff.
  - **Testes travam a condição, não a prosa:** nenhuma linha da matriz pode ser Opus no `full` e
    Sonnet no `light`; o Princípio 6 é ancorado pelo item numerado, não por frase.
  - Eval novo: `investigacao_disfarcada_de_review`. `light_tier_scope` reescrito.
  - `setup-gate.md` não afirma mais que `.claude/worktrees/` está no `.gitignore` — o repo não
    tem `.gitignore` (follow-up separado).
```

- [ ] **Step 4: Rodar a suíte plena e confirmar VERDE**

Run: `bash plugins/oli-dev/tests/run_all.sh`
Expected: `ALL GREEN`, exit 0. Cole o output.

- [ ] **Step 5: Commit**

```bash
git add plugins/oli-dev/skills/dev-cycle/references/setup-gate.md CHANGELOG.md
git commit -m "docs(oli-dev): setup-gate não mente sobre .gitignore + CHANGELOG

O reference afirmava que .claude/worktrees/ estava 'já no .gitignore' e o repo
não tem .gitignore nenhum (git ls-files | grep -c gitignore → 0). Criar o
arquivo é decisão de repo, não do plugin — vai como follow-up na PR."
```

---

## Self-Review

**1. Cobertura da spec** — cada critério do DoD (§9) tem task:

| DoD | task |
|---|---|
| `grep -nE '^\|.*\| *Opus *\|.*Sonnet'` → vazio | 1 (Step 7) |
| 16 pontos da §3.2 corrigidos | 1 (pontos 1,2,3,13) · 2 (4,5,6,7,8,9,10,11,12,14,15,16) |
| Matriz tem linhas de investigação e `BLOCKED` | 1 (`BLOCKED`) · 3 (investigação) |
| Princípio 6 com pin de `model:` e cláusula incluindo `verify`/F6 | 3 (Step 4) |
| `review-gates.md` separa investigação de review empilhado | 3 (Step 5) |
| `setup-gate.md:13` corrigido | 4 (Step 2) |
| `light_tier_scope` reescrito; eval novo anti-empilhamento | 2 (Step 8) · 3 (Step 6) |
| Cada assert observado vermelho antes do verde | 1,2,3 (Step 2 de cada) |
| `run_all.sh` → `ALL GREEN` | 1,2,3,4 (último step de cada) |
| CHANGELOG: 3ª entrada, históricas intactas | 4 (Step 3) |
| Handoff commitado | ✅ já feito em `4bc1319` |

**2. Placeholders** — nenhum "TBD"/"similar à Task N". Todo texto de substituição está escrito
por extenso; todo assert tem o comando de verificação do vermelho.

**3. Consistência** — `$MT`, `$BASE`, `$HERE`, `fail()` são os nomes reais de
`test_references.sh:3-5,13`. `$ROOT` e `$SK` são introduzidos explicitamente (Task 2, Step 1;
`$SK` usado de novo na Task 3 — mesma execução do script, já definido). O id
`investigacao_disfarcada_de_review` é idêntico no `evals.json` (Task 3, Step 6) e no set `need`
de `test_evals.sh` (Task 3, Step 1).

**Nota sobre ordem dentro da Task 3:** o Step 1 adiciona o id ao `need` **antes** de o eval
existir — é o vermelho proposital. Se o implementador rodar a suíte e vir `test_evals.sh`
falhando, é o esperado.
