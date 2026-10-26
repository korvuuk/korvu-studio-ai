# EDL — 2026-10-23-livro-chatgpt (versão 5)

> **Como aprovar:** assista `edicao/preview.mp4` e revise a tabela. Para aprovar, diga ao agente
> **"aprovado"** — ou edite `edicao/edl.json` e troque `"aprovado": false` por `"aprovado": true`.
> **Trocar take:** diga, por exemplo, "L05 usa T1" (o agente muda `segmentos[].take` e roda `edl.py --recalcular`).
> **Ajuste fino:** edite `in` / `out` / `cortes_internos` no `edl.json` e rode `edl.py --recalcular`.

**Estado:** NÃO APROVADA · **Duração do corte:** 34.4 s (alvo 35.0 s) · **Linhas:** 9 ok, 0 revisar, 0 paráfrase, 0 faltando

**Locutores (método ChatGPT-monitor):** scribe · IA = classe B (confiança 0.949) · IA 54.5 s · Carlos 145.3 s · 10 leitura(s) da IA e 13 fala(s) de monitor fora do corte · sobreposições 1 · a coluna **IA · Carlos** = leituras da IA · takes do Carlos da linha

| # | Linha | Status | Take | Fonte · in → out | Saída | Texto no corte | Alternativas | IA · Carlos |
|---|---|---|---|---|---|---|---|---|
| 1 | L01 | [OK] | T1 | praq0996 · 01:06.04 → 01:10.16 | 00:00.00–00:04.12 | joga o livro no ChatGPT e escreve /mindmap. | — | 1 · 1 |
| 2 | L02 | [OK] | T2 | praq0996 · 01:29.52 → 01:32.76 ✂1 | 00:04.12–00:07.08 | Ele te devolve uma mapa mental do livro. | T1 (0.88) · T3 (0.50; muleta) | 2 · 3 |
| 3 | L03 | [OK] | T3 | praq0996 · 03:56.96 → 04:02.24 ✂1 | 00:07.08–00:11.64 | /Sketchnote, o resumo do livro em anotação ilustrada. | T1 (0.67; pausa_interna, final_cortado) · T2 (0.67; muleta, pausa_interna) · T4 (0.67; muleta) | 1 · 4 |
| 4 | L04 | [OK] | T3 | praq0996 · 06:06.56 → 06:12.08 ✂1 | 00:11.64–00:15.84 | /flashcard. Ele te entrega cartões com resumo do conteúdo. | T1 (0.55; pausa_interna, final_cortado) · T2 (0.64; pausa_interna) | 0 · 3 |
| 5 | L05 | [OK] | T1 | praq0996 · 06:37.99 → 06:43.76 ✂1 | 00:15.84–00:20.68 | /fluxograma. Ele resume o livro num fluxo de aprendizado. | — | 0 · 1 |
| 6 | L06 | [OK] | T1 | praq0996 · 07:43.20 → 07:49.24 ✂1 | 00:20.68–00:25.84 | E /quadrinhos. Ele resume as ideias principais em quadrinhos. | — | 0 · 1 |
| 7 | L07 | [OK] | T2 | praq0996 · 08:18.00 → 08:20.84 | 00:25.84–00:28.68 | Comente a palavra "livro" que eu vou te enviar. | T1 (0.89) | 2 · 2 |
| 8 | L08 | [OK] | T1 | praq0996 · 08:29.20 → 08:31.92 | 00:28.68–00:31.40 | Mais 50 comandos no seu direct. | — | 1 · 1 |
| 9 | L09 | [OK] | T1 | praq0996 · 08:39.40 → 08:42.44 | 00:31.40–00:34.44 | E manda pra quem tem livros parados no seu estante. | — | 1 · 1 |

## Motivos e cortes internos

