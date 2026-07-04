# Versionamento — oli-plugins

Cada plugin versiona **independentemente**. A tag do git é **prefixada por
plugin**: `oli-dev-vMAJOR.MINOR.PATCH` (ex.: `oli-dev-v1.0.0`).

- **MAJOR:** quebra na interface do plugin (flags/sintaxe de comando) ou
  remoção de fase/gate.
- **MINOR:** nova fase/gate/tier; ou um plugin novo entra no marketplace.
- **PATCH:** correção/documentação sem mudança de comportamento.

O `plugin.json` **não** carrega `version`: pinar obriga bumpar a cada mudança,
ou o `/plugin update` serve cache velho; sem versão, ele segue o SHA — sempre
fresco. A versão canônica é a **tag + GitHub release + seção do CHANGELOG**.

Release do GitHub intitulado `oli-dev vX.Y.Z`, com notas = seção do CHANGELOG.
