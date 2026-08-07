# Design — Opus julga, Sonnet produz e coleta

**Data:** 2026-08-07
**Repo alvo:** `oli-plugins` (plugin `oli-dev` modifica a si mesmo)
**Tier do ciclo:** `full`
**Status:** revisada (staff-review incorporado — ver Apêndice A)
**Origem:** `handoffs/2026-08-07-sonnet-escritores-tdd-full-handoff.md` (item 1) +
feedback direto do usuário em 2026-08-07 (item 2)

---

## 1. Problema e objetivo

Duas mudanças com a mesma raiz, por isso uma spec só.

**Item 1 — o escritor TDD é Opus no `full` sem justificativa própria.**
`model-tiers.md:45` fixa `| **F4 — escritores TDD** | Opus | **Sonnet** |`. É o único papel
que muda de modelo por tier. Mas o escritor nunca foi papel de julgamento neste design: sua
saída é conferida por **execução de teste** (vermelho→verde), não por opinião de modelo. Quem
julga — staff-reviewer (F2), adjudicação, conductor — já é Opus nos dois tiers
(`model-tiers.md:16-17`).

**Item 2 — a skill não diz quem investiga.** O Princípio 5 (`SKILL.md:38-47`) manda "não presuma
o que não dá pra verificar", mas nunca diz **quem** vai atrás da fonte — hoje, implicitamente,
sempre o próprio conductor. Fora da Fase 4, não há uma linha mandando delegar leitura/coleta, e
o único lugar que avalia paralelismo é uma cláusula solta da Fase 4 (`SKILL.md:61`).

**Tese que une os dois:**

> **Opus julga. Sonnet produz e coleta.** O escritor TDD produz código verificado por execução
> de teste. O agente de investigação coleta fatos verificados por citação `arquivo:linha`.
> Nenhum dos dois emite opinião — logo, nenhum dos dois precisa de Opus.

### ⚠️ Premissa não medida (rotulada conforme Princípio 5)

**Que Sonnet seja adequado ao escritor TDD no `full` é premissa de design, não medição.** Não há
medição no repo, e `specs/2026-06-30-oli-dev-model-tiers-design.md:7` registra que o headline
original de tiering **foi refutado** — a justificativa honesta virou custo/latência.

O argumento que sustenta a premissa é estrutural, não empírico: a saída do escritor é validada
por execução de teste, e o SDD tem escalada embutida para quando Sonnet não dá conta
(`subagent-driven-development/SKILL.md:174-175`, `:244-250`). **Reverter é barato** — é trocar
uma célula de tabela. Aceitar sem medição é decisão consciente, não descuido.

### Não-objetivos (YAGNI)

- **Não** mexer em hook ID, `.pre-commit-hooks.yaml`, `policies/ENFORCEMENT.md`. Hooks são
  independentes de tier (grep confirma zero menções a modelo em `hooks/*.sh`).
- **Não** rebaixar papel de julgamento. Staff-reviewer, adjudicação e conductor seguem Opus.
- **Não** mexer em `/code-review`, `/simplify`, `verify`, `/security-review` — fleet próprio.
- **Não** introduzir Haiku (`model-tiers.md:64-67` já documenta a exclusão).
- **Não** decidir o bump de versão — fica para a hora de taguear (§3.4).

---

## 2. Base factual (verificada, não inferida)

Levantada por 5 agentes de investigação paralelos, revisada por staff-reviewer cético, e cada
citação load-bearing reconfirmada por leitura direta do arquivo antes de escrever.

### 2.1 A suíte de testes é uma rede fraca para esta mudança

Baseline (`bash plugins/oli-dev/tests/run_all.sh`): `ALL GREEN`, `exit=0` — 6 arquivos de teste,
23+15 asserts numeradas de hook, `shellcheck` limpo.

Todos os asserts de modelo em `test_references.sh` são **presence checks**, nunca **pairing
checks**:

```sh
# tests/test_references.sh:17-18
grep -qi  'sonnet' "$MT" || fail "model-tiers.md must mention Sonnet"
grep -qi  'opus'   "$MT" || fail "model-tiers.md must mention Opus"
```

