---
name: rodar-e-preaprovar-indexacao
description: Orquestrar no oli-indexer a descoberta ou criação de jobs, execução monitorada e pré-aprovação especializada, com prevenção de duplicidade e medição de custo. Use quando o usuário pedir o fluxo diário completo; não use para aprovar ou concluir jobs em nome dele.
---

# Rodar e pré-aprovar indexação

Execute o fluxo diário como uma cadeia auditável, sem misturar autorização para criar/rodar com autorização para reprocessar, corrigir ou aprovar.

Antes de operar, leia [references/workflow.md](references/workflow.md) e use `$consultar-oli-indexer` para snapshots. Após a execução, use `$preaprovar-indexacoes`, que aplica a régua comum e compõe a especialização correta. Use `$inspecionar-configuracao-indexacao` quando a execução ou o parecer depender de prompt, grafo, taxonomia ou analyzer.

## Autoridade

- “Crie os jobs e execute” autoriza enqueue e execução apenas para o escopo explicitamente resolvido nesta solicitação.
- Não autoriza `--allow-multiple`, recall, delete, conclusão, aprovação, correção de staging, mudança de prompt ou novo run após falha.
- Antes de LLM/reprocessamento não previsto, mostre custo estimado e peça autorização.
- Nunca altere o gate de aprovação humana nem rode `--run-approved` sem pedido explícito posterior do usuário.

## Entrega

Reporte jobs criados/pulados, job IDs/CNJs, fases executadas, retries/fallbacks, cobertura,
custo por operação e folha, parecer especializado e próximos passos. A pré-aprovação publica
o relatório e o patch proposto no control plane pelo fluxo compartilhado, mas não aplica o
patch nem aprova o job. Preserve logs locais sem expor segredos. Um job operacionalmente
concluído pode continuar semanticamente bloqueado.
