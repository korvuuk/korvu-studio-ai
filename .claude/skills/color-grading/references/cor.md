# Notas técnicas de cor

## Ordem da cadeia (por segmento do corte, e por extra de câmera)
```
corte.mp4 / extras/<ID>.mp4  (câmera: H.264 4:2:2 10-bit V-Log, range limitado · tela/celular: SDR)
  → [HDR→SDR só se o stream ainda for HDR]
  → RGB 16 bits (gbrp16le, matriz bt709, in_range=tv: limited→full)          ← nada a 8 bits daqui…
  → trim do segmento (frames exatos da EDL)
  → [LUT de entrada V-Log→Rec.709: só câmera com perfil vlog]
  → primária (curves por canal: ganho nos meios-tons com roll-off)
  → LUT da marca (lut3d tetraédrica) [misturada com a primária se --intensidade < 1]
  → concat → yuv420p bt709 limited + tags (setparams) [+ grão]               ← …até aqui (encode 8-bit)
  → H.264 CRF 16, mesmo fps da fonte (-r da fonte se CFR; passthrough se VFR), áudio copiado
Segmentos tela-* e extras não-câmera: nunca recebem nada de cor.
```
`curves`, `lut3d`, `blend` e `concat` trabalham em gbrp16le (medido: 877 níveis de entrada → 877 de saída); o teste
confirma > 700 níveis distintos do gradiente 10-bit depois de entrada+curves+LUT, antes do encode 8-bit.

## Perfil e tipo de cada fonte
- `edicao/fontes.json`: `fontes.<id>.tipo` (`camera|celular|tela`) e `perfil` (`vlog|sdr`); `extras.<Exx>` idem.
- Sem `perfil`: câmera → env `CAMERA_PERFIL` (padrão `vlog`); celular/tela → `sdr`.
- Sem `tipo`: pelo nome (`tela-*` → tela, `celular-*`/`iphone*`/`img_*` → celular, resto → câmera).
- `criar_lut.py`: `--perfil` > fontes.json do vídeo (se a amostra está em `edicao/fontes/`) > `CAMERA_PERFIL`.

## Entrada V-Log / V-Gamut (Panasonic Lumix S5IIX)
### Qual LUT
1. `00-marca/cor/luts/panasonic/*V709*.cube` (oficial, descarregada pelo Carlos) — preferida.
2. `00-marca/cor/luts/entrada-camera.cube` (gerada por `gerar_entrada_vlog.py`, `"provisorio": true` no JSON).
Sem nenhuma e com fonte V-Log → erro com instruções (V-Log sem transformação estraga a medição da primária).

### Range (legal vs. full) — a convenção
- A curva V-Log é definida em **códigos 10-bit**: `V = código/1023` (preto 0% = 128, 18% = 433, 90% = 602).
- A câmera grava YUV com tag **limitado** (tv). O filtergraph faz `scale=in_color_matrix=bt709:in_range=tv,format=gbrp16le`
  — **sempre** `tv` para V-Log, mesmo que o arquivo venha marcado `pc` (aviso impresso) — portanto o lut3d vê
  `x = (código − 64)/876` por canal (64 → 0, 940 → 1).
- A LUT gerada desfaz isso exatamente: `V = (64 + 876·x)/1023`. É a mesma convenção do Resolve/Premiere em
  "video levels" e das LUTs oficiais da Panasonic → a oficial entra no lugar da gerada sem mudar mais nada.
- Super-brancos acima de 940 (> +6.8 stops sobre o cinza) são cortados na conversão; a S5IIX satura antes (~+6 stops).
  Códigos abaixo de 128 (abaixo do preto V-Log) → linear ≤ 0 → preto.

### Transformação gerada (65³)
`log_decoding_VLog` → linear V-Gamut → `RGB_to_RGB` V-Gamut→BT.709 (ambos D65, sem adaptação cromática)
→ exposição (ganho que mantém 18% em 0.18; = 1.0 porque a matriz preserva o branco)
→ soft-clip de gamut (RGC simplificado: distância ao acromático > 0.8 comprimida; 1.2/1.3/1.3 → 1.0)
→ curva de tom por canal `f = m·(x/(x+s0))^p`, `g = f²/(f+t)` (p = 1.3, toe t = 0.012, `m` faz a assíntota = 1.0,
  `s0` resolvido para o cinza sair em 0.43) + reconstrução de 70% do canal do meio (preserva a matiz)
→ código = `g^(1/2.4)` (inverso do EOTF **BT.1886**, Lb = 0: a curva já produz luz de ecrã; o OETF BT.709 de câmera
  aplicaria o gamma de sistema duas vezes) → clamp 0–1.

