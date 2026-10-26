---
description: Gera a música de fundo do Reel (ElevenLabs), mistura sob a voz e entrega as opções para o Carlos ouvir
argument-hint: <slug> [clima] | escolher <slug> <N>
---

Chame o agente **`produtor-musical`** com `$ARGUMENTS`.

1. Ler o roteiro e definir o clima (ou usar o que o Carlos disse).
2. `uv run python scripts/gerar_musica.py gerar <slug> --clima "..." --n 2`
3. `uv run python scripts/gerar_musica.py mixar <slug> --opcao N` para cada opção → `edicao/final-musica-N.mp4`.
4. Medir (−14 LUFS, TP ≤ −1,5) e mandar as versões ao Carlos para ouvir.
5. Quando ele escolher: `gerar_musica.py escolher <slug> <N>` — o `/renderizar` passa a usar `--musica` com essa faixa.

Sem `ELEVENLABS_API_KEY` o script para e diz: peça ao Carlos para pôr a chave no `.env` (nunca abrir o `.env`).