Como `Opus` continua no doc (conductor, staff-reviewer) e `Sonnet` também, **a suíte fica
`ALL GREEN` mesmo com a prosa logicamente contraditória**. `test_evals.sh` só valida schema,
nunca conteúdo — `light_tier_scope` sequer está no set de ids obrigatórios.

**Consequência:** o vermelho não vem de graça. Ver §6.

### 2.2 A célula `light` do fix loop é inalcançável

`model-tiers.md:47`: `| **F4 — fix-subagents** (só se houver achado) | Opus | Sonnet |`.

Gatilho do fix loop no SDD 6.2.0 (versão ativa, confirmada em `installed_plugins.json`):

> `subagent-driven-development/SKILL.md:304-305` — "The loop triggers when the review reports
> spec ❌, any Critical or Important finding, or a ⚠️ item you confirmed as a real gap."

No `light`, o task-reviewer **não roda** (`model-tiers.md:46`) e o review final de branch
**não roda** (`:48`). Nada dispara o fix loop.

**Origem: bug de propagação, não decisão.** Antes de `60853e9` a matriz tinha uma linha
combinada `| Fase 4 — task-reviewers + fix-subagents | Opus | **Sonnet** |` (confirmado por
`git show 60853e9^`). O commit separou em duas, mudou task-reviewer para "não roda" no `light`,
e não propagou. A mensagem do commit **não menciona fix-subagents uma única vez**.

### 2.3 O fix loop não é papel com modelo próprio — e não é a única rota de re-dispatch

> `subagent-driven-development/SKILL.md:322` — "Rounds 1-3 — **resume the original implementer**."
> `subagent-driven-development/SKILL.md:328` — "Rounds 4-5 — dispatch a fresh implementer **on a
> more capable model**"
> `subagent-driven-development/SKILL.md:174-175` — "**Fix-loop escalation (rounds 4-5)**: use a
> model at least one tier above the implementer that got stuck."

O fix é o **escritor retomado**, com escalada embutida no SDD. Não é papel a alocar. A linha
`| Opus | Sonnet |` está errada nas duas colunas.

**Rota independente que a primeira versão desta spec não considerou** (achado do staff-review):

> `subagent-driven-development/SKILL.md:244-250` — "**BLOCKED:** The implementer cannot complete
> the task. (…) 2. If the task requires more reasoning, **re-dispatch with a more capable
> model** (…) **Never** ignore an escalation or force the same model to retry without changes."

`BLOCKED` **não depende do task-reviewer** e vale nos dois tiers. Com escritor em Sonnet, a rota
`BLOCKED` → modelo mais capaz passa a existir também no `light`. Dizer "no `light` nada dispara"
sem qualificar seria falso — ver a célula proposta em §3.1.

### 2.4 A contagem de passes de LLM: não medir onde não se sabe

`model-tiers.md:54` e `README.md:33` publicam `full ~10 · light ~6`. **Nenhum arquivo documenta
a fórmula.** Uma reconstrução contando dispatches (`1 staff-reviewer + 4 escritores +
4 task-reviewers + 1 code-review`) fecha exato em 10/6 — mas trata `/code-review` como **1**,
e `specs/2026-06-30-oli-dev-model-tiers-design.md:32` diz, "verificado por leitura do código",
que ele "hardcoda **Haiku+5×Sonnet+Haiku**" — 7 passes. A convenção de contagem é arbitrária e
não documentada; o encaixe em 10/6 não prova a fórmula.

**O que se afirma, e basta:** esta mudança **não altera dispatch nenhum** — só troca qual modelo
roda em dispatches que já existiam. Qualquer que seja a convenção, o número publicado continua
tão válido quanto era. **Nenhuma edição** em `model-tiers.md:54` nem `README.md:33`.

### 2.5 O que a skill já diz sobre delegar (para não duplicar)

- `SKILL.md:61` — Fase 4: "Pipeline (serial) ou Fan-out (`dispatching-parallel-agents`) conforme
  dependência." **Única** menção a paralelismo na skill; só cobre escritores de task.
