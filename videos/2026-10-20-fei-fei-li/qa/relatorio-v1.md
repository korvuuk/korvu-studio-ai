RESULTADO: FAIL

# QA final — 2026-10-20-fei-fei-li

Revisado em 2026-10-17 · `edicao/final.mp4` (168,49 s · 170,8 MB · corte EDL v14 → cor cadeia Hassabis → Remotion com 30 extras `modo: full` de `extras-v2/overlays.json` → `audio.py` com `musica/opcao-1.mp3`).

**Veredicto:** a parte técnica passa (specs, loudness, pretos/congelados, extras sem "faltando"), a correção das legendas da revisão 1 está confirmada (palavra a palavra e no tempo), e o Carlos em tela cheia, a cor e a capa estão certos. O que reprova é o **enquadramento de 6 extras** (rosto fora do quadro, palco vazio, barras pretas/coloridas dentro do 9:16) — critério "nenhum extra com barra/caixa" e "o extra mostra o que a fala cita". São ajustes de `enquadrar` em `edicao/extras-v2/montar.py` (+ regerar `overlays.json`, `gerar_props.py`, `render_reel.py`, `audio.py`, `qa_check.py`). **Não mexe** em corte, cor, legendas nem EDL.

## Tabela de checagens

| # | Checagem | Resultado |
|---|---|---|
| 1 | Resolução 1080×1920 | OK |
| 2 | FPS 25 (FPS do projeto) | OK |
| 3 | H.264 High, yuv420p 8-bit, tags bt709/bt709/bt709 | OK |
| 4 | Áudio AAC 48 kHz, 256 kbps | OK |
| 5 | Duração 168,49 s (EDL 168,44 s, delta 0,05 s) | OK |
| 6 | Faststart (`ftyp > moov > free > mdat`) · 170,8 MB · 8,5 Mbps | OK |
| 7 | Loudness integrada −14,2 LUFS (LRA 2,8 LU) | OK |
| 8 | True peak −1,7 dBTP (qa_check/ebur128; `audio.log` diz −1,6) — ambos ≤ −1,5 | OK |
| 9 | Pretos ≥ 0,5 s: 0; quadro preto isolado (blackdetect 0,04 s): 0; congelados ≥ 2 s: 0 | OK |
| 10 | Extras: 30 overlays, 0 `faltando`, nenhum placeholder visível no vídeo; E06 fora da camada (como combinado) | OK |
| 11 | Crédito "Fonte: …" em 30/30 extras, no topo da zona segura (y≈270–310, texto a partir de x=65) | OK (avisos W7) |
| 12 | Logo Bloomberg (canto sup. dir.), barra CBS, logo NatGeo e legenda queimada de fonte: nenhum visível | OK (fragmento de texto em V20, aviso W4) |
| 13 | Faixa contínua L03→L26 sem "entra e sai"; Carlos em tela cheia em 0–8,88 · 78,96–81,68 · 115,64–118,00 · 128,72–fim (conferido no `reel-props` e nos quadros) | OK |
| 14 | Legendas × fala (ASR do corte `qa/transcricao-corte.json`, 346 palavras casadas): só sobram diferenças de flexão/contração (usa/usaram, neural/neurais, estava/tava, eram/era, ano/anos, 50/cinquenta, 18/dezoito, IA/AI) e 5 palavras funcionais faladas sem legenda (e, o, E, os, o) | OK |
| 15 | Sincronia legenda × fala: mediana 0 ms; nenhuma das 346 palavras casadas com desvio > 120 ms (L14 corrigida: "exatamente" não está mais 1,95 s adiantada) | OK |
| 16 | Stills pedidos na revisão 1 em `final.mp4`: 66,8 s "reconhecer" · 72,0 s "mil" (50 mil) · 105,5 s "meu" (no meu canal) · 133,9 s "A inteligência artificial" (`qa/contato-pedidos-revisao1.jpg`) | OK |
| 17 | Linhas L04 L06 L08 L09 L10 L12 L14 L15 L21 L22 L23 L26 L28 L29 L31 L32 L33: texto = fala, algarismos (2007, 2012, 50 mil, 18), sem pontuação (nenhum token com caractere especial; só o hífen de "Fei-Fei"), "Fei-Fei" hifenizado em todas as ocorrências (L03, L26, L32), ImageNet, Geoffrey Hinton, Princeton ok | OK |
| 18 | `destaque`: "fiscais" (27,42 s) e "significa" (143,34 s) agora marcados | OK |
| 19 | Páginas de 2–4 palavras (SRT: 65×4, 20×3, 18×2); única de 1 palavra = "Ela" (L07, 28,2 s, intencional) | OK |
| 20 | Legenda na zona segura (y≈1150, até ≈1215 nas palavras grandes; base limite 1250), nunca sobre o rosto do Carlos; estilo "seleção" (cinza→branco, destaque grande, sombra, sem caixa) | OK |
| 21 | Cartão AULA 154,02–160,78 s: "comenta AULA / que eu te envio no seu direct" (bate com a fala), abaixo da boca, dentro da zona segura | OK |
| 22 | Cor do Carlos × `07-publicados/2026-10-20-geoffrey-hinton/video/video-final-cor.mp4`: mesmo tom quente (RGB médio da caixa central 75/59/57 aqui contra 79–84/61–62/58–60 no Hinton, R ≈ 5–9 pontos mais baixo) e consistente entre 1,0 · 142 · 165,5 s | OK |
| 23 | Áudio: voz alinhada com `corte-audio.wav` (lag 0, corr. 0,93); ASR no áudio final recupera o roteiro (razão 0,94, só nomes próprios divergem); fade-out final, último 0,2 s em silêncio | OK (aviso W9: nível da música) |
| 24 | Capa `capa/capa.png` 1080×1920 + `grade-3x4.png` 1080×1440: título "Quem é a madrinha da IA" abaixo do queixo (y 1070–1280), fora do rosto, dentro do 3:4 (y 840–1010 na grade, margens laterais ≥ 65 px); "Foto: Stanford HAI" legível; mesma foto do V01 (CAPA-01) e tema da L26/L03 | OK |
| 25 | Enquadramento dos extras (rosto no quadro, sem barra/caixa, extra mostra o que a fala cita) | **FAIL** — 6 extras (abaixo) |