- **L01** [OK]: último take limpo (sim 0.89)
- **L02** [OK]: último take limpo (sim 0.88) · cortes internos: 01:30.84–01:31.12
- **L03** [OK]: último take limpo (sim 0.89); pausa interna encurtada · cortes internos: 03:58.72–03:59.44
- **L04** [OK]: último take limpo (sim 0.82); pausa interna encurtada · cortes internos: 06:07.48–06:08.80
- **L05** [OK]: último take limpo (sim 0.90); pausa interna encurtada · cortes internos: 06:39.72–06:40.64
- **L06** [OK]: último take limpo (sim 0.90); pausa interna encurtada · cortes internos: 07:44.64–07:45.52
- **L07** [OK]: último take limpo (sim 0.89)
- **L08** [OK]: último take limpo (sim 1.00)
- **L09** [OK]: último take limpo (sim 0.80)
- **L01B** [PARAFRASE] (hook alternativo de L01): paráfrase: melhor sim 0.61 (score 0.76)
- **L01C** [OK] (hook alternativo de L01): último take limpo (sim 1.00)

## Fora do corte

- Não mapeado (praq0996 00:45.20–00:47.04): "Ok, a capa já tá gravada."
- Não mapeado (praq0996 00:56.44–00:56.84): "Começar."
- Não mapeado (praq0996 01:04.88–01:05.26): "Joga,"
- Não mapeado (praq0996 01:39.46–01:39.67): "/Sketchnote,"
- Não mapeado (praq0996 02:10.44–02:36.48): "/Sketchnote."
- Não mapeado (praq0996 03:07.42–03:09.24): "/Sketchnote, o,"
- Não mapeado (praq0996 03:10.60–03:13.38): "o resumo do livro em anotação ilustrada."
- Não mapeado (praq0996 03:32.46–03:33.06): "ilustração."
- Não mapeado (praq0996 04:19.22–04:19.79): "Próximo. /Flashcards."
- Não mapeado (praq0996 04:43.04–04:44.62): "anotações de todo o livro."
- Não mapeado (praq0996 05:28.74–05:31.81): "Ele te entrega cartões com o resumo do conteúdo."
- Não mapeado (praq0996 05:41.36–05:59.82): "em flashcard. /Flashcard"
- Não mapeado (praq0996 06:24.20–06:24.82): "Próximo /fluxograma."
- Não mapeado (praq0996 06:48.66–06:49.08): "Próximo"
- Não mapeado (praq0996 07:52.72–07:53.16): "Próximo"
- Não mapeado (praq0996 08:08.12–08:08.88): "no seu direct."
- 1 trecho(s) só de muletas entre takes (descartados)
- Fala da IA — monitor (praq0996 00:49.06): "Ótimo. Agora vamos para as linhas. Quando você quiser, é só dizer: "começar", e eu dou início."
- Fala da IA — monitor (praq0996 01:11.58): "Próxima:"
- Fala da IA — monitor (praq0996 01:22.28): "De novo:"
- Fala da IA — monitor (praq0996 01:34.08): "Próxima:"
- Fala da IA — monitor (praq0996 04:23.06): "Ele te entrega cartões com o resumo do conteúdo."
- Fala da IA — monitor (praq0996 06:28.76): "Ele resume o livro num fluxo de aprendizado."
- Fala da IA — monitor (praq0996 06:50.72): "E /quadrinhos. Ele resume as ideias principais em quadrinhos."
- Fala da IA — monitor (praq0996 08:10.74): "De novo."
- Fala da IA — monitor (praq0996 08:22.40): "Próxima:"
- Fala da IA — monitor (praq0996 08:33.44): "Próxima:"
- Fala da IA — monitor (praq0996 08:44.60): "Agora vamos para os hooks alternativos. Primeiro,"
- Fala da IA — monitor (praq0996 09:07.35): "Próxima:"
- Fala da IA — monitor (praq0996 09:27.96): "Fim do roteiro. Se precisar repetir ou ajustar, é só me avisar."
- 10 leitura(s) das linhas pela IA (nunca entram no corte; ver `leituras_ia` no alinhamento.json)

## Hooks alternativos (variantes, fora da montagem principal)

