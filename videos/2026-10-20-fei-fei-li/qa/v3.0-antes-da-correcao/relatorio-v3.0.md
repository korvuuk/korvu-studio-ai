RESULTADO: FAIL

# QA final — 2026-10-20-fei-fei-li — versão 3 (layouts variados)

Revisado em 2026-10-17 · `edicao/final.mp4` (168,49 s · 191,0 MB · 9,5 Mbps) · camada de extras `edicao/extras-v2/overlays-v3.json` (30 extras: 14 full, 8 solo, 6 pilha, 2 split; `reel-props.json` confere 30/30 com o `overlays-v3.json`, mesmos modos e tempos). Relatório da v1 guardado em `qa/relatorio-v1.md`.

**Veredicto:** a parte técnica, a sincronia, o Carlos em tela cheia, a cor, a capa, as legendas, as pilhas, os splits e as 6 correções da v1 estão bons. **Reprova um único ponto, o do item (1) que você pediu para olhar: nos `solo`, a legenda de 2–3 linhas sobe e SOBREPÕE a base da imagem** (V15 ImageNet, V26 gráfico) ou encosta nela (V06, V18). É um parâmetro só (`LAYOUTS.solo.baseY`) e não mexe em corte, cor, legendas, EDL nem áudio. Depois da correção basta re-renderizar, refazer `audio.py`/`qa_check.py` e conferir os 4 trechos abaixo.

## CORREÇÃO OBRIGATÓRIA (1)

**Legenda sobre a imagem nos `solo`.** Em `remotion/src/brand.ts`, `LAYOUTS.solo = { baseY: 1060, alturaMax: 760 }`; o centro da legenda fica em y≈1150 e uma página de 2–3 linhas (palavra de destaque grande na linha de baixo) cresce para cima e passa de y 1060. A imagem termina em y 1060–1069 (Ken Burns 1,03). Medido por quadro (12,5 fps) e conferido a olho (`qa/v3-legenda-sobre-imagem-V15-V18.jpg`, `qa/v3-legenda-sobre-imagem-V26.jpg`):

| Extra | Tempo (s) | Página | Problema |
|---|---|---|---|
| V15 (slide ImageNet) | 59,5–60,96 | "chamado / ImageNet" | "chamado" começa em y≈1050 e entra ~14 px na base do slide, em cima da linha de citação "Jia Deng, Wei Dong…CVPR 2009". É justamente o momento de sincronia do ImageNet. |
| V26 (gráfico Y60) | 113,6–115,6 | "da / inteligência / artificial" (3 linhas) | "da" começa em y≈1035 e cobre ~30 px da base do gráfico (caixa "Other models / State-of-the-art models"). A linha "artificial" desce até y≈1280, 30 px dentro da zona da base (limite 1250). |
| V06 (E04 TED) | 27,3–28,04 | "os / fiscais" | "os" encosta na borda da imagem (0–4 px de folga). |
| V18 (E05 TED) | 70,3–71,8 | "Segundo ela / 50" | "Segundo ela" encosta na borda (0–5 px). |
| V22 (Y24) | ≈ 90,2–91,5 | "Um grupo da / Universidade" | passa, mas com ~9 px de folga (apertado). |

**O que mudar:** `solo.baseY` 1060 → **1000** (a imagem sobe 60 px; o topo do maior solo, o V06 com 504 px de altura, vai a y≈496, longe do crédito em y≈337; o fundo de todo solo fica ≤ 1009). Com isso a página de 3 linhas do V26 deixa ~30 px de folga e as de 2 linhas ~70 px. Opcional e recomendado: no V26 (113,5–115,6) quebrar "da inteligência artificial" em 2 linhas (ou tirar o `destaque` de "inteligência"/"artificial" nessa página) para a base não passar de y 1250. Depois: conferir 27,3–28,04 · 59,5–60,96 · 70,3–71,8 · 113,6–115,6 em `final.mp4`.

## Tabela de checagens

