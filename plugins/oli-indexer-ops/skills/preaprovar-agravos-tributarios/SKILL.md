---
name: preaprovar-agravos-tributarios
description: Auditar em modo somente leitura Agravos de Instrumento tributários nativos do perfil tributario/agravo_instrumento no oli-indexer. Use antes da aprovação humana para conferir processo de origem, decisão recorrida, peças de formação, tutela recursal, julgamentos monocráticos e colegiados, embargos, perda de objeto, trânsito, análises e custos; nunca aprova, corrige, chama LLM ou reprocessa sem autorização específica.
---

# Pré-aprovar agravos tributários

Produza um parecer técnico anterior à decisão do usuário. A aprovação humana continua sendo exclusivamente dele.

Use `$preaprovar-indexacoes` para o protocolo compartilhado, leia [references/checklist.md](references/checklist.md) e use `$inspecionar-configuracao-indexacao` para confirmar taxonomia, prompts, grafo, dispatch, analyzer e schemas atuais. As regras desta skill são adicionais às regras comuns.

## Escopo

- O perfil alvo é `tributario/agravo_instrumento`, com natureza `Agravo de Instrumento`; não decida apenas pelo assunto, título ou menção a agravo.
- A skill audita os próprios autos do AI. Um bloco de AI juntado em ação de conhecimento ou execução fiscal pertence à especialização do processo principal e usa regras de cópia/eficácia próprias.
- Sem job/CNJ explícito, liste todos os jobs desse perfil em `awaiting_approval`, não aprovados, e informe a quantidade.

## Custo e autoridade

- A primeira passada é integralmente somente leitura e sem LLM. Reviewer já executado pode ser analisado; não o rode novamente.
- Antes de correção, recall, pipeline ou reviewer, apresente escopo, chamadas/modelos, custo estimado e alternativa determinística. Prossiga somente com autorização explícita.
- Nunca altere `approved_at`, `approved_by`, `status` para conclusão ou o gate de revisão secundária.

## Parecer

Use os estados e a cobertura de `$preaprovar-indexacoes`. `APTO` exige protocolo comum integral e checklist recursal integral. Para cada processo, apresente primeiro um resumo e depois cada achado no formato `fls. | está | deve ficar | por quê`, identificando o `id_externo` quando houver correção proposta.

Reporte separadamente origem/decisão recorrida, tutela recursal, julgamento final do AI, incidentes posteriores, trânsito/baixa, análises verticais e custo conhecido. Não esconda um processo bloqueado em totais consolidados.

## Correções

Pré-aprovação não autoriza aplicar correção. Gere no máximo um patch corrente por processo no
contrato compartilhado e mantenha `proposto → aprovado pelo usuário → aplicado → verificado`.
Fusão ou divisão de andamentos não é operação v1: registre achado bloqueante, sem improvisar
updates. Snapshot before/readback/after pertencem ao runner após o clique no app.
