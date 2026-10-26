---
name: legendas-animadas
description: Gera legendas (legendas.json + legendas.srt), o reel-props.json e renderiza o Reel no Remotion com legendas estilo "Texto Selecionado", título do hook, zooms, cenas extras (B-roll em split/full/card, imagens com Ken Burns, animações) e créditos. Use depois do corte/cor, quando for a hora de aplicar os gráficos (passo "Remotion" do /renderizar).
---

# Legendas animadas + render Remotion

Transforma a EDL aprovada em props para a composição `Reel` (pasta `remotion/`) e renderiza.
Contratos: `docs/contratos.md` §0 (principal + extras), §4 (edl.json), §6 (legendas), §7 (reel-props.json).
Estilo: `00-marca/referencias/legendas/estilo-selecao.md`. Tokens visuais: `remotion/src/brand.ts` (provisórios);
**layouts dos extras: `LAYOUTS` em `brand.ts`** (espelho de `00-marca/layouts.md` — quando o modelo do Carlos
chegar, mude só ali).

## Formato
- **fps = `FPS_PROJETO` (padrão 25)**: o `gerar_props.py` escreve `"fps"` no `reel-props.json` a partir do
  `edl.json`; a composição `Reel` pega o fps no `calculateMetadata` (nada de 30 fixo). Tempos de animação ficam em
  segundos (`TEMPO_SEG` / `useTempo()` em `brand.ts`), então o visual é o mesmo a 25 ou 30 fps.
- Saída: `edicao/render-remotion.mp4` — H.264 8-bit **yuv420p bt709**, CRF 18, AAC, no fps do projeto (Instagram).
- O Chrome do Remotion não lê H.264 4:2:2 10-bit: o `gerar_props.py` cria proxies 8-bit em `edicao/remotion/`
  quando preciso (com carimbo; só refaz se a fonte/LUT mudar):
  - sem `edicao/cor/corte-cor.mp4` ainda → usa o `corte.mp4` (10-bit, V-Log) como proxy 8-bit **com a LUT de
    visualização** (`00-marca/cor/luts/entrada-camera.cube`) nos trechos de câmera — serve para conferir; o render
    final tem que usar o `corte-cor.mp4` do `/cor`;
  - extra tipo `camera` em V-Log sem `<ID>-cor.mp4` → proxy 8-bit com a LUT de visualização.

## Pré-requisitos
- `videos/<slug>/edicao/edl.json` com `palavras_saida` (**as palavras do roteiro**, não as da transcrição) e `aprovado: true`.
- `videos/<slug>/edicao/cor/corte-cor.mp4` (ou `edicao/corte.mp4` como fallback, ver acima).
- `videos/<slug>/roteiro.json` (opcional, mas melhora o título e as descrições das animações).
- Cenas extras ingeridas (`edicao/extras/`, via `ingest.py` da skill `corte-por-roteiro`).

## Passo a passo
1. **Gerar props + symlink**
   ```bash
   uv run python .claude/skills/legendas-animadas/scripts/gerar_props.py videos/<slug>
   # opções: --video edicao/cor/corte-cor.mp4  --titulo-json <arquivo>  --sem-titulo  --sem-cta
   ```
   Cria `edicao/legendas.json`, `edicao/legendas.srt`, `edicao/reel-props.json` (com `fps`) e o symlink
   `remotion/public/_render/<slug>` → `videos/<slug>/edicao`. Extras ganham `src` (`_render/<slug>/extras/E01.mp4`)
   e `fonteLargura/fonteAltura`. Avisa se algum extra está FALTANDO.