- L01B (alt. de L01): L01B-T1 · praq0996 08:59.08 → 09:05.88 [parafrase]
- L01C (alt. de L01): L01C-T1 · praq0996 09:21.88 → 09:26.32 [ok]

## Cenas extras

11 ok · **0 faltando**

| ID | Tipo | Arquivo | Linhas | Modo | Saída | Status |
|---|---|---|---|---|---|---|
| E01 | imagem | edicao/extras/E01.png | L01 | split | 00:00.00–00:04.12 | OK |
| E02 | tela | edicao/extras/E02.mp4 (00:00.00–00:03.72) | L01 | split | 00:00.00–00:03.72 | OK · extra (3.72s) mais curto que a fala: sai 0.40s antes, em vez de segurar o último quadro |
| E03 | imagem | edicao/extras/E03.png | L01, L02 | split | 00:00.00–00:07.08 | OK |
| E04 | tela | edicao/extras/E04.mp4 (00:00.00–00:04.52) | L03 | split | 00:07.08–00:11.60 | OK · extra (4.52s) mais curto que a fala: sai 0.04s antes, em vez de segurar o último quadro |
| E05 | imagem | edicao/extras/E05.png | L03 | split | 00:07.08–00:11.64 | OK |
| E06 | tela | edicao/extras/E06.mp4 (00:00.00–00:03.92) | L04 | split | 00:11.64–00:15.56 | OK · extra (3.92s) mais curto que a fala: sai 0.28s antes, em vez de segurar o último quadro |
| E07 | imagem | edicao/extras/E07.png | L04 | split | 00:11.64–00:15.84 | OK |
| E08 | tela | edicao/extras/E08.mp4 (00:00.00–00:04.24) | L05 | split | 00:15.84–00:20.08 | OK · extra (4.24s) mais curto que a fala: sai 0.60s antes, em vez de segurar o último quadro |
| E09 | imagem | edicao/extras/E09.png | L05 | split | 00:15.84–00:20.68 | OK |
| E10 | tela | edicao/extras/E10.mp4 (00:00.00–00:03.24) | L06 | split | 00:20.68–00:23.92 | OK · extra (3.24s) mais curto que a fala: sai 1.92s antes, em vez de segurar o último quadro |
| E11 | imagem | edicao/extras/E11.png | L06 | split | 00:20.68–00:25.84 | OK |

## Enquadramento (zoom por peça — aplicado UMA vez, no corte)

> Cada corte troca o enquadramento (1.00 ↔ 1.12, origem no rosto) para disfarçar o jump cut. Para mudar: `zoom_pecas` (uma escala por peça) e/ou `zoom_origem` ("x% y%") no segmento + `edl.py --recalcular`; `"zoom": {"tipo": "punch", "escala": 1.2}` muda a escala do punch e faz o segmento começar fechado.

- **L01** · origem 39.7% 30.5% (rosto 2/3) · 1.00
- **L02** · origem 43.9% 27.5% (rosto 4/4) · 1.12 → 1.00
- **L03** · origem 41.2% 27.7% (rosto 4/4) · 1.12 → 1.00
- **L04** · origem 33.4% 29.2% (rosto 4/4) · 1.12 → 1.00
- **L05** · origem 40.8% 28.3% (rosto 3/4) · 1.12 → 1.00
- **L06** · origem 37.9% 29.0% (rosto 3/4) · 1.12 → 1.00
- **L07** · origem 45.0% 28.7% (rosto 3/3) · 1.12
- **L08** · origem 46.4% 28.0% (rosto 3/3) · 1.00
- **L09** · origem 50% 28% (padrão (rosto 0/3)) · 1.12

13 corte(s) com troca de enquadramento · nenhum corte com o mesmo enquadramento

## Cenas extras — plano do editor (VALE ESTE, não a tabela acima)

