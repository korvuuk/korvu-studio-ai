# EDL — 2026-10-20-fei-fei-li (versão 14)

> **Como aprovar:** assista `edicao/preview.mp4` e revise a tabela. Para aprovar, diga ao agente
> **"aprovado"** — ou edite `edicao/edl.json` e troque `"aprovado": false` por `"aprovado": true`.
> **Trocar take:** diga, por exemplo, "L05 usa T1" (o agente muda `segmentos[].take` e roda `edl.py --recalcular`).
> **Ajuste fino:** edite `in` / `out` / `cortes_internos` no `edl.json` e rode `edl.py --recalcular`.

**Estado:** APROVADA · **Duração do corte:** 168.4 s (alvo 165.0 s) · **Linhas:** 23 ok, 0 revisar, 11 paráfrase, 0 faltando

**Locutores (método ChatGPT-monitor):** local · IA = classe A (confiança 0.927) · IA 212.9 s · Carlos 395.9 s · 51 leitura(s) da IA e 52 fala(s) de monitor fora do corte · sobreposições 0 · a coluna **IA · Carlos** = leituras da IA · takes do Carlos da linha

| # | Linha | Status | Take | Fonte · in → out | Saída | Texto no corte | Alternativas | IA · Carlos |
|---|---|---|---|---|---|---|---|---|
| 1 | L01 | [OK] | T1 | praq0987 · 01:23.20 → 01:28.44 ✂1 | 00:00.00–00:05.00 | Imagina chegar adolescente num país novo e sem falar o inglês. | — | 2 · 1 |
| 2 | L02 | [OK] | T1 | praq0987 · 01:35.40 → 01:39.28 | 00:05.00–00:08.88 | E anos depois, ajudar as máquinas a enxergar o mundo. | — | 1 · 1 |
| 3 | L03 | [OK] | T2 | praq0987 · 01:57.28 → 01:59.68 | 00:08.88–00:11.28 | Essa é a história da Fei-Fei Li. | T1 (0.86) | 1 · 2 |
| 4 | L04 | [OK] | T1 | praq0987 · 02:10.16 → 02:16.08 ✂2 | 00:11.28–00:16.32 | Ela nasceu na China e chegou nos Estados Unido e ainda adolescente. | — | 2 · 1 |
| 5 | L05 | [OK] | T1 | praq0987 · 02:25.56 → 02:28.96 | 00:16.32–00:19.72 | E os pais praticamente não falavam inglês. | — | 1 · 1 |
| 6 | L06 | [PARAFRASE] | T2 | praq0987 · 03:22.80 → 03:32.32 ✂2 | 00:19.72–00:28.04 | Então, na lavanderia da família, ela atendia os telefone e fazia as cobranças e até atendia os fiscais. | T1 (0.53; muleta, pausa_interna, final_cortado) | 2 · 2 |
| 7 | L07 | [OK] | T1 | praq0987 · 03:38.84 → 03:39.72 | 00:28.04–00:28.92 | Ela. | — | 1 · 1 |
| 8 | L08 | [PARAFRASE] | T1 | praq0987 · 03:47.16 → 03:52.32 ✂1 | 00:28.92–00:33.44 | E foi assim, ela contou que foi assim que ela ajudou a pagar as faculdade. | — | 1 · 1 |
| 9 | L09 | [PARAFRASE] | T2 | praq0987 · 05:13.56 → 05:20.60 | 00:33.44–00:40.48 | Fei-Fei estudou Física em Princeton e foi aí que ela entrou para o mundo da inteligência artificial. | T1 (0.77; muleta, pausa_interna) | 2 · 2 |
| 10 | L10 | [PARAFRASE] | T1 | praq0987 · 05:29.52 → 05:34.88 ✂1 | 00:40.48–00:45.44 | E a partir daí, ela começou a pensar em uma coisa muito simples. | — | 3 · 1 |
| 11 | L11 | [OK] | T6 | praq0987 · 07:55.80 → 08:03.72 ✂4 | 00:45.44–00:52.36 | Uma criança aprende a reconhecer o mundo vendo milhões de exemplos. | T1 (0.46; pausa_interna, final_cortado) · T2 (0.75) · T3 (0.75; pausa_interna) · T4 (0.83; pausa_interna, fala_ia_interna) · T5 (1.00) | 2 · 6 |
| 12 | L12 | [PARAFRASE] | T2 | praq0987 · 09:23.44 → 09:28.16 ✂1 | 00:52.36–00:56.56 | Então, por que que um computador deveria ser diferente? | T1 (0.56) | 2 · 2 |
| 13 | L13 | [OK] | T3 | praq0987 · 10:32.60 → 10:37.32 ✂1 | 00:56.56–01:00.96 | Em 2007, ela começou um projeto chamado ImageNet. | T1 (0.75; muleta) · T2 (0.91) | 2 · 3 |
| 14 | L14 | [PARAFRASE] | T3 | praq0987 · 12:00.08 → 12:10.52 ✂3 | 01:00.96–01:10.08 | A ideia era reunir milhões de imagem e passar para o computador reconhecer exatamente cada uma delas | T1 (0.42; final_cortado) · T2 (0.16; false_start) | 2 · 3 |
| 15 | L15 | [PARAFRASE] | T4 | praq0987 · 13:42.76 → 13:53.68 ✂3 | 01:10.08–01:18.96 | Segundo ela, 50 mil pessoas pela internet ajudaram a organizar e identificar cada uma dessas imagens. | T1 (0.60; pausa_interna, sem_ancora) · T2 (0.73; pausa_interna, sem_ancora) · T3 (0.53; pausa_interna) | 1 · 4 |
| 16 | L16 | [OK] | T1 | praq0987 · 14:19.88 → 14:22.60 | 01:18.96–01:21.68 | E sabe o mais curioso? | — | 1 · 1 |
| 17 | L17 | [OK] | T1 | praq0987 · 14:32.64 → 14:38.36 ✂2 | 01:21.68–01:26.64 | Ela disponibilizou tudo de graça para os pesquisadores. | — | 2 · 1 |
| 18 | L18 | [OK] | T1 | praq0987 · 14:45.32 → 14:48.04 | 01:26.64–01:29.36 | Aí chega o 2012. | — | 1 · 1 |
| 19 | L19 | [MANUAL] | T4 | praq0987 · 16:29.40 → 16:40.80 ✂4 | 01:29.36–01:39.08 | Um grupo da Universidade de Toronto usaram a ImageNet para treinar uma rede neurais em uma competição de reconhecimento das imagens. | T1 (0.55; muleta, final_cortado) · T2 (0.81; muleta, pausa_interna) · T3 (0.45; muleta, pausa_interna, final_cortado) | 1 · 4 |
| 20 | L20 | [OK] | T1 | praq0987 · 16:55.32 → 16:57.60 | 01:39.08–01:41.36 | E sabe quem tava nesse grupo? | — | 1 · 1 |
| 21 | L21 | [OK] | T1 | praq0987 · 17:31.40 → 17:36.32 | 01:41.36–01:46.28 | Geoffrey Hinton, de quem eu já falei aqui no meu canal. | — | 2 · 1 |
| 22 | L22 | [OK] | T4 | praq0987 · 19:01.56 → 19:11.80 ✂3 | 01:46.28–01:55.64 | O resultado foi tão superior ao concorrente e naquele momento começou a mudar o rumo da inteligência artificial. | T1 (0.56; pausa_interna) · T2 (0.72; muleta) · T3 (0.78; muleta) | 1 · 4 |
| 23 | L23 | [OK] | T1 | praq0987 · 19:18.92 → 19:21.28 | 01:55.64–01:58.00 | mas olha só que interessante. | — | 1 · 1 |
| 24 | L24 | [OK] | T1 | praq0987 · 19:33.44 → 19:35.40 | 01:58.00–01:59.96 | A IA era deles. | — | 1 · 1 |
| 25 | L25 | [PARAFRASE] | T1 | praq0987 · 19:42.60 → 19:46.00 ✂1 | 01:59.96–02:03.00 | Os exemplos era dela. | — | 1 · 1 |
| 26 | L26 | [OK] | T1 | praq0987 · 19:54.84 → 20:00.96 ✂2 | 02:03.00–02:08.40 | Hoje, a imprensa chama a Fei-Fei Li da madrinha da inteligência artificial | — | 1 · 1 |
| 27 | L26 | [MANUAL] | manual | praq0988 · 00:00.00 → 00:00.32 | 02:08.40–02:08.72 |  | T1 (0.83; muleta) | 1 · 1 |
| 28 | L27 | [OK] | T1 | praq0988 · 00:07.32 → 00:11.92 ✂1 | 02:08.72–02:13.04 | E a história dela mostra uma coisa muito importante | — | 1 · 1 |
| 29 | L28 | [OK] | T2 | praq0988 · 00:38.52 → 00:42.00 | 02:13.04–02:16.52 | A inteligência artificial não aprende por mágica | T1 (0.57; muleta) | 2 · 2 |
| 30 | L29 | [MANUAL] | T3 | praq0989 · 01:05.60 → 01:15.60 ✂3 | 02:16.52–02:24.04 | Ela aprende porque alguém teve o trabalho de organizar informações, ensinar o que cada coisa significa. | T1 (0.53) · T2 (0.58; muleta, pausa_interna) · T4 (0.26; false_start) · T5 (0.53; pausa_interna) | 2 · 5 |
| 31 | L30 | [OK] | T1 | praq0991 · 00:17.00 → 00:20.20 | 02:24.04–02:27.24 | E às vezes, quem ajuda a mudar o futuro- | — | 1 · 1 |
| 32 | L31 | [OK] | T7 | praq0992 · 01:03.16 → 01:10.84 ✂2 | 02:27.24–02:33.88 | É aquela adolescente que um dia precisou traduzir tudo para sua própria família. | T1 (0.54) · T2 (0.69) · T3 (0.23; false_start) · T4 (0.61; final_cortado) · T5 (1.00) · T6 (0.93; pausa_interna) | 2 · 7 |
| 33 | L32 | [MANUAL] | manual | praq0993 · 00:11.48 → 00:18.44 ✂1 | 02:33.88–02:40.64 | Comenta "aula" aqui embaixo, eu te envio no seu direct uma entrevista completa sobre a Fei Fei Li. | T1 (0.46; false_start) · T2 (0.55; final_cortado) · T3 (0.46; pausa_interna, final_cortado) | 1 · 3 |
| 34 | L33 | [PARAFRASE] | T1 | praq0993 · 00:46.44 → 00:49.88 | 02:40.64–02:44.08 | São somente 18 minutos com a legenda em português. | — | 1 · 1 |
| 35 | L34 | [OK] | T1 | praq0993 · 00:56.92 → 01:01.28 | 02:44.08–02:48.44 | E manda esse vídeo pra alguém que já foi o tradutor da família. | — | 1 · 1 |

