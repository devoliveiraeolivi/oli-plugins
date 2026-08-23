# Protocolo comum de pré-aprovação

Execute este protocolo para cada job e depois aplique a checklist do perfil.

## 1. Identidade e estado

- Registre repositório, worktree, branch, commit e horário do snapshot.
- Resolva um único `OPS.jobs.id`, CNJ, área e perfil; rejeite job duplicado ou ambíguo.
- Para o fluxo normal, exija `queue=indexing`, `status=awaiting_approval`, `approved_at` vazio e ausência de executor/lease ativo.
- Registre `validation_published_at`. Valor nulo bloqueia `reviewctl save`; o relatório pode ser produzido localmente, mas o checkpoint legado só pode ser preenchido pelo fluxo cirúrgico autorizado, com manifesto e readback.
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
- Valide a tripla contra a taxonomia do perfil no commit auditado.
- Não confunda envelope eletrônico com o ator/data material da peça.
- Página com múltiplos atos exige conferir se todos sobreviveram ao Indexing e ao Refinement.
- Modele também a unidade documental: várias rows podem ser fragmentos de uma única peça, e uma
  row pode conter atos materiais independentes. Cobertura de folhas correta não prova atomicidade.
- Antes de propor merge/split, feche origem, saída, faixas, continuidade, referência processual e
  função documental. Ausência de lastro em qualquer desses eixos permanece finding bloqueante.
- Quando houver compactação documental, componha esta seção com
  `$preaprovar-compactacoes-documentais`. Ausência intencional das folhas compactadas em
  `DATA.folhas` não é lacuna se o checkpoint e o PDF de origem preservarem o lastro previsto.

### 3.1. Completude causal e transições externas

Cobertura estrutural responde se todas as folhas **recebidas** foram indexadas. Antes de `APTO`,
responda separadamente se a sequência processual está materialmente completa. Monte um ledger
das transições relevantes no formato `gatilho | consequência esperada | evidência encontrada |
lacuna` e aplique os encadeamentos definidos pela especialização.

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

O código de saída `2` indica blocker determinístico. Trate a saída como detector de lacuna: abra
as fontes indicadas e aplique a especialização; nunca rebaixe o blocker apenas porque o script não
consegue nomear o ato externo ausente.

## 4. Análises horizontais e verticais

- Para cada row, derive o analyzer esperado pelo grafo/dispatch e compare com `analise_estruturada.classificacao`, `schema_version`, dados e escalares denormalizados.
- Liste análise ausente, analyzer errado, envelope antigo, divergência, evento órfão ou campos sem evidência por `id_externo` e folhas.
- Confira operações de processo aplicáveis no grafo contra `OPS.jobs.llm_results`; ausência pode ser correta somente quando o dispatch não a ativa.
- Concilie verticais com as indexações e com a fonte. Resultado agregado nunca pode contradizer o ato material.
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

## 5. Validation, reviewer e edições humanas

- Leia relatório, warnings, findings, divergências e instruções bloqueadas.
- Reviewer obrigatório ausente, pulado ou incompleto bloqueia `APTO`.
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
estrutural integral. Achado na amostra amplia a leitura ao bloco e aos vizinhos conforme a régua
de `$preaprovar-compactacoes-documentais`.

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
- Antes de qualquer LLM, reviewer, correção ou reprocessamento, apresente escopo,
  chamadas/modelos, estimativa, teto prudencial e alternativa determinística. Aguarde autorização
  somente se o pedido corrente ainda não autorizar explicitamente a mutação proposta; não peça
  confirmação duplicada para o mesmo patch e escopo.

## 8. Parecer

Use exatamente um estado:

- `APTO`: cobertura integral comum e especializada, sem dúvida material.
- `APTO COM RESSALVAS`: somente limitação opcional sem impacto em classificação, conteúdo, rastreabilidade ou decisão.
- `REVISÃO NECESSÁRIA`: dúvida semântica localizada para usuário/reviewer, patch determinístico
  publicado aguardando autorização de aplicação ou outro achado material que exija decisão
  humana.
- `BLOQUEADO`: erro material sem patch determinístico seguro, fonte ou alvo elegível ausente,
  ambiguidade, cobertura incompleta, ou aplicação sem verificação terminal.

