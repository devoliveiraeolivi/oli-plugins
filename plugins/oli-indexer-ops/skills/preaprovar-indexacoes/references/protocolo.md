# Protocolo comum de pré-aprovação

Execute este protocolo para cada job e depois aplique a checklist do perfil.

## 1. Identidade e estado

- Registre repositório, worktree, branch, commit e horário do snapshot.
- Resolva um único `OPS.jobs.id`, CNJ, área e perfil; rejeite job duplicado ou ambíguo.
- Para o fluxo normal, exija `queue=indexing`, `status=awaiting_approval`, `approved_at` vazio e ausência de executor/lease ativo.
- Registre `validation_published_at`. Valor nulo bloqueia `reviewctl save`; o relatório pode ser
  produzido localmente, mas o checkpoint legado só pode ser preenchido por backfill versionado,
  com autorização específica para a lista exata de jobs, manifesto prévio, CAS e readback.
- Registre gap, recalls/deletes, `skip_reviewer`, edições humanas e gate secundário.

## 2. Fontes e configuração

Use esta prioridade para resolver divergências:

1. fonte material em `DATA.indexacoes.integra` ou `DATA.folhas`;
2. configuração runtime rastreada: prompt/hash, grafo/nó, taxonomia, contrato e schema;
3. rows do job vigente em `DATA.indexacoes`;
4. análises horizontais, `OPS.jobs.llm_results` e relatório da Validation;
5. `DATA.processos` e históricos apenas como comparação.

Não presuma que o arquivo local foi o prompt usado. Compare `OPS.llm_runs.template_hash`, a row exata de `DATA.prompts` e o arquivo resolvido em `flows-src/` com `$inspecionar-configuracao-indexacao`.

## 3. Cobertura estrutural

Em todas as indexações, confira identidade, intervalo, data, tripla taxonômica, título, resumo, função/nome responsável, referência processual, resultado, resultado do cliente e status de validação.

- Meça páginas do escopo, lacunas, sobreposições incompatíveis, duplicidade material e rows órfãs.
- Faça essa medição também no universo processual visível, não apenas nas rows do job corrente.
  Execute `check_process_structure.py` e concilie suas contagens com a tela: a Validation pode
  declarar zero overlaps dentro do `ctx` e, ainda assim, o oli-app exibir staging pendente de um
  job anterior. Registre por `job_id` e `status_validacao` todas as owners encontradas.
- Valide a tripla contra a taxonomia do perfil no commit auditado.
- Não confunda envelope eletrônico com o ator/data material da peça.
- Página com múltiplos atos exige conferir se todos sobreviveram ao Indexing e ao Refinement.
- Modele também a unidade documental: várias rows podem ser fragmentos de uma única peça, e uma
  row pode conter atos materiais independentes. Cobertura de folhas correta não prova atomicidade.
- Separe quatro níveis antes de decidir a topologia: processo referido, ato eletrônico de juntada,
  `carimbo_subato`/arquivo anexado e conteúdo interno. O mesmo CNJ ou `carimbo_ato` não autoriza
  merge de arquivos distintos; uma referência interna, como relatório do TCU, não cria por si só
  outro processo juntado.
- Quando cabeçalhos, `carimbo_subato` ou nomes de arquivo identificarem anexos `parte_N` distintos,
  preserve uma saída por arquivo e a ordem física das folhas, mesmo que a numeração venha fora de
  ordem (`parte_002` antes de `parte_001`). Só una fragmentos dentro do mesmo arquivo/subato quando
  a fonte demonstrar que a separação é artificial.
- Antes de propor merge/split, feche origem, saída, faixas, continuidade, referência processual e
  função documental. Ausência de lastro em qualquer desses eixos permanece finding bloqueante.
- Quando houver compactação documental, componha esta seção com a
  [camada de compactação](overlays/compactacao-documental.md). Ausência intencional das folhas compactadas em
  `DATA.folhas` não é lacuna se o checkpoint e o PDF de origem preservarem o lastro previsto.

### 3.1. Colisão entre jobs e staging órfão

