# Spec — redesenho do `/oli-dev` para a geração 5: menos roteiro, mesmo rigor

**Data:** 2026-08-07 · **Repo:** `oli-plugins` · **Tier do ciclo:** `light`
**Fonte:** `handoffs/2026-08-07-oli-dev-peso-do-ciclo-handoff.md` (autocontido, nesta branch).
**Critério de desenho:** <https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models>
(lido na Fase 1 deste ciclo, não citado de memória).
**Revisada:** staff-review Opus na Fase 2 — 6 blockers, 8 likely issues, 3 polish. Todos
tratados; o registro de adjudicação está na §"Achados do staff-review".

## Goal

A skill `dev-cycle` é roteiro passo a passo. Um ciclo que entregou **~80 linhas de
documentação** custou **22+ despachos de subagente, 5 rodadas de fix e 30+ passes de LLM**
(handoff §1). Este redesenho remove o roteiro que substitui julgamento, preserva todo gate
que impede perda de trabalho, e conserta 3 bugs que continuam na `main`.

Dois ganhos, de naturezas diferentes — registrados separados porque só um é medível:

- **Medível — passes de LLM.** Numa mudança de 4 tasks: **22+ → ~8**. Vem do corte de
  camada (D2), não do corte de prosa.
- **Aposta de qualidade — contexto.** −40% de linha reduz token e, pela tese do artigo,
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

**O que migra, nomeado** (hoje 32 linhas; alvo ~18 após compressão):

| Conteúdo | Origem | Destino |
|---|---|---|
| Matriz de papéis/camadas | `model-tiers.md:39-52` | `setup-gate.md`, reduzida a 2 linhas de texto |
| As 3 redes que justificam dispensar o task-reviewer (P2) | `:56-62` | `setup-gate.md` |
| Piso Haiku (fora dos tiers por decisão) | `:64-67` | `setup-gate.md`, 1 linha |
| Persistência do tier no cabeçalho do plano | `:102-108` | `setup-gate.md`, 1 linha + D2.1 |
| **Override "sem review final de branch"** | `:26-30` | **`SKILL.md`** — já está em `:32-33`; é onde os asserts vão apontar (ver Testes) |

**Morre com o arquivo, deliberadamente:** a tabela de parsing com casos de borda
(`:69-89`), o piso de segurança em 10 linhas (`:91-100`), a conta errada (`:54`, ver D7) e
a célula morta (`:47`, ver D6.1).

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

`light` continua parseando por compatibilidade, e `test_skill_structure.sh:28-30` exige os
dois tokens no command file. ⚠️ **Corrigido após o `/code-review` da Fase 5:** a justificativa
original ("sem o alias, uma ideia que comece com 'light' perde a primeira palavra") estava
**invertida**. É aceitar `light` como token de tier que faz `/oli-dev light mode toggle` virar
ideia `"mode toggle"`. A mitigação é o **eco da interpretação** (*"tier=X, ideia='…'"*), que eu
havia cortado como roteiro — é gate, porque torna visível um parse com perda. Restaurado.

O **piso de segurança** (hoje 10 linhas em `model-tiers.md:91-100`) encolhe, mas **mantém o
ack**. ⚠️ **Corrigido após o `/code-review`:** a versão anterior desta spec dizia "não precisa
mais de ack, porque o caminho arriscado deixou de ser o default" — raciocínio de cabeça pra
baixo. Antes, `full` era o default e mudança sensível já caía no caminho seguro; o ack existia
para *sair* dele. Agora o default é enxuto, então uma mudança de auth/secrets/SQL roda sem
aderência-à-spec por task **sem ninguém digitar nada**. O ack ficou mais necessário, não menos:
superfície sensível → recomende `full` e peça ack antes de seguir no default.

