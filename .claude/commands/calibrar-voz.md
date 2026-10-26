---
description: Aprende o jeito de falar do Carlos a partir de vídeos-amostra e atualiza 00-marca/voz-carlos.md
argument-hint: [arquivo(s) em 02-calibracao/amostras/]
---

Amostras: "$ARGUMENTS" (vazio = todos os arquivos de `02-calibracao/amostras/`). Ideal: 3–5 min falando livre sobre IA/negócios + 1 min lendo um roteiro (arquivo com "leitura" no nome).

1. Transcrever cada amostra com a skill `corte-por-roteiro` (mesmo formato `transcricao.json`), salvando em `02-calibracao/analises/<arquivo>.transcricao.json`. Se não houver `ELEVENLABS_API_KEY`, usar `--engine mlx`.
2. `uv run python .claude/skills/roteiro-reels/scripts/voice_stats.py <livres…> [--leitura <leitura>]`.
   **Com gravação real já editada** (o melhor material — decisão do Carlos, 17/10: "tem que aprender como eu falo"): `uv run python .claude/skills/roteiro-reels/scripts/comparar_fala.py videos/<slug> > 02-calibracao/analises/<data>-<slug>-fala.md` — roteiro × dito linha a linha, trocas sistemáticas, ritmo nos takes da EDL, fala fora das linhas. Só palavras `locutor: carlos`.
3. Ler também as transcrições em si e anotar: como ele abre frases, como explica (analogias? exemplos?), expressões e bordões, vícios que devem sumir no roteiro, palavras que ele nunca usa, energia/ritmo.
4. Reescrever `00-marca/voz-carlos.md`: YAML (`status: calibrado`, `wps_roteiro`, `palavras_60s`, `muletas`, `expressoes`, `frase_media_palavras`, data) + seções "Como o Carlos fala", "Use", "Evite", "Exemplos reais (trechos curtos)".
5. Adicionar as muletas reais dele à lista de muletas do editor (`.claude/skills/corte-por-roteiro/references/algoritmo.md` / `common.py`, se houver lista configurável).
6. Mostrar o resumo ao Carlos e o novo tamanho padrão do roteiro de 60 s.
