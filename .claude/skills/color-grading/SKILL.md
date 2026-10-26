---
name: color-grading
description: Cor dos Reels da Korvu — LUT de entrada V-Log→Rec.709 da Panasonic Lumix S5IIX (gerada ou oficial), criar a LUT fixa da marca a partir de referências (/criar-lut), aplicar cor ao corte e às cenas extras de câmera (entrada V-Log + primária automática por take + LUT + grão, antes dos gráficos) (/cor), dividir mosaicos de referência e analisar scopes (waveform, parade RGB, vectorscope). Usar sempre que pedirem LUT, look, grading, V-Log, correção de cor, exposição/balanço de branco ou scopes.
---

# Color grading (agente `colorista`)

**Princípio:** um único look da marca (LUT fixa `korvu-look-vN.cube`) em todos os vídeos. Por vídeo
só se faz a **primária automática** (igualar exposição e balanço de branco de cada take ao que a LUT
espera). Nada de LUT nova por vídeo.

**Câmera do Carlos:** Panasonic Lumix **S5IIX** em **V-Log / V-Gamut**, 4K 25p **4:2:2 10-bit** (MOV H.264/HEVC
ou ProRes 422 HQ). O corte (`edicao/corte.mp4`) e os extras de câmera chegam **ainda em V-Log**, 1080×1920,
25 fps, H.264 4:2:2 10-bit. Por isso toda imagem de câmera passa por esta cadeia, a 16 bits por canal:

```
V-Log 10-bit ──► ENTRADA (V-Log→Rec.709) ──► PRIMÁRIA (por take) ──► LUT CRIATIVA (korvu-look) ──► GRÃO (opcional) ──► 8-bit bt709
```

Regras rígidas:
- **Nunca recebem cor:** gravações de ecrã (`tela-*`) e extras de tipo `tela`, `print`, `imagem`, `video`, `animacao`.
  Só o principal de câmera e os **extras de tipo `camera`** (B-roll da Lumix) são graduados — com a **mesma** cor.
- Cor é aplicada **antes** do Remotion (legendas, títulos, animações ficam por cima, sem LUT).
- Nunca editar à mão um `.cube`. Para mudar o look, criar **nova versão** (`v2`, `v3`…) e pedir aprovação ao Carlos.
- Scripts sempre da raiz do projeto com `uv run python .claude/skills/color-grading/scripts/<script>.py`.
- Perfil de cada fonte: `edicao/fontes.json` (`"perfil": "vlog"|"sdr"`, também em `"extras"`); sem ele, câmera usa
  a env `CAMERA_PERFIL` (padrão `vlog`). Celular e tela são SDR (iPhone HDR é convertido automaticamente).
- Detalhes técnicos (range legal/full, curva de tom, LUT 65³/33³, tetraédrica, pele): `references/cor.md`.

## 0. LUT de entrada V-Log → Rec.709 (uma vez)

Duas opções; o `entrada.py` escolhe sozinho e **imprime qual está a usar**:

1. **LUT oficial da Panasonic (preferida quando existir).** O Carlos descarrega ele mesmo do site da Panasonic
   (LUT "V-Log → V-709" em `.cube`) e coloca em `00-marca/cor/luts/panasonic/` — qualquer nome com `V709`,
   ex. `VLog_to_V709_forV35_ver100.cube`. Nunca descarregar automaticamente.
2. **LUT gerada (provisória, fallback):** `00-marca/cor/luts/entrada-camera.cube` (65³) + `.json` com `"provisorio": true`.
   ```bash
   uv run python .claude/skills/color-grading/scripts/gerar_entrada_vlog.py [--forcar] [--cinza 0.43] [--contraste 1.3]
   ```
   V-Log → linear V-Gamut → BT.709 → curva fílmica com roll-off das altas → Rec.709 (BT.1886). Cinza 18% → 43%,
   +5 stops → ~94%, +6 stops → ~97% (nunca recorta), pele sem desvio de matiz.

Conferir para um arquivo: `uv run python .claude/skills/color-grading/scripts/entrada.py <video>`.
**Se a LUT de entrada mudar** (p. ex. chegou a oficial), refazer o `/criar-lut` numa versão nova: a LUT criativa foi
ajustada sobre a imagem que a entrada antiga produzia.

### Exposição em V-Log (conselhos para o Carlos)
- ISO base V-Log da S5IIX: **640** (e 4000 no segundo nativo). Usar ND para controlar a luz, não o ISO.
- **Cinza 18% ≈ 42 IRE** em V-Log; pele clara ≈ 50–55 IRE, pele morena/escura ≈ 38–48 IRE. Nada de pele acima de ~60 IRE.
- Pode expor 1/3–2/3 de stop à direita (menos ruído nas sombras), mas **igual em todos os takes**. A primária só
  corrige ±0.5 EV por padrão.
