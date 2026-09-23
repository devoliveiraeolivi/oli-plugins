---
name: preaprovar-indexacoes
description: Auditar jobs do oli-indexer após as análises e antes da aprovação humana, aplicando o protocolo comum e a régua jurídica do perfil. A primeira passada é somente leitura; patches determinísticos elegíveis podem ser fechados, mas a skill nunca aprova o job nem chama LLM ou reprocessa sem autorização separada.
---

# Pré-aprovar indexações

Produza o parecer técnico final sem substituir a aprovação humana. A régua comum controla
identidade, cobertura, rastreabilidade, custo e reparos; a referência do perfil acrescenta os
gates jurídicos aplicáveis.

Antes da auditoria, leia [references/protocolo.md](references/protocolo.md). Use
`$consultar-oli-indexer` para OPS/DATA e `$inspecionar-configuracao-indexacao` apenas quando a
conclusão depender de prompt, grafo, taxonomia, contrato, schema, dispatch ou analyzer.

## Diagnóstico obrigatório

Antes de abrir o primeiro snapshot, resolva o alvo:

- Com `job_id` ou CNJ explícito, confirme que o job pertence ao perfil e à natureza pedidos.
- Sem `job_id` ou CNJ, use `$consultar-oli-indexer` para listar deterministicamente jobs
  `queue=indexing`, `status=awaiting_approval` e `approved_at` vazio, filtrados pelo
  `area/perfil/natureza` solicitado; informe a quantidade antes de auditar um por vez.
- Para restituições, separe `Ação Restituição` de `MS - Restituição`. Para administrativos,
  discrimine os três perfis exatos. Mais de um job aberto para o mesmo processo impede escolher o
  vigente por conveniência.
- Resolva identidade pela row do job e pela configuração do indexador, nunca apenas por assunto,
  título, menção textual, formato do número ou aparência do CNJ.

Para todo job:

1. congele job, processo, checkpoint e cabeças correntes conforme o protocolo;
2. leia `DATA.indexacoes` do processo inteiro, preservando o `job_id` proprietário de cada row;
3. execute os três detectores em `scripts/`:
   - `check_logical_chain.py`;
   - `check_process_structure.py`;
   - `list_deterministic_findings.py`;
4. concilie cada finding com a fonte material e a régua do perfil;
5. classifique cada achado como `patchavel` ou `nao_patchavel` antes do parecer.

`blockers > 0` impede `APTO`, mas o detector não substitui interpretação jurídica. Branch
terminal ainda aberta não é lacuna por si só quando o corpus termina na remessa/distribuição e
nenhum ato posterior pressupõe desfecho. `snapshot.complete=false` exige detectores legados
aplicáveis ou Validation completa; nunca significa ausência de warnings.

Não esconda rows de outros jobs nem transforme duplicata técnica em `Documento (Duplicação)`.
Gaps, overlaps, staging órfão e owners anteriores continuam visíveis no processo inteiro.

Execute todos os scripts Python desta skill pelo ambiente do repositório:
`uv run python <caminho-do-script>`. Não use o `python3` do sistema, porque ele
não carrega as dependências e o `.env` do `oli-indexador`.

## Roteamento jurídico

Resolva `area/perfil/natureza` pelo job e leia exatamente uma referência principal:

- `tributario/execucao_fiscal`:
  [execução fiscal](references/profiles/execucao-fiscal.md);
- `tributario/conhecimento` + `Ação Restituição` ou `MS - Restituição`:
  [restituições judiciais](references/profiles/restituicoes-judiciais.md);
- `tributario/conhecimento` + `Embargos à Execução Fiscal`:
  [embargos à execução fiscal](references/profiles/embargos-execucao-fiscal.md);
- demais naturezas de `tributario/conhecimento`: leia
  [conhecimento tributário](references/profiles/conhecimento-tributario.md), mas só admita `APTO`
  quando houver seção material explícita para a natureza; não transporte gates por analogia;
- `tributario/agravo_instrumento` + natureza `Agravo de Instrumento`:
  [agravo de instrumento](references/profiles/agravo-instrumento.md);