Não emita `BLOQUEADO` como desfecho final por um achado que já foi corrigido por patch autorizado
e verificado. Refaça os gates sobre o estado persistido e emita um relatório sucessor. Se restar
somente `revisao_secundaria_at < human_edited_at`, use `APTO` ou `APTO COM RESSALVAS` conforme a
auditoria material e exponha o timestamp apenas como gate operacional pendente. No contrato,
isso corresponde a `fit`/`fit_with_notes`, sem finding sintético de revisão secundária. O RPC de
aprovação aceita somente esses vereditos positivos quando há relatório corrente; usar
`review_required` para o próprio gate impede circularmente `Confirmar e aprovar`.

Após merge/split aplicado, o parecer continua `BLOQUEADO` até a nova topologia passar pelos gates
e as análises horizontais/verticais aplicáveis serem recompostas e revisadas.

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

## 9. Contratos e patch proposto

Gere um relatório por job no contrato `review-report/v1`. `findings` é uma lista única e
cada achado precisa trazer, nesta ordem visual, `pages`, `current`, `expected` e `reason`,
além de evidência e IDs externos quando aplicável. O `source_digest` cobre a fotografia
material auditada; obtenha-o com `reviewctl digest` e, quando houver patch, passe sempre
`--patch <patch.json>`. Não invente nem reutilize digest antigo.

Quando houver correção determinística esparsa, gere `review-patch/v1` com uma ou mais das
operações:

- `indexacao.update`: somente campos taxonômicos/metadados permitidos;
- `indexacao.analysis.replace`: troca atômica de envelope, `resultado` e
  `resultado_cliente`;
- `job.vertical.replace`: substituição CAS do vertical permitido.

Adote repair-first: se um erro puder ser corrigido por uma dessas operações, o resultado esperado
é o estado corrigido e reavaliado, não uma lista de blockers acompanhada de patches não executados.
A publicação do patch continua permitida na primeira passada; sua aplicação exige autorização
explícita no pedido corrente ou em mensagem posterior.

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
- análises, escalares, confiança, evidência, julgador e metadados de revisão das saídas limpos;
  `status_validacao=pendente`;
- `impact.horizontal=invalidate` e todas as `vertical_keys` dependentes;
- exatamente um `job.vertical.replace` que grave `null` nas chaves declaradas.

A união das folhas de saída deve ser idêntica à união das origens, contínua e sem sobreposição.
Cada saída deve apontar somente para suas origens. Não misture merge/split com operações DATA v1
no mesmo patch. Não use v2 para inserir ou retirar conteúdo sem reaproveitamento integral das
folhas; nesse caso registre finding bloqueante.

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

### 9.1. Aplicação autorizada e fechamento do ciclo

Quando a aplicação estiver explicitamente autorizada:

1. releia job, cabeça corrente do relatório/patch, `content_hash`, elegibilidade e ausência de run
   ativo;
2. aplique pelo oli-app/gateway com `expected_content_hash`, `request_id` idempotente e nota de
   aprovação que delimite o escopo; nunca escreva diretamente nas tabelas;
3. acompanhe o run até `verified`, `stale`, `failed` ou `failed_partial`; não trate `queued` ou
   `running` como sucesso e não repita cegamente uma tentativa terminal;
4. em `verified`, compare cada alvo persistido com o `set`, confira efeitos estruturais,
   análises/verticais dependentes e `human_edited_at`; o readback interno do runner não substitui
   essa conferência independente;
5. repita a régua comum e a especialização sobre o estado atual, recompute o `source_digest` sem
   reutilizar a fotografia anterior e publique relatório sucessor com CAS das cabeças esperadas;
6. se não restar dúvida material, retire o blocker antigo e publique `APTO`/`fit` (ou a ressalva
   material cabível), ainda que `revisao_secundaria_at < human_edited_at`. Não crie finding para
   esse timestamp: registre-o somente na recomendação/estado operacional, pois o oli-app confirma
   o gate imediatamente antes da aprovação final;
7. reporte separadamente correção verificada, parecer atual, gate secundário e aprovação do job.
   Nunca infira nem execute aprovação do job a partir do sucesso do patch.

Em `stale`, releia o alvo e reautorize somente se o conteúdo efetivamente mudou em relação ao
escopo aprovado. Em `failed` ou `failed_partial`, preserve tentativa, erro e snapshots como
evidência; proponha reparo específico em vez de criar nova execução indistinguível.

Para v2, confira antes da publicação que `reviewctl schema --contract patch` e o gateway em uso
aceitam `review-patch/v2`; não publique um contrato que o ambiente ainda não executa. Após a
aplicação autorizada no app, faça readback de: topologia exata, hashes das íntegras, rows de
linhagem, verticais nulas e `human_edited_at`. Em seguida produza novo relatório sobre o estado
atual. A recomposição de análises é uma etapa separada, com custo e autorização próprios.

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
