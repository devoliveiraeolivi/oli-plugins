---
name: oli-dev
description: Roda o ciclo de desenvolvimento OLI (worktree → brainstorm → review → plano → escrita TDD → review → pre-push → PR). Use `/oli-dev <ideia>` para iniciar o ciclo (default enxuto: sem task-reviewer por task, escritores TDD em Sonnet), `/oli-dev full <ideia>` para readicionar o task-reviewer por task, ou `/oli-dev finalize` para a limpeza pós-merge.
---

Argumentos recebidos: `$ARGUMENTS`

Invoque a skill `dev-cycle` (plugin oli-dev) e siga-a à risca. Faça o parsing de `$ARGUMENTS`
(case-insensitive; `W1` = primeira palavra):

1. Se `W1` == `finalize` (match **exato**, não "começa com") → modo **finalize** (apenas Fase 8:
   close-out + limpeza pós-merge).
2. Senão, se `W1` ∈ {`light`, `full`} **e** houver ≥1 palavra depois → **tier** = `W1` (`light` é
   alias do default, aceito por compatibilidade) e a **ideia** é o resto → modo **ciclo** (Fases 0–7).
3. Senão → tier não informado (default **enxuto**, equivalente a `light`); toda a `$ARGUMENTS` é a
   ideia → modo **ciclo**.

O tier troca **camadas de review**, não modelo: o **default não roda task-reviewer** por task —
a Fase 5 cobre o mesmo diff com contexto fresco. `full` readiciona essa camada, para
contrato/enforcement/superfície sensível; nesse caso **peça ack explícito** antes de seguir no
default. Escritores TDD em `model: "sonnet"` nos dois. Conductor, staff-reviewer (Fase 2) e
adjudicação seguem em Opus em ambos; `/code-review`, `verify` e o pre-push gate inalterados.
Ao reconhecer `light`/`full` como 1ª palavra, **ecoe** *"tier=X, ideia='…'"* — o token some da
ideia, e truncar em silêncio é o modo de falha.
Em ambos: **sem review final de branch** na Fase 4 (a Fase 5 cobre o mesmo diff) e `/simplify`
só se o diff passa de ~150 linhas. Detalhes: `references/setup-gate.md`.

Não pule fases nem gates. Os Princípios de processo do spec são invioláveis.