## Motivos e cortes internos

- **L01** [OK]: último take limpo (sim 0.82); muleta cortada internamente · cortes internos: 01:26.92–01:27.16
- **L02** [OK]: último take limpo (sim 1.00)
- **L03** [OK]: último take limpo (sim 1.00)
- **L04** [OK]: último take limpo (sim 0.83); muleta cortada internamente, pausa interna encurtada · cortes internos: 02:11.76–02:12.48, 02:14.36–02:14.52
- **L05** [OK]: último take limpo (sim 1.00)
- **L06** [PARAFRASE]: paráfrase: melhor sim 0.50 (score 0.65) · cortes internos: 03:25.24–03:25.80, 03:27.88–03:28.52
- **L07** [OK]: último take limpo (sim 1.00)
- **L08** [PARAFRASE]: paráfrase: melhor sim 0.60 (score 0.74) · cortes internos: 03:48.12–03:48.76
- **L09** [PARAFRASE]: paráfrase: melhor sim 0.77 (score 0.86)
- **L10** [PARAFRASE]: paráfrase: melhor sim 0.70 (score 0.80) · cortes internos: 05:30.64–05:31.04
- **L11** [OK]: último take limpo (sim 1.00); pausa interna encurtada · cortes internos: 07:56.84–07:56.96, 07:59.20–07:59.32, 08:00.32–08:00.80, 08:01.76–08:02.04
- **L12** [PARAFRASE]: paráfrase: melhor sim 0.67 (score 0.79) · cortes internos: 09:24.92–09:25.44
- **L13** [OK]: último take limpo (sim 1.00) · cortes internos: 10:34.04–10:34.36
- **L14** [PARAFRASE]: paráfrase: melhor sim 0.55 (score 0.69) · cortes internos: 12:01.00–12:01.36, 12:05.04–12:05.44, 12:07.32–12:07.88
- **L15** [PARAFRASE]: paráfrase: melhor sim 0.67 (score 0.79) · cortes internos: 13:43.96–13:45.08, 13:47.28–13:47.92, 13:51.96–13:52.24
- **L16** [OK]: último take limpo (sim 1.00)
- **L17** [OK]: último take limpo (sim 0.88) · cortes internos: 14:34.36–14:34.76, 14:35.96–14:36.32
- **L18** [OK]: último take limpo (sim 0.86)
- **L19** [OK]: último take limpo (sim 0.81); muleta cortada internamente, pausa interna encurtada · cortes internos: 16:31.48–16:31.76, 16:34.44–16:34.88, 16:36.40–16:37.16, 16:38.44–16:38.64
- **L20** [OK]: último take limpo (sim 1.00)
- **L21** [OK]: último take limpo (sim 1.00)
- **L22** [OK]: último take limpo (sim 0.83); muleta cortada internamente · cortes internos: 19:05.00–19:05.36, 19:06.64–19:07.00, 19:10.40–19:10.56
- **L23** [OK]: último take limpo (sim 0.80)
- **L24** [OK]: último take limpo (sim 1.00)
- **L25** [PARAFRASE]: paráfrase: melhor sim 0.75 (score 0.82) · cortes internos: 19:44.64–19:45.00
- **L26** [OK]: último take limpo (sim 0.83); muleta cortada internamente · cortes internos: 19:56.40–19:56.76, 19:58.56–19:58.92
- **L27** [OK]: último take limpo (sim 1.00) · cortes internos: 00:08.36–00:08.64
- **L28** [OK]: último take limpo (sim 0.80)
- **L29** [PARAFRASE]: paráfrase: melhor sim 0.53 (score 0.66); L29-T3 pontua mais (0.80 vs 0.66) — peça a troca se preferir · cortes internos: 01:07.84–01:08.08, 01:09.20–01:09.44, 01:11.12–01:13.12
- **L30** [OK]: último take limpo (sim 1.00)
- **L31** [OK]: último take limpo (sim 0.92); pausa interna encurtada · cortes internos: 01:06.12–01:06.76, 01:07.60–01:08.00
- **L32** [PARAFRASE]: paráfrase: melhor sim 0.46 (score 0.61) · cortes internos: 00:16.76–00:16.96
- **L33** [PARAFRASE]: paráfrase: melhor sim 0.78 (score 0.87)
- **L34** [OK]: último take limpo (sim 1.00)
- **L01B** [PARAFRASE] (hook alternativo de L01): paráfrase: melhor sim 0.67 (score 0.77)
- **L01C** [PARAFRASE] (hook alternativo de L01): paráfrase: melhor sim 0.40 (score 0.61)

