---
name: preaprovar-embargos-execucao-fiscal
description: Auditar em modo somente leitura Embargos à Execução Fiscal tributários do perfil tributario/conhecimento no oli-indexer. Use antes da aprovação humana para conferir execução de origem, CDA e garantia, tempestividade, efeito suspensivo, apensamento, provas, sentença, recursos, traslados e análises; nunca aprova, corrige, chama LLM ou reprocessa sem autorização específica.
---

# Pré-aprovar embargos à execução fiscal

Use esta régua somente para `tributario/conhecimento` com natureza
`Embargos à Execução Fiscal`. Leia [references/checklist.md](references/checklist.md) por
inteiro e componha-a com `$preaprovar-indexacoes` e `$consultar-oli-indexer`.

Embargos são uma ação de conhecimento autônoma ligada à execução fiscal. Preserve a
identidade e o efeito de cada processo: peça meramente copiada continua documental; decisão
proferida fora, mas trasladada com eficácia nestes autos, continua ato de Julgador.

Revise integralmente os atos críticos da checklist e todas as relações processuais. Não
converta reunião, apensamento, traslado e comunicação em sinônimos. A decisão que manda
apensar, a certidão que materializa e a comunicação posterior são atos diferentes.

A saída segue `review-report/v1`; patch é apenas proposta determinística e versionada. Não
aplique patch nem aprove o job.
