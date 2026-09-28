# Checklist especializada de processos administrativos

Execute depois do protocolo comum. Valores válidos vêm da configuração atual do perfil.

Use `$inspecionar-configuracao-indexacao` em toda auditoria destes perfis para confirmar taxonomia,
prompt, grafo, dispatch, analyzer e schema efetivamente usados; não confie apenas no checkout.

Use somente para `tributario/administrativo_fiscal`, `administrativo_creditorio` ou
`administrativo_regulatorio`. Não decida pelo formato do número do processo e não transporte rito,
órgão, ator ou efeito entre os três perfis.

## 1. Rito, ator e taxonomia

- Categoria identifica o ator; classe identifica o efeito/tipo do ato.
- Não aceite o legado `Magistrado` nem classes judiciais aposentadas, salvo quando o texto exato existir como valor válido na taxonomia corrente.
- `Julgamento` não implica necessariamente `Julgador`: o perfil creditório pode ter decisão da Autoridade Fiscal. Use a tripla e o conteúdo.
- Não aplique CPC, instâncias judiciais ou terminologia de sentença/acórdão por analogia quando o rito administrativo define órgãos e recursos próprios.
- Diferencie decisão/julgamento de encaminhamento, diligência, manifestação fiscal, intimação e mero expediente pelo dispositivo e pelo ator.
- Não autocorrija data por monotonicidade; emissão, publicidade, ciência, protocolo e documento copiado podem divergir.

## 2. Atos críticos

Abra integralmente a fonte de:

- autuação/lavratura e peças inaugurais;
- defesa, impugnação, manifestação fiscal e parecer;
- julgamento, admissibilidade, recurso e trânsito administrativo;
- diligências, perícias e decisões interlocutórias relevantes;
- qualquer ato que altere crédito, penalidade, exigibilidade ou encerramento.

Confirme objeto, autoridade, órgão, pedidos, fundamentos, dispositivo, efeito, resultado e favorabilidade sem converter alegação em decisão.

Encaminhamento terminal à DRJ, CARF ou CSRF, distribuição por sorteio e admissibilidade que ainda
aguarda julgamento descrevem o estágio atual normal do processo; não exija um ato futuro que ainda
não ocorreu. Bloqueie completude causal somente quando retorno, trânsito administrativo, cobrança,
baixa ou outra consequência posterior pressupuser um desfecho intermediário ausente. Se uma
vertical afirmar remessa ou julgamento sem fonte material, bloqueie a afirmação sem lastro, não a
mera pendência do processo.

## 3. Análises horizontais

- Derive o analyzer pelo grafo/dispatch atual; não use listas antigas por memória.
- `julgadores` e `votacao` só podem existir em análise cuja categoria final seja `Julgador`. Em ato de `Autoridade Fiscal` ou `Agente Fiscalizador`, a presença é divergência.
- `sem_analise` e envelope antigo podem exigir nova chamada, mas nesta etapa apenas planeje.
- `escalar_orfao` pode permitir correção determinística posterior; `escalar_divergente` deve preservar ambos e ir à decisão humana.
- `envelope_de_outro_analyzer` indica que o analyzer correto não rodou; não renomeie o envelope para fazê-lo parecer válido.
- Valide classificação, `schema_version`, resultado, resultado do cliente, fundamentação, órgão, julgadores e votação contra a fonte.

## 4. Verticais administrativas

Confira, quando ativadas pelo grafo:

- `resumo_processual`;
- dossiê de julgamentos e seus níveis aplicáveis ao rito;
- julgadores/votação;
- argumentos e insights.

Regras:

- ausência é aceitável apenas se o dispatch/toggle do perfil não produz a vertical ou não existe ato canônico necessário;
- argumentos e insights formam par atômico;
- sem andamento de classe canônica `Julgamento`, argumentos/insights devem ser não aplicáveis e não gerar chamada;
- decisão provável mal classificada é dúvida bloqueante, não justificativa para omitir silenciosamente a vertical;
- nenhuma vertical pode inventar instância, autoridade, voto, recurso ou resultado.

## 5. Cobertura especializada

Revise integralmente todas as rows de julgamento, decisão de admissibilidade, defesa, recurso, pedido, lavratura, manifestação/parecer fiscal e trânsito administrativo; todas as rows com analyzer; e toda anomalia ou resumo genérico.

No parecer, discrimine os três perfis administrativos e qualquer regra exclusiva identificada na taxonomia/grafo. Não esconda um processo bloqueado em totais consolidados.

## Diagnóstico opcional de análises

`scripts/backfill/corrigir_analises_faltantes.py` pode ser executado sem `--execute`, limitado aos
CNJs/jobs auditados, para enumerar análises ausentes ou divergentes. O dry-run informa chamadas
planejadas; não autoriza executá-las nem representa custo já incorrido.

Em qualquer patch, preserve campos e escolhas já editados por humano fora do alvo determinístico
fechado. Mudança de código ou prompt fica em worktree própria, recebe testes e só alcança runtime
pelo fluxo `git → merge → apply`; a pré-aprovação não autoriza essas etapas.
