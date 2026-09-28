# Perda semântica na consolidação

## Sinal

Mover checklists para referências preserva o conteúdo principal, mas pode deixar nos wrappers
removidos regras pequenas e decisivas: fallback proibitivo, comando de script, interpretação de
exit code ou limite de autoridade.

## Tratamento atual

Antes de remover um wrapper, compare separadamente `SKILL.md`, referências e scripts. Toda regra
de roteamento, segurança ou escalonamento precisa ficar alcançável a partir da skill pública; não
basta mover a checklist. A validação independente deve exercitar também casos limítrofes, não só
links e testes existentes.

## Evidência desta proposta

A primeira candidata perdeu quatro freios: natureza judicial não coberta, checker de prescrição,
falha sistêmica de compactação e proibição de OCR/Vision/materialização sem autorização. Uma
auditoria posterior reabriu a proposta e encontrou regras menores ainda presas aos wrappers,
inclusive identidade exata de perfis, limites de aprovação e backfill legado. A sucessora híbrida
recolocou essas regras nas fontes canônicas e restaurou nove aliases explícitos sem duplicar o
conteúdo.
