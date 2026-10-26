---
description: QA final e montagem do pacote do vídeo em 05-render-pronto/<slug>/
argument-hint: <slug> [--capa capa-B.png]
---

Para **$ARGUMENTS**:
1. `uv run python scripts/portoes.py estado videos/<slug>`: portão vencido/pendente → rodar o portão dessa área (corte → **revisor-de-video** passagem 2; imagem → **portao-imagem**; roteiro → **revisor-de-roteiro**; pauta → **portao-pauta**) (GAUNTLET, `docs/gauntlet.md`: roda sozinho, sem perguntar; BLOQUEADO → o construtor corrige os S0/S1 e volta ao mesmo portão, até 3 voltas; nada chega ao Carlos antes do APROVADO).
2. `uv run python scripts/montar_pacote.py videos/<slug> [--capa …]`.
   O pacote leva **só o PDF** de `material/` (+ `cta_palavra` e `material_titulo` no `pacote.json`); dossiê, `fontes.json`, `obra*` e `_fonte/` ficam em `videos/` — o `publicar.py` sobe o material para o R2 público (`docs/contratos.md` §1a).
3. Se o CTA é de palavra-chave e o script recusar por falta de PDF: usar o subagente **produtor-de-material** (gera `material/<arquivo>.pdf` a partir do roteiro) e montar de novo. Mais de um PDF em `material/` → `--material nome.pdf`.
4. Atualizar estado `pronto` e mostrar o conteúdo do pacote.
