---
name: preaprovar-insumos-indexacao
description: Auditar o corpus process-wide no gate awaiting_indexing_review antes das análises. A primeira passada é somente leitura; a skill prepara um review-patch/v3 exaustivo para aplicação humana e acompanha o aceite técnico, mas nunca substitui o clique, a aprovação final, LLM, recall ou reprocessamento.
---

# Pré-aprovar insumos da indexação

Revise o corpus que alimentará as análises caras. A skill produz o resultado
operacional completo e prepara um único patch visível quando necessário. O
usuário aplica o conjunto; depois do clique não há nova revisão nem LLM, apenas
aplicação, CAS/fencing, readback e aceite técnico. A aprovação humana final
continua separada, depois das análises.

Antes de agir, leia [references/protocolo.md](references/protocolo.md). Use
`$consultar-oli-indexer` para OPS/DATA e `$inspecionar-configuracao-indexacao`
quando perfil, taxonomia, grafo, template, hash, dispatch ou analyzer forem
materialmente relevantes.

## Escopo obrigatório

- Resolva um job `queue=indexing`, `status=awaiting_indexing_review`, não aprovado,
  com `indexing_checkpoint_published_at` e `indexing_checkpoint_digest` presentes.
- Congele o job e o processo pelo par `job_id` + `numero_processo`; nunca aceite
  apenas CNJ, título ou posição na fila como identidade suficiente.
- Leia `DATA.indexacoes` do CNJ inteiro, em todos os jobs proprietários. Preserve
  `job_id`, `id_externo`, folhas, status e íntegra de cada row.
- Leia todas as folhas, a taxonomia resolvida e o manifesto runtime do checkpoint.
- Exclua da decisão a qualidade de `analise_estruturada`, resultados, resumos e
  verticais. Eles ainda não devem existir para esta safra.
- Não faça nova chamada LLM do Indexer. O relatório deve registrar custo zero.

Execute os detectores process-wide do protocolo comum, inclusive cadeia lógica e
estrutura do processo. Resolva `area/perfil/natureza` pelo roteador de
[`preaprovar-indexacoes`](../preaprovar-indexacoes/SKILL.md#roteamento-jurídico), leia a referência
principal correspondente e use apenas seus requisitos sobre peças, decisões, rito, sujeitos,
relações e causalidade. Não exija nem avalie horizontais ou verticais ainda não produzidas. Se
houver compactação documental, leia também a camada condicional indicada pelo roteador.

## Autoridade e limites

O pedido explícito de pré-aprovação dos insumos autoriza, apenas para os jobs
congelados no snapshot inicial:

- salvar `review-report/v2` do estágio `indexing_input`;
- publicar um único `review-patch/v3` determinístico e exaustivo;
- depois do clique humano, acompanhar até terminal e conferir o readback;
- aceitar tecnicamente o input pelo readback tipado do mesmo run.

Essa autorização cobre a autoria e a publicação do plano. Não cobre o clique
**Aplicar patch**: não enfileire nem execute por iniciativa própria. Depois da
aplicação autorizada, o mesmo run faz o readback e o aceite técnico sem novo
turno de análise.

Não autoriza LLM, reviewer, Refinement adicional, recall, delete, reprocessamento,
backfill, SQL livre, edição direta de tabela, publicação de prompt, deploy,
Conclusion ou alteração de `approved_at`/`approved_by`.

## Repair-first

Classifique cada achado como `patchavel` ou `nao_patchavel`. Patch só é elegível
quando a fonte já lida determina uma única correção, o alvo e o owner são exatos,
o estado corrente foi relido e `review-patch/v3` representa toda a mudança.

`review-patch/v3` permite somente correções de input:

- `indexacao.update` para campos materiais suportados;
- `indexacao.merge` e `indexacao.split` com cobertura, source IDs, conteúdo e
  linhagem explícitos.

Nunca use `indexacao.analysis.replace`, `job.vertical.replace`, escreva
`jobs.llm_results` ou promova `status_validacao`. Não misture operações esparsas
e estruturais na mesma revisão.

Para merge/split, use impacto `downstream_state=not_started`,
`horizontal=not_present`, `vertical_keys=[]`. Prove antes:

- continuidade ou separação material da unidade documental;
- inventário de `carimbo_subato`, arquivo, faixa e ordem física; anexos `parte_N` distintos não se
  fundem pelo mesmo CNJ ou ato de juntada;
- cobertura sem gap/overlap criado;
- peça nativa versus cópia e processo de referência;
- agravo, decisão recorrida, decisão do agravo, retorno e eficácia nestes autos;
- owner real de toda row absorvida e íntegra reconstruível pelas folhas.

Não pare no primeiro defeito. Audite o estágio inteiro e publique um único patch
com operação ou justificativa explícita para cada finding material. Decisões de
relações do mesmo snapshot pertencem ao mesmo `review-patch/v3`; `candidate` e
`conflict` não podem sobrar sem `accept`, `reject` ou ambiguidade jurídica real.
Depois do clique, aguarde `verified`, confira DATA, `indexing_input_edited_at` e o
digest aceito. Não exija novo turno de auditoria quando o plano exaustivo e o
readback casarem.

## Parecer

Use os quatro resultados operacionais:

- `PRONTO_PARA_APROVAR`: input apto, sem patch;
- `PATCH_PRONTO_PARA_APLICAR`: plano exaustivo pronto para o clique;
- `DECISAO_HUMANA_NECESSARIA`: ambiguidade jurídica real;
- `BLOQUEIO_TECNICO`: fonte, cobertura, topologia, identidade, runtime ou contrato
  incapaz de representar a correção.

`fit_with_notes` não pode esconder dúvida de classificação, fronteira, relação,
origem, fonte crítica ou cadeia causal. Amostragem nunca produz parecer positivo.

Ao terminar, a ação exibida ao usuário deve ser somente **Aplicar patch**,
**Aprovar**, **Aguardando processamento** ou **Decisão jurídica necessária**.
Detalhe estados técnicos apenas diante de erro e separe:

1. gate técnico aceito após aplicação humana e readback, ou ainda bloqueado por exceção;
2. patches e readbacks executados;
3. análises horizontais/verticais ainda não executadas;
4. aprovação humana final ainda pendente.