**D2.1 — o fallback do resume continua fail-safe.** `model-tiers.md:104-108` estabelece que
perder o tier num resume "degrada para `full`, nunca para algo mais arriscado". Depois da
inversão, "ausente → default" passaria a significar **enxuto** — e alguém que pediu `full`
por tocar contrato perderia o task-reviewer em silêncio ao retomar. Então: **plano sem
cabeçalho de tier → assume `full`**, e o conductor anuncia que assumiu. O princípio é o
mesmo de antes; só a direção do default mudou em volta dele.

**D2.2 — o ciclo deixa de gerenciar o ponytail.** `setup-gate.md:30-40` ramifica o ponytail
por **nome de tier** (`light` → invoca `/ponytail lite`; `full` → não toca). Com `light`
virando alias do default, esse ramo passaria a disparar em **todo** ciclo padrão,
sobrescrevendo um ajuste global do usuário a cada invocação. O passo inteiro sai (−11
linhas). A justificativa já está escrita no texto que morre, aplicada só ao `full`: *"não
ligar ≠ desligar: se o usuário o ligou globalmente por escolha própria, o ciclo não
sobrescreve"* (`:37-38`). Agora vale em todos os caminhos. Quem gerencia ponytail é o
usuário.

### D3 — O que sai (roteiro) e o que fica (gate)

**Regra de corte:** roteiro que substitui julgamento sai; gate que impede perda de trabalho
fica. Confundir os dois é o único jeito de errar feio aqui.

**Sai:**

| Onde | Hoje | Vira |
|---|---|---|
| `setup-gate.md` | 7 passos numerados, incluindo "ecoe a interpretação do tier" | Objetivo + os invariantes duros em lista |
| `setup-gate.md:30-40` | Os 3 ramos do ponytail | Deletado (D2.2) |
| `setup-gate.md:14-15` | "garanta `.worktrees/` no `.gitignore` nesse caminho" | Deletado — `using-git-worktrees/SKILL.md:83-86` já faz isso sozinha |
| `review-gates.md:28-41` | Ordem da Fase 5 fixa, com "proposital, não reordene" | O porquê da ordem em uma frase; a ordem vira consequência |
| `model-tiers.md:69-89` | Tabela de parsing com casos de borda enumerados | Deletado com o arquivo — o modelo parseia um argumento sem tabela de decisão |
| `SKILL.md` §Verification | Checklist de o que colar como evidência, por fase | Um princípio: evidência é output real, nunca alegação |

