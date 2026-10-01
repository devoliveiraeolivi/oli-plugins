# Checklist — Cumprimento de sentença tributário

## Escopo

Use esta referência em `tributario/cumprimento_sentenca`, que recebe as 7 naturezas tributárias
de cumprimento ("Cump. Sentença - Honorários O&O", "- Honorários Fazenda", "- Crédito",
"- Mandamental", "- Provisório", "Cumpr. Sentença - Honorários (Outros Advs)" e "Cumprimento de
Sentença"). A taxonomia é a do conhecimento tributário, mais os atos de execução da execução fiscal
com os mesmos nomes, mais as subclasses próprias do cumprimento (spec 0001 §3.3 do
`oli-indexador`).

Antes dos gates, identifique nos autos, não no cadastro:

- **Tipo de autos.** Autônomos: CNJ próprio, só a execução, com o título judicial em cópia. Mistos:
  mesmo CNJ, a fase de conhecimento nativa e depois o cumprimento.
- **Rito.** Fazenda executada (arts. 534-535: impugnação, cálculos, RPV ou precatório); particular
  executado (art. 523: multa, penhora, SISBAJUD, protesto); obrigação de fazer (art. 536);
  provisório (art. 520).
- Natureza cadastral incompatível com o conteúdo (ex.: desapropriação ou ação bancária cadastrada
  como cumprimento tributário) é lacuna de identidade: registre e não emita `APTO`.

Nos mistos, a fase de conhecimento usa o núcleo comum e a completude causal de
[conhecimento tributário](conhecimento-tributario.md); os gates abaixo valem a partir da virada.

## Gate 1 — Abertura e pertinência

- A âncora inaugural exige ao menos uma row nativa entre `Petição Inicial` (só nos mistos),
  `Requerimento de Cumprimento de Sentença` e `Requerimento de Liquidação de Sentença`, todas em
  `Parte / Peça Processual`. Sem nenhuma, a Conclusion bloqueia (`SEM_ANCORA_ADMINISTRATIVA`,
  mensagem "âncora inaugural"): não emita `APTO`.
- O rótulo "Petição inicial" do PJe e do Projudi não decide a subclasse. Nos autônomos, `Petição
  Inicial` nativa exige abrir a íntegra: o requerimento é `Requerimento de Cumprimento de Sentença`
  (patchável); lista de movimentos, certidão de migração ou folha vazia seguem o conteúdo.
- Peça nova protocolada nestes autos e dirigida a este cumprimento é nativa, mesmo citando o CNJ
  do processo de origem. Requerimento, impugnação ou manifestação sobre cálculos rebaixados a
  `Parte / Documento / Documento` com `Cópia — ` por citar o principal são erro de pertinência.

## Gate 2 — Cópias do título

- Inicial, sentença, acórdão, certidão de trânsito e cálculos do processo de origem em cópia são
  `Parte / Documento / Documento`, `numero_processo_ref` = origem, título `Cópia — `; um andamento
  por processo copiado. Nunca `Petição Inicial`, `Julgamento` ou `Trânsito em Julgado` destes autos.
- Autos alheios juntados pelo cartório sem figura própria são `Cartório / Juntada / Juntada de
  Cópia Integral`, sem o prefixo `Cópia — `.
- Julgamento do título só em cópia não abre ramo recursal destes autos: não cobre remessa,
  devolução nem trânsito que pertencem ao processo de origem.

## Gate 3 — Virada de fase nos mistos

- A passagem é registrada por `Cartório / Movimentação / Início do Cumprimento de Sentença`
  (alteração de classe, reautuação) e pelo requerimento. Ledger: `trânsito em julgado ou decisão
  exequível → requerimento → intimação do executado → pagamento ou impugnação`.
- Requerimento definitivo antes do trânsito, sem indicação de cumprimento provisório, é quebra a
  conferir na íntegra.

## Gate 4 — Decisões do cumprimento

- `Julgador / Julgamento / Julgamento: Decisão sobre Impugnação ou Cálculos`: resolve a
  impugnação (art. 525 ou 535) ou fixa o valor (homologa cálculos, acolhe a contadoria, decide
  excesso) **sem extinguir**. Não é `Julgamento: Sentença de Mérito` nem `Decisão Interlocutória`.
- `Julgador / Decisão Interlocutória / Decisão Interlocutória: Suspensão do Cumprimento`: suspende
  ou sobresta (falta de bens e arquivamento provisório do art. 921, acordo do art. 922, art. 313,
  tema repetitivo). O arquivamento feito pelo cartório é `Arquivamento`; a retomada é `Cartório /
  Movimentação / Levantamento de Suspensão`.
- `Julgamento: Extinção do Cumprimento de Sentença`: só a decisão que extingue a fase de cobrança,
  por qualquer causa do art. 924 (pagamento, acordo, renúncia, prescrição intercorrente). Pagamento
  ou levantamento sem decisão extintiva não é extinção; extinção por pagamento sem pagamento nem
  levantamento nos autos é lacuna a conferir.

## Gate 5 — Requisição, pagamento e levantamento

Ledger da Fazenda executada: `decisão que fixa o valor ou concordância → Expedição de Requisição
de Pagamento → Pagamento de Requisição → Expedição de Alvará ou Expedição de Ofício de
Transferência → Extinção do Cumprimento de Sentença`.

- Ramo terminal pendente é normal (precatório aguardando pagamento, levantamento ainda não pedido).
  Quebra é ato posterior que pressupõe o anterior ausente: pagamento sem requisição, levantamento
  sem pagamento, extinção por pagamento sem nenhum dos dois.
- Classes: a requisição não é `Expedição de Ofício`; o extrato de pagamento não é `Pagamento de
  Depósito` nem `Atos de Cartório`; a transferência por TED é `Expedição de Ofício de
  Transferência`; o alvará continua `Expedição de Alvará`.
- Cálculos: planilha do exequente ou da Fazenda é `Parte / Documento / Documento (Memória de
  Cálculo)`; cálculo do juízo é `Terceiro / Petições de Terceiros / Cálculo da Contadoria`
  (`Contador Judicial`). Certidão de teor para protesto (art. 517) é `Cartório / Expedição /
  Expedição de Certidão para Protesto`.

## Gate 6 — Constrição e expropriação

Execução contra particular usa as mesmas subclasses e regras da execução fiscal.

- Três partes: pedido → `Cartório / Expedição / Pedido de Bloqueio SISBAJUD` (e os de CNIB,
  RENAJUD, INFOJUD, SerasaJud); resposta consolidada → `Cartório / Juntada / Resposta Consolidada
  …`; resposta de uma instituição → `Terceiro / Resposta a Ofício / Resposta …`, `Registro de
  Imóveis` ou `Depositário Público`. A resposta individual segue o produtor mesmo juntada pelo
  servidor.
- `Cartório / Juntada / Auto de Penhora e Avaliação` (oficial, com avaliação) × `Cartório /
  Certidão / Penhora (Lavratura)`, `Penhora (Averbação)` ou `Constrição Negativa`.
- Carta precatória devolvida é um andamento `Juntada de Carta Precatória (Devolvida)`; atos e
  baixa da própria carta no juízo deprecado não são movimentação destes autos.
- Expropriação: `Expedição de Edital de Leilão` → `Auto de Arrematação`, `Auto de Adjudicação` ou
  `Termo de Remição`. Garantia ofertada pela parte é `Parte / Documento / Documento (Garantia)`.
- Ledger: `decisão que defere a constrição → pedido ou mandado → resposta, auto ou certidão →
  levantamento, transferência ou desbloqueio`.

## Limitações conhecidas do indexador

Registre no parecer, sem tratar como erro do job:

- O requerimento passa pela análise de manifestação, não pela de petição inicial: nos autônomos,
  objeto e pedidos da ação podem sair vazios.
- Nos autônomos não há `Petição Inicial` destes autos; confira a data do `Índice Processual` e dos
  primeiros atos contra o requerimento, não contra a inicial copiada.

## Atos críticos obrigatórios

Requerimento de cumprimento ou de liquidação; memória de cálculo do exequente e da Fazenda;
impugnação e a decisão sobre ela ou sobre os cálculos; requisição, pagamento e levantamento ou
transferência; pedidos, respostas e autos de constrição; suspensão e retomada; extinção. Nos mistos,
também a sentença, os acórdãos e o trânsito da fase de conhecimento e a virada de fase.

Qualquer ato crítico aplicável não confrontado com a íntegra impede `APTO`.
