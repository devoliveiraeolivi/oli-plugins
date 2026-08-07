# Review gates — um caça-bug por artefato (tier: ver `references/setup-gate.md`)

## Princípio inviolável — evidência ou abstenha

Um reviewer que **afirma sem checar** é **pior que não ter reviewer**: lava um palpite em "fato
revisado" que ninguém mais questiona.

- **Achado sem evidência citada** (`file:line`, ou comando + saída real) não é finding: é
  palpite → rotule **`⚠️ não verificado`**.
- **Nunca raciocine de memória sobre código/tool/API** — abra o arquivo ou rode. Doc, CLAUDE.md
  e memória envelhecem; o código é a verdade.
- **"Não consegui verificar X" é saída válida e obrigatória.** Não preencha lacuna com suposição.
- **O conductor adjudica com evidência, não por deferência.** Claim load-bearing ou que
  contradiga o código é checada antes de virar ação.

## Fase 2 — pré-código (sobre brainstorm + spec)

**1 subagente `staff-reviewer`** (effort alto) em **Opus nos dois tiers** — julgamento sobre a
spec inteira não é onde se economiza modelo. Mandato cético e amplo, sem lista fechada de
categorias. Incorpore, atualize a spec, commit. Só avance quando a spec sobrevive ao review.

## Fase 5 — pós-código (sobre o diff)

Idêntica nos dois tiers. `/code-review` roda seu fleet próprio; o resto roda no contexto do
conductor (**Opus 5**), que adjudica.

1. `/code-review` (effort alto) — bugs de correção; verifique os achados adversarialmente. É o
   **único caça-bug de contexto fresco sobre o diff inteiro**, e o que substitui o branch review.
2. `/simplify` — só se o diff passa de **~150 linhas alteradas** (`git diff --stat` vs. `main`).
   Em diff pequeno rende churn cosmético e ainda cobra a adjudicação. Em dúvida, rode. **Se
   pular, cole o `git diff --stat`** — o motivo é o tamanho, e tamanho se mostra.
3. `verify` (`superpowers:verification-before-completion`) roda **sempre** — qualquer tier,
   qualquer diff. Testes de verdade, evidência colada, sobre o resultado já simplificado.

A ordem não é decreto: não se simplifica código com bug em aberto.

**O `/simplify` propõe; o conductor adjudica.** Concisão que remove tratamento, caso de borda ou
correção é regressão disfarçada de limpeza — em dúvida, não simplifique. O gate duro é o `verify`.

**Sem buracos temporários.** TODO, stub, `pass`, mock no lugar de lógica: achado pequeno conserta
agora, completo; o que não cabe no ciclo vira registro visível (issue, `docs/project_notes`).

## O que NÃO fazer: empilhar review sobre review

Antes de despachar um reviewer "só pra conferir", pergunte se existe **artefato novo que nenhum
gate já cobriu** — fatiar um diff já revisado em 3 arquivos e chamar cada pedaço de "artefato
distinto" é o mesmo empilhamento com outro nome. Sem artefato novo, o gate que agrega é o
objetivo (`verify`, Fase 6), não outra opinião.

### Sub-gate condicional de security-review
Diff que toca **superfície sensível** — auth, secrets/`.env`, SQL/RPC, rede/HTTP, credenciais,
browser/`page.evaluate` — dispara também `/security-review`. Detecte pelos paths e pelo conteúdo
do diff. Não roda em todo ciclo.
