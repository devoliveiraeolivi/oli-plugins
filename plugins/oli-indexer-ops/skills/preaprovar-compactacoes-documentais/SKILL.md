---
name: preaprovar-compactacoes-documentais
description: Auditar em modo somente leitura jobs do oli-indexer que usaram compactação documental determinística, conciliando checkpoint, blocos fiscais de origem, grupos exibidos, herança de metadados, cobertura e exceções sem ler milhares de NF-e. Use junto da pré-aprovação do perfil quando output.compactacao_documental ou evidências compactacao_documental estiverem presentes; nunca aprova, corrige, materializa folhas, chama LLM ou reprocessa sem autorização separada.
---

# Pré-aprovar compactações documentais

Esta é uma camada adicional, não uma natureza processual. Use `$preaprovar-indexacoes` e a
especialização jurídica do perfil normalmente; depois leia
[references/checklist.md](references/checklist.md) e aplique esta régua ao caminho compactado.
Use `$consultar-oli-indexer` para todas as leituras.

## Limites

- A primeira passada é somente leitura e não chama LLM, reviewer, OCR ou Vision.
- Não baixe nem materialize todas as folhas fiscais. O PDF de origem e o checkpoint são o
  lastro; abra somente as amostras e exceções exigidas pela checklist.
- Não trate a ausência intencional de folhas compactadas em `DATA.folhas` como falha de
  extração. Bloqueie se também faltar checkpoint, fingerprint ou PDF recuperável.
- Agrupamento de apresentação nunca pode apagar os blocos técnicos do checkpoint nem atravessar
  uma página normal.
- Conflito de autoria/data não é resolvido por herança; registre-o para o agente revisor ou para
  decisão humana.

## Parecer e artefatos

Use os estados e contratos de `$preaprovar-indexacoes`. No relatório, separe obrigatoriamente:

- folhas fiscais compactadas e folhas normais;
- blocos técnicos do checkpoint e grupos exibidos;
- redução de linhas obtida;
- grupos com herança aplicada, sem origem e com conflito;
- amostra visual aberta e escalonamentos;
- rastreabilidade dos grupos aos blocos e ao PDF.

Falha sistêmica de agrupamento/herança pede correção de código e nova indexação controlada;
não gere automaticamente dezenas de merges estruturais para mascará-la. Patch versionado é
adequado apenas para exceção localizada cuja fonte, impacto e digest estejam fechados. Qualquer
recall ou reprocessamento exige autorização separada com custo e escopo.
