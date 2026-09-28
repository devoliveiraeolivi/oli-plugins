# Checklist de compactação documental

## Limites e escalonamento

- A primeira passada é somente leitura e não chama LLM, reviewer, OCR ou Vision.
- Não baixe nem materialize todas as folhas fiscais. O PDF de origem e o checkpoint são o lastro;
  abra somente as amostras e exceções exigidas abaixo.
- Não trate a ausência intencional de folhas compactadas em `DATA.folhas` como falha de extração.
  Bloqueie se também faltar checkpoint, fingerprint ou PDF recuperável.
- Agrupamento de apresentação nunca pode apagar blocos técnicos nem atravessar uma página normal.
- Conflito de autoria ou data não se resolve por herança; encaminhe ao reviewer ou à decisão
  humana.

Falha sistêmica de agrupamento ou herança exige correção de código e nova indexação controlada;
não gere dezenas de merges estruturais para mascará-la. Patch versionado serve apenas para exceção
localizada com fonte, impacto e digest fechados. Recall, materialização integral, OCR/Vision ou
reprocessamento exigem autorização separada com custo e escopo.

## 1. Ativação e checkpoint

- Registre `job_id`, CNJ, status, commit, gap e horário do snapshot.
- Leia `OPS.jobs.output.compactacao_documental`: modo, versão, fingerprint do PDF, tamanho,
  intervalo, métricas e plano. Ausência ou incompatibilidade bloqueia o parecer.
- Reconcilie `paginas_lidas = folhas_compactadas + folhas_normais`, limites do gap, ranges sem
  sobreposição e `unidades_efetivas` com a trava que liberou o job.
- Confirme que cada bloco foi certificado inteiro e que os blocos técnicos continuam enumerados
  no checkpoint, mesmo quando a UI mostra um grupo único.

## 2. Grupos de apresentação

Recalcule os grupos esperados sem LLM: ordene os blocos por folha e forme a sequência contínua
máxima; qualquer página não compactada encerra o grupo.

Para cada grupo, confira:

- range igual à união exata e contínua dos blocos de origem;
- nenhum ato, folha de rosto, índice ou outra página normal absorvida;
- uma única row compactada com título `Documentos fiscais (NF-e e/ou cartas de correção)`
  para DANFE/CC-e, ou título material específico para relatórios fiscais;
- evidência com ID do grupo, quantidade/hash dos blocos de origem e resumo com contagens;
- soma das folhas e tipos idêntica ao checkpoint.

Reporte `COMPACTACAO_GRUPO_FRAGMENTADO` se uma sequência esperada virou várias rows e
`COMPACTACAO_GRUPO_ATRAVESSA_ANCORA` se o grupo engoliu qualquer folha normal. Perda do vínculo
com o checkpoint é `COMPACTACAO_LASTRO_PERDIDO` e bloqueia.

## 3. Herança de metadados

Uma row compactada pode herdar somente do andamento imediatamente anterior quando todas as
guardas forem verdadeiras:

1. `origem.folha_fim + 1 = grupo.folha_inicio`;
2. origem em `Parte` ou `Terceiro`;
3. datas iguais quando ambas existem;
4. nomes responsáveis iguais após normalização; se o grupo não tiver nome, aceite apenas
   `Folha de Rosto` adjacente com a mesma data;
5. não existe sinal conflitante no grupo.

Confira somente `data`, `categoria`, `funcao_responsavel`, `nome_responsavel` e
`partes_responsaveis`. A herança não muda classe, subclasse, título, resumo, range nem
classificação fiscal. Confira o espelho final produzido depois do reviewer, não apenas o
staging de Indexing, e exija proveniência na evidência da row.

Metadado ausente apesar de origem segura é `COMPACTACAO_HERANCA_AUSENTE`. Herança sem uma das
guardas ou que sobrescreva conflito é `COMPACTACAO_HERANCA_INSEGURA` e bloqueia. Conflito em que
o sistema se absteve é encaminhado ao reviewer/humano, não corrigido por palpite.

## 4. Fonte e amostra sem explosão de custo

A cobertura estrutural é integral: reconcilie todos os ranges, tipos, contagens, hashes e rows.
Depois abra no PDF, no mínimo:

- primeira e última folha compactada de cada grupo;
- fronteiras antes/depois de cada grupo;
- um exemplar de cada tipo fiscal presente;
- todo bloco com menor confiança, metadados divergentes, chave ausente inesperada ou veto;
- qualquer grupo apontado pelo reviewer, pela taxonomia ou pela especialização jurídica.

Se uma amostra não for fiscal, contiver ato material ou discordar do checkpoint, amplie ao bloco
inteiro e aos blocos vizinhos até duas fronteiras limpas. Reincidência ou fronteira ambígua torna
o parecer `BLOQUEADO`; não dispare Vision em massa.

## 5. Resultado mensurável

Registre a fotografia antes/depois esperada:

```text
folhas_gap / compactadas / normais:
blocos_checkpoint / grupos_esperados / rows_compactadas_atuais:
rows_totais_atuais / rows_totais_agrupadas / reducao:
herancas_seguras / aplicadas / conflitos / sem_origem:
amostras_abertas / escalonadas / inacessiveis:
```

`APTO` exige reconciliação integral do checkpoint e dos grupos, amostra obrigatória limpa,
metadados de todas as rows e todos os gates da especialização jurídica. A amostra isolada nunca
autoriza aprovação.
