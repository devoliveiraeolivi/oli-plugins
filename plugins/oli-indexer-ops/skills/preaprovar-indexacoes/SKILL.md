---
name: preaprovar-indexacoes
description: Aplicar o protocolo comum de pré-aprovação do oli-indexer, compô-lo com a régua especializada, publicar relatório/patch versionados e, sob autorização explícita, resolver correções determinísticas com CAS e readback antes do novo parecer. Use para auditar jobs antes da aprovação humana, inclusive quando o tipo ainda precisa ser resolvido; não aprova job, chama LLM, reprocessa nem aplica patch sem autorização separada.
---

# Pré-aprovar indexações

Esta é a régua comum. Ela garante que todos os perfis especializados tenham o mesmo padrão de identidade, cobertura, rastreabilidade, custo e parecer, sem apagar suas diferenças jurídicas.

Antes da auditoria, leia [references/protocolo.md](references/protocolo.md), use `$consultar-oli-indexer` para as fontes e `$inspecionar-configuracao-indexacao` quando a conclusão depender de prompt, grafo, taxonomia, contrato ou analyzer.

Para todo job, execute também `scripts/check_logical_chain.py --repo <repo> --job-id <uuid>`.
Saída com `blockers > 0` impede `APTO` e deve ser conciliada com a íntegra e a régua
especializada. `branches[].status=open`, isoladamente, descreve uma etapa terminal ainda pendente:
não é lacuna quando o corpus termina na remessa/distribuição e não há ato posterior que pressuponha
seu encerramento. O bloqueio nasce de `gaps`, de consequência posterior sem causa material ou de
estado/resultado afirmado sem fonte; o script não inventa qual foi o desfecho jurídico.

## Composição obrigatória

Resolva `area/perfil` pelo job e aplique exatamente uma especialização:

- `tributario/execucao_fiscal`: `$preaprovar-execucoes-fiscais`.
- `tributario/conhecimento` com natureza `Ação Restituição` ou `MS - Restituição`: `$preaprovar-restituicoes-tributarias`.
- `tributario/conhecimento` com natureza `Embargos à Execução Fiscal`: `$preaprovar-embargos-execucao-fiscal`.
- `tributario/conhecimento` nas demais naturezas: `$preaprovar-conhecimento-tributario`.
- `tributario/agravo_instrumento`: `$preaprovar-agravos-tributarios`.
- `tributario/cautelar_fiscal`: `$preaprovar-cautelares-fiscais`.
- `tributario/administrativo_fiscal`, `administrativo_creditorio` ou `administrativo_regulatorio`: `$preaprovar-processos-administrativos`.
- Perfil sem especialização: use a régua comum, mas o parecer não pode ser `APTO`; reporte `REVISÃO NECESSÁRIA` ou `BLOQUEADO` e diga qual conhecimento de domínio falta.

Job legado sem `output.perfil` não é roteado por palpite. Resolva o perfil esperado com a
mesma configuração do indexador, usando área, classe, natureza e tribunal, registre a
divergência cadastral e aplique a checklist correspondente apenas como diagnóstico. O parecer
fica `BLOQUEADO` até a identidade do perfil do job ser confirmada ou saneada.

A especialização acrescenta gates; não substitui nem relaxa o protocolo comum. Não aplique regras de um perfil por analogia a outro.

## Camada documental adicional

Se `OPS.jobs.output.compactacao_documental` existir ou alguma row tiver evidência iniciada por
`compactacao_documental:`, aplique também `$preaprovar-compactacoes-documentais`. Essa régua é
ortogonal ao perfil: ela confere checkpoint, grupos de apresentação, herança de metadados e
exceções sem substituir a especialização jurídica escolhida acima.

## Limites

- A primeira passada é somente leitura e sem novas chamadas ao LLM do indexador.
- A pré-aprovação pode gravar somente artefatos de controle imutáveis
  (`indexing_review_reports` e `indexing_review_patches`) pelo `reviewctl save`, depois de
  anunciar essa etapa. Ela não altera `indexacoes`, análises, `jobs.llm_results`, prompts,
  status, aprovação ou gate secundário.
- Qualquer correção, reviewer, recall ou reprocessamento é uma operação posterior, com escopo, custo e autorização próprios.
- Autorizada a aplicação de um patch determinístico, não encerre o trabalho no parecer antigo:
  aplique-o com CAS, acompanhe o run até estado terminal, faça readback material, repita a
  pré-aprovação e publique o relatório sucessor. Patch verificado não aprova o job.
- O gate `revisao_secundaria_at >= human_edited_at` é independente do parecer material. Se a
  reauditoria pós-patch não encontrar dúvida material, publique `fit`/`fit_with_notes` e relate o
  gate pendente apenas como próxima ação humana; nunca crie finding `F-SECONDARY-REVIEW` nem use
  `review_required` só por esse timestamp. O oli-app confirma o gate antes da aprovação final, e
  um parecer não positivo tornaria `Confirmar e aprovar` circular.
