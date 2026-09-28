# Checklist — Conhecimento tributário

## Escopo e fallback

Use esta referência em `tributario/conhecimento`, exceto restituições judiciais e Embargos à
Execução Fiscal, que têm referências próprias. Primeiro selecione a seção material exata da
natureza. Natureza não listada pode receber a auditoria comum, mas não parecer `APTO` até existir
checklist explícita; registre a lacuna de domínio. Não transporte automaticamente gates de MS,
ação ordinária, produção de prova, cautelar ou suspensão entre si.

## Núcleo comum judicial

- Confirme partes, polos, pedidos, tributos, períodos, atos administrativos impugnados e processos relacionados.
- Abra inicial, emendas materiais, defesa/informações, manifestações, decisões, sentença, recursos, acórdãos e trânsito aplicáveis.
- Separe alegação, prova e conclusão judicial. Resultado do cliente segue o dispositivo eficaz, não o título otimista do documento.
- Decisão trasladada de outro processo com eficácia declarada aqui é ato de Julgador; cópia meramente juntada permanece documento.

## Completude causal da linha do tempo

Antes de `APTO`, construa o ledger `gatilho | consequência esperada | evidência encontrada |
lacuna` para todas as transições judiciais relevantes. Não basta conferir isoladamente que cada
row existente parece correta.

- `Petição Inicial própria → desenvolvimento do processo` exige uma única âncora inaugural
  nativa. Conte todas as rows de subclasse `Petição Inicial` no universo processual visível, não
  apenas a inicial escolhida como amostra. Zero ou mais de uma candidata impede `APTO` até a
  origem ser reconciliada.
- Para cada candidata adicional, abra a íntegra e confronte número do processo, partes, pedido,
  juntador/invólucro, `numero_processo_ref`, `mapeamento_origem`, `mapeamento_ref` e
  `mapeamento_relacao`. Se a folha estiver mapeada como `outro_processo`, `copia`, `traslado` ou
  `efeito_no_processo_atual=meramente_documental`, ela não pode permanecer como
  `Peça Processual/Petição Inicial` própria: registre a quebra e prepare a correção taxonômica com
  a referência processual demonstrada pela fonte.
- Não confunda ausência de overlap ou de duplicata textual com unicidade jurídica. A pré-aprovação
  permanece bloqueada até a cardinalidade inaugural, a classificação e a referência processual
  estarem coerentes e terem sido verificadas por readback.
- `sentença → apelação ou remessa necessária → remessa ao tribunal` abre uma etapa recursal. Ela
  pode ser o estágio terminal legitimamente pendente quando o corpus acaba na remessa e nenhum ato
  posterior pressupõe seu encerramento. Nesse caso, registre a pendência, mas não bloqueie `APTO`.
- `remessa ao tribunal → devolução à origem → trânsito/baixa/cumprimento` sem o desfecho
  intermediário é quebra lógica bloqueante. `Segunda instância: Não Julgado` não é resposta válida
  quando houve apelação ou remessa e atos posteriores pressupõem seu encerramento.
- Ato ordinatório ou certidão de trânsito prova a consequência processual, mas não substitui o
  julgamento superior ausente. Exija a fonte do tribunal e confira resultado, eficácia e
  favorabilidade antes de reconciliar as verticais.
- Se um ato posterior exigir julgamento que está em outro processo, repositório ou PDF, registre a
  fonte externa ausente e a necessidade de ingestão/merge. Não proponha patch de conteúdo e não
  aceite `100%` das folhas locais como completude dessa passagem intermediária.
- A mesma regra vale para outras ramificações causais da natureza auditada: tutela revogada ou
  substituída, incidente remetido e retornado, recurso especial/extraordinário e cumprimento que
  pressuponha título. Exija o ato que fecha cada ramo; não imponha etapas que o rito não abriu.

Inclua o ledger no parecer sempre que houver remessa, recurso, retorno, trânsito, baixa ou
cumprimento. Ramo terminal pendente é normal; somente a quebra entre atos existentes impede
`APTO`.

## Tutela cautelar antecedente

Use esta seção quando a natureza cadastrada ou a inicial adotar o procedimento cautelar
antecedente dos arts. 305 a 310 do CPC. Não aplique a ela, por analogia, a estabilização do art.
304: esse regime é próprio da tutela **antecipada** antecedente, não da cautelar antecedente.

- Delimite o risco ao resultado útil do processo, a probabilidade do direito, a medida cautelar
  pedida e o pedido principal indicado na inicial. Separe proteção provisória de satisfação
  definitiva do direito tributário.
- Identifique o ato administrativo, crédito, autorização, garantia ou efeito regulatório cuja
  eficácia se pretende conservar, suspender ou impedir, bem como os processos administrativos e
  judiciais relacionados. Cópias desses processos são prova ou contexto, salvo quando uma decisão
  trasladada receber eficácia expressa nestes autos.
- Confira a decisão que defere, indefere, limita, substitui, revoga ou faz cessar a medida:
  alcance subjetivo e objetivo, termo de eficácia, caução, reversibilidade, multa e comandos de
  cumprimento. Favorabilidade segue o dispositivo eficaz e não a formulação do pedido.