**Fica** (P3): worktree da `main` (Princípio 2); `gh pr view` antes de deletar branch
(Princípio 3 — já houve perda real: PR #4 gerou commits órfãos); Fase 6; `verify` da Fase 5;
os hooks (`branch-state-guard.sh`, `pre-push-gate.sh`); `pre-push-gate.md` e `finalize.md`
intocados; Princípio 5 (é heurística de julgamento, o formato que o artigo recomenda).

⚠️ A seção `## Verification` do `SKILL.md` **esvazia mas não some** —
`test_skill_structure.sh:15` exige o literal, junto com as outras 3 seções e as 9 strings
`"Fase N"` (`:23-25`).

### D4 — Princípio 6 vira heurística de uma linha

Hoje são 9 linhas prescritivas com cláusula de escape enumerada — resolver comportamento
com mais texto é precisamente o que o artigo diz para parar de fazer. Vira:

> 6. **O conductor coordena.** Investigação, coleta e teste vão para subagentes — paralelos
>    quando independentes.

Mesmo formato do Princípio 5. O pedido do usuário que o originou segue válido; o que muda é
a forma.

### D5 — Teto de rodadas de fix: **considerada e rejeitada**

O handoff §3d propunha baixar o teto do SDD de 5 rodadas para 1. Escrita e derrubada no
staff-review da Fase 2, com três evidências verificadas. Registrada aqui em vez de
descartada em silêncio, para o próximo ciclo não repropor:

1. **Só agiria no `full`.** O fix loop dispara com veredito do task-reviewer
   (`subagent-driven-development/SKILL.md:304`), e a D2 tira o task-reviewer do default.
   Sobra o `full` — o caminho de rigor deliberado, que é justamente onde não se quer capar
   o loop de conserto.
2. **Criaria célula morta nova.** A escalada "≥1 tier acima" acontece nas **rodadas 4-5**
   (`:174`). Com teto 1 ela é inalcançável — a mesma classe de bug que a D6.1 conserta,
   reintroduzida pelo próprio conserto.
3. **Achataria o breaker do SDD.** Com teto 1, o ramo *"Real and load-bearing → STOP,
   `BLOCKED`, reporte ao humano"* (`:365-374`) passa de raro a rotina — e o texto proposto
   o resumia como "a Fase 5 tria", que é exatamente o que o SDD diz que a Fase 5 **não**
   consegue fazer: *"Parking a structural failure … hands the final review a problem it
   cannot fix either."*

A patologia medida (5 rodadas, 4 delas por assert mal especificado pelo conductor, handoff
§3d) sai do caminho padrão pela D2 sozinha. O teto de 5 do SDD fica intacto no `full`.

### D6 — Os 3 bugs

1. **Célula morta** (`model-tiers.md:47`, `light`/fix-subagents inalcançável): resolvida pela
   deleção do arquivo. O texto que a substitui diz o que é verdade — o fix **retoma o próprio
   escritor** (`subagent-driven-development/SKILL.md:322`), não é papel com modelo próprio.
   A rota **`BLOCKED`** (`:244`) é independente do task-reviewer e vale nos dois caminhos: é
   o implementador dizendo que travou, não um reviewer.
   ⚠️ Não citar a escalada de rodada 4-5 sem o teto de 5 junto — foi assim que a célula
   morta original nasceu.
2. **`setup-gate.md:13` mente** ("já no `.gitignore`"; `git ls-files | grep -c gitignore` → `0`,
   confirmado na Fase 0 deste ciclo). Conserto **na raiz, não no texto**: criar `.gitignore`
   na raiz do repo com `.claude/worktrees/`. A frase passa a ser verdadeira e o `git status`
   do checkout principal para de ser poluído.
3. **Brecha anti-empilhamento** (`review-gates.md:68-74`): "arquivos" como exemplo de artefato
   distinto autoriza fatiar um diff já revisado em 3 e despachar 3 "investigadores".
   Qualificar para *artefatos distintos **que nenhum gate já cobriu***.

### D7 — A conta publicada sai, nas três cópias

"`full` ~10 · `light` ~6" ignora rodadas de fix, re-reviews escopadas e investigação —
errada por 2-3×. **Removida, não substituída.** Número errado é pior que número nenhum, e um
número novo aqui seria igualmente não medido.

Cópias: `README.md:33`; `model-tiers.md:54` (morre com o arquivo); `CHANGELOG.md:29` —
dentro de `[Unreleased]`, ainda editável, não é registro histórico.

### D8 — SEMVER: é MAJOR

`policies/SEMVER.md:6-7`: *"MAJOR: quebra na interface do plugin (flags/sintaxe de comando)
ou **remoção de fase/gate**"*. A D2 remove o task-reviewer do caminho padrão — remoção de
gate. Última tag: `oli-dev-v1.0.0`.

Escopo deste ciclo: a entrada em `[Unreleased]` **declara MAJOR**. A tag e o GitHub release
são passo de release, fora deste ciclo (`SEMVER.md:11-13`: a versão canônica é tag + release
+ seção do CHANGELOG).

## Alvo mensurável

| Métrica | Hoje | Alvo |
|---|---|---|
| Linhas (`SKILL.md` + `references/*.md`) | 343 | **≤206 (−40%)** — projeção ~189, tratada como aspiração, não como alvo |
| Despachos numa mudança de doc de ~100 linhas | 22+ | ≤8 |
| `plugins/oli-dev/tests/run_all.sh` | verde | verde |
| Gates de D3-"Fica" | ver tabela abaixo | **todos** travados por teste |

O staff-review auditou a cobertura atual — dois gates de D3-"Fica" estão **descobertos hoje**,
e a spec anterior os dava como travados. Corrigido:

| Gate | Coberto hoje? | Ação |
|---|---|---|
| worktree da `main` | ✅ `test_references.sh:33` | mantém |
| `gh pr view` / MERGED | ✅ `test_references.sh:31` | mantém |
| Fase 6 (pre-push) | ✅ `test_references.sh:32` | mantém |
| hooks registrados | ✅ `test_manifests.sh:41-43` | mantém |
| `verify` da Fase 5 ("sempre") | ❌ descoberto | **assert novo** |
| Princípio 5 | ❌ descoberto | **assert novo** |

## Arquivos afetados

| Arquivo | Ação |
|---|---|
| `plugins/oli-dev/skills/dev-cycle/SKILL.md` | reescrito (78 → ~58) |
| `plugins/oli-dev/skills/dev-cycle/references/setup-gate.md` | reescrito, absorve o tier (40 → ~45) |
| `plugins/oli-dev/skills/dev-cycle/references/model-tiers.md` | **deletado** (−108) |
| `plugins/oli-dev/skills/dev-cycle/references/review-gates.md` | reescrito (79 → ~48) |
| `plugins/oli-dev/skills/dev-cycle/references/pre-push-gate.md` | **intocado** |
| `plugins/oli-dev/skills/dev-cycle/references/finalize.md` | **intocado** |
| `plugins/oli-dev/commands/oli-dev.md` | parsing invertido (D2) **+ frontmatter `description`** |
| `plugins/oli-dev/.claude-plugin/plugin.json` | `description` — cita "tier full/light trocando camadas" |
| `plugins/oli-dev/README.md` | tier invertido; conta removida (D7); ponteiro p/ `model-tiers.md` (`:23`) |
| `plugins/oli-dev/tests/test_references.sh` | asserts de `model-tiers.md` saem; novos com sonda negativa |
| `plugins/oli-dev/tests/test_skill_structure.sh` | remover `model-tiers` do loop de referências (`:19`) |
| `plugins/oli-dev/evals/evals.json` | `light_tier_scope` reescrita; `:42` aponta p/ arquivo deletado |
| `.gitignore` | **criado** (D6.2) |
| `CHANGELOG.md` | somar em `[Unreleased]`; declarar MAJOR (D8); remover a conta (`:29`) |

**Ponteiros pendurados para `model-tiers.md`** a limpar: `commands/oli-dev.md:21`,
`README.md:23`, `review-gates.md:1`, `:23`, `:34`, `evals.json:42`.
**Não tocar:** `CHANGELOG.md:33` e os plans em `docs/superpowers/plans/` — são registro
histórico; um ponteiro para um arquivo que existia na época está correto.

## Testes

O invariante de não-regressão é `plugins/oli-dev/tests/run_all.sh` verde.

**Asserts que saem** — `test_references.sh:13-29` tem 8 amarrados a `model-tiers.md`, e
`:8` o lista num loop de existência. Saem junto com o arquivo; teste que trava texto
removido é o próximo falso vermelho (handoff §8). O mesmo vale para
`test_skill_structure.sh:19`.

**Asserts obrigatórios** — sem estes, D3-"Fica" abre buraco:

| # | Assert | Por quê |
|---|---|---|
| 1 | `review final de branch` e `override deliberado` **re-apontados para `SKILL.md`** (conteúdo em `:32-33`) | Hoje existem só contra `$MT` (`test_references.sh:27-28`). É o Princípio 4 e tem eval dedicado (`evals.json:39-42`) — o gate mais caro de perder |
| 2 | `model-tiers` fora do loop de `test_skill_structure.sh:19` | Senão `run_all.sh` fica vermelho |
| 3 | Default enxuto em `commands/oli-dev.md` | Sem ele, uma reescrita futura reverte a D2 sem vermelho |
| 4 | `verify` "sempre" em `review-gates.md` | Descoberto hoje |
| 5 | Princípio 5 em `SKILL.md` | Descoberto hoje |

**Regra obrigatória para todo assert de conteúdo (handoff §6c):** cada assert novo precisa de
**sonda negativa** — apagar/eviscerar a claim numa cópia fora do repo e confirmar que o assert
**falha**. Três asserts do ciclo anterior davam falsa segurança sem isso: regex que exigia
célula literal ` Opus ` e escapava do negrito da própria tabela; âncora `'nos dois tiers'`
presente em 4 lugares; `grep -qE '^6\. '` que protegia o **número** do item, não o conteúdo.

**Limite conhecido, aceito:** nenhum conjunto finito de `grep` protege semântica de prosa. O
texto entre duas âncoras é sempre livre. Cobrir o conteúdo mais load-bearing e parar —
perseguir cobertura semântica infla a suíte até ela quebrar em toda reescrita legítima.

## Achados do staff-review (Fase 2) — registro de adjudicação

| # | Achado | Ruling |
|---|---|---|
| B1 | `test_skill_structure.sh:19` quebra com a deleção | **Aceito** — entrou em Arquivos afetados |
| B2 | D5 criaria célula morta (escalada rodada 4) | **Aceito** — D5 cortada |
| B3 | D5 achatava o breaker load-bearing do SDD | **Aceito** — D5 cortada |
| B4 | Override de branch-review ficaria sem teste | **Aceito** — destino nomeado (Testes #1) |
| B5 | Ponytail dispararia em todo ciclo padrão | **Aceito** — passo removido (D2.2) |
| B6 | Fallback do resume invertia p/ fail-open | **Aceito** — D2.1 |
| L1 | `evals.json` com referência pendurada e eval desatualizada | **Aceito** — saiu de "fora de escopo" |
| L2 | "hoje travados por teste" era inferência | **Aceito** — tabela de cobertura real |
| L3 | SEMVER não classificado | **Aceito** — D8 |
| L4 | Contratos de teste do `SKILL.md` não declarados | **Aceito** — nota na D3 |
| L5 | D5 é escopo inflado | **Aceito** — D5 cortada |
| L6 | −45% otimista | **Aceito** — alvo é ≤206; ~189 é aspiração |
| L7 | `plugin.json` e frontmatters mentem | **Aceito** — em Arquivos afetados |
| L8 | Conta errada também no `CHANGELOG:29` | **Aceito** — D7 |
| P1 | `ENFORCEMENT.md`/`.pre-commit-hooks.yaml` não existem neste repo | **Aceito** — corrigido em Fora de escopo |
| P2 | Ponteiros pendurados | **Aceito** — listados |
| P3 | Linha de graça no `setup-gate.md:14-15` | **Aceito** — na tabela "Sai" |

Nenhum achado rejeitado.

## Fora de escopo (explícito)

- `plugins/oli-dev/hooks/` (`branch-state-guard.sh`, `pre-push-gate.sh`) — enforcement
  determinística, fora do alcance de redesenho de prosa.
- `references/pre-push-gate.md` e `references/finalize.md`.
- Tag e GitHub release do MAJOR (D8) — passo de release, não deste ciclo.
- `policies/SEMVER.md` — consultado, não alterado.

⚠️ O handoff §8 listava `policies/ENFORCEMENT.md` e IDs de hook no `.pre-commit-hooks.yaml`
como fora de escopo. **Nenhum dos dois existe neste repo** (`ls policies/` → só `SEMVER.md`;
`find . -name .pre-commit-hooks.yaml` → vazio). Vinham de `model-tiers.md:94`, que os cita
como exemplo genérico de outro repo. Removidos da lista para ela não descrever coisa que
não existe.
