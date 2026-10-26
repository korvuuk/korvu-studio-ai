# Cor da marca — ficha do look

```yaml
status: ativo
versao_ativa: v5                # 2026-09-18: o Carlos comparou v5 x v11 lado a lado na regravação e
                                # ESCOLHEU O v5 ("a cor da pele ficou muito boa, gostei como ficou").
                                # As medições favorecem o v11 (rosto 40,9 IRE vs 23,2 do v5) — decisão dele,
                                # e a pele natural tem prioridade sobre o resto no critério abaixo.
alternativa_medida: v11         # WAY v5 + pele recuperada (aprovado em 2026-09-17: "ficou bem melhor, ganhou mais
                                # a iluminação na cena"). O v5 sozinho deixava o rosto em 16,5 IRE — abaixo do fundo.
                                # Descartadas: v9 (lábios vermelhos), v10 (fraco demais), v12 (estoura o branco).
                                # v4 (Tenet) ARQUIVADO em 2026-10-24 (decisão do Carlos; o .cube continua, ainda dá para usar com --lut).
arquivados: [v4]                # look "Tenet" (frio e contido)
# Aprovar = também marcar "aprovada": true em luts/korvu-look-vN.json (o aplicar_cor.py usa a maior versão aprovada)
intensidade_lut: 0.8            # usada no criar_lut; no aplicar_cor a mistura padrão é 1.0
grao: 0.3                       # grão fino de película do look WAY (aplicar_cor --grao 0.3)
referencia: referencias/LOOK-REFERENCIA.md   # look "Tenet" (frio, contido, pele natural)
entrada_camera: luts/entrada-camera.cube (gerado, provisório)   # V-Log/V-Gamut→Rec.709 (S5IIX); a oficial em luts/panasonic/*V709*.cube tem prioridade
```

## Look desejado (resumo)
Cinematográfico, frio e contido: sombras teal, pele natural dessaturada, verdes oliva, contraste de filme suave, altas macias. Detalhes e números-alvo em `referencias/LOOK-REFERENCIA.md`.

## Critérios de aprovação (MEDIDOS, não julgados no olho — 2026-09-17)
- **Rosto do Carlos no arquivo final: ≥ 35 IRE** (ideal 40–50). No 1.º vídeo real ficou em **13 IRE** e a parede
  atrás em 25 IRE — o fundo mais claro que ele. Metade veio da captação (rosto a 32 IRE em V-Log, ~1 diafragma
  subexposto) e metade do look: só a conversão V-Log→709 deixa o rosto em 29 IRE; o WAY v5 derruba para 16,5 IRE.
- **Fundo abaixo do rosto.**
- **Pelo menos um detalhe perto de 90 IRE** — no 1.º vídeo nada passava de 70 IRE (imagem chapada no topo).
- Pele natural (sem laranja, sem cinza) — prioridade sobre fidelidade ao look.
- Pretos ~3–5 IRE **sem cortar** (no 1.º vídeo o mínimo caiu abaixo do preto legal, perdendo sombra).
- Como medir: `ffmpeg -ss T -i <arquivo> -vf "crop=<rosto>,signalstats,metadata=print:key=lavfi.signalstats.YAVG" -f null -`
  e converter: IRE = (código − 16) ÷ 219 × 100 em 8-bit faixa limitada.
- Guia de gravação (o que pedir ao Carlos antes de gravar): `00-marca/captura.md`.
- Takes com luz diferente chegam iguais depois da correção primária.
- Legendas laranja/brancas continuam destacando sobre a imagem.

