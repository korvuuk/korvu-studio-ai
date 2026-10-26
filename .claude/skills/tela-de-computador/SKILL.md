---
name: tela-de-computador
description: Transforma uma gravação de TELA DE COMPUTADOR (ChatGPT no Mac, ou outro app) em cenas extras prontas para brutos/extras/ — acha os momentos (anexar, digitar o comando, enviar, "gerando", resultado), corta as esperas longas, recorta a caixa de digitação em 16:9 e entrega os clipes no formato que o editor já conhece. Usar ANTES do /editar sempre que houver gravação de tela do Mac/PC em videos/<slug>/material/ (vídeos de ferramenta/comando, ex. "joga o livro no ChatGPT"). Não muda nada no editor, no Remotion nem nos vídeos de perfil.
---

# tela-de-computador — da gravação da tela do Mac às cenas extras

> Criada em 21/10 (pedido do Carlos: "temos que ter um skill específico só para quando gravamos alguma coisa na tela
> do Mac… para não misturar com o skill que já tem"). Decisão: esta skill fica **antes** do editor. Ela só fabrica
> arquivos em `brutos/extras/`; o `corte-por-roteiro`, o `legendas-animadas` (Remotion), a cor e o QA ficam intocados.
> Primeiro vídeo: `videos/2026-10-23-livro-chatgpt/` (modelo de referência para os próximos).

## Quando usar
- O roteiro tem cenas `tela` e o Carlos gravou **a tela do computador** (não o celular): arquivo deitado ou quase
  quadrado, longo (minutos), com esperas (geração de imagem de 40–90 s, menus, Finder).
- O resultado de cada comando é uma **imagem baixada** do app (PNG), não a tela.

## O que entra e o que sai
| Entra (em `videos/<slug>/material/`) | Sai (em `videos/<slug>/`) |
|---|---|
| `screnn record/*.mov` (ou qualquer nome) — a gravação inteira, 1 só | `brutos/extras/Exx-tela-<comando>.mp4` — 1 clipe por comando, **900×820 (proporção do `card`), 25 fps, sem áudio**: a capa aparece no campo (1 s) → digitar e enviar (tempo real) |
| `img/Exx.png` — os resultados baixados do app | `brutos/extras/Exx-<nome>.png` — cópia com o nome da cena do roteiro |
| `capas/` (ou o que foi anexado) | `edicao/tela.json` — a lista de cortes (tempos, velocidade, recorte), editável à mão |
| | `edicao/tela-previa/Exx-n.jpg` — 1 quadro por trecho, para conferir o recorte olhando |

**Layout decidido pelo Carlos (21/10, 2.ª rodada):** o clipe do campo de digitação entra como **`card`** (900×820, o Carlos
continua em tela cheia atrás) — por isso o recorte padrão é **900×820, só o campo** (miniatura anexada + texto digitado
+ menu de barra), colado à esquerda e ao pé da janela, saída 900 de largura (`largura_saida: 900`). Nunca a janela inteira.
(A 1.ª versão, 16:9 da parte de baixo em `split`, ficou guardada em `edicao/tela-v1-split.json` do livro-chatgpt.)
Depois do cartão, o resultado entra INTEIRO em `full`. O PNG do resultado entra como extra normal: em pé → `full`;
deitado/quase quadrado → **`full` com `enquadrar`** (zoom que revela o detalhe, padrão 19/10 "toda imagem em
movimento") — decisão de 21/10: o resultado entra sempre inteiro. Nunca inventar modo novo no Remotion por causa de tela de computador.

## Passo a passo
1. **Mapear os momentos** (automático, sem OCR):
   ```bash
   uv run --with pillow --with numpy python .claude/skills/tela-de-computador/scripts/momentos.py "videos/<slug>/material/screnn record/<arquivo>.mov" --saida videos/<slug>/edicao/momentos
   ```
   Sai `momentos.json` (eventos `caixa` = mexeu na caixa de digitação; `tela` = mudança grande em cima; `parados` =
   trechos ≥ 8 s sem nada, que são as esperas a cortar) + `momentos-contato.jpg` (um quadro por evento, com o tempo) +
   `momentos-caixa.jpg` (só a caixa, ampliada, para ler o que foi digitado). **Olhar as duas folhas.**
2. **Afinar a 4 fps** em volta de cada digitação (o `momentos.py` acha o segundo; a folha a 4 fps dá o quarto de
   segundo): extrair a caixa com `ffmpeg -ss A -to B -vf "fps=4,crop=…"` e montar uma folha (`tile`). Ler nela:
   o "/" que abre o menu de barra do ChatGPT, o comando completo, o quadro em que a caixa esvazia (= enviado).
3. **Escrever `edicao/tela.json`** (formato no topo de `scripts/recortar.py`): uma cena por comando, 3 trechos
   (anexar ×2, digitar ×1, gerando ×1 de 1 s), `recorte_padrao` 16:9 da parte de baixo da janela (ex.: janela
   1716×1982 → `{"x":0,"y":1017,"w":1716,"h":965}`: pega a caixa, o menu de barra, o botão de enviar e o
   placeholder do "gerando"). Todos os recortes de uma cena com a **mesma proporção**.
4. **Conferir o recorte olhando:** `uv run python …/recortar.py videos/<slug>/edicao/tela.json --previa` →
   `edicao/tela-previa/`. Se cortou o botão de enviar ou o texto ficou pequeno demais, ajustar o recorte.
5. **Gerar os extras:** `uv run python …/recortar.py videos/<slug>/edicao/tela.json` → `brutos/extras/Exx-tela-*.mp4`.
   Copiar os PNG de resultado para `brutos/extras/Exx-<nome>.png`. Ver um filmstrip de 1 clipe (`fps=2,tile`) e o
   `ffprobe` (1080 de largura, 25 fps).
6. **Ligar ao roteiro:** a tabela `## Cenas extras` já diz em que linha cada `Exx` entra; conferir que os nomes dos
   arquivos batem com os IDs. Daí em diante é o fluxo normal: `/extras` lista o que falta, `/editar` ingere
   (`ingest.py` normaliza 1080 / 25 fps) e o editor monta por cima da fala.

## Sem legenda karaokê neste formato (Carlos, 21/10)
Vídeo rápido de comandos já tem cartão + resultado na tela: **sem legenda falada e sem título do hook** — só as imagens, o cartão do comando e o cartão do CTA.
No /renderizar: `gerar_props.py … --sem-titulo --sem-legendas` (ou `legendas_no_video: false` no roteiro). O cartão fica no peito (1000×330).

## Ficha de gravação da tela no Mac (passar ao Carlos antes de gravar)
- Gravar **só a região da janela** do app (Cmd+Shift+5 → "Gravar parte selecionada"), não a tela inteira. Janela
  **estreita e alta** (quase em pé), num lugar fixo — não mover nem redimensionar durante a gravação.
- Texto do app ampliado (Cmd e `+`, 2–3 vezes) para o comando ficar legível depois de recortado para 1080 de largura.
- **Uma gravação só**, os comandos todos na **mesma conversa**, em **chat temporário**. Um comando por imagem anexada.
- No ChatGPT, digitar "/" abre o menu de barra (Create image, Deep research…): é esperado — continuar digitando o
  comando e Enter. Na 1.ª vez pedir "em imagem, em português" (ou combinar antes: "tudo que eu enviar é para gerar
  imagem", como feito em 21/10).
- Esperar a geração terminar (40–90 s) sem mexer na janela: a skill corta a espera. Não abrir a imagem em janela
  separada antes do próximo comando (o visualizador cobre a caixa).
- No fim, **baixar cada imagem** gerada com o nome da cena do roteiro (`E03.png`, `E05.png`…) em `material/img/`.
- Tema claro ou escuro, um só, igual em todos. 60/120 fps da gravação não importam (vira 25).

## Armadilhas já vistas (21/10)
- A gravação sai a **120 fps** com `nb_frames` enorme: extrair quadros sempre com `fps=` no filtro, nunca quadro a quadro.
- O **Finder** de anexar e o **visualizador de imagem** cobrem a janela: esses trechos não servem para a tela; usar o
  arrasto do arquivo para a caixa (2–4 s, acelerado) como "anexar".
- `sips` só rasteriza a 1.ª página/quadro; para folhas de contato usar ffmpeg `tile`.
- O placeholder do "gerando" fica **acima** da caixa (y≈1100–1300 numa janela de 1982): o recorte só da caixa não o
  mostra — por isso o recorte padrão é o 16:9 inteiro da parte de baixo.
- Imagens de resultado **deitadas** (1536×1024) existem: o pipeline as põe em `split`; se o Carlos quiser tela cheia,
  `full` + `enquadrar` com zoom (nunca estática).

## Scripts
- `scripts/momentos.py` — eventos + trechos parados + folhas de contato (PIL + numpy; `uv run --with pillow --with numpy`).
- `scripts/recortar.py` — `tela.json` → `brutos/extras/Exx-*.mp4` (ffmpeg: crop, scale 1080, setpts, fps 25, concat); `--previa`, `--so E02,E04`.
