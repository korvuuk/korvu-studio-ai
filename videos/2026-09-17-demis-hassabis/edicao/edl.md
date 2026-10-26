# EDL — 2026-09-17-demis-hassabis (versão 24)

> **Como aprovar:** assista `edicao/preview.mp4` e revise a tabela. Para aprovar, diga ao agente
> **"aprovado"** — ou edite `edicao/edl.json` e troque `"aprovado": false` por `"aprovado": true`.
> **Trocar take:** diga, por exemplo, "L05 usa T1" (o agente muda `segmentos[].take` e roda `edl.py --recalcular`).
> **Ajuste fino:** edite `in` / `out` / `cortes_internos` no `edl.json` e rode `edl.py --recalcular`.

**Estado:** APROVADA · **Duração do corte:** 57.8 s (alvo 60.0 s) · **Linhas:** 3 ok, 0 revisar, 9 paráfrase, 1 faltando

**Locutores (método ChatGPT-monitor):** local · IA = classe B (confiança 0.778) · IA 200.2 s · Carlos 192.0 s · 33 leitura(s) da IA e 56 fala(s) de monitor fora do corte · sobreposições 2 · **5 palavra(s) com locutor incerto** · a coluna **IA · Carlos** = leituras da IA · takes do Carlos da linha

| # | Linha | Status | Take | Fonte · in → out | Saída | Texto do take | Alternativas | IA · Carlos |
|---|---|---|---|---|---|---|---|---|
| 1 | L01 | [OK] | T3 | praq0969 · 02:38.67 → 02:43.12 ✂2 | 00:00.00–00:04.12 | Aprendeu xadrez aos 4 anos? ganhou um Nobel com E .A. | T1 (0.18; false_start) · T2 (0.55; false_start) | 3 · 3 |
| 2 | L02 | [PARAFRASE] | T1 | praq0969 · 03:18.87 → 03:22.68 ✂1 | 00:04.12–00:07.04 | Denis Assabi, nascido aqui em Londres. | — | 0 · 1 |
| 3 | L03 | [PARAFRASE] | T2 | praq0969 · 04:19.13 → 04:45.21 ✂4 | 00:07.04–00:12.08 | Aos 17 anos já era mestre de xadrez e aos 17 anos criava videogames. | T1 (0.58; muleta, pausa_interna, final_cortado, sem_ancora) | 3 · 2 |
| 4 | L04 | [PARAFRASE] | T2 | praq0969 · 05:09.24 → 05:13.24 ✂2 | 00:12.08–00:15.80 | Estudou computações em Cambridge e depois a Neurociência. | T1 (0.43; final_cortado) | 2 · 2 |
| 5 | L05 | [PARAFRASE] | T2 | praq0969 · 05:42.66 → 05:48.62 ✂2 | 00:15.80–00:21.28 | Em 2010, juntou tudo aqui em Londres, | T1 (0.64; final_cortado) | 2 · 2 |
| 6 | L06 | [PARAFRASE] | T2 | praq0970 · 00:08.66 → 00:15.32 ✂3 | 00:21.28–00:27.40 | quatro anos depois, o Google comprou a empresa dele por 400 milhões de libras. | T1 (0.64) | 2 · 2 |
| 7 | L07 | [MANUAL] | T2 | praq0971 · 00:08.21 → 00:14.84 ✂6 | 00:27.40–00:32.56 | 2016, a IA deles venceu o maior nome do | T1 (0.67; muleta) | 2 · 2 |
| 8 | L08 | [PARAFRASE] | T1 | praq0971 · 00:53.29 → 00:57.85 ✂2 | 00:32.56–00:36.72 | Um jogo com mais posições com átomos do universo. | — | 3 · 1 |
| 9 | L09 | [PARAFRASE] | T6 | praq0974 · 00:47.33 → 00:55.49 ✂5 | 00:36.72–00:43.80 | Mas o maior feito veio depois, onde o alfa -fold passou a prever o formato da proteína. | T1 (0.27; false_start) · T2 (0.47; final_cortado) · T3 (0.47; final_cortado) · T4 (0.40; false_start) · T5 (0.62) | 4 · 6 |
| 10 | L10 | [OK] | T2 | praq0975 · 00:19.41 → 00:24.64 ✂4 | 00:43.80–00:47.56 | Um problema que travava a ciência havia 50 anos. | T1 (0.60; locutor_incerto) | 4 · 2 |
| – | L11 | [FALTANDO] | — | — | — | _E isso deu a ele o Nobel de Química, junto com o John Jumper._ | — | 2 · 0 |
| 11 | L12 | [OK] | T2 | praq0975 · 00:53.87 → 01:01.34 ✂6 | 00:47.56–00:53.68 | Quer dizer, o menino do xadrez virou um dos nomes mais importantes da | T1 (0.50) | 2 · 2 |
| 12 | L13 | [PARAFRASE] | T1 | praq0976 · 00:07.22 → 00:11.80 ✂3 | 00:53.68–00:57.84 | Para mais conteúdos como esse, é só me seguir e te vejo na próxima. | — | 0 · 1 |

