---
name: preaprovar-extracoes
description: Auditar e fechar o gate pós-Extraction antes da Indexing, distinguindo fonte PDF, extração de texto, backlog certificado e metadado técnico. A primeira passada é somente leitura; escrita exige runtime 0141/0142 comprovado e limita-se ao reparo PyMuPDF allowlisted com CAS, orçamento e readback. Nunca aprova o job, chama LLM/OCR/Vision ou troca a fonte.
---

# Pré-aprovar extrações

Audite a fonte técnica que alimentará a Indexing. Este gate valida PDF,
cobertura, proveniência e texto extraído; classificação jurídica, relações e
fronteiras de peças pertencem aos gates seguintes.

Antes de agir, leia [references/protocolo.md](references/protocolo.md). Use
`$consultar-oli-indexer` para a fotografia OPS/DATA. A primeira passada é sempre
somente leitura.

## Gate de capacidade

Não presuma que código local ou migration pendente existe no runtime. Antes de
qualquer escrita, exija prova conjunta do worker compatível, da migration DATA
`0141_extraction_treatment_budget_data`, da migration OPS
`0142_extraction_gate_fencing_ops` e dos respectivos smokes/readbacks.

Se faltar qualquer prova, conclua a auditoria em modo leitura e devolva
`BLOQUEADO_POR_CAPACIDADE`. Não use RPC v1, release/start separados, SQL livre
ou outro fallback para contornar o gate.

## Quatro classes

Classifique cada finding em exatamente uma classe:

- `source_pdf`: bytes, `%PDF`/`%%EOF`, multipart, contagem, identidade ou fonte
  divergente; tratamento `source_blocker`.
- `text_extraction`: página ausente/vazia, texto curto/duplicado ou camada
  nativa ausente; só a allowlist literal pode autorizar reparo.
- `normal_backlog`: compactação certificada ou prova de base legitimamente à
  frente; sem prova, trate como ausência material.
- `technical_metadata`: cardinalidade, intervalo, owner ou proveniência
  inconsistentes; nunca inferir mutação destrutiva.

## Allowlist e orçamento

A única operação automática é:

```text
page.native_text.repair/v1
engine=pymupdf
same_frozen_pdf_bytes=true
max_successful_mutations=1 por (job_id, source_digest, página, tratamento)
```

Ela só preenche `texto_pymupdf` nulo. Exija patch tipado, head corrente,
`expected_updated_at`, hashes de texto/PDF, cardinalidade 1,
`mutation_started_at` imediatamente antes da RPC DATA, ledger/readback e série
sucessora. Uma segunda run é permitida somente se a primeira falhou antes da
marca e deve citar `retry_of_run_id`; depois da marca, sucesso ou falha esgota o
orçamento automático.

OCR/Vision exige autorização e orçamento separados. LLM, reviewer, fonte/PDF
novo ou reconstruído, recall, delete, reextração ampla, migration, deploy e
Indexing não entram nessa autoridade.

## Autoridade e saída

Com capacidade comprovada, o pedido explícito de pré-aprovação autoriza salvar
o parecer, aplicar somente o reparo allowlisted, verificar, reauditar e aceitar
tecnicamente um sucessor `fit|fit_with_notes` fresco. Anuncie cada escrita. Não
altere `approved_at`/`approved_by` e não aprove/conclua o job.

O aceite só torna o job elegível ao claim. O worker recaptura a fonte e chama
`begin_extraction_indexing`, que valida série, head, checkpoint, report, lease,
runs, patches e mutações antes de gravar release + início numa transação OPS.

Relate separadamente: capacidade/runtime; série/head; findings e evidência;
patches/tentativas/readbacks; custo externo e LLM zero; estado da Indexing; e
aprovação humana final pendente.

Se não houver canário inequívoco, apresente candidatos exatos e peça escolha.
Nunca escolha um job produtivo por posição na fila.
