# Handoff — `/oli-dev` está pesado demais para os modelos da geração 5

**Data:** 2026-08-07. **Origem:** medição do próprio ciclo que implementou a spec
`2026-08-07-oli-dev-opus-julga-sonnet-produz-design.md`, no `oli-plugins`.
Autocontido — uma sessão futura executa sem a conversa original.

**Gatilho:** o usuário interrompeu o ciclo perguntando por que uma mudança simples
levava horas. A pergunta estava certa e os números confirmam.

## O dado

Mudança entregue: **~80 linhas de markdown + JSON + shell de teste**. Nenhum código
de runtime.

Custo real do ciclo `full`:

| Fase | Despachos de subagente |
|---|---|
| F1 — investigação | 5 (paralelos) |
| F2 — staff-review | 1 |
| Task 1 | 4 (escritor + task-review + 1 fix + 1 re-review) |
| Task 2 | 6 (2 rodadas de fix) |
| Task 3 | 6 (2 rodadas de fix) |
| **Subtotal** | **22** |
| F5 — `/code-review` | fleet próprio de 7 passes + `verify` |

Mais de 30 passes de LLM. Tempo de parede: horas.

`references/model-tiers.md` publica **"`full` ~10 · `light` ~6"** para uma mudança de
4 tasks. A conta não inclui rodadas de fix, re-reviews escopadas nem investigação.
**Está errada por 2-3×.**

## Por que — três causas, em ordem de peso

### 1. Dois caça-bugs sobre o mesmo código, apesar do Princípio 4

`SKILL.md:29` afirma "**um caça-bug por artefato**" e removeu o review final de branch
do SDD por ser redundante com a Fase 5. Mas manteve o **review por task**, que é a
mesma redundância distribuída: o task-reviewer lê o código da task, e depois o
`/code-review` da Fase 5 lê o mesmo código no diff inteiro.

O princípio está certo; a implementação o contradiz.

### 2. Cada rodada de fix custa 2 despachos

Fix + re-review escopada. Foram 5 rodadas neste ciclo = **10 despachos**, quase metade
do total. E o SDD permite até 5 rodadas **por task** — teto de 40 despachos só de fix
numa mudança de 4 tasks.

### 3. A skill foi desenhada para uma geração de modelo anterior

Evidência externa direta —
<https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models>:

- A Anthropic removeu **mais de 80% do system prompt do Claude Code** para Opus 5 e
  Fable 5 "sem perda mensurável nas avaliações de código".
- "Dar exemplos **constrange** os modelos a um certo espaço de exploração" — a
  recomendação passou a ser desenhar melhores interfaces de ferramenta, não roteiro.
- Verificação e code review **saíram do system prompt** e viraram skills chamadas
  **seletivamente**.
- Princípio central: **"deixe o Claude usar julgamento"** em vez de regra rígida.

`/oli-dev` é o anti-padrão descrito: prescrição passo a passo, camadas de review
obrigatórias, gates que não se pulam. Isso foi acerto quando escrito. Com Opus 5 no
conductor, vira imposto.

## Evidência do outro lado — o que o processo pagou

Não desmontar sem olhar isto. O ciclo pegou três bugs reais que iam para o merge:

1. **Célula morta na matriz** — a linha `fix-subagents | Opus | Sonnet` era inalcançável
   no `light` (sem task-reviewer, nada dispara o loop). Bug de propagação do refactor
   `60853e9`. Achado por agente de investigação, não pelo conductor.
2. **Cláusula de escape incompleta** — o texto do Princípio 6 protegia o gate da Fase 6
   e esquecia o `verify` da Fase 5, sendo que `model-tiers.md:41-43` nomeia os dois como
   os únicos que nunca caem. Achado pelo staff-reviewer.
3. **Brecha no anti-empilhamento** — `review-gates.md` dava "arquivos" como exemplo de
   artefato distinto, permitindo fatiar um diff já revisado em 3 e despachar 3
   "investigadores". Achado pelo task-reviewer.

Também: 3 asserts com âncora fraca, todos escritos pelo conductor no plano, todos
pegos por sonda de reviewer. **Nenhum defeito de conteúdo foi atribuído aos escritores
Sonnet** nas 3 tasks revisadas.

Conclusão honesta: **o gate que paga é o review sobre artefato NOVO** (spec → staff,
diff → code-review). O que não paga é o **review por task**, que relê código que o
`/code-review` vai reler de novo.

## LER PRIMEIRO

1. `plugins/oli-dev/skills/dev-cycle/SKILL.md` — Princípio 4 (`:29-38`) e Fase 4 (`:73`).
2. `plugins/oli-dev/skills/dev-cycle/references/model-tiers.md` — a matriz (`:45-60`),
   a contagem de passes (`:62`), e a seção "Por que o `light` pode dispensar o
   task-reviewer" (`:64-70`) — que já tem o argumento pronto para o `full` também.
3. `plugins/oli-dev/skills/dev-cycle/references/review-gates.md:68-82` — "O que NÃO
   fazer: empilhar review sobre review". O argumento contra o review por task já está
   escrito aí; só não foi aplicado a ele.
4. A skill `subagent-driven-development` do superpowers (6.2.0) — §"The fix loop"
   (`SKILL.md:300-340`), de onde vem o teto de 5 rodadas.

## Propostas — a decidir no brainstorm, não presumir

**A. Cortar o task-reviewer também no `full`.** O `light` já o dispensa, e
`model-tiers.md:64-70` justifica com três redes: TDD (verificação por execução),
`/code-review` da F5 (contexto fresco sobre o diff inteiro), Fase 6 (lint/test real).
As três valem igual no `full`. O que se perde é aderência-à-spec **por task** — pesar
se isso justifica dobrar o custo.

**B. Teto de 1 rodada de fix por task** (hoje 5). Achado que sobrevive a uma rodada
vira parkeado com ruling, e a Fase 5 tria. Neste ciclo, 4 das 5 rodadas foram por
assert do conductor, não por defeito do escritor.

**C. Corrigir a conta publicada** em `model-tiers.md:62` e `README.md:33`, ou remover.
Número errado por 2-3× é pior que número nenhum.

**D. Revisar a prescritividade à luz do artigo.** Candidatos a virar julgamento em vez
de roteiro: a ordem fixa da Fase 5, os passos numerados do `setup-gate.md`, a exigência
de eco de interpretação do tier. **Cuidado:** gates de segurança (worktree da main,
`gh pr view` antes de deletar branch, gate da Fase 6) **não** são prescritividade
supérflua — são o que impede perda de trabalho. Cortar roteiro ≠ cortar gate.

**E. Considerar tornar `light` o default** e `full` opt-in explícito para mudança de
contrato/enforcement.

## Restrições de processo

- Este handoff é sobre **peso de processo**, não sobre correção. Não mexer em hook,
  `policies/ENFORCEMENT.md`, nem nos gates determinísticos (Fase 6).
- Se a proposta A passar, `model-tiers.md`, `SKILL.md`, `commands/oli-dev.md`,
  `README.md`, `evals/evals.json` e `tests/test_references.sh` mudam juntos — mesma
  classe do ciclo de 2026-08-07.
- **Rodar este ciclo em `light`.** Rodar um ciclo `full` para diagnosticar que `full` é
  pesado demais seria piada de mau gosto — e o próprio diagnóstico diz que não paga.
