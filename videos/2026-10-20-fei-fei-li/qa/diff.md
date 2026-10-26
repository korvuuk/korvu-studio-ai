# QA do corte — 2026-10-20-fei-fei-li

Vídeo: `edicao/corte.mp4` · engine scribe · 2026-10-17T05:25:19+01:00

**Resultado: FALHOU** — 2.78s de voz da IA detectados no áudio do corte (limite 0.2s); WER geral 27.0% > 8%

- WER geral: **27.0%** (limite 8%; 91 erros / 337 palavras esperadas)
- Duração: vídeo 168.400s · áudio 168.440s · soma das peças 168.440s · EDL 168.440s · alvo 165.0s (+2%)
- Sincronia A/V: OK (Δ 40.0 ms; tolerância 1 frame = 40.0 ms)
- Duração vs peças: OK (Δ 40.0 ms)
- FPS: OK (25 fps; projeto 25) · 1080x1920 yuv422p10le
- Voz da IA no corte: FALHOU — **2.78 s** detectados (limite 0.2 s; modelo por quadro do `edicao/locutores.json`) · peças da EDL dentro das zonas da IA: 0.00 s · trechos: 00:11.36–00:11.45, 00:20.85–00:20.95, 00:22.32–00:22.38, 00:26.51–00:26.54, 00:34.80–00:34.87, 00:40.67–00:40.77, 00:45.27–00:45.33, 00:52.13–00:52.19, 00:52.46–00:52.53, 00:53.34–00:53.54, 00:54.14–00:54.19, 00:59.40–00:59.45, 01:00.76–01:00.83, 01:06.71–01:06.76, 01:07.81–01:07.92, 01:09.84–01:09.90, 01:10.73–01:10.82, 01:19.24–01:19.64, 01:25.15–01:25.20, 01:25.33–01:25.39, 01:26.15–01:26.20, 01:26.71–01:26.79, 01:38.88–01:38.92, 01:39.39–01:39.46, 01:40.15–01:40.20, 01:55.90–01:56.14, 01:57.48–01:57.53, 02:03.08–02:03.12, 02:08.86–02:08.91, 02:16.69–02:16.74, 02:21.40–02:21.50, 02:43.86–02:43.95, 02:44.18–02:44.22