| # | Checagem | Resultado |
|---|---|---|
| 1 | Resolução 1080×1920 | OK |
| 2 | FPS 25 (FPS do projeto) | OK |
| 3 | H.264 High, yuv420p 8-bit, tags bt709/bt709/bt709 | OK |
| 4 | Áudio AAC 48 kHz (256 kbps) | OK |
| 5 | Duração 168,49 s (EDL 168,44 s, delta 0,05 s; limite 180 s) | OK |
| 6 | Faststart (`ftyp > moov > free > mdat`) · 191,0 MB · 9,51 Mbps | OK |
| 7 | Loudness integrada −14,2 LUFS (LRA 2,8 LU) | OK |
| 8 | True peak −1,7 dBTP (qa_check; `audio.log` diz −1,6), ambos ≤ −1,5 | OK |
| 9 | Pretos ≥ 0,5 s: 0 · congelados ≥ 2 s: 0. Os solos têm fundo preto mas com a imagem sempre presente (nenhum quadro vazio). Congelados curtos (0,5–0,7 s) em 72,3 e 106,7–114,8 s = gráfico/slide parado do próprio vídeo (esperado) | OK |
| 10 | Extras: 30 overlays, 0 `faltando`, nenhum placeholder; E06 (print) fora da camada, substituído pelo gráfico Y60 (WARN no máximo, como combinado) | OK |
| 11 | Crédito "Fonte: …" em 30/30 extras, um só chip por cena no topo da zona segura (texto a partir de x=65, y≈337); o mais largo (V09, "Wikimedia Commons (CC BY-SA) · Bloomberg Originals · CBS Mornings") termina em x≈945 ≤ 960; V24 em x≈862 | OK |
| 12 | **(1) SOLO** — fundo preto, imagem inteira sem corte de texto (V03 jornal, V06 telão TED, V15 slide, V18 palco/"48.940 workers", V21 artigo 2012, V22 Hinton/Sutskever/Krizhevsky, V23 esquema ImageNet, V26 gráfico), crédito no topo, sem barras coloridas | OK |
| 13 | **(1) SOLO — legenda abaixo da imagem sem sobrepor** | **FAIL** — V15 e V26 sobrepõem; V06, V18 encostam (correção obrigatória acima) |
| 14 | **(2) PILHA** (V09, V10, V11, V13, V24, V28) — 3 faixas preenchidas em todos os quadros (nenhuma preta; luma média por faixa 39–165; fresta de 6 px, luma 7–13), crédito único no topo e legenda legível sobre a faixa do meio/base | OK (avisos W2–W5) |
| 15 | **(3) SPLIT** (V04 SFPL 16,32–19,72; V20 TED 81,68–86,64) — rosto dela no painel de cima em todo o trecho; Carlos embaixo; legenda logo abaixo da divisória, sem tapar os olhos dele | OK |
| 16 | **(3) Transição do split** — entrada e saída são um único deslize de 0,4 s (10 quadros), monotônico, sem oscilação (`qa/v3-transicao-split-V04-*.jpg`, `…V20-*.jpg`). No V20 a entrada vem do Carlos em tela cheia, suave. No V04 a entrada vem de um corte seco do solo V03 para o Carlos (1–2 quadros em tela cheia) e a saída revela o Carlos voltando à tela cheia por ~0,2 s antes do corte seco para o V05 | OK (aviso W1) |
| 17 | **(4) Sincronia** — slide ImageNet (V15) em 58,39–60,96: "chamado" 59,42, "ImageNet" 60,10 (a imagem entra ~1 s antes da palavra e fica durante ela). Esquema (V23) em 91,55–95,57: "usa" 91,55, "o ImageNet" 92,31, "rede neural" 94,75–95,05 (mosaico com a tarja IMAGENET na palavra, árvore de categorias em "rede neural"). Papel de 2012 (V21) em "Aí chega 2012" (86,64–89,36). Hardware (F21) só na faixa de baixo da pilha V24 | OK (aviso W7) |
| 18 | **(5) Carlos em tela cheia** só em 0–8,88 · 78,96–81,68 · 115,64–118,00 · 128,72–168,44 (nenhum buraco/sobreposição de overlay fora disso; conferido nos quadros, `qa/v3-carlos-tela-cheia.jpg`); CTA sem extra | OK |
| 19 | **(6) Legendas × fala** — `legendas.json` idêntico ao da v1 (357 palavras, texto, tempos e `destaque` iguais; `reel-props.json` = `legendas.json`), já confirmadas na v1 contra o áudio. As 35 divergências do `qa_check` (texto × `roteiro.json`) são improviso aceito (regra de 17/10), não defeito | OK |
| 20 | Legenda sem pontuação/caracteres especiais, "Fei-Fei" hifenizado, ImageNet/Geoffrey Hinton/Princeton/AULA corretos; páginas de 2–4 palavras; legenda fora do rosto do Carlos (full) e abaixo da divisória (split); estilo "seleção" (cinza→branco) | OK |
| 21 | Cartão AULA 154,02–160,78 s: "comenta AULA / que eu te envio no seu direct", abaixo da boca, na zona segura | OK |
| 22 | **(7) Cor** do Carlos × Hinton publicado (`07-publicados/…/video-final-cor.mp4`, caixa central do rosto): Fei-Fei R 71–81 · G 53–58 · B 48–57 (1 · 6 · 80 · 117 · 142 · 165,5 s) contra Hinton R 70–88 · G 50–61 · B 49–57; consistente entre takes; `corte-cor.mp4` inalterado desde a v1 | OK |
| 23 | Áudio: voz + música opção 1 (piso nas pausas ≈ −22 dBFS, música presente em todo o vídeo); voz mediana −12,8 dBFS contra música −18,8 dBFS nas pausas; fade-out final | OK (aviso W8) |
| 24 | **(8) Capa** `capa/capa.png` 1080×1920 (nº 1, escolha do Carlos 17/10) + `grade-3x4.png` 1080×1440: "Quem é a madrinha da IA" abaixo do queixo, rabisco laranja em "madrinha", dentro do corte 3:4 com margens laterais, "Foto: Stanford HAI" legível, mesma foto do V01 | OK |
| 25 | Correções da v1 aplicadas: E02 (agora split, rosto dela em quadro) · Y04 x 0,58 (V05, rosto inteiro) · E09 (split, `in` 2,3, close dela) · Y59 `area` (V17, sem a faixa vinho) · E04 (solo, sem as barras do auditório) · Y01 `area` (V02, sem a faixa azul) · créditos encurtados (≤ x 960) | OK |

