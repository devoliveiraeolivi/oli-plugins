---
name: preaprovar-conhecimento-tributario
description: Auditar em modo somente leitura ações tributárias judiciais do perfil tributario/conhecimento que não sejam restituição nem embargos à execução fiscal. Use antes da aprovação humana para ações anulatórias, declaratórias, mandados de segurança, produção antecipada de provas, suspensão de liminar/sentença e demais ritos expressamente cobertos; nunca aprova, corrige, chama LLM ou reprocessa sem autorização específica.
---

# Pré-aprovar conhecimento tributário

Use esta régua para `tributario/conhecimento`, exceto restituições e Embargos à Execução
Fiscal, que têm skills próprias. Leia [references/checklist.md](references/checklist.md) e
componha-a com `$preaprovar-indexacoes` e `$consultar-oli-indexer`.

Primeiro selecione a seção exata da natureza. Natureza não listada pode receber a auditoria
comum, mas não parecer `APTO` até existir uma checklist material explícita; registre a lacuna
de domínio. Não transporte automaticamente gates de MS, ação ordinária, produção de prova ou
suspensão entre si.

Revise integralmente todos os atos críticos aplicáveis e gere `review-report/v1`. Patch é
somente proposta determinística e versionada; não aplique patch nem aprove o job.
