# Mapa de rastreabilidade: prompt até resultado

## Caminho de uma classificação

1. `OPS.jobs` fornece CNJ, input e perfil resolvido em `output`.
2. `src/oli_indexer/profiles/registry.py` e `src/oli_indexer/profiles/areas/*.yaml` explicam a resolução e toggles legados.
3. `flows-src/grafos/<area>/<perfil>/` define operações, condições, prioridade e analyzer por andamento. OPS contém a materialização publicada.
4. `flows-src/taxonomia/<area>/<perfil>.yaml` define triplas válidas.
5. `flows-src/prompts/` é a fonte git. A resolução é perfil, depois área, depois `_default`.
6. `DATA.prompts`, chave exata `(app, area, operacao, perfil)`, é a fonte runtime; `DATA.prompts_history` guarda versões anteriores.
7. `OPS.llm_runs` registra `operacao`, `template_hash`, `grafo_id`, `no_id`, modelo, parâmetros, tokens e custo. O hash da chamada prova qual conteúdo foi usado quando a telemetria existe.
8. `DATA.indexacoes` recebe a classificação e a análise horizontal; `OPS.jobs.llm_results` recebe verticais do job; `DATA.processos`, `eventos_processo` e `cascata_estado` refletem persistência/checkpoint quando aplicável.

## Localização por tipo de operação

### Indexing e Refinement

- operações: `processo.indexacao`, `processo.refinamento`;
- contrato: `src/oli_indexer/prompts/contracts/processo/`;
- prompt git: `flows-src/prompts/<area>/...`;
- montagem do payload: `src/oli_indexer/prompts/payload_builders.py` e services das fases;
- saída: `DATA.indexacoes`.

### Analyzer por andamento

- grafo: nó `andamento.*` e `analyzer_ref`;
- compatibilidade/dispatch: `src/oli_indexer/analises/andamento/registry.py` e `src/oli_indexer/flows/dispatch.py`;
- prompt/schema do pacote: `src/oli_indexer/analises/andamento/<analyzer>/`;
- contrato publicado: `src/oli_indexer/prompts/contracts/andamento/`;
- saída: `DATA.indexacoes.analise_estruturada` e escalares relacionados.

### Análise de processo

- grafo: nós `processo.resumo`, `processo.argumentos`, `processo.dossie_*` e cascatas;
- prompts: `flows-src/prompts/` e fallbacks explicitamente sancionados no pacote;
- saída transitória: `OPS.jobs.llm_results`;
- persistência após Conclusion: campos de `DATA.processos` e, para EF, eventos/checkpoints.

### Reviewer

- nó: `agente.revisor`;
- implementação/prompt: `src/oli_indexer/pipeline/validation/reviewer/`;
- evidência: relatório/findings e chamadas `conferencia_pipeline` em `OPS.llm_runs`.

## Auditoria de hash

Para cada operação:

1. obtenha os `template_hash` distintos do job;
2. calcule SHA-256 da row atual de `DATA.prompts`;
3. resolva e calcule o arquivo git atual;
4. se não casar, pesquise `prompts_history` pelo snapshot cujo template tenha o mesmo hash;
5. conclua apenas: usado no job, publicado atualmente, resolvido no git atual ou não localizado.

Hash ausente não prova que o prompt atual foi usado. Fallback de pacote deve ser identificado no código e não inventado como row de banco.

## Diagnóstico de análise

Para uma row, registre tripla, folhas, `id_externo`, envelope, classificação, versão e campos escalares. Depois:

1. derive o analyzer esperado pelo grafo e regras de exclusão/prioridade;
2. confira se a operação aparece em `llm_runs` ligada ao andamento;
3. valide o envelope contra o schema daquela versão;
4. confronte os dados com a fonte material;
5. verifique se a vertical absorveu o evento corretamente.

Classificação errada pode nascer no Indexing, sobreviver ou ser criada no Refinement, disparar analyzer errado, ser alterada pelo reviewer ou apenas aparecer errada na persistência. Localize a primeira camada divergente antes de propor correção.
