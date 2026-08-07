# Design — Opus julga, Sonnet produz e coleta

**Data:** 2026-08-07
**Repo alvo:** `oli-plugins` (plugin `oli-dev` modifica a si mesmo)
**Tier do ciclo:** `full`
**Status:** proposta
**Origem:** handoff `handoffs/2026-08-07-sonnet-escritores-tdd-full-handoff.md` (item 1) +
feedback direto do usuário em 2026-08-07 (item 2)

---

## 1. Problema e objetivo

Duas mudanças com a mesma raiz, por isso uma spec só.

**Item 1 — o escritor TDD é Opus no `full` sem justificativa própria.**
`model-tiers.md:45` fixa `| **F4 — escritores TDD** | Opus | **Sonnet** |`. É o único papel
que muda de modelo por tier. Mas o escritor nunca foi papel de julgamento neste design: sua
saída é conferida por **execução de teste** (vermelho→verde), não por opinião de modelo. Quem
julga — staff-reviewer (F2), adjudicação, conductor — já é Opus nos dois tiers
(`model-tiers.md:16-17`). Reservar Opus pro escritor só no `full` é sobra do desenho anterior.

**Item 2 — a skill não diz quem investiga.** O Princípio 5 (`SKILL.md:38-47`) manda "não presuma
o que não dá pra verificar", mas nunca diz **quem** vai atrás da fonte — hoje, implicitamente,
sempre o próprio conductor. Fora da Fase 4, não há uma linha mandando delegar leitura/coleta, e
o único lugar que avalia paralelismo é uma cláusula solta da Fase 4 (`SKILL.md:61`: "Pipeline
(serial) ou Fan-out (`dispatching-parallel-agents`) conforme dependência").

**Tese que une os dois:**

> **Opus julga. Sonnet produz e coleta.** O escritor TDD produz código verificado por execução
> de teste. O agente de investigação coleta fatos verificados por citação `arquivo:linha`.
> Nenhum dos dois emite opinião — logo, nenhum dos dois precisa de Opus. O que precisa de Opus
> é julgamento: staff-reviewer, adjudicação, conductor.

**Objetivo:** aplicar essa régua nos dois eixos — produção (item 1) e coleta (item 2).

### Não-objetivos (YAGNI)

- **Não** mexer em hook ID, `.pre-commit-hooks.yaml`, `policies/ENFORCEMENT.md` — não é matéria
  de MAJOR. Hooks são independentes de tier
  (`specs/2026-06-30-oli-dev-model-tiers-design.md:106`, e grep confirma zero menções a modelo
  em `hooks/*.sh`).
- **Não** rebaixar nenhum papel de julgamento. Staff-reviewer, adjudicação e conductor seguem
  Opus nos dois tiers, sem mudança.
- **Não** mexer em `/code-review`, `/simplify`, `verify`, `/security-review` — têm fleet próprio,
  fora do alcance do tier.
- **Não** introduzir Haiku. `model-tiers.md:64-67` já documenta a exclusão por decisão; segue.
- **Não** criar `.gitignore` (ver §8, achado lateral).

---

## 2. Base factual (verificada, não inferida)

Levantada por 5 agentes de investigação paralelos; cada afirmação abaixo foi reconfirmada por
`grep` direto antes de escrever esta spec.

### 2.1 A suíte de testes é uma rede fraca para esta mudança

Baseline atual (`bash plugins/oli-dev/tests/run_all.sh`):

```
=== test_branch_state_guard.sh [hook shell: sh] ===   23 passed, 0 failed
=== test_branch_state_guard.sh [hook shell: dash] === 23 passed, 0 failed
=== test_evals.sh ===        PASS
=== test_manifests.sh ===    PASS
=== test_pre_push_gate.sh [sh] ===   15 passed, 0 failed
=== test_pre_push_gate.sh [dash] === 15 passed, 0 failed
=== test_references.sh ===   PASS
=== test_shellcheck.sh ===   PASS
=== test_skill_structure.sh === PASS
ALL GREEN
exit=0
```

Todos os asserts de modelo em `test_references.sh` são **presence checks**, nunca **pairing
checks**:

```sh
# tests/test_references.sh:17-18
grep -qi  'sonnet' "$MT" || fail "model-tiers.md must mention Sonnet"
grep -qi  'opus'   "$MT" || fail "model-tiers.md must mention Opus"
```

Como `Opus` continua no doc (conductor, staff-reviewer) e `Sonnet` também, **a suíte fica
`ALL GREEN` mesmo com a prosa logicamente contraditória**. `test_evals.sh` só valida schema
(`id`/`scenario`/`pressure`/`expected_gate` não-vazios + presença de 5 ids obrigatórios), nunca
conteúdo textual — `light_tier_scope` sequer está no set obrigatório.

**Consequência para o TDD da Fase 4:** o vermelho não vem de graça. Ver §6.

### 2.2 A célula `light` do fix-subagent é inalcançável

`model-tiers.md:47` diz `| **F4 — fix-subagents** (só se houver achado) | Opus | Sonnet |`.

O SDD 6.2.0 (versão ativa, confirmada em `~/.claude/plugins/installed_plugins.json`) define o
gatilho do fix loop:

> `subagent-driven-development/SKILL.md:304-305` — "The loop triggers when the review reports
> spec ❌, any Critical or Important finding, or a ⚠️ item you confirmed as a real gap."

No `light`, o task-reviewer **não roda** (`model-tiers.md:46`) e o review final de branch
**não roda** (`model-tiers.md:48`). Nada pode disparar o loop. A célula promete "só se houver
achado" e o achado nunca existe.

**Origem: bug de refactor, não decisão.** Antes de `60853e9` a matriz tinha uma linha combinada
`| Fase 4 — task-reviewers + fix-subagents | Opus | Sonnet |`. O commit separou em duas, mudou
task-reviewer para "não roda" no `light`, e não propagou na segunda metade. A mensagem do commit
justifica a remoção do task-reviewer em detalhe e **não menciona fix-subagents uma única vez**.

### 2.3 O fix loop não é um papel com modelo próprio

O SDD define quem executa o fix:

> `subagent-driven-development/SKILL.md:322` — "Rounds 1-3 — **resume the original implementer**.
> Send it the open findings verbatim."
> `subagent-driven-development/SKILL.md:328` — "Rounds 4-5 — dispatch a fresh implementer **on a
> more capable model**"

Ou seja: o fix é o **próprio escritor retomado**, com escalada de modelo embutida no SDD. Não é
um terceiro papel a alocar. A linha `| Opus | Sonnet |` está errada nas duas colunas.

Nota: o termo literal "fix subagent" aparece **uma única vez** no SDD, e está amarrado ao
whole-branch review final (`SKILL.md:404-407`) — que não roda em nenhum tier do `oli-dev`.

### 2.4 A contagem de passes de LLM não muda

`model-tiers.md:54` e `README.md:33` publicam `full ~10 · light ~6`. Nenhum arquivo documenta a
fórmula; reconstruída por eliminação para uma mudança de 4 tasks, contando **dispatches de
subagente**:

| | `full` | `light` |
|---|---|---|
| staff-reviewer (F2) | 1 | 1 |
| escritores TDD (F4) | 4 | 4 |
| task-reviewer por task (F4) | 4 | 0 |
| `/code-review` (F5) | 1 | 1 |
| **total** | **10** ✓ | **6** ✓ |

Bate exato com o publicado. A fórmula conta *quantos dispatches*, não *qual modelo* — trocar
Opus por Sonnet não move o número. **Nenhuma edição necessária** em `model-tiers.md:54` nem
`README.md:33` por conta do item 1.

⚠️ Mas ver §4.4: o item 2 tem interação com esse número.

### 2.5 O que a skill já diz sobre delegar (para não duplicar)

- `SKILL.md:61` — Fase 4: "Pipeline (serial) ou Fan-out (`dispatching-parallel-agents`) conforme
  dependência." **Única** menção a paralelismo em toda a skill, e só cobre escritores de task.
- `SKILL.md:59`, `review-gates.md:22` — F2 despacha **1** staff-reviewer (singular, deliberado).
- `setup-gate.md` (Fase 0 inteira), `pre-push-gate.md:3` ("Gate primário (você roda e mostra
  evidência)"), `SKILL.md:69-78` (Verification), `finalize.md` — todos escritos com o conductor
  executando diretamente, sem menção a delegar.

**Lacuna real:** delegar *investigação/coleta* fora da Fase 4 não é coberto em lugar nenhum; e
avaliar paralelismo existe só como cláusula pontual da Fase 4, nunca como princípio.

### 2.6 Risco de contradição a desarmar

`review-gates.md:68-74` tem a seção **"O que NÃO fazer: empilhar review sobre review"**:

> "Se você está por despachar um reviewer adicional 'só pra conferir', a pergunta certa é se
> existe **artefato novo** ou apenas o mesmo diff relido."

Isso é sobre redundância de **julgamento** sobre o mesmo artefato. Paralelizar **investigação**
sobre artefatos distintos é o eixo oposto. Um princípio novo de "use mais agentes" lê como
contradição direta se não separar os dois explicitamente.

---

## 3. Decisão — item 1: escritor TDD = Sonnet nos dois tiers

### 3.1 A matriz depois

| Papel / camada | `full` (default) | `light` |
|---|---|---|
| **Conductor** (F1 · F3 · adjudicação · `/simplify` `verify` `/security-review` inline) | Opus | Opus |
| **F2 — staff-reviewer** (sobre a spec) | Opus | Opus |
| **F4 — escritores TDD** | **Sonnet** | **Sonnet** |
| **F4 — task-reviewer por task** | Opus | **não roda** |
| **F4 — fix loop** (só se o task-reviewer achar) | escritor retomado (Sonnet); SDD §4 escala a modelo mais capaz na rodada 4 | **não roda** — sem task-reviewer, nada dispara |
| **F4 — review final de branch** | **não roda** (coberto pela F5) | **não roda** |
| **F5 — `/code-review`** | fleet próprio, inalterado | inalterado |
| **F5 — `/simplify`** | se diff > ~150 linhas | se diff > ~150 linhas |
| **F5 — `verify`** | sempre | sempre |
| **F6 — pre-push gate** | sempre | sempre |

**A linha do escritor fica na matriz** mesmo sem variar por tier. A matriz já tem 6 linhas que
não variam (`F2 staff-reviewer Opus|Opus`, `F4 review final não roda|não roda`, `F5 verify
sempre|sempre`, `F6 sempre|sempre`, e as duas de `/code-review`/`/simplify`) — ela é **retrato
completo, não diff**. Manter a linha é o menor diff e torna mais difícil alguém reintroduzir um
split de tier numa edição futura.

### 3.2 Efeito estrutural — o princípio vira literal

Depois da mudança, **o tier tem zero downgrade de modelo**. A única diferença `full`/`light` é o
task-reviewer, que é **camada**. O Princípio 4 ("o tier troca camada, não modelo") deixa de ser
aproximação e passa a ser descrição exata.

Isso obriga a reescrever a narrativa, não só a célula. Frases que ficam **factualmente falsas**:

| `arquivo:linha` | texto atual (literal) |
|---|---|
| `model-tiers.md:13` | "**Um único downgrade de modelo:** os **escritores TDD** (Fase 4) no `light`." |
| `model-tiers.md:45` | `\| **F4 — escritores TDD** \| Opus \| **Sonnet** (\`model: "sonnet"\`) \|` |
| `model-tiers.md:47` | `\| **F4 — fix-subagents** (só se houver achado) \| Opus \| Sonnet \|` |
| `SKILL.md:10` | "`light` (menos camadas de review + escritores TDD em Sonnet)" |
| `SKILL.md:35-36` | "O `light` **derruba camada** (…) e faz **um** downgrade de modelo: escritores TDD → `model: \"sonnet\"`." |
| `SKILL.md:61` | "Escritores com `model:` por tier (`full`=opus, `light`=sonnet)" |
| `commands/oli-dev.md:3` | "`light` = menos camadas de review + escritores TDD em Sonnet" |
| `commands/oli-dev.md:17-18` | "no `light` não roda task-reviewer por task (Fase 4) e os escritores TDD vão pra `model: \"sonnet\"`." |
| `README.md:11` | "…e só os escritores TDD trocam de modelo no `light`." |
| `README.md:21-22` | "tier `light`: **menos camadas** (sem task-reviewer por task) + escritores TDD em **Sonnet 5**." |
| `evals/evals.json:36` | `"expected_gate": "Só os escritores TDD (F4) vão pra Sonnet; …"` |

**Nenhuma delas quebra teste** (§2.1). É por isso que §6 constrói o vermelho à mão.

### 3.3 Reescritas (direção, não texto final)

- `model-tiers.md:12-17` (corpo do princípio) — trocar a lista "1 downgrade no `light`" por:
  *o tier derruba camada redundante, é o único botão; **nenhum** papel troca de modelo por tier
  — escritores TDD sempre Sonnet (produção verificada por teste), julgamento sempre Opus.*
- `model-tiers.md:13-15` — o conteúdo sobre "maior volume de token, menor exigência de
  julgamento, saída verificada por execução" **não se perde**: migra para a seção "Base dos dois
  tiers" (`model-tiers.md:22-37`) como item 3, que é onde vivem as invariantes não-tier.
- `SKILL.md:35-36` — "O `light` **só** derruba camada (sem task-reviewer por task). Nenhum papel
  muda de modelo por tier."
- `SKILL.md:61` — "Escritores sempre em `model: \"sonnet\"` (nos dois tiers); task-reviewer por
  task só no `full`."
- `commands/oli-dev.md`, `README.md` — separar "isto só no `light`" (task-reviewer) de "isto
  sempre" (escritor Sonnet). Remover do bullet do `light` o que deixou de ser diferenciador.
- `evals.json:36` — reescrever o `expected_gate` para não implicar exclusividade do `light`.

### 3.4 CHANGELOG

Entrada **nova** no `[Unreleased]` já existente (não abre seção). O `[Unreleased]` hoje tem 2
entradas sob `#### Changed`, ambas commitadas; esta vira a 3ª.

As entradas históricas **não se reescrevem** (convenção Keep a Changelog) — inclusive a que diz
"Único downgrade que resta: escritores TDD → Sonnet" e a que amarra fix-subagents ao tier. São
registro do que era verdade quando escrito. A entrada nova é que corrige a leitura linear.

Bump esperado ao taguear: **MINOR** (aditivo/retrocompatível, mesmo raciocínio do redesenho
anterior). Última tag `oli-dev-v1.0.0`; `git describe` → `oli-dev-v1.0.0-4-g60853e9`. **A decisão
do bump fica para a hora de taguear**, considerando tudo acumulado em `[Unreleased]` — não é
matéria desta spec.

---

## 4. Decisão — item 2: Princípio 6, o conductor coordena

### 4.1 Onde

**Novo Princípio 6 em `SKILL.md`**, após a linha 47, antes de `## Workflow`.

Alternativas descartadas:
- **Dentro do Princípio 4** — o eixo é ortogonal ao tier. Delegação vale igual em `full` e
  `light`, e vale na Fase 0, que o tier nem toca. Misturar confunde "camada de review" com "quem
  executa a leitura", dois conceitos que a skill mantém separados de propósito.
- **Em `model-tiers.md`** — o arquivo declara na linha 19 *"Escopo desta matriz: **camadas e
  modelo**"*. Delegação de investigação não é camada de review nem modelo de tier. Além disso
  `model-tiers.md` só carrega na Fase 0 (progressive disclosure), e o princípio precisa valer em
  todas as fases. `SKILL.md` carrega sempre.

### 4.2 Texto proposto

> 6. **O conductor coordena — investigação, coleta de dados e teste vão para subagentes,
>    paralelos quando independentes.** O contexto do conductor é o recurso escasso do ciclo:
>    gastar ele lendo N arquivos é gastar o que decide. Antes de investigar, pergunte se dá pra
>    despachar; antes de despachar 2+, pergunte se são independentes — se forem, **fan-out numa
>    mensagem só**, não em sequência. Investigação roda em **Sonnet** (é leitura e síntese,
>    verificada por citação `arquivo:linha`, não por opinião) e volta com **fonte, não com
>    conselho**. **Fica no conductor:** comando determinístico de uma linha, adjudicação de
>    achado, o gate da Fase 6, e o que é do próprio estado da sessão (worktree, modelo). Isto
>    **não** é licença para empilhar review — paralelizar investigação sobre artefatos distintos
>    é o oposto de um segundo reviewer sobre o mesmo diff (`references/review-gates.md`, "o que
>    NÃO fazer").

Segue o molde dos Princípios 4 e 5: tese em negrito → justificativa causal → regra operacional →
cláusula de escape. Comprimento comparável (6–9 linhas).

### 4.3 A cláusula de escape é obrigatória, não decorativa

Sem ela, o princípio entra em tensão direta com passagens existentes que estão **corretas** e
não devem mudar:

| `arquivo:linha` | o que faz | por que fica no conductor |
|---|---|---|
| `setup-gate.md:3` | checa o modelo da própria sessão | um subagente não muda o modelo de quem o despachou |
| `setup-gate.md:11-15` | cria worktree (`EnterWorktree`) | opera sobre o estado da própria sessão |
| `pre-push-gate.md:3` | "Gate primário (você roda e mostra evidência); o hook `hooks/pre-push-gate.sh` é o backstop." | determinístico, zero token, é um dos dois gates que `model-tiers.md:35-36` diz que nunca caem |
| `review-gates.md:17-19` | "O conductor adjudica com evidência, não por deferência" | adjudicação é julgamento, não investigação |
| `finalize.md` (passos 1,3,5) | `gh pr view`, `git checkout main`, `git branch -d` | comandos únicos, sem leitura nem síntese |

### 4.4 Interação com a contagem de passes de LLM

`model-tiers.md:54` publica `full ~10 · light ~6`. Essa conta cobre dispatches de **escrita e
review** (§2.4). O Princípio 6 adiciona dispatches de **investigação**, cuja quantidade varia com
a mudança (esta spec, por exemplo, usou 5).

Deixar o número como está sem ressalva vira alegação enganosa. **Adicionar nota curta** ao lado
da contagem esclarecendo que ela cobre escrita+review, e que a investigação da Fase 1 varia com
a mudança. Não alterar o número — ele continua correto para o que mede.

### 4.5 `SKILL.md:61` vira instância, não regra solta

A cláusula "Pipeline (serial) ou Fan-out conforme dependência" da Fase 4 passa a ser um **caso
particular** do Princípio 6. Manter a frase (é operacional e específica da Fase 4), sem
duplicar a justificativa — ela agora mora no princípio.

---

## 5. Arquivos afetados

| arquivo | o que muda |
|---|---|
| `skills/dev-cycle/references/model-tiers.md` | corpo do princípio (§12-17), matriz (§45,47), item 3 na "Base dos dois tiers", nota na contagem |
| `skills/dev-cycle/SKILL.md` | linha 10, Princípio 4 (§35-36), **Princípio 6 novo**, Fase 4 (§61) |
| `commands/oli-dev.md` | frontmatter (§3), corpo (§17-18) |
| `README.md` | §11, §21-22 |
| `evals/evals.json` | `light_tier_scope.expected_gate`; **eval novo** para o Princípio 6 |
| `tests/test_references.sh` | asserts novos (§6) |
| `CHANGELOG.md` (raiz) | 3ª entrada no `[Unreleased]` |

Precedente da mesma classe: `72ab1d0` (mudança da matriz original) tocou os mesmos 10 arquivos.
Spec e plan vão em **commits separados**, antes da implementação.

**Não muda:** `hooks/*.sh` (zero menções a modelo), `.claude-plugin/plugin.json` (descrição segue
verdadeira), `references/review-gates.md`, `references/setup-gate.md`, `references/finalize.md`,
specs/plans históricos (congelados).

---

## 6. Testes (critérios observáveis)

A suíte não denuncia esta mudança sozinha (§2.1). O vermelho é construído: cada assert abaixo
**falha no repo de hoje** e passa depois.

| assert | vermelho hoje porque | trava contra |
|---|---|---|
| `! grep -q 'único downgrade' model-tiers.md` | a frase existe em `model-tiers.md:13` | a alegação obsoleta voltar numa edição futura |
| frase literal nova em `model-tiers.md` afirmando escritor Sonnet nos **dois** tiers | a frase não existe | reintroduzir split de tier no escritor |
| frase literal do Princípio 6 em `SKILL.md` | o princípio não existe | remoção silenciosa do princípio |

⚠️ **Cuidado ao escolher a frase-âncora:** `grep -qi 'nos dois tiers'` **já passa hoje**
(`model-tiers.md:16-17` — "Todo papel de julgamento roda em Opus nos dois tiers"). A âncora tem
de ser específica o bastante para estar ausente hoje. Confirmar o vermelho por execução antes de
escrever o verde — não presumir.

Padrão do repo para travar invariante (copiado de `test_references.sh:28-30`, commit `60853e9`):

```sh
grep -qi 'override deliberado' "$MT" || fail "model-tiers.md must flag the SDD override explicitly"
grep -qi '150' "$MT" || fail "model-tiers.md must state the /simplify diff threshold"
```

**Gate da Fase 6:** `bash plugins/oli-dev/tests/run_all.sh` (não pytest). CI roda `shellcheck` +
a mesma suíte em ubuntu (dash + GNU sed).

---

## 7. Riscos e mitigações

| risco | mitigação |
|---|---|
| Prosa fica contraditória e a suíte não denuncia | §6 constrói asserts que travam a frase nova e proíbem a antiga |
| Princípio 6 lido como licença para empilhar review | cláusula explícita no próprio texto do princípio (§4.2), referenciando `review-gates.md` |
| Princípio 6 lido como "Fase 0 e Fase 6 estão erradas" | cláusula de escape enumerando o que fica no conductor (§4.3) |
| Âncora de teste escolhida já passa hoje → falso verde | §6 exige confirmar o vermelho por execução antes do verde |
| Contagem `~10/~6` vira alegação enganosa com mais dispatches | nota de escopo ao lado do número (§4.4) |

---

## 8. Achado lateral (fora do escopo)

Não existe `.gitignore` em lugar nenhum do repo (`git ls-files | grep gitignore` vazio, sem
`core.excludesFile`). `.claude/worktrees/` — onde este ciclo roda — aparece como untracked no
`git status` do checkout principal. Poluição real, não mitigada.

Não é matéria desta spec. Reportar na PR para decisão separada.

---

## 9. Critérios de aceite (DoD)

- [ ] `model-tiers.md` não contém mais a alegação de downgrade exclusivo do `light`; matriz
      mostra escritor `Sonnet | Sonnet` e o fix loop descrito conforme o SDD (§3.1).
- [ ] Nenhum dos 11 pontos da tabela §3.2 continua factualmente falso.
- [ ] Princípio 6 existe em `SKILL.md`, com cláusula de escape e a ressalva sobre empilhar
      review (§4.2).
- [ ] `evals.json`: `light_tier_scope` reescrito; eval novo cobrindo o Princípio 6.
- [ ] Cada assert novo de `test_references.sh` foi observado **vermelho** antes do verde.
- [ ] `bash plugins/oli-dev/tests/run_all.sh` → `ALL GREEN`, exit 0, output colado.
- [ ] `CHANGELOG.md`: 3ª entrada no `[Unreleased]` existente; entradas históricas intactas.