## Fora do corte

- Não mapeado (praq0987 00:00.28–00:01.98): "Você já tem o roteiro, ok?"
- Não mapeado (praq0987 00:05.58–00:06.44): "Tá com o roteiro pronto?"
- Não mapeado (praq0987 00:10.16–00:11.36): "Ok. Hum."
- Não mapeado (praq0987 00:21.74–00:24.11): "Ok, podemos começar? Tudo pronto?"
- Não mapeado (praq0987 01:00.50–01:00.60): "Ok."
- Não mapeado (praq0987 01:02.14–01:03.04): "Pronto, podemos ir."
- Não mapeado (praq0987 01:11.60–01:12.30): "Imagina--"
- Não mapeado (praq0987 02:58.58–02:59.20): "os ficais."
- Não mapeado (praq0987 04:17.90–04:21.46): "Fei-Fei Li estudou Física em Princeton."
- Não mapeado (praq0987 04:32.56–04:34.88): "Fei-Fei estudou em Princeton."
- Não mapeado (praq0987 08:27.36–08:36.30): "Foi aí que ela tem uma sacada. Ela pensou assim: "Por que, então, que um computador não pode fazer o mesmo?""
- Não mapeado (praq0987 08:42.72–08:50.58): "Então, foi aí que ela teve uma sacada. Por que, então, que um computador não pode fazer o mesmo?"
- Não mapeado (praq0987 09:02.38–09:04.94): "Foi aí que ela teve uma sacada."
- Não mapeado (praq0987 09:36.98–09:39.22): "E aí, em 2027-"
- Não mapeado (praq0987 10:20.24–10:20.88): "ImageMed."
- Não mapeado (praq0987 11:25.36–11:29.28): "o computador reconhecer cada uma delas."
- Não mapeado (praq0987 12:56.51–12:58.29): "e reconhecer cada uma delas."
- Não mapeado (praq0987 13:23.35–13:26.33): "imagem para reconhecer cada uma delas."
- Não mapeado (praq0987 14:04.93–14:05.79): "E sabe qual a ma-"
- Não mapeado (praq0987 15:38.37–15:38.89): "imagem."
- Não mapeado (praq0987 16:46.75–16:47.19): "Próximo."
- Não mapeado (praq0987 17:06.77–17:08.35): "Ninguém mais de que o"
- Não mapeado (praq0987 17:10.05–17:15.81): "Geoffrey Hinton. Foi a pessoa que eu falei anteriormente no vídeo passado."
- Não mapeado (praq0987 18:20.65–18:21.15): "Os resulta--"
- Não mapeado (praq0987 19:18.19–19:18.55): "Agora,"
- Não mapeado (praq0987 19:24.77–19:25.21): "Próximo."
- Não mapeado (praq0988 00:26.42–00:26.64): "As"
- Não mapeado (praq0990 00:43.26–00:43.72): "e como,"
- Não mapeado (praq0990 00:45.14–00:47.40): "como identificar. Caramba"
- Não mapeado (praq0991 00:03.50–00:05.74): "Ela aprende porque? Caramba."
- Não mapeado (praq0991 00:08.50–00:08.94): "Próximo."
- Não mapeado (praq0991 00:37.18–00:39.30): "que um dia mudava o mundo."
- Não mapeado (praq0992 00:00.64–00:04.58): "Que precisava traduzir tudo para sua família."
- Não mapeado (praq0993 00:00.00–00:04.58): "eu te mando no seu direct a entrevista completo da Fei Fei Li."
- Não mapeado (praq0993 00:29.86–00:33.60): "enviar no seu direct a entrevista completo sobre a Fei Fei Li."
- Não mapeado (praq0993 00:37.32–00:37.76): "Próximo."
- Não mapeado (praq0994 00:21.26–00:21.62): "Tá bom."
- Não mapeado (praq0994 00:23.98–00:25.62): "Tchau. Cansado."
- 1 trecho(s) só de muletas entre takes (descartados)
- Fala da IA — monitor (praq0987 00:33.10): "Segure três segundos."
- Fala da IA — monitor (praq0987 01:13.84): "não."
- Fala da IA — monitor (praq0987 01:15.78): "De novo."
- Fala da IA — monitor (praq0987 01:29.66): "Próximo."
- Fala da IA — monitor (praq0987 01:40.11): "Próximo."
- Fala da IA — monitor (praq0987 01:49.90): "Próximo."
- Fala da IA — monitor (praq0987 02:02.46): "De novo."
- Fala da IA — monitor (praq0987 02:17.26): "Próximo."
- Fala da IA — monitor (praq0987 02:31.78): "Próximo."
- Fala da IA — monitor (praq0987 03:00.62): "De novo."
- Fala da IA — monitor (praq0987 03:33.58): "Próximo."
- Fala da IA — monitor (praq0987 03:40.72): "Próximo."
- Fala da IA — monitor (praq0987 03:53.59): "Próximo."
- Fala da IA — monitor (praq0987 04:23.02): "De novo."
- Fala da IA — monitor (praq0987 04:36.55): "Próximo."
- Fala da IA — monitor (praq0987 05:01.70): "De novo."
- Fala da IA — monitor (praq0987 05:21.86): "De novo."
- Fala da IA — monitor (praq0987 05:37.54): "Próximo."
- Fala da IA — monitor (praq0987 05:54.20): "De novo."
- Fala da IA — monitor (praq0987 06:14.16): "Próxima."
- Fala da IA — monitor (praq0987 06:41.26): "De novo."
- Fala da IA — monitor (praq0987 09:29.62): "Próxima."
- Fala da IA — monitor (praq0987 09:42.80): "De novo."
- Fala da IA — monitor (praq0987 09:57.12): "Próxima."
- Fala da IA — monitor (praq0987 11:47.35): "De novo."
- Fala da IA — monitor (praq0987 12:15.05): "Quase 50 mil pessoas ajudaram pela internet a organizar e identificar essas imagens."
- Fala da IA — monitor (praq0987 12:35.05): "De novo."
- Fala da IA — monitor (praq0987 13:00.09): "Próximo."
- Fala da IA — monitor (praq0987 14:08.73): "Próximo."
- Fala da IA — monitor (praq0987 14:25.39): "De novo."
- Fala da IA — monitor (praq0987 14:39.60): "Próximo."
- Fala da IA — monitor (praq0987 14:49.50): "Próximo."
- Fala da IA — monitor (praq0987 16:59.07): "Próximo."
- Fala da IA — monitor (praq0987 17:17.63): "De novo."
- Fala da IA — monitor (praq0987 17:39.61): "Próximo."
- Fala da IA — monitor (praq0987 18:00.38): "Próximo."
- Fala da IA — monitor (praq0987 19:38.65): "Próximo."
- Fala da IA — monitor (praq0987 19:47.08): "Próximo."
- Fala da IA — monitor (praq0988 00:02.12): "Próxima."
- Fala da IA — monitor (praq0988 00:15.06): "Próxima."
- Fala da IA — monitor (praq0988 00:33.42): "De novo."
- Fala da IA — monitor (praq0988 00:45.46): "Próxima."
- Fala da IA — monitor (praq0988 01:14.26): "De novo."
- Fala da IA — monitor (praq0989 00:00.00): "ação e ensinar o que cada coisa significa."
- Fala da IA — monitor (praq0991 00:23.70): "Próximo."
- Fala da IA — monitor (praq0991 00:40.78): "De novo."
- Fala da IA — monitor (praq0991 00:56.56): "Próximo."
- Fala da IA — monitor (praq0992 00:19.72): "fuck now."
- Fala da IA — monitor (praq0993 00:51.86): "Próxima."
- Fala da IA — monitor (praq0993 01:03.28): "Agora vamos para os looks alternativos. Primeiro,"
- Fala da IA — monitor (praq0993 01:21.14): "Próxima"
- Fala da IA — monitor (praq0994 00:14.91): "Fim do roteiro. Se quiser gravar de novo ou ajustar algo, é só falar"
- 51 leitura(s) das linhas pela IA (nunca entram no corte; ver `leituras_ia` no alinhamento.json)

