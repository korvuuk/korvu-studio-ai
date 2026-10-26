---
name: capa-reels
description: Escolhe o frame da capa do Reel (candidatos pontuados por nitidez, rosto, centragem e olhos abertos) e renderiza a capa no estilo da marca (título nível 2 + rabisco) com prévia do recorte 3:4 da grade. Use no estado "capa" do pipeline, depois do corte com cor.
---

# Capa do Reel

## 0. Formato (o que o Instagram faz com a capa)
| Onde aparece | Recorte | O que isso obriga |
|---|---|---|
| Arquivo da capa | **1080×1920 (9:16)** PNG/JPG — mesmo enquadramento do Reel | é o que vai no `cover_url` da publicação |
| Grade do perfil | **3:4 central = 1080×1440** | rosto **e** título têm que caber aqui, senão somem na grade |
| Reel em tela cheia | 9:16 com a UI por cima | livre ~270 px no topo e ~670 px embaixo (@, legenda, botões) |

Regra prática: nada de essencial fora de 1080×1440 centrado, nem abaixo de y≈1250.
Estilo visual: `00-marca/referencias/capas/estilo-editorial-escuro.md` (referência do Carlos, 2026-09-16).

## 1. Candidatos
```bash
uv run python .claude/skills/capa-reels/scripts/frame_candidates.py videos/<slug> [--n 12]
```
- **A pose vem escrita no roteiro** (`pose_capa` no `roteiro.json`): o script imprime, grava no `scores.json` e
  **escreve no topo do `contato.jpg`, em laranja**. Quem escolhe a capa procura **aquela pose** — "mão aberta
  pedindo calma", "mão no queixo" — e não o quadro genericamente mais parado. Entre dois candidatos bons, ganha
  o que mostra a pose; se nenhum mostrar, avisar o Carlos (provavelmente esqueceu na gravação).
- **PAUSA DA CAPA primeiro** (2026-09-18): todo roteiro manda o Carlos olhar para a câmera e ficar **parado
  3 s antes da 1.ª fala**. Esse trecho fica fora do corte, mas continua no intermediário
  `edicao/fontes/<fonte>.mp4` — o script amostra essa janela (com a conversão V-Log + o look ativo, para o
  frame sair na cor do vídeo) antes de qualquer outra coisa. É o que evita procurar quadro a quadro.
  `--pausa-capa <s>` muda a duração; `--sem-pausa-capa` ignora (gravações antigas). Os candidatos trazem
  `origem: pausa | corte` no `scores.json`.
- Depois disso, amostra frames das linhas de **hook** e **payoff** do corte final (tempos `saida_*` da `edl.json`
  + `secao` do `roteiro.json`); sem esses dados, amostra uniformemente.
- Nota = 0,22 nitidez (variância do Laplaciano) + 0,18 **boca fechada** + 0,16 tamanho do rosto
  + 0,15 olhos abertos + 0,13 centragem (rosto dentro do recorte 3:4) + 0,12 **quadro parado**
  + 0,04 exposição do rosto.
- **Boca fechada e quadro parado** são exigência do Carlos (2026-09-16): a capa não pode pegá-lo no meio de
  uma palavra nem com a mão em movimento.
  - `boca`: altura da mancha escura na faixa da boca ÷ altura do rosto (`abertura_boca` no `scores.json`);
    até ~5 % conta como fechada, ≥ 15 % zera a nota.
  - `parado`: diferença média do quadro para os vizinhos a ±0,12 s (`movimento`); gesto de mão, cabeça
    virando ou borrão de deslocamento derrubam a nota.
- Saídas em `videos/<slug>/capa/candidatos/`: `cand-01.jpg` (melhor) … `cand-NN.jpg`,
  `contato.jpg` (folha rotulada, tracejado = recorte 3:4, caixa laranja = rosto), `scores.json`.
- **Olhe o `contato.jpg`** (Read) antes de escolher: a nota ajuda, mas a expressão manda
  (boca entreaberta no meio de palavra, olhos semicerrados e borrão de movimento derrubam a capa).