- `setup-gate.md` (Fase 0 inteira), `pre-push-gate.md:3` ("Gate primário (você roda e mostra
  evidência)"), `SKILL.md:69-78` (Verification), `finalize.md` — todos escritos com o conductor
  executando diretamente, sem menção a delegar.

**Lacuna:** delegar investigação fora da Fase 4 não é coberto; avaliar paralelismo existe só
como cláusula pontual da Fase 4.

### 2.6 Dois riscos de contradição a desarmar

**(a) Empilhar review.** `review-gates.md:68-74` — "Se você está por despachar um reviewer
adicional 'só pra conferir', a pergunta certa é se existe **artefato novo** ou apenas o mesmo
diff relido." Isso é sobre redundância de **julgamento**. Paralelizar **investigação** sobre
artefatos distintos é o eixo oposto — mas lê como contradição se não for separado no texto.

**(b) Modelo herdado.** `subagent-driven-development/SKILL.md:177-179` — "**Always specify the
model explicitly when dispatching a subagent.** An omitted model inherits your session's model —
often the most capable and most expensive — which silently defeats this section." Um princípio
que manda delegar sem mandar fixar o modelo faz o conductor vazar Opus em toda investigação.

---

## 3. Decisão — item 1: escritor TDD = Sonnet nos dois tiers

### 3.1 A matriz depois

| Papel / camada | `full` (default) | `light` |
|---|---|---|
| **Conductor** (F1 · F3 · adjudicação · `/simplify` `verify` `/security-review` inline) | Opus | Opus |
| **Investigação / coleta** (qualquer fase — Princípio 6) | Sonnet | Sonnet |
| **F2 — staff-reviewer** (sobre a spec) | Opus | Opus |
| **F4 — escritores TDD** | **Sonnet** | **Sonnet** |
| **F4 — task-reviewer por task** | Opus | **não roda** |
| **F4 — fix loop** (SDD §4, só com achado do task-reviewer) | escritor retomado (Sonnet); rodada 4+ escala ≥1 tier acima (SDD `:174-175`) | **não roda** — sem task-reviewer, nada dispara |
| **F4 — rota `BLOCKED`** (SDD `:244-250`, independente de review) | vale | **vale** — pode escalar modelo |
| **F4 — review final de branch** | **não roda** (coberto pela F5) | **não roda** |
| **F5 — `/code-review`** | fleet próprio, inalterado | inalterado |
| **F5 — `/simplify`** | se diff > ~150 linhas | se diff > ~150 linhas |
| **F5 — `verify`** | sempre | sempre |
| **F6 — pre-push gate** | sempre | sempre |

Notas:
- A linha do escritor **fica na matriz** mesmo sem variar. A matriz já tem linhas que não variam
  (`F2 Opus|Opus`, `F5 verify sempre|sempre`) — é **retrato completo, não diff**. Manter torna
  mais difícil reintroduzir um split de tier numa edição futura.
- A linha de **investigação** entra na matriz porque `model-tiers.md:3` se declara "fonte única"
  e `:19` define o escopo como "camadas e modelo". Um papel despachado com modelo fixo pertence
  aqui — o Princípio 6 aponta para cá em vez de fixar modelo por conta própria.

### 3.2 Efeito estrutural

Depois da mudança, **nenhum papel troca de modelo por tier**. Duas linhas ainda variam — ambas
por **camada**, não por modelo: `task-reviewer` (roda / não roda) e `fix loop` (consequência da
primeira).

Efeito secundário a nomear, que não é downgrade: com escritor em Sonnet, o `full` mantém o teto
de escalada da rodada 4 (≥1 tier acima de Sonnet); o `light`, sem fix loop, só escala pela rota
`BLOCKED`.

**Frases que ficam factualmente falsas ou viram hedge desnecessário** (16 pontos; nenhuma quebra
teste — §2.1):

