---
name: preaprovar-execucoes-fiscais
description: Auditar em modo somente leitura as execuções fiscais do oli-indexer que aguardam aprovação, conferindo classificação, CDA, eventos fiscais, relações processuais, decisões, responsáveis, análises e custos contra as fontes. Use antes da aprovação humana; nunca aprova o job nem chama LLM ou reprocessa sem autorização específica.
---

# Pré-aprovar execuções fiscais

Produza um parecer técnico anterior à decisão do usuário. A aprovação humana continua sendo exclusivamente dele.

Use `$preaprovar-indexacoes` para o protocolo compartilhado, leia [references/checklist.md](references/checklist.md) e use `$inspecionar-configuracao-indexacao` para confirmar taxonomia, prompts, grafo, dispatch, analyzer e schemas atuais. As regras desta skill são adicionais às regras comuns.

## Escopo e custo

- O perfil alvo é `tributario/execucao_fiscal`; não decida apenas pelo assunto ou CNJ.
- Sem job/CNJ explícito, liste todos os jobs desse perfil em `awaiting_approval`, não aprovados, e informe a quantidade.
- A primeira passada é integralmente somente leitura e sem LLM. Reviewer já executado pode ser analisado; não o rode novamente.
- Antes de qualquer correção, recall, pipeline ou reviewer, apresente escopo, chamadas/modelos, custo estimado e alternativa determinística. Prossiga somente com autorização explícita.
- Nunca altere `approved_at`, `approved_by`, `status` para conclusão ou o gate de revisão secundária.

## Parecer

Use os estados e a cobertura de `$preaprovar-indexacoes`. `APTO` exige protocolo comum integral e checklist fiscal integral. Reporte separadamente CDA, relações processuais, atos de cobrança/defesa/garantia, verticais fiscais e custo conhecido.

## Correções

Pré-aprovação não autoriza aplicar correção. Quando a fonte correta já estiver disponível,
modele metadados/análises pelo `review-patch/v1` compartilhado. Quando o erro for de unidade
documental, use `review-patch/v2` para merge/split somente depois de provar cobertura e linhagem.
Publique a proposta junto do relatório; o runner fará snapshot before/readback/after após
aprovação explícita no app. Mudança de código ou prompt fica em worktree e recebe testes. Não
reindexe apenas para atualizar um relatório que pode ser validado deterministicamente.

Patch estrutural de EF invalida obrigatoriamente `cascata_estado`, `passivo_tributario`,
`julgamentos` e `resumo_processual`. Depois de aplicado, rode a pré-aprovação novamente sobre as
novas rows; recomposição horizontal/vertical e eventual LLM têm autorização e custo separados.