| stops vs. cinza | −6 | −4 | −2 | 0 | +1 | +2 | +2.3 (90%) | +3 | +4 | +5 | +6 | +6.8 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| código de saída | 0.018 | 0.069 | 0.201 | **0.430** | 0.570 | 0.707 | 0.746 | 0.819 | 0.897 | 0.945 | 0.971 | 0.983 |

- 65³ (e não 33³) porque a curva log→ecrã é muito curva nas sombras/altas; a LUT criativa continua 33³.
- Matiz (CIELAB) medida no teste, ida e volta V-Log: pele escura/média/clara dentro de ±2°.
- É um equivalente técnico da V-709 (cinza 42–44%), **não** a LUT oficial; o look vem da LUT criativa.

### Rotação e 4K
- Arquivos da câmera na vertical: 3840×2160 + display matrix ±90°. O ffmpeg auto-roda antes do `-vf`;
  `_comum.dims_exibidas()` troca largura/altura para o redimensionamento. Para ler, reduz-se primeiro no YUV
  10-bit e só depois se converte para gbrp16le + lut3d (um frame 4K não passa pelo lut3d em resolução total).
- Criar um arquivo rodado para testes: `ffmpeg -display_rotation -90 -i in.mov -c copy out.mov`
  (−90 → a coluna da esquerda gravada aparece no topo).

## Outras entradas (`entrada.py`)
- **celular**: iPhone grava HDR (HLG `arib-std-b67`, ou Dolby Vision sobre HLG) em bt2020. Se o stream
  ainda é HDR (`color_transfer` = `smpte2084`/`arib-std-b67` ou side data DOVI) → `zscale` para linear
  (npl=100) → `gbrpf32le` → primárias bt709 → `tonemap=hable:desat=0` → bt709 limited. Se a ingestão já
  converteu (tags bt709), **não** se aplica de novo — a deteção é pelo stream, não pelo nome.
- **camera perfil sdr**: passthrough. **tela**: nunca transformada.

## LUT da marca
- **Domínio**: Rec.709, gamma de ecrã (~2.4), valores RGB 0–1 **full range** — para câmera V-Log, é a imagem
  **depois** da entrada V-Log→709 (o `criar_lut` e o `aplicar_cor` aplicam a mesma entrada).
- **Tamanho 33³** (35 937 pontos): padrão Resolve/Premiere; suficiente para looks suaves, ficheiro pequeno.
  17³ dá bandas em gradientes; 65³ não traz ganho visível para transferências estatísticas.
- **Interpolação tetraédrica** (`interp=tetrahedral`): usa 4 vértices em vez de 8; preserva melhor a
  diagonal de cinzentos (neutros continuam neutros) e é o padrão dos coloristas. A trilinear só é usada em
  numpy para estatísticas (diferença média medida < 0.002).
- **Formato .cube**: `LUT_3D_SIZE 33`, `DOMAIN_MIN/MAX`, linhas "R G B" com **R a variar mais depressa**.
  O teste compara ffmpeg vs numpy para garantir a orientação.
- **Construção**: a transferência é ajustada entre *pixels da amostra* (depois da transformação de entrada)
  e *pixels das referências* (mesmo nº de pixels por imagem), e o **mesmo modelo** é aplicado à grade identidade:
  - `mkl`: Monge–Kantorovich (color-matcher) = `M·(x − μ_amostra) + μ_ref`. Linear, estável, bom padrão.
    O script verifica que o modelo reproduz a saída do `ColorMatcher` (erro < 1e-6).
  - `hm-mvgd-hm` / `hm-mkl-hm`: curva 1D por canal (quantis 0.1–99.9%, suavizada, monótona, extensão de declive 1
    fora do intervalo) → MKL → nova curva 1D. O estágio central é sempre MKL (a solução analítica MVGD exige
    correspondência pixel a pixel entre imagens, que não existe entre amostra e referência).
  - `reinhard`: média/desvio por canal em lαβ (log-LMS), com as matrizes do color-matcher.
- **Proteção de pele**: o peso de pele é calculado na cor de **entrada** (YCrCb clássico: Cr 133–173,
  Cb 77–127, Y 0.1–0.99, bordas suaves). Nesses pontos, a matiz de saída volta para a de entrada na proporção
  `--proteger-pele`, a mudança de saturação reduz-se a metade disso e a **luminância (Y) de saída mantém-se**
  (o contraste do look continua a atuar na pele).
- **Intensidade**: `saída = x + (LUT(x) − x)·intensidade`, depois clamp 0–1.
- **Sanidade**: rampa de cinzentos monótona; % de pretos esmagados (max < 0.02) e brancos estourados
  (min > 0.985) na amostra com LUT; o ffmpeg tem de conseguir carregar o `.cube`.