## Avisos (não bloqueiam; ajustar na mesma passada se for barato)

- **W1 · split V04 e V20, sobe-e-desce curto.** `Reel.tsx` aplica o deslize de entrada/saída (`transicaoFrames` 10) mesmo quando o vizinho é `full`/`solo` (corte seco). Resultado: V04 em 16,32–16,72 (corte do solo para o Carlos em tela cheia e deslize para baixo) e 19,32–19,72 (a cena sobe e o Carlos volta à tela cheia por ~0,2 s, depois corte para o V05); V20 em 86,40–86,60 (idem, antes do solo V21). Não é estranho nem repete o "sobe e desce" reprovado (cada split faz UM movimento por lado), mas, se quiser a faixa mais limpa: tratar `entra`/`sai` como seco quando o vizinho não é split. Durante o deslize a legenda cruza o rosto dele por ~0,15 s (V20 em 86,44–86,52; V20 em 81,84–81,92).
- **W2 · V10 (40,48–45,44), faixas 2 e 3 repetem a mesma foto** (menino de laranja: Y10 e Y11), só muda o enquadramento; a faixa 3 ainda tem as barras laterais marrons da fonte (~100 px cada lado). Trocar a faixa 3 por outra imagem (ex.: crianças de Y14 em outro recorte ou uma reserva de "ideia" do `sequencia-extras.md`). O mesmo menino ainda reaparece em V11 (faixa 1, com as caixas) e V28 (faixa 3, como callback).
- **W3 · V09 faixa 3 e V13 faixas 1–3 (CBS):** o logo laranja "CBS MORNINGS" aparece no pé de cada faixa e, nas faixas 2 e 3 do V13, cortado pela metade; no V13 a palavra "computador" (52,4–56,6, ~54,3 s) passa por cima dele. Subir o `area.y` ~45 px na base dessas faixas (`area.altura` −45) tira o logo (`qa/v3-pilha-V13-cbs.jpg`).
- **W4 · restos de logo e legenda queimada da fonte nos solos:** o "B" da Bloomberg (canto superior direito da imagem, ~x 1010–1060) aparece em V03 (13,04–16,32), V21 (86,64–89,36), V22 (89,36–91,55) e no início do V23 (91,55–~93), e a tarja da fonte no canto superior esquerdo ("Daily Record", "Alex Krizhevsky, Ilya Sutskever and Geoffrey E. Hinton", "Johnny Guatto/University of Toronto", "ImageNet") (`qa/v3-solo-logo-bloomberg-topo.jpg`). Para tirar sem cortar o assunto: `area.y` +45 no V21 (papel, margem em branco) e no V03; no V22 e no V23 cortaria o topo das cabeças/do esquema, então aceitável.
- **W5 · V24 (95,57–99,08):** o chip de crédito (3 fontes) cobre a etiqueta "NEURAL" da animação Y26 na faixa 1; e "rede neural numa" em cinza (95,6–96,4) tem pouco contraste sobre o mosaico de ferramentas da faixa 2. Faixas 2–3 do V11 e V28 (slide do ursinho) mostram laterais de degradê verde/roxo da própria fonte (não são pretas).
- **W6 · V03 (13,04–16,32):** a faixa do jornal perde a metade de cima do título "Parsippany" (`area.y` 70); a manchete e a foto dela estão inteiras. Aceitável.
- **W7 · sincronia fina da L19:** a pilha com o hardware e a animação DATA/NEURAL/GPUs (V24) entra em 95,57 ("numa competição"), ~0,5–2 s depois de "treinar uma rede neural" (93,59–95,05), que está sob o esquema do V23. Funciona (a árvore de categorias cobre "rede neural"); se quiser colar, antecipar o V24 em ~0,5 s.
- **W8 · música:** o leito fica ~6 dB abaixo da voz (voz mediana −12,8 dBFS; pausas −18,8 dBFS; no 10.º percentil das palavras a diferença cai para ~3 dB). Inteligível; se competir ao ouvir, `audio.py --musica-db -26`. `musica.json.escolhida` ainda `null` e `edl.json.audio.musica` `None`: registrar `opcao-1.mp3` (`audio.log` desta passada não menciona a música; o mix está no `final.mp4`, conferido nas pausas).
- **W9 · split, rosto na faixa superior:** no V04 e no V20 os olhos dela caem em y≈235 (zona insegura do topo, 270 px); é o desenho do split (cena em cima), não um defeito de enquadramento.

