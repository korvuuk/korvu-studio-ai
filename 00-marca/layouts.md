# Layouts do vídeo — principal + cenas extras

> **Regra do Carlos (2026-09-17), com screenshots de referência:** o **formato do arquivo** decide o layout.
> Extra deitado (formato YouTube) divide a tela; extra em pé ocupa a tela toda. Os números abaixo são os valores
> em `remotion/src/brand.ts` (`LAYOUTS`).

Tela 1080×1920 · 25 fps · zonas seguras: topo 270 px, base 670 px, laterais 65 px (direita 120 px).

| Modo | Quando | Extra | Principal (Carlos) | Legendas |
|---|---|---|---|---|
| **full-principal** (padrão) | hook, CTA, falas de opinião | — | tela cheia | y≈1150 |
| **split** | extra **deitado** (largura/altura ≥ 1,2 — 16:9) | **em cima, encostado no topo**: largura cheia, caixa 1080×608 em y 0 (sem faixa preta — Carlos, 02/10) | **embaixo** (de y 608 até o fim), recortada no rosto | **y≈715**, logo abaixo da divisória |
| **full** | extra **em pé** (vertical) | tela cheia (`cover`) | sai de cena; volta quando o extra termina | por cima, se a mídia não tiver texto |
| **card** | print, número, imagem rápida | cartão arredondado central (900×820) | atrás, escurecido | abaixo do cartão |

## Regras
- **O formato manda.** O `modo` escrito no roteiro é sugestão; o `gerar_props.py` mede o arquivo e corrige (e avisa no log). `card` é a exceção: é escolha de layout.
- **Transição fluida** (não pode ser corte seco): a câmera **desliza** entre tela cheia e o painel de baixo em `LAYOUTS.split.transicaoFrames` (10 frames ≈ 0,4 s), com curva suave, e o extra entra deslizando de cima. Na saída o caminho é o inverso: o extra sai e o Carlos volta a ocupar a tela.
- **Abrir com a imagem do CONTEÚDO em tela cheia** (voz do Carlos por cima) e o Carlos entra depois — teste C5/C10/C20 (decisão de 17/10, `_controle/estrategia-de-alcance.md` §2.8). **Fechar** com o Carlos em tela cheia (CTA).
- Não ficar mais de ~8 s sem mudança visual (extra, zoom ou texto).
- **O vídeo final é cru:** extra que falta não vira etiqueta no render de entrega (`gerar_props.py --final`). A etiqueta "EXTRA Exx FALTANDO" existe só no preview/revisão, para eu e você sabermos o que ainda falta; o QA reprova até o arquivo chegar.
- Crédito de extras de terceiros: "Fonte: X", pequeno, dentro da zona segura.
