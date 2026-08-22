# Checklist especializada de Agravo de Instrumento tributário

Execute depois do protocolo comum. Valores taxonômicos e analyzers válidos vêm da configuração atual do perfil `tributario/agravo_instrumento`.

## 1. Identidade recursal

- Confirme o CNJ do próprio AI, o processo de origem, a decisão interlocutória recorrida, agravante, agravado e polo do cliente.
- Nos próprios autos do AI, subclasses nativas não recebem prefixo `(Agravo)`. Esse prefixo pertence ao bloco de AI levado aos autos principais.
- A petição que inaugura o AI é `Parte / Peça Processual / Petição Inicial` neste perfil. A cópia da interlocutória recorrida e as peças da origem são `Parte / Documento / Documento`, com `numero_processo_ref` da origem.
- Não promova atos da origem a decisões deste AI. Tampouco rebaixe decisão do relator/colegiado deste AI a documento por mencionar o processo originário.

## 2. Formação e granularidade

- Delimite petição do agravo, comprovante de preparo e documentos obrigatórios/facultativos sem transformar a cópia integral da origem em timeline nativa.
- Reconstrua os frames e slots do evento que juntou as peças da origem. Se as páginas formam um único pacote de cópia integral, a fragmentação folha a folha ou evento a evento é anomalia; anexos materialmente distintos permanecem separados. O mesmo CNJ, sozinho, não autoriza fundir documentos diferentes.
- Ementa, relatório, voto, extrato/ata e acórdão do mesmo julgamento devem obedecer às regras de fusão ou de `Ato de Julgamento` do prompt atual.
- Evento “recurso conhecido/não provido” seguido da juntada do inteiro teor do mesmo acórdão não pode produzir dois julgamentos materiais.
- Inclusão em pauta e relatório anexado podem exigir dois andamentos: ato cartorário de pauta e `Julgador / Ato de Julgamento / Relatório de Julgamento`. Não fundir ambos como despacho apenas por compartilharem o evento.

## 3. Escada de decisões do AI

Leia o dispositivo e pergunte o que foi decidido:

- só tutela recursal/efeito suspensivo, com AI seguindo: `Julgamento: Liminar Agravo`;
- mérito/extinção monocrática do próprio AI, inclusive “liminarmente”: `Julgamento: Decisão Monocrática`;
- mérito colegiado: `Julgamento: Acórdão Agravo`;
- perda superveniente do objeto do próprio AI: `Julgamento: Agravo Prejudicado`;
- desistência homologada: `Julgamento: Homologação de Desistência`;
- embargos de declaração: `Julgamento: Embargos Declaratórios` ou variante infringente;
- agravo interno contra monocrática: `Julgamento: Agravo Interno`;
- gate de REsp/RE: `Decisão de Admissibilidade` apropriada.

“O mais engole o menos”: se o dispositivo dá/nega provimento ou não conhece do AI, o recurso terminou; menção simultânea à tutela não converte o ato em liminar.

## 4. Prejudicialidade e incidentes

- `Agravo Prejudicado` é reservado à perda de objeto do próprio AI.
- Embargos de declaração julgados prejudicados continuam sendo `Julgamento: Embargos Declaratórios`; o título/resumo/resultado registram a prejudicialidade.
- Sentença superveniente na origem pode prejudicar o AI ou apenas um incidente. Identifique no dispositivo qual recurso foi julgado.
- ED ou agravo interno com efeito infringente pode substituir o resultado anterior; sem efeito modificativo, não apague o resultado principal.

## 5. Atos críticos

Abra integralmente a fonte de:

- petição inicial do AI e decisão recorrida da origem;
- decisão de tutela recursal, monocrática terminativa e acórdão do AI;
- relatório, votos, extrato/ata e certidão de julgamento;
- contraminuta, parecer do MP, ED, agravo interno, REsp/RE e admissibilidade;
- comunicação ao juízo de origem, trânsito e baixa;
- qualquer bloco grande de peças da origem ou outro processo.

Confirme dispositivo, objeto, recorrente, colegialidade, resultado e favorabilidade. Certidão de julgamento não é o acórdão; comunicação entre instâncias não é ofício a destinatário externo.

## 6. Funções, trânsito e baixa

- Ato nativo do AI é de relator, presidente ou colegiado; `Magistrado - Juiz` é incompatível salvo documento da origem corretamente classificado como documento.
- Decisão monocrática usa relator; juízo de admissibilidade da Presidência/Vice usa presidente; o acórdão deve preservar relator e demais julgadores quando a fonte permitir.
- Só marque trânsito com ato explícito. Decurso de prazo e análise de decurso, isolados, não bastam.
- O trânsito encerra o AI, não necessariamente o processo de origem. A baixa devolve a questão ao juízo a quo e não altera o mérito já julgado.

## 7. Análises horizontais e verticais

- Inicial e todos os julgamentos canônicos devem ter analyzer esperado pelo grafo/dispatch vigente; confira classificação, schema, dispositivo, resultado, cliente, julgadores e votação.
- No AI standalone, `primeira_instancia = Não Julgado` é normal: a interlocutória da origem não preenche esse campo. O mérito do AI alimenta segunda instância.
- Uma decisão cumulativa pode alimentar liminar e segunda instância, conforme o dispositivo, sem criar dois andamentos falsos.
- `transito_julgado` exige fonte explícita; vertical que infere trânsito de mero decurso é bloqueante.
- Resumo, argumentos e dossiê devem distinguir tutela, mérito do AI e incidentes, e nunca chamar decisão terminativa de simples indeferimento de efeito suspensivo.

## 8. Casos de regressão obrigatórios

Trate como gates explícitos em toda auditoria:

- o mesmo acórdão aparece duas vezes: evento de julgamento/juntada e inteiro teor em rows separados;
- `Agravo Prejudicado` foi aplicado a embargos de declaração prejudicados;
- inclusão em pauta com relatório foi comprimida em um despacho e o relatório desapareceu;
- um único pacote de cópia integral da origem foi fragmentado em dezenas de andamentos sem apoio nos frames/slots; não acione este gate apenas porque anexos distintos referem o mesmo CNJ;
- dossiê marcou trânsito apenas porque houve decurso de prazo;
- decisão recorrida da origem foi classificada como Julgador do AI;
- subclasses `(Agravo) ...` aparecem nos autos nativos do AI.

## 9. Cobertura e saída

Revise metadados de todas as rows, a íntegra de todos os atos críticos, todas as rows com analyzer e todas as anomalias. `APTO` exige cobertura integral do escopo e reconciliação da cadeia recursal completa usada pelas verticais.

Por processo, escreva:

1. resumo da origem, decisão recorrida e estado atual;
2. veredito;
3. tabela `fls. | está | deve ficar | por quê`;
4. divergências das verticais;
5. patch proposto, sem aplicá-lo;
6. custo histórico e, quando identificável, delta da execução.