Rows `pendente` ou `aprovado` de outro job continuam materialmente visíveis mesmo quando o job
proprietário é legado, terminal ou não aparece na fila do oli-app. Elas não podem ser ignoradas
como histórico nem camufladas por filtro de UI. Trate como finding estrutural e confronte:

- proprietário real, estado do job, aprovação, lease/heartbeat e data da execução;
- CNJ, status, contagem, intervalos, IDs e hash canônico do conjunto;
- versão/modelo e hashes de prompt efetivamente usados nos jobs concorrentes;
- cobertura, gaps, overlaps e duplicidades exatas depois de selecionar a fonte que permanecerá.

Se dois jobs concorrem pelas mesmas folhas e o job mais novo está elegível, prefira-o somente
quando a trilha comprovar execução/configuração posterior ou correções materiais já verificadas.
A limpeza do staging antigo é operação destrutiva separada: exige autorização explícita para o
`job_id` exato, manifesto prévio, filtro `job_id + status_validacao`, ausência de worker vivo e
readback com zero rows antigas. Nunca promova, apague ou recategorize rows para apenas fazer o
detector passar. Depois da limpeza, repita a auditoria estrutural, causal e especializada e
publique relatório sucessor; a limpeza não aprova o job.

### 3.2. Completude causal e transições externas

Cobertura estrutural responde se todas as folhas **recebidas** foram indexadas. Antes de `APTO`,
responda separadamente se a sequência processual está materialmente completa. Monte um ledger
das transições relevantes no formato `gatilho | consequência esperada | evidência encontrada |
lacuna` e aplique os encadeamentos definidos pela especialização.

- A âncora inaugural também integra a sequência lógica. Em processo judicial, o universo
  processual visível deve conter exatamente uma `Petição Inicial` nativa. Duas ou mais rows com
  essa subclasse constituem quebra causal bloqueante, ainda que não tenham folhas sobrepostas nem
  sejam duplicatas textuais. Abra todas as candidatas e reconcilie processo de origem,
  `numero_processo_ref`, o invólucro da juntada e, somente quando o recurso
  estava habilitado na execução auditada, `DATA.folhas.mapeamento_origem`,
  `mapeamento_ref` e `mapeamento_relacao`. Com
  `PIPELINE_ENABLE_MAPEAMENTO=false`, não produza mapeamento manual, não cobre
  preenchimento desses campos e não use sua ausência como finding.
- Um ato que remete autos, recurso ou incidente para outro órgão abre uma ramificação externa. Se
  ele for o último estágio material disponível, sem retorno, trânsito, baixa, cumprimento ou outra
  consequência posterior, registre a ramificação como terminal pendente; o processo simplesmente
  ainda não chegou ao desfecho e isso não impede `APTO`.
- A ramificação vira quebra causal quando aparece depois retorno, trânsito, baixa, cumprimento ou
  outra consequência que pressuponha seu encerramento, mas falta o julgamento, admissibilidade,
  desistência, extinção ou ato equivalente que explique juridicamente essa passagem. A mera
  devolução física não supre o desfecho.
- Trânsito, cumprimento ou baixa posteriores exigem o título ou desfecho anterior que lhes dá
  suporte. O ato posterior prova que houve uma consequência, mas não substitui a fonte material
  ausente que decidiu a etapa intermediária.
- `100%` de cobertura, ausência de gaps e correspondência `1:1` não neutralizam uma quebra
  intermediária. Se o ato posterior torna necessária uma fonte que está em outro processo,
  instância ou repositório, registre `fonte externa ausente` e mantenha `BLOQUEADO` até sua
  incorporação ou vínculo auditável. Não exija como ausente um julgamento que ainda não ocorreu.
- Não corrija uma lacuna de corpus por patch sem fonte nem use `Não Julgado` para ocultá-la. O
  parecer deve dizer qual ato posterior demonstrou a quebra, qual etapa intermediária falta e qual
  merge, ingestão ou consulta é necessária. Se uma vertical afirmar remessa, julgamento ou estado
  não demonstrado pelas fontes, trate a afirmação sem lastro como erro próprio; não a use para
  converter uma pendência terminal em história processual inventada.

