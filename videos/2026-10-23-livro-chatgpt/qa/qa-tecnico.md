## QA técnico — `final-L01C.mp4`

Resultado: **PASS** · 2026-10-21T19:18:29+00:00

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
| Duração | 34.82s | 3–180 s | PASS |
| Faststart (moov antes do mdat) | ftyp > moov > free > mdat | moov antes de mdat | PASS |
| Tamanho | 51.4 MB | ≤ 300 MB | PASS |
| Bitrate | 12.38 Mbps | ≤ 25 Mbps | PASS |
| Loudness integrada | -14.1 LUFS | −14 ±1 LUFS | PASS |
| True peak | -1.7 dBTP | ≤ −1,5 dBTP | PASS |
| Trechos pretos (≥0,5 s) | 0 | 0 (revisar se houver) | PASS |
| Congelados (≥2 s) | 0 | 0 (ok se cartela estática) | PASS |
| Duração vs EDL | 34.82 vs 34.44 | ±0,2 s | WARN |
| Cenas extras (nenhuma faltando) | 11 ok | 0 faltando (placeholder no vídeo) | PASS |
| Legendas vs roteiro | 0 | 0 divergências | PASS |

### Pretos / congelados
- nenhum trecho detectado

### Legendas vs roteiro
- sem divergências
