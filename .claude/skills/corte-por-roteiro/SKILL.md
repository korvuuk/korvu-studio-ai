---
name: corte-por-roteiro
description: Edita o vídeo bruto do Carlos seguindo o roteiro (roteiro.json) — transcreve o vídeo PRINCIPAL com tempo por palavra, alinha a fala às linhas L01, L02…, escolhe o melhor take de cada linha, corta erros, falsos começos, repetições, muletas e pausas longas, encaixa as CENAS EXTRAS (B-roll E01, E02…) por cima, gera a EDL para aprovação e depois renderiza o corte com ffmpeg e verifica o resultado contra o roteiro. Use quando houver brutos em videos/<slug>/brutos/ para editar, no /editar e na etapa de corte do /renderizar, quando o Carlos pedir para trocar take ("L05 usa T1"), tirar/incluir linha, refazer a EDL, conferir cenas extras ou conferir se o corte bate com o roteiro.
---

# Corte por roteiro

Transforma `videos/<slug>/brutos/` (vários takes, tropeços, "de novo") num corte limpo na ordem do
roteiro: **ingest → transcribe → locutores → align → edl → PARA (aprovação) → render → filmstrip → verify**.
Contratos de dados: `docs/contratos.md` (§0 principal + extras, §1b cenas extras, §2 transcrição, §2b locutores,
§3 alinhamento, §4 EDL, §5 mídia, §8 status). Algoritmo, limiares e pesos: `references/algoritmo.md`.