## Hooks alternativos (variantes, fora da montagem principal)

- L01B (alt. de L01): L01B-T1 · praq0993 01:11.56 → 01:17.68 [parafrase]
- L01C (alt. de L01): L01C-T1 · praq0994 00:06.76 → 00:13.24 [parafrase]

## Cenas extras

7 ok · **1 faltando** — o vídeo sai com placeholder e o QA reprova até chegar

| ID | Tipo | Arquivo | Linhas | Modo | Saída | Status |
|---|---|---|---|---|---|---|
| E01 | video | edicao/extras/E01.mp4 (00:00.00–00:02.40) | L03 | split | 00:08.88–00:11.28 | OK · crédito: San Francisco Public Library — "The Worlds I See" |
| E02 | video | edicao/extras/E02.mp4 (00:00.00–00:05.00) | L04, L05, L06 | split | 00:11.28–00:16.28 | OK · extra (5.00s) mais curto que a fala: sai 11.76s antes, em vez de segurar o último quadro; crédito: San Francisco Public Library — "The Worlds I See" |
| E08 | video | edicao/extras/E08.mp4 (00:00.00–00:04.52) | L08 | split | 00:28.92–00:33.44 | OK · crédito: Fei-Fei Li — TED2015 / TED |
| E03 | video | edicao/extras/E03.mp4 (00:00.00–00:09.00) | L10, L11, L12 | split | 00:40.48–00:49.48 | OK · extra (9.00s) mais curto que a fala: sai 7.08s antes, em vez de segurar o último quadro; crédito: Fei-Fei Li — TED2015 / TED |
| E05 | video | edicao/extras/E05.mp4 (00:00.00–00:08.00) | L14, L15 | split | 01:00.96–01:08.96 | OK · extra (8.00s) mais curto que a fala: sai 10.00s antes, em vez de segurar o último quadro; crédito: Fei-Fei Li — TED2015 / TED |
| E09 | video | edicao/extras/E09.mp4 (00:00.00–00:04.96) | L17 | split | 01:21.68–01:26.64 | OK · crédito: Fei-Fei Li — TED2015 / TED |
| E06 | print | — | L19, L20, L21, L22 | split | 01:29.36–01:55.64 | **FALTANDO** · sem arquivo: pôr em brutos/extras/E06-… e rodar ingest.py + edl.py --recalcular; crédito: image-net.org (ILSVRC 2012) |
| E01 | video | edicao/extras/E01.mp4 (00:00.00–00:05.72) | L26 | split | 02:03.00–02:08.72 | OK · crédito: San Francisco Public Library — "The Worlds I See" |