O ledger deve ser revisado mesmo quando o relatório da Validation declara cobertura integral.
`status=open` no último ato não é blocker por si só; `gap` entre atos existentes é. Cada
especialização define quais gatilhos e consequências têm força bloqueante.

Execute o detector comum antes do parecer:

```bash
uv run python <plugin>/skills/preaprovar-indexacoes/scripts/check_logical_chain.py \
  --repo <repo> --job-id <uuid>
```

O código de saída `2` indica blocker determinístico. Trate a saída como detector de lacuna ou de
quebra da âncora inaugural: abra as fontes indicadas e aplique a especialização; nunca rebaixe o
blocker apenas porque o script não consegue nomear o ato externo ausente.

## 4. Análises horizontais e verticais

- Para cada row, derive o analyzer esperado pelo grafo/dispatch e compare com `analise_estruturada.classificacao`, `schema_version`, dados e escalares denormalizados.
- Liste análise ausente, analyzer errado, envelope antigo, divergência, evento órfão ou campos sem evidência por `id_externo` e folhas.
- Confira operações de processo aplicáveis no grafo contra `OPS.jobs.llm_results`; ausência pode ser correta somente quando o dispatch não a ativa.
- Concilie verticais com as indexações e com a fonte. Resultado agregado nunca pode contradizer o ato material.
- Em EF v5, processo relacionado sem corpus indexado é warning não bloqueante
  quando o snapshot registra `dependent_verticals={}`. Só bloqueie quando uma
  operação publicada depende materialmente desse corpus, houver candidata ou
  conflito relacional pendente de decisão humana, ou a relação contradisser a
  fonte.
- Confira `DATA.processos` e checkpoints apenas para detectar drift de persistência; eles não substituem o resultado do job em aprovação.
- Mudança de topologia invalida toda análise horizontal das rows produzidas e toda vertical que as
  absorveu. Nunca copie envelope, resultado, evento, resumo ou cascata da topologia anterior.

### 4.1. Anulação de sentença e estado corrente das instâncias judiciais

Na vertical judicial `julgamentos`, os campos por instância representam o estado corrente do
julgamento de mérito, não todo pronunciamento historicamente favorável ou desfavorável. Quando a
2ª instância anular ou cassar a sentença e determinar o retorno à origem:

- enquanto a anulação ainda estiver sujeita a Embargos de Declaração, Agravo Interno ou outro
  recurso capaz de revertê-la, não antecipe a reabertura: preserve os resultados correntes que a
  fonte ainda sustenta;
- depois de encerrada essa cadeia recursal, com trânsito/preclusão do pronunciamento anulatório e
  retorno ou determinação definitiva de retorno à 1ª instância, marque **tanto 1ª quanto 2ª
  instância como `Não Julgado`**, salvo se já houver nova sentença de mérito posterior ao retorno;
- não marque a 2ª instância como `Favorável` apenas porque a anulação beneficiou o autor: a decisão
  anulou o julgamento anterior, mas não substituiu a sentença por um julgamento de mérito;
- preserve no resumo, argumentos, julgadores e linha do tempo a sentença anulada, os recursos e o
  acórdão anulatório. O reset alcança somente os indicadores correntes por instância;
- trânsito do acórdão anulatório não é trânsito do processo: se a causa voltou para instrução ou
  novo julgamento, `transito_julgado` continua `Sem Trânsito em Julgado`.

Confirme a sequência material completa — sentença, anulação/cassação, recursos contra a anulação,
trânsito/preclusão e retorno à origem — antes de aplicar o reset. Ausência dessa estabilização não
autoriza usar `Não Julgado` para ocultar recurso ainda pendente ou lacuna de corpus.

## 5. Validation, reviewer opcional e edições humanas

- Execute `list_deterministic_findings.py` e leia a lista integral, nao apenas a previa truncada
  do HTML. Reconcilie os dois produtores: `jobs.output.achados_deterministicos` e
  `DATA.achados_indexacao`. Registre completude, totais por fonte/severidade/codigo e o destino de
  cada item (`confirmado`, `falso positivo justificado`, `patchavel`, `nao_patchavel`).
