# Fronteira entre processo, juntada e anexo PJe

## Falha observada

Uma cópia integral do processo originário foi tratada como uma única indexação porque os arquivos
tinham o mesmo CNJ, o mesmo ato de juntada e continuidade de folhas. Isso apagou seis identidades
PJe (`parte_002` a `parte_006`, seguidas de `parte_001`) e fez o título da primeira parte parecer o
título do conjunto inteiro.

O erro oposto também era possível: o relatório do TCU contido nas primeiras partes poderia ser
interpretado como outro processo juntado, embora fosse apenas material interno da cópia judicial.

## Regra reutilizável

Decida a topologia em quatro níveis independentes:

1. processo referido;
2. ato eletrônico que realizou a juntada;
3. `carimbo_subato` e arquivo efetivamente anexado;
4. documentos e referências contidos dentro do arquivo.

Mesmo CNJ e mesmo ato não fundem arquivos distintos. Um `carimbo_subato` ou invólucro de arquivo
distinto cria fronteira auditável; cabeçalho e nome `parte_N` são evidências de apoio e precisam ser
conciliados com esse envelope e com as folhas. Quando a separação for comprovada, preserve uma
saída por arquivo e a ordem física das folhas, não a ordem numérica do sufixo. Em contrapartida,
uma referência interna não cria processo juntado autônomo sem invólucro eletrônico próprio.

Só proponha merge dentro do mesmo subato/arquivo quando a fonte demonstrar fragmentação artificial.
No split final, mantenha a referência ao processo originário em todas as partes e cite materiais
internos apenas nos resumos das faixas em que aparecem.

## Evidência do canário

- processo atual: `1031000-59.2025.4.01.0000`;
- processo originário: `1107303-36.2024.4.01.3400`;
- seis subatos nas faixas `20–199`, `200–379`, `380–559`, `560–739`, `740–921` e `922–1101`;
- ordem de anexação: `002`, `003`, `004`, `005`, `006`, `001`;
- o TCU `TC 015.561/2021-6` permaneceu conteúdo interno das partes `002` e `003`;
- o patch estrutural foi verificado com seis hashes e seis registros de linhagem.
