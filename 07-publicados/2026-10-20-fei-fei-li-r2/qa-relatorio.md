RESULTADO: PASS

# QA final — 2026-10-20-fei-fei-li — versão 3.1 (layouts variados, correções do QA aplicadas)

Revisado em 2026-10-17 · `edicao/final.mp4` (168,49 s · 189,8 MB · 9,45 Mbps, arquivo de 06:29) · camada `edicao/extras-v2/overlays-v3.json` (30 extras: 14 full, 8 solo, 6 pilha, 2 split; `reel-props.json` confere 30/30 com o `overlays-v3.json`, mesmos modos e tempos). Histórico: v1 FAIL (6 enquadramentos) em `qa/relatorio-v1.md`; v3.0 FAIL (legenda sobre a imagem nos `solo`) em `qa/v3.0-antes-da-correcao/relatorio-v3.0.md`.

**Veredicto:** PASS. A correção obrigatória da v3.0 (legenda sobreposta à base da imagem nos `solo`) está resolvida: em nenhum `solo` a legenda toca a imagem (folga mínima 27 px, no V26; nos demais ≥ 44 px). Os avisos W1, W2, W5 e W7 da v3.0 também foram resolvidos. Ficam só avisos de acabamento, listados abaixo (nenhum bloqueia a publicação).

## Conferência da correção obrigatória (v3.0 → v3.1)

`LAYOUTS.solo = { baseY: 1000, alturaMax: 700 }`: a imagem termina em y 1000–1009 (Ken Burns 1,03). Medido quadro a quadro (25 fps) o topo mais alto do texto da legenda abaixo da base da imagem (`qa/v3.1-legenda-abaixo-V06-V15-V18.jpg`, `qa/v3.1-legenda-abaixo-V18-V26.jpg`):

| Extra | Trecho marcado | Antes | Agora (folga mínima) |
|---|---|---|---|
| V06 (E04 TED) | 27,3–28,04 "os / fiscais" | encostava (0–4 px) | 57 px (topo do texto em y 1066) |
| V15 (slide ImageNet) | 59,5–60,96 "chamado / ImageNet" | sobrepunha ~14 px | 45 px (y 1054 em 59,53) |
| V18 (E05 TED) | 70,3–71,8 "Segundo ela / 50" | encostava (0–5 px) | 44 px (y 1053 em 70,38) |
| V26 (gráfico Y60) | 113,6–115,6 "da / inteligência / artificial" | sobrepunha ~30 px | 27 px (y 1036 em 113,62; 3 px abaixo da meta de 30, sem sobreposição) |
| V22 (Y24) | 89,4–91,5 | 9 px | 69 px |
| V03 · V21 · V23 | — | — | 93 · 90 · 112 px |

Fora dos solos, nada mudou (extras `full` idênticos aos da v3.0 por diferença de pixels; legendas idênticas às da v1).

## Tabela de checagens