**Método de gravação "ChatGPT monitor"** (o padrão do Carlos): o ChatGPT Voice, no alto-falante do celular na sala
(sem fone), lê cada linha e o Carlos repete para a câmera; o ChatGPT também corrige ("de novo", "repete: …", "faltou
a palavra X", "próxima"). O áudio da câmera tem **duas vozes com o mesmo texto**. O `locutores.py` separa quem é quem
e o corte usa **só a voz do Carlos**: leituras e falas de monitor da IA nunca são candidatas nem vazam nas bordas
(nem a cauda da reverb). Gravação sem IA (1 voz) funciona igual — tudo vira `carlos`.

## Formato do projeto (câmera do Carlos: Lumix S5IIX)
- **Frame rate = `FPS_PROJETO` (padrão 25)** em tudo: ingestão CFR, EDL (`"fps": 25`), corte, preview, filmstrip,
  verificação e Remotion. Câmera grava 25p. Celular/tela a 30/60 fps viram 25 com o filtro `fps` (aviso: quadros
  descartados/duplicados). 50p vira 25 limpo (1 de cada 2). Nunca misture 25/30 (judder).
- **Câmera em V-Log (V-Gamut), 4K 4:2:2 10-bit** (`CAMERA_PERFIL`, padrão `vlog`). A ingestão **não converte o
  log** — só reduz 4K → 1080×1920 (lanczos, em 10 bits). A transformação V-Log → Rec.709 é do colorista (`/cor`).
- **Intermediários 10-bit:** H.264 High 4:2:2 10-bit (`yuv422p10le`, CRF 12), tags bt709.
  `edicao/fontes/*.mp4` = **1440×2560 supersampled** (o punch-in do corte recorta daqui e ainda REDUZ para 1080 —
  1.12–1.33 sem ampliar); `edicao/corte.mp4` = 1080×1920 (o colorista lê este). Cada intermediário é decodificado
  logo depois de gerado (a fonte, inteira). Obs.: o libx264 4:2:2 10-bit do ffmpeg estático gera stream ilegível em
  larguras 1920/3840 com várias threads — 1440 e 1080 decodificam; se um dia a 1440 falhar, o ingest recodifica em
  HEVC main422-10 sozinho (aviso).
- **Áudio sem perdas até o fim:** o ingest grava `edicao/audio48k/<fonte>.wav` (48 kHz **24-bit mono** da faixa a:0
  da câmera — na S5IIX a:0/a:1 têm a voz, a:2/a:3 mudas), só com **passa-altas 60 Hz** (12 dB/oit.) — **sem redução
  de ruído** (o `afftdn=nf=-25` antigo tirava ~10 dB de 5–16 kHz: voz abafada). O `render_corte` monta o áudio do
  corte desse WAV e grava `edicao/corte-audio.wav` (24-bit); o `audio.py` masteriza dele → o AAC final é o único
  encode com perdas.
- **LUT de visualização:** o que é mostrado antes da cor (`preview.mp4`, filmstrips, candidatos de capa) aplica
  `00-marca/cor/luts/entrada-camera.cube` (lut3d tetraédrica) **só nos trechos de câmera em log**; gravação de tela
  nunca. Sem esse arquivo: `[AVISO] sem LUT de entrada V-Log — imagem vai parecer lavada`. (Teste: `LUT_ENTRADA_CAMERA`
  aponta para outra `.cube`.) A saída final (Remotion/Instagram) continua 8-bit yuv420p bt709.

## Pré-requisitos
- `videos/<slug>/roteiro.json` (gerado pelo `parse_roteiro.py` da skill de roteiro, com `extras` e `extras_ref`).
  Sem ele, pare e peça.
- Brutos (`.mov/.mp4/.m4v`; extras também `.png/.jpg/.webp/.heic`):
  - `brutos/principal/` — o Carlos falando (A-roll): `camera-01.mov`, `camera-02.mov`, `celular-01.mp4` (sem prefixo
    = câmera). Vários arquivos de câmera são lidos em ordem alfabética (= ordem "cronológica" dos takes).
    `camera-00-cor.mov` (qualquer `*-cor.*`) = **amostra de cor** para o colorista: não é ingerida, transcrita nem
    entra na EDL (fica no `fontes.json` como `"tipo": "amostra_cor"`).
  - `brutos/extras/` — cenas extras (B-roll) **nomeadas pelo ID**: `E01-chatgpt.mov`, `E02.png`, `E03-noticia.mp4`…
    O tipo vem de `roteiro.json.extras[].tipo` (senão do nome: tela/print/imagem/video/camera).
  - Legado: arquivos soltos em `brutos/` — `camera-*`/`celular-*` = principal; `tela-*`, `E01-*` e imagens = extras.
- Rodar sempre da raiz do projeto, com caminhos entre aspas (a pasta tem espaço):

```bash
cd "/Users/teste/Documents/CONTENT AI"
S=".claude/skills/corte-por-roteiro/scripts"
V="videos/<slug>"          # também aceita só o slug
```

## Fluxo (siga na ordem)

1. **Ingestão** → `edicao/fontes/<stem>.mp4` (1440×2560) + `edicao/audio48k/<stem>.wav` (master 24-bit) +
   `edicao/audio16k/<stem>.wav` (principal), `edicao/extras/<ID>.mp4|.png` (extras) e `edicao/fontes.json`
   (`fontes` com `perfil` vlog/sdr, `audio` = faixa/cadeia/níveis das faixas, e `extras`).
   ```bash
   uv run python "$S/ingest.py" "$V"            # --force para refazer tudo
   uv run python "$S/ingest.py" "$V" --faixa-audio 1     # outra faixa da câmera (padrão a:0; muda -> melhor SNR)
   uv run python "$S/ingest.py" "$V" --limpar-ruido      # só se o ruído incomodar: afftdn SUAVE (piso medido)
   ```
   - Principal: 1440×2560, 25 fps CFR, 10-bit 4:2:2; câmera fica em V-Log; celular HDR/HLG/PQ → SDR (tone-map);
     rotação respeitada (3840×2160 / C4K 4096×2160 com "vertical position info" → 1440×2560, crop central 9:16).
     Reingerir NÃO invalida transcrição/locutores/alinhamento (tempos da fonte).
   - Extras: vídeo → 1080 de largura (mantém proporção), 25 fps; tipo `camera` fica V-Log 10-bit (o colorista gera
     `<ID>-cor.mp4`); tela/vídeo/print → 8-bit SDR. Imagem → PNG com lado maior ≤ 2160 px.
   - Leia os `[AVISO]`: horizontal cortado para 9:16, 30/60 fps → 25, HDR convertido, sem áudio, extra do roteiro sem
     arquivo (entra como FALTANDO), extra fora da tabela do roteiro. Repasse ao Carlos o que for relevante.

2. **Transcrição** (palavras com tempo) → `edicao/transcricao.json` — **só o principal** (extras nunca).
   ```bash
   uv run python "$S/transcribe.py" "$V"                                  # Scribe se ELEVENLABS_API_KEY existir
   uv run --extra local python "$S/transcribe.py" "$V" --engine mlx      # local (Apple Silicon), sem API
   ```
   Scribe guarda a resposta bruta em `edicao/raw/<fonte>.scribe.json` (cache; `--force` refaz a chamada) e pede
   **diarização** (`diarize=True`, `num_speakers=2` — env `SCRIBE_NUM_SPEAKERS`): o `speaker_id` vira `locutor_bruto`.
   Cache antigo sem diarização é refeito (com chave) ou usado só com a análise local (sem chave).
   `--fontes camera-02` retranscreve só uma fonte (amostras de cor são ignoradas).
   mlx: o Whisper "engole" a repetição idêntica de uma frase dita logo antes (a IA lê → o Carlos repete); por isso
   todo trecho com fala e sem palavra é re-transcrito sozinho (`lacuna … re-transcrita: +N palavra(s)` no log).

2b. **Locutores** (Carlos × IA) → `locutor`/`locutor_conf` em cada palavra da `transcricao.json` + `edicao/locutores.json`
   ```bash
   uv run python "$S/locutores.py" "$V"                     # automático (Scribe diarize se houver, senão local)
   uv run python "$S/locutores.py" "$V" --ia-primeiro       # gravou no método ChatGPT-monitor (reforça a evidência de ordem)
   uv run python "$S/locutores.py" "$V" --forcar-metodo local   # ignora a diarização do Scribe
   ```
   O `align.py` roda isto sozinho se o `locutores.json` faltar ou for mais velho que a transcrição. **Leia a saída**:
   separação acústica (≥ 3 = 2 vozes), as duas classes (graves, nível, centróide, pitch) e as evidências de qual é a IA —
   `assinatura` (celular: sem graves, mais baixo), `ordem` (a IA lê primeiro, o Carlos repete), `monitor` ("de novo",
   "próxima"…), `inscricao` (perfil do Carlos em `00-marca/voz-carlos.json` → `perfil_locutor`, ou áudio em
   `02-calibracao/amostras/`). Repasse ao Carlos: `[AVISO] evidências em conflito`, `confiança do papel baixa`,
   palavras `null` (as linhas vão para [REVISAR]), sobreposições e "só 1 voz foi separada" com `--ia-primeiro`.

3. **Alinhamento** → `edicao/alinhamento.json` + tabela no terminal (coluna `IA` = leituras da IA da linha)
   ```bash
   uv run python "$S/align.py" "$V"
   ```
   Takes só com a voz do Carlos; leituras da IA → `leituras_ia` da linha; falas de monitor → `fala_ia`.

4. **EDL** → `edicao/edl.json` (editável), `edicao/edl.md` (legível) e `edicao/preview.mp4` (540×960, 8-bit)
   ```bash
   uv run python "$S/edl.py" "$V"
   uv run python "$S/status.py" "$V" edicao
   ```
   O preview tem a mesma timeline da EDL **e o mesmo plano de zoom do corte**, com a LUT de visualização na câmera e o
   rótulo **`EXTRA E01 · split`** queimado durante cada cena extra (fundo vermelho = FALTANDO). A composição de verdade
   (split/full/card) só no Remotion.
   **Plano de enquadramento (automático):** a cada corte (troca de linha e corte interno) o enquadramento alterna
   1.00 ↔ 1.12 com a origem no rosto (OpenCV em alguns quadros de cada segmento; sem rosto → `50% 38%`) —
   `segmentos[].zoom_pecas` / `zoom_origem`, seção "Enquadramento" do `edl.md`. Linha com `ZOOM` na TELA (hook)
   começa fechada. `edl.json.zoom_no_corte: true` = o zoom é aplicado **no corte** (uma vez; o Remotion não repete).

5. **PARE — aprovação do Carlos.** Mostre o resumo do `edl.md` (linhas [REVISAR]/[PARAFRASE]/[FALTANDO],
   trechos não mapeados, **tabela "Cenas extras"** com FALTANDO, duração vs alvo) e o caminho do `preview.mp4`.
   Método ChatGPT-monitor: a linha **Locutores** (IA identificada, confiança, sobreposições), a coluna **IA · Carlos**
   (linha com `1 · 0` = só a IA leu → regravar ou tirar) e takes preteridos por `sobreposicao_ia`.
   **Não renderize o corte final** até ele aprovar (regra rígida 1 do CLAUDE.md; `--force/--auto` só se ele pedir).

6. **Aprovado** → no `edl.json`: `"aprovado": true`, `"aprovado_em": "<ISO agora>"`; depois:
   ```bash
   uv run python "$S/edl.py" "$V" --recalcular --sem-preview
   uv run python "$S/status.py" "$V" edl_aprovada
   uv run python "$S/render_corte.py" "$V"          # -> edicao/corte.mp4 (10-bit, V-Log, zoom aplicado) +
                                                    #    edicao/corte-audio.wav (24-bit); confere ±1 frame
   ```

7. **Ver os cortes** — gere e LEIA as imagens (Read) antes de seguir:
   ```bash
   uv run python "$S/filmstrip.py" "$V"             # edicao/frames/corte-NN.png + contato.png
   ```
   Em cada `corte-NN.png`: 5 frames (−0,2…+0,2 s, com a escala `×1.12`) + forma de onda de ±0,5 s, linha vermelha =
   ponto de corte; o título mostra `zoom 1.00→1.12` (vermelho `MESMO!` se não trocou). Os frames do `corte.mp4`
   recebem a LUT de visualização nos trechos de câmera (`--lut nao` desliga).
   Procure: palavra cortada (onda "cortada" no meio de uma fala), clique, enquadramento que NÃO troca no corte,
   testa/queixo cortados no 1.12 (ajuste `zoom_origem`), frame preto, imagem de lado. `contato.png` = um frame por linha.

8. **Verificação** → `qa/diff.md` (+ `qa/verificacao.json`, `qa/transcricao-corte.json`)
   ```bash
   uv run python "$S/verify.py" "$V"                # --engine mlx para rodar local
   ```
   Exit 1 se faltar linha, WER geral > 8 %, A/V fora de 1 frame (40 ms a 25 fps), fps ≠ projeto ou **voz da IA no
   corte > 0,2 s** — medida acústica (modelo por quadro do `locutores.json` no áudio do corte; só pega vazamento
   ≳ 0,5 s) **ou** conta pelas peças da EDL dentro das zonas da IA (pega vazamento curto e cauda). O esperado é 0. Linha
   "faltando (não gravada)" não é bug do corte: avise o Carlos. Depois: `status.py "$V" revisao`.

## Coluna TELA e cenas extras
Itens separados por ` · ` (ou `|`), cada um lido independentemente:

| Item | Efeito |
|---|---|
| `EXTRA: E01 split` · `EXTRA: E01 full 00:02–00:09` · `EXTRA: E03 card` | overlay `tipo: extra` (trecho do próprio extra opcional; `–` ou `-`) |
| `TEXTO: "..."` | texto na tela (por cima dos extras) |
| `ZOOM` (`ZOOM 1.2`) | punch-in no segmento |
| `tela-01 00:04–00:11 split` (legado) | extra `tela-01` (arquivo `brutos/tela-01.*`) |
| `ANIMACAO[split]: descrição` (legado) | extra de animação com id = linha (ignorado se a linha já usa um extra `animacao`) |
| `GESTO: …` · `B-ROLL: …` | anotação — ignorada |

Regras dos overlays de extra (`edl.json.overlays`, contrato §4):
- O **mesmo extra em linhas seguidas** (mesmo modo, trecho contínuo) vira **um overlay contínuo** (`linhas: ["L03","L04"]`).
- `in/out`: padrão do 0, com a duração da fala; se o extra acaba antes, **segura o último quadro** (aviso no `edl.md`).
- `arquivo`: `edicao/extras/<ID>.mp4|.png`; tipo `camera` usa `<ID>-cor.mp4` quando o colorista já gerou.
- `animacao`: `componente` = chave no `remotion/src/animacoes/registry.ts` (`"<slug>/E02"` ou `"E02"`).
- `faltando: true` se não há arquivo (ou componente, para animação): placeholder "EXTRA Exx FALTANDO" no Reel e
  **QA final reprova**. Quando o arquivo chegar: `ingest.py` + `edl.py --recalcular` (mantém a aprovação).
- `som` e `credito` vêm da tabela "Cenas extras" do roteiro (crédito aparece como "Fonte: X").

## Como ler o alinhamento / a EDL

| Status | Significado | O que fazer |
|---|---|---|
| `[OK]` | último take limpo (sim ≥ 0,80, sem tropeço) | nada |
| `[REVISAR]` | nenhum take limpo; escolhido o melhor score, ou transcrição com confiança baixa | conferir no preview; oferecer alternativa |
| `[PARAFRASE]` | melhor take com sim 0,60–0,80: disse com outras palavras | perguntar se aceita; legenda usa o que foi dito |
| `[FALTANDO]` | nada com sim ≥ 0,60 (ou só falsos começos) | ver "Fora do corte"; regravar ou tirar a linha |
| `[MANUAL]` | take escolhido pelo Carlos (difere do automático) | — |

| Flag (take) | Significado | Impede "take limpo"? |
|---|---|---|
| `false_start` | começou certo (prefixo ≥ 0,85) mas parou (< 60 % da linha) | sim |
| `recomeco` | as 2 primeiras palavras aparecem de novo dentro do take | sim |
| `final_cortado` | as 2 últimas palavras da linha não foram ditas | sim |
| `muleta` | "é…", "hum", "tipo", "né"… fora do roteiro → vira corte interno | não |
| `pausa_interna` | pausa > 0,7 s dentro da linha → encurtada para 0,25 s | não |
| `baixa_confianca` | confiança média da transcrição < 0,6 | não, mas status vira [REVISAR] |
| `sobreposicao_ia` | a IA fala colada/por cima do take (sem silêncio para cortar) | sim → outro take limpo; sem alternativa, [REVISAR] |
| `fala_ia_interna` | a IA fala num silêncio entre duas palavras do take → corte interno | não |
| `locutor_incerto` | alguma palavra do take com `locutor: null` (pode ser a IA) | não, mas status vira [REVISAR] |

`nao_mapeado` = fala do Carlos que não casou com nenhuma linha (improviso, comentários, conversa) — fica fora do corte
e aparece em "Fora do corte" no `edl.md`. Separadores falados **pelo Carlos** ("de novo", "corta", "repete", "vou de
novo") são descartados e dividem takes. Fala da IA: as leituras de linha vão para `leituras_ia` (por linha) e o resto
("de novo", "repete: …", "faltou a palavra X", "próxima", "ótimo") para `fala_ia` — tudo fora do corte, listado no
`edl.md`. A fala da IA também divide takes. Hooks alternativos (`L01B`…, `alternativa_de`) são alinhados à parte e
aparecem em `edl.json.variantes`, nunca na montagem principal.

## Pedidos do Carlos → o que editar no `edicao/edl.json` (depois SEMPRE `edl.py --recalcular`)

| Pedido | Edição |
|---|---|
| "L05 usa T1" | no segmento da L05: `"take": "L05-T1"` (ou só `"T1"`) — in/out/cortes do novo take são recalculados |
| "tira a L04" | apagar o objeto da L04 em `segmentos` |
| "coloca a L07 com o T2" | adicionar `{"linha": "L07", "take": "L07-T2"}` em `segmentos` |
| "usa 01:23–01:27 da camera-02 na L06" | `{"linha": "L06", "take": "manual", "fonte": "camera-02", "in": 83.0, "out": 87.0}` |
| "começa a L02 um pouco antes" / "corta o fim" | ajustar `in` / `out` (segundos da fonte) |
| "não corta a pausa da L04" | `"cortes_internos": []` |
| "tira o 'né' da L03" | acrescentar `[ini, fim]` em `cortes_internos` (tempos da fonte; ver palavras em `transcricao.json`) |
| "a L03 começa fechada" / "zoom maior na L03" | `"zoom": {"tipo": "punch", "escala": 1.2}` (escala do punch do segmento + 1.ª peça fechada; máx. 1.33) |
| "sem zoom na L05" / "L05 toda aberta" | `"zoom_pecas": [1.0, 1.0]` (uma escala por peça; o plano dos vizinhos se adapta) |
| "o zoom corta a testa" / "centra mais à esquerda" | `"zoom_origem": "45% 30%"` (ponto fixo do zoom; y menor = mais headroom) |
| "o E01 em tela cheia" / "mostra do 0:05 do E01" | mudar a coluna TELA do roteiro (`EXTRA: E01 full 00:05–00:12`), `parse_roteiro.py`, `edl.py --recalcular` |
| "chegou o E04" | pôr em `brutos/extras/E04-….mp4`, `ingest.py`, `edl.py --recalcular` |
| "aprovado" | `"aprovado": true`, `"aprovado_em": "<ISO>"` → passo 6 |

```bash
uv run python "$S/edl.py" "$V" --recalcular      # mantém as edições, recalcula saida_*, palavras_saida, overlays
```
`--recalcular` compara com `edicao/edl.auto.json` (valores automáticos da última geração): campo que você
mudou é preservado; troca de take recalcula in/out/cortes daquele take. Overlays (textos e extras) são sempre
recalculados a partir do roteiro + `fontes.json`. Depois de editar, mostre ao Carlos as linhas alteradas do
`edl.md` e o novo `preview.mp4`. Rodar `edl.py` **sem** `--recalcular` refaz tudo do zero (a versão anterior vai
para `edl.anterior.json`). Os `T1, T2…` são os takes listados na coluna Alternativas.

## Regras de corte (resumo)
- `in` = 1ª palavra − 0,15 s; `out` = última palavra + pausa (`normal` 0,20 s, `pausa` 0,60 s,
  `pausa_longa` 0,90 s; mínimo 0,18 s), usando o silêncio real do take; cada borda vai para o ponto mais silencioso
  em ±60 ms, mas **nunca entra na energia de uma palavra** (ataque suave / cauda medidos no áudio, + 0,04 s — nem da
  palavra vizinha) e fica na grade de frames arredondada "para fora" (o render não come o ataque).
- Muletas viram corte interno (fica 0,15 s de respiro); pausas > 0,7 s ficam com 0,25 s — as bordas também guardam
  a energia das palavras (cortes internos quantizados para dentro do trecho removido).
- **Enquadramento:** toda troca de peça (segmento ou corte interno) alterna 1.00 ↔ 1.12 com origem no rosto — o
  zoom só muda nos cortes (silêncio), nunca no meio de uma palavra.
- **Voz da IA = zona proibida** (`locutores.json.zonas_ia`, fala + cauda da reverb): `in`/`out`/pausa ficam a ≥ 0,08 s
  dela (a pausa encolhe se a IA começa a falar); IA num silêncio do take → corte interno. `edl.json.segmentos[].voz_ia`
  tem que ser 0 — editou in/out à mão e apareceu ⚠ no `edl.md`? Devolva a borda.
- Render: peças alinhadas à grade de frames do projeto (25 fps = 40 ms); cada peça recortada/escalada para o seu
  enquadramento (lanczos, 10 bits); áudio do master WAV com alças de 15 ms e `acrossfade` de 30 ms → sem cliques e
  duração exata (soma das peças); `corte-audio.wav` 24-bit ao lado do `corte.mp4`.

## Troubleshooting
- **`mlx-whisper não instalado`** → `uv sync --extra local` (ou `uv run --extra local ...`).
- **Scribe falha / sem chave** → confira `ELEVENLABS_API_KEY` no ambiente (não imprimir o `.env`); use `--engine mlx`.
  Modelo: `SCRIBE_MODEL` (padrão `scribe_v2`).
- **Whisper "engoliu" muletas ou repetições** → normal no Whisper; o Scribe é mais literal. As bordas das
  palavras são ajustadas pela energia do áudio (`--sem-refino` desliga).
- **Palavra "fantasma" no silêncio** (ex.: "E aí" no fim) → alucinação do Whisper; palavras sem energia de fala
  são descartadas automaticamente (a mensagem aparece no transcribe/verify).
- **Linha [FALTANDO] mas o Carlos gravou** → veja "Não mapeado" no `edl.md`: se ele parafraseou muito
  (sim < 0,6), use um segmento `manual` com os tempos do trecho, ou ajuste o roteiro e rode align+edl de novo.
- **Linhas parecidas trocadas** (ex.: "O primeiro truque…" / "O segundo truque…") → veja os takes no
  `alinhamento.json`; corrija com override de take.
- **Sílaba comida no começo/fim** → aumente `out`/diminua `in` 0,05–0,1 s e `--recalcular`; confira no filmstrip.
- **render_corte: "está a 30 fps" / "diferença > 1 frame"** → fonte ingerida com outro fps (ou `FPS_PROJETO` mudou):
  `ingest.py --force` + `edl.py --recalcular` e renderize de novo.
- **"não decodifica — arquivo inválido"** → intermediário corrompido pelo encoder; confira se não mudaram a largura
  dos 10-bit (1440 nas fontes, 1080 no corte — nunca 1920/3840) e rode de novo.
- **Voz abafada / sem brilho** → a ingestão não faz redução de ruído; se alguém rodou `--limpar-ruido` (ou o
  `audio.py --limpar`), reingira sem. Compare com `audio.py --medir <arquivo> --trecho INI FIM` (energia por banda).
- **`zoom … AMPLIA o intermediário`** → fonte ingerida no formato antigo (1080): `ingest.py --force`.
- **`EDL sem plano de zoom`** → EDL antiga: `edl.py --recalcular` (gera `zoom_pecas` + `zoom_no_corte`).
- **Zoom no rosto errado / testa cortada** → `zoom_origem` do segmento (ex. `"48% 30%"`) + `--recalcular`; sem rosto
  detectado o `edl.md` mostra `padrão (rosto 0/3)`.
- **Imagem lavada/cinza no preview/filmstrip** → é V-Log sem a LUT de visualização: falta
  `00-marca/cor/luts/entrada-camera.cube` (o `/criar-lut` gera). A cor final é trabalho do `/cor`.
- **Câmera virada/deitada** → confira `rotacao` e `original` no `fontes.json` (a S5IIX grava 3840×2160 + rotação
  quando está na vertical). Arquivo horizontal sem rotação é cortado ao centro para 9:16 (aviso no ingest).
- **HDR lavado/escuro (celular)** → confira `ffprobe` do bruto (`color_transfer` arib-std-b67/smpte2084); a ingestão
  usa `zscale+tonemap=hable`. Câmera marcada como HLG com `CAMERA_PERFIL=vlog` → aviso e tone-map (ajuste o perfil).
- **Extra FALTANDO** → arquivo com o ID no nome em `brutos/extras/` (ex.: `E04-demo.mp4`), `ingest.py`,
  `edl.py --recalcular`. Animação: registrar o componente em `remotion/src/animacoes/registry.ts`.
- **[BLOQUEADO] edl não aprovada** → é proposital. Aprovação do Carlos primeiro (ou `--preview`).
- **verify: "extras"** (trechos extras de fala) → sobrou fala fora do roteiro no corte; confira `cortes_internos`/
  `in`/`out` da linha vizinha.
- **Linha [FALTANDO] com `IA · Carlos` = `1 · 0`** → só a IA leu; o Carlos não repetiu (ou o Whisper engoliu a
  repetição: veja `lacuna … re-transcrita` no log do transcribe e o áudio em volta da leitura). Nunca use a leitura da IA.
- **"só 1 voz foi separada" / separação na zona cinzenta, mas o ChatGPT falava** → voz da IA parecida com a do Carlos
  e/ou celular alto e perto do microfone. Rode `locutores.py --ia-primeiro` (as 1.ªs leituras de cada par ficam `null` →
  [REVISAR]) e, se possível, `ELEVENLABS_API_KEY` + `transcribe.py --engine scribe --force` (diarização). Na próxima
  gravação: ver "Gravação com o ChatGPT".
- **`evidências em conflito` / `confiança do papel baixa`** → o script não sabe qual classe é a IA: palavras `null`,
  linhas [REVISAR]. Confira no preview; um perfil do Carlos (`00-marca/voz-carlos.json` → `perfil_locutor` com
  `pitch_hz`, `centroide_hz`, `graves_db`, ou um áudio só dele em `02-calibracao/amostras/`) desempata.
- **verify: "voz da IA no corte"** → veja os `trechos` no `qa/diff.md`: take com `sobreposicao_ia` sem alternativa
  (regravar a linha) ou `in`/`out` editados à mão para dentro de uma zona da IA (`voz_ia` > 0 no `edl.json`).
- **`sobreposicao_ia` em todos os takes da linha** → o ChatGPT interrompeu o Carlos em todas as tentativas; use o
  take menos ruim ([REVISAR]) ou regrave. Dica de gravação: esperar 1 s depois da última palavra antes de parar.

## Gravação com o ChatGPT (método monitor) — o que ajuda o editor
- Celular **longe do microfone da câmera** (≥ 1,5 m, atrás/ao lado da câmera, virado para o Carlos, não para o mic)
  e **volume médio**: a IA tem de soar claramente mais baixa e "fina" (sem graves) que o Carlos. Nunca no mesmo tripé.
- Microfone da câmera **perto do Carlos** (lapela ou shotgun) e **sem corte de graves** (low-cut desligado): os graves
  do Carlos são a principal assinatura que o separa do alto-falante do celular.
- Deixe o ChatGPT **terminar** antes de repetir, e espere ~1 s de silêncio no fim da linha antes de ele responder
  (sobreposição = take perdido).
- Voz do ChatGPT **bem diferente** da do Carlos (se ele é homem, uma voz feminina ou bem aguda). Com voz parecida, a
  separação depende da diarização do Scribe e da assinatura do celular.
- Um áudio de 30–60 s só do Carlos em `02-calibracao/amostras/` (mesmo microfone) ajuda a desempatar.

## Arquivos gerados (`videos/<slug>/`)
`edicao/fontes.json` (`fontes` + `extras`), `edicao/fontes/*.mp4` (1440×2560), `edicao/audio48k/*.wav` (master
24-bit), `edicao/extras/*.mp4|.png`, `edicao/audio16k/*.wav`, `edicao/raw/*`, `edicao/transcricao.json`,
`edicao/locutores.json`, `edicao/alinhamento.json`, `edicao/edl.json`, `edicao/edl.md`, `edicao/edl.auto.json`,
`edicao/preview.mp4`, `edicao/corte.mp4`, `edicao/corte-audio.wav`, `edicao/frames/*.png`, `qa/diff.md`,
`qa/verificacao.json`, `status.json`.

Acabamento de áudio (master sem esmagar a partir do `corte-audio.wav`, música com ducking, medição): skill `audio-polish`.
Teste de ponta a ponta: `tests/make_synthetic.py` + `tests/check_synthetic.py` (ver `tests/README.md`); método
ChatGPT-monitor (2 vozes): `make_synthetic.py --modo monitor` + `check_synthetic.py --modo monitor`.
