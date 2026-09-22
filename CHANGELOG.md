# Changelog — oli-plugins

Segue [Keep a Changelog](https://keepachangelog.com/) e SemVer por plugin
(ver [policies/SEMVER.md](policies/SEMVER.md)).

## oli-indexer-ops

### [Unreleased]

#### Added

- Primeira fonte versionada do plugin Codex de operações do `oli-indexer`, com
  12 skills para consulta segura, rastreabilidade de configuração, execução
  monitorada e pré-aprovação especializada de processos tributários.
- Protocolo comum repair-first: publica correções determinísticas como patches
  imutáveis para revisão/aplicação no `oli-app`; aplicação direta continua
  exigindo autorização explícita separada e nunca aprova o job.
- Regras aprendidas em auditoria real para não confundir etapa terminal ainda
  pendente com quebra causal, separar revisão secundária do parecer material,
  e rotear agravos e produção antecipada de provas pela especialização correta.
- Marketplace Codex do repositório em `.agents/plugins/marketplace.json` e
  teste determinístico do detector de cadeias processuais incompletas.

## oli-dev

### [Unreleased]

#### Changed

- **MAJOR — o staff-reviewer de spec (Fase 2) sai do caminho padrão e passa a rodar só no
  `full`.** Revisar spec é revisar um palpite sobre código que ainda não existe: é a camada de
  menor rendimento do ciclo, e erro de spec reaparece no diff, onde o `/code-review` da Fase 5 tem
  evidência para julgar. No default a Fase 2 é pulada **com anúncio** — pular em silêncio é o modo
  de falha. `full` passa a significar duas camadas de julgamento sobre prosa e código:
  staff-reviewer da spec (F2) + task-reviewer por task (F4). O piso de segurança fica mais
  forte: superfície sensível (auth, secrets, SQL/RPC, rede, cripto) exige **ack explícito** para
  seguir no default, já que agora são duas camadas que ficam de fora, não uma.
  Classificado como **MAJOR** (`policies/SEMVER.md`: "remoção de fase/gate").
  - Novos evals `sensitive_surface_needs_ack` e `single_cycle_artifact`;
    `skip_precode_review` e `default_tier_scope` reescritos para o novo escopo do tier.

- **Um artefato por ciclo: o plano da Fase 3 passa a ser a seção `## Plano` da spec da Fase 1.**
  Antes o ciclo produzia dois arquivos (`docs/superpowers/specs/` e `docs/superpowers/plans/`) e
  três commits antes da primeira linha de código. Agora a Fase 1 escreve a spec e grava o tier no
  cabeçalho, a Fase 3 anexa o plano na mesma spec, e **um** commit fecha os dois. É **override
  deliberado** de `superpowers:writing-plans`, que criaria arquivo próprio — a mesma classe de
  override já documentada para o branch review do SDD. O resume da Fase 0 passa a detectar
  `## Plano` dentro da spec, e ciclo antigo com arquivo separado em `plans/` continua sendo
  reconhecido como spec+plano.

- **MAJOR — o default deixa de rodar task-reviewer por task; `full` vira o opt-in que o
  readiciona.** Antes, `full` era o tier default (task-reviewer por task incluído) e `light` era
  o opt-in enxuto. Agora o default é o enxuto: sem task-reviewer por task (Fase 4) e escritores
  TDD em Sonnet — a Fase 5 (`/code-review`) cobre o mesmo diff com contexto fresco. `full` passa a
  significar uma coisa só: readiciona a aderência-à-spec por task, para contrato/enforcement/
  superfície sensível. `light` segue aceito como alias do default, por compatibilidade.
  Classificado como **MAJOR** (`policies/SEMVER.md`: "remoção de fase/gate") porque tira o
  task-reviewer do caminho padrão. Última tag: `oli-dev-v1.0.0`.
  - Command file, `plugin.json`, README e evals atualizados (`light_tier_scope` →
    `default_tier_scope`); `references/model-tiers.md` sai, ponteiros passam a
    `references/setup-gate.md`.

- **A skill sai de roteiro passo a passo para julgamento — 343 → 207 linhas (−39,6%).**
  Critério: roteiro que substitui julgamento sai, gate que impede perda de trabalho fica.
  Saíram os 7 passos numerados do setup-gate (viram objetivo + invariantes), a ordem decretada
  da Fase 5 (vira o porquê da ordem), a tabela de parsing de tier com casos de borda, o
  checklist de evidência por fase (vira um princípio) e a enumeração do mandato do
  staff-reviewer. Ficaram todos os gates: worktree da `main`, guard de branch com `gh pr view`,
  Fase 6, `verify` sempre, o ack de superfície sensível e o eco da interpretação de tier.
  Base: <https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models>.
- **O ciclo deixa de gerenciar o `/ponytail`.** O passo era ramificado por nome de tier; com a
  inversão do default ele passaria a disparar em toda invocação, sobrescrevendo um ajuste
  global do usuário. Removido em todos os caminhos.
- **Princípio 6 (delegação do conductor) vira heurística de uma linha**, com a exceção
  explícita dos gates cuja evidência é o output em si (Fase 6, `verify`) — esses o conductor
  roda e cola.

#### Fixed

- **Célula morta na matriz de tiers.** `model-tiers.md:47` listava um modelo para
  `fix-subagents` no `light`, caminho inalcançável: o fix loop do SDD só dispara com veredito
  do task-reviewer, que no `light` não rodava. Resolvido pela deleção do arquivo; o texto que
  o substitui diz o que é verdade — o fix retoma o próprio escritor, não é papel com modelo
  próprio, e a rota `BLOCKED` independe do task-reviewer.
- **`setup-gate.md` afirmava que `.claude/worktrees/` estava "já no `.gitignore`", e não havia
  `.gitignore` no repo** (`git ls-files | grep -c gitignore` → `0`). Consertado na raiz: o
  arquivo foi criado, e a frase passou a ser verdadeira. O `git status` do checkout principal
  para de ser poluído pelos worktrees.
- **Brecha na regra anti-empilhamento de review.** `review-gates.md` dava "arquivos" como
  exemplo de artefato distinto, o que autorizava fatiar um diff **já revisado** em 3 e
  despachar 3 "investigadores". Passa a exigir artefato que **nenhum gate já cobriu**.

- **Um caça-bug por artefato — o tier passa a trocar camadas de review, não modelo
  de julgamento.** O custo/latência do ciclo vinha do número de passes de LLM sobre
  o mesmo código (~15 numa mudança de 4 tasks, nos dois tiers), não do modelo de cada
  passe. Mudanças:
  - **Base (`full` e `light`): sem review final de branch na Fase 4** — a Fase 5 roda
    `/code-review` sobre o mesmo diff com fleet maior. Era o mesmo trabalho duas vezes.
    Override deliberado do SDD, marcado como tal para não voltar por deferência.
  - **Base: `/simplify` condicional** ao diff passar de ~150 linhas alteradas; em diff
    pequeno rendia churn cosmético + adjudicação.
  - **`light` derruba camada** (sem task-reviewer por task) em vez de rebaixar modelo.
    Único downgrade que resta: escritores TDD → Sonnet (maior volume de token, menor
    exigência de julgamento, saída verificada por execução de teste).
  - **Staff-reviewer (F2) volta pra Opus nos dois tiers.** Economizar modelo em gate de
    review produz palpite com selo de "revisado" — o que `review-gates.md` já chamava de
    pior que não ter reviewer.
  - Intocados: Fase 6 (lint/test) e `verify` — os únicos gates que produzem verdade
    objetiva e custam zero token.
  - Evals novos: `redundant_branch_review`, `simplify_on_tiny_diff`.

- **Tier `light` explicita TODOS os papéis despachados da Fase 4**
  (`references/model-tiers.md` + SKILL.md): além dos escritores TDD, os
  **task-reviewers** e **fix-subagents** do subagent-driven-development também
  seguem o tier (`light` = Sonnet) — fecha a ambiguidade entre o SKILL.md
  ("subagentes", plural) e a matriz (só "escritores"). ~~Exceção nova e
  explícita: o review final de branch é sempre Opus nos dois tiers~~ —
  **superseda pela entrada acima**: o review final de branch deixou de rodar
  (a Fase 5 cobre o mesmo diff), então não há modelo a fixar. Haiku fica
  documentado como fora do tier por decisão (custo de turnos em trabalho
  multi-step), não por limitação.

### [oli-dev-v1.0.0] — 2026-07-04

Primeira release do plugin como projeto independente, extraído do `oli-devops`
com histórico preservado (`git filter-repo`). Sem mudança de comportamento em
relação ao último estado no `oli-devops`.

- Maestro do ciclo de desenvolvimento OLI: worktree → brainstorm → review staff
  cético → plano → escrita TDD por subagente (tier full/light) → code-review/
  simplify/verify (+security-review condicional) → pre-push gate → PR → finalize.
- Instalação via `/plugin marketplace add devoliveiraeolivi/oli-plugins`.
