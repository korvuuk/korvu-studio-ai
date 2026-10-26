## QA técnico — `final.mp4`

Resultado: **FAIL** · 2026-10-15T09:31:25+00:00

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
| Duração | 158.74s | 3–180 s | PASS |
| Faststart (moov antes do mdat) | ftyp > moov > free > mdat | moov antes de mdat | PASS |
| Tamanho | 163.5 MB | ≤ 300 MB | PASS |
| Bitrate | 8.64 Mbps | ≤ 25 Mbps | PASS |
| Loudness integrada | -14.1 LUFS | −14 ±1 LUFS | PASS |
| True peak | -1.9 dBTP | ≤ −1,5 dBTP | PASS |
| Trechos pretos (≥0,5 s) | 0 | 0 (revisar se houver) | PASS |
| Congelados (≥2 s) | 0 | 0 (ok se cartela estática) | PASS |
| Duração vs EDL | 158.74 vs 158.68 | ±0,2 s | PASS |
| Cenas extras (nenhuma faltando) | E01, E04, E06 faltando | 0 faltando (placeholder no vídeo) | FAIL |
| Legendas vs roteiro | 56 | 0 divergências | WARN |

### Pretos / congelados
- nenhum trecho detectado

### Legendas vs roteiro
- L01 · delete: roteiro «quase» → legenda «»
- L02 · replace: roteiro «dar» → legenda «dá»
- L03 · grafia: roteiro «Essa» → legenda «essa»
- L03 · replace: roteiro «de» → legenda «do»
- L04 · replace: roteiro «numa» → legenda «em uma»
- L05 · delete: roteiro «do» → legenda «»
- L05 · replace: roteiro «muita gente imagina,» → legenda «muitas pessoas imaginavam»
- L05 · replace: roteiro «estudando» → legenda «a estudar os»
- L06 · replace: roteiro «funciona» → legenda «funcionava»
- L07 · insert: roteiro «» → legenda «ele»
- L07 · delete: roteiro «naquela época:» → legenda «»
- L08 · replace: roteiro «conseguisse criar máquinas capazes de aprender como o cérebro humano?» → legenda «criasse uma máquina que consegue imitar a mente humana»
- L09 · insert: roteiro «» → legenda «Só que»
- L09 · grafia: roteiro «O» → legenda «o»
- L09 · delete: roteiro «é que» → legenda «»
- L09 · replace: roteiro «nisso.» → legenda «nessa ideia»
- L10 · replace: roteiro «Até» → legenda «O mais curioso»
- L10 · replace: roteiro «que abandonasse» → legenda «ele a abandonar»
- L10 · replace: roteiro «poderia destruir sua» → legenda «essa pesquisa pode comprometer a»
- L10 · insert: roteiro «» → legenda «dele»
- L11 · replace: roteiro «Mas Hinton» → legenda «Como o cara é fera ele simplesmente»
- L12 · replace: roteiro «junto» → legenda «ele juntou»
- L13 · grafia: roteiro «ele» → legenda «Ele»
- L13 · replace: roteiro «imagens com uma precisão impressionante.» → legenda «imagem de forma precisa e impecável»
- L14 · replace: roteiro «Aquilo mudou completamente» → legenda «Foi aí que ele acabou de mudar»
- L15 · replace: roteiro «comprou» → legenda «acabou de comprar»
- L15 · replace: roteiro «tinham criado.» → legenda «acabaram de criar»
- L16 · insert: roteiro «» → legenda «o»
- L16 · insert: roteiro «» → legenda «mais de»
- L16 · insert: roteiro «» → legenda «junto»
- L16 · replace: roteiro «a gigante» → legenda «gigantes»
- L17 · replace: roteiro «Mas» → legenda «Agora»
- L17 · insert: roteiro «» → legenda «só»
- L18 · replace: roteiro «deixou» → legenda «acabou deixando»
- L19 · grafia: roteiro «para» → legenda «Para»
- L20 · insert: roteiro «» → legenda «ele»
- L20 · insert: roteiro «» → legenda «e meia»
- L21 · insert: roteiro «» → legenda «E a ligação»
- L21 · grafia: roteiro «Era» → legenda «era»
- L22 · replace: roteiro «ganhar o» → legenda «ganhado um»
