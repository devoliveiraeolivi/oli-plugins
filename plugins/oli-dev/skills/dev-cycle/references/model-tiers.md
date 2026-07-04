# Tiers de modelo — `full` (default) e `light`

Fonte única do tier de modelo do `/oli-dev`. Carregada na Fase 0.

## Princípio (o que o tier muda — e o que NÃO muda)

O tier troca **apenas o modelo dos papéis cujo modelo o conductor realmente
controla** — os despachados via `Agent`/`subagent-driven-development` com `model:`
explícito: o **staff-reviewer (Fase 2)** e, na **Fase 4**, os **escritores TDD**,
os **task-reviewers** e os **fix-subagents**. **Exceção deliberada:** o **review
final de branch** (Fase 4, fecho do subagent-driven-development) é **sempre Opus**
nos dois tiers — a guidance do próprio SDD manda o review de branch inteiro para o
modelo mais capaz, e ele é a última rede antes da Fase 5.

Escopo desta matriz: **modelo, e só modelo**. Integrações ambientes opcionais condicionadas
ao tier (quando presentes na sessão) vivem na **Fase 0** — ver `setup-gate.md`, passo 7 —
e não entram nesta fonte única.

**Justificativa = custo/latência, não qualidade.** A rede que pega bug é **idêntica**
nos dois tiers. Não use o tier como se fosse "mesma qualidade mais barato" — a aposta
honesta é: onde a produção de código pode ir pra Sonnet, o ganho de token/latência é
real e a rede de segurança continua de pé.

## O que é (e não é) controlável por tier

| Papel | Como roda | Tier controla? |
|---|---|---|
| **Conductor** (loop principal) | modelo da sessão | **Não** — sempre Opus (Fase 0). Cobre brainstorm (F1), plano (F3), adjudicação, e os gates inline `/simplify` · `verify` · `/security-review`, que herdam o Opus do conductor |
| **Escritores TDD** (Fase 4) | `Agent` / subagent-driven-development, `model:` | **SIM — modelo** |
| **Task-reviewers + fix-subagents** (Fase 4) | `Agent` dispatch do SDD, `model:` | **SIM — modelo** |
| **Review final de branch** (Fase 4, fecho do SDD) | `Agent` dispatch, `model:` | **Não por política** — sempre Opus (última rede antes da Fase 5) |
| **Staff-reviewer** (Fase 2) | `Agent` dispatch, `model:` | **SIM — modelo** |
| **`/code-review`** (Fase 5) | slash-command, fleet Haiku+Sonnet próprio | **Não** (nem modelo; nem mexemos no effort) |

Base factual (verificada): `/code-review` é um command que define o próprio fleet e opera
sobre o diff/PR — o conductor não passa `model:` pra ele. `/simplify`, `verify`,
`/security-review` são built-in e rodam no contexto do conductor (Opus). Logo o botão
honesto do tier é o **modelo dos papéis despachados com `model:` (Fases 2 e 4)** —
menos o review final de branch, fixado em Opus por política.

**Fora do tier por decisão (não por limitação): Haiku.** A guidance do SDD permite
o tier mais barato p/ fixes de 1 arquivo e implementação-transcrição, mas avisa que
modelos mais baratos gastam 2–3× mais turnos em trabalho multi-step — e TDD é
multi-step por natureza. O piso do `light` é Sonnet; revisite só com medição.

## A matriz

| Papel | `full` (default) | `light` |
|---|---|---|
| Conductor (+ F1 brainstorm + F3 plano + adjudicação + inline `/simplify` `verify` `/security-review`) | Opus | Opus |
| Fase 5 — `/code-review` (fleet próprio) | inalterado | inalterado |
| Fase 4 — escritores TDD | Opus | **Sonnet** (`model: "sonnet"`) |
| Fase 4 — task-reviewers + fix-subagents | Opus | **Sonnet** (`model: "sonnet"`) |
| Fase 4 — **review final de branch** | **Opus** | **Opus** (sempre — última rede antes da Fase 5) |
| Fase 2 — staff-reviewer | Opus | **Sonnet** (`model: "sonnet"`) |

- **`full`** = comportamento idêntico ao `/oli-dev` de hoje (tudo Opus).
- **`light`** = os papéis despachados das Fases 2 e 4 em Sonnet — escritores TDD,
  task-reviewers, fix-subagents e staff-reviewer. O ganho vem sobretudo dos
  **escritores** (vários subagentes, várias tasks — o maior sink de tokens).
  Coerência interna: o staff-reviewer (que revisa o *spec inteiro*) já era Sonnet
  no light; o reviewer de uma task individual não deve custar mais que ele.

## Invocação e parsing

```
/oli-dev <ideia>          → tier full (default; = hoje)
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
Como o default é `full`, o caminho seguro é o padrão e o `light` é sempre deliberado.
(Isto é *prior* sobre a ideia; o sub-gate de `/security-review` na Fase 5 continua
independente do tier e detecta superfície sensível pelo diff.)

## Persistência do tier (resume)

O default `full` é o fallback seguro — perder o tier num resume degrada para `full`,
nunca para algo mais arriscado. Para não perder o ganho num ciclo retomado:
- Ao escrever o plano (Fase 3), **grave o tier no cabeçalho do plano**.
- O resume da Fase 0 (`setup-gate.md`) **lê o tier do plano** ao retomar de spec+plano → Fase 4.
  Ausente/antigo → assuma **`full`**.
