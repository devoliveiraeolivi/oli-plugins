# Critérios de validação

`discovery.jsonl` cobre somente a escolha da skill. Casos `mode: implicit` recebem as seis skills
automáticas e devem escolher o gate principal, nunca um alias ou a Conclusion. Casos
`mode: explicit` invocam um dos dez aliases de compatibilidade ou uma das duas skills operacionais
explicit-only (Conclusion e reconciliação pós-reaper).
Casos `expected_skill: null` verificam que o plugin não captura tarefas alheias ou pedidos que
excedem sua autoridade.

Ao rodar uma avaliação com modelo:

1. use uma cópia do plugin contendo apenas manifesto e `skills/`; no modo implícito, não exponha
   os aliases marcados com `allow_implicit_invocation: false`;
2. não exponha `knowledge/`, respostas esperadas ou histórico da proposta ao agente executor;
3. mantenha modelo, esforço, ferramentas e `AGENTS.md` iguais entre baseline e candidata;
4. repita casos não determinísticos antes de aceitar uma mudança;
5. rejeite qualquer regressão de autoridade, segredo, aprovação humana ou custo, mesmo se a taxa
   média de acerto melhorar.

Além da seleção, confirme que cada alias explícito lê o roteador comum e exatamente a referência ou
overlay aplicável. A presença do alias nunca transforma sua checklist em segunda fonte de verdade.

`extraction_gate.jsonl` é o contrato comportamental mínimo do gate pós-extração. Ele cobre
capacidade/versionamento, fonte, reparo, retry, stale head, backlog, handoff jurídico e escolha de
canário. Pode ser executado com snapshots sanitizados; enquanto fixtures reais não existirem, o
validador garante ao menos que toda revisão da skill preserve esses nove casos e os invariantes
literais. Não fabricar um benchmark grande antes de haver parecer humano suficiente.

`conclusion_gate.jsonl` fixa o contrato pós-aprovação: filtro estrito por `approved_at`, lease,
paridade do dry-run, execução serial, resposta incerta, novo gate humano, readback canônico e a
incompatibilidade de `--run-approved --reindex-only`. A skill continua explicit-only; os casos
comportamentais não concedem autorização para executar jobs reais.

`documentary_boundaries.jsonl` protege a fronteira entre processo, juntada, subato/arquivo e
conteúdo interno. `reaper_reconciliation.jsonl` cobre somente o fechamento contábil depois de
`ZOMBIE_NO_HEARTBEAT`, sem autorizar retry. `editorial_quality.jsonl` verifica português correto
nos campos humanos, preservação de literais técnicos e fidelidade UTF-8 no readback. Esses corpora
são pequenos de propósito e devem crescer por falhas reais, não por casos inventados em massa.
