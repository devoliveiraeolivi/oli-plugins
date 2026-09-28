---
name: inspecionar-configuracao-indexacao
description: Rastrear a configuração efetivamente usada por um job do oli-indexer, incluindo prompts, hashes, grafo, perfil, taxonomia, schemas e dispatch. Use para explicar resultados ou drift; a inspeção não autoriza publicação nem reprocessamento.
---

# Inspecionar configuração da indexação

Responda à pergunta “qual configuração realmente produziu este resultado?” com evidência, sem assumir que o arquivo aberto no checkout foi o runtime do job.

Antes da inspeção, leia [references/mapa.md](references/mapa.md) e use `$consultar-oli-indexer` para os dados. Para prompts e análises, prefira os subcomandos `prompts` e `analises` de `scripts/oli_db.py`.

## Modos

- **Traçar um job:** parta do job/perfil e relacione chamadas, hashes, grafo/nó, prompts e envelopes produzidos.
- **Explicar uma row:** parta de `id_externo`/folhas/tripla, derive o analyzer esperado e compare schema/resultado com a fonte.
- **Auditar drift:** compare git resolvido, `DATA.prompts`, histórico e `OPS.llm_runs.template_hash`; diferencie “publicado agora” de “usado naquele job”.
- **Preparar mudança:** identifique a camada responsável e proponha arquivo/mecanismo correto. Não edite banco, prompt ou grafo sem pedido explícito.

## Saída

Informe job/CNJ, commit/worktree, área/perfil, operação, origem de cada evidência, hash completo ou prefixo inequívoco, grafo/nó quando disponível, configuração efetiva, divergências e impacto provável. Separe fato, inferência e ausência de telemetria.