## Referências (mosaicos)
- `00-marca/cor/referencias/LOOK-REFERENCIA.md` descreve o look alvo ("Tenet"). O `criar_lut` lê **todas** as imagens
  da pasta (não as subpastas), por isso um mosaico tem de ser dividido: `dividir_mosaico.py` deteta faixas separadoras
  (linhas com desvio-padrão < 0.025 e pretas/brancas, ou < 0.006 de qualquer cor) e, sem elas, costuras (salto > 0.06
  entre linhas vizinhas em > 50% das colunas); painéis < 6% da altura são descartados; bordas uniformes aparadas.
  O mosaico original vai para `referencias/_mosaicos/`.

## Primária automática (`aplicar_cor.py`)
- Agrupa segmentos por `(fonte, take)` — o mesmo take partido em vários segmentos recebe a mesma correção.
  Cada extra de câmera é um grupo próprio, com o mesmo alvo.
- Mede (4 fps, 270 px) **depois da entrada V-Log→709** (reduzido no YUV 10-bit, LUT a 16 bits): luminância média
  (Rec.709, sem recortados) e gray-world em meios-tons (Y 0.12–0.88, sem pele, sem recortados), preferindo pixels
  quase neutros (sat < 0.12, depois < 0.25).
- Alvo (`alvo_primaria` no JSON da LUT) = mesma medição na amostra da LUT, isto é, a exposição/neutro
  que a LUT leva até à média da referência.
- Exposição: `EV ≈ 2.2·log2(alvo/medido)` limitado a `--limite-ev` (padrão ±0.5); ganho `2^(EV/2.2)` em valores codificados.
- Balanço: razões de canal normalizadas pela luminância, limitadas a `--limite-wb` (padrão ±8%).
- Aplicação por `curves` (pchip, monótona): `y = x·k / (1 + (k−1)·xⁿ)` → ganho k nos meios-tons,
  y(0)=0 e y(1)=1 (brancos não estouram nem ficam cinzentos). n = 4 até k = 4/3 (histórico); acima, n = 1 + 1/(k−1)
  para continuar monótona. Faixa de ganho = a dos limites (nunca menor que 0.7–1.3).
- Quando subir os limites: take exposto > 0.5 stop diferente (ETTR desigual, nuvem) → `--limite-ev 1.0`;
  luz mista/Kelvin errado → `--limite-wb 0.12–0.15`. Mais que isso: corrigir na gravação.
- Limitações: gray-world engana-se com cenários dominados por uma cor (parede verde, luz neon).
  Nesse caso `--sem-primaria` ou corrigir na gravação. Em V-Log a exposição é corrigida já em Rec.709 (depois da curva
  de tom), o que é aproximado para diferenças grandes — mais uma razão para expor igual na câmera.

## Extras (B-roll)
- `fontes.json.extras.<Exx>.tipo == "camera"` → `edicao/extras/<Exx>.mp4` → `edicao/extras/<Exx>-cor.mp4`
  (entrada + primária para o mesmo alvo + mesma LUT/intensidade + mesmo `--grao`; 8-bit yuv420p bt709; fps/frames iguais;
  áudio copiado). Outros tipos (tela, print, imagem, video, animacao) nunca: não é gerado `-cor`.
- `--so-extras` mantém o relatório do corte em `correcoes.json` e só atualiza `extras` (PNGs em `antes-depois-extras.png`
  e `scopes-extras.png`, para não apagar a vista do corte); `--sem-extras` não toca nos extras.

## ffmpeg (7.1 estático)
- `-/filter_complex arquivo` lê o filtergraph de um arquivo (os `filtro*.txt` ficam guardados para depuração).
- Caminhos com espaço dentro de opções de filtro: entre aspas simples (`file='/…/CONTENT AI/…cube'`).
- As opções `-color_primaries/-color_trc` de saída não passam pelo filtergraph: usar
  `setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv` no fim da cadeia.
- `trim=start_frame/end_frame` + `setpts=PTS-STARTPTS` + `concat` mantém o nº exato de frames.
  fps nunca é convertido: fonte CFR → `-r` = o `r_frame_rate` da própria fonte (com `-fps_mode passthrough` o mp4
  perdia a duração do último frame e o fps médio saía 30.18 em vez de 30); fonte VFR → `-fps_mode passthrough`.
- Vectorscope do ffmpeg: x = Cb, y = 255 − Cr (8 bits); a linha de pele desenhada pelo `scopes.py` passa pelo
  tom de pele médio (~123° no vectorscope clássico).