## Motivos e cortes internos

- **L01** [OK]: último take limpo (sim 0.82); muleta cortada internamente, pausa interna encurtada · cortes internos: 02:41.05–02:41.35, 02:41.12–02:41.32
- **L02** [PARAFRASE]: paráfrase: melhor sim 0.67 (score 0.75) · cortes internos: 03:20.02–03:20.88
- **L03** [PARAFRASE]: paráfrase: melhor sim 0.71 (score 0.82) · cortes internos: 04:20.92–04:21.26, 04:22.13–04:42.50, 04:42.03–04:42.50, 04:43.88–04:44.21
- **L04** [PARAFRASE]: paráfrase: melhor sim 0.75 (score 0.83) · cortes internos: 05:11.45–05:11.72, 05:11.48–05:11.72
- **L05** [PARAFRASE]: paráfrase: melhor sim 0.71 (score 0.79) · cortes internos: 05:44.11–05:44.37, 05:46.04–05:46.34
- **L06** [PARAFRASE]: paráfrase: melhor sim 0.71 (score 0.82) · cortes internos: 00:10.14–00:10.46, 00:10.16–00:10.44, 00:12.69–00:12.91
- **L07** [PARAFRASE]: paráfrase: melhor sim 0.67 (score 0.64) · cortes internos: 00:09.55–00:10.25, 00:09.56–00:10.24, 00:12.35–00:12.81, 00:12.40–00:12.80, 00:13.96–00:14.33, 00:14.00–00:14.32
- **L08** [PARAFRASE]: paráfrase: melhor sim 0.64 (score 0.74) · cortes internos: 00:54.10–00:54.29, 00:56.67–00:56.89
- **L09** [PARAFRASE]: paráfrase: melhor sim 0.71 (score 0.80) · cortes internos: 00:48.59–00:48.81, 00:49.99–00:50.57, 00:50.04–00:50.56, 00:52.23–00:52.55, 00:52.28–00:52.52
- **L10** [OK]: último take limpo (sim 0.89) · cortes internos: 00:21.87–00:22.21, 00:21.92–00:22.20, 00:22.91–00:23.35, 00:22.96–00:23.32
- **L11** [FALTANDO]: a IA leu a linha (2×), mas não há take do Carlos
- **L12** [OK]: último take limpo (sim 0.93); pausa interna encurtada · cortes internos: 00:54.60–00:55.12, 00:54.68–00:55.12, 00:56.99–00:57.35, 00:57.04–00:57.32, 00:58.81–00:59.00, 01:00.25–01:00.52
- **L13** [PARAFRASE]: paráfrase: melhor sim 0.57 (score 0.74) · cortes internos: 00:08.84–00:09.00, 00:10.02–00:10.24, 00:10.04–00:10.28
- **L01B** [OK] (hook alternativo de L01): último take limpo (sim 0.89)
- **L01C** [OK] (hook alternativo de L01): último take limpo (sim 0.80); pausa interna encurtada

## Fora do corte

