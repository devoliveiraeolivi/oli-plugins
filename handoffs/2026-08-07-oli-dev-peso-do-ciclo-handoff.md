# Handoff — redesenhar `/oli-dev` para a geração 5: menos roteiro, mesmo rigor

**Data:** 2026-08-07. **Repo:** `oli-plugins`.
**Origem:** medição do ciclo `/oli-dev` que implementou a spec
`2026-08-07-oli-dev-opus-julga-sonnet-produz-design.md`. O usuário interrompeu o ciclo
perguntando por que uma mudança simples levava horas. A pergunta estava certa.
Autocontido — uma sessão futura executa sem a conversa original.

**Decisão já tomada pelo usuário (2026-08-07):** a PR #5 foi **fechada sem merge**. O
redesenho vem antes. Ver §6 para o que resgatar de lá.

> **Aviso à sessão que executar isto — modo de falha óbvio.** A skill que vai conduzir
> a remoção do roteiro **é a própria skill sendo removida**. Ela vai querer brainstorm +
> staff-review + plano + TDD por task para cortar texto. Se isso virar outro ciclo de 22
> despachos, o redesenho **provou** o problema em vez de resolvê-lo. Rodar em `light`, com
> o teto de **≤8 despachos** da §4 valendo para este ciclo também. Corte de prosa não
> precisa de fan-out.

---

## 1. O dado que motiva tudo

Mudança entregue naquele ciclo: **~80 linhas** de markdown + JSON + shell de teste.
Nenhum código de runtime.

| Fase | Despachos de subagente |
|---|---|
| F1 — investigação | 5 (paralelos) |
| F2 — staff-review | 1 |
| Task 1 | 4 (escritor + task-review + 1 fix + 1 re-review) |
| Task 2 | 6 (2 rodadas de fix) |
| Task 3 | 6 (2 rodadas de fix) |
| **Subtotal** | **22** |
| F5 — `/code-review` | fleet próprio de 7 passes + `verify` (foi cortada) |

**Mais de 30 passes de LLM. Horas de parede. Para 80 linhas de doc.**

`references/model-tiers.md:62` e `README.md:33` publicam **"`full` ~10 · `light` ~6"**.
A conta ignora rodadas de fix, re-reviews escopadas e investigação. **Errada por 2-3×.**

---

## 2. O critério de desenho: o artigo da geração 5

<https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models>

Pontos que se aplicam diretamente:

- A Anthropic removeu **mais de 80% do system prompt do Claude Code** para Opus 5 e
  Fable 5 **"sem perda mensurável nas avaliações de código"**.
- **"Deixe o Claude usar julgamento"** em vez de regra rígida. O exemplo dado: trocar
  *"nunca escreva docstring de múltiplos parágrafos"* por *"escreva código que se pareça
  com o código ao redor — mesma densidade de comentário, naming e idioma"*.
- **"Dar exemplos constrange os modelos a um certo espaço de exploração."** A recomendação
  virou desenhar melhores **interfaces de ferramenta**, não roteiro passo a passo.
- Verificação e code review **saíram do system prompt** e viraram **skills chamadas
  seletivamente** — progressive disclosure ganhou de especificação antecipada.

⚠️ **Ressalva honesta:** o artigo fala de **system prompt de produto**, não de skill de
projeto. A extrapolação 1:1 não é garantida. Mas a direção — menos roteiro, mais
julgamento — vale nos dois, e a medição de §1 é evidência local independente.

---

## 3. Auditoria de prescritividade — o trabalho central

**A regra de corte:** roteiro que substitui julgamento sai; gate que impede perda de
trabalho fica. Confundir os dois é o único jeito de errar feio aqui.

### 3a. Sai — roteiro que o Opus 5 faz melhor sozinho

| Onde | O que é hoje | Vira |
|---|---|---|
| `references/setup-gate.md` | 7 passos numerados, incluindo "ecoe a interpretação do tier" e ramos do ponytail | Objetivo + os 3 invariantes duros (worktree da main, Opus no conductor, guard de branch) |
| `references/review-gates.md:28-41` | Fase 5 com ordem fixa e proibição de reordenar | O porquê da ordem em uma frase; a ordem vira consequência, não decreto |
| `references/model-tiers.md:69-89` | Regras de parsing do tier com casos de borda enumerados | O modelo faz parsing de argumento sem tabela de decisão |
| `SKILL.md` "Verification" | Checklist por fase de o que colar como evidência | Um princípio: evidência é output real, não alegação |

### 3b. Fica — gate, não roteiro

