# Spec — redesenho do `/oli-dev` para a geração 5: menos roteiro, mesmo rigor

**Data:** 2026-08-07 · **Repo:** `oli-plugins` · **Tier do ciclo:** `light`
**Fonte:** `handoffs/2026-08-07-oli-dev-peso-do-ciclo-handoff.md` (autocontido, nesta branch).
**Critério de desenho:** <https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models>
(lido na Fase 1 deste ciclo, não citado de memória).

## Goal

A skill `dev-cycle` é roteiro passo a passo. Um ciclo que entregou **~80 linhas de
documentação** custou **22+ despachos de subagente, 5 rodadas de fix e 30+ passes de LLM**
(handoff §1). Este redesenho remove o roteiro que substitui julgamento, preserva todo gate
que impede perda de trabalho, e conserta 3 bugs que continuam na `main`.

Dois ganhos, de naturezas diferentes — registrados separados porque só um é medível:

- **Medível — passes de LLM.** Numa mudança de 4 tasks: **22+ → ~8**. Vem de três cortes
  de camada (abaixo), não do corte de prosa.
- **Aposta de qualidade — contexto.** −45% de linha reduz token e, pela tese do artigo,
  para de constranger o julgamento do modelo. ⚠️ **Não há medição local disso.** A evidência
  é a da Anthropic sobre o próprio system prompt do Claude Code, e o artigo trata de
  system prompt de produto, não de skill de projeto — a extrapolação 1:1 não é garantida.

## Premissas

| # | Premissa | Fonte |
|---|---|---|
| P1 | O escritor TDD não é papel de julgamento — a saída é verificada por execução de teste | ⚠️ **premissa de design, não medição** (handoff §6b). Evidência a favor: 3 task-reviews em Opus no ciclo fechado, zero defeito de conteúdo atribuído aos escritores Sonnet. Reverter custa uma célula. |
| P2 | O task-reviewer é redundante com o `/code-review` da Fase 5 | `review-gates.md:68-74` (argumento já escrito na própria skill) + `model-tiers.md:56-62` (as 3 redes: TDD verificado por execução, `/code-review` de contexto fresco, Fase 6) |
| P3 | Guardrail de pior-caso permanece mesmo na geração 5 | Artigo, seção de contra-indicações: os guardrails existiam "para evitar piores cenários, como deletar arquivos" |
| P4 | Progressive disclosure (um `references/*.md` por fase) é o formato recomendado, não o alvo do corte | Artigo, seção (e): árvore de arquivos carregada sob demanda > repositório central |

Sem SQL, sem schema, sem banco neste escopo — o Princípio 5 não tem superfície aqui.

## Decisões

### D1 — `references/model-tiers.md` é deletado; o que sobra vai para `setup-gate.md`

O nome mente: com escritor Sonnet nos dois tiers (P1), o tier deixa de trocar qualquer
modelo. E o arquivo é carregado na mesma fase que o `setup-gate.md` (Fase 0, onde o tier é
parseado) — dois arquivos para uma fase é overhead sem ganho de disclosure.

Sobrevivem ~15 linhas: a matriz reduzida, o argumento das 3 redes (P2), o piso Haiku, e a
persistência do tier no cabeçalho do plano.

### D2 — O default inverte: enxuto é o padrão, `full` é o opt-in

```
/oli-dev <ideia>          → enxuto (default): sem task-reviewer, escritores Sonnet
/oli-dev full <ideia>     → + task-reviewer por task
/oli-dev light <ideia>    → alias do default, aceito e anunciado (compat)
/oli-dev finalize         → Fase 8
```

`full` deixa de ser "o ciclo inteiro" e passa a significar **uma coisa só**: re-adiciona a
aderência-à-spec por task — que `model-tiers.md:61-62` nomeia como a única coisa que se
perde sem o task-reviewer, e que erra caro em contrato/enforcement/superfície sensível.

`light` continua parseando por compatibilidade. Sem isso, uma ideia que comece com a
palavra "light" é interpretada como tier e perde a primeira palavra.

