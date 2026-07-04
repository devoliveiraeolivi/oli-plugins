# oli-plugins

Marketplace de plugins do ecossistema OLI para Claude Code.

## Plugins

| Plugin | Descrição |
|---|---|
| [oli-dev](plugins/oli-dev/) | Maestro do ciclo de desenvolvimento OLI (worktree → brainstorm → review → plano → TDD → review → pre-push → PR → finalize). |

## Instalação

```
/plugin marketplace add devoliveiraeolivi/oli-plugins
/plugin install oli-dev
```

## Versionamento

Cada plugin versiona de forma independente, com tag prefixada por plugin
(`oli-dev-vX.Y.Z`). Ver [policies/SEMVER.md](policies/SEMVER.md).
