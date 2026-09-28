# Drift entre fonte, cache e sessão

## Sinal

Uma sessão pode continuar anunciando a revisão de plugin carregada no início mesmo depois de a
fonte local e o cache instalado avançarem. Skills novas podem não aparecer até reinstalação e nova
sessão.

## Tratamento atual

- fonte local versionada em Git;
- cachebuster único no manifesto a cada reinstalação;
- validação da fonte antes do `codex plugin add`;
- teste do catálogo somente em uma nova sessão;
- registro separado de fonte, versão instalada e versão observada pela sessão.

Não diagnosticar isso como erro semântico da skill antes de conferir as três versões.
