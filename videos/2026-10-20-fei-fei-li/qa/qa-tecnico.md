## QA técnico — `final.mp4`

Resultado: **PASS** · 2026-10-17T05:30:37+00:00

| Check | Valor | Esperado | Status |
|---|---|---|---|
| Resolução | 1080×1920 | 1080×1920 | PASS |
| FPS | 25.0 | 25 ±0,01 (FPS_PROJETO) | PASS |
| Codec vídeo | h264 | h264 | PASS |
| Perfil H.264 | High | High | PASS |
| Pixel format | yuv420p | yuv420p (8-bit) | PASS |
| Cor (tags) | bt709/bt709/bt709 | bt709/bt709/bt709 | PASS |
| Codec áudio | aac | aac | PASS |
| Sample rate | 48000 | 48000 | PASS |
| Duração | 168.49s | 3–180 s | PASS |
| Faststart (moov antes do mdat) | ftyp > moov > free > mdat | moov antes de mdat | PASS |
| Tamanho | 189.8 MB | ≤ 300 MB | PASS |
| Bitrate | 9.45 Mbps | ≤ 25 Mbps | PASS |
| Loudness integrada | -14.2 LUFS | −14 ±1 LUFS | PASS |
| True peak | -1.7 dBTP | ≤ −1,5 dBTP | PASS |
| Trechos pretos (≥0,5 s) | 0 | 0 (revisar se houver) | PASS |
| Congelados (≥2 s) | 0 | 0 (ok se cartela estática) | PASS |
| Duração vs EDL | 168.49 vs 168.44 | ±0,2 s | PASS |
| Cenas extras (nenhuma faltando) | 30 ok | 0 faltando (placeholder no vídeo) | PASS |
| Legendas vs roteiro | 35 | 0 divergências | WARN |

### Pretos / congelados
- congelado a partir de 72.28s (0.56s) — ok se for cartela/animação estática?
- congelado a partir de 106.68s (0.64s) — ok se for cartela/animação estática?
- congelado a partir de 109.28s (0.52s) — ok se for cartela/animação estática?
- congelado a partir de 111.20s (0.68s) — ok se for cartela/animação estática?
- congelado a partir de 112.32s (0.56s) — ok se for cartela/animação estática?
- congelado a partir de 113.76s (0.56s) — ok se for cartela/animação estática?
- congelado a partir de 114.76s (0.68s) — ok se for cartela/animação estática?

### Legendas vs roteiro
- L04 · replace: roteiro «aos» → legenda «nos»
- L04 · insert: roteiro «» → legenda «e»
- L06 · replace: roteiro «quem» → legenda «ela»
- L06 · replace: roteiro «o telefone, resolvia cobrança» → legenda «os telefones e fazia as cobranças»
- L06 · replace: roteiro «falava com o fiscal?» → legenda «atendia os fiscais»
- L08 · replace: roteiro «conta,» → legenda «contou»
- L08 · insert: roteiro «» → legenda «foi assim que ela»
- L08 · replace: roteiro «a faculdade.» → legenda «as faculdades»
- L09 · replace: roteiro «depois» → legenda «foi aí que ela»
- L10 · insert: roteiro «» → legenda «a partir daí»
- L10 · replace: roteiro «numa» → legenda «em uma»
- L12 · insert: roteiro «» → legenda «que»
- L12 · replace: roteiro «seria» → legenda «deveria ser»
- L14 · replace: roteiro «dizer ao» → legenda «passar para o»
- L14 · insert: roteiro «» → legenda «reconhecer»
- L14 · delete: roteiro «o que aparecia em» → legenda «»
- L15 · delete: roteiro «quase» → legenda «»
- L15 · delete: roteiro «ajudaram» → legenda «»
- L15 · insert: roteiro «» → legenda «ajudaram»
- L15 · replace: roteiro «essas» → legenda «cada uma dessas»
- L21 · insert: roteiro «» → legenda «no meu canal»
- L22 · replace: roteiro «aos concorrentes que aquele» → legenda «ao concorrente e naquele»
- L22 · replace: roteiro «ajudou» → legenda «começou»
- L23 · insert: roteiro «» → legenda «só»
- L26 · insert: roteiro «» → legenda «a»
- L26 · replace: roteiro «de» → legenda «da»
- L28 · replace: roteiro «IA» → legenda «A inteligência artificial»
- L29 · delete: roteiro «mostrar exemplos,» → legenda «»
- L29 · replace: roteiro «informação e» → legenda «informações»
- L31 · replace: roteiro «a» → legenda «sua»
- L32 · delete: roteiro «que» → legenda «»
- L32 · replace: roteiro «mando» → legenda «envio no seu direct uma entrevista completa sobre»
- L32 · replace: roteiro «palestra dela.» → legenda «Fei-Fei Li»
- L33 · insert: roteiro «» → legenda «somente»
- L33 · insert: roteiro «» → legenda «a»

### Frames para revisão visual
- `/Users/teste/Documents/CONTENT AI/videos/2026-10-20-fei-fei-li/qa/frames/qa-01-007.0s.jpg`
- `/Users/teste/Documents/CONTENT AI/videos/2026-10-20-fei-fei-li/qa/frames/qa-02-021.1s.jpg`
- `/Users/teste/Documents/CONTENT AI/videos/2026-10-20-fei-fei-li/qa/frames/qa-03-035.1s.jpg`
- `/Users/teste/Documents/CONTENT AI/videos/2026-10-20-fei-fei-li/qa/frames/qa-04-049.1s.jpg`
- `/Users/teste/Documents/CONTENT AI/videos/2026-10-20-fei-fei-li/qa/frames/qa-05-063.2s.jpg`
- `/Users/teste/Documents/CONTENT AI/videos/2026-10-20-fei-fei-li/qa/frames/qa-06-077.2s.jpg`
- `/Users/teste/Documents/CONTENT AI/videos/2026-10-20-fei-fei-li/qa/frames/qa-07-091.3s.jpg`
- `/Users/teste/Documents/CONTENT AI/videos/2026-10-20-fei-fei-li/qa/frames/qa-08-105.3s.jpg`
- `/Users/teste/Documents/CONTENT AI/videos/2026-10-20-fei-fei-li/qa/frames/qa-09-119.3s.jpg`
- `/Users/teste/Documents/CONTENT AI/videos/2026-10-20-fei-fei-li/qa/frames/qa-10-133.4s.jpg`
- `/Users/teste/Documents/CONTENT AI/videos/2026-10-20-fei-fei-li/qa/frames/qa-11-147.4s.jpg`
- `/Users/teste/Documents/CONTENT AI/videos/2026-10-20-fei-fei-li/qa/frames/qa-12-161.5s.jpg`