## Histórico
| Data | Versão | Referências | Amostra | Parâmetros | Decisão |
|---|---|---|---|---|---|
| 2026-09-18 | **v5 ✅ ATIVO** | — | `chatgpt02.MOV` (regravação, exposição corrigida) | mkl · 0.7 · pele 0 | **ESCOLHIDO pelo Carlos** na comparação v5 × v11 feita neste corte: "a cor da pele ficou muito boa". Medido: rosto 23,2 IRE, fundo 32,7, branco 61,5, preto 4,8 — abaixo do mínimo de 35 IRE da ficha, mas a decisão é dele e a pele tem prioridade. O v11 media rosto 40,9 / branco 93,3 no mesmo corte |
| 2026-09-15 | — | ref-tenet-01a, b, d (c fora do cálculo) | aguardando `camera-00-cor.mov` | — | entrada V-Log→709 gerada (provisória); LUT criativo aguarda a amostra real |
| 2026-09-15 | v1 | a, b, d | PRAQ0967.MOV (20 frames; V-Log lido em full range) | mkl · 0.8 · pele 0.7 | descartada: rosto escuro demais, >2% pretos esmagados |
| 2026-09-15 | **v2** | a, b, d | idem | hm-mvgd-hm · 0.7 · pele 0.8 | **provisória para o 1.º teste**: pele natural, sem esmagar; luma 0.38 / contraste 0.25 (ref 0.36 / 0.27); saturação ainda alta (0.48 vs 0.27) e fundo quente → próximo passo: ajuste de look (dessaturar + sombras teal, protegendo a pele) |
| 2026-09-15 | v3 | a, b, d | idem | reinhard · 0.75 · pele 0.8 | descartada: saturação subiu (0.53) |
| 2026-09-15 | v2 (revisão) | — | render real | — | **descartada**: a proteção de pele criou manchas magenta no pescoço (fronteira pele iluminada/sombra) e lábios rosados; brancos com tom creme-esverdeado. Lição: com pele escura e luz quente, `--proteger-pele` + método por histograma cria descontinuidades — preferir método linear (mkl) sem máscara |
| 2026-09-15 | **v4** | a, b, d | PRAQ0967.MOV | mkl · 0.6 · pele 0 | alternativa "Tenet": transformação linear (sem manchas), luma 0.40 / contraste 0.25 / saturação 0.35 (ref 0.36 / 0.27 / 0.27) |
| 2026-09-15 | **v5 ✅** | `referencias/way/` ref-way-01a, b, c (só a metade nítida, sem texto nem vidro fosco) | PRAQ0967.MOV | mkl · 0.7 · pele 0 · grão 0.3 | **APROVADA pelo Carlos ("gostei do way v5")**: luma 0.30 / contraste 0.19 / saturação 0.37 (ref 0.26 / 0.18 / 0.34); tom geral verde-azulado (brancos puxam para menta), pescoço sem manchas |
| 2026-09-17 | **v11 ✅** | — | PRAQ0967.MOV | `criar_look.py --base korvu-look-v5.cube --exposicao 1.0 --contraste 1.0 --preto 0.0 --branco 1.0` | **APROVADA**: devolve à pele o que o v5 tirava. Rosto 16,5 → **22,8 IRE**, preto 1,3 IRE (continua profundo), branco 98 IRE (sem estourar a luminária). Medido, não julgado no olho. Com a exposição corrigida na gravação (`00-marca/captura.md`), o rosto passa a cair em 35–45 IRE |
| 2026-09-17 | v10, v12 | — | idem | +0,5 e +1,5 stop sobre o v5 | descartadas: v10 fraca demais (rosto 19,5 IRE); v12 estoura o branco (100,3 IRE) |
| 2026-09-16 | v8 (candidata) | — | — | `criar_look.py --base korvu-look-v5.cube` · pele +6% sat, +0.022 quente, croma-min 0.006 | proposta para as **manchas esverdeadas na pele** que o Carlos viu no v5: mesmo look, pele mais quente e uniforme; resto da imagem igual. Aguardando decisão dele (pode ir mais forte) |
| 2026-09-16 | **v5 (reaplicada)** | — | `videos/2026-09-16-chatgpt-contexto` | mkl · 0.7 · pele 0 · grão 0.3 | **volta ao v5** a pedido do Carlos ("a cor ficou muito vermelho nos lábios, vamos voltar à versão anterior"); v9 arquivada em `luts/_descartadas/`. As manchas esverdeadas da pele ficam para uma versão futura, sem mexer nos lábios |
| 2026-09-15 | v6, v7 | — | — | paramétricas (`criar_look.py`) | descartadas: brancos neutros e pele limpa, mas sutis demais; a parede tem a MESMA cor da pele (matiz 26° vs 20°), então nenhum LUT separa fundo e pele — para fundo sálvia + pele quente seria preciso recorte da pessoa |