- Não mapeado (praq0969 00:34.10–00:34.82): "Tchau, tchau."
- Não mapeado (praq0969 01:13.19–01:14.68): "Ok, eu estou pronto. Vamos ir."
- Não mapeado (praq0969 01:45.72–01:46.87): "Pronto, pode começar. começar."
- Não mapeado (praq0969 02:17.50–02:18.16): "o do início."
- Não mapeado (praq0969 02:23.79–02:26.72): "Não, antes, antes, antes. Primeiro, primeira linha."
- Não mapeado (praq0969 02:51.50–02:52.50): "Denis Hassabis."
- Não mapeado (praq0969 03:01.94–03:03.09): "Denis Hassabi."
- Não mapeado (praq0969 03:04.22–03:04.74): "Nassib."
- Não mapeado (praq0969 03:35.03–03:39.41): "não precisa dizer respiração tá bom não precisa dizer a respiração"
- Não mapeado (praq0969 03:57.30–03:58.70): "aos 13 anos."
- Não mapeado (praq0969 03:59.28–03:59.50): "daí."
- Não mapeado (praq0969 05:27.68–05:30.07): "uma empresa chamada DeepMine."
- Não mapeado (praq0969 05:46.37–05:48.50): "fundou uma empresa, a DeepMind."
- Não mapeado (praq0970 00:32.91–00:33.86): "Em 2016,"
- Não mapeado (praq0970 00:34.94–00:39.74): "a EA e deles venceram o maior jogo da competição do gol."
- Não mapeado (praq0970 00:50.38–00:51.18): "Em 2016,"
- Não mapeado (praq0970 00:53.12–00:56.36): "a EA e deles venceram o maior nome do gol."
- Não mapeado (praq0970 01:05.07–01:06.24): "vamos repetir antes"
- Não mapeado (praq0970 01:12.31–01:15.62): "não vamos repetir em"
- Não mapeado (praq0970 01:20.56–01:20.76): "gol"
- Não mapeado (praq0971 00:08.23–00:08.36): "Em"
- Não mapeado (praq0971 00:14.48–00:14.72): "gol."
- Não mapeado (praq0971 00:26.16–00:26.62): "Continua."
- Não mapeado (praq0971 01:03.16–01:03.50): "Alpha"
- Não mapeado (praq0972 00:00.00–00:01.02): "O maior feito veio depois."
- Não mapeado (praq0972 00:08.24–00:10.48): "Calma, eu acho que você não está me escutando, você"
- Não mapeado (praq0972 00:10.62–00:20.09): "passando direto, mesmo que eu arrasse, você está passando direto. Vamos repetir, E... mas o maior feito do AlphaFold. isso? Ahn."
- Não mapeado (praq0972 01:09.46–01:09.51): "previa..."
- Não mapeado (praq0972 01:19.36–01:22.06): "Você tem que me escutar. Quando eu começo a falar..."
- Não mapeado (praq0973 00:00.00–00:04.02): "De uma linha, você vai ter que entender que aquela linha eu quero repetir. Então,"
- Não mapeado (praq0973 00:04.54–00:06.00): "naquela mesma linha que eu estou falando."
- Não mapeado (praq0973 00:36.05–00:37.62): "mais um maior"
- Não mapeado (praq0974 00:00.38–00:02.38): "Ok, vamos começar no linha A,"
- Não mapeado (praq0975 00:03.25–00:05.30): "Um problema que traba..."
- Não mapeado (praq0975 00:40.72–00:42.29): "história do AI."
- Não mapeado (praq0975 01:07.81–01:10.56): "Me segue que eu trago mais histórias assim."
- Não mapeado (praq0976 00:38.30–00:39.48): "a DeepMind."
- Não mapeado (praq0976 00:58.24–00:59.96): "história da AI."
- Separador descartado (praq0969 02:16.03): "Repete, repete. Repete"
- Separador descartado (praq0969 03:56.75): "Repete"
- Separador descartado (praq0969 03:58.88): "Repete"
- Separador descartado (praq0971 01:06.97): "De novo."
- Separador descartado (praq0973 00:04.18): "repete"
- 5 trecho(s) só de muletas entre takes (descartados)
- Fala da IA — monitor (praq0969 00:04.00): "E aí E aí"
- Fala da IA — monitor (praq0969 00:13.72): "E aí"
- Fala da IA — monitor (praq0969 00:28.29): "E aí E aí"
- Fala da IA — monitor (praq0969 01:11.44): "E aí"
- Fala da IA — monitor (praq0969 01:16.03): "Ótimo. Me dá o sinal de começar e eu já entro com a primeira linha."
- Fala da IA — monitor (praq0969 01:29.39): "E aí"
- Fala da IA — monitor (praq0969 01:53.53): "aos quatro"
- Fala da IA — monitor (praq0969 02:00.46): "vou, eu vou, eu vou."
- Fala da IA — monitor (praq0969 02:09.09): "Bem, mis Hassabis. Respiro curto. Nascido aqui em Londres."
- Fala da IA — monitor (praq0969 02:20.78): "Demis Hassabis. Respiro curto."
- Fala da IA — monitor (praq0969 02:34.17): "curto. E ganhão, não deu conha."
- Fala da IA — monitor (praq0969 02:44.37): "Próximo. Denis Hassabis. Respiro curto. Nascido aqui em Londres."
- Fala da IA — monitor (praq0969 02:54.07): "De novo. Denis Hassabis. Respiro curto. Nascido aqui em Londres."
- Fala da IA — monitor (praq0969 03:32.35): "ver videogame."
- Fala da IA — monitor (praq0969 03:40.72): "Entendi. Sem falar das respirações, eu vou direto para o conteúdo da linha. Vamos continuar, enquanto o que você quiser."
- Fala da IA — monitor (praq0969 04:06.33): "Obrigado."
- Fala da IA — monitor (praq0969 04:09.15): "aí"
- Fala da IA — monitor (praq0969 04:13.19): "aí"
- Fala da IA — monitor (praq0969 04:29.37): "Aos 17 anos já era mestre de chaves. Aos 17,"
- Fala da IA — monitor (praq0969 04:34.49): "criava videogame."
- Fala da IA — monitor (praq0969 05:21.45): "Adiv, Mike."
- Fala da IA — monitor (praq0970 00:16.77): "Próximo."
- Fala da IA — monitor (praq0970 00:22.56): "gol."
- Fala da IA — monitor (praq0970 00:41.99): "E, inubar, E, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní, ní"
- Fala da IA — monitor (praq0971 00:00.72): "De novo,"
- Fala da IA — monitor (praq0971 00:06.36): "gol."
- Fala da IA — monitor (praq0971 00:16.98): "Próximo. Um jogo com o Mai."
- Fala da IA — monitor (praq0971 00:30.52): "De novo,"
- Fala da IA — monitor (praq0971 00:37.84): "Ausa de um segundo."
- Fala da IA — monitor (praq0971 00:42.63): "E aí"
- Fala da IA — monitor (praq0971 00:50.20): "E aí"
- Fala da IA — monitor (praq0971 00:59.23): "Próximo."
- Fala da IA — monitor (praq0972 00:02.95): "Próximo."
- Fala da IA — monitor (praq0972 00:07.21): "Fíjants,"
- Fala da IA — monitor (praq0972 00:10.48): "está"
- Fala da IA — monitor (praq0972 00:38.45): "hum, hum, hum."
- Fala da IA — monitor (praq0972 01:13.81): "De novo,"
- Fala da IA — monitor (praq0973 00:07.53): "Entendi. A partir de agora, se você começar uma linha, eu fico atento àquela linha e repetimos desde o início dela. Tá, corre? Vamos nessa."
- Fala da IA — monitor (praq0974 00:07.12): "Combinado. Vamos começar dessa linha. Assim que você sinalizar, eu refiro certinho."
- Fala da IA — monitor (praq0974 00:22.85): "aí"
- Fala da IA — monitor (praq0974 00:25.90): "aí"
- Fala da IA — monitor (praq0974 00:37.41): "E, IA, good to have a world."
- Fala da IA — monitor (praq0974 00:57.58): "Próximo."
- Fala da IA — monitor (praq0974 01:13.78): "brofold."
- Fala da IA — monitor (praq0975 00:06.22): "E aí"
- Fala da IA — monitor (praq0975 00:13.54): "aí"
- Fala da IA — monitor (praq0975 01:03.88): "Me segue que eu trago mais histórias assim."
- Fala da IA — monitor (praq0975 01:12.72): "gravamos os books alternativos. Primeiro,"
- Fala da IA — monitor (praq0975 01:18.64): "nó."
- Fala da IA — monitor (praq0976 00:17.52): "vindo lá."
- Fala da IA — monitor (praq0976 00:31.62): "modô, Aya."
- Fala da IA — monitor (praq0976 00:49.90): "AI."
- Fala da IA — monitor (praq0976 01:01.72): "Fim do roteiro. Se precisar de mais alguma repetição ou ajuste, é só falar."
- Fala da IA — monitor (praq0976 01:15.97): "E aí"
- Fala da IA — monitor (praq0977 00:00.47): "E aí"
- Fala da IA — monitor (praq0977 00:03.46): "E aí aí"
- 33 leitura(s) das linhas pela IA (nunca entram no corte; ver `leituras_ia` no alinhamento.json)

