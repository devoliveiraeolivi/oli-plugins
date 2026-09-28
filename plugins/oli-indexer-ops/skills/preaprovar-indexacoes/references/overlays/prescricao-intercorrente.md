# Checklist de prescrição intercorrente

Use esta checklist depois do protocolo comum e da especialização de Execução Fiscal.

Use esta camada somente quando o grafo publicado declarar a vertical legada ou
`jobs.llm_results.prescricao_intercorrente` existir como objeto não vazio. A
mera presença de fatos de prescrição no ledger EF v5 não ativa este checker.

Antes da revisão material, execute `uv run python
<plugin>/skills/preaprovar-indexacoes/scripts/check_prescricao_intercorrente.py
--input <snapshot.json>` sobre uma fotografia local restrita do output. Código
`1` significa inconsistência para revisão, não falha do worker; código `2`
significa input inválido. Ausência de payload confirma que esta camada não é
aplicável e é devolvida como `gate_status=not_applicable`, com exit code `0`.
Não converta isso em erro do pipeline. O checker nunca escolhe automaticamente
o patch.

Revise somente o resultado já produzido; não rode novamente vertical ou reviewer. Ausência da
vertical quando ela não estava configurada não autoriza fabricar análise. Erro semântico vira
finding da pré-aprovação e não transforma o término do worker em falha.

## 1. Fotografia e cobertura

- Registre job, CNJ, perfil, data de referência, commit, prompt/hash, schema e versão da política.
- Leia a união processual visível, não apenas as rows do job atual.
- Use a cópia integral (`DATA.indexacoes.integra`/`DATA.folhas`) e eventos EF com evidência como
  fontes principais. Andamentos de site/Salesforce são fonte secundária e não criam marco material
  quando contraditos ou não confirmados pela íntegra.
- Abra integralmente cada ato que possa constituir frustração, ciência, suspensão material,
  interrupção, retomada, parcelamento/transação, extinção ou desconstituição de decisão.
- Registre cobertura ausente, processo relacionado, apenso, recurso ou expediente coletivo que
  precise ser consultado para fechar o estado.

## 2. Ledger causal

Monte uma linha por fato relevante:

```text
data_fato | data_fonte | executado/CDA | tipo | resultado/efeito | folhas/ID/hash |
evidência literal | explícito/inferido/ambíguo | impacto no relógio
```

Não combine automaticamente fatos de executados, CDAs ou processos diferentes. Identifique o
vínculo como `explicito`, `inferido_unico`, `ambiguo` ou `indeterminado`.

Inferência não equivale a ausência. Um vínculo `inferido_unico`, apoiado pela sequência dos autos e
sem alternativa factual razoável, sustenta um cenário probabilístico; reduza graduação ou confiança
e explicite a premissa. Só trate a probabilidade como nula quando nenhum cenário juridicamente
plausível sobreviver à evidência disponível.

### Possíveis marcos iniciais

Exigem ciência demonstrável da Fazenda sobre frustração, por exemplo:

- intimação ou vista após citação/localização/busca negativa;
- certidão de frustração seguida de comunicação auditável;
- petição da Fazenda reconhecendo ausência de devedor ou bens;
- comunicação de descumprimento de parcelamento e necessidade de retomada;
- decisão de retomada após suspensão, quando comunicada e seguida de inércia.

Não use isoladamente distribuição, ordem de expedir edital, carga administrativa sem frustração
identificada, anotação genérica de suspensão, arquivamento sem contexto ou simples falta de eventos.
Se nenhum marco for sustentável, mantenha a data nula e declare a insuficiência.

### Suspensões e interrupções

- Diferencie art. 40 da LEF de suspensão material da exigibilidade.
- Diferencie pedido/ordem/tentativa de resultado efetivo.
- Trate citação e constrição como candidatas somente quando o cumprimento estiver demonstrado.
- Para parcelamento/transação, confira adesão/homologação, início, vigência, acompanhamento,
  término, rescisão/descumprimento e comunicação à Fazenda.
- Liste todas as interrupções aparentes. Havendo mais de uma, apresente cenários conservador e
  pró-contribuinte, identifique a primeira interrupção válida e calcule datas próprias para cada
  cenário; não repita a mesma conclusão com rótulos diferentes.
- No cenário conservador, exponha quais atos poderiam ser tratados como novas interrupções. No
  cenário pró-contribuinte, aplique a unicidade e desconsidere as interrupções posteriores à
  primeira causa válida. A existência do cenário conservador reduz a força da tese favorável, mas
  não a elimina quando a unicidade for juridicamente sustentável.
- Não converta automaticamente múltiplas interrupções aparentes em `Indicioprescricao__c = false`.
  Se a consumação depender da unicidade, preserve o indício e calibre a classificação, em regra,
  entre `Prescrição - Remota` e `Prescrição - Possível`, conforme o lastro factual e os
  contra-argumentos. Não use `Provável` ou `Quase Certa` apenas com base nessa divergência.

## 3. Cálculo determinístico

- Use a data de referência persistida, nunca a data implícita da execução da auditoria.
- Conte o regime 1+5 uma única vez. O primeiro ano já integra o intervalo total de seis anos.
- Some apenas períodos de suspensão material cuja abertura e encerramento estejam demonstrados.
- Compare qualquer citação, constrição, acordo ou retomada com a data final calculada, inclusive em
  dias; não arredonde anos para fazer o evento parecer anterior ou posterior.
- Cada data real ou estimada deve apontar para evidências e premissas. Sem base, use `null`.

### Graduação da tese

Aplique os rótulos exatos do contrato publicado e use a seguinte régua para não transformar
incerteza em resposta binária:

