# Checklist especializada de execução fiscal

Execute depois do protocolo comum. Valores válidos vêm da configuração atual do perfil.

Use `$inspecionar-configuracao-indexacao` em toda auditoria deste perfil para confirmar taxonomia,
prompts, grafo, dispatch, analyzers e schemas efetivamente usados; não confie apenas no checkout.

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

- Resolva primeiro o grafo publicado. No fluxo EF v5 esperado, as operações são
  `processo.execucao_fiscal` → `processo.argumentos` → `processo.resumo`.
  Confira em `output.verticais_execucao` que cada operação declarada terminou
  `success` nesta safra; `failed` bloqueia descendentes e
  `blocked_dependency` nunca é resultado aceitável.
- Confira analyzers horizontais somente quando declarados pelo dispatch. O
  contrato atual mantém inicial e CDA determinísticos/estruturados e não exige
  mapeamento LLM ou reviewer embutido.
- Leia o ledger `processo_execucao_fiscal/v5` em `passivo_tributario`, a saída
  atual de `processo.argumentos` e o resumo atual. Concilie sujeitos, CDA/débito,
  citação, redirecionamento, garantia/constrição, defesa, pagamento,
  parcelamento, prescrição, honorários, custas, extinção e situação corrente com
  as indexações e a fonte.
- Não procure nem reconstrua `eventos_ef`, prompts em cascata, `cascata_estado`,
  dossiê clássico ou `prescricao_intercorrente` como fallback. Se alguma dessas
  estruturas antigas aparecer num job criado após o hard cut, registre drift de
  configuração/runtime.
- Menção a art. 40, frustração, hiato, parcelamento rompido ou decisão de
  prescrição é revisada dentro do ledger v5. Só componha a
  [camada legada de prescrição intercorrente](../overlays/prescricao-intercorrente.md)
  quando o grafo efetivamente declarar essa vertical ou a subárvore legada
  existir como objeto não vazio.
- `não decidido` pode ser resposta honesta; ausência contraditória, estado
  afirmativo sem fonte ou narrativa que exceda o ledger é bloqueante.
- Processo relacionado sem corpus não bloqueia quando
  `dependent_verticals={}`; registre o aviso e siga. Candidata/conflito pendente
  de decisão humana ou dependência ativa continua bloqueante.
- Merge/split invalida as análises horizontais e as três saídas v5 dependentes:
  `passivo_tributario`, `argumentos` e `resumo_processual`. Nenhuma pode ser
  herdada silenciosamente. Depois da aplicação, confira rows, linhagem e
  íntegras; a recomposição autorizada das análises é etapa separada.

### Árvore segura de correção v5

Corrija a primeira camada divergente, sem mascarar uma camada anterior:

- análise horizontal incorreta, com fonte inequívoca: use
  `indexacao.analysis.replace` com envelope completo, CAS e readback; a
  recomposição vertical posterior permanece etapa separada;
- ledger correto e somente argumentos ou resumo divergentes: use
  `job.vertical.replace` apenas se o contrato publicado aceitar o alvo e a nova
  saída completa for determinística;
- ledger `passivo_tributario` incorreto ou vertical dependente não derivável de
  forma determinística: não force patch narrativo. Corrija código/prompt em
  worktree própria e use reanálise EF autorizada.

Mudança necessária de código ou prompt fica em worktree dedicada e recebe testes antes de qualquer
publicação; a pré-aprovação apenas registra essa necessidade e não autoriza implementação, merge,
apply ou reanálise.

Por incoerência, registre operação, contrato, IDs externos, folhas, cronologia
determinante, camada de origem e tratamento. Não reindexe apenas para atualizar
relatório que possa ser validado ou corrigido deterministicamente.

## 5. Cobertura especializada

Abra integralmente inicial/CDAs; decisões, sentenças, acórdãos e despachos; citações, defesas e recursos; garantias, constrições, parcelamentos, pagamentos e extinções; apensamentos, reuniões, traslados e cartas precatórias; e toda anomalia ou finding.

Só use `APTO` quando os gates comuns, todos esses atos críticos e as verticais aplicáveis tiverem cobertura integral.

No parecer, reporte separadamente CDA, relações processuais, atos de cobrança, defesa e garantia,
verticais fiscais e custo conhecido. Não esconda processo bloqueado em totais consolidados.