- Nunca subexpor: o preto do V-Log está no código 128 e as sombras de V-Log são ruidosas. Zebra ~90% nas altas.
- Balanço de branco **fixo em Kelvin** (nada de AWB); o mesmo em todos os takes do dia.
- Monitorar com a LUT V-709 na câmera (View Assist) mas **gravar V-Log limpo** (sem LUT "baked").

## /criar-lut — criar ou revisar o look da marca

1. **Referências** em `00-marca/cor/referencias/` (≥ 3 imagens com o look desejado, com pele). O look atual está descrito
   em `00-marca/cor/referencias/LOOK-REFERENCIA.md` (look "Tenet": frio, contido, pele natural). **Mosaicos** (vários
   frames empilhados numa imagem) têm de ser divididos antes — o `criar_lut` lê todas as imagens da pasta:
   ```bash
   uv run python .claude/skills/color-grading/scripts/dividir_mosaico.py 00-marca/cor/referencias/ref-tenet-01.jpg [--n auto|4] [--ignorar 3]
   ```
   Deteta separadores pretos/uniformes ou, sem eles, as "costuras" entre frames; `--n 4` divide em 4 faixas iguais se a
   deteção falhar. Grava `ref-tenet-01a.jpg`, `…b.jpg`… e move o mosaico para `referencias/_mosaicos/`.
   `--ignorar 3` salta um painel (p. ex. o close desfocado com o título).
2. **Amostra**: o arquivo **cru da câmera** serve direto — `videos/<slug>/brutos/principal/camera-00-cor.mov` (4K, rodado,
   V-Log 10-bit): a rotação é respeitada, os frames são reduzidos e passam pela mesma entrada V-Log→709 do `/cor`.
3. Rodar:
   ```bash
   uv run python .claude/skills/color-grading/scripts/criar_lut.py \
     --referencias 00-marca/cor/referencias --amostra videos/<slug>/brutos/principal/camera-00-cor.mov \
     --tipo camera --versao v1 [--perfil vlog|sdr] [--metodo mkl] [--intensidade 0.8] [--proteger-pele 0.7]
   ```
   Saídas: `00-marca/cor/luts/korvu-look-v1.cube` + `.json` e `00-marca/cor/analises/v1-antes-depois.png`.
4. **Ver** o `v1-antes-depois.png` com o Read (colunas: amostra já em Rec.709 | com LUT | referência mais próxima) e ler a
   tabela luma/contraste/saturação impressa (também em `estatisticas` no JSON). Rodar `scopes.py` num frame com LUT se tiver dúvida.
5. Avaliar com os critérios abaixo. Ajustar e criar nova versão (`--versao v1b`, `--forcar` para sobrescrever a mesma):

   | Problema visto | Ajuste |
   |---|---|
   | Look forte demais / artificial | `--intensidade 0.6` |
   | Look fraco, longe da referência | `--intensidade 0.9–1.0` |
   | Pele alaranjada/esverdeada/magenta | `--proteger-pele 0.85–1.0` |
   | Pele "morta", sem o calor da referência | `--proteger-pele 0.4–0.5` |
   | Contraste/curva errada mas cor ok | `--metodo hm-mvgd-hm` (casa histograma por canal; mais fiel à curva da referência, mais agressivo) |
   | Cores estranhas em saturados | `--metodo reinhard` (mais suave) ou reduzir intensidade |
   | Aviso de pretos esmagados/brancos estourados | reduzir intensidade; se persistir, trocar referências (muito contrastadas) |
   | Amostra (1.ª coluna) lavada/cinzenta | a entrada V-Log não foi aplicada: ver `entrada.py <amostra>` / `--perfil vlog` |

6. Mostrar ao Carlos o antes/depois e **esperar aprovação**. Aprovado → no `.json` da LUT pôr
   `"aprovada": true` e `"aprovada_em": "<ISO>"`. O `aplicar_cor.py` usa por padrão a versão mais alta aprovada.

## /cor — aplicar cor a um vídeo (corte + extras de câmera)

Pré-requisitos: `edicao/corte.mp4`, `edicao/edl.json` (segmentos/takes/fontes) e, de preferência, `edicao/fontes.json`
(perfil por fonte e lista de `extras`).

