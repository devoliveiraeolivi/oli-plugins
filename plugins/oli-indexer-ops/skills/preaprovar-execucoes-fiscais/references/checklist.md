# Checklist especializada de execução fiscal

Execute depois do protocolo comum. Valores válidos vêm da configuração atual do perfil.

## 1. Fonte material versus envelope

- Em PDF virtualizado, diferencie assinatura/data material da peça e carimbo do servidor que migrou, juntou ou trasladou o documento.
- Para Julgador, preserve o magistrado e a data material. Servidor do wrapper não pode virar magistrado.
- Datas internas de CDA, decisão copiada, certidão e protocolo têm papéis diferentes; não imponha monotonicidade cega.
- Quando a página contém mais de um ato material, confira se algum ato desapareceu no Refinement ou reviewer.

## 2. Relações processuais e apensamento

Revise integralmente toda folha com relação processual e seus andamentos sobrepostos/adjacentes.

- Decisão que determina apensamento/reunião continua sendo Julgador; não é o apensamento consumado.
- Certidão que efetiva o ato é cartorária e deve preservar direção/modalidade corretas.
- Comunicação ou mero traslado cartorário permanece separada da decisão material.
- Decisão de outro processo com eficácia direta nestes autos é Julgador e preserva magistrado/data de origem e referência externa.
- Peça apenas copiada, sem eficácia direta, não vira decisão deste processo.
- Confira processo referido, direção, modalidade, efeito, evidência, grupo de relação e confiança contra OCR.
- Não colapse reunião do art. 28 da LEF em apensamento: preserve modalidade e efeito jurídicos.
- Uma sequência contínua de `Cópia dos Autos` de processo externo é uma unidade documental do
  processo principal, ainda que contenha muitos atos internos do apenso. Classifique-a como
  ponteiro/maço com `numero_processo_ref`; não crie um andamento principal por ato apenas copiado.
- O inverso também vale: decisão determinante, execução cartorária e comunicação posterior são
  atos materiais autônomos e nunca devem ser fundidos só por proximidade ou assunto comum.

### Gate de merge/split

Antes de propor mudança estrutural, responda com evidência:

1. Qual é a unidade material e onde ela começa/termina?
2. As folhas são contínuas e a união origem/saída é exatamente a mesma?
3. O envelope é único ou há atos independentes que exigem split?
4. A autoria/data vêm do ato material ou do wrapper eletrônico?
5. Há processo externo; qual direção, modalidade, efeito e função documental?
6. Cada saída tem taxonomia, responsável, referência e linhagem próprias?

Dúvida em qualquer resposta bloqueia merge/split. Para maço externo, use `content_mode=pointer`;
para peça local, `rebuild_from_folhas` e confira o hash da íntegra reconstruída.

## 3. Atos críticos da execução fiscal

- Petição inicial: exequente, executado, fundamento, pedido, responsável e data material/protocolo.
- CDA: número literalmente apoiado pelo OCR, valor, origem, devedor/coobrigado e vínculo com a inicial. Nunca complete número federal antigo por plausibilidade.
- Citação: diferencie pedido, expedição, tentativa, cumprimento positivo/negativo e comparecimento espontâneo.
- Garantias: pedido, oferta, aceitação, rejeição, substituição, reforço, penhora, seguro, fiança, avaliação e liberação são fatos distintos.
- Defesa: embargos, exceção de pré-executividade, impugnação e recursos não se confundem com comunicação de sua existência.
- Crédito: parcelamento, transação, suspensão, rescisão, pagamento, compensação, prescrição, decadência e extinção exigem ato/evidência próprios.
- Constrição/expropriação: ordem, tentativa, bloqueio, conversão, adjudicação, leilão e levantamento são estágios distintos.
- Resultado e favorabilidade derivam do dispositivo/efeito e da posição do cliente; pedido não é deferimento.

## 4. Análises e verticais fiscais

- Confira analyzers de inicial, CDA, eventos EF, julgamento, laudo e temas conforme o grafo/dispatch atual.
- Leia resumo, argumentos, dossiê de julgamentos e `passivo_tributario`/cascata quando aplicáveis.
- Concilie caixas de citação, redirecionamento, garantia/constrição, defesa, pagamento, prescrição, honorários, custas e extinção com os andamentos.
- `não decidido` pode ser resposta honesta; ausência contraditória ou caixa afirmativa sem fonte é bloqueante.
- Para cascata, confira eventos absorvidos, hashes, grupos, template e estado efetivo sem confundir checkpoint com fonte jurídica.
- Merge/split limpa horizontais e invalida, no mesmo patch, `cascata_estado`,
  `passivo_tributario`, `julgamentos` e `resumo_processual`. Nenhuma dessas estruturas pode ser
  herdada silenciosamente.
- Após a aplicação estrutural, confira rows/linhagem/íntegras e reexecute esta checklist. Só então
  proponha recomposição de eventos, analyzers horizontais e verticais; não marque `APTO` entre as
  duas etapas.

## 5. Cobertura especializada

Abra integralmente inicial/CDAs; decisões, sentenças, acórdãos e despachos; citações, defesas e recursos; garantias, constrições, parcelamentos, pagamentos e extinções; apensamentos, reuniões, traslados e cartas precatórias; e toda anomalia ou finding.

Só use `APTO` quando os gates comuns, todos esses atos críticos e as verticais aplicáveis tiverem cobertura integral.
