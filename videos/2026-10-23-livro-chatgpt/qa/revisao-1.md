RESULTADO: FAIL

# Revisão 1 (corte + legendas/props) — 2026-10-23-livro-chatgpt

## Erros (bloqueiam)
1. `edicao/reel-props.json` → `titulo` está DESATUALIZADO (origem "heuristica"): contexto "Joga o livro no", impacto "ChatGPT e escreve barra mindmap", rabisco "mindmap", selecao "livro no", fim 4.38. O aprovado em `edicao/titulo.json` é "Joga o livro no ChatGPT" / "e escreve isso", cinza 2, rabisco "isso". Regenerar os props (`gerar_props.py`) lendo o titulo.json. Efeito se não for corrigido: título errado e legendas ocultas 0–4,38 s.
   - Conferir depois que a janela do título esconde só o necessário: com "isso" o comando "barra mindmap" (2,58–3,99 s) fica sem legenda enquanto o título estiver na tela; o hook precisa fechar antes do E02 ficar longo ou o título terminar ~2,6 s. Decisão de design, mas olhar no still.

## Avisos (não bloqueiam)
- Corte: 34,44 s, 9 linhas presentes, sem duplicadas, voz da IA 0,06 s em 16,08–16,14 (resíduo; limite 0,2 s, OK). Sincronia A/V OK. WER 16 % só pelas falas aprovadas (L02 "uma mapa", L04 "flashcard… com resumo", L07 "Comente", L09 "livros parados no seu estante") e "/" no lugar de "barra".
- Legenda x áudio (texto do roteiro, como a regra manda):
  - L02: legenda "o mapa mental", ele diz "uma mapa mental". Sem ação.
  - L04: legenda "Barra flashcards ... cartões com o resumo"; ele diz "flashcard" (singular) e "com resumo" (sem "o"). Ouvir 11,7–12,5 s: o ASR não transcreveu "barra/" aqui (EDL traz "/flashcard"). Se ele realmente não disse "barra", a legenda "Barra" mente. Confirmar com o Carlos.
  - L07: legenda "Comenta a palavra LIVRO"; ele diz "Comente". Cartão CTA (topo "comenta") também fica "comenta". Sem ação (decisão dele).
  - L09: legenda "tem livro parado na estante"; ele diz "livros parados no seu estante". Divergência mais visível (concordância e "seu"). Recomendo, na minha opinião, legenda fiel à fala real aqui ("livros parados no seu estante") ou regravar; decisão do Carlos.
  - L08: legenda "50", áudio "cinquenta": OK.
- Sincronia: L03 a página "Barra sketchnote" entra em 7,08 s, mas ele diz "barra" ~7,38 e "sketchnote" ~7,94 (karaokê ~0,3–0,7 s adiantado). L04 "Barra" 0,14 s adiantado. Conferir no render; ajustar tempos em legendas.json se ficar visível.
- Comandos: todos aparecem como "Barra X" (nenhum "/"): OK. Grafia ChatGPT, mindmap, sketchnote, flashcards, fluxograma, quadrinhos, LIVRO OK. Sem pontuação. Páginas de 2–4 palavras (SRT 3–4): OK. `destaque` coincide com as palavras do roteiro (barra+comando, mapa mental, LIVRO, 50 comandos).
- Extras: E02/E04/E06/E08/E10 em `card` e E03/E05/E07/E09/E11 em `full`, na linha certa, todos presentes (faltando=false), `credito` null (padrão 19/10 OK), sem dado pessoal evidente. `enquadrar` em E03, E07, E09 (movimento). Card: centroY 700, altura 820 = y 290–1110; legenda em y≈1150, logo abaixo, sem colisão. E02 só entra em 1,84 s (0–1,84 s é só o Carlos + título).
- Movimento: E05 e E11 (em pé, `full`, SEM `enquadrar`) dependem do Ken Burns padrão do Remotion (1,0→1,08, ~2,8 s e 3,7 s): fraco para imagem com detalhe (sketchnote, tirinha). Sugiro `enquadrar` com zoom/pan revelando o detalhe. Conferir no render que ambos se mexem. Cards `tela` são vídeos, em movimento.
- Legenda sobre resultados em `full`: E05 e E11 (sem `enquadrar`, logo sem véu) recebem a legenda em y≈1150 por cima de imagem com texto; E03/E07/E09 têm véu de base. Ver still: se ilegível, subir a legenda ou usar véu.
- `segmentos[].layout` vale "split" para L01–L06 enquanto os overlays são card/full. O Remotion calcula a legenda pelos overlays (progressoDoSplit), então a legenda fica em 1150 e não em 715; conferir no still, mas não deve haver erro.
- Rosto: stills do corte (1, 9, 27, 33 s, com LUT) com o rosto em y≈600–900 e mãos/peito em 1000–1400; legenda em 1150 não cobre o rosto. Zoom alternado visível, enquadramento consistente.
- CTA: LIVRO 25,98–28,84 s (L07 25,84–28,68; ASR "livro" ~27,0), rodapé "que eu vou te enviar"; legendas da janela somem (sem duplicar). Ok. Cartão dentro das zonas seguras a confirmar no still do Remotion.
- Stills com legenda do Remotion não renderizados (Remotion pendente): refazer a checagem de zonas seguras (topo 270, base 670, laterais 65/120; "flashcards" a 132 px tem ~840 px, perto do limite de ~895) depois do render.

## Correções pedidas
1. Regenerar `reel-props.json` com o `titulo.json` aprovado (erro 1) e conferir a janela do título e do E02.
2. Confirmar com o Carlos o "barra" da L04 e a grafia da L09 (aviso).
3. Considerar `enquadrar` em E05 e E11.
4. Nova passagem rápida após o 1.º render para ver stills de 1, 5, 9, 13, 17, 21, 27 s.
