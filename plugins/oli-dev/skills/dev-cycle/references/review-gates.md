# Review gates (Producer-Reviewer; um caça-bug por artefato, camadas por tier — ver `references/model-tiers.md`)

## Princípio inviolável — evidência ou abstenha (todos os gates)

Um reviewer que **afirma sem checar** — de memória, de como "acha" que uma tool/API/flag
se comporta, ou de doc desatualizado — é **pior que não ter reviewer**: lava um palpite em
"fato revisado" que ninguém mais questiona e leva a decisão pro caminho errado. Vale pra
staff-reviewer (Fase 2), pros gates da Fase 5 e pro conductor.

- **Todo achado precisa de evidência citada** — `file:line`, ou comando + saída real. Sem
  evidência não é finding: é palpite → rotule **`⚠️ não verificado`**, não afirme.
- **Nunca raciocine de memória sobre comportamento de código/tool/API** — cheque o arquivo real
  ou rode. Doc/CLAUDE.md/memória podem estar velhos; o código é a verdade. Confirme que
  arquivo/função/flag citada existe antes de basear um achado nela.
- **"Não consegui verificar X" é saída válida e obrigatória** — melhor um ⚠️ honesto que uma
  asserção confiante e errada. Não preencha lacuna com suposição.
- **O conductor adjudica com evidência, não por deferência** — claim de reviewer que seja
  load-bearing ou contradiga o código é checado antes de virar ação (ex.: não mandar corrigir
  código que está certo por causa de um "achado" que o reviewer não verificou).

## Fase 2 — pré-código (sobre brainstorm + spec)
Despache **1 subagente `staff-reviewer`** (effort alto) em **Opus nos dois tiers** — julgamento
sobre a spec inteira não é onde se economiza modelo (ver `references/model-tiers.md`). Mandato
cético: complexidade desnecessária, requisito ambíguo, escopo inflado, riscos não tratados,
suposições não verificadas. Incorpore achados, atualize o spec, checkpoint commit. Só avance
quando o spec sobrevive ao review.

## Fase 5 — pós-código (sobre o diff)
Encadeie na ordem (proposital, não reordene). Nenhum destes gates é model-controlável pelo tier:
`/code-review` roda seu fleet próprio; `/simplify`/`verify`/`/security-review` rodam no
contexto do conductor (**Opus 5**), que adjudica. A Fase 5 é idêntica em `full` e `light`:
1. `/code-review` (effort alto) — bugs de correção; verifique achados adversarialmente.
   **Este é o único caça-bug de contexto fresco sobre o diff inteiro** — ele substitui o
   whole-branch review que o SDD faria no fecho da Fase 4 (ver `model-tiers.md`), em vez de repetí-lo.
2. `/simplify` — **condicional: só se o diff passa de ~150 linhas alteradas** (`git diff --stat`
   vs. `main`); em diff pequeno rende churn cosmético e ainda cobra a adjudicação. Em dúvida, rode.
   Quando roda, é **depois** do code-review (não simplificar código com bug em aberto) e **antes**
   do verify (o verify valida o resultado já simplificado).
3. `verify` / `superpowers:verification-before-completion` — rode testes/app de verdade, com evidência.
   **Sempre**, em qualquer tier e qualquer tamanho de diff.

### O `/simplify` NÃO é soberano — é conservador e adjudicado
O simplify erra para o lado da **concisão**, e concisão que remove tratamento, caso de borda ou
correção é **regressão disfarçada de limpeza**. Por isso ele **propõe**, mas o conductor **adjudica
cada mudança** — aceita só o ganho real, descarta o resto. Dois filtros antes de qualquer coisa ir pra PR:
- **Gate duro = `verify`.** Como o simplify aplica edições, ele pode introduzir regressão. O `verify`
  (passo 3) roda logo após e decide: testes quebraram → a mudança **não passa** (reverter). "Quality
  only, não caça bug" ≠ "não pode causar bug".
- **Julgamento do conductor** (filosofia `superpowers:receiving-code-review` — verificar, não concordar
  por performance). **Rejeite** mudanças do simplify que: removam tratamento de erro/caso de borda em
  nome da brevidade; piorem legibilidade ou troquem clareza intencional por concisão; violem convenções
  do projeto (português, naming, line 100, estrutura); ou sejam *churn* cosmético sem ganho real.
- **Em dúvida, NÃO simplifique.** Manter código correto e claro > deixá-lo "elegante" e sutilmente errado.

### Princípio: sem buracos temporários (fix pequeno e completo > placeholder)
Buraco temporário vira eterno. Um TODO, stub, `pass`, `...`, mock deixado no lugar de lógica, ou
"depois eu arrumo" entra como dívida silenciosa e nunca sai. No ciclo:
- **Achado pequeno → conserta agora**, completo, não adia. Um fix de 3 linhas feito direito é melhor
  que um placeholder que finge estar pronto e passa pelo gate.
- O simplify (ou qualquer fix) **nunca** pode trocar lógica real por um stub "mais simples". Isso é
  abrir buraco, não simplificar.
- Se algo genuinamente não cabe neste ciclo, **não** deixe um buraco mudo: registre explicitamente
  (issue/`docs/project_notes`) — visível e rastreável, não um `# TODO` perdido no diff.

Quem tem a palavra final no gate pós-código é o **`verify`** (objetivo: testes verdes com evidência)
somado ao conductor (subjetivo: melhora real, sem buracos, respeito às convenções). Nada vai pra push sem isso.

## O que NÃO fazer: empilhar review sobre review
Passe de LLM sobre o mesmo diff custa token e tempo, e o retorno **cai rápido** depois do primeiro
reviewer de contexto fresco: o segundo relê o mesmo código com o mesmo prior e produz sobretudo
concordância e churn. Por isso o ciclo tem **um** caça-bug por artefato — spec → staff-reviewer (F2);
diff → `/code-review` (F5) — e não um review do review. Se você está por dispachar um reviewer
adicional "só pra conferir", a pergunta certa é se existe **artefato novo** ou apenas o mesmo diff
relido. Sem artefato novo, o gate que agrega é o objetivo (`verify`, Fase 6), não outra opinião.

### Sub-gate condicional de security-review
Se o diff toca **superfície sensível** — auth, secrets/`.env`, SQL/RPC, rede/HTTP, credenciais,
browser/`page.evaluate` — dispare também `/security-review` (ou o plugin `security-guidance`).
Detecte pelos paths/conteúdo do diff. Não roda em todo ciclo.