## Enquadramento (zoom por peça — aplicado UMA vez, no corte)

> Cada corte troca o enquadramento (1.00 ↔ 1.12, origem no rosto) para disfarçar o jump cut. Para mudar: `zoom_pecas` (uma escala por peça) e/ou `zoom_origem` ("x% y%") no segmento + `edl.py --recalcular`; `"zoom": {"tipo": "punch", "escala": 1.2}` muda a escala do punch e faz o segmento começar fechado.

- **L01** · origem 54.2% 34.2% (rosto 4/4) · 1.00 → 1.12
- **L02** · origem 57.1% 33.5% (rosto 3/3) · 1.00
- **L03** · origem 53.2% 32.7% (rosto 3/3) · 1.12
- **L04** · origem 49.2% 34.5% (rosto 3/3) · 1.00 → 1.12 → 1.00
- **L05** · origem 41.1% 32.2% (rosto 3/3) · 1.12
- **L06** · origem 43.5% 33.5% (rosto 3/3) · 1.00 → 1.12 → 1.00
- **L07** · origem 59.3% 34.2% (rosto 3/3) · 1.12
- **L08** · origem 43.1% 37.0% (rosto 3/4) · 1.00 → 1.12
- **L09** · origem 53.9% 34.1% (rosto 3/3) · 1.00
- **L10** · origem 45.4% 35.9% (rosto 4/4) · 1.12 → 1.00
- **L11** · origem 56.8% 34.1% (rosto 5/5) · 1.12 → 1.00 → 1.12 → 1.00 → 1.12
- **L12** · origem 51.6% 32.1% (rosto 4/4) · 1.00 → 1.12
- **L13** · origem 61.2% 34.4% (rosto 4/4) · 1.00 → 1.12
- **L14** · origem 44.2% 34.6% (rosto 4/4) · 1.00 → 1.12 → 1.00 → 1.12
- **L15** · origem 44.0% 34.7% (rosto 4/4) · 1.00 → 1.12 → 1.00 → 1.12
- **L16** · origem 46.2% 43.6% (rosto 2/3) · 1.00
- **L17** · origem 52.6% 36.3% (rosto 3/3) · 1.12 → 1.00 → 1.12
- **L18** · origem 56.0% 35.4% (rosto 3/3) · 1.00
- **L19** · origem 56.5% 35.4% (rosto 4/5) · 1.12 → 1.00 → 1.12 → 1.00 → 1.12
- **L20** · origem 58.1% 36.6% (rosto 3/3) · 1.00
- **L21** · origem 59.9% 37.1% (rosto 3/3) · 1.12
- **L22** · origem 51.4% 32.9% (rosto 4/4) · 1.00 → 1.12 → 1.00 → 1.12
- **L23** · origem 56.7% 35.2% (rosto 3/3) · 1.00
- **L24** · origem 56.2% 35.2% (rosto 3/3) · 1.12
- **L25** · origem 47.2% 36.9% (rosto 3/4) · 1.00 → 1.12
- **L26** · origem 52.5% 33.7% (rosto 3/3) · 1.00 → 1.12 → 1.00
- **L26** · origem 52.5% 33.7% (rosto 3/3) · 1.00
- **L27** · origem 49.2% 33.6% (rosto 4/4) · 1.12 → 1.00
- **L28** · origem 59.2% 34.8% (rosto 2/3) · 1.12
- **L29** · origem 46.0% 34.2% (rosto 4/4) · 1.00 → 1.12 → 1.00 → 1.12
- **L30** · origem 55.8% 34.5% (rosto 3/3) · 1.00
- **L31** · origem 51.9% 38.0% (rosto 3/3) · 1.12 → 1.00 → 1.12
- **L32** · origem 53.7% 32.7% (rosto 4/4) · 1.00 → 1.12
- **L33** · origem 59.0% 33.0% (rosto 3/3) · 1.00
- **L34** · origem 61.5% 33.2% (rosto 2/3) · 1.12

71 corte(s) com troca de enquadramento · nenhum corte com o mesmo enquadramento