> A tabela "Cenas extras" acima é a leitura automática do roteiro (tudo `split`, extras da mesma linha sobrepostos).
> O plano real segue o layout do Carlos de 21/10 (decisões §3): **card do campo de digitação → resultado inteiro em
> `full`, na mesma linha**. Arquivos: `edicao/overlays-ab/overlays-A.json` e `overlays-B.json` (gerados por
> `overlays-ab/montar_overlays.py` a partir desta EDL; o `edl.json.overlays` está com a versão A). **Depois de qualquer
> `edl.py --recalcular`, rodar de novo o `montar_overlays.py`** (o recalcular refaz os overlays a partir do roteiro).
> No Remotion: `gerar_props.py <slug> --overlays edicao/overlays-ab/overlays-A.json` (e `-B.json` para a versão B).

| Linha | Card (campo, Carlos escurecido atrás) | Troca | Resultado `full` |
|---|---|---|---|
| L01 | E02 1,84–4,12 s (clipe 1,37–3,65: digita /mindmap e envia) — em "e escreve barra mindmap" | 4,12 | — |
| L02 | — | — | E03 4,12–7,08 + `enquadrar` (título central → pan para os ramos 1/5) |
| L03 | E04 7,08–8,84 (clipe 2,68–4,44) — "Barra sketchnote" | 8,84 = corte interno | E05 8,84–11,64 (em pé, cobre) |
| L04 | E06 11,64–13,52 (clipe 2,04–3,92) — "Barra flashcards: ele te entrega" | 13,52 | E07 13,52–15,84 + `enquadrar` (capa "Hábitos Atômicos" → pan para os cartões) |
| L05 | E08 15,84–17,56 (clipe 2,52–4,24) — "Barra fluxograma" | 17,56 = corte interno | E09 17,56–20,68 + `enquadrar` (capa/ciclo → pan para o fluxo) |
| L06 | E10 20,68–22,12 (clipe 1,80–3,24) — "E barra quadrinhos" | 22,12 = corte interno | E11 22,12–25,84 (em pé, cobre) |
| L07–L09 | — (CTA: Carlos em tela cheia) | — | — |

- **Versão A:** Carlos desde o quadro 0 ("Joga o livro no ChatGPT" com ele em tela cheia), depois a tabela acima.
- **Versão B:** E01 (capa + logo) em `full` + `enquadrar` (pan da capa para o logo) de 0,00 a 4,12; o card E02 entra
  POR CIMA do E01 (1,84–4,12); E03 até 7,08. **O Carlos entra aos 7,08 s** (L03, atrás do card E04); em tela cheia sem
  nada por cima só aos 25,84 s (CTA) — igual na A depois de 1,84 s.
- O card mostra só o FIM da digitação (o `in` faz o envio cair ~0,2–0,4 s antes da troca): a fala de cada linha de
  comando é ~4,2–5,2 s, e um card de ~4 s deixaria o resultado só 0,5 s na tela. A miniatura da capa já está no campo.

## Correções manuais desta EDL (editor, 21/10)

- `locutores`: "estante." (08:41.90) e "isso" (09:24.94, L01C) estavam como IA só por serem mais baixos no fim da
  frase — graves +0,4 / +2,1 dB (voz do Carlos; a IA fica em −33 dB); "te" (08:20.20) estava incerto, dentro da frase
  dele. Os três → `carlos` (`locutores.json.correcoes_manuais`); zonas da IA dessas palavras removidas.
- `transcricao`: o Scribe esticou "/Sketchnote," da L03-T3 por 10,7 s de silêncio (03:47.94–03:58.60); borda refeita
  pela energia do áudio → 03:57.10–03:58.65 (original em `borda_asr`). Sem isso a legenda "Barra sketchnote" caía 1,5 s atrasada.
- `in` de L03/L04/L05 apertados (sem o toco de 1 quadro antes do silêncio da L03; ~0,15 s de ar a menos na L04/L05) e
  plano de zoom explícito (1.00/1.12 alternando em todos os 13 cortes); L09 sem rosto detectado → origem `50% 28%`.