| # | Checagem | Resultado |
|---|---|---|
| 1 | Resolução 1080×1920 | OK |
| 2 | FPS 25 (FPS do projeto) | OK |
| 3 | H.264 High, yuv420p 8-bit, tags bt709/bt709/bt709 | OK |
| 4 | Áudio AAC 48 kHz (256 kbps) | OK |
| 5 | Duração 168,49 s (EDL 168,44 s, delta 0,05 s; limite 180 s) | OK |
| 6 | Faststart (`ftyp > moov > free > mdat`) · 189,8 MB · 9,45 Mbps | OK |
| 7 | Loudness integrada −14,2 LUFS (LRA 2,8 LU) | OK |
| 8 | True peak −1,7 dBTP (qa_check/ebur128; `audio.py` diz −1,6), ambos ≤ −1,5 | OK |
| 9 | Pretos ≥ 0,5 s: 0 · congelados ≥ 2 s: 0. Os solos têm fundo preto mas a imagem está sempre presente. Congelados curtos (0,5–0,7 s) no gráfico/slide parado do próprio vídeo (esperado) | OK |
| 10 | Extras: 30 overlays, 0 `faltando`, nenhum placeholder; E06 (print) fora da camada, substituído pelo gráfico Y60 (WARN no máximo, como combinado) | OK |
| 11 | Crédito "Fonte: …" em 30/30 extras, um só chip por cena no topo da zona segura (texto a partir de x=65, y≈337); o mais largo (V09) termina em x≈945 ≤ 960; V24 (agora na ordem das faixas: U of Toronto / CHM · TED2015 · Bloomberg) em x≈862 | OK |
| 12 | **SOLO** — fundo preto, imagem inteira sem corte de texto relevante (V03 jornal, V06 telão TED, V15 slide, V18 palco/"48.940 workers", V21 artigo 2012, V22 Hinton/Sutskever/Krizhevsky, V23 esquema ImageNet, V26 gráfico), crédito no topo, sem barras | OK |
| 13 | **SOLO — legenda abaixo da imagem sem sobrepor** (ver tabela acima) | OK (era FAIL na v3.0) |
| 14 | **PILHA** (V09, V10, V11, V13, V24, V28) — 3 faixas preenchidas em todos os quadros (nenhuma preta; fresta de 6 px, luma 7–13), crédito único no topo, legenda legível sobre a faixa do meio/base. V10 faixa 3 agora é E03 (ela no palco, TED), sem repetir a foto da faixa 2. V24 reordenada: F21 (hardware) no topo, Y21 (mosaico) no meio, Y26 (DATA / NEURAL NETWORKS / GPUs → AI) no pé, sem o crédito cobrindo "NEURAL" | OK (avisos W2–W4) |
| 15 | **SPLIT** (V04 SFPL 16,32–19,72; V20 TED 81,68–86,64) — rosto dela no painel de cima em todo o trecho; Carlos embaixo; legenda logo abaixo da divisória, sem tapar os olhos dele no estado estável | OK |
| 16 | **Transição do split** — agora seca no lado encostado a extra de tela cheia/solo: V04 entra em 16,32 direto no split (sem o Carlos em tela cheia) e sai em 19,72 com corte seco para o V05 (`qa/v3-transicao-split-V04-*.jpg`); V20 entra em 81,68 vindo do Carlos em tela cheia (deslize de 0,4 s, correto) e sai em 86,64 com corte seco para o V21 (`…V20-*.jpg`). O Carlos não volta à tela cheia antes dos cortes | OK (aviso W1) |
| 17 | **Sincronia** — slide do ImageNet (V15) 58,39–60,96: "chamado" 59,42, "ImageNet" 60,10 (a imagem entra ~1 s antes e fica durante a palavra). Esquema (V23) 91,55–93,59: "usa" 91,55, "o ImageNet" 92,31, "para" 93,35. Pilha da L19 (V24) entra em 93,59 = "treinar" (93,59), com "rede neural" 94,75–95,05 e "competição de reconhecimento de imagens" sobre mosaico + animação. Artigo de 2012 (V21) em "Aí chega 2012" | OK |
| 18 | **Carlos em tela cheia** só em 0–8,88 · 78,96–81,68 · 115,64–118,00 · 128,72–168,44 (nenhum buraco/sobreposição de overlay fora disso); CTA sem extra | OK |
| 19 | **Legendas × fala** — `legendas.json` idêntico ao da v1 (357 palavras, texto, tempos e `destaque` iguais; `reel-props.json` = `legendas.json`). As 35 divergências do `qa_check` (texto × `roteiro.json`) são improviso aceito (regra de 17/10), não defeito | OK |
| 20 | Legenda sem pontuação/caracteres especiais, "Fei-Fei" hifenizado, ImageNet/Geoffrey Hinton/Princeton/AULA corretos; páginas de 2–4 palavras; fora do rosto do Carlos (full) e abaixo da divisória (split); estilo "seleção" (cinza→branco) | OK |
| 21 | Cartão AULA 154,02–160,78 s: "comenta AULA / que eu te envio no seu direct", abaixo da boca, na zona segura | OK |
| 22 | **Cor** do Carlos × Hinton publicado (caixa central do rosto): Fei-Fei R 71–81 · G 53–58 · B 48–57 (1 · 6 · 80 · 117 · 142 · 165,5 s) contra Hinton R 70–88 · G 50–61 · B 49–57; consistente entre takes; `corte-cor.mp4` inalterado desde a v1 | OK |
| 23 | Áudio: voz + música opção 1 em todo o vídeo (voz mediana −12,8 dBFS; música ≈ −18,8 dBFS nas pausas); fade-out final. `musica.json.escolhida = 1` registrado | OK (aviso W8) |
| 24 | **Capa** `capa/capa.png` 1080×1920 (nº 1, escolha do Carlos 17/10) + `grade-3x4.png` 1080×1440: "Quem é a madrinha da IA" abaixo do queixo, rabisco laranja em "madrinha", dentro do corte 3:4, "Foto: Stanford HAI" legível, mesma foto do V01 | OK |
| 25 | Correções da v1 mantidas: E02 (split, rosto em quadro) · Y04 x 0,58 · E09 (split, `in` 2,3) · Y59 `area` · E04 (solo, sem as barras do auditório) · Y01 `area` · créditos curtos (≤ x 960) | OK |