- Fonte: `edicao/cor/corte-cor.mp4` (com cor). Se ainda não existe, cai no `edicao/corte.mp4` — que está em
  **V-Log 10-bit** (Lumix S5IIX): nos trechos de câmera o frame recebe a LUT de visualização
  `00-marca/cor/luts/entrada-camera.cube` (lut3d tetraédrica) para não ficar lavado (`scores.json` →
  `lut_visualizacao: true`). Sem a LUT aparece `[AVISO] sem LUT de entrada V-Log — imagem vai parecer lavada`.
  Nesse caso os candidatos servem só para adiantar: **refaça depois do `/cor`** para a capa final ter a cor do vídeo.

### Detector de rosto
O OpenCV 5.x instalado **não traz** os cascades Haar (nem `CascadeClassifier`). O script usa o primeiro disponível:
1. Haar: `haarcascade_frontalface_default.xml` + `haarcascade_eye.xml` em `$HAAR_DIR` ou
   `.claude/skills/capa-reels/assets/haar/` (precisa de OpenCV com `CascadeClassifier`, ex. 4.x).
2. YuNet: `assets/face_detection_yunet_2023mar.onnx` (ou `$YUNET_MODEL`) — funciona no OpenCV 5.
3. Fallback: heurística de pele + olhos como manchas escuras (aproximado; o `scores.json` registra `detector`).

## 2. Render da capa
```bash
uv run python .claude/skills/capa-reels/scripts/render_capa.py videos/<slug> --frame cand-03.jpg --variante A
```
- Título: `--titulo-json`, ou `capa/titulo.json`, ou `edicao/titulo.json`, ou o `titulo` do `reel-props.json`.
  A capa usa só o **impacto** (nível 2) + rabisco; `--com-contexto` adiciona o nível 1.
- Variantes: **A** texto embaixo/rabisco cinza · **B** em cima/cinza · **C** embaixo/laranja · **D** em cima/laranja.
  Ajustes: `--posicao topo|base`, `--cor-rabisco acento|#RRGGBB`, `--escurecer 0.12`.
- Saídas: `capa/capa-<V>.png` (1080×1920), `capa/grade-<V>.png` (1080×1440 = como aparece no perfil), `capa/grade-comparacao.jpg` (todas lado a lado) e `capa/grade-3x4.png` (a última).
- O frame é copiado para `remotion/public/_render/_capas/<slug>/` (ignorado pelo git).

## Checklist
- Texto inteiro dentro do recorte central 1080×1440 (confira `grade-3x4.png`). A base do bloco já é travada
  na zona segura (y≈1250) pela composição `Capa` — nas 1.as capas reais o texto descia até y≈1590 e ficava
  debaixo do @ e da legenda do Reel.
- Rosto não coberto pelo texto; olhos abertos; sem borrão.
- 3–6 palavras no impacto; rabisco na palavra-chave.
- **Gere 3 variantes com HEADLINES DIFERENTES** (decisão do Carlos, 2026-10-02 — "devemos gerar variações de capas com headline diferente"). Cada variante tem o seu `titulo-<V>.json` com uma frase completa que se entende sozinha (diz de quem/do quê é o vídeo, ou abre uma curiosidade; nunca começa com "e"/"mas"/"que"; sem pontuação; `contexto: null`, frase inteira em `impacto`):
  ```bash
  uv run python .claude/skills/capa-reels/scripts/render_capa.py videos/<slug> --frame <f> --variante A --titulo-json capa/titulo-A.json
  uv run python .claude/skills/capa-reels/scripts/render_capa.py videos/<slug> --frame <f> --variante C --titulo-json capa/titulo-C.json
  uv run python .claude/skills/capa-reels/scripts/render_capa.py videos/<slug> --frame <f> --variante D --titulo-json capa/titulo-D.json
  ```
  Exemplo aprovado (Hassabis): "Quem é o gênio que ganhou o Nobel com IA" · "O menino do xadrez que ganhou o Nobel com IA" · "Conheça o homem que ganhou o Nobel com IA".
  Mostre ao Carlos `capa/grade-comparacao.jpg` (as 3 grades lado a lado); a escolhida vira `capa/capa.png` e vai para `05-render-pronto/<slug>/capa/capa.png`.
