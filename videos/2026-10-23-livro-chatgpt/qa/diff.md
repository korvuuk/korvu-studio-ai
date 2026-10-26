# QA do corte — 2026-10-23-livro-chatgpt

Vídeo: `edicao/corte.mp4` · engine scribe · 2026-10-21T18:35:28+01:00

**Resultado: FALHOU** — WER geral 16.0% > 8%

- WER geral: **16.0%** (limite 8%; 13 erros / 81 palavras esperadas)
- Duração: vídeo 34.440s · áudio 34.440s · soma das peças 34.440s · EDL 34.440s · alvo 35.0s (-2%)
- Sincronia A/V: OK (Δ 0.0 ms; tolerância 1 frame = 40.0 ms)
- Duração vs peças: OK (Δ 0.0 ms)
- FPS: OK (25 fps; projeto 25) · 1080x1920 yuv422p10le
- Voz da IA no corte: OK — **0.06 s** detectados (limite 0.2 s; modelo por quadro do `edicao/locutores.json`) · peças da EDL dentro das zonas da IA: 0.00 s · trechos: 00:16.08–00:16.14

| Linha | Status | WER | Esperado (roteiro) | Ouvido no corte |
|---|---|---|---|---|
| L01 | presente | 11.1% | Joga o livro no ChatGPT e escreve barra mindmap. | Joga o livro no ChatGPT e escreve /mindmap. |
| L02 | presente | 12.5% | Ele te devolve o mapa mental do livro. | Ele te devolve uma mapa mental do livro. |
| L03 | presente | 11.1% | Barra sketchnote: o resumo do livro em anotação ilustrada. | sketchnote, o resumo do livro em anotação ilustrada. |
| L04 | presente | 27.3% | Barra flashcards: ele te entrega cartões com o resumo do conteúdo. | Flashcard, ele te entrega cartões com resumo do conteúdo. |
| L05 | presente | 10.0% | Barra fluxograma: ele resume o livro num fluxo de aprendizado. | /fluxograma, ele resume o livro num fluxo de aprendizado. |
| L06 | presente | 10.0% | E barra quadrinhos: ele resume as ideias principais em quadrinhos. | E /quadrinhos, ele resume as ideias principais em quadrinhos. |
| L07 | presente | 11.1% | Comenta a palavra LIVRO que eu vou te enviar | Comente a palavra "livro" que eu vou te enviar |
| L08 | presente | 0.0% | mais 50 comandos no seu direct. | mais cinquenta comandos no seu direct |
| L09 | presente | 44.4% | E manda pra quem tem livro parado na estante. | e manda pra quem tem livros parados no seu estante |

## Trechos extras (fala fora do roteiro no corte)

- nenhum