## Observações (herdadas; não bloqueiam)

1. **Gancho sem título:** `reel-props.titulo = null`; o hook sai só com a legenda "Imagina chegar…" (0,14 s; Carlos em tela cheia 0–8,88 s). Confirmar que é intencional.
2. **L32 diz "uma entrevista completa"; o material (AULA) é `material/palestra-fei-fei-li-ted2015.pdf`** (palestra TED 2015). A L33 ("18 minutos com a legenda em português") bate com a TED; a EDL foi aprovada assim. Critério do Carlos.
3. **Zoom segurando menos de 1,0 s** (5 trechos de 0,84–0,96 s): EDL aprovada, só registro.
4. **L29:** "mostrar exemplos" do roteiro não foi dito; o corte não perdeu nada.
5. **Capa × gancho:** o hook é a história da imigrante e a capa pergunta "Quem é a madrinha da IA", que só se explica na L26 (≈ 123–128 s). A capa reaparece como V01 (8,88 s). Escolha do Carlos (17/10).
6. Repetições deliberadas entre pilhas e fulls (cavalo "person/horse/gate" em V17 e V28; teddy e menino em V11/V28): callback da L25, aceitável.
7. **E06 (print do ILSVRC 2012)** não entra na camada (substituído pelo gráfico Y60); WARN, não FAIL.

## Arquivos de apoio em `qa/`
`qa-tecnico.md` / `qa-tecnico.json` + `frames/` (qa_check desta passada) · `v3-solo-1…4.jpg`, `v3-pilha-1…3.jpg`, `v3-split.jpg`, `v3-full-1…5.jpg` (início/meio/fim de cada extra, 30/30) · `v3-transicao-split-V04-entrada|saida.jpg`, `v3-transicao-split-V20-entrada|saida.jpg` (quadro a quadro, 0,04 s) · `v3-legenda-sobre-imagem-V15-V18.jpg`, `v3-legenda-sobre-imagem-V26.jpg` (evidência da correção obrigatória) · `v3-solo-logo-bloomberg-topo.jpg`, `v3-pilha-V13-cbs.jpg` · `v3-carlos-tela-cheia.jpg` · `relatorio-v1.md`.
