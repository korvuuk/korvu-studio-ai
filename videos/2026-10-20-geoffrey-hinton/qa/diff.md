# QA do corte — 2026-10-20-geoffrey-hinton

Vídeo: `edicao/corte.mp4` · engine scribe · 2026-10-15T01:40:30+01:00

**Resultado: FALHOU** — 1.19s de voz da IA detectados no áudio do corte (limite 0.2s); WER geral 40.7% > 8%

- WER geral: **40.7%** (limite 8%; 127 erros / 312 palavras esperadas)
- Duração: vídeo 158.640s · áudio 158.680s · soma das peças 158.680s · EDL 158.680s · alvo 90.0s (+76%)
- Sincronia A/V: OK (Δ 40.0 ms; tolerância 1 frame = 40.0 ms)
- Duração vs peças: OK (Δ 40.0 ms)
- FPS: OK (25 fps; projeto 25) · 1080x1920 yuv422p10le
- Voz da IA no corte: FALHOU — **1.19 s** detectados (limite 0.2 s; modelo por quadro do `edicao/locutores.json`) · peças da EDL dentro das zonas da IA: 0.00 s · trechos: 00:02.18–00:02.22, 00:11.88–00:11.94, 00:22.15–00:22.22, 00:34.91–00:34.94, 00:38.81–00:38.92, 00:59.17–00:59.23, 00:59.67–00:59.73, 01:02.82–01:02.84, 01:06.85–01:06.87, 01:07.26–01:07.32, 01:20.85–01:21.00, 01:35.15–01:35.26, 01:59.31–01:59.36, 02:05.55–02:05.61, 02:08.41–02:08.52, 02:12.86–02:12.91, 02:16.97–02:17.04, 02:32.54–02:32.60

| Linha | Status | WER | Esperado (roteiro) | Ouvido no corte |
|---|---|---|---|---|
| L01 | presente | 7.1% | Imagina você passar quase 50 anos acreditando numa ideia que ninguém levava a sério… | Imagina você passar 50 anos acreditando numa ideia que ninguém levava a sério |
| L02 | presente | 6.7% | E, no final, essa ideia mudar o mundo e ainda te dar um Prêmio Nobel. | e, no final, essa ideia mudar o mundo e ainda te dá um Prêmio Nobel. |
| L03 | presente | 11.1% | Pois é. Essa é a história de Geoffrey Hinton. | Pois é, essa é a história do Geoffrey Hinton. |
| L04 | presente | 13.3% | Hinton nasceu em Londres, em 1947, numa família de cientistas. | Hinton nasceu em Londres em 1947, em uma família de cientistas. |
| L05 | presente | 58.3% | Mas, diferente do que muita gente imagina, ele não começou estudando computadores. | Mas, diferente que muitas pessoas imaginavam, ele não começou a estudar os computadores. |
| L06 | presente | 12.5% | Ele queria entender como funciona a mente humana. | Ele queria entender como funcionava a mente humana. |
| L07 | presente | 23.1% | Nos anos 70, começou a defender uma ideia que parecia impossível naquela época: | Nos anos 70, ele começou a defender uma ideia que parecia impossível: |
| L08 | presente | 78.6% | E se a gente conseguisse criar máquinas capazes de aprender como o cérebro humano? | e se a gente criasse uma máquina que consegue imitar a mente humana? Só que |
| L09 | presente | 37.5% | O problema é que quase ninguém acreditava nisso. | o problema: quase ninguém acreditava nessa |
| L10 | presente | 80.0% | Até o próprio orientador dele aconselhou que abandonasse essa pesquisa, porque poderia destruir sua carreira. | ideia. O mais curioso, o próprio orientador dele aconselhou ele a abandonar essa pesquisa, porque essa pesquisa pode comprometer a carreira |
| L11 | presente | 200.0% | Mas Hinton não desistiu. | dele. Como o cara é fera, ele simplesmente não desistiu. |
| L12 | presente | 33.3% | Em 2012, junto com dois alunos, | Em 2012, ele juntou com dois alunos e |
| L13 | presente | 41.7% | ele desenvolveu um sistema capaz de reconhecer imagens com uma precisão impressionante. | ele desenvolveu um sistema capaz de reconhecer imagem de forma precisa e |
| L14 | presente | 100.0% | Aquilo mudou completamente o rumo da inteligência artificial. | impecável. Foi aí que ele acabou de mudar o rumo da inteligência artificial. |
| L15 | presente | 54.5% | Pouco depois, o Google comprou a empresa que eles tinham criado. | Pouco depois, o Google acabou de comprar a empresa que eles acabaram de criar. |
| L16 | presente | 54.5% | E Hinton passou 10 anos trabalhando com a gigante da tecnologia. | E o Hinton passou mais de dez anos trabalhando junto com gigantes da tecnologia. |
| L17 | presente | 50.0% | Mas olha que interessante… | Agora, olha só que interessante. |
| L18 | presente | 18.2% | Em 2023, ele deixou o Google | Em 2023, ele acabou deixando o Google |
| L19 | presente | 10.0% | para poder falar livremente sobre os riscos da inteligência artificial. | para poder falar livremente sobre os riscos das inteligência artificial. |
| L20 | presente | 23.1% | E, um ano e meio depois, recebeu uma ligação às duas da manhã. | E um ano e meio depois, ele recebeu uma ligação às duas e meia da manhã. |
| L21 | presente | 20.0% | Era o comitê do Nobel. | era a comitê do Nobel. |
| L22 | presente | 62.5% | Ele tinha acabado de ganhar o Nobel de Física de 2024. | Ele tinha acabado de ganhado um Nobel e |
| L23 | presente | 9.1% | Hoje, Geoffrey Hinton é conhecido como o padrinho da inteligência artificial. | hoje o Geoffrey Hinton é conhecido como o padrinho da inteligência artificial. |
| L24 | presente | 14.3% | E o mais curioso é que o homem que ajudou a desenvolver essa tecnologia | E o mais curioso, o homem que ajudou a desenvolver essa tecnologia |
| L25 | presente | 36.4% | é também um dos que mais alertam sobre os seus riscos. | é também o que mais alerta sobre os riscos |
| L26 | presente | 0.0% | A história dele mostra uma coisa: | A história dele mostra uma coisa: |
| L27 | presente | 0.0% | Às vezes, uma ideia que ninguém acredita pode mudar o mundo. | às vezes, uma ideia que ninguém acredita pode mudar o mundo. |
| L28 | presente | 83.3% | Comenta NOBEL que eu te mando o link oficial da entrevista dele. | Comenta a palavra Nobel que eu vou te enviar a entrevista completa e também não |
| L29 | presente | 70.0% | E manda pra alguém que tá desistindo de uma ideia. | esquece de mandar pra alguém que tá querendo desistir duma grande ideia. |

## Trechos extras (fala fora do roteiro no corte)

- 01:54.06–01:54.88: "E a ligação"
- 02:17.52–02:18.90: "da inteligência artificial."

> Aviso: duração 158.6s está +76% do alvo de 90.0s (não reprova).
