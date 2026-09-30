# Versionamento — oli-plugins

Cada plugin versiona **independentemente**. A tag do git é **prefixada por
plugin**: `<plugin>-vMAJOR.MINOR.PATCH` (ex.: `oli-indexer-ops-v0.1.0`).

- **MAJOR:** quebra na interface do plugin (flags/sintaxe de comando) ou
  remoção de fase/gate.
- **MINOR:** nova fase/gate/tier; ou um plugin novo entra no marketplace.
- **PATCH:** correção/documentação sem mudança de comportamento.

No Claude Code, o `.claude-plugin/plugin.json` **não** carrega `version`: pinar
obriga bumpar a cada mudança, ou o `/plugin update` serve cache velho; sem
versão, ele segue o SHA — sempre fresco.

No Codex, o `.codex-plugin/plugin.json` exige SemVer válido. Durante o
desenvolvimento local, um sufixo `+codex.<cachebuster>` pode ser usado apenas na
cópia instalada; a fonte versionada mantém o número base da próxima release.
A versão canônica continua sendo a **tag + GitHub release + seção do
CHANGELOG**.

Release do GitHub intitulada `<plugin> vX.Y.Z`, com notas = seção do CHANGELOG.