- Leia relatório, warnings, findings, divergências e instruções bloqueadas. A ausencia visual de
  secao no HTML nao prova zero warnings quando o snapshot estruturado estiver ausente ou legado.
- Warning deterministico nao trava automaticamente o pipeline, mas e gate de leitura da
  pre-aprovacao: nenhum parecer omite item atual ou o rebaixa apenas porque
  `bloqueia_conclusao=false`.
- Reviewer externo é opcional. Ausência, `skip_reviewer` ou execução incompleta não bloqueiam
  `APTO` por si sós quando a auditoria local desta skill fechou identidade, cobertura, findings e
  régua jurídica. Se houver saída de reviewer, trate-a como evidência adicional: leia-a por inteiro
  e resolva ou apresente qualquer finding material antes do parecer.
- Finding crítico precisa estar resolvido ou apresentado ao usuário.
- Após edição humana, confira e registre `revisao_secundaria_at >= human_edited_at`; a auditoria
  não carimba o gate. Timestamp pendente, isoladamente, não é finding material nem altera o
  veredito do relatório: o oli-app deve confirmá-lo no fluxo humano de aprovação.
- Relatório que mande consultar/corrigir Google Sheets é resíduo defeituoso.
- Achado determinístico representável pelo contrato deve seguir o ciclo repair-first da seção 9;
  não o deixe como recomendação manual nem como bloqueio terminal quando já houver autorização
  para aplicar o patch.

## 6. Cobertura semântica

Revise metadados de todas as rows. Abra a fonte integral de todos os atos críticos definidos pela especialização, de toda row analisada por LLM e de toda anomalia. Para o restante, revise por blocos documentais e amplie ao bloco inteiro diante de qualquer inconsistência.

Em grupos fiscais compactados, a cobertura integral pode ser demonstrada pelo plano
determinístico folha a folha, pela reconciliação de todos os blocos/grupos e pelo PDF de origem;
a amostra visual obrigatória valida a saúde do classificador, mas nunca substitui essa cobertura
estrutural integral. Achado na amostra amplia a leitura ao bloco e aos vizinhos conforme a
[camada de compactação](overlays/compactacao-documental.md).

Registre separadamente:

- `linhas_estruturais`: total/revisadas;
- `linhas_metadados`: total/revisadas;
- `linhas_fonte`: elegíveis/revisadas/inacessíveis;
- `atos_criticos`: total/revisados integralmente;
- `analises_horizontais`: aplicáveis/revisadas;
- `verticais`: aplicáveis/revisadas.

## 7. Custo e autoridade

- A leitura de resultados existentes não autoriza nova chamada.
- Meça `OPS.llm_runs` pela janela da execução; total histórico deve ser rotulado como histórico.
- O pedido de pré-aprovação autoriza autoria e publicação dos patches determinísticos elegíveis
  gerados nesta auditoria para os jobs do snapshot inicial. A aplicação oficial continua sendo o
  clique humano **Aplicar patch**; depois dele, CAS, readback e ativação do parecer não exigem
  confirmação intermediária.
- Antes de qualquer LLM, reviewer, recall/delete, reprocessamento, backfill legado, mudança de
  código/prompt ou correção fora de `review-patch`, apresente escopo, chamadas/modelos, estimativa,
  teto prudencial e alternativa determinística e aguarde autorização própria.

## 8. Parecer

Classifique internamente o parecer, mas entregue um dos quatro resultados operacionais:

- `APTO`: cobertura integral comum e especializada, sem dúvida material.
- `APTO COM RESSALVAS`: somente limitação opcional sem impacto em classificação, conteúdo, rastreabilidade ou decisão.
- `REVISÃO NECESSÁRIA`: dúvida semântica localizada para usuário/reviewer ou outro achado material
  que exija decisão humana e não admita correção determinística unívoca.
- `BLOQUEADO`: erro material sem patch determinístico seguro, fonte ou alvo elegível ausente,
  cobertura incompleta, ou aplicação sem verificação terminal. Ambiguidade jurídica real é
  `REVISÃO NECESSÁRIA`, não bloqueio técnico.

