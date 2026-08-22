---
name: preaprovar-processos-administrativos
description: Auditar em modo somente leitura os processos administrativos do oli-indexer, aplicando a régua comum e regras próprias dos perfis fiscal, creditório e regulatório. Use antes da aprovação humana para conferir rito, classificação, análises, resumos, dossiês e argumentos; nunca aprova o job nem chama LLM ou reprocessa sem autorização específica.
---

# Pré-aprovar processos administrativos

Esta skill incorpora e preserva a experiência da skill administrativa anterior dentro do plugin comum.

Use `$preaprovar-indexacoes` para o protocolo compartilhado, leia [references/checklist.md](references/checklist.md) e use `$inspecionar-configuracao-indexacao` para confirmar taxonomia, prompt, grafo, dispatch, analyzer e schema atuais. As regras desta skill são adicionais às regras comuns.

## Escopo

- Perfis: `tributario/administrativo_fiscal`, `administrativo_creditorio` e `administrativo_regulatorio`. Não decida pelo formato do número do processo.
- Sem job/CNJ explícito, liste todos os jobs desses perfis em `awaiting_approval`, ainda não aprovados, e informe a quantidade.
- Não misture rito judicial e administrativo. Resolva o órgão, ator e efeito segundo o perfil exato.

## Parecer

Use os estados e a cobertura de `$preaprovar-indexacoes`. `APTO` exige protocolo comum integral e checklist administrativa integral. Em dúvida real, preserve o dado e emita `REVISÃO NECESSÁRIA` com linha, folhas, evidência e pergunta objetiva.

O diagnóstico `scripts/backfill/corrigir_analises_faltantes.py` pode ser executado sem `--execute`, limitado aos CNJs/jobs auditados, para enumerar análises ausentes ou divergentes. O dry-run informa chamadas planejadas; ele não autoriza executá-las nem representa custo já incorrido.

## Correções

Pré-aprovação não autoriza aplicar correção. Quando a fonte correta existe, modele a proposta
no contrato compartilhado e publique-a para revisão no app, preservando edições humanas.
Snapshot/readback e repetição dos gates pertencem ao runner após aprovação explícita.
Mudanças de código ou prompt ficam em worktree e alterações publicadas seguem o fluxo
git → merge → apply.
