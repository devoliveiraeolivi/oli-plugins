---
name: preaprovar-restituicoes-tributarias
description: Auditar em modo somente leitura ações judiciais de restituição tributária do oli-indexer, incluindo Ação Restituição e MS - Restituição no perfil tributario/conhecimento. Use antes da aprovação humana para conferir objeto do indébito, períodos, provas, liminar, sentença, recursos, cumprimento, resultados e análises; não use para PER/DCOMP administrativo e nunca aprove, corrija, chame LLM ou reprocesse sem autorização separada.
---

# Pré-aprovar restituições tributárias

Produza um parecer técnico anterior à decisão do usuário. A aprovação humana continua sendo exclusivamente dele.

Use `$preaprovar-indexacoes` para o protocolo compartilhado, leia [references/checklist.md](references/checklist.md) e use `$inspecionar-configuracao-indexacao` para confirmar taxonomia, prompts, grafo, dispatch, analyzer e schemas atuais. As regras desta skill são adicionais às regras comuns.

## Escopo

- Exija `area=tributario`, `perfil=conhecimento` e natureza `Ação Restituição` ou `MS - Restituição`; confirme também a classe cadastral `Restituição` quando disponível.
- Não aplique esta régua a toda ação de conhecimento. Ação anulatória, declaratória, embargos à execução e produção antecipada seguem outras particularidades.
- Não inclua `administrativo_creditorio`: PER/DCOMP, pedido administrativo de ressarcimento/restituição, despacho decisório, DRJ e CARF pertencem à régua administrativa.
- Sem job/CNJ explícito, liste todos os jobs de restituição em `awaiting_approval`, não aprovados, e informe separadamente ações ordinárias e mandados de segurança.

## Custo e autoridade

- A primeira passada é integralmente somente leitura e sem LLM. Reviewer já executado pode ser analisado; não o rode novamente.
- Antes de correção, recall, pipeline ou reviewer, apresente escopo, chamadas/modelos, custo estimado e alternativa determinística. Prossiga somente com autorização explícita.
- Nunca altere `approved_at`, `approved_by`, `status` para conclusão ou o gate de revisão secundária.

## Parecer

Use os estados e a cobertura de `$preaprovar-indexacoes`. `APTO` exige protocolo comum integral e checklist de restituição integral. Para cada processo, apresente primeiro um resumo e depois cada achado no formato `fls. | está | deve ficar | por quê`, identificando o `id_externo` quando houver correção proposta.

Antes de emitir `APTO`, execute explicitamente o ledger de completude causal do protocolo comum e
teste todos os casos de regressão da checklist. Em especial, toda apelação ou remessa necessária
deve terminar em um desfecho recursal material antes de retorno, trânsito ou cumprimento. Não
trate `Segunda instância: Não Julgado` como solução para julgamento superior ausente.

Reporte separadamente objeto tributário, modalidade de recuperação, período/valores, cadeia de julgamentos, eficácia de atos de outros autos, análises verticais e custo conhecido. Não esconda um processo bloqueado em totais consolidados.

## Correções

Pré-aprovação não autoriza aplicar correção. Gere no máximo um patch corrente por processo no
contrato compartilhado e mantenha `proposto → aprovado pelo usuário → aplicado → verificado`.
Se a fonte correta já estiver disponível, publique a proposta; snapshot before/readback/after
pertencem ao runner após o clique no app. Não reindexe apenas para atualizar relatório ou
vertical que possa ser corrigido e validado deterministicamente.

Como restituições frequentemente chegam em incrementos, confira o proprietário de cada
andamento em `DATA.indexacoes.job_id`. Se a correção recair em incremento anterior, preserve
esse `job_id` no alvo do patch e aplique as guardas comuns de mesmo CNJ, row `concluido` e job
atual elegível; nunca copie o id do job corrente para a row antiga.