| Linha | Status | WER | Esperado (roteiro) | Ouvido no corte |
|---|---|---|---|---|
| L01 | presente | 22.2% | Imagina chegar adolescente num país novo, sem falar inglês… | Imagina chegar adolescente num país novo e sem falar o inglês. |
| L02 | presente | 10.0% | e, anos depois, ajudar as máquinas a enxergar o mundo. | E ano depois, ajudar as máquinas a enxergar o mundo. |
| L03 | presente | 0.0% | Essa é a história da Fei-Fei Li. | Essa é a história da Fei-Fei Li. |
| L04 | presente | 27.3% | Ela nasceu na China e chegou aos Estados Unidos ainda adolescente. | Ela nasceu na China e chegou nos Estados Unidos, e ainda adolescente. E |
| L05 | presente | 0.0% | Os pais praticamente não falavam inglês. | os pais praticamente não falavam inglês. |
| L06 | presente | 64.7% | Então, na lavanderia da família, quem atendia o telefone, resolvia cobrança e até falava com o fiscal? | Então, na lavanderia da família, ela atendia os telefones e fazia as cobranças e até atendia os fiscais. |
| L07 | presente | 0.0% | Ela. | Ela, |
| L08 | presente | 63.6% | E foi assim, ela conta, que ajudou a pagar a faculdade. | e foi assim, ela contou, que foi assim que ela ajudou a pagar as faculdades. |
| L09 | presente | 28.6% | Fei-Fei estudou física em Princeton e depois entrou para o mundo da inteligência artificial. | Fei-Fei estudou física em Princeton e foi aí que ela entrou para o mundo da inteligência artificial. |
| L10 | presente | 55.6% | E ela começou a pensar numa coisa muito simples: | E a partir daí, ela começou a pensar em uma coisa muito simples: |
| L11 | presente | 0.0% | Uma criança aprende a reconhecer o mundo vendo milhões de exemplos. | uma criança aprende a reconhecer o mundo vendo milhões de exemplos. |
| L12 | presente | 42.9% | Então por que um computador seria diferente? | Então, por que que um computador deveria ser diferente? |
| L13 | presente | 0.0% | Em 2007, ela começou um projeto chamado ImageNet. | Em 2007, ela começou um projeto chamado ImageNet. |
| L14 | presente | 36.8% | A ideia era reunir milhões de imagens e dizer ao computador exatamente o que aparecia em cada uma delas. | A ideia era reunir milhões de imagens e passar para o computador reconhecer exatamente cada uma delas. |
| L15 | presente | 40.0% | Segundo ela, quase 50 mil pessoas ajudaram pela internet a organizar e identificar essas imagens. | Segundo ela, cinquenta mil pessoas pela internet ajudaram a organizar e identificar cada uma dessas imagens. |
| L16 | presente | 0.0% | E sabe o mais curioso? | E sabe o mais curioso? |
| L17 | presente | 14.3% | Ela disponibilizou tudo de graça para pesquisadores. | Ela disponibilizou tudo de graça para os pesquisadores. |
| L18 | presente | 16.7% | Aí chega 2012. | Aí chega o 2012. |
| L19 | presente | 30.0% | Um grupo da Universidade de Toronto usa o ImageNet para treinar uma rede neural numa competição de reconhecimento de imagens. | Um grupo da Universidade de Toronto usaram a ImageNet para treinar uma rede neurais em uma competição de reconhecimento das imagens. |
| L20 | presente | 0.0% | E sabe quem estava nesse grupo? | E sabe quem tava nesse grupo? |
| L21 | presente | 0.0% | Geoffrey Hinton, de quem eu já falei aqui. | Geoffrey Hinton, de quem eu já falei aqui |
| L22 | presente | 27.8% | O resultado foi tão superior aos concorrentes que aquele momento ajudou a mudar o rumo da inteligência artificial. | O resultado foi tão superior ao concorrente e naquele momento começou a mudar o rumo da inteligência artificial. |
| L23 | presente | 25.0% | Mas olha que interessante: | Mas olha só que interessante: |
| L24 | presente | 25.0% | A IA era deles. | a AI era deles, |
| L25 | presente | 25.0% | Os exemplos eram dela. | os exemplos era dela. |
| L26 | presente | 18.2% | Hoje, a imprensa chama Fei-Fei Li de madrinha da inteligência artificial. | Hoje, a imprensa chama a Fei-Fei Li da madrinha da inteligência artificial. |
| L27 | presente | 0.0% | E a história dela mostra uma coisa muito importante: | E a história dela mostra uma coisa muito importante: |
| L28 | presente | 60.0% | IA não aprende por mágica. | a inteligência artificial não aprende por mágica. |
| L29 | presente | 21.1% | Ela aprende porque alguém teve o trabalho de mostrar exemplos, organizar informação e ensinar o que cada coisa significa. | Ela aprende porque alguém teve o trabalho de organizar informações, ensinar o que cada coisa significa. |
| L30 | presente | 0.0% | E, às vezes, quem ajuda a mudar o futuro… | E às vezes, quem ajuda a mudar o futuro |
| L31 | presente | 7.7% | é aquela adolescente que um dia precisou traduzir tudo para a própria família. | é aquela adolescente que um dia precisou traduzir tudo para sua própria família. |
| L32 | presente | 100.0% | Comenta AULA aqui embaixo que eu te mando a palestra dela. | Comenta "aula" aqui embaixo, eu te envio no seu direct uma entrevista completa sobre a Fei-Fei Li. |
| L33 | presente | 28.6% | São 18 minutos, com legenda em português. | São somente dezoito minutos com a legenda em português. |
| L34 | presente | 0.0% | E manda esse vídeo pra alguém que já foi o tradutor da família. | E manda esse vídeo pra alguém que já foi o tradutor da família. |

## Trechos extras (fala fora do roteiro no corte)

- 01:45.26–01:45.82: "no meu canal."
