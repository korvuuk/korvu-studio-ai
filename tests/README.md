# Testes

Sete suítes, todas locais (sem publicar nada, sem tocar no tracker/calendário reais, sem API):

| Suíte | Comando | O que cobre | Resultado atual |
|---|---|---|---|
| Edição por roteiro + extras | `uv run python tests/check_synthetic.py` (depois da cadeia abaixo) | escolha de takes, flags, silêncios, improviso, linha faltando, 25 fps / 10-bit, intermediário 1440×2560 + master WAV 24-bit, margens de corte fora da energia das palavras, zoom alternado (plano **e** pixels do corte/preview), zoom aplicado uma vez, agudos preservados (corte e master), principal + extras, TELA com vários itens, amostra de cor ignorada, 1 locutor só | 47/47 |
| Método ChatGPT-monitor (2 vozes) | `uv run python tests/check_synthetic.py --modo monitor` (cadeia "monitor" abaixo) | locutores Carlos × IA (acerto vs verdade), takes só do Carlos, nenhuma voz/cauda da IA no corte, sobreposição, frases de monitor, linha só lida pela IA, diarização do Scribe simulada, margens, zoom alternado/uma vez, agudos preservados | 28/28 |
| Cor | `uv run python tests/cor/test_cor.py` | LUT criativo, primária por take, V-Log → Rec.709 10-bit, extras `camera`, ecrã sem cor, grão, mosaico | 65/65 |
| Publicação | `uv run python tests/publicar/test_publicar.py` | agendar, `--due`, confirmação, dry-run (sem rede), launchd (sem instalar), **selo GAUNTLET** (sem selo, legado, capa trocada, portão da publicação) | 81/85 — as 4 falhas são as vagas antigas do calendário (D1 em `_controle/backlog-portoes.md`) |
| Portões (GAUNTLET) | `uv run python tests/portoes/test_portoes.py` | impressão congelada, S0/S1/S2, relatório obrigatório, só a FALA vence o roteiro, cor refeita vence a imagem (caso de 21/10), cópia/apagado não vencem, tecto de 3 voltas → ESCALADO → decisão do Carlos, selo do pacote, post na fila bloqueado quando a origem muda, Trial × normal vence a publicação, legado | 39/39 |
| Métricas | `uv run python tests/metricas/test_metricas.py` | Reels com ≥ 5 dias, `--slug/--forcar`, taxas e % assistido, métrica não suportada (#100), permissão em falta (exit 3), histórico, dry-run, só GET, plist 09:30 | 32/32 |
| Remotion | `cd remotion && npx tsc --noEmit && npx remotion compositions` | tipos e composições (25 fps) | ok |
| Cartão do CTA | `uv run python tests/test_cta_props.py` | `gerar_props.derivar_cta`: palavra, início no "comenta", fim +0,5 s sem invadir a linha seguinte, rodapé, casos sem cartão | 11/11 |

## Teste sintético de ponta a ponta
`make_synthetic.py` gera `videos/_teste-sintetico/`:
- **Principal** (`brutos/principal/camera-01.mov`): ProRes 422 HQ 10-bit, 3840×2160 com rotação (vertical), 25 fps, imagem "log", voz TTS pt-BR (`say`) com problemas propositais:

| Problema gravado | Esperado |
|---|---|
| L03 falada 3× (T1 cortada, T2 com "é...", T3 limpa) | escolhe **L03-T3**; T1 `false_start`, T2 `muleta` |
| L04 com pausa interna de 1,0 s | `pausa_interna` → pausa curta no corte |
| L05: falso começo + "de novo" + linha completa | T1 `false_start`, separador descartado, escolhe T2 |
| 3 s de silêncio entre L05 e L06 | some do corte |
| frase improvisada fora do roteiro | `nao_mapeado`, fora do corte |
| L07 não gravada | `faltando` no alinhamento e em `qa/diff.md` |
| L01B (hook alternativo) | alinhado, fora da montagem |
| `camera-00-cor.mov` | ignorado na edição (amostra do colorista) |

- **Extras** (`brutos/extras/`): E01 tela (split, em 2 linhas → overlay contínuo), E02 animação (componente registrado), E03 imagem (card com crédito), E04 declarado mas ausente → `faltando` e QA FAIL até `make_synthetic.py --so-e04`.

### Critérios da revisão do Carlos (áudio abafado/esmagado, cortes bruscos)
| Critério | Como é conferido |
|---|---|
| Intermediário 1440×2560 + master `audio48k/*.wav` 48 kHz 24-bit mono, só passa-altas (sem `afftdn`) | ffprobe + `fontes.json.audio.cadeia` |
| Margens de corte | nenhuma borda de peça (in/out/corte interno, na grade de frames) dentro da energia de uma palavra (`limites_energia`: ataque suave/cauda); mediana ≥ 0,12 s antes da 1.ª e ≥ 0,18 s depois da última palavra |
| Zoom alterna a cada corte | `zoom_pecas` sem duas peças seguidas com a mesma escala; **nos pixels**: o quadro do meio de cada peça no `corte.mp4` e no `preview.mp4` é comparado ao intermediário recortado em 1.00/1.06/1.12 (z-score + MSE) → escala medida = plano |
| Zoom aplicado uma vez | `edl.zoom_no_corte`, `gerar_props.segmentos_props()` sem zoom, `Reel.tsx` com `!zoomNoCorte` |
| Agudos preservados | energia 2–5k / 5–10k / 10–16k (dB rel. 60 Hz–16 kHz) do `corte-audio.wav` e do master (`audio.py`) vs o bruto `.mov` no mesmo trecho: ±1,5 dB. O `afftdn=nf=-25` antigo dava ≈ −10 dB |
| Master sem esmagar | −14 ±0,5 LUFS, TP ≤ −1,5 dBTP, crest cai ≤ 1 dB vs o corte (a voz TTS tem crest 10,9 dB no bruto; o ≥ 13 dB absoluto é conferido na voz real) |

## Cadeia completa
```bash
cd "/Users/teste/Documents/CONTENT AI"
S=".claude/skills/corte-por-roteiro/scripts"; V="videos/_teste-sintetico"
uv run python tests/make_synthetic.py --limpar
uv run python "$S/ingest.py" "$V"
uv run --extra local python "$S/transcribe.py" "$V" --engine mlx
uv run python "$S/locutores.py" "$V"                                # 1 voz -> tudo "carlos"
uv run python "$S/align.py" "$V"
uv run python "$S/edl.py" "$V"
uv run python "$S/render_corte.py" "$V" --force
uv run python "$S/filmstrip.py" "$V"
uv run --extra local python "$S/verify.py" "$V" --engine mlx      # exit 1 esperado: L07 não foi gravada
uv run python tests/check_synthetic.py                              # 47 critérios (roda um master de teste)
# cor (LUT criativo de teste da suíte de cor) → gráficos → áudio → QA
uv run python .claude/skills/color-grading/scripts/aplicar_cor.py "$V" --lut tests/cor/_saida/root/00-marca/cor/luts/korvu-look-v1.cube
uv run python .claude/skills/legendas-animadas/scripts/gerar_props.py "$V"
uv run python .claude/skills/legendas-animadas/scripts/render_reel.py "$V" --auto
uv run python .claude/skills/audio-polish/scripts/audio.py "$V/edicao/render-remotion.mp4" "$V/edicao/final.mp4"
uv run python .claude/skills/qa-video/scripts/qa_check.py "$V/edicao/final.mp4" --video_dir "$V"
```
Última execução integrada (2026-09-15): Remotion usou `cor/corte-cor.mp4`, 25 fps, −14,0 LUFS, QA PASS (13/13).
Revisão de áudio/zoom (2026-09-15, noite): clássico 47/47, monitor 28/28. No vídeo real (2026-09-16-chatgpt-contexto,
`revisao-v3`): agudos vs bruto +0,3/+1,2/+1,1 dB (v2: −7,1/−10,3/−10,6), crest 14,3 dB, −14,1 LUFS, TP −1,7 dBTP,
15/15 cortes com troca de enquadramento, 1.12 do intermediário 1440 1,3× mais nítido que ampliado de 1080.

## Método ChatGPT-monitor (duas vozes na mesma gravação)
`make_synthetic.py --modo monitor` gera `videos/_teste-monitor/` (sem cenas extras): o "ChatGPT" (voz **Luciana**,
processada como alto-falante de celular na sala — highpass 350 Hz 2×, lowpass 7 kHz, −10 dB, reverb curta `aecho`) lê
cada linha e o "Carlos" (voz **Reed**, masculina, seca/perto) repete. `verdade.json` traz o locutor e o início/fim
reais (com a cauda da reverb) de cada pedaço.

| Gravado | Esperado |
|---|---|
| IA lê cada linha antes do Carlos | `leituras_ia` por linha, nunca take; locutores acerta ≥ 95 % das palavras |
| "Próxima." colado numa leitura; "Boa! Mais uma vez…"; "Ótimo, terminamos." | `fala_ia` (fora do corte e de `nao_mapeado`) |
| L03: Carlos erra ("exemplo") → IA "De novo. Faltou a palavra contexto. Repete: …" → retake | escolhe **L03-T2**; o "de novo" da IA não é separador |
| L04: T1 limpo, depois T2 com a IA ("Perfeito. Próxima.") começando 0,3 s antes do fim | T2 `sobreposicao_ia`, escolhe **L04-T1** |
| L05: falso começo + "de novo" **do Carlos** + linha completa | separador do Carlos, escolhe T2 |
| L07: só a IA lê, o Carlos nunca repete | `faltando` ("a IA leu a linha (1×), mas não há take do Carlos") |
| repetição idêntica logo depois da leitura (L01, L02, L06, L08) | o Whisper "engole" — o transcribe re-transcreve a lacuna |

Também confere: nenhuma peça da EDL (± alça de 15 ms) toca a voz real da IA nem a cauda; `voz_ia` = 0 em todos os
segmentos; verify com 0 s de voz de IA no corte; `edl.md` com a coluna **IA · Carlos**; e a camada A (Scribe) simulada
com os ids da verdade + 3 % trocados (`locutores.rotular(..., forcar_metodo="scribe")`).
```bash
S=".claude/skills/corte-por-roteiro/scripts"; V="videos/_teste-monitor"
uv run python tests/make_synthetic.py --modo monitor --limpar
uv run python "$S/ingest.py" "$V"
uv run --extra local python "$S/transcribe.py" "$V" --engine mlx   # lacunas re-transcritas (L01, L02, L03-T2, L06, L08)
uv run python "$S/locutores.py" "$V"                                # separação ~11, IA = classe A, 3 evidências
uv run python "$S/align.py" "$V"
uv run python "$S/edl.py" "$V"
uv run python "$S/render_corte.py" "$V" --force
uv run python "$S/filmstrip.py" "$V"
uv run --extra local python "$S/verify.py" "$V" --engine mlx      # exit 1 esperado: L07 (voz da IA 0,00 s)
uv run python tests/check_synthetic.py --modo monitor               # 28 critérios
```
Última execução (2026-09-15): acerto de locutor 100 % (218 palavras; Scribe simulado 100 %), voz de IA no corte 0,00 s,
WER 0 % nas 7 linhas gravadas, clássico 40/40.

Para testar o `status.py` sem mexer no tracker real:
`uv run python "$S/status.py" "$V" edicao --tracker /tmp/tracker-teste.md`

Mídia de teste e saídas ficam fora do git (`videos/_teste-*`, `tests/render/`, `tests/cor/_saida/`).
