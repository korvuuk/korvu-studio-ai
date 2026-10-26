---
name: audio-polish
description: Acabamento de áudio dos Reels — master da voz sem esmagar (nivelador leve 1,5:1 → ganho linear até −14 LUFS → limitador de true peak −1,5 dBTP com sobreamostragem 4×), a partir do áudio SEM PERDAS do corte (corte-audio.wav), trilha musical com ducking automático sob a voz (sidechain) e medição de LUFS/true peak/crest/energia por banda para o QA. Use no fim do /renderizar (depois do Remotion, antes do QA final), quando pedirem para ajustar volume, voz abafada ou "apertada", colocar música de fundo, "abaixar a música quando eu falo", ou para medir o loudness de um vídeo.
---

# Audio polish

Script: `.claude/skills/audio-polish/scripts/audio.py` (ffmpeg de `FFMPEG_BIN`). O vídeo nunca é reencodado
(`-c:v copy`): fps (25, `FPS_PROJETO`), pix_fmt e cor saem exatamente como vieram (Remotion ou colorista). A voz é
sempre a do vídeo principal (cenas extras entram mudas no Remotion, salvo `som: true`).

**Caminho sem perdas:** ingest → `edicao/audio48k/<fonte>.wav` (24-bit, só passa-altas 60 Hz) → `render_corte` →
`edicao/corte-audio.wav` (24-bit) → **aqui** → AAC 256k. O `audio.py` pega o vídeo da entrada e o **áudio do
`corte-audio.wav`** (procurado na pasta `edicao/` acima da entrada; só se a duração bater com a do vídeo) — o único
encode com perdas é o AAC final. Sem ele (ou `--sem-master`, ou EDL com extra `som: true`) usa o áudio da entrada.

```bash
cd "/Users/teste/Documents/CONTENT AI"
A=".claude/skills/audio-polish/scripts/audio.py"
V="videos/<slug>"
```

## Masterizar (padrão do Reel)
```bash
uv run python "$A" "$V/edicao/render-remotion.mp4" "$V/edicao/final.mp4"          # master automático
uv run python "$A" "$V/edicao/cor/corte-cor.mp4" "$V/edicao/revisao.mp4"          # revisão sem gráficos
uv run python "$A" in.mp4 out.mp4 --audio-master "$V/edicao/corte-audio.wav"      # master explícito
```
Cadeia (nenhum EQ — a voz sai com o timbre da câmera):
1. mede o **RMS da fala** (quadros de 20 ms com fala) e o piso;
2. `acompressor` **leve 1,5:1**, limiar = RMS da fala **+ 9 dB**, ataque 30 ms, release 300 ms, joelho suave (~9 dB),
   detecção RMS — só nivela frases que saltam. Medido na voz do Carlos: 2:1 com limiar no RMS da fala (10/150 ms)
   inclinava +2,9 dB em 5–10 kHz (abaixa as vogais altas, as sibilantes ficam = "chiado") **sem ganhar crest**;
   quem controla os picos é o limitador (crest 17,8 → ~14,2 dB);
3. **ganho linear** até **−14 LUFS** integrado (medido depois da compressão);
4. `alimiter` a **192 kHz** (4× = true peak), teto = −1,5 − 0,5 dBTP, lookahead compensado (`latency=1`, sem atraso);
5. AAC 256k, voz mono nos 2 canais. Mede a saída e corrige ganho/teto (até 4 passadas): −14 ±0,3 LUFS, TP ≤ −1,5.

Imprime o crest da fala antes/depois (esmagamento = crest caindo muito; alvo ≥ 13 dB). O `loudnorm` só é usado como
**medidor** (o modo "dynamic" dele comprimia a voz: crest 17,8 → 14,8 dB na revisão v2).
Opções: `--razao` (1.5; 1 = sem compressor), `--limiar` (+9 dB acima do RMS da fala), `--ataque` (30 ms),
`--release` (300 ms), `--lufs` (−14), `--tp` (−1,5). Mais compressão = mais "denso", mas confira o timbre com
`--medir --trecho` (agudos ±1,5 dB do bruto).

## Com música (ducking)
```bash
uv run python "$A" "$V/edicao/render-remotion.mp4" "$V/edicao/final.mp4" \
    --musica "00-marca/musicas/<faixa>.mp3" --musica-db -22
```
Música em loop, volume `--musica-db` (padrão −22 dB), `sidechaincompress` com a voz (comprimida) como sidechain
(`threshold=0.05:ratio=8:attack=20:release=300`), fade-out de 1,5 s, `amix` — antes do ganho e do limitador.
Registre em `edl.json.audio.musica` o arquivo usado. Só use música com licença para uso comercial.

## Medir (QA)
```bash
uv run python "$A" --medir "$V/edicao/final.mp4"                    # LUFS integrado | True peak | LRA
uv run python "$A" --medir "$V/edicao/final.mp4" --json             # {"lufs": -14.0, "true_peak": -1.6, "lra": 4.2}
uv run python "$A" --medir "$V/edicao/final.mp4" --trecho 6.9 10.6  # + crest e energia por banda (dB rel. 60 Hz–16 kHz)
```
Critério do QA: LUFS −14 ± 1, true peak ≤ −1,5 dBTP. Voz "abafada" = bandas 2–5k / 5–10k / 10–16k bem abaixo das do
bruto da câmera no mesmo trecho (compare com `--trecho` no `.MOV`); o alvo é ±1,5 dB.

## Opções
`--limpar` aplica redução de ruído **suave** (passa-altas 60 Hz + `afftdn=nr=8` com o piso medido) antes de tudo —
só se o ruído incomodar de verdade (tira um pouco de brilho). A ingestão não faz mais redução de ruído (o
`afftdn=nf=-25` antigo tirava ~10 dB dos agudos); para limpar na origem: `ingest.py --limpar-ruido`.

## Troubleshooting
- **"não achei a saída JSON do loudnorm"** → arquivo sem áudio ou corrompido; confira com `ffprobe`.
- **"corte-audio.wav tem X s e o vídeo Y s"** → o corte foi re-renderizado depois da cor/Remotion (ou vice-versa):
  refaça as etapas na ordem, ou passe `--sem-master`.
- **Voz "bombeando"** → `--release 500`; **pouco controle / frases muito desiguais** → `--razao 2 --limiar 6`
  (confira crest ≥ 13 dB e os agudos com `--medir --trecho`).
- **Música some demais / pouco** → ajuste `--musica-db` (−18 mais presente, −26 mais discreta).
- **Duração muda** → o áudio é cortado/completado na duração do vídeo (`-t`, `apad`); a música nunca estende o vídeo.
