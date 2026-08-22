# Checklist especializada de restituições tributárias judiciais

Execute depois do protocolo comum. Valores taxonômicos e analyzers válidos vêm da configuração atual do perfil `tributario/conhecimento`.

## 1. Identidade do rito

- Separe `Ação Restituição` de `MS - Restituição`. Ambas discutem indébito, mas a sequência processual e os efeitos do provimento não são intercambiáveis.
- No mandado de segurança, informações da autoridade coatora são `Parte / Peça Processual / Informações da Autoridade Coatora`, com função `Autoridade Coatora`; não são ofício de terceiro. Diferencie autoridade coatora, União/Fazenda interessada e Ministério Público.
- No rito comum, confira contestação, réplica, saneamento, perícia, memoriais, sentença e recursos sem importar terminologia do mandado de segurança.
- Não misture restituição judicial com `administrativo_creditorio`. PER/DCOMP e decisões de Receita/DRJ/CARF juntadas como prova continuam documentos, salvo ato com eficácia processual direta demonstrada.

## 2. Objeto econômico e jurídico

Na inicial, decisões, laudos e julgamentos, confronte a fonte para registrar sem extrapolação:

- tributo/contribuição e tese material discutida;
- origem do indébito, fato gerador e período alcançado;
- valor pedido, valor comprovado e valor reconhecido, sem transformar estimativa ou laudo em condenação;
- modalidade pedida e deferida: declaração de inexigibilidade, reconhecimento de crédito, compensação, restituição judicial por RPV/precatório ou restituição administrativa;
- prescrição/decadência, modulação, art. 166 do CTN, SELIC e outros limitadores somente quando efetivamente enfrentados;
- matriz/filiais, legitimidade e polo do cliente quando relevantes.

Pedido, prova, cálculo, reconhecimento do direito e efetivo pagamento/compensação são estados distintos. O título e o resumo devem dizer qual deles ocorreu.

## 3. Atos críticos

Abra integralmente a fonte de:

- petição inicial e emendas que alterem pedido, período, valor ou fundamento;
- tutela/liminar, inclusive postergação, revogação e perda de objeto;
- informações da autoridade coatora, contestação, réplica e manifestações fiscais;
- saneamento, deferimento/indeferimento de prova, laudo, esclarecimentos e homologação de cálculos;
- sentença, acórdão, decisão monocrática, embargos, agravo interno, REsp/AREsp, RE e respectivas admissibilidades;
- trânsito em julgado, cumprimento, compensação, RPV/precatório, alvará e extinção da fase executiva;
- bloco de outro processo ou tribunal que possa ter eficácia direta nestes autos.

Confirme pedidos, fundamentos, dispositivo, efeito, resultado e favorabilidade. Alegação da parte ou conclusão pericial não é decisão judicial.

## 4. Resultados e cadeia recursal

- Resultado e `resultado_cliente` vêm do dispositivo e da posição do cliente. Procedência parcial exige identificar capítulos acolhidos e rejeitados.
- Liminar, primeira instância, segunda instância, STJ e STF são campos independentes, mas devem formar uma cadeia temporal coerente.
- Para cada apelação ou remessa necessária, registre no ledger o ato que abriu a etapa, o processo
  ou órgão destinatário e o ato material que a encerrou. Remessa seguida de retorno, trânsito ou
  cumprimento sem acórdão, decisão monocrática, admissibilidade, desistência ou extinção é
  bloqueante, ainda que todas as folhas locais estejam cobertas.
- Certidão ou ato ordinatório posterior não permite inferir o conteúdo do julgamento superior. Se
  a fonte estiver fora do corpus, exija sua ingestão/merge e mantenha a vertical recursal como
  lacuna explícita, nunca como simples `Não Julgado`.
- Decisão monocrática ou acórdão de tribunal superior que resolve recurso deste caso tem eficácia direta mesmo quando retornou aos autos dentro de um envelope de baixa. Não a rebaixe automaticamente a `Documento` por ter outro número de registro.
- Peça ou jurisprudência apenas anexada como prova permanece `Documento`. Para decidir, use origem, juntador, relação processual, retorno oficial e efeito sobre estes autos.
- `STJ/STF = Não Julgado` contradiz decisão de mérito/admissibilidade final narrada no próprio resumo ou andamento; trate como bloqueante.
- Só marque trânsito quando houver certidão/ato explícito. Decurso de prazo isolado não autoriza inferir trânsito.
- Trânsito da sentença/acórdão de mérito encerra a lide; trânsito de incidente ou AI resolve apenas aquela questão. Nomeie o ato que transitou.

## 5. Granularidade e documentos externos

- Ementa, relatório, voto e acórdão do mesmo julgamento formam um andamento; evento de juntada e inteiro teor não podem virar dois julgamentos materiais.
- Cópia integral do mesmo processo deve respeitar o frame e a granularidade definidos pelo prompt atual; não fragmente cada movimentação em uma falsa timeline viva.
- Retorno oficial de instância superior pode conter atos vivos deste caso. Classifique decisão, trânsito e comunicações pelo efeito e autoria, não pela aparência de “cópia”.
- Preserve `numero_processo_ref` do ato externo sem perder o vínculo com o processo auditado.

## 6. Análises horizontais e verticais

- Inicial e cada julgamento canônico devem ter o analyzer esperado pelo grafo/dispatch vigente; confira classificação, schema, dispositivo, resultado, cliente, julgadores e valores contra a íntegra.
- Concilie `resumo_processual`, dossiê de julgamentos, argumentos e insights com todos os atos críticos e com o estágio atual.
- Argumentos/insights não podem antecipar julgamento pendente, converter pedido em direito reconhecido ou tratar recomendação estratégica como fato.
- O dossiê não pode omitir decisão superior que o resumo narra, afirmar trânsito sem ato explícito nem indicar segunda instância não julgada quando há acórdão válido.

## 7. Casos de regressão obrigatórios

Trate como gates explícitos em toda auditoria:

- decisão do STJ retornada oficialmente foi classificada como `Terceiro / Documento` e o dossiê ficou `STJ: Não Julgado`;
- apelação/remessa retornou sem o julgamento correspondente no material indexado, mas uma certidão posterior afirma trânsito da sentença;
- relatório ou vertical confunde restituição administrativa, compensação e restituição judicial;
- resultado parcialmente favorável não explica o corte temporal, material ou quantitativo;
- laudo/perícia é tratado como deferimento definitivo do indébito.
- resumo permanece em perícia ou instrução embora haja pedido posterior de desistência, extinção ou outro ato que altere o estado atual;
- RE e REsp simultâneos, dirigidos a fundamentos distintos do mesmo acórdão, são indevidamente fundidos ou tratados como duplicidade.

## 8. Cobertura e saída

Revise metadados de todas as rows, a íntegra de todos os atos críticos, todas as rows com analyzer e todas as anomalias. `APTO` exige que o escopo incremental do job esteja coberto e que a cadeia completa já persistida usada pelas verticais também seja reconciliada.

Por processo, escreva:

1. resumo do objeto e estado atual;
2. veredito;
3. tabela `fls. | está | deve ficar | por quê`;
4. divergências das verticais;
5. patch proposto, sem aplicá-lo;
6. custo histórico e, quando identificável, delta da execução.
