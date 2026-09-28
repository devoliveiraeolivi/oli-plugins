# Runtime local do worker

Este arquivo preserva o nome antigo apenas para não quebrar links de versões
instaladas. O contrato vigente não é portátil por container: a execução de
código do `oli-indexador` ocorre localmente, no checkout atual, com `uv run` e
o `.env` local.

- Não subir Docker local.
- Não procurar worker em VPS ou Portainer.
- Não usar o repositório histórico `oli-indexer` como runtime.
- Não exigir deploy do worker depois de mudança comum de pipeline.
- Em checkout limpo, atualizar com `git pull --ff-only` antes da execução. Em
  checkout sujo, preservar mudanças e usar worktree limpa ou aguardar o usuário.
- Deploy manual do usuário só entra quando a mudança atinge
  `oli-indexer-api`, `oli-indexer-patch`, `oli-gateway`, `oli-app` ou `oli-bi`.

Não use `scripts/oli_ops.py`, `assets/host-config.example.json`, imagem OCI,
`doctor` Docker ou ceilings monetários para o fluxo atual. Esses artefatos são
legado da arquitetura portátil anterior e não concedem autoridade operacional.
