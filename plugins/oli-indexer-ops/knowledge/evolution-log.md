# Log de evolução

## 2026-09-02 — runtime local portátil e multiarch

- a raiz completa do plugin, e não apenas `skills/`, virou a unidade de migração entre hosts;
- `oli-indexer-ops-host/v1` fixa plugin, imagem, plataforma, budgets, recursos e AppRole por host;
- o launcher Python faz doctor/pull/invoke sem shell, cerca o container e exige o hash integral do
  preview antes de executar;
- Mac arm64 e Windows amd64 usam o mesmo manifest Linux multiarch; OPS claim/CAS continua sendo a
  autoridade global e `executor_site` é apenas telemetria;
- seis cenários de portabilidade cobrem hosts, writer único, segredo, crash e cron prematuro;
- nenhuma imagem, migration, configuração remota, job, cron ou Conclusion foi promovida.

## 2026-09-02 — budgets tipados e qualidade editorial ponta a ponta

- a intenção passou a reservar separadamente LLM, reviewer, embedding e páginas de Vision, além
  de custo total, custo por efeito e tempo, sempre ligada ao snapshot de preços;
- o gate editorial deixou de revisar apenas o parecer e passou a cobrir campos humanos de
  indexações, análises horizontais/verticais e o readback da Conclusion;
- literais técnicos continuam preservados após confirmação de schema, prompt e consumidores;
- quatro regressões cobrem parecer sem acentos, rótulo humano persistido, literal técnico e perda
  de UTF-8 entre manifesto e Salesforce;
- nenhuma dessas regras autoriza chamada LLM, edição direta de DATA, reprocessamento ou Conclusion.

## 2026-09-02 — fechamento pós-reaper e manifesto canônico executável

- adicionada a skill explícita `reconciliar-orquestracao-pos-reaper`; ela só
  fecha o ledger depois de `ZOMBIE_NO_HEARTBEAT` comprovado e nunca faz retry;
- reservas não iniciadas passam a `released`; efeitos já iniciados passam a
  `UNKNOWN` pelo teto reservado, com target/run bloqueados e recibo hash-only;
- a skill de Conclusion passou a exigir que o servidor confirme contagens e
  hashes observados do `persistence-manifest/v1`, além do booleano do runner;
- cinco casos comportamentais cobrem ausência de prova do reaper, efeitos
  started/reserved, drift contábil e tentativa de retry;
- fonte e plugin passaram nos validadores locais; promoção de migration,
  deploy, canário e qualquer cron escritor continuam gates separados.

## 2026-09-01 — arquitetura orientada a roteamento

- estabelecida fonte Git para o plugin local;
- preservados como skills públicas os gates operacionais distintos;
- especializações jurídicas e overlays migrados para referências da pré-aprovação final;
- descrições reduzidas para melhorar discovery;
- iniciado corpus leve de casos de discovery e histórico de impacto.
- uma primeira revisão independente rejeitou a candidata por quatro perdas semânticas; os freios
  foram repostos no roteador e nas referências antes de nova validação.
- uma auditoria pós-consolidação encontrou regras materiais adicionais nos wrappers antigos; a
  arquitetura foi ajustada para seis skills automáticas, nove aliases explícitos e referências
  canônicas completas;
- o teste de encaminhamento encontrou a ausência dos gates técnicos de extração e insumos no fluxo
  completo; a orquestração passou a compor esses gates antes da pré-aprovação final;
- a revisão semântica sucessora encerrou sem bloqueios depois de proibir parecer positivo para
  perfil sem régua especializada.

O ciclo automático de manutenção/proposição ficou deliberadamente fora desta etapa. Ele só será
considerado após acumular falhas reais e uma validação comportamental confiável.

## 2026-09-01 — promoção versionada do gate pós-extração

- o overlay do PR 1224 foi comparado com a skill canônica e promovido sem criar outra skill;
- o conteúdo curto ficou no `SKILL.md` e o procedimento detalhado em `references/protocolo.md`;
- migrations e runtime passaram a ser capability gate: sem 0141/0142 + worker + smoke, toda
  execução fica somente leitura e nenhum caminho legado é usado;
- após a entrada da migration de assuntos `0140` no `main`, o gate foi renumerado de 0140/0141
  para DATA 0141/OPS 0142 em runtime, skill, validadores e histórico antes da publicação;
- nove cenários comportamentais fixam fonte, backlog, repair, retry, stale head, handoff jurídico e
  seleção de canário;
- a revisão de segurança encontrou e a implementação corrigiu ACL do claim, stale patch, ordem de
  locks e overwrite de lease sucessora antes da promoção.

## 2026-09-01 — orquestração integral com Conclusion separada

- `orquestrar-indexacoes` substituiu o nome diário como única entrada automática do fluxo
  integral; `rodar-e-preaprovar-indexacao` permaneceu como alias explicit-only;
- a intenção `orchestration-intent/v1` passou a congelar escopo, ações, versões, budgets e
  concorrência antes das escritas;
- `concluir-indexacoes-aprovadas` isolou a autoridade pós-humana e exige approved-only, dry-run,
  execução serial, reconciliação de resposta incerta e readback OPS/DATA/Salesforce;
- o contrato proíbe inferir aprovação por `approved_by`, `success` ou logs e trata retorno a
  `approved_at=null` como novo gate humano;
- agentes paralelos ficaram limitados a auditoria read-only; worker, patch e aceite permanecem na
  fila escritora única;
- o catálogo inicial de uma sessão deixou de ser tratado como oráculo: a documentação oficial
  permite truncamento quando há muitas skills, então o smoke valida invocação/composição e versão;
- a revisão independente sucessora exigiu job IDs também no run normal, intenção standalone,
  budget pré-chamada, CAS do snapshot aprovado, prova OCI imutável e
  `persistence-manifest/v1`; sem essas capacidades a skill para no dry-run;
- a regressão final estendeu o CAS a toda retomada `--run-only` e tornou o
  manifesto imutável e sensível aos valores materiais, não apenas à identidade;
- automação recorrente escritora continua fora enquanto control plane, deploy, canários e kill
  switch não estiverem comprovados.

## 2026-09-01 — fronteira documental de anexos PJe

- o canário Royal FIC revelou que unidade jurídica da cópia, ato eletrônico e arquivo anexado não
  são a mesma fronteira;
- a row agregada de folhas 20–1101 foi dividida nas seis partes físicas `002–006, 001`, com hashes
  e linhagem verificados;
- o TCU permaneceu referência interna das partes iniciais, não um segundo processo juntado;
- os protocolos de input e pré-aprovação final passaram a inventariar subato, arquivo, faixa e
  ordem física antes de qualquer merge/split;
- quatro casos de regressão cobrem ordem fora do sufixo, referência interna, fragmento no mesmo
  subato e anexos distintos com o mesmo CNJ.
- validadores das duas skills, plugin e fonte, `17/17` testes e igualdade entre fonte e cache
  passaram antes da reinstalação; resta apenas o smoke comportamental em sessão nova.