## Hooks alternativos (variantes, fora da montagem principal)

- L01B (alt. de L01): L01B-T1 · praq0976 00:20.40 → 00:24.00 [ok]
- L01C (alt. de L01): L01C-T2 · praq0976 00:52.80 → 00:58.24 [ok]

## Cenas extras

9 ok · **0 faltando**

| ID | Tipo | Arquivo | Linhas | Modo | Saída | Status |
|---|---|---|---|---|---|---|
| E30 | video | edicao/extras/E30.mp4 (00:00.00–00:04.12) | L01 | split | 00:00.00–00:04.12 | OK · crédito: The Thinking Game (Google DeepMind / Greg Kohs) |
| E41 | video | edicao/extras/E41.mp4 (00:00.00–00:02.92) | L02 | split | 00:04.12–00:07.04 | OK · crédito: The Thinking Game (Google DeepMind / Greg Kohs) |
| E42 | video | edicao/extras/E42.mp4 (00:00.00–00:05.04) | L03 | split | 00:07.04–00:12.08 | OK · crédito: The Thinking Game (Google DeepMind / Greg Kohs) |
| E32 | video | edicao/extras/E32.mp4 (00:00.00–00:03.72) | L04 | split | 00:12.08–00:15.80 | OK · crédito: The Thinking Game (Google DeepMind / Greg Kohs) |
| E44 | video | edicao/extras/E44.mp4 (00:00.00–00:11.60) | L05, L06 | split | 00:15.80–00:27.40 | OK · crédito: The Thinking Game (Google DeepMind / Greg Kohs) |
| E45 | video | edicao/extras/E45.mp4 (00:00.00–00:05.16) | L07 | split | 00:27.40–00:32.56 | OK · crédito: The Thinking Game (Google DeepMind / Greg Kohs) |
| E37 | video | edicao/extras/E37.mp4 (00:00.00–00:04.16) | L08 | split | 00:32.56–00:36.72 | OK · crédito: AlphaGo - The Movie (Google DeepMind) |
| E38 | video | edicao/extras/E38.mp4 (00:00.00–00:07.08) | L09 | split | 00:36.72–00:43.80 | OK · crédito: The Thinking Game (Google DeepMind / Greg Kohs) |
| E39 | video | edicao/extras/E39.mp4 (00:00.00–00:03.76) | L10 | split | 00:43.80–00:47.56 | OK · crédito: The Thinking Game (Google DeepMind / Greg Kohs) |