| # | `arquivo:linha` | problema |
|---|---|---|
| 1 | `model-tiers.md:13` | "**Um único downgrade de modelo:** os escritores TDD (Fase 4) no `light`" — falso |
| 2 | `model-tiers.md:45` | célula `Opus \| Sonnet` — vira `Sonnet \| Sonnet` |
| 3 | `model-tiers.md:47` | linha do fix loop — errada nas duas colunas (§2.3) |
| 4 | `SKILL.md:10` | "`light` (menos camadas de review + escritores TDD em Sonnet)" — atribui ao `light` o que vale nos dois |
| 5 | `SKILL.md:35-36` | "faz **um** downgrade de modelo" — falso |
| 6 | `SKILL.md:61` | "`full`=opus, `light`=sonnet" — falso |
| 7 | `commands/oli-dev.md:3` | mesmo padrão do #4 |
| 8 | `commands/oli-dev.md:17-18` | mesmo padrão do #4 |
| 9 | `README.md:11` | "só os escritores TDD trocam de modelo no `light`" — falso |
| 10 | `README.md:21-22` | "+ escritores TDD em **Sonnet 5**" no bullet do `light` — deixou de diferenciar |
| 11 | `evals.json:36` | "**Só** os escritores TDD (F4) vão pra Sonnet" — implica exclusividade |
| 12 | `SKILL.md:29` | hedge "não modelo **de julgamento**" — o qualificador vira desnecessário |
| 13 | `model-tiers.md:5` | idem (título da seção) |
| 14 | `commands/oli-dev.md:17` | idem |
| 15 | `README.md:38` | "não em modelo **de review**" — idem |
| 16 | `evals.json:36` | "não modelo **de julgamento**" — idem |

Os itens 12-16 não são *falsos*: são o hedge que a mudança torna dispensável. Sem cortá-los,
`model-tiers.md` fica com o **título** dizendo "não modelo *de julgamento*" e o **corpo logo
abaixo** dizendo "nenhum papel troca de modelo por tier".

### 3.3 Reescritas (direção, não texto final)

- `model-tiers.md:12-17` — trocar a lista "1 downgrade no `light`" por: *o tier derruba camada
  redundante, é o único botão; nenhum papel troca de modelo por tier.*
- `model-tiers.md:13-15` — o conteúdo sobre "maior volume de token, menor exigência de
  julgamento, saída verificada por execução" **não se perde**: migra para a seção "Base dos dois
  tiers" (`:22-37`), onde vivem as invariantes não-tier.
- `SKILL.md:35-36`, `:61`, `commands/oli-dev.md`, `README.md` — separar "isto só no `light`"
  (task-reviewer) de "isto sempre" (escritor Sonnet); cortar o qualificador dos itens 12-16.
- `evals.json:36` — reescrever para não implicar exclusividade do `light`.

### 3.4 CHANGELOG e versão

Entrada **nova** no `[Unreleased]` existente (não abre seção); hoje tem 2 entradas sob
`#### Changed`, esta vira a 3ª. Entradas históricas **não se reescrevem** (Keep a Changelog) —
inclusive a que diz "Único downgrade que resta: escritores TDD → Sonnet". São registro do que
era verdade quando escrito.

Última tag `oli-dev-v1.0.0`; `git describe` → `oli-dev-v1.0.0-4-g60853e9`. Bump esperado
**MINOR**, mas **a decisão fica para a hora de taguear** — não é matéria desta spec.

---

## 4. Decisão — item 2: Princípio 6, o conductor coordena

### 4.1 Onde, e a divisão de texto

**Princípio 6 curto em `SKILL.md`** (após a linha 47) + **detalhe em `references/review-gates.md`**.

- `SKILL.md` carrega **sempre**; o princípio precisa valer em todas as fases (a Fase 0 inclusive,
  que o tier nem toca). `model-tiers.md` só carrega na Fase 0 — erra o alvo como local do
  princípio. Mas o **modelo** do investigador mora na matriz (§3.1), que é a fonte única disso.