1. Rodar:
   ```bash
   uv run python .claude/skills/color-grading/scripts/aplicar_cor.py videos/<slug> [--lut <cube>] [--intensidade 1.0] [--grao 0.3]
   ```
   Saídas em `videos/<slug>/edicao/cor/`: `corte-cor.mp4` (8-bit yuv420p bt709, mesmo fps e nº de frames), `antes-depois.png`,
   `scopes.png`, `correcoes.json` (medição e correção por take e por extra) e `filtro*.txt` (filtergraphs usados).
   Cada extra de tipo `camera` listado em `fontes.json` → `edicao/extras/<ID>-cor.mp4` (entrada V-Log + primária para o
   **mesmo alvo** + mesma LUT + mesmo `--grao`; áudio copiado). Os outros tipos de extra nunca são tocados.
2. Ler o resumo impresso: LUT de entrada usada, por take/extra EV aplicado e ganhos RGB. Notas "limitada" = fora dos
   limites da primária — ver abaixo.
3. **Ver** `antes-depois.png` e `scopes.png` com o Read e aplicar os critérios.
4. Ajustes (repetir e rever):
   - `--intensidade 0.7` — look mais leve só neste vídeo.
   - `--sem-primaria` — a correção automática piorou um take (cenário muito colorido engana o gray-world).
   - `--limite-ev 1.0` (padrão 0.5) — quando um take foi exposto de propósito ou por engano mais de meio stop diferente
     e o waveform continua com alturas diferentes entre takes. Acima de ~1 EV é melhor regravar/corrigir na câmera.
   - `--limite-wb 0.12–0.15` (padrão 0.08 = ±8%/canal) — luz mista ou Kelvin errado num take. Subir os limites aumenta o
     risco de o gray-world "corrigir" um cenário que é mesmo colorido: rever a pele no vectorscope.
   - `--so-extras` (só gradua os extras; o corte e o seu relatório ficam; PNGs em `antes-depois-extras.png` /
     `scopes-extras.png`) · `--sem-extras` (só o corte).
   - `--sem-entrada` — só se a ingestão já tiver aplicado a V-Log→709 (senão a imagem sai lavada).
5. Aprovado → atualizar `videos/<slug>/status.json` (estado `cor`) e a linha do `_controle/tracker.md`.
   O Remotion usa `edicao/cor/corte-cor.mp4` e `edicao/extras/<ID>-cor.mp4` (via symlink `remotion/public/_render/<slug>/`).

## Critérios de aprovação

- **Pele natural**: no vectorscope o "braço" da pele fica em cima (ou muito perto) da linha laranja tracejada,
  entre o R e o Yl. Nada de pele puxada para magenta, verde ou laranja-néon. No antes/depois, o rosto deve
  parecer saudável, sem cor de plástico.
- **Sem pretos esmagados**: no waveform, o chão da imagem acima de ~0–2 IRE com detalhe (não uma linha
  grossa colada ao 0). O JSON da LUT tem `pretos_esmagados_pct` (< 2%).
- **Sem brancos estourados**: picos até ~95–100 IRE; nada achatado no topo em áreas grandes (janelas podem estourar).
  `brancos_estourados_pct` < 2%.
- **Exposição**: pele de meio-tom tipicamente entre ~45 e 70 IRE; takes consecutivos com a mesma altura no waveform.
- **Contraste/saturação próximos da referência**: comparar `contraste_std` e `saturacao_media` de
  `amostra_com_lut` com `referencia` (diferença de até ~15% é ok). No parade, as três colunas de um objeto neutro
  (parede, camisa cinza) devem ficar à mesma altura, salvo o tom intencional do look (quente = R um pouco acima de B).
- **Consistência**: takes diferentes do mesmo vídeo — e os extras de câmera — com o mesmo brilho e temperatura aparentes.
- **Tela intocada**: segmentos `tela-*` idênticos ao corte; extras não-câmera sem `-cor.mp4`.

## Como ler os PNGs

- `antes-depois` (LUT): cada linha é um frame da amostra; 3.ª coluna é a referência mais parecida (recortada).
  Pergunta-chave: "a coluna do meio parece da mesma família da 3.ª, sem estragar a pele?"
- `antes-depois` (/cor): com V-Log são 3 colunas — **ANTES (V-Log)** lavado é normal | **ENTRADA → Rec.709** (deve parecer
  vídeo "normal", sem look; se estiver escura/clara demais o problema é exposição na câmera) | **DEPOIS** (look final).
  Linhas com legenda laranja `EXTRA Exx` são as cenas extras de câmera.
- `scopes.png`: esquerda = antes (já em Rec.709 quando há V-Log), direita = depois, com os frames lado a lado.
  Waveform = brilho por coluna (0–100 IRE); parade = R, G, B separados; vectorscope = matiz (ângulo) e saturação (distância ao centro).
- Scope avulso: `uv run python .claude/skills/color-grading/scripts/scopes.py <imagem_ou_video> [--t 3.2]`.
- Teste do skill: `uv run python tests/cor/test_cor.py` (sintético; não toca em `00-marca/`).