- `Remota`: existe cenário jurídico sustentável, mas o marco ou elo causal é fraco/inferido, ou o
  cenário conservador apresenta contra-argumento forte;
- `Possível`: a cronologia sustenta a tese em ao menos um cenário jurídico razoável, inclusive pela
  unicidade da interrupção, embora permaneçam controvérsias materiais;
- `Provável`: evidência e maioria dos cenários relevantes convergem, com contra-argumentos mais
  fracos;
- `Quase Certa`: marcos claros, cálculo estável e cenários relevantes convergentes; não pode
  depender apenas da tese controvertida da unicidade.

Não zere uma tese porque ela não alcança `Provável`. De modo simétrico, não descreva como consumação
incontroversa uma tese apenas `Remota` ou `Possível`.

## 4. Estado corrente e decisões

- Separe sentença, publicação/intimação, embargos, anulação/cassação, recurso, trânsito, baixa e
  arquivamento. Um evento posterior não substitui a decisão intermediária ausente.
- Em sentença coletiva ou expediente concentrador, confirme que o CNJ integra a lista e se decisão
  posterior retirou seus efeitos especificamente para ele.
- Acordo antigo não prova parcelamento vigente. Exija acompanhamento ou estado atual suficiente.
- Não classifique como extinto se a extinção foi desconstituída; não classifique como em curso se
  trânsito/baixa eficazes permanecerem sem explicação.

## 5. Coerência do contrato

Confira todos os campos preservados pelo baseline e qualquer projeção interna equivalente.

- classificação `Prescrição - ...` ou `Extinto - Prescrição` exige indício verdadeiro;
- classificação `Não Prescrito - ...`, `Suspenso - ...` ou `Não Classificado - ...` exige indício
  falso;
- tag de prescrição consumada exige data final não nula, anterior à data de referência e sustentada
  pela tese adotada;
- data de início legada e marco inicial não podem divergir sem explicação do contrato;
- confiança deve refletir estimativas, lacunas, contra-argumentos e divergência entre cenários;
- fato demonstrado, como ciência por intimação, vista ou carga após frustração, não pode ser apagado
  por divergência sobre seus efeitos posteriores; essa divergência calibra a tese e a confiança;
- tags de processo principal/apensado exigem relação processual demonstrada;
- relatório, badges e projeção não podem afirmar conclusão mais forte que os campos ou a fonte;
- citações legais e temas jurisprudenciais usados como fundamento devem ser conferidos em fonte
  oficial; citação incorreta é finding próprio.

Revise também justificativa, eventos processuais, linha do tempo, observações, todos os marcos
alternativos, hiatos, suspensões, interrupções e a análise dual. Não aprove apenas o JSON escalar.

## 6. Suficiência e parecer

Classifique a fonte como `suficiente`, `parcial` ou `insuficiente` para cada conclusão relevante.

- Fonte insuficiente não autoriza afirmar consumação, ausência de interrupção ou vigência de acordo.
- Heurística por idade pode permanecer como hipótese de triagem somente se o contrato permitir e o
  relatório a separar claramente dos fatos; ela nunca substitui os autos.
- Erro objetivo no baseline autoriza rejeitar aquele output mesmo quando ainda não seja possível
  fechar a saída substituta.
- Decisão jurídica humana deve ser registrada no parecer antes de converter cenário controvertido
  em patch.

Saída mínima adicional ao protocolo comum:

```text
PRESCRIÇÃO INTERCORRENTE: gatilho e versão da análise
Fonte: cobertura da íntegra e documentos externos
Ledger: marcos, suspensões, interrupções e hiatos por cadeia
Cenário conservador:
Cenário pró-contribuinte:
Campos: classificação; indício; confiança; datas; tags; dual; relatório
Suficiência: suficiente | parcial | insuficiente
Inconsistências determinísticas:
Questões para parecer humano:
Patch: ausente | proposto | publicado | aplicado/verificado
Impacto: parecer da pré-aprovação; gate humano; worker preservado
```

## 7. Patch seguro

Antes de propor `job.vertical.replace`:

1. confirme que o job está elegível e sem executor ativo;
2. confirme no código/schema runtime que `prescricao_intercorrente` é alvo aceito;
3. leia o envelope completo corrente de `jobs.llm_results` e confirme que a subárvore de prescrição
   já existe como objeto não vazio e contém os 13 campos do baseline legado congelado; nulo,
   ausente, vazio, malformado ou projeção interna sem schema fechado não admite bootstrap nesta fatia;
4. preserve todas as chaves fora de `prescricao_intercorrente` em `expect` e `set`;
5. preserve recursivamente o conjunto completo de chaves dentro da subárvore e limite a mudança
   aos valores cobertos pelo parecer; resumo, julgamentos e outras verticais permanecem byte a byte
   equivalentes no envelope;
6. valide e calcule o digest patch-aware;
7. publique a saída determinística e unívoca no plano final e entregue **Aplicar patch**; decisão
   jurídica ainda ambígua permanece **Decisão jurídica necessária**;
8. depois de `verified`, confira o readback. Com `completion.report`, não repita a checklist nem
   publique sucessor: o parecer favorável já foi ativado para o estado exato.

O patch desta camada contém exatamente uma operação `job.vertical.replace`; não combine mudança
colateral em resumo, julgamentos ou outra vertical. Se a chave estiver ausente, nula, vazia ou
malformada, a saída existir apenas no fluxo legado, a projeção futura não tiver schema fechado ou o
contrato runtime não aceitar o alvo, registre `contrato_patch_ausente`. Não faça bootstrap nem
escreva em `processo_json`, Salesforce ou projeções finais por conveniência.

`stale`, `failed` ou `failed_partial` não autorizam retry cego. Releia o envelope e crie nova
fotografia/revisão quando o estado tiver mudado.