- `SKILL.md` deve ficar **magro** (`specs/2026-06-24-oli-dev-plugin-design.md:90-94` — "manter o
  custo de token do maestro baixo em todo ciclo"). Hoje: 78 linhas / 995 palavras. Um princípio
  de 9 linhas custaria ~+13% de palavras. Por isso a justificativa causal e o limite
  anti-empilhamento vão para `review-gates.md`, que já tem a seção "O que NÃO fazer" e já carrega
  nas Fases 2 e 5.
- **Não** dentro do Princípio 4: o eixo é ortogonal ao tier.

### 4.2 Texto proposto — `SKILL.md`

> 6. **O conductor coordena — investigação e coleta de dados vão para subagentes, paralelos
>    quando independentes.** O contexto do conductor é o recurso escasso do ciclo: gastá-lo
>    lendo N arquivos é gastar o que decide. Antes de investigar, pergunte se dá pra despachar;
>    antes de despachar 2+, se são independentes — se forem, **fan-out numa mensagem só**. O
>    investigador volta com **fonte (`arquivo:linha`), não com conselho**, e é despachado com
>    `model:` **explícito** (omitir herda o modelo da sessão — SDD `SKILL.md:177-179`); qual
>    modelo, ver `references/model-tiers.md`. **Fica no conductor:** adjudicação **e a
>    verificação do achado que a sustenta**, os gates `verify` (F5) e Fase 6, comando
>    determinístico de uma linha, e o estado da própria sessão (worktree, modelo). Limite:
>    `references/review-gates.md`.

### 4.3 O que fica no conductor — e por quê

| o que | `arquivo:linha` | por quê |
|---|---|---|
| modelo da própria sessão | `setup-gate.md:3` | subagente não muda o modelo de quem o despachou |
| criar worktree | `setup-gate.md:11-15` | opera sobre o estado da própria sessão |
| **`verify` (F5)** | `review-gates.md:39-40`; `model-tiers.md:35-36` | um dos **dois** gates que "nunca caem"; delegar transforma evidência em relato |
| **gate da F6** | `pre-push-gate.md:3` | o outro dos dois; determinístico, zero token |
| adjudicação **e a checagem que a sustenta** | `review-gates.md:17-19` | "claim de reviewer que seja load-bearing (…) **é checado antes de virar ação**" |
| comando determinístico de 1 linha | `finalize.md` (passos 1,3,5) | sem leitura nem síntese; delegar não paga |

**A distinção que fecha o buraco (B3 do staff-review):** coleta **antes** de existir achado se
delega; verificação **de** um achado é do conductor. Sem isso, adjudicar sobre relato de
subagente reintroduz o "afirma sem checar" com um hop a mais e um selo a mais.

**Nota sobre "testes":** rodar teste **exploratório** (baseline, repro) é coleta — delega. Rodar
os **gates** `verify` (F5) e Fase 6 é do conductor, sempre. `model-tiers.md:35-36` os nomeia
como "os únicos gates que produzem verdade objetiva em vez de opinião".

### 4.4 Texto proposto — `references/review-gates.md`

Parágrafo curto na seção "O que NÃO fazer: empilhar review sobre review" (`:68-74`), separando
os eixos: paralelizar **investigação** sobre artefatos distintos ≠ despachar um segundo
**reviewer** sobre o mesmo artefato. O primeiro é o Princípio 6; o segundo continua proibido.

---

## 5. Arquivos afetados

| arquivo | o que muda |
|---|---|
| `skills/dev-cycle/references/model-tiers.md` | corpo do princípio (§12-17), matriz (§45,47 + 2 linhas novas), item na "Base dos dois tiers", hedge do título (§5) |
| `skills/dev-cycle/SKILL.md` | §10, Princípio 4 (§29,35-36), **Princípio 6 novo**, Fase 4 (§61) |
| `skills/dev-cycle/references/review-gates.md` | parágrafo na seção "O que NÃO fazer" (§4.4) |
| `skills/dev-cycle/references/setup-gate.md` | §13 — afirma que `.claude/worktrees/` está "já no `.gitignore`"; **é falso** (§8) |
| `commands/oli-dev.md` | §3, §17-18 |
| `README.md` | §11, §21-22, §38 |
| `evals/evals.json` | `light_tier_scope` reescrito; **eval novo** = anti-empilhamento (§6) |
| `tests/test_references.sh` | asserts estruturais novos (§6) |
| `CHANGELOG.md` (raiz) | 3ª entrada no `[Unreleased]` |
| `handoffs/2026-08-07-…-handoff.md` | commitado (era untracked; a spec o cita como origem) |

Precedente de mudança da mesma classe: `72ab1d0` e `60853e9`.

**Não muda:** `hooks/*.sh` (zero menções a modelo), `.claude-plugin/plugin.json` (a descrição
"conductor e review sempre Opus, tier trocando camadas de review" fica **mais** verdadeira),
`references/finalize.md`, specs/plans históricos (congelados).

---

## 6. Testes (critérios observáveis)

A suíte não denuncia esta mudança sozinha (§2.1). O vermelho é construído — e cada assert trava
**a condição**, não uma string de prosa (correção do staff-review; a v1 desta spec propunha
`! grep -q 'único downgrade'`, que baniria uma frase e não o invariante).

| assert | vermelho hoje (verificado por execução) | trava |
|---|---|---|
| nenhuma linha da matriz é `Opus` no `full` e `Sonnet` no `light`:<br>`grep -nE '^\|.*\| *Opus *\|.*Sonnet' model-tiers.md` | retorna **2 linhas** (`:45`, `:47`); vazio depois | a condição inteira do item 1 — sobrevive a qualquer reescrita de prosa. Sem falso positivo nas linhas `Opus\|Opus` (verificado) |
| Princípio 6 existe:<br>`grep -qE '^6\. ' SKILL.md` | hoje só há `1.`–`5.` (verificado) | remoção do princípio; sobrevive a reescrita do corpo |

**Nota de implementação:** `test_references.sh` roda com `set -eu`. Assert de ausência precisa da
forma `if grep -qE … ; then fail …; fi`, não `! grep …` solto.

**Eval novo** (`evals.json`): não um eval de "o conductor delega" — isso é heurística, não gate,
e todos os 8 evals existentes têm a forma **recusa sob pressão**. O eval com forma de gate é o
**inverso**: pressão para despachar um segundo reviewer disfarçado de "investigação", com
`expected_gate` = a recusa de `review-gates.md:68-74`.

**Gate da Fase 6:** `bash plugins/oli-dev/tests/run_all.sh` (não pytest). CI roda `shellcheck` +
a mesma suíte em ubuntu (dash + GNU sed).

---

## 7. Riscos e mitigações

| risco | mitigação |
|---|---|
| Prosa contraditória e a suíte não denuncia | asserts estruturais que travam a condição (§6) |
| Princípio 6 lido como licença para empilhar review | limite explícito em `review-gates.md` (§4.4) + ponteiro no princípio |
| Princípio 6 lido como "delegue o `verify`" | `verify` e F6 nomeados na cláusula do que fica (§4.3) |
| Conductor delega sem `model:` e vaza Opus | pin explícito no princípio, com a citação do SDD (§4.2) |
| Adjudicação sobre relato de subagente | distinção coleta-antes / verificação-de (§4.3) |
| Sonnet insuficiente pro escritor no `full` | premissa rotulada (§1); escalada do SDD é a rede; reverter = trocar 1 célula |

---

## 8. Achado lateral incorporado

Não existe `.gitignore` no repo (`git ls-files | grep -c gitignore` → `0`). Duas consequências:

1. `.claude/worktrees/` aparece como untracked no `git status` do checkout principal.
2. **`setup-gate.md:13` afirma que ele está "já no `.gitignore`" — o doc está mentindo.**

O item 2 é uma linha e entra neste ciclo (`review-gates.md:55-63` — "achado pequeno → conserta
agora, completo, não adia"). O item 1 (criar `.gitignore`) fica fora: é decisão de repo, não do
plugin — reportar na PR.

---

## 9. Critérios de aceite (DoD)

- [ ] `grep -nE '^\|.*\| *Opus *\|.*Sonnet' model-tiers.md` → **vazio**.
- [ ] Nenhum dos **16** pontos da tabela §3.2 continua falso ou com hedge dispensável.
- [ ] Matriz tem as linhas de **investigação/coleta** e de **rota `BLOCKED`** (§3.1).
- [ ] Princípio 6 existe em `SKILL.md`, curto, com o pin de `model:` explícito e a cláusula do
      que fica no conductor incluindo **`verify` (F5)** e **F6**.
- [ ] `review-gates.md` separa investigação paralela de review empilhado (§4.4).
- [ ] `setup-gate.md:13` não afirma mais que `.claude/worktrees/` está no `.gitignore`.
- [ ] `evals.json`: `light_tier_scope` reescrito; eval novo é **anti-empilhamento**, não
      "conductor delega".
- [ ] Cada assert novo foi observado **vermelho** antes do verde.
- [ ] `bash plugins/oli-dev/tests/run_all.sh` → `ALL GREEN`, exit 0, output colado.
- [ ] `CHANGELOG.md`: 3ª entrada no `[Unreleased]`; entradas históricas intactas.
- [ ] Handoff commitado.

---

## Apêndice A — Staff-review: achados → resolução

| # | achado | resolução |
|---|---|---|
| B1 | Princípio fixava modelo fora da fonte única, contra o argumento da própria §4.1 | **Aceito, saída própria.** Linha de investigação entra na matriz (§3.1); o princípio aponta pra ela. O reviewer ofereceu "tirar o pin **ou** botar na matriz" — tirar descartaria o pedido explícito do usuário |
| B2 | Cláusula de escape esquecia o `verify` (F5); princípio mandava "teste" pra subagente | **Aceito.** "teste" saiu do texto; `verify` nomeado em §4.3 + nota separando teste exploratório de gate |
| B3 | Princípio não separava coletar de ler-para-julgar | **Aceito.** Regra explícita em §4.3 |
| B4 | Separar os dois itens em ciclos distintos | **Rejeitado por decisão do usuário** (2026-08-07), com o argumento apresentado. Os 3 blockers tinham correção concreta; separar custaria 2 ciclos completos para mudança só de doc |
| B5 | Assert negativo é frágil; assert estrutural trava a condição | **Aceito.** §6 reescrita; ambos os asserts verificados vermelhos por execução |
| L1 | 5 lugares com hedge "não modelo *de julgamento*" fora da lista | **Aceito.** Tabela §3.2 foi de 11 para 16 pontos |
| L2 | "única diferença é o task-reviewer" é falso | **Aceito.** §3.2 diz 2 linhas, ambas por camada; teto de escalada nomeado |
| L3 | Rota `BLOCKED` do SDD dispara re-dispatch independente do task-reviewer | **Aceito** — achado novo. §2.3 + linha própria na matriz |
| L4 | Eval do Princípio 6 é categoria errada | **Aceito.** Trocado pelo eval inverso (anti-empilhamento) |
| L5 | "precedente `72ab1d0` tocou os mesmos 10 arquivos" é falso | **Aceito.** Alegação removida |
| L6 | §4.4 (nota na contagem) é hedge sobre hedge | **Aceito.** Seção cortada; §2.4 rebaixa a fórmula a reconstrução não-provada |
| P1 | `setup-gate.md:13` afirma `.gitignore` que não existe | **Aceito.** Entra no escopo (§8) |
| P2 | Handoff untracked; spec cita fonte inacessível | **Aceito** (decisão do usuário): commitar |
| P4 | Custo de token do `SKILL.md` | **Aceito.** Princípio curto no SKILL.md, detalhe em `review-gates.md` (§4.1) |
| ⚠️1 | Adequação do Sonnet é premissa, não medição | **Aceito.** Rotulada em §1 |

**Não verificáveis registrados** (do staff-review, sem ação): se o harness honra `model:` nos
dispatches do SDD; interação do `/ponytail lite` com escritor Sonnet; se `~10/~6` bate com
telemetria real.