2. **Revisar o título do hook** (o script imprime o que derivou). Sem `edicao/titulo.json`, o título vem
   de uma heurística: linha do hook do roteiro (+ `TEXTO:"..."` da coluna TELA, se existir).
   Se ficar ruim, escreva `edicao/titulo.json` e rode de novo:
   ```json
   {"contexto": "Se você usa o ChatGPT assim,", "impacto": "tá jogando tempo fora.",
    "cinza": 3, "rabisco": "fora", "selecao": "ChatGPT assim"}
   ```
   - `cinza` = quantas palavras iniciais do impacto ficam cinza (o resto fica branco).
   - `rabisco` = palavra do impacto sublinhada; `selecao` = palavras do contexto com realce de seleção.
   - Opcionais: `fim` (s, padrão fim da 1.ª linha ≈3 s), `posicao` (`baixo`|`centro`|`topo`),
     `corRabisco` (`"acento"` = laranja da marca), `ocultarLegendas` (padrão `true`).
3. **Conferir o cartão do CTA** (o script imprime `CTA: 'NOBEL' 53.72–56.66s (linha L18) rodapé '...'`). Com
   `cta_palavra` no roteiro, o `reel-props.json` ganha `cta` (contrato §7): entra na palavra **"comenta"** falada
   na linha de seção `cta` e fica até o fim dessa linha + 0,5 s (nunca por cima da linha seguinte). Para ajustar sem
   mexer no roteiro, escreva `edicao/cta.json` (ex.: `{"rodape": "que eu te mando no direct"}`, `{"inicio": 41.2}`
   ou `{"ativo": false}`) e rode de novo. Sem `cta_palavra` (CTA de envio/salvar/seguir) não há cartão.
4. **Conferir no Studio** (opcional): `cd remotion && npx remotion studio` → composição `Reel`,
   prop `arquivoProps: "_render/<slug>/reel-props.json"`.
5. **Render**
   ```bash
   uv run python .claude/skills/legendas-animadas/scripts/render_reel.py videos/<slug>
   ```
   Bloqueia se `edl.aprovado != true` (`--auto` só com pedido explícito do Carlos); confere que o render saiu no
   fps do `reel-props.json`. Extras faltando não bloqueiam e **não aparecem no vídeo** (o QA reprova, mas quem avisa é o relatório). Depois: `audio.py`
   (master a partir do `edicao/corte-audio.wav`, sem perdas) e `qa-video`.

## O que o Reel faz
- Vídeo principal. **Zoom é aplicado UMA vez:** com `edl.json.zoom_no_corte` (EDLs novas) o punch-in alternado por
  peça já vem no `corte.mp4` (render_corte) → o `gerar_props.py` escreve `zoomNoCorte: true` e `segmentos[].zoom: null`
  e o Reel não aplica zoom (título, legendas e animações continuam). EDL antiga: punch-in por segmento
  (`segmentos[].zoom`, origem `zoom.origem` ou `ZOOM.origem`).
- **Legendas** (páginas de 2–4 palavras, `createTikTokStyleCaptions` ~900 ms): entram no ritmo da fala,
  karaokê cinza→branco, `destaque: true` sobe para o nível "impacto". Somem durante o título do hook e
  durante cartelas de texto em tela cheia. Em split continuam em y≈1150 — dentro do painel do Carlos, que fica embaixo.
- **Cenas extras** (`tipo: "extra"`), por `modo` (medidas em `LAYOUTS`):
  - `split` — **extra no painel de cima** (caixa 1080×608, 16:9), Carlos embaixo recortado no rosto; escolhido pelo **formato** do arquivo (deitado), não pelo roteiro;
  - `full` — extra em tela cheia (mídia vertical cobre a tela; horizontal fica contida na caixa com grade),
    voz e legendas continuam;
  - `card` — cartão arredondado sobre o Carlos (fundo escurecido).
  Vídeo do extra toca `[in, out]` **mudo** (a voz é do principal; `som: true` liga) e, se acabar antes do overlay,
  **segura o último quadro**. Imagem = Ken Burns lento (`LAYOUTS.kenBurns`). `print`/`tela` ficam contidos,
  `imagem`/`camera` cobrem (`LAYOUTS.ajuste`). `animacao` → componente do registry (`componente`, ex. `"<slug>/E02"`).
  `credito` → "Fonte: X" pequeno, dentro da zona segura. `faltando` → o extra **não entra no vídeo** (`mostrarFaltando: false`, padrão — regra do Carlos: nenhum vídeo que chega a ele leva etiqueta). A etiqueta "EXTRA Exx FALTANDO" só aparece no `preview.mp4` da EDL e quando se pede `--mostrar-faltando` para depurar.
