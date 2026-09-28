# Impacto das propostas

## OLI-SKILL-001 — consolidar especializações com compatibilidade explícita

- **Status:** aceita
- **Data:** 2026-09-01
- **Alvo:** `preaprovar-indexacoes` e nove wrappers especializados
- **Hipótese:** reduzir competição de discovery e duplicação sem perder as réguas jurídicas
- **Mudança:** o conteúdo dos wrappers virou referência canônica de perfil/overlay; seis skills
  ficam no discovery automático e nove aliases sem regras próprias preservam invocações explícitas
- **Validação exigida:** estrutura, links, testes dos scripts, corpus de discovery, revisão da
  preservação de conteúdo e reinstalação em cache separado
- **Rollback:** branch `main` no commit baseline; a fonte anterior também permanece no cache
  instalado até a reinstalação
- **Primeira revisão:** rejeitada por quatro perdas semânticas: fallback de natureza judicial não
  coberta, checker de prescrição não roteado, reparo em massa de falha sistêmica de compactação e
  ausência dos limites de OCR/Vision/materialização.
- **Correção sucessora:** repôs os quatro freios, restaurou regras adicionais de identidade,
  aprovação, backfill e reparo nas fontes canônicas e criou aliases explicit-only sem checklists
  paralelos.
- **Teste de encaminhamento:** 14/14 pedidos automáticos e 9/9 aliases chegaram ao destino
  correto; o único finding, composição ausente dos gates técnicos no fluxo completo, foi corrigido
  e reverificado.
- **Resultado local:** 15 → 6 skills automáticas, com 9 aliases explícitos; 6.798 → 1.481
  caracteres no catálogo automático; 32 casos de discovery; 17 testes passando; validadores de
  fonte, skills e plugin passando; revisão independente final sem bloqueio semântico.
- **Pendente:** smoke de discovery em nova sessão após reinstalação e, quando houver harness
  controlado, comparação real baseline/candidata com modelo.

## OLI-SKILL-002 — promover o gate pós-extração com versionamento fail-closed

- **Status:** aceita na fonte; escrita condicionada ao runtime
- **Data:** 2026-09-01
- **Alvo:** `preaprovar-extracoes`
- **Origem:** PR `oli-indexer#1224`, head `e5dbe6de0c7981b40546541e064619a274a890f3`,
  migrations DATA `0141_extraction_treatment_budget_data` e OPS
  `0142_extraction_gate_fencing_ops`
- **Hipótese:** preservar a régua técnica completa sem aumentar o catálogo automático, carregando
  detalhes somente após a skill ser selecionada e impedindo escrita contra runtime antigo
- **Mudança:** incorporadas quatro classes de problema, allowlist literal, série/head/ledger,
  orçamento de uma mutação com único retry pré-mutação, release/start atômico, escolha explícita de
  canário e gate de capacidade que bloqueia qualquer fallback v1
- **Validação exigida:** contrato documental, nove casos comportamentais, validadores da fonte e do
  plugin, cache fonte=instalado e smoke posterior em nova sessão
- **Evidência de segurança:** scan `d4eccd1f-4f01-4998-9541-bdfe13ec4cfd` encontrou o claim sem ACL
  explícita no head anterior; o sucessor restringiu-o a `service_role`, cercou lease/head e adicionou
  smoke de ACL antes da promoção
- **Rollback:** reinstalar a versão anterior da fonte; o gate de capacidade mantém a candidata em
  somente leitura enquanto 0141/0142, worker, smokes e deploy não forem comprovados
- **Resultado local:** conteúdo promovido sem nova skill automática ou alias; 6 skills automáticas
  + 9 aliases explícitos, catálogo automático de 1.565 caracteres, 32 casos de discovery, 9 casos
  comportamentais do gate, 17 testes e validadores das 15 skills/fonte/plugin passando; ativação de
  escrita continua pendente de merge, migrations, deploy, smoke/readback e canário selecionado

## OLI-SKILL-003 — orquestração integral e Conclusion explícita

- **Status:** candidata local; sem autorização de deploy, migration ou job real
- **Data:** 2026-09-01
- **Alvo:** `orquestrar-indexacoes`, `concluir-indexacoes-aprovadas` e alias
  `rodar-e-preaprovar-indexacao`
- **Hipótese:** manter uma única entrada automática para o fluxo integral e isolar Conclusion em
  uma skill explicit-only reduz ambiguidade de autoridade e permite fechamento auditável depois
  da aprovação humana
- **Mudança:** o fluxo diário foi promovido para a skill canônica com intenção v1, gates técnicos,
  budgets e escritor serial; o nome anterior virou alias explícito; a Conclusion ganhou contrato
  próprio com approved-only, dry-run, readback e proibição de retry cego
- **Validação exigida:** validadores das skills/plugin, discovery automático e explícito, quinze
  casos comportamentais de Conclusion, igualdade fonte/cache e smoke em sessão nova
- **Runtime relacionado:** `run_batch.py` precisa publicar o contrato estruturado, propagar
  `orchestration_run_id` e suportar o opt-in de Extraction; o workflow de deploy precisa ler de
  volta os dois modos de gate
- **Bloqueio inicialmente observado:** o control plane OPS em shadow ainda não existia e o runner
  não reservava budgets antes das chamadas nem fazia CAS do snapshot aprovado no claim. Uma linha
  de trabalho separada passou a conter 0149–0151 e o runtime correspondente, mas isso continua
  local, não promovido e sem prova de deploy/readback; automação e Conclusion escritora permanecem
  desabilitadas até todos esses gates passarem