## Enquadramento (zoom por peça — aplicado UMA vez, no corte)

> Cada corte troca o enquadramento (1.00 ↔ 1.12, origem no rosto) para disfarçar o jump cut. Para mudar: `zoom_pecas` (uma escala por peça) e/ou `zoom_origem` ("x% y%") no segmento + `edl.py --recalcular`; `"zoom": {"tipo": "punch", "escala": 1.2}` muda a escala do punch e faz o segmento começar fechado.

- **L01** · origem 50% 38% (padrão (rosto 1/4)) · 1.00 → 1.12
- **L02** · origem 54.8% 33.4% (rosto 4/4) · 1.00 → 1.12
- **L03** · origem 62.6% 30.2% (rosto 3/4) · 1.00 → 1.12 → 1.12 → 1.00
- **L04** · origem 55.1% 33.0% (rosto 2/4) · 1.12 → 1.00
- **L05** · origem 43.8% 32.9% (rosto 3/3) · 1.12 → 1.00 → 1.12
- **L06** · origem 60.3% 31.5% (padrão (rosto 1/3)) · 1.00 → 1.12 → 1.06
- **L07** · origem 49.6% 32.6% (rosto 3/4) · 1.00 → 1.12 → 1.00 → 1.12
- **L08** · origem 43.0% 30.6% (rosto 2/3) · 1.12 → 1.00 → 1.12
- **L09** · origem 46.9% 30.4% (rosto 4/4) · 1.12 → 1.00 → 1.12 → 1.00
- **L10** · origem 55.3% 31.4% (rosto 4/4) · 1.12 → 1.00
- **L12** · origem 54.0% 32.2% (rosto 5/5) · 1.12 → 1.12 → 1.00 → 1.12 → 1.00
- **L13** · origem 39.6% 30.1% (rosto 3/3) · 1.00 → 1.12 → 1.00

31 corte(s) com troca de enquadramento · **sem troca: L03, L08, L09, L12, L13**
