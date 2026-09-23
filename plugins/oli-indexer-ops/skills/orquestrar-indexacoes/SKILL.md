---
name: orquestrar-indexacoes
description: Orquestrar jobs do oli-indexador da descoberta ou criação até os gates técnicos e a pré-aprovação final usando o checkout local, `.env`, IDs exatos, CAS e readback. Use no fluxo integral ou para avançar uma safra; nunca substitua aprovação humana nem acione Conclusion sem autoridade posterior específica.
---

# Orquestrar indexações

Conduza o caminho feliz com o menor número de intervenções e abra diagnóstico
somente quando surgir uma exceção estruturada. OPS, leases e os ledgers de cada
gate continuam sendo a fonte operacional.

Antes de operar, leia [references/workflow.md](references/workflow.md). Para
qualquer escrita, materialize também a
[intenção de orquestração](references/intent.md). Use
`$consultar-oli-indexer` para snapshots e
`$inspecionar-configuracao-indexacao` quando a decisão depender de prompt,
grafo, taxonomia, contrato, dispatch ou analyzer efetivamente executado.

## Runtime obrigatório

- Execute o worker no checkout local de `oli-indexador`, com `uv run` e o
  `.env` local. Não use Docker, VPS, Portainer, imagem OCI nem o repositório
  histórico `oli-indexer` para executar o batch.
- Antes da execução, confira branch/commit e `git status`. Em checkout limpo,
  atualize com `git pull --ff-only`; se houver mudanças locais, preserve-as e
  use uma worktree limpa ou peça ao usuário que faça a atualização.
- Não exija deploy do worker. Deploy só pode ser necessário quando a mudança
  atingir `oli-indexer-api`, `oli-indexer-patch`, `oli-gateway`, `oli-app` ou
  `oli-bi`; o usuário executa esses deploys manualmente.
- Nunca abra site, Portainer ou painel de produção para substituir a confirmação
  do usuário sobre deploy.

## Autoridade

- Consulta ou diagnóstico não autoriza enqueue, execução, patch ou aceite.
- “Crie e execute” autoriza somente o conjunto resolvido no snapshot inicial e
  para no primeiro gate técnico.
- “Fluxo completo” ou pedido que inclua pré-aprovação autoriza atravessar os
  gates técnicos pelas skills próprias, inclusive correções determinísticas
  previstas e aceites técnicos depois de parecer sucessor positivo e fresco.
- A autorização do processo cobre as chamadas normais do pipeline. Não invente
  `max_llm_calls`, teto monetário, tokens, custo por chamada ou tempo. O gate
  extraordinário é escopo superior a 2.500 folhas, que exige autorização
  explícita antes da execução.
- Essa autoridade termina depois de `$preaprovar-indexacoes`; o job continua
  dependente de aprovação humana.
- Conclusion exige pedido posterior específico ou intenção durável ainda
  válida com `conclude_human_approved=true`. Delegue a
  `$concluir-indexacoes-aprovadas`; nunca execute `--run-approved` diretamente.
- Recall, delete, correção ad hoc, mudança de fonte, LLM fora do pipeline,
  deploy e ampliação de escopo permanecem fora desta skill.

## Composição dos gates

Avance um job por vez:

1. `pending`: execute o job exato;
2. `awaiting_extraction_review`: use `$preaprovar-extracoes`;
3. `awaiting_indexing_review`: use `$preaprovar-insumos-indexacao`;
4. depois de Analysis/Validation: use `$preaprovar-indexacoes`;
5. `awaiting_approval` sem `approved_at`: entregue para aprovação humana;
6. `awaiting_approval` com `approved_at`: apenas a skill explícita de
   Conclusion pode continuar.

`PIPELINE_ENABLE_MAPEAMENTO=false` e `PIPELINE_ENABLE_REVIEWER_AGENT=false`
são o contrato atual: não execute, repare, exija ou simule essas fases. O grafo
publicado decide quais verticais existem; ausência não autoriza fallback legado.

Pare diante de parecer negativo/ambíguo, snapshot stale, lease incompatível,
cardinalidade divergente ou escopo acima de 2.500 folhas sem autorização. Não
improvise transição nem use log como substituto de readback.

## Entrega

Reporte o recibo local, repo/commit, jobs/CNJs, folhas, fases, pareceres,
patches/readbacks, telemetria conhecida, bloqueios e próxima autoridade. Separe
aceite técnico, pré-aprovação final, aprovação humana, Conclusion e deploy.