Não emita `BLOQUEADO` como desfecho final por um achado determinístico corrigível. Termine o plano,
inclua o parecer favorável antecipado e entregue **Aplicar patch**. Se um patch legado sem
`completion.report` já tiver sido verificado, refaça os gates e emita relatório sucessor. Se restar
somente `revisao_secundaria_at < human_edited_at`, use `APTO` ou `APTO COM RESSALVAS` conforme a
auditoria material e exponha o timestamp apenas como gate operacional pendente. No contrato,
isso corresponde a `fit`/`fit_with_notes`, sem finding sintético de revisão secundária. O RPC de
aprovação aceita somente esses vereditos positivos quando há relatório corrente; usar
`review_required` para o próprio gate impede circularmente `Confirmar e aprovar`.

Não publique `BLOQUEADO` como entrega para erro determinístico corrigível. Faça a auditoria
exaustiva, materialize as correções e dependências e entregue **Aplicar patch**. Sem patch, ou após
ativação exata do parecer antecipado, entregue **Aprovar**. Durante o run use **Aguardando
processamento**; ambiguidade jurídica real usa **Decisão jurídica necessária**.

Saída mínima:

```text
PARECER: APTO | APTO COM RESSALVAS | REVISÃO NECESSÁRIA | BLOQUEADO
CNJ / job / perfil / commit:
Cobertura: estrutural; metadados; fonte; críticos; horizontais; verticais
Configuração rastreada: prompt(s), hash(es), grafo e taxonomia
Erros bloqueantes:
Dúvidas para humano/reviewer:
Ressalvas:
LLM e custo:
Ação recomendada:
```

### 8.1. Qualidade editorial dos campos humanos

O contrato e o control plane aceitam JSON UTF-8. Nunca remova acentos ou outros diacríticos para
facilitar a serialização. Revise todos os campos humanos das indexações, análises horizontais,
verticais e relatório — em especial títulos, resumos, resultados, narrativas de
`analise_estruturada`, `julgamento_argumentos`, `resumo_processual`, `process_summary`,
`recommendation` e `current`, `expected`, `reason` e `evidence` de cada finding — e exija
ortografia, acentuação, concordância, pontuação e terminologia jurídica corretas em português do
Brasil. Preserve literalmente identificadores, códigos e hashes; antes de alterar algo que pareça
enum ou valor técnico, confirme schema, prompt e consumidores.

Texto editorialmente degradado não está pronto para publicação, ainda que o conteúdo jurídico e
o contrato estejam corretos. Corrija localmente os campos do relatório antes de `reviewctl save`,
sem chamada LLM. Se o defeito já estiver no dado canônico, registre o finding e aplique repair-first
somente quando a correção textual for unívoca e couber no contrato tipado — por exemplo,
`indexacao.analysis.replace` com o envelope completo e as dependências exigidas. Nunca edite DATA
diretamente nem altere conteúdo jurídico por inferência.

Se o usuário apontar depois da publicação um defeito apenas do relatório, gere sucessor imutável
com CAS sobre a cabeça corrente, preservando fotografia, veredito e conteúdo material. Essa
revisão do relatório não cria patch de DATA, não chama LLM, não reprocessa e não aprova o job.

## 9. Contratos e ciclo repair-first

Gere um relatório por job no contrato `review-report/v1`. `findings` é uma lista única e
cada achado precisa trazer, nesta ordem visual, `pages`, `current`, `expected` e `reason`,
além de evidência e IDs externos quando aplicável. O `source_digest` cobre a fotografia
material auditada; obtenha-o com `reviewctl digest` e, quando houver patch, passe sempre
`--patch <patch.json>`. Não invente nem reutilize digest antigo.

Use UUIDs reais nos contratos e um `patch_key` curto e estável para a série. Antes de qualquer
`reviewctl save`, anuncie que a próxima etapa gravará artefatos imutáveis no control plane; essa
gravação não altera por si só indexações, análises, status, aprovação nem gate secundário.

Quando houver correção determinística esparsa, gere `review-patch/v1` com uma ou mais das
operações:

