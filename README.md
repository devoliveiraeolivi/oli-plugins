# oli-plugins

Marketplace de plugins do ecossistema OLI para Claude Code e Codex.

## Plugins

| Plugin | Produto | Descrição |
|---|---|---|
| [oli-indexer-ops](plugins/oli-indexer-ops/) | Codex | Consulta, rastreia, executa e pré-aprova jobs do oli-indexer com relatórios e patches versionados, sem substituir a aprovação humana. |

O antigo `oli-dev` (Claude Code) saiu em 2026-09-30. O ciclo de engenharia agora é a
skill `engineering-task-harness`, compartilhada por Claude Code e Codex, em
[`oli-devops/harness`](https://github.com/devoliveiraeolivi/oli-devops/tree/main/harness).

## Instalação no Codex

```bash
codex plugin marketplace add devoliveiraeolivi/oli-plugins --ref main
codex plugin add oli-indexer-ops@oli-plugins
```

Após uma atualização do plugin, reinstale-o com o segundo comando e inicie uma
nova task para que as skills atualizadas sejam carregadas.

## Versionamento

Cada plugin versiona de forma independente, com tag prefixada pelo nome
(ex.: `oli-indexer-ops-vX.Y.Z`). Ver
[policies/SEMVER.md](policies/SEMVER.md).