- Se a medida foi deferida, confronte a comunicação e a efetivação material com o comando. Ausência
  de efetivação enquanto ainda possível é ramo terminal pendente; afirmação posterior de
  cumprimento, revogação ou cessação sem a fonte intermediária é quebra causal.
- Confira o aditamento ou formulação do pedido principal nos mesmos autos, o marco de efetivação da
  cautelar e o prazo de 30 dias do art. 308. Registre eventual decisão específica sobre o prazo sem
  presumir que ela exista. O pedido principal pode constar da inicial cautelar; se não constar, o
  corpus que termina antes do vencimento pode estar legitimamente pendente, mas ato posterior de
  prosseguimento do mérito exige o pedido principal/aditamento ou outra fonte que explique a
  transição.
- Verifique a citação para contestar o pedido cautelar e indicar provas no prazo-base do art. 306,
  conciliado com eventual regime legal especial e com a ordem material do juízo. Depois do pedido
  principal, confira audiência ou sua dispensa, prazo de contestação, revelia quando declarada,
  réplica, prova necessária e saneamento. Não trate a contestação ao pedido principal como prova de
  que o aditamento ocorreu se a respectiva peça estiver ausente.
- A medida pode cessar nas hipóteses do art. 309: pedido principal não formulado no prazo,
  não efetivação no prazo legal, ou julgamento desfavorável/extinção sem resolução do mérito.
  Registre cessação somente quando o marco temporal e o ato correspondente estiverem nos autos;
  não a presuma do silêncio do corpus.
- Indeferimento da cautelar não equivale a improcedência automática do pedido principal, ressalvada
  decisão que reconheça prescrição ou decadência. Mantenha o mérito como `Não Julgado` enquanto não
  houver decisão final própria.
- Uma cautelar deferida pode ser `Favorável` no andamento liminar e coexistir com 1ª instância
  `Não Julgado` na vertical de mérito. Só sentença ou decisão final com cognição do pedido
  principal altera o estado corrente da instância.
- Se houver recurso contra a tutela, confira decisão recorrida, efeito atribuído, julgamento e
  eficácia atual. Recurso pendente é ramo aberto; revogação, substituição ou cumprimento posterior
  exige o pronunciamento que fechou a etapa.

Ledger mínimo desta natureza:

- `pedido cautelar antecedente → decisão`: decisão e alcance encontrados, ou lacuna;
- `deferimento → comunicação/efetivação`: mandado, intimação ou cumprimento encontrado, ou ramo
  terminal ainda pendente;
- `efetivação → pedido principal/aditamento`: peça e tempestividade encontradas, pendência dentro
  do prazo, ou cessação apoiada por fonte;
- `pedido principal → resposta/instrução → decisão final`: atos existentes em sequência, sem
  promover a liminar a julgamento de mérito;
- `recurso, revogação, substituição ou cessação → eficácia atual`: pronunciamento intermediário e
  consequência material conciliados.

## Ação anulatória ou declaratória

- Delimite ato/crédito cuja validade ou existência é discutida, tutela requerida e alcance por tributo/período.
- Confira garantia ou suspensão da exigibilidade sem tratá-la como requisito universal da ação.
- Concilie dispositivo, alcance da nulidade/declaração, sucumbência e efeitos sobre cobrança relacionada.

## MS mandamental ou declaratório

- Identifique impetrante, autoridade coatora, ato apontado, direito líquido e certo e pedido liminar/final.
- Diferencie informações da autoridade, manifestação fazendária, parecer do MP e decisão judicial.
- Confira liminar, sentença concessiva/denegatória, remessa necessária e recursos; não invente dilação probatória incompatível com o rito.

## Produção antecipada de provas

- Registre qual prova se busca, contra quem, finalidade, adequação/urgência e processo futuro relacionado.
- Confira nomeação de perito, quesitos, laudo, esclarecimentos, entrega/exibição e encerramento.
- Homologação ou encerramento da prova não decide automaticamente o mérito tributário futuro e não recebe favorabilidade como se anulasse o crédito.

## Suspensão de liminar e de sentença

- Identifique processo de origem, decisão cujos efeitos se pretende suspender, requerente legitimado e risco alegado à ordem/saúde/segurança/economia públicas.
- Classifique decisões da presidência competente, agravo interno e eventual perda de objeto como atos deste incidente.
- Não importe o mérito integral da ação originária nem trate suspensão provisória de efeitos como reforma definitiva.

## Atos críticos obrigatórios

Inicial e emendas materiais; tutela/liminar; peça de resposta própria do rito; prova decisiva;
sentença ou decisão final; decisões/acórdãos recursais; trânsito/perda de objeto; decisão
trasladada com eficácia. Para produção antecipada, inclua laudo/entrega e encerramento; para
suspensão, a decisão originária e a decisão da presidência.

Qualquer ato crítico aplicável não confrontado com a íntegra impede `APTO`.
