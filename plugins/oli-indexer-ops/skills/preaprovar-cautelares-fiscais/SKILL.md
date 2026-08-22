---
name: preaprovar-cautelares-fiscais
description: Auditar em modo somente leitura medidas cautelares fiscais do perfil tributario/cautelar_fiscal no oli-indexer. Use antes da aprovação humana para conferir crédito, requisitos da Lei 8.397/1992, indisponibilidade, responsáveis, conexão com execução fiscal, substituição/liberação, sentença e recursos; nunca aprova, corrige, chama LLM ou reprocessa sem autorização específica.
---

# Pré-aprovar cautelares fiscais

Use somente para `tributario/cautelar_fiscal`. Leia
[references/checklist.md](references/checklist.md) e componha-a com
`$preaprovar-indexacoes` e `$consultar-oli-indexer`.

A cautelar fiscal é preventiva e não se confunde com a execução fiscal relacionada. Preserve
o alcance subjetivo e patrimonial de cada decisão e revise integralmente os atos críticos.

A saída segue `review-report/v1`; patch é apenas proposta determinística e versionada. Não
aplique patch nem aprove o job.
