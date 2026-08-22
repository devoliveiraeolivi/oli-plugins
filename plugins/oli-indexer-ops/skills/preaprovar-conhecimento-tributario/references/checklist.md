# Checklist — Conhecimento tributário

## Núcleo comum judicial

- Confirme partes, polos, pedidos, tributos, períodos, atos administrativos impugnados e processos relacionados.
- Abra inicial, emendas materiais, defesa/informações, manifestações, decisões, sentença, recursos, acórdãos e trânsito aplicáveis.
- Separe alegação, prova e conclusão judicial. Resultado do cliente segue o dispositivo eficaz, não o título otimista do documento.
- Decisão trasladada de outro processo com eficácia declarada aqui é ato de Julgador; cópia meramente juntada permanece documento.

## Completude causal da linha do tempo

Antes de `APTO`, construa o ledger `gatilho | consequência esperada | evidência encontrada |
lacuna` para todas as transições judiciais relevantes. Não basta conferir isoladamente que cada
row existente parece correta.

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
