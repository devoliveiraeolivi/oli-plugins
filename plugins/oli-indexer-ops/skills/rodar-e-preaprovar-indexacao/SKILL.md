---
name: rodar-e-preaprovar-indexacao
description: Alias explícito de compatibilidade para o fluxo diário do oli-indexer. Use somente quando o usuário invocar $rodar-e-preaprovar-indexacao; encaminhe integralmente para a skill canônica de orquestração, sem ampliar autoridade nem concluir ou aprovar jobs.
---

# Rodar e pré-aprovar indexação

Este nome permanece apenas para compatibilidade. Leia e siga
[`orquestrar-indexacoes`](../orquestrar-indexacoes/SKILL.md), incluindo seu
[workflow](../orquestrar-indexacoes/references/workflow.md) e contrato de
[intenção](../orquestrar-indexacoes/references/intent.md).

Não mantenha regras paralelas neste alias. A invocação explícita não acrescenta
autoridade: Approval, Conclusion, recall, delete, reprocessamento e ampliação de
escopo continuam sujeitos aos gates da skill canônica.