- **Worktree da `main`** (Princípio 2) e **`gh pr view` antes de deletar branch**
  (Princípio 3). Já houve perda real: PR #4 gerou commits órfãos, recuperados na #5.
- **Fase 6** (lint/test/typecheck) — determinística, zero token, evidência objetiva.
- **`verify` da Fase 5** — `model-tiers.md:41-43` nomeia esses dois como os únicos que
  nunca caem em nenhum tier. Manter.
- **Hooks** (`branch-state-guard.sh`, `pre-push-gate.sh`) — enforcement determinística,
  fora do alcance de qualquer redesenho de prosa.
- **Princípio 5** ("não presuma o que não dá pra verificar") — é heurística de julgamento,
  não roteiro. É o formato que o artigo recomenda.

### 3c. A redundância estrutural — o maior ganho isolado

`SKILL.md:29` afirma **"um caça-bug por artefato"** e removeu o review final de branch do
SDD por ser redundante com a Fase 5. **Mas manteve o review por task**, que é a mesma
redundância distribuída: o task-reviewer lê o código da task, e o `/code-review` da
Fase 5 lê o mesmo código no diff inteiro.

O argumento contra isso **já está escrito** em `review-gates.md:68-82` ("O que NÃO fazer:
empilhar review sobre review"). Nunca foi aplicado a ele mesmo.

E `model-tiers.md:64-70` já justifica dispensar o task-reviewer no `light` com três redes
— TDD verificado por execução, `/code-review` de contexto fresco, Fase 6 com lint/test
real. **As três valem igual no `full`.**

### 3d. O teto de rodadas de fix

Cada rodada custa **2 despachos** (fix + re-review escopada). O SDD permite **5 por
task** — teto de 40 despachos só de fix numa mudança de 4 tasks. Neste ciclo foram 5
rodadas, e **4 delas por assert mal especificado pelo conductor**, não por defeito do
escritor.

Proposta: teto de **1**. Achado que sobrevive vira parkeado com ruling; a Fase 5 tria.

---

## 4. Alvo mensurável

Sem número, "simplificar" vira opinião. Propostas:

- **Volume:** `SKILL.md` + `references/*.md` somam hoje ~X linhas (medir com
  `wc -l plugins/oli-dev/skills/dev-cycle/SKILL.md plugins/oli-dev/skills/dev-cycle/references/*.md`).
  Alvo: **−40%**, sem perder nenhum item de §3b.
- **Despachos:** numa mudança de doc de ~100 linhas, alvo **≤8** (hoje: 22+).
- **Conta publicada:** ou vira correta (contando fix rounds e investigação), ou sai.
  Número errado por 2-3× é pior que número nenhum.
- **Invariante de não-regressão:** a suíte `tests/run_all.sh` continua verde e os gates
  de §3b continuam travados por teste.

---

## 5. A ironia que o redesenho precisa encarar

O ciclo fechado adicionou o **Princípio 6** ("o conductor coordena — investigação e coleta
vão para subagentes, paralelos quando independentes"), nascido de um pedido legítimo do
usuário: *"quero que o orquestrador toque mais a bola, use mais agentes, mais paralelos"*.

**A implementação contradiz o artigo.** São 9 linhas de regra prescritiva, com cláusula de
escape **enumerada**, num arquivo que carrega em todo ciclo (`SKILL.md` foi de 79 → 88
linhas, +12% de palavras). Resolveu-se um problema de comportamento com mais texto — que é
precisamente o que o artigo diz para parar de fazer.

**A pergunta para o brainstorm, não para presumir:** o comportamento desejado (delegar
investigação, avaliar paralelismo) precisa de regra escrita, ou o Opus 5 já o faz quando
**não** está preso a um roteiro que manda o conductor executar tudo? Se a resposta for a
segunda, o conserto certo é **remover** as instruções que hoje mandam o conductor fazer
(§3a), não **somar** uma que manda delegar.

Note que o pedido do usuário continua válido — o que está em questão é a **forma** da
solução, não o objetivo.

---

## 6. O que resgatar da PR #5 (fechada, branch preservada)

Branch: `worktree-oli-dev-escritores-sonnet-conductor-delegacao`, HEAD `40a385b`.
Os commits existem no remoto. Recuperar com
`git log origin/worktree-oli-dev-escritores-sonnet-conductor-delegacao` ou cherry-pick.

### 6a. Três bugs REAIS que continuam na `main` — consertar em qualquer redesenho

1. **Célula morta em `references/model-tiers.md:47`.**
   `| **F4 — fix-subagents** (só se houver achado) | Opus | Sonnet |`
   A célula `light` é **inalcançável**: o fix loop do SDD só dispara com veredito do
   task-reviewer (`subagent-driven-development/SKILL.md:304-305`), e no `light` o
   task-reviewer não roda (`model-tiers.md:46`). Origem: `60853e9` separou uma linha
   combinada e não propagou — a mensagem do commit não menciona fix-subagents.
   Além disso o fix **não é papel com modelo próprio**: o SDD retoma o próprio escritor
   (`SKILL.md:322`) e escala ≥1 tier acima na rodada 4 (`:174-175`).
   Existe ainda a rota **`BLOCKED`** (`:244-250`), independente do task-reviewer, válida
   nos dois tiers — a matriz nunca a mencionou.

2. **`references/setup-gate.md:13` mente.** Afirma que `.claude/worktrees/` está "já no
   `.gitignore`". **Não existe `.gitignore` no repo** (`git ls-files | grep -c gitignore`
   → `0`). Consequência real: `.claude/worktrees/` polui o `git status` do checkout
   principal.

3. **Brecha em `references/review-gates.md`.** A seção anti-empilhamento dá "arquivos"
   como exemplo de artefato distinto — o que autoriza fatiar um diff **já revisado** pelo
   `/code-review` em 3 arquivos e despachar 3 "investigadores". Correção: qualificar para
   *artefatos distintos **que nenhum gate já cobriu***.

### 6b. Decisão de conteúdo que segue válida

**Escritor TDD (F4) = Sonnet nos dois tiers.** O escritor nunca foi papel de julgamento —
a saída é verificada por execução de teste. Efeito: o tier deixa de trocar modelo, só
troca camada, e o Princípio 4 passa a ser literalmente verdadeiro.
⚠️ **É premissa de design, não medição** — rotular como tal. Reverter custa uma célula.

Evidência a favor colhida no ciclo fechado: **3 task-reviews em Opus, zero defeito de
conteúdo atribuído aos escritores Sonnet.** Todos os Critical/Important vieram de assert
mal especificado pelo conductor no plano.

### 6c. Lição sobre teste de invariante em doc

Três asserts foram escritos com âncora fraca antes de acertar: (a) regex que exigia célula
literal ` Opus ` e escapava do estilo em negrito da própria tabela; (b) âncora
`'nos dois tiers'` presente em 4 lugares — apagar a claim protegida deixava a suíte verde;
(c) `grep -qE '^6\. '`, que protegia o **número** do item — trocar o princípio inteiro por
"6. Use tabs" passava.

**Regra que emergiu:** todo assert de conteúdo em doc precisa de **sonda negativa** —
apagar/eviscerar a claim numa cópia fora do repo e confirmar que o assert **falha**. Sem
isso, o teste dá falsa segurança.

**Limite conhecido:** nenhum conjunto finito de `grep` protege semântica de prosa. O texto
entre duas âncoras é sempre livre. Cobrir o conteúdo mais load-bearing e parar — perseguir
cobertura semântica infla a suíte até ela quebrar em toda reescrita legítima.

---

## 7. LER PRIMEIRO

1. `plugins/oli-dev/skills/dev-cycle/SKILL.md` — Princípios 1-5, Workflow, Verification.
2. `plugins/oli-dev/skills/dev-cycle/references/model-tiers.md` — matriz (`:41-52`),
   contagem (`:54`), e `:56-62` (o argumento pronto para dispensar o task-reviewer).
3. `plugins/oli-dev/skills/dev-cycle/references/review-gates.md:68-74` — o argumento
   anti-empilhamento que nunca foi aplicado ao review por task.
4. `plugins/oli-dev/skills/dev-cycle/references/setup-gate.md` — o caso mais claro de
   roteiro numerado substituível por objetivo + invariantes.
5. O artigo de §2.
6. A skill `subagent-driven-development` (superpowers 6.2.0), seção "The fix loop"
   (`SKILL.md:300-340`) — de onde vem o teto de 5 rodadas.

## 8. Restrições de processo

- **Rodar em `light`.** Diagnosticar que `full` é pesado demais rodando um ciclo `full`
  seria piada — e o próprio diagnóstico diz que não paga.
- **Não tocar** em hooks, `policies/ENFORCEMENT.md`, nem nos gates de §3b.
- **Não mexer em hook ID** — não é matéria de MAJOR.
- CHANGELOG: `[Unreleased]` já tem 2 entradas commitadas. Somar, não abrir seção.
  Última tag `oli-dev-v1.0.0`; HEAD da `main` 4 commits à frente.
- Se o redesenho remover comportamento documentado, os asserts correspondentes em
  `tests/test_references.sh` saem **junto** — teste que trava texto removido é o próximo
  falso vermelho.