## CORREÇÕES OBRIGATÓRIAS (extras) — tempo de saída, o que está errado, o que mudar

Medido com as fórmulas de `MidiaEnquadrada` (Reel.tsx): `enquadrar.x/y` = foco em fração da `area`, a janela é presa dentro da `area`. Pontos de referência em px da fonte. Evidências: `qa/contato-extras-1.jpg` a `-5.jpg` (início/meio/fim de cada extra), `qa/contato-detalhe-faces.jpg`, `qa/contato-final-0X.jpg`.

1. **V04 · E02 (SFPL) · 16,32–19,72 s · L05 "os pais praticamente não falavam inglês"** — o rosto dela NÃO aparece: só parede de madeira e a ponta do cabelo no canto direito durante os 3,4 s. `enquadrar.x = 0.25` (janela 176–784 px de 1920) e ela está em ≈ 0,40–0,60 da largura (rosto em 0,43–0,53 em todo o clipe). **Trocar para `x ≈ 0.49`** (janela ≈ 650–1260).
2. **V05 · Y04 (lavanderia) · 19,72–24,23 s · L06** — rosto cortado ao meio pela borda esquerda nos 4,5 s (janela começa em x=1098, o rosto vai de ≈ 1000 a 1200). `x = 0.72` → **`x ≈ 0.58`** (janela ≈ 850–1420; mantém as araras à direita).
3. **V21 · E09 (TED, "abri tudo de graça") · 81,68–86,64 s · L17** — (a) de 81,68 a ≈ 84,3 s a tela mostra só palco vazio (cortina azul e carpete): o clipe abre com plano aberto dela pequena (≈ x 0,37) e só a partir de 2,24 s do clipe vem o close; (b) no close o rosto fica meio cortado à esquerda (x=0.6, rosto em ≈ 0,41); (c) em ≈ 84,5–86,6 s a legenda (y≈1150) cai em cima da boca dela. **Pôr `in: 2.3` (o clipe tem 8 s, precisa de 4,96) e `x ≈ 0.42`.** Como o close é height-limited (sem folga vertical), a legenda continuará perto da boca/queixo; se a boca ficar entre y≈1090 e 1230 durante a legenda, **trocar por plano mais aberto** (reservas E03/E08 em `sequencia-extras.md`) ou outro clipe dela falando.
4. **V18 · Y59 (cavalo "person/horse/gate") · 64,89–70,08 s · L14** — faixa vinho-escura de ≈ 223 px no topo (margem do slide TED2024; luma 29–35, y 0–223) durante ≈ 4,8 s: lê como barra. O clipe só tem 0,36 s de Fei-Fei no palco e depois é o slide. **`area` = `{x:0, y:115, largura:1920, altura:855}`** (a foto vai de y≈111 a ≈969; o texto de rodapé "J. Deng…" fica fora). Os 0,36 s iniciais perdem um pouco de topo, aceitável. (O clipe tem 5,20 s para 5,19 s de overlay, não há folga para `in`.)
5. **V06 · E04 (TED2015, foto da lavanderia no telão) · 24,23–28,04 s · L06** — barras pretas: ≈ 150 px no topo (luma 5–11) e ≈ 130–170 px embaixo (luma 6–9 a partir de y≈1790): é o escuro do auditório em volta do telão. `enquadrar = {x:.5,y:.5}` sem `area`. **Usar `area` que exclua ≈ 8 % do topo e ≈ 9 % da base da fonte (ou `zoom ≈ 1.22`, `y ≈ 0.48`).**
6. **V02 · Y01 (foto P&B dela criança) · 11,28–13,90 s · L04** — faixa azul-marinho de ≈ 110 px na base (y≈1808–1920, luma 42): o `area` (`y:108, altura:950`) passa 74 px do fim da foto (≈ y 983). **`altura ≈ 870`.**