- **Textos** (`tipo: "texto"`): padrão sobre o vídeo; `"modo": "cartela"` = card em tela cheia. Ficam por cima dos extras.
- Overlays legados (`tela`, `animacao` de EDLs antigas) continuam funcionando.
- **Título do hook** nos primeiros ~3 s quando `titulo` existe.
- **CTA final em cartão** (`cta`, decisão do Carlos 14/10 — `components/CtaPalavra.tsx`): "comenta" em cima, a
  **palavra em minúsculas, SEM ponto** ("nobel" — o ponto confundia quem vai comentar, Carlos 21/10; Bricolage Grotesque 800, `CTA_COR` = laranja da marca) num cartão
  de papel editorial (visual de 21/10: sem canto, sem sombra, sem contorno), fio fino, uma linha pequena embaixo, sem
  carimbo (Carlos, 21/10: "muito poluído"). Cartão sobe em 6 frames, palavra com mola curta, saída de 4 frames. Base do cartão em
  y 1236 (zona segura), centrado na área útil, palavra até 190 px: fica abaixo da boca do Carlos, que está em tela
  cheia no CTA. As legendas das palavras dentro da janela **somem** (sem duplicar). Tokens em `CTA` / `EDITORIAL`
  (`brand.ts`); design em `00-marca/design-system/korvu-editorial.md` §5.

## Animações novas (extras tipo `animacao`)
Crie `remotion/src/animacoes/<Nome>.tsx` (`React.FC<AnimacaoProps>`: recebe `palavras` com tempos
relativos ao início do overlay, `largura`, `altura`, `modo`, `duracaoFrames`) e registre em `registry.ts` com a
chave **`"<slug>/E02"`** (preferível — IDs de extra se repetem entre vídeos) ou `"E02"`. Sem registro, a EDL marca
o extra como `faltando`. Use `ExemploFluxo.tsx` como modelo (tokens de `brand.ts`, `useTempo()` para tempos,
nada de `Math.random`).

## SRT
2–4 palavras por cue, máx. 42 caracteres, quebra em troca de linha, fim de frase e pausas > 0,7 s.

## Padrão fixado pelo Carlos em 19/10 (vale para todos os vídeos a partir do Jensen Huang)
1. **Nenhum crédito/fonte de imagem DENTRO do vídeo.** "Polui a imagem, não fica profissional." O campo `credito` continua nos overlays/catálogos, mas o Remotion não o desenha (`LAYOUTS.credito.mostrar: false`); os créditos vão TODOS na **descrição do post** (legenda IG/FB), numa linha "Imagens: …".
2. **Toda imagem em MOVIMENTO, sempre.** Nunca uma foto/slide parado: zoom ou Ken Burns em toda imagem, também em cada faixa da `pilha` e no `solo`. Imagem com informação/detalhe (gráfico, jornal, esquema) ganha zoom que revela o detalhe (`enquadrar.zoom` + pan `xFim/yFim`). Imagem parada e pequena quebra o ritmo (decisões 17/10 e 19/10).

## Sem legendas (decisão de 21/10)
Vídeos do formato **rápido de comandos** (tela de computador, cartão + resultado) saem **sem legenda karaokê**: `gerar_props.py --sem-legendas`
(escreve `mostrarLegendas: false` no `reel-props.json`; o Reel não desenha `<Legendas>`; título do hook e cartão do CTA continuam).
O roteiro marca `legendas_no_video: false`. Perfis e os outros formatos continuam com legenda.
