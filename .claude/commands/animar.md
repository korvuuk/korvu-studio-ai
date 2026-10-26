---
description: Gera o brief para o Claude Design ou importa/sincroniza uma animação explicativa
argument-hint: <slug> [ID da linha, ex. L05]
---

Usar o subagente **animador** para: **$ARGUMENTS** (sem ID = todas as linhas com ANIMACAO).
- Se `videos/<slug>/animacoes/<ID>/export/` não existe ou está vazio → gerar/atualizar `brief.md` e mostrar ao Carlos o texto pronto para colar no Claude Design, com a instrução de onde salvar o export.
- Depois de portar/capturar: **PORTÃO-IMAGEM** (subagente **portao-imagem**) (GAUNTLET, `docs/gauntlet.md`: roda sozinho, sem perguntar; BLOQUEADO → o construtor corrige os S0/S1 e volta ao mesmo portão, até 3 voltas; nada chega ao Carlos antes do APROVADO).
- Se o export existe → portar para Remotion (preferido para animações simples) **ou**, quando for um export grande do Claude Design, capturar com `scripts/capturar_animacao.mjs` (§3 da skill) → `ingest.py` → `edl.py --recalcular` → `gerar_props.py`; registrar, renderizar prévia e mostrar.
- Antes de capturar, comparar a `TIMELINE` do export com os tempos reais do `edl.json`: cena esticada > 1,25× congela a tela, comprimida < 0,8× acelera a digitação. Fora disso, atualizar o brief com os tempos reais e pedir a regeneração ao Carlos.
