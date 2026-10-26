# Amostras de calibração do LUT — PRAQ0967

Os 20 quadros em que os looks `korvu-look-v1…v5` (`00-marca/cor/luts/`) foram medidos — campo `amostra.frames` dos
JSON —, tirados de `videos/2026-09-16-chatgpt-contexto/brutos/(principal|_nao-usar)/PRAQ0967.MOV` antes de o vídeo-teste
ser apagado na limpeza de 23/10/2026 (`_controle/limpeza-2026-10-23.md`).

- Um quadro por arquivo, nome = o tempo do JSON (`praq0967-25.61s.mkv` …).
- **Sem perdas**: FFV1, 4096×2160, `yuv422p10le`, **full range** (V-Log 0–1023), metadado de rotação −90 preservado.
  Conferido quadro a quadro: o framemd5 de cada `.mkv` é igual ao do quadro decodificado do MOV original
  (ler sempre com `-noautorotate`, senão o hash muda por causa do giro).
- Para medir de novo: usar estes arquivos no lugar do MOV, com a mesma `transformacao_entrada` do JSON
  (V-Log → Rec.709 por `00-marca/cor/luts/entrada-camera.cube`).
