# Tiers — `full` (default) e `light`

Fonte única do tier do `/oli-dev`. Carregada na Fase 0.

## Princípio: o tier troca **camadas de review**, não modelo

O custo e a latência do ciclo vêm do **número de passes de LLM sobre o mesmo código**, não do
modelo de cada passe. E downgrade de modelo num gate de review economiza no lugar errado:
produz palpite com selo de "revisado" — exatamente o que o `review-gates.md` chama de pior que
não ter reviewer. Logo:

- **O tier derruba camada redundante.** É o único botão.
- **Nenhum papel troca de modelo por tier.** Escritores TDD são Sonnet por padrão; conductor,
  staff-reviewer (Fase 2) e adjudicação são sempre Opus. O que varia entre `full` e `light` é
  **camada** — o task-reviewer por task roda ou não roda.

Escopo desta matriz: **camadas e modelo**. Integrações ambientes opcionais condicionadas ao tier
(quando presentes na sessão) vivem na **Fase 0** — ver `setup-gate.md`, passo 7.

## Base dos dois tiers (isto não é tier — é o fluxo e o modelo)

Três decisões valem igualmente em `full` e `light`:

1. **Sem review final de branch na Fase 4.** O SDD
   (`superpowers:subagent-driven-development`) prescreve um whole-branch review no fecho — e a
   **Fase 5 roda `/code-review` sobre o mesmo diff, com fleet maior**. É o mesmo trabalho duas
   vezes. A Fase 5 **substitui** esse gate, não o dispensa.
   ⚠️ **Override deliberado do SDD** — não re-adicione por deferência à skill invocada.
2. **`/simplify` condicional:** só quando o diff passa de **~150 linhas alteradas**
   (`git diff --stat` vs. `main`). Em diff pequeno ele rende churn cosmético e ainda cobra a
   adjudicação do conductor. Em dúvida, rode.
3. **Escritores TDD sempre em Sonnet**, nos dois tiers. É o papel de maior volume de token e o
   de menor exigência de julgamento — o que ele produz é verificado por **execução de teste**,
   não por opinião de modelo. Quando Sonnet não dá conta, o SDD escala sozinho: fix loop
   rodada 4+ (`subagent-driven-development/SKILL.md:174-175`) e rota `BLOCKED`
   (`subagent-driven-development/SKILL.md:244-250`).
   ⚠️ **Premissa de design, não medição** — ver
   `docs/superpowers/specs/2026-08-07-oli-dev-opus-julga-sonnet-produz-design.md`, §1. Reverter
   custa uma célula.

O que **nunca** cai, em nenhum tier: **Fase 6** (lint/test/typecheck — determinístico, zero token)
e o **`verify`** da Fase 5. São os únicos gates que produzem verdade objetiva em vez de opinião;
foi por isso que sobreviveram ao corte.

## A matriz

| Papel / camada | `full` (default) | `light` |
|---|---|---|
| **Conductor** (F1 brainstorm · F3 plano · adjudicação · `/simplify` `verify` `/security-review` inline) | Opus | Opus |
| **F2 — staff-reviewer** (sobre a spec) | Opus | **Opus** |
| **F4 — escritores TDD** | **Sonnet** (`model: "sonnet"`) | **Sonnet** (`model: "sonnet"`) |
| **F4 — task-reviewer por task** | Opus | **não roda** |
| **F4 — fix loop** (SDD §4) | 1-3: retoma escritor; 4-5: fresco ≥1 tier; teto 5 (`subagent-driven-development/SKILL.md:174-175,320,328`) | **não roda** |
| **F4 — rota `BLOCKED`** (SDD `subagent-driven-development/SKILL.md:244-250`, indep. de review) | vale | **vale** — pode escalar modelo |
| **F4 — review final de branch** | **não roda** (coberto pela F5) | **não roda** |
| **F5 — `/code-review`** | fleet próprio, inalterado | inalterado |
| **F5 — `/simplify`** | se diff > ~150 linhas | se diff > ~150 linhas |
| **F5 — `verify`** | sempre | sempre |
| **F6 — pre-push gate** | sempre | sempre |

Passes de LLM numa mudança de 4 tasks: **`full` ~10 · `light` ~6** (era ~15 nos dois tiers).

### Por que o `light` pode dispensar o task-reviewer
O SDD diz *"never skip the task review"* — dispensá-lo é **override deliberado**, e a rede que
sobra é explícita: (a) a task roda em **TDD**, e o ciclo vermelho→verde é verificação por
**execução**, não por opinião; (b) o **`/code-review` da Fase 5** lê o diff inteiro com contexto
fresco; (c) a **Fase 6** roda lint+test de verdade, com evidência colada.
O que se perde é a checagem de **aderência à spec por task** — e é por isso que `light` é
deliberado, nunca default.

### Fora dos tiers por decisão (não por limitação): Haiku
A guidance do SDD permite o tier mais barato p/ fixes de 1 arquivo e implementação-transcrição,
mas avisa que modelos mais baratos gastam 2–3× mais turnos em trabalho multi-step — e TDD é
multi-step por natureza. O piso é Sonnet nos dois tiers; revisite só com medição.

## Invocação e parsing

```
/oli-dev <ideia>          → tier full (default)
/oli-dev light <ideia>    → tier light
/oli-dev full <ideia>     → tier full explícito
/oli-dev finalize         → modo finalize (Fase 8), sem tier
```

Regras (comparações **case-insensitive**; `$ARGUMENTS` já trimado; `W1` = 1ª palavra):

1. `W1` == `finalize` (match **exato**) → modo finalize (Fase 8).
2. Senão, `W1` ∈ {`light`, `full`} **E** existe ≥1 palavra depois → tier = `W1`; ideia = o resto.
3. Senão → tier não informado (default **`full`**); ideia = todo o `$ARGUMENTS`.

Casos de borda:
- **Eco da interpretação:** ao reconhecer um tier explícito, a Fase 0 **anuncia** *"Interpretei:
  tier=`<t>`, ideia='`<...>`'"* antes de agir — deixa visível uma colisão (ex.: ideia que
  começa com a palavra "light"/"full").
- `/oli-dev light` (só o token, sem ideia) ou `/oli-dev light finalize` → **peça
  esclarecimento**; não rode um ciclo com ideia vazia nem com a ideia == palavra-modo.

## Piso de segurança (advisory com ack)

Se o usuário pedir **`light`** numa mudança que toca **contrato/enforcement**
(`policies/ENFORCEMENT.md`, IDs de hook no `.pre-commit-hooks.yaml`, `security.yml`
reusável, pins em `common.sh`) **ou superfície sensível** (auth, secrets, SQL/RPC, rede,
cripto): **recomende `full`** e peça **confirmação explícita** (ack) para seguir em `light`.
Aqui o que falta no `light` é a aderência-à-spec por task — justo o que erra caro em contrato.
Como o default é `full`, o caminho seguro é o padrão e o `light` é sempre deliberado.
(Isto é *prior* sobre a ideia; o sub-gate de `/security-review` na Fase 5 continua
independente do tier e detecta superfície sensível pelo diff.)

## Persistência do tier (resume)

O default `full` é o fallback seguro — perder o tier num resume degrada para `full`,
nunca para algo mais arriscado. Para não perder o ganho num ciclo retomado:
- Ao escrever o plano (Fase 3), **grave o tier no cabeçalho do plano**.
- O resume da Fase 0 (`setup-gate.md`) **lê o tier do plano** ao retomar de spec+plano → Fase 4.
  Ausente/antigo → assuma **`full`**.
