# oli-plugins

Marketplace de plugins do ecossistema OLI para Claude Code e Codex.

## Plugins

| Plugin | Produto | Descrição |
|---|---|---|
| [oli-dev](plugins/oli-dev/) | Claude Code | Maestro do ciclo de desenvolvimento OLI (worktree → brainstorm → review → plano → TDD → review → pre-push → PR → finalize). |
| [oli-indexer-ops](plugins/oli-indexer-ops/) | Codex | Consulta, rastreia, executa e pré-aprova jobs do oli-indexer com relatórios e patches versionados, sem substituir a aprovação humana. |

## Instalação no Claude Code

```
/plugin marketplace add devoliveiraeolivi/oli-plugins
/plugin install oli-dev
```

## Instalação no Codex

```bash
codex plugin marketplace add devoliveiraeolivi/oli-plugins --ref main
codex plugin add oli-indexer-ops@oli-plugins
```

Após uma atualização do plugin, reinstale-o com o segundo comando e inicie uma
nova task para que as skills atualizadas sejam carregadas.

## Versionamento

Cada plugin versiona de forma independente, com tag prefixada pelo nome
(`oli-dev-vX.Y.Z`, `oli-indexer-ops-vX.Y.Z`). Ver
[policies/SEMVER.md](policies/SEMVER.md).
