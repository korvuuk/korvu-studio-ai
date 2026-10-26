RESULTADO: PASS

# QA final (6.a rodada: sem legenda, sem titulo do hook, sem veu escuro) - edicao/final-L01C-A.mp4 (hook L01C, Carlos em tela desde o quadro 0)

| Checagem | Resultado |
|---|---|
| qa_check.py | PASS: 1080x1920, 25 fps, H.264 High yuv420p bt709, AAC 48 kHz, 34,82 s, faststart ok, sem preto/congelado; -14,1 LUFS / TP ok |
| Texto desenhado | PASS: nenhum titulo nem legenda em 0,5 / 1 / 2,5 / 3,9 / 4,5 / 6 / 7,2 / 9 / 12 / 14 / 19 / 24 / 27 / 33 s; so o cartao do CTA 'comenta livro / que eu vou te enviar' (27 s) |
| Sem degrade/sombra no pe das imagens full | PASS: capa+logo, mapa mental, sketchnote, flashcards, fluxograma e quadrinhos vao limpos ate a base |
| Cartao do comando no peito | PASS: nao cobre o rosto (/sketchnote em 7,2-9 s; cartao /flashcards em fade translucido em 14 s, normal) |
| Regressao | PASS: cor quente consistente, CTA sem cobrir a boca, imagens com movimento, sem "/" nem credito desenhado |
| Abertura L01C-A | PASS: Carlos em tela em 0,5 e 1 s; cartao entra antes de 2,5 s (~2,2 s), /mindmap em 3,9 s; mapa mental full em 4,5 s (~4,4 s) ate 7,2 s; Carlos de volta ~9 s com /sketchnote |
## Avisos (nao bloqueiam)
- qa_check 'Duracao vs EDL 34,82 vs 34,44' WARN: esperado (EDL da pasta e a da A/B).