- `indexacao.update`: somente campos taxonômicos/metadados permitidos;
- `indexacao.analysis.replace`: troca atômica de envelope, `resultado` e
  `resultado_cliente`;
- `job.vertical.replace`: substituição CAS do vertical permitido.

Adote repair-first: se um erro puder ser corrigido por uma dessas operações, o resultado esperado
é o estado corrigido e reavaliado, não uma lista de blockers acompanhada de patches incompletos.
Após fechar a passada inicial somente leitura, publique um patch exaustivo com o estado final e o
parecer favorável antecipado quando representável. Entregue **Aplicar patch** e aguarde o clique;
não enfileire por iniciativa própria. O runner executa CAS, readback e ativação do parecer sem nova
análise.

Para toda operação `indexacao.*`, copie do banco a identidade completa da row:
`target.job_id = DATA.indexacoes.job_id` e `target.id_externo = DATA.indexacoes.id_externo`.
Não substitua o proprietário pelo `job_id` do relatório. O alvo normalmente é do job atual e
deve estar `pendente`/`aprovado`; se o erro estiver num incremento anterior do mesmo CNJ, v1
aceita somente a row anterior `concluido`, enquanto o job atual segue elegível em
`awaiting_approval`. Ausência, duplicidade, CNJ diferente ou qualquer outro status é finding
sem patch executável. Isso não autoriza corrigir processo fechado nem projeções finais.

Mudança de categoria/classe/subclasse informa a tripla completa antes/depois. Se ela mudar o
analyzer do perfil, inclua `indexacao.analysis.replace` compatível no mesmo changeset.

Quando a fonte demonstrar erro de unidade documental, gere `review-patch/v2` com:

- `indexacao.merge`: duas ou mais origens e exatamente uma saída;
- `indexacao.split`: uma origem e duas ou mais saídas com identidades UUID novas;
- `expect.rows`: fotografia completa das origens, inclusive hash da íntegra;
- `set.rows`: saídas com `source_ids`, faixa exata, taxonomia, metadados,
  `content_mode` e `integra_sha256` esperado;
- `content_mode=rebuild_from_folhas` para conteúdo material local ou `pointer` para maço externo
  cujo conteúdo vive no processo referido;
- análises, escalares, confiança, evidência, julgador e metadados de revisão das saídas inicialmente
  limpos; `status_validacao=pendente`;
- `impact.horizontal=invalidate` e todas as `vertical_keys` dependentes;
- exatamente um `job.vertical.replace`. Sem conclusão antecipada ele grava `null`; com
  `completion.report`, grava todas as verticais declaradas já recalculadas e inclui exatamente as
  `indexacao.analysis.replace` exigidas pelos analyzers dos outputs.

A união das folhas de saída deve ser idêntica à união das origens, contínua e sem sobreposição.
Cada saída deve apontar somente para suas origens. Nesta fundação não misture merge/split com
`indexacao.update`; reflita a correção nos outputs ou resolva-a antes da proposta estrutural.
`indexacao.analysis.replace` só entra como materialização pós-estrutural de um output. Não use v2
para inserir ou retirar conteúdo sem reaproveitamento integral das folhas; se o contrato não
representar a correção, registre `BLOQUEIO_TECNICO`.

Para montar `expect.rows` sem despejar OCR ou recalcular hashes manualmente, gere antes uma
fotografia local restrita:

```bash
uv run reviewctl snapshot --report <report.json> --output <review-source-v2.json>
```

O arquivo contém fonte material e fica com permissão `0600`; mantenha-o no diretório local de
artefatos, não o publique no control plane nem o inclua em commit. Use suas rows e folhas para
construir as saídas. Calcule cada hash de saída localmente com o mesmo algoritmo da RPC:

```bash
uv run reviewctl integral-hash --snapshot <review-source-v2.json> \
  --from-page <inicio> --to-page <fim>
```

Não copie o texto integral para o patch; grave somente o hash retornado.

Antes de publicar:

```bash
uv run reviewctl validate --report <report.json> [--patch <patch.json>]
uv run reviewctl digest --report <report.json> [--patch <patch.json>]
uv run reviewctl save --report <report.json> [--patch <patch.json>] \
  [--expected-current-report-id <uuid>] \
  [--expected-current-patch-hash <sha256>]
```