- `tributario/cautelar_fiscal`:
  [cautelar fiscal](references/profiles/cautelar-fiscal.md);
- `tributario/administrativo_fiscal`, `administrativo_creditorio` ou
  `administrativo_regulatorio`:
  [processos administrativos](references/profiles/processos-administrativos.md).

Perfil sem referência explícita recebe apenas a régua comum, deve indicar qual conhecimento de
domínio falta e termina somente `REVISÃO NECESSÁRIA` ou `BLOQUEADO`, nunca `APTO` ou `APTO COM
RESSALVAS`. Job legado sem `output.perfil` não é roteado por palpite: derive o perfil esperado pela
configuração do indexador usando área, classe, natureza e tribunal, registre a divergência e use a
referência correspondente somente como diagnóstico. Mantenha `BLOQUEADO` até confirmar ou sanear
a identidade.

## Camadas condicionais

Além da referência principal, leia somente quando o gatilho existir:

- [compactação documental](references/overlays/compactacao-documental.md), quando houver
  `output.compactacao_documental` ou evidência `compactacao_documental:`;
- [prescrição intercorrente](references/overlays/prescricao-intercorrente.md), em execução fiscal
  quando o grafo publicado declarar a vertical legada ou
  `jobs.llm_results.prescricao_intercorrente` existir como objeto não vazio. Só
  nesse caso execute `uv run python scripts/check_prescricao_intercorrente.py
  --input <snapshot.json>`. Menção ao art. 40, frustração, parcelamento ou
  decisão continua exigindo revisão material dentro do ledger EF v5, mas não
  autoriza fabricar nem cobrar a vertical legada. Idade do processo, feed
  vazio, ausência de notícia, citação, penhora ou garantia isoladas não bastam.

Essas camadas acrescentam gates; não substituem a referência principal.

## Autoridade e fechamento

- A primeira passada, até fechar e classificar o snapshot, é somente leitura e sem nova chamada
  ao LLM do indexador.
- A pré-aprovação técnica e jurídica é executada localmente por esta skill e suas referências;
  reviewer externo é uma camada opcional de evidência, nunca pré-requisito para `APTO`.
- O pedido de pré-aprovação autoriza, para os jobs do snapshot inicial, salvar os artefatos de
  controle e fechar patches determinísticos elegíveis pelo runner oficial com CAS, estado
  terminal, readback, reauditoria e relatório sucessor.
- Não autoriza correção ad hoc, alvo novo, LLM/reviewer, recall/delete, reprocessamento, backfill,
  mudança de código/prompt, Conclusion ou aprovação humana.
- Nunca altere `approved_at`, `approved_by`, `status` para conclusão nem o gate/timestamp de revisão
  secundária. Esses campos pertencem ao fluxo humano ou ao produtor autorizado.
- Aplique um patch corrente por vez. Pare em ambiguidade, escopo novo, conflito CAS recorrente,
  `failed` ou `failed_partial`; preserve a evidência e reporte o ponto exato.
- Patch verificado corrige o dado, mas não aprova o job. Merge/split invalida dependências e exige
  nova pré-aprovação antes de qualquer recomposição horizontal ou vertical.

Use `review-report/v1`, `review-patch/v1` para correções esparsas e `review-patch/v2` para
merge/split. Valide e publique com `reviewctl`; nunca escreva diretamente nas tabelas nem use SQL
livre. O ciclo completo, contratos e readbacks obrigatórios estão no protocolo.

## Entrega

Separe fatos, inferências e lacunas. Informe identidade, fontes, cobertura, findings, perfil e
camadas lidas, custo novo, patches/runs/readbacks, parecer corrente e gates ainda pendentes. Use
somente `APTO`, `APTO COM RESSALVAS`, `REVISÃO NECESSÁRIA` ou `BLOQUEADO` conforme o protocolo.
Antes de publicar, aplique também o gate editorial da seção 8.1 do protocolo a todos os campos
humanos exibidos na UI.
