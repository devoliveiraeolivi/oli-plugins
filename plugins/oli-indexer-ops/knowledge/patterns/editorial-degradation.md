# Degradação editorial em campos humanos

## Sinal observado

Um parecer juridicamente correto foi publicado com palavras sem acentuação — por exemplo,
`favoravel`, `copia`, `apos` e `sentenca` — em campos exibidos diretamente na UI. A mesma classe
de defeito pode aparecer dentro de análises persistidas, como o valor humano `Nao enfrentado` em
`julgamento_argumentos`.

## Causa

O agente tratou texto humano como se precisasse ser limitado a ASCII por estar dentro de JSON.
Essa restrição não existe: o contrato e o control plane preservam UTF-8. A simplificação não reduz
tokens ou risco de serialização de forma relevante e degrada legibilidade, credibilidade e
qualidade jurídica.

## Regra reutilizável

- Campos narrativos, explicativos e rótulos humanos de relatórios, indexações, análises horizontais
  e verticais devem usar português do Brasil com ortografia, acentuação, concordância, pontuação e
  terminologia jurídica corretas.
- Identificadores, códigos, hashes, enums e valores técnicos permanecem literais.
- Antes de alterar um valor que pareça enum, confira schema, prompt e consumidores: um literal
  técnico sem diacrítico não é corrigido como se fosse texto de UI.
- A revisão editorial ocorre antes da publicação e não exige chamada LLM separada.
- Se o defeito estiver apenas no relatório, publique sucessor imutável por CAS e não crie patch de
  DATA. Se estiver no dado canônico, use somente o patch determinístico tipado aplicável, com CAS,
  dependências e readback; não edite tabela nem reprocesse por conveniência.

## Validação

Revise os campos humanos completos no documento final e nas análises do escopo, não apenas o
trecho que revelou o erro.
Evite um dicionário rígido de palavras sem acento: ele produziria falsos positivos e não avaliaria
concordância ou contexto. A evidência observável é o próprio relatório renderizado e o readback do
documento persistido.