Os colchetes acima indicam ausência total de patch. Se `patch.json` existir, passe-o tanto ao
`validate` quanto ao `digest` e ao `save`.

O `save` grava apenas o control plane. Nunca grave as tabelas diretamente e nunca inclua SQL
executável no JSON. Após a publicação, faça readback pelo gateway e reporte:
`report_id`, `content_hash`, `patch_key`, `patch_revision_id`, `version` e `computed_risk`.

### 9.1. Aplicação humana e fechamento automático do ciclo

Depois de publicar um patch determinístico elegível durante a pré-aprovação:

1. releia job, cabeça corrente do relatório/patch, `content_hash`, elegibilidade e ausência de run
   ativo;
2. entregue **Aplicar patch** e aguarde o clique humano; não chame `approve_and_queue_*` por conta
   própria. O gateway envia `expected_content_hash` e `request_id` idempotente;
3. acompanhe o run até `verified`, `stale`, `failed` ou `failed_partial`; não trate `queued` ou
   `running` como sucesso e não repita cegamente uma tentativa terminal;
4. em `verified`, compare cada alvo persistido com o `set`, confira efeitos estruturais,
   análises/verticais dependentes e `human_edited_at`; o readback interno do runner não substitui
   essa conferência independente;
5. quando houver `completion.report`, o runner recomputa a fonte e ativa o parecer favorável na
   mesma transação terminal somente se os digests esperado e real coincidirem. Não faça nova LLM,
   revisão ou relatório sucessor;
6. entregue **Aprovar** na mesma tela. Não crie finding para
   `revisao_secundaria_at`: o oli-app confirma o gate na aprovação final;
7. reporte separadamente correção verificada, parecer atual, gate secundário e aprovação do job.
   Nunca infira nem execute aprovação do job a partir do sucesso do patch.

Em `stale`, releia o alvo e compare separadamente o valor bruto, a forma
normalizada usada no snapshot e o `set` desejado. Se não houve mutação e a
diferença for apenas normalização textual, não crie fotografia ou revisão
sucessora: o patch continua materialmente corrente. Confirme que o patch worker
contém a correção do PR #156 e então use o retry oficial do mesmo patch uma vez,
com nova chave idempotente e readback. Se o worker ainda não estiver atualizado,
pare e peça ao usuário o deploy de `oli-indexer-patch`.

Crie nova fotografia/revisão somente quando o estado material, o alvo ou a
correção tiver mudado. Não tente contornar um `REVIEW_FENCE_STALE_GENERATION`
criando sucessores em série; preserve o run e trate o fence antes. Pare se
surgir escopo novo ou o conflito CAS recorrer. Em `failed` ou `failed_partial`,
preserve tentativa, erro e snapshots como evidência; proponha reparo específico
em vez de criar nova execução indistinguível.

Para v2, confira antes da publicação que contrato, gateway e runner aceitam conclusão estrutural;
não publique um contrato que o ambiente ainda não executa. Antes de anunciar **Aplicar patch**,
as recomposições horizontal/vertical necessárias já devem ter ocorrido e seus resultados devem
constar do plano. Após o clique, faça readback de topologia, hashes, linhagem, análises, verticais,
estado esperado e `human_edited_at`. Resultado pago fora das chaves afetadas deve permanecer
idêntico.

## 10. Revisão solicitada pelo usuário

Uma correção conversacional cria sucessora imutável da mesma série:

```bash
uv run reviewctl revision --parent-revision-id <uuid> --patch <patch-vN+1.json> \
  --expected-parent-hash <sha256>
```

Preserve o `report_id`, incremente exatamente uma versão, explique `revision_reason` e valide
novamente. Run ativo bloqueia sucessão. Versão anterior continua disponível para auditoria.
Se a versão nova acrescentar/trocar um alvo que não compunha o snapshot anterior, gere novo
relatório com digest patch-aware e use `reviewctl save`; não prenda o alvo novo a um digest que
nunca o auditou. Não aplique o patch durante a revisão.