## Avisos (não bloqueiam; ajustar numa próxima passada só se for barato)

- **W1 · V20 entrada (81,84–81,96):** no deslize de 0,4 s a legenda "Ela" sobe cruzando os óculos dele por ~0,1 s. Transitório; o estado estável está limpo. Idem V04 não tem mais esse cruzamento.
- **W2 · legendas de 2–3 linhas passam de y 1250 (base)** em ~7–21 px de tinta (inclui descendentes), só em palavras grandes de destaque: V15 59,5–60,96 ("ImageNet", y 1266), V18 70,3–71,8 ("50", y 1257), V26 114,5–115,6 ("artificial", y 1271). É o desenho da legenda (centro y 1150 fixo), não do solo; a base do IG só começa bem abaixo disso. Se quiser ficar estritamente dentro: quebrar "da inteligência artificial" do V26 em 2 linhas (tirar `destaque` de "inteligência") e/ou subir `LEGENDA.centroYBaixo` ~20 px nos solos. A folga do V26 (27 px) cairia junto, então só se subir a imagem (`baseY` ≈ 985).
- **W3 · resto do logo CBS no pé das faixas (corrigido pela metade):** o logo cheio saiu, mas ainda aparece a metade de cima do chip laranja "CBS MORNINGS" (~20–25 px) no pé de V13 faixa 1 (52,4–54,8, depois some com o zoom), V13 faixa 2 (início) e V09 faixa 3 (33,4–40,5, vai encolhendo com o zoom) (`qa/v3.1-pilha-resto-cbs.jpg`). Reduzir mais `A_CBS.altura` (795 → ≈ 765, ou `area.altura` −30 nessas faixas) tira o resto.
- **W4 · Bloomberg/fonte nos solos:** V03 e V21 limpos (resta uma lasca quase invisível do "B" no canto, `qa/v3.1-solo-topo-V03-V21.jpg`); V22 (89,36–91,55) e o início do V23 (91,55–93,59) ainda mostram o "B" da Bloomberg no canto superior direito e a tarja da fonte no canto superior esquerdo ("Johnny Guatto/University of Toronto", "ImageNet"). Cortar tiraria o topo das cabeças/do esquema; aceitável. Em V03 a faixa do jornal perde quase todo o título "Parsippany" (só restam respingos de tinta na borda de cima); manchete e foto estão inteiras.
- **W5 · V10 faixa 3 (E03) escura:** palco TED com cortinas pretas/azuis (luma média 27; flancos quase pretos), mas é conteúdo (ela, letras vermelhas "TED"), não barra. V11 faixas 2–3 e V28 faixas 2–3 mantêm as laterais de degradê/marrom da própria fonte (não são pretas).
- **W6 · V24:** "para" em cinza (93,6–94,0) tem pouco contraste sobre o mosaico de ferramentas; legível.
- **W7 · split, rosto na faixa superior:** no V04 e no V20 os olhos dela caem em y≈235 (zona insegura do topo, 270 px); é o desenho do split (cena em cima), não defeito de enquadramento.
- **W8 · música:** leito ~6 dB abaixo da voz (mediana); inteligível. `edl.json.audio.musica` ainda `None` (o `musica.json.escolhida` já é 1): registrar `opcao-1.mp3` na EDL para o pacote. Se competir ao ouvir: `audio.py --musica-db -26`.

## Observações (herdadas; não bloqueiam)