- `APTO` exige cobertura integral prevista no protocolo comum, completude causal da linha do
  tempo e todos os gates da especialização. Cobertura de 100% das folhas disponíveis não prova
  que o corpus esteja completo quando os próprios atos apontam para outro processo, instância ou
  incidente. Amostragem nunca autoriza esse parecer.

## Regra repair-first

Antes do parecer, classifique cada achado como `patchavel` ou `nao_patchavel`. É `patchavel`
somente quando a fonte auditada determina sem ambiguidade o valor correto, o contrato de patch
aceita o alvo, a identidade e o estado corrente foram lidos, e a correção não depende de LLM,
reviewer, nova fonte, recall ou reprocessamento.

- Para todo achado `patchavel`, gere e publique o patch no mesmo fluxo. Não entregue apenas a
  descrição do erro nem recomende uma correção manual já representável por `review-patch`.
- Se o pedido corrente já contém autorização explícita para corrigir/aplicar aquele escopo,
  aplique o patch imediatamente após preflight e prossiga até readback e parecer sucessor. Não
  mantenha `BLOQUEADO` por um erro que o patch autorizado acabou de resolver.
- Sem autorização de aplicação, preserve a separação de autoridade: publique o patch e use
  `REVISÃO NECESSÁRIA`, indicando que a única ação pendente é autorizar/revisar sua aplicação.
  O dado ainda incorreto impede `APTO`, mas não deve ser apresentado como impasse material.
- Use `BLOQUEADO` quando não houver correção determinística segura, faltar fonte ou alvo elegível,
  houver ambiguidade, o contrato não representar a mudança, ou a aplicação terminar
  `stale`, `failed` ou `failed_partial` sem reparo verificado. Nunca force um patch para evitar o
  bloqueio.

Leia em [references/protocolo.md](references/protocolo.md) o ciclo de aplicação, readback e
publicação sucessora.

## Artefatos e publicação

Para cada job, produza em diretório local de artefatos um `report.json` conforme
`review-report/v1` e, somente quando toda correção for determinística e suportada, um
`patch.json`. Use `review-patch/v1` para correções esparsas e `review-patch/v2` somente
para `merge`/`split` estruturais. Use UUIDs reais e um `patch_key` curto e estável. O patch
contém operações tipadas, valores `expect`/`set`, impacto e linhagem quando aplicáveis;
nunca contém SQL livre.

Valide com `reviewctl validate`, recompute o `source_digest` e publique pelo gateway com
`reviewctl save`, enviando as cabeças esperadas lidas do OPS. Sempre que houver patch, v1 ou
v2, calcule com `reviewctl digest --patch <patch.json>`; sem essa associação, alvos explícitos
fora do staging atual não entram na fotografia e o snapshot é inválido. Para patch estrutural,
o digest usa `review-source/v2`. Conflito `STALE_*` exige nova leitura; nunca sobrescreva por
último. Se não houver correção segura, publique o relatório sem patch. Informe IDs, hash,
chave e versão persistidos.

Ao auditar o processo completo, um erro pode estar numa `DATA.indexacoes` de incremento
anterior. Nesse caso, `target.job_id` deve ser o proprietário real lido naquela row, nunca o
`job_id` do relatório por conveniência. Em v1, só proponha esse alvo se ele tiver o mesmo CNJ,
estiver `concluido` e existir um job atual elegível em pré-aprovação; não use essa exceção para
corrigir processo fechado, `DATA.processos` ou projeções derivadas.

Merge/split é a primeira de duas revisões. A aplicação estrutural deixa as saídas pendentes,
invalida horizontais e remove verticais dependentes; não herda conclusões nem chama LLM. Após o
readback da topologia e da linhagem, execute nova pré-aprovação sobre o estado atual e proponha a
recomposição horizontal/vertical separadamente. Patch estrutural verificado não torna o job
`APTO` por si só.

Antes do `save`, exija `jobs.validation_published_at` preenchido. Em jobs anteriores ao
checkpoint, não improvise o carimbo e não use `report_html` antigo como prova suficiente:
gere o manifesto pelo backfill versionado do repositório, obtenha autorização específica para
a lista exata e só então aplique com CAS e readback. Ausência do checkpoint não impede a
auditoria local, mas impede a publicação do relatório no control plane.

Se o usuário discordar de um patch já publicado, resolva a série pela chave, altere apenas o
JSON local, incremente a versão e use `reviewctl revision` com o hash exato do parent. Não
edite uma revisão existente. Se a revisão acrescentar ou trocar um alvo material que não
estava na fotografia anterior, publique um novo relatório-snapshot com `reviewctl save`, não
uma simples revisão presa ao digest antigo. A aplicação ocorre pelo oli-app ou por comando
explicitamente autorizado, nunca como efeito implícito desta skill.