Depois de corrigir: conferir os mesmos tempos (início, meio e fim de cada um) em `final.mp4` e rodar `qa_check.py` de novo; os demais números (LUFS/TP) não mudam se `audio.py` usar os mesmos parâmetros.

## Avisos (não bloqueiam; ajustar na mesma passada se for barato)

- **W1 · V08 · F03 formatura · 30,96–33,44 s:** o rosto dela fica na borda direita (zona lateral) no 1.º segundo (início 31,26 s: rosto quase cortado). `x 0.33 → 0.47`, `xFim 0.40 → 0.48`.
- **W2 · V25 · Y24 (Hinton/Sutskever/Krizhevsky) · 99,08–106,28 s:** no início (99,1–≈100,3 s) a janela corta o rosto do Sutskever ao meio e mostra fragmentos "YA / KEVER" e "er, OpenAI" da tarja. `x 0.30 → ≈ 0.17` (rosto dele) e `xFim` no Hinton (0.50 já cai nele aos 102,5 s, "Geoffrey").
- **W3 · V03 · Y03 jornal · 13,90–16,32 s:** com o pan `x 0.32 → 0.60` a foto dela sai do quadro por volta de 15,0 s e sobra só texto do jornal. `xFim ≈ 0.45` mantém a foto + manchete.
- **W4 · V20 · Y19 (ursinho "Girl/Boy") · 74,01–78,96 s:** fragmento "nd Fei-Fei Li" (da linha de texto no topo da fonte) no canto superior esquerdo até ≈ 75,5 s. Subir o topo do `area` (`y ≈ 60`).
- **W5 · V29 · N14 (Rei Charles + Fei-Fei) · 123,00–125,38 s:** rosto da Fei-Fei encosta na lateral direita (zona 120 px) e o do Rei fica cortado à esquerda. Com a legenda "Hoje a imprensa chama" funciona, mas `x 0.50 → ≈ 0.55` centra ela.
- **W6 · V14 · Y13 (gatos) · 52,36–56,56 s:** divisórias marrons entre as 3 fotos do slide aparecem à esquerda e, no fim, a ponta do gato laranja à direita. Fonte 1280×720; restringir a `area` à foto do meio ampliaria demais. Aceitável.
- **W7 · créditos de V22 (86,64–89,36) e V25 (99,08–106,28):** a caixa vai até x≈985 (limite direito 960); encurtar ("Bloomberg Originals — The Circuit / Krizhevsky, Sutskever, Hinton (2012)" e "… / Johnny Guatto, University of Toronto"). Em V26 (106,28–115,64) o crédito cai sobre o título do gráfico "Top 1 Accuracy…" e aparece uma faixa de miniaturas (≈ 70 px) no topo (`area.y ≈ 30`).
- **W8 · legenda sobre o queixo/mandíbula em close:** V15 CAPA-04 (56,56–58,39 s, "Em 2007" entre lábio e queixo), V10 Y09 (36,35–40,48 s, logo abaixo do queixo) e, no V21, sobre a boca (ver item 3). É limite do enquadramento de retrato fechado com legenda fixa em y≈1150; se quiser tirar, subir o foco (`y`) de V15 de 0.40 para ≈ 0.33.
- **W9 · música:** o bed está ≈ 6 dB abaixo da voz durante a fala (RMS por palavra: voz −33,5 dBFS, música já com ducking −39,5; no 10.º percentil a diferença é só 0,3 dB) porque o sidechain quase não atua (limiar 0,05); o piso do áudio subiu de −27,3 dBFS (Hinton, sem música) para −23,1 dBFS. A fala continua inteligível (o ASR do `final.mp4` recupera o roteiro, razão 0,94), por isso fica como aviso. Se ao ouvir a música competir com a voz: `audio.py --musica-db -26`. `musica.json.escolhida` está `null` e `edl.json.audio.musica` está `None` — registrar `opcao-1.mp3`.
- **W10 · documentação desatualizada:** `edicao/sequencia-extras.md` (Montagem final) diz V20 = E05; o `overlays.json`/`reel-props` usam `Y19.png` (o `V20-E05.mp4` ficou sem uso) e V19 = `Y23.png`, V14 = `Y13.png` (quadro parado).

