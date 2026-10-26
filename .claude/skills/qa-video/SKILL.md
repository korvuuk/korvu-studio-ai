---
name: qa-video
description: QA final do Reel antes de ir para 05-render-pronto — specs técnicas (1080×1920, 30 fps, H.264 High, AAC 48 kHz, faststart, bitrate), loudness (−14 LUFS / −1,5 dBTP), pretos/congelados, grafia das legendas vs roteiro, zonas seguras e revisão visual de frames. Use no estado "qa" ou sempre que precisar validar um MP4 para Instagram/Facebook.
---

# QA do vídeo (revisor)

O QA tem duas partes: **automática** (script) e **visual** (você, olhando frames). Só dá PASS se as duas passarem.
Relatório final: `videos/<slug>/qa/qa-relatorio.md` (vai para o pacote como `qa-relatorio.md`).

## 1. Checagem automática
```bash
uv run python .claude/skills/qa-video/scripts/qa_check.py videos/<slug>/edicao/video-final.mp4 \
    --video_dir videos/<slug> --frames 12
```
Gera `qa/qa-tecnico.json` + `qa/qa-tecnico.md` (seção PT-BR para colar no relatório) e `qa/frames/*.jpg`.
Sai com código 1 se houver FAIL.

| Check | Regra | Falha = |
|---|---|---|
| Resolução | 1080×1920 | FAIL |
| FPS | `FPS_PROJETO` ±0,01 (padrão **25**, Lumix S5IIX; `--fps` sobrescreve) | FAIL |
| Vídeo | H.264 perfil High, yuv420p (8-bit — os intermediários 10-bit 4:2:2 não servem para postar) | FAIL |
| Cor (tags) | bt709 / bt709 / bt709 | WARN |
| Cenas extras | nenhum overlay `tipo: extra` com `faltando` (edl.json / reel-props.json) | FAIL |
| Áudio | AAC 48 kHz | FAIL |
| Duração | 3–180 s (e ±0,2 s da `edl.duracao_saida`, aviso) | FAIL |
| Faststart | átomo `moov` antes do `mdat` | FAIL |
| Tamanho / bitrate | ≤ 300 MB · ≤ 25 Mbps | FAIL |
| Loudness | integrada −14 ±1 LUFS; true peak ≤ −1,5 dBTP (ebur128) | FAIL |
| Pretos ≥ 0,5 s / congelados ≥ 2 s | blackdetect / freezedetect | WARN (revisar: cartela estática é ok) |
| Legendas vs roteiro | grafia/palavras diferentes da FALA | WARN (corrigir se for erro) |

`render-remotion.mp4` sai **antes** do loudnorm — é normal falhar loudness nele; rode o QA no arquivo final.
Extra FALTANDO = placeholder "EXTRA Exx FALTANDO" no vídeo: peça o arquivo ao Carlos; quando chegar,
`ingest.py` + `edl.py --recalcular` + `gerar_props.py` + `render_reel.py` + `audio.py` e rode o QA de novo.

## 2. Diferenças do corte (`diff.md`)
Leia o `diff.md` gerado pela verificação (verify) do editor (`videos/<slug>/edicao/diff.md`, se existir):
- toda linha do roteiro presente no corte (nenhuma `faltando`), sem paráfrases não aprovadas;
- nenhum false start / recomeço / muleta que sobrou;
- cortes internos sem "pulo" de áudio audível.

## 3. Legendas
- Compare `edicao/legendas.json` com a FALA do `roteiro.json` (o script lista divergências).
- Nomes próprios e marcas com a grafia do roteiro (ChatGPT, Claude, Gemini…); PT-BR ("você", "tá", "pra").
- `destaque` só nas palavras marcadas `**assim**` no roteiro.
- Páginas de 2–4 palavras, sem palavra "órfã" no fim de frase, sem legenda durante o título do hook.

## 4. Zonas seguras (olhe os frames)
Leia os `qa/frames/*.jpg` (e extraia mais nos trechos de título, cartelas, telas e animações):
- Nada importante no topo (< 270 px), na base (> 1250 px, legenda do post e botões) nem nas laterais
  (< 65 px; direita < 120 px).
- Legendas entre y 1150–1250 (ou na costura do split) sem cobrir o rosto nem a tela.
- Título do hook legível: contexto + impacto (cinza→branco), realce de seleção com alças, rabisco na palavra-chave.
- Split: rosto enquadrado no painel de cima; tela legível embaixo.
- Nenhuma cartela "Animação Lxx · pendente" nem placeholder "EXTRA Exx FALTANDO" no vídeo final.
- Cenas extras: split com o rosto no painel de cima; full sem cortar o que importa; card legível; crédito
  "Fonte: X" visível nos extras de terceiros; imagem da câmera com cor (nada cinza/lavado de V-Log).

## 5. Assistir
Veja o vídeo inteiro pelo menos uma vez (filmstrip/frames ou `/watch` se instalado): sincronia das legendas,
punch-ins escondendo os jump cuts, transições, música sem briga com a voz, final sem corte seco.

## Resultado
Escreva em `qa/qa-relatorio.md`: seção automática (colar `qa-tecnico.md`) + itens 2–5 com ✅/❌ e ações.
**PASS** só se não houver FAIL e todos os itens visuais estiverem ok; atualize `status.json`/tracker.
