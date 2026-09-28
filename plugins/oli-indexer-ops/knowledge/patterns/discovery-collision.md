# Colisão entre roteador e especializações

## Sinal

Várias skills de pré-aprovação descreviam o mesmo trabalho com o mesmo vocabulário: auditoria,
primeira passada somente leitura, patch determinístico e aprovação humana posterior. A régua comum
mandava carregar a especialização, e a especialização mandava carregar novamente a régua comum.

## Efeito provável

- disputa no gatilho implícito;
- descrições longas no catálogo inicial;
- carregamento repetido de instruções compartilhadas;
- risco de drift entre wrappers e protocolo comum.

## Tratamento atual

Manter uma única skill descoberta automaticamente para a pré-aprovação final. Perfis jurídicos e
camadas condicionais ficam em referências canônicas selecionadas pelo roteador. Aliases de
compatibilidade podem continuar públicos, mas somente por invocação explícita e sem regras,
scripts ou checklists próprios. Gates operacionais realmente distintos, como extração e insumos
da indexação, continuam skills automáticas próprias.

## Reabrir quando

Uma referência passar a representar pedido independente frequente, com autoridade, entrega ou
ferramentas próprias. Nesse caso, comparar a nova skill com a referência em casos de discovery
antes de promovê-la ao catálogo automático.