- **Resultado local:** 6 skills automáticas + 11 explícitas, 35 casos de discovery, 9 casos do
  gate de Extraction e 15 casos de Conclusion; 17 testes e validadores de fonte/skill/plugin
  passaram. A revisão independente adicionou fencing de identidade, budget, TOCTOU, runtime e
  manifesto canônico antes da publicação.
- **Rollback:** reinstalar a versão anterior do plugin; nenhuma mudança de skill autoriza rollback
  de banco, worker ou job

## OLI-SKILL-004 — preservar a fronteira dos anexos PJe

- **Status:** aceita após canário produtivo, validada e instalada; smoke em sessão nova pendente
- **Data:** 2026-09-01
- **Alvo:** protocolos de `preaprovar-insumos-indexacao` e `preaprovar-indexacoes`, com reforço no
  perfil de Agravo de Instrumento
- **Hipótese:** distinguir processo, ato de juntada, subato/arquivo e conteúdo interno evita tanto
  o falso merge de anexos quanto o falso split por uma referência textual interna
- **Mudança:** anexos `parte_N` distintos preservam uma saída por arquivo e ordem física; mesmo CNJ
  ou ato não autoriza merge; referência ao TCU só cria processo juntado quando houver invólucro
  eletrônico próprio
- **Evidência:** no job Royal FIC, seis partes `002–006, 001` substituíram a row 20–1101; o run
  terminou `verified`, os seis hashes conferiram e a linhagem ficou 6/6
- **Validação:** quatro casos em `evals/documentary_boundaries.jsonl`, validadores das
  skills/plugin, `17/17` testes e igualdade fonte/cache passaram; smoke em sessão nova pendente
- **Rollback:** reinstalar a versão anterior do plugin; a correção DATA já aplicada permanece
  auditável por patch e linhagem próprios

## OLI-SKILL-005 — reconciliação explícita pós-reaper

- **Status:** candidata local; nenhuma RPC ou migration promovida
- **Data:** 2026-09-02
- **Alvo:** `reconciliar-orquestracao-pos-reaper`, orquestrador e protocolo de
  Conclusion
- **Hipótese:** separar o fechamento de uma lease zumbi do retry impede dupla
  cobrança/duplo efeito e torna o estado incerto observável sem inferência
- **Mudança:** skill explicit-only com censo, preview, CAS, RPC restrita,
  contabilidade released/unknown e readback terminal; o servidor do manifesto
  também exige contagens e hashes observados antes de permitir sucesso canônico
- **Validação exigida:** validadores de fonte/skill/plugin, testes do runtime e
  migration, smoke SQL transacional e, só após deploy coordenado, canário único
- **Resultado local:** 6 skills automáticas + 12 explícitas, 36 casos de
  discovery e 5 casos pós-reaper; validação local da fonte, skill e plugin
  passou
- **Rollback:** reinstalar o cachebuster anterior; não há estado remoto para
  desfazer enquanto migration/runtime não forem promovidos

## OLI-SKILL-006 — estender o gate editorial aos dados jurídicos

- **Status:** aceita localmente; sem mutação de DATA ou job
- **Data:** 2026-09-02
- **Alvo:** protocolo comum de `preaprovar-indexacoes`, Conclusion e padrão de degradação editorial
- **Hipótese:** revisar apenas o relatório deixa escapar português degradado em análises exibidas
  na UI; tratar relatório, análises e readback como superfícies distintas preserva qualidade sem
  confundir texto humano com enum técnico
- **Mudança:** o gate agora cobre campos humanos de indexações, horizontais e verticais, incluindo
  `julgamento_argumentos`; defeito no relatório gera sucessor, defeito canônico usa apenas patch
  tipado elegível, e perda de UTF-8 na Conclusion bloqueia a confirmação de persistência
- **Validação exigida:** quatro casos comportamentais, validador da fonte, validadores das skills e
  do plugin, testes e igualdade fonte/cache após reinstalação
- **Resultado local:** quatro casos adicionados; validador da fonte, seis skills alteradas e plugin
  passando; `17/17` testes; fonte igual ao cache instalado. Nenhuma regra usa dicionário rígido de
  palavras nem autoriza LLM, edição direta de tabela ou inferência semântica
- **Rollback:** reinstalar o cachebuster anterior; não houve escrita remota para desfazer

## OLI-SKILL-007 — executor Docker portátil por host

- **Status:** candidata local instalada; imagem multiarch e runtime remoto ainda não promovidos
- **Data:** 2026-09-02
- **Alvo:** `orquestrar-indexacoes`, launcher do plugin e build do runtime
- **Hipótese:** uma imagem Linux multiarch e um launcher host-side pequeno permitem alternar entre
  Mac e Windows sem criar duas implementações ou deslocar autoridade para o host
- **Mudança:** host config fechado, AppRole separado, doctor local, preview cercado por
  `command_sha256`, Docker non-root/read-only e ledger local redigido; `executor_site` é somente
  correlação e o claim/CAS OPS continua serializando o writer
- **Validação exigida:** seis casos de portabilidade, testes do launcher, validação integral do
  plugin, build manifest amd64/arm64, doctor em cada host e canário manual serial
- **Rollback:** reinstalar o cachebuster anterior; nenhuma mudança externa precisa ser revertida

Atualize o resultado com métricas, falhas e decisão. Mesmo uma rejeição permanece neste arquivo
para impedir repetição sem nova evidência.
