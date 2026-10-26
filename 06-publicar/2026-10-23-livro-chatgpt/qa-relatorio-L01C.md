RESULTADO: PASS

# QA final (6.a rodada: sem legenda, sem titulo do hook, sem veu escuro) - edicao/final-L01C.mp4 (hook L01C, conteudo primeiro)

| Checagem | Resultado |
|---|---|
| qa_check.py | PASS: 1080x1920, 25 fps, H.264 High yuv420p bt709, AAC 48 kHz, 34,82 s, faststart ok, sem preto/congelado; -14,1 LUFS / TP ok |
| Texto desenhado | PASS: nenhum titulo nem legenda em 0,5 / 1 / 2,5 / 3,9 / 4,5 / 6 / 7,2 / 9 / 12 / 14 / 19 / 24 / 27 / 33 s; so o cartao do CTA 'comenta livro / que eu vou te enviar' (27 s) |
| Sem degrade/sombra no pe das imagens full | PASS: capa+logo, mapa mental, sketchnote, flashcards, fluxograma e quadrinhos vao limpos ate a base |
| Cartao do comando no peito | PASS: nao cobre o rosto (/sketchnote em 7,2-9 s; cartao /flashcards em fade translucido em 14 s, normal) |
| Regressao | PASS: cor quente consistente, CTA sem cobrir a boca, imagens com movimento, sem "/" nem credito desenhado |
| Abertura L01C | PASS: capa+logo (0,5-1 s), cartao (2,5 s; /mindmap em 3,9 s), mapa mental full (4,5-6 s), Carlos em 7,2 s |
## Avisos (nao bloqueiam)
- qa_check 'Duracao vs EDL 34,82 vs 34,44' WARN: esperado (edl.json da pasta e o da A/B).
- Sem titulo do hook: a sobreposicao com a capa do livro some, aviso anterior resolvido.