O **piso de segurança** (hoje 10 linhas em `model-tiers.md:91-100`) vira uma linha: mudança
que toca contrato/enforcement/superfície sensível → recomende `full`. Não precisa mais de
ack, porque o caminho arriscado deixou de ser o default.

### D3 — O que sai (roteiro) e o que fica (gate)

**Regra de corte:** roteiro que substitui julgamento sai; gate que impede perda de trabalho
fica. Confundir os dois é o único jeito de errar feio aqui.

**Sai:**

| Onde | Hoje | Vira |
|---|---|---|
| `setup-gate.md` | 7 passos numerados, incluindo "ecoe a interpretação do tier" e os 3 ramos do ponytail | Objetivo + os invariantes duros em lista |
| `review-gates.md:28-41` | Ordem da Fase 5 fixa, com "proposital, não reordene" | O porquê da ordem em uma frase; a ordem vira consequência |
| `model-tiers.md:69-89` | Tabela de parsing com casos de borda enumerados | Deletado com o arquivo — o modelo parseia um argumento sem tabela de decisão |
| `SKILL.md` §Verification | Checklist de o que colar como evidência, por fase | Um princípio: evidência é output real, nunca alegação |

**Fica** (P3): worktree da `main` (Princípio 2); `gh pr view` antes de deletar branch
(Princípio 3 — já houve perda real: PR #4 gerou commits órfãos); Fase 6; `verify` da Fase 5;
os hooks (`branch-state-guard.sh`, `pre-push-gate.sh`); `pre-push-gate.md` e `finalize.md`
intocados; Princípio 5 (é heurística de julgamento, o formato que o artigo recomenda).

### D4 — Princípio 6 vira heurística de uma linha

Hoje são 9 linhas prescritivas com cláusula de escape enumerada — resolver comportamento
com mais texto é precisamente o que o artigo diz para parar de fazer. Vira:

> 6. **O conductor coordena.** Investigação, coleta e teste vão para subagentes — paralelos
>    quando independentes.

Mesmo formato do Princípio 5. O pedido do usuário que o originou segue válido; o que muda é
a forma.

### D5 — Teto de rodadas de fix: 5 → 1, **no `full`**

Cada rodada custa 2 despachos (fix + re-review escopada) e o SDD permite 5 por task
(`subagent-driven-development/SKILL.md:320`) — teto de 40 despachos só de fix numa mudança de
4 tasks. No ciclo medido foram 5 rodadas, **4 delas por assert mal especificado pelo
conductor**, não por defeito do escritor (handoff §3d).

Achado que sobrevive à primeira rodada vira **parkeado com ruling**; a Fase 5 tria.
⚠️ Override deliberado do SDD — marcar como tal.

**Escopo exato, verificado:** o fix loop **só dispara com veredito do task-reviewer**
(`:304` — "The loop triggers when the review reports spec ❌, any Critical or Important
finding…"). Como o default não roda task-reviewer (D2), **este teto só tem efeito no `full`**.
Escrevê-lo sem essa ressalva repetiria o bug D6.1 em forma nova: regra inalcançável no
caminho padrão. O texto na skill deve dizer isso explicitamente.

A rota **`BLOCKED`** (`:244`) é independente do task-reviewer e continua valendo nos dois
caminhos — é o próprio implementador dizendo que travou, não um reviewer. Ela **não** é
rodada de fix e não conta contra o teto.

### D6 — Os 3 bugs

1. **Célula morta** (`model-tiers.md:47`, `light`/fix-subagents inalcançável): resolvida pela
   deleção do arquivo. O texto que a substitui diz o que é verdade — o fix **retoma o próprio
   escritor** (`subagent-driven-development/SKILL.md:322`) e escala ≥1 tier acima na rodada 4
   (`:174-175`); não é papel com modelo próprio. A rota **`BLOCKED`** (`:244-250`) é
   independente do task-reviewer e vale sempre.
2. **`setup-gate.md:13` mente** ("já no `.gitignore`"; `git ls-files | grep -c gitignore` → `0`,
   confirmado na Fase 0 deste ciclo). Conserto **na raiz, não no texto**: criar `.gitignore`
   na raiz do repo com `.claude/worktrees/`. A frase passa a ser verdadeira e o `git status`
   do checkout principal para de ser poluído.
3. **Brecha anti-empilhamento** (`review-gates.md:68-74`): "arquivos" como exemplo de artefato
   distinto autoriza fatiar um diff já revisado em 3 e despachar 3 "investigadores".
   Qualificar para *artefatos distintos **que nenhum gate já cobriu***.

### D7 — A conta publicada sai

`README.md:33` publica "`full` ~10 · `light` ~6". Ignora rodadas de fix, re-reviews escopadas
e investigação — errada por 2-3×. **Removida, não substituída.** Número errado é pior que
número nenhum, e um número novo aqui seria igualmente não medido.
(`model-tiers.md:54` carrega a mesma conta e morre com o arquivo.)

## Alvo mensurável

| Métrica | Hoje | Alvo |
|---|---|---|
| Linhas (`SKILL.md` + `references/*.md`) | 343 | ≤206 (−40%); projetado ~189 (−45%) |
| Despachos numa mudança de doc de ~100 linhas | 22+ | ≤8 |
| `plugins/oli-dev/tests/run_all.sh` | verde | verde |
| Gates de D3-"Fica" | travados por teste | continuam travados por teste |

## Arquivos afetados

| Arquivo | Ação |
|---|---|
| `plugins/oli-dev/skills/dev-cycle/SKILL.md` | reescrito (78 → ~58) |
| `plugins/oli-dev/skills/dev-cycle/references/setup-gate.md` | reescrito, absorve o tier (40 → ~45) |
| `plugins/oli-dev/skills/dev-cycle/references/model-tiers.md` | **deletado** (−108) |
| `plugins/oli-dev/skills/dev-cycle/references/review-gates.md` | reescrito (79 → ~48) |
| `plugins/oli-dev/skills/dev-cycle/references/pre-push-gate.md` | **intocado** |
| `plugins/oli-dev/skills/dev-cycle/references/finalize.md` | **intocado** |
| `plugins/oli-dev/commands/oli-dev.md` | parsing invertido (D2) |
| `plugins/oli-dev/README.md` | tier invertido; conta removida (D7) |
| `plugins/oli-dev/tests/test_references.sh` | asserts de `model-tiers.md` saem; novos asserts com sonda negativa |
| `.gitignore` | **criado** (D6.2) |
| `CHANGELOG.md` | somar em `[Unreleased]`, não abrir seção |

## Testes

O invariante de não-regressão é `plugins/oli-dev/tests/run_all.sh` verde.

`test_references.sh:8` lista `model-tiers.md` num loop de existência e `:13-29` tem 8 asserts
amarrados a ele. **Saem junto com o arquivo** — teste que trava texto removido é o próximo
falso vermelho (handoff §8). Os asserts equivalentes que ainda fazem sentido migram para o
arquivo que passou a carregar a claim.

**Regra obrigatória para todo assert de conteúdo (handoff §6c):** cada assert novo precisa de
**sonda negativa** — apagar/eviscerar a claim numa cópia fora do repo e confirmar que o assert
**falha**. Três asserts do ciclo anterior davam falsa segurança sem isso: regex que exigia
célula literal ` Opus ` e escapava do negrito da própria tabela; âncora `'nos dois tiers'`
presente em 4 lugares; `grep -qE '^6\. '` que protegia o **número** do item, não o conteúdo.

**Limite conhecido, aceito:** nenhum conjunto finito de `grep` protege semântica de prosa. O
texto entre duas âncoras é sempre livre. Cobrir o conteúdo mais load-bearing e parar —
perseguir cobertura semântica infla a suíte até ela quebrar em toda reescrita legítima.

## Fora de escopo (explícito)

- `hooks/` e `policies/ENFORCEMENT.md` — enforcement determinística, fora do alcance de
  redesenho de prosa.
- IDs de hook no `.pre-commit-hooks.yaml` — não é matéria de MAJOR.
- `references/pre-push-gate.md` e `references/finalize.md`.
- `evals/` — não há mudança de comportamento avaliado que exija nova eval neste ciclo.