1. **Gancho sem título:** `reel-props.titulo = null`; o hook sai só com a legenda "Imagina chegar…" (0,14 s; Carlos em tela cheia 0–8,88 s). Confirmar que é intencional.
2. **L32 diz "uma entrevista completa"; o material (AULA) é `material/palestra-fei-fei-li-ted2015.pdf`** (palestra TED 2015). A L33 ("18 minutos com a legenda em português") bate com a TED; a EDL foi aprovada assim. Critério do Carlos.
3. **Zoom segurando menos de 1,0 s** (5 trechos de 0,84–0,96 s): EDL aprovada, só registro.
4. **L29:** "mostrar exemplos" do roteiro não foi dito; o corte não perdeu nada.
5. **Capa × gancho:** o hook é a história da imigrante e a capa pergunta "Quem é a madrinha da IA", que só se explica na L26 (≈ 123–128 s). A capa reaparece como V01 (8,88 s). Escolha do Carlos (17/10).
6. Repetições deliberadas (cavalo "person/horse/gate" em V17 e V28; teddy e menino em V11/V28) = callback da L25.
7. **E06 (print do ILSVRC 2012)** não entra na camada (substituído pelo gráfico Y60); WARN, não FAIL.

## Arquivos de apoio em `qa/`
`qa-tecnico.md` / `qa-tecnico.json` + `frames/` (qa_check desta passada) · `v3-solo-1…4.jpg`, `v3-pilha-1…3.jpg`, `v3-split.jpg`, `v3-full-1…5.jpg` (início/meio/fim dos 30 extras, v3.1) · `v3-transicao-split-V04-entrada|saida.jpg`, `v3-transicao-split-V20-entrada|saida.jpg` (quadro a quadro, 0,04 s) · `v3.1-legenda-abaixo-V06-V15-V18.jpg`, `v3.1-legenda-abaixo-V18-V26.jpg` (prova da correção) · `v3.1-pilha-resto-cbs.jpg`, `v3.1-solo-topo-V03-V21.jpg` · `v3-carlos-tela-cheia.jpg` · `v3.0-antes-da-correcao/` (evidências e relatório da v3.0) · `relatorio-v1.md`.


## Adendo 17/10 — versão C5 (abertura sem o Carlos)
A L01 (0–5,0 s) passou a ser coberta por Y55 (Fei-Fei no sofá, Bloomberg Originals) em tela cheia; o Carlos entra em **5,00 s** (início da L02). Resto idêntico à v3.1. `qa_check.py`: PASS (−14,2 LUFS, −1,7 dBTP, 0 pretos, 0 congelados). Conferido por quadros em 0,0 · 0,5 · 2,5 · 4,9 (Fei-Fei) e 5,0 · 5,2 · 6,5 (Carlos). Vídeo do pacote substituído antes da publicação de 18/10 19:00.


## Adendo 17/10 — versão A (par A/B, `2026-10-20-fei-fei-li-a`)
Versão A do teste de abertura (`_controle/estrategia-de-alcance.md` §2.8): o Carlos aparece **desde o quadro 0**; do 5,0 s em diante o vídeo é idêntico ao da B (`2026-10-20-fei-fei-li`, abertura com a Fei-Fei, Carlos entra aos 5,0 s). Capa, legendas (`legendas.srt` idêntico), roteiro, legenda do post, hooks e material (AULA) iguais aos da B.
Vídeo: `video/video-final-a.mp4` = `videos/2026-10-20-fei-fei-li/edicao/final-A.mp4` (cópia conferida com `cmp`), 168,49 s, 1080×1920, 25 fps, H.264/AAC. `qa_check.py` (`edicao/final-A.qa.md`): **PASS** — −14,2 LUFS, −1,7 dBTP, 0 pretos, 0 congelados ≥ 2 s. Quadros conferidos em 0 · 2,5 · 5,2 · 100 s (Carlos nos 3 primeiros; a B tem a Fei-Fei em 0 e 2,5 s e o Carlos em 5,2 s).
Publicação: só Instagram, Trial Reel com graduação MANUAL, ≥ 24 h depois da B.


## Adendo 17/10 (A v2)
Mesmas mudanças da B a partir da L03 (CAPA-01 na L04, foto da família na L05, E02 saiu); o Carlos desde o quadro 0 até a L03. `qa_check.py` PASS. Conferido por quadros.


## Adendo 17/10 (v3.2) — crédito no rodapé + L22 em pilha
Pedido do Carlos: o "Fonte:" saiu do topo (caía no rosto) e ficou no rodapé, embaixo da legenda (y 1262; no split, no pé da caixa); créditos completos na descrição do post. O gráfico parado da L22 (106,28–115,64 s) virou pilha com movimento (Y60 com zoom/pan no salto de 2012 · F22 gráfico da queda do erro · Y61 usos da IA). `qa_check.py` PASS nas duas versões. Conferido por quadros em 2 · 10 · 14,5 · 18 · 36 · 60 · 84 · 108 · 111,5 · 114,5 · 124 s.