## Observações (herdadas da revisão 1; não bloqueiam)

1. **Gancho sem título:** `reel-props.titulo = null`; o hook sai só com a legenda "Imagina chegar…" (começa em 0,14 s; Carlos em tela cheia 0–8,88 s). Confirmar que é intencional.
2. **L32 diz "uma entrevista completa"; o material (AULA) é `material/palestra-fei-fei-li-ted2015.pdf`** (palestra TED 2015, ~18 min, com legenda em português; o PDF também leva a conversa de 62 min na SFPL). A L33 ("São somente 18 minutos com a legenda em português") bate com a TED; a palavra "entrevista" cabe melhor na conversa da SFPL. A EDL foi aprovada assim; fica a critério do Carlos.
3. **Zoom segurando menos de 1,0 s** (5 trechos de 0,84–0,96 s, regra de 18/09): EDL aprovada, só registro.
4. **L29:** "mostrar exemplos" do roteiro não foi dito no take; o corte não perdeu nada.
5. Capa: o gancho do vídeo é a história da imigrante ("Imagina chegar adolescente…") e a capa pergunta "Quem é a madrinha da IA", que só se explica na L26 (≈ 123–128 s). A capa reaparece como V01 (8,88 s), então a ligação existe; é escolha do Carlos (17/10).

## Arquivos gerados em `qa/`
`qa-tecnico.md` / `qa-tecnico.json` + `frames/` (qa_check), `contato-final-01…06.jpg` (1 quadro a cada 3,5 s, 48 quadros), `contato-extras-1…5.jpg` (início/meio/fim dos 30 extras), `contato-pedidos-revisao1.jpg` (66,8 · 72,0 · 105,5 · 133,9 s), `contato-detalhe-faces.jpg` (V04, V05, V21).
