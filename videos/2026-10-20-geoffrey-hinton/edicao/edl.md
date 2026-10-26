# EDL — 2026-10-20-geoffrey-hinton (versão 24)

> **Como aprovar:** assista `edicao/preview.mp4` e revise a tabela. Para aprovar, diga ao agente
> **"aprovado"** — ou edite `edicao/edl.json` e troque `"aprovado": false` por `"aprovado": true`.
> **Trocar take:** diga, por exemplo, "L05 usa T1" (o agente muda `segmentos[].take` e roda `edl.py --recalcular`).
> **Ajuste fino:** edite `in` / `out` / `cortes_internos` no `edl.json` e rode `edl.py --recalcular`.

**Estado:** NÃO APROVADA · **Duração do corte:** 158.7 s (alvo 90.0 s) · **Linhas:** 13 ok, 0 revisar, 14 paráfrase, 2 faltando

**Locutores (método ChatGPT-monitor):** local · IA = classe A (confiança 0.917) · IA 230.4 s · Carlos 270.9 s · 46 leitura(s) da IA e 61 fala(s) de monitor fora do corte · sobreposições 4 · **11 palavra(s) com locutor incerto** · a coluna **IA · Carlos** = leituras da IA · takes do Carlos da linha

| # | Linha | Status | Take | Fonte · in → out | Saída | Texto do take | Alternativas | IA · Carlos |
|---|---|---|---|---|---|---|---|---|
| 1 | L01 | [OK] | T1 | praq0979 · 00:13.36 → 00:19.68 ✂1 | 00:00.00–00:05.84 | Imagina você passar 50 anos acreditando numa ideia que ninguém levava a sério | — | 1 · 1 |
| 2 | L02 | [OK] | T5 | praq0980 · 00:45.00 → 00:51.64 | 00:05.84–00:12.48 | E no final, essa ideia mudar o mundo e ainda te dá um Prêmio Nobel | T1 (0.47; false_start, pausa_interna) · T2 (0.47) · T3 (1.00; pausa_interna) · T4 (0.33; false_start, pausa_interna) | 4 · 5 |
| 3 | L03 | [OK] | T2 | praq0980 · 00:58.56 → 01:02.56 | 00:12.48–00:16.48 | Pois é, essa é a história do Geoffreys Hinton | T1 (0.89; sobreposicao_ia) | 2 · 2 |
| 4 | L04 | [MANUAL] | manual | praq0980 · 01:18.31 → 01:21.60 | 00:16.48–00:19.76 | Hinton nasceu em Londres, em 194 | T1 (0.47; final_cortado) · T2 (0.33; muleta, sem_ancora) | 2 · 2 |
| 5 | L04 | [MANUAL] | manual | praq0981 · 00:00.00 → 00:02.62 | 00:19.76–00:22.40 | 47 é uma família de cientistas | T1 (0.47; final_cortado) · T2 (0.33; muleta, sem_ancora) | 2 · 2 |
| 6 | L05 | [MANUAL] | manual | praq0982 · 00:16.49 → 00:23.44 ✂1 | 00:22.40–00:28.88 | Mas diferente que muitas pessoas imaginavam, ele não começou a estudar os computadores. | T1 (0.42; final_cortado) · T2 (0.17; false_start) · T3 (0.58; pausa_interna, final_cortado) | 3 · 3 |
| 7 | L06 | [OK] | T1 | praq0982 · 00:31.24 → 00:35.52 | 00:28.88–00:33.16 | Ele queria entender como funcionava a mente humana. | — | 1 · 1 |
| 8 | L07 | [PARAFRASE] | T1 | praq0982 · 00:51.80 → 00:58.08 ✂2 | 00:33.16–00:38.68 | Nos anos 70, ele começou a defender uma ideia que parecia impossível. | — | 1 · 1 |
| 9 | L08 | [MANUAL] | manual | praq0983 · 00:14.33 → 00:20.00 | 00:38.68–00:44.36 | e se a gente criasse uma máquina que consegue imitar a mente humana? | T1 (0.57; pausa_interna) | 2 · 1 |
| 10 | L09 | [MANUAL] | manual | praq0983 · 00:46.95 → 00:51.86 ✂1 | 00:44.36–00:48.92 | Só que o problema, quase ninguém acreditava nessa ideia. | T1 (0.62) | 2 · 1 |
| 11 | L10 | [MANUAL] | manual | praq0983 · 01:04.63 → 01:16.06 ✂3 | 00:48.92–00:59.04 | o mais curioso, o próprio orientador dele aconselhou ele a abandonar essa pesquisa, porque essa pesquisa pode comprometer a carreira dele. | T1 (0.47; muleta) | 1 · 1 |
| 12 | L11 | [MANUAL] | manual | praq0984 · 00:12.38 → 00:17.30 ✂1 | 00:59.04–01:03.60 | Como o cara é fera, ele simplesmente não desistiu | — | 1 · 0 |
| 13 | L12 | [OK] | T1 | praq0984 · 00:26.48 → 00:29.92 | 01:03.60–01:07.04 | em 2012, ele juntou com dois alunos | — | 1 · 1 |
| 14 | L13 | [MANUAL] | manual | praq0985 · 00:08.38 → 00:15.96 ✂1 | 01:07.04–01:14.28 | ele desenvolveu um sistema capaz de reconhecer imagem de forma precisa e impecável | T1 (0.50; final_cortado) · T2 (0.58; false_start) · T3 (0.67) | 2 · 3 |
| 15 | L14 | [MANUAL] | manual | praq0985 · 00:25.40 → 00:32.32 ✂1 | 01:14.28–01:20.64 | Foi aí que ele acabou de mudar o rumo da inteligência artificial | T1 (0.62; sem_ancora) | 2 · 1 |
| 16 | L15 | [MANUAL] | manual | praq0986 · 00:08.78 → 00:15.79 | 01:20.64–01:27.68 | Pouco depois, o Google acabou de comprar a empresa que eles acabaram de criar. | T1 (0.61; final_cortado) | 1 · 1 |
| 17 | L16 | [PARAFRASE] | T1 | praq0986 · 00:26.28 → 00:33.44 | 01:27.68–01:34.84 | E o Hinton passou mais de 10 anos trabalhando junto com gigantes da tecnologia. | — | 1 · 1 |
| 18 | L17 | [MANUAL] | manual | praq0986 · 00:39.86 → 00:42.94 | 01:34.84–01:37.96 | Agora, olha só que interessante. | T1 (0.50; sem_ancora) | 1 · 1 |
| 19 | L18 | [OK] | T1 | praq0986 · 00:52.76 → 00:56.44 ✂1 | 01:37.96–01:41.32 | Em 2023, ele acabou deixando o Google. | — | 1 · 1 |
| 20 | L19 | [OK] | T2 | praq0986 · 02:24.88 → 02:30.72 | 01:41.32–01:47.16 | Para poder falar livremente sobre os riscos da inteligência artificial. | T1 (0.55) | 1 · 2 |
| 21 | L20 | [PARAFRASE] | T2 | praq0986 · 01:42.72 → 01:50.80 ✂2 | 01:47.16–01:53.92 | E um ano e meio depois, ele recebeu uma ligação às 2:30 da manhã. | T1 (0.50; pausa_interna, sem_ancora, fala_ia_interna) | 2 · 2 |
| 22 | L21 | [MANUAL] | manual | praq0986 · 02:50.88 → 02:55.30 ✂1 | 01:53.92–01:57.88 | E a ligação era a comitê do Nobel. | T1 (0.80; muleta, pausa_interna) | 2 · 1 |
| 23 | L22 | [OK] | T2 | praq0986 · 03:27.20 → 03:31.16 ✂1 | 01:57.88–02:01.52 | Ele tinha acabado de ganhado um Nobel de Física em 2024. | T1 (0.44; muleta, final_cortado) | 2 · 2 |
| 24 | L23 | [MANUAL] | manual | praq0986 · 03:42.24 → 03:49.86 ✂1 | 02:01.52–02:08.72 | E hoje, o Geoffrey Hinton é conhecido como o padrinho da inteligência artificial. | T1 (0.91) | 1 · 1 |
| 25 | L24 | [OK] | T1 | praq0986 · 04:00.20 → 04:05.08 ✂1 | 02:08.72–02:13.28 | E o mais curioso, o homem que ajudou a desenvolver essa tecnologia | — | 1 · 1 |
| 26 | L25 | [MANUAL] | manual | praq0986 · 04:17.04 → 04:22.90 | 02:13.28–02:19.12 | É também o que mais alerta sobre os riscos da inteligência artificial. | T1 (0.73) | 1 · 1 |
| 27 | L26 | [OK] | T1 | praq0986 · 04:29.40 → 04:32.36 | 02:19.12–02:22.08 | a história dele mostra uma coisa. | — | 1 · 1 |
| 28 | L27 | [OK] | T1 | praq0986 · 04:42.84 → 04:49.16 ✂1 | 02:22.08–02:27.76 | Às vezes, uma ideia que ninguém acredita pode mudar o mundo. | — | 1 · 1 |
| 29 | L28 | [MANUAL] | manual | praq0986 · 04:59.48 → 05:04.40 ✂1 | 02:27.76–02:32.32 | Comenta a palavra Nobel que eu vou te enviar a entrevista completa. | T1 (0.25; muleta, sem_ancora) · T2 (0.25; muleta, sem_ancora) · T3 (0.23; muleta, sem_ancora) | 1 · 3 |
| 30 | L29 | [MANUAL] | manual | praq0986 · 06:03.58 → 06:09.95 | 02:32.32–02:38.68 | E também não esquece de mandar pra alguém que tá querendo desistir duma grande ideia. | T1 (0.55) | 2 · 1 |

## Motivos e cortes internos

- **L01** [OK]: último take limpo (sim 0.93) · cortes internos: 00:15.64–00:16.12
- **L02** [OK]: último take limpo (sim 0.93)
- **L03** [OK]: último take limpo (sim 0.89)
- **L04** [PARAFRASE]: paráfrase: melhor sim 0.47 (score 0.52)
- **L05** [PARAFRASE]: paráfrase: melhor sim 0.58 (score 0.69) · cortes internos: 00:19.92–00:20.40
- **L06** [OK]: último take limpo (sim 1.00)
- **L07** [PARAFRASE]: paráfrase: melhor sim 0.77 (score 0.84) · cortes internos: 00:53.36–00:53.76, 00:56.12–00:56.48
- **L08** [PARAFRASE]: paráfrase: melhor sim 0.57 (score 0.69)
- **L09** [PARAFRASE]: paráfrase: melhor sim 0.62 (score 0.74) · cortes internos: 00:48.08–00:48.40
- **L10** [PARAFRASE]: paráfrase: melhor sim 0.47 (score 0.64) · cortes internos: 01:05.88–01:06.32, 01:07.96–01:08.40, 01:11.72–01:12.16
- **L11** [FALTANDO]: a IA leu a linha (1×), mas não há take do Carlos · cortes internos: 00:14.04–00:14.36
- **L12** [OK]: último take limpo (sim 0.90)
- **L13** [PARAFRASE]: paráfrase: melhor sim 0.67 (score 0.77) · cortes internos: 00:13.08–00:13.40
- **L14** [PARAFRASE]: paráfrase: melhor sim 0.62 (score 0.74) · cortes internos: 00:27.36–00:27.92
- **L15** [PARAFRASE]: paráfrase: melhor sim 0.61 (score 0.73)
- **L16** [PARAFRASE]: paráfrase: melhor sim 0.64 (score 0.79)
- **L17** [PARAFRASE]: paráfrase: melhor sim 0.50 (score 0.69)
- **L18** [OK]: último take limpo (sim 0.83) · cortes internos: 00:54.36–00:54.68
- **L19** [OK]: último take limpo (sim 1.00)
- **L20** [PARAFRASE]: paráfrase: melhor sim 0.75 (score 0.83) · cortes internos: 01:44.44–01:45.20, 01:47.60–01:48.16
- **L21** [OK]: último take limpo (sim 0.80); muleta cortada internamente, pausa interna encurtada · cortes internos: 02:52.00–02:52.44
- **L22** [OK]: último take limpo (sim 0.81); muleta cortada internamente, pausa interna encurtada · cortes internos: 03:29.80–03:30.12
- **L23** [OK]: último take limpo (sim 0.91) · cortes internos: 03:45.00–03:45.40
- **L24** [OK]: último take limpo (sim 0.86) · cortes internos: 04:01.40–04:01.72
- **L25** [PARAFRASE]: paráfrase: melhor sim 0.73 (score 0.81)
- **L26** [OK]: último take limpo (sim 1.00)
- **L27** [OK]: último take limpo (sim 1.00); pausa interna encurtada · cortes internos: 04:46.52–04:47.16
- **L28** [FALTANDO]: a IA leu a linha (1×), mas não há take do Carlos; só tentativas incompletas/fracas (3 take(s), melhor sim 0.25) · cortes internos: 05:02.44–05:02.80
- **L29** [PARAFRASE]: paráfrase: melhor sim 0.55 (score 0.69)
- **L01B** [OK] (hook alternativo de L01): último take limpo (sim 1.00)
- **L01C** [OK] (hook alternativo de L01): último take limpo (sim 0.90)

## Fora do corte

- Não mapeado (praq0978 00:17.96–00:19.06): "Ok, estamos de volta."
- Não mapeado (praq0978 00:23.60–00:25.98): "Estamos de volta, podemos voltar a ler o, o roteiro?"
- Não mapeado (praq0978 00:36.14–00:37.16): "Vamos começar do início."
- Não mapeado (praq0978 01:09.74–01:14.36): "Pronto, pode pular a p-a fase do, da pose e vamos diretamente pro roteiro."
- Não mapeado (praq0979 00:03.16–00:03.92): "Ok, começar"
- Não mapeado (praq0979 00:55.74–00:56.24): "Próxima."
- Não mapeado (praq0979 01:14.94–01:17.76): "Vamos repetir aaa, a linha anterior"
- Não mapeado (praq0980 00:00.56–00:01.30): "Não, não, não, não."
- Não mapeado (praq0980 00:02.24–00:03.34): "a linha anterior dessa"
- Não mapeado (praq0980 00:06.86–00:10.28): "Ah, certo. Vamo voltar. Me diga qual linha"
- Não mapeado (praq0980 00:15.08–00:18.94): "A linha anterior que seria: "de mudar o mundo""
- Não mapeado (praq0981 00:36.72–00:39.94): "Porém, diferente que muitas pessoas imagin-"
- Não mapeado (praq0981 00:44.88–00:46.72): "Calma, calma, calma. Faz o seguinte:"
- Não mapeado (praq0981 00:47.80–00:52.56): "quando você ler uma linha, espera quando eu peço pra você prosseguir, ok?"
- Não mapeado (praq0981 01:07.26–01:10.40): "Porém, diferente que muitas pessoas imaginavam,"
- Não mapeado (praq0981 01:11.98–01:14.80): "o Hinton vem duma família de cientistas"
- Não mapeado (praq0982 00:22.00–00:23.24): "a estudar os computadores."
- Não mapeado (praq0982 01:11.50–01:12.40): "Ele pensou assim:"
- Não mapeado (praq0983 00:11.50–00:19.54): "E aí ele começou a pensar assim: e se a gente criasse uma máquina que consegue imitar a mente humana?"
- Não mapeado (praq0983 00:29.96–00:35.42): "Só que aí que tá o problema. As pessoas não acreditavam nessa ideia."
- Não mapeado (praq0983 00:47.08–00:47.30): "Só que"
- Não mapeado (praq0983 00:50.92–00:51.66): "nessa ideia."
- Não mapeado (praq0983 01:03.66–01:05.80): "E aí, o mais curioso,"
- Não mapeado (praq0983 01:15.58–01:15.86): "dele."
- Não mapeado (praq0984 00:06.58–00:07.04): "Próximo"
- Não mapeado (praq0984 00:12.52–00:16.70): "Como o cara é fera, ele simplesmente não desistiu"
- Não mapeado (praq0984 00:42.14–00:43.54): "E aí vem uma sacada."
- Não mapeado (praq0984 00:48.94–00:51.80): "imagem duma forma impecável"
- Não mapeado (praq0984 01:12.42–01:14.12): "imagem de forma"
- Não mapeado (praq0984 01:15.50–01:16.22): "impecável"
- Não mapeado (praq0985 00:14.92–00:15.76): "e impecável"
- Não mapeado (praq0985 00:25.54–00:27.22): "Foi aí que ele"
- Não mapeado (praq0986 00:15.24–00:15.59): "criar."
- Não mapeado (praq0986 00:40.00–00:40.36): "Agora,"
- Não mapeado (praq0986 01:13.48–01:14.69): "de forma mais livre."
- Não mapeado (praq0986 02:51.02–02:51.86): "E a ligação"
- Não mapeado (praq0986 03:42.62–03:43.08): "E hoje,"
- Não mapeado (praq0986 04:05.38–04:06.68): "da inteligência artificial..."
- Não mapeado (praq0986 04:21.28–04:22.67): "da inteligência artificial."
- Não mapeado (praq0986 05:13.44–05:14.96): "Comenta a palavra Nobel."
- Não mapeado (praq0986 05:20.26–05:20.68): "sobre"
- Não mapeado (praq0986 05:22.40–05:23.71): "o Geoffrey Hinton."
- Não mapeado (praq0986 05:27.72–05:29.06): "Calma, calma, calma"
- Não mapeado (praq0986 05:56.08–05:57.19): "Geoffrey Hinton."
- Não mapeado (praq0986 06:03.72–06:05.24): "E também não esquece"
- Não mapeado (praq0986 06:37.80–06:38.65): "que é impossível."
- Não mapeado (praq0986 06:47.78–06:48.28): "Thank you."
- Separador descartado (praq0980 00:01.70): "Repete"
- Separador descartado (praq0980 00:32.16): "repete de novo"
- 5 trecho(s) só de muletas entre takes (descartados)
- Fala da IA — monitor (praq0978 00:28.98): "Com certeza, vamo continuar. Me avisa se quer retomar da última linha ou de algum ponto específico."
- Fala da IA — monitor (praq0978 00:38.50): "Beleza. Assim que você me der o sinal, eu começo do início exatamente como antes."
- Fala da IA — monitor (praq0978 01:15.76): "Combinado. Vou ignorar a pose da capa e já começo direto do roteiro principal, assim que você disser"
- Fala da IA — monitor (praq0979 00:00.00): "Pois é, começar"
- Fala da IA — monitor (praq0979 00:20.91): "Próxima."
- Fala da IA — monitor (praq0979 00:39.80): "De novo."
- Fala da IA — monitor (praq0979 01:07.25): "Próxima."
- Fala da IA — monitor (praq0979 01:19.18): "De novo. Hinton nasceu em Londres"
- Fala da IA — monitor (praq0980 00:10.32): "anterior você quer repetir e eu repito aquela"
- Fala da IA — monitor (praq0980 00:20.43): "De novo."
- Fala da IA — monitor (praq0980 00:36.56): "De novo."
- Fala da IA — monitor (praq0980 00:52.66): "Próxima."
- Fala da IA — monitor (praq0980 01:03.88): "Próxima."
- Fala da IA — monitor (praq0981 00:03.92): "Próxima."
- Fala da IA — monitor (praq0981 00:24.62): "De novo."
- Fala da IA — monitor (praq0981 00:43.36): "De novo. Mas-"
- Fala da IA — monitor (praq0981 00:54.10): "Combinado. Eu só vou seguir pra próxima linha quando você me disser. Vamo continuar no seu ritmo"
- Fala da IA — monitor (praq0981 01:16.40): "De novo."
- Fala da IA — monitor (praq0982 00:00.00): "Ou estudando computadores"
- Fala da IA — monitor (praq0982 00:24.74): "Próxima."
- Fala da IA — monitor (praq0982 00:36.98): "Próxima."
- Fala da IA — monitor (praq0982 01:01.72): "Próxima."
- Fala da IA — monitor (praq0983 00:02.29): "De novo."
- Fala da IA — monitor (praq0983 00:22.66): "Próxima."
- Fala da IA — monitor (praq0983 00:39.14): "De novo."
- Fala da IA — monitor (praq0983 00:53.24): "Próxima."
- Fala da IA — monitor (praq0983 01:17.52): "De novo. Até o próprio orientador dele aconselhou"
- Fala da IA — monitor (praq0984 00:00.00): "Ele houve que abandonasse essa pesquisa, porque poderia destruir sua carreira"
- Fala da IA — monitor (praq0984 00:18.38): "Próxima."
- Fala da IA — monitor (praq0984 00:32.97): "Próxima."
- Fala da IA — monitor (praq0984 00:53.56): "De novo."
- Fala da IA — monitor (praq0984 01:17.84): "Próxima."
- Fala da IA — monitor (praq0985 00:00.00): "a inteligência artificial"
- Fala da IA — monitor (praq0985 00:17.36): "De novo,"
- Fala da IA — monitor (praq0986 00:01.04): "Próxima."
- Fala da IA — monitor (praq0986 00:17.14): "Próxima."
- Fala da IA — monitor (praq0986 00:35.01): "Próxima."
- Fala da IA — monitor (praq0986 00:45.74): "Próxima."
- Fala da IA — monitor (praq0986 00:58.09): "Próxima."
- Fala da IA — monitor (praq0986 01:16.33): "Próxima."
- Fala da IA — monitor (praq0986 01:21.48): "2 am."
- Fala da IA — monitor (praq0986 01:33.90): "De novo."
- Fala da IA — monitor (praq0986 01:39.00): "2 am."
- Fala da IA — monitor (praq0986 01:52.25): "Próxima."
- Fala da IA — monitor (praq0986 02:33.37): "De novo."
- Fala da IA — monitor (praq0986 02:56.80): "Próxima."
- Fala da IA — monitor (praq0986 03:16.40): "De novo."
- Fala da IA — monitor (praq0986 03:35.16): "Próxima."
- Fala da IA — monitor (praq0986 03:51.50): "Próxima."
- Fala da IA — monitor (praq0986 04:10.42): "Próxima."
- Fala da IA — monitor (praq0986 04:24.62): "Próxima."
- Fala da IA — monitor (praq0986 04:35.48): "Próxima."
- Fala da IA — monitor (praq0986 04:50.76): "Próxima."
- Fala da IA — monitor (praq0986 05:06.14): "Próxima."
- Fala da IA — monitor (praq0986 05:26.20): "Próxima. E manda-"
- Fala da IA — monitor (praq0986 05:31.00): "Sem pressa. Você que manda. Quando tiver pronto, seguimos no ritmo que você quiser."
- Fala da IA — monitor (praq0986 05:59.04): "Próxima."
- Fala da IA — monitor (praq0986 06:11.14): "Agora vamos para os hooks alternativas. Primeiro,"
- Fala da IA — monitor (praq0986 06:25.71): "Próxima."
- Fala da IA — monitor (praq0986 06:42.28): "Fim do roteiro. Mandou muito bem. Se precisar de algo mais, é só falar."
- Fala da IA — monitor (praq0986 06:50.24): "Imagina."
- 46 leitura(s) das linhas pela IA (nunca entram no corte; ver `leituras_ia` no alinhamento.json)

## Hooks alternativos (variantes, fora da montagem principal)

- L01B (alt. de L01): L01B-T1 · praq0986 06:19.60 → 06:24.00 [ok]
- L01C (alt. de L01): L01C-T1 · praq0986 06:33.00 → 06:37.76 [ok]

## Cenas extras

9 ok · **3 faltando** — o vídeo sai com placeholder e o QA reprova até chegar

| ID | Tipo | Arquivo | Linhas | Modo | Saída | Status |
|---|---|---|---|---|---|---|
| E02 | video | edicao/extras/E02.mp4 (00:00.00–00:09.92) | L03, L04 | split | 00:12.48–00:22.40 | OK · crédito: 60 Minutes / CBS News |
| E03 | video | edicao/extras/E03.mp4 (00:00.00–00:05.52) | L07 | split | 00:33.16–00:38.68 | OK · crédito: 60 Minutes / CBS News |
| E04 | animacao | — | L08, L09 | split | 00:38.68–00:48.92 | **FALTANDO** · sem componente no registry do Remotion ('2026-10-20-geoffrey-hinton/E04' ou 'E04') |
| E05 | video | edicao/extras/E05.mp4 (00:00.00–00:07.52) | L10 | split | 00:48.92–00:56.44 | OK · extra (7.52s) mais curto que a fala: sai 2.60s antes, em vez de segurar o último quadro; crédito: 60 Minutes / CBS News |
| E12 | video | edicao/extras/E12.mp4 (00:00.00–00:03.12) | L11 | split | 00:59.04–01:02.16 | OK · extra (3.12s) mais curto que a fala: sai 1.44s antes, em vez de segurar o último quadro; crédito: 60 Minutes / CBS News |
| E06 | animacao | — | L12, L13 | split | 01:03.60–01:14.28 | **FALTANDO** · sem componente no registry do Remotion ('2026-10-20-geoffrey-hinton/E06' ou 'E06'); crédito: ImageNet / Stanford Vision Lab (dado) |
| E07 | video | edicao/extras/E07.mp4 (00:00.00–00:05.20) | L15 | split | 01:20.64–01:25.84 | OK · extra (5.20s) mais curto que a fala: sai 1.84s antes, em vez de segurar o último quadro; crédito: 60 Minutes / CBS News |
| E08 | video | edicao/extras/E08.mp4 (00:00.00–00:09.20) | L18, L19 | split | 01:37.96–01:47.16 | OK · crédito: BBC News |
| E01 | animacao | — | L20 | split | 01:47.16–01:53.92 | **FALTANDO** · sem componente no registry do Remotion ('2026-10-20-geoffrey-hinton/E01' ou 'E01') |
| E09 | video | edicao/extras/E09.mp4 (00:00.00–00:07.60) | L21, L22 | split | 01:53.92–02:01.52 | OK · crédito: NobelPrize.org |
| E10 | video | edicao/extras/E10.mp4 (00:00.00–00:07.52) | L23, L24 | split | 02:01.52–02:09.04 | OK · extra (7.52s) mais curto que a fala: sai 4.24s antes, em vez de segurar o último quadro; crédito: NobelPrize.org |
| E11 | video | edicao/extras/E11.mp4 (00:00.00–00:05.84) | L25 | split | 02:13.28–02:19.12 | OK · crédito: NobelPrize.org |

## Enquadramento (zoom por peça — aplicado UMA vez, no corte)

> Cada corte troca o enquadramento (1.00 ↔ 1.12, origem no rosto) para disfarçar o jump cut. Para mudar: `zoom_pecas` (uma escala por peça) e/ou `zoom_origem` ("x% y%") no segmento + `edl.py --recalcular`; `"zoom": {"tipo": "punch", "escala": 1.2}` muda a escala do punch e faz o segmento começar fechado.

- **L01** · origem 49.0% 30.0% (rosto 3/4) · 1.00 → 1.12
- **L02** · origem 41.8% 31.8% (rosto 3/3) · 1.00
- **L03** · origem 52.2% 31.0% (rosto 2/3) · 1.06
- **L04** · origem 50% 32% (rosto 2/3) · 1.12
- **L04** · origem 50% 32% (rosto 2/3) · 1.12
- **L05** · origem 49.7% 31.7% (rosto 3/4) · 1.00 → 1.12
- **L06** · origem 49.7% 31.5% (rosto 2/3) · 1.00
- **L07** · origem 56.5% 32.1% (rosto 2/3) · 1.12 → 1.00 → 1.12
- **L08** · origem 56.7% 34.5% (rosto 2/3) · 1.00
- **L09** · origem 30.0% 34.0% (rosto 2/4) · 1.12 → 1.00
- **L10** · origem 41.7% 31.1% (rosto 2/4) · 1.12 → 1.00 → 1.12 → 1.00
- **L11** · origem 47.6% 32.3% (rosto 3/4) · 1.12 → 1.00
- **L12** · origem 36.4% 35.5% (rosto 3/3) · 1.12
- **L13** · origem 48.8% 33.2% (rosto 4/4) · 1.00 → 1.12
- **L14** · origem 36.7% 29.4% (rosto 3/4) · 1.00 → 1.12
- **L15** · origem 37.8% 33.2% (rosto 2/3) · 1.00
- **L16** · origem 50% 38% (padrão (rosto 1/3)) · 1.12
- **L17** · origem 62.8% 35.3% (rosto 3/3) · 1.00
- **L18** · origem 50% 38% (padrão (rosto 1/4)) · 1.12 → 1.00
- **L19** · origem 36.9% 31.9% (rosto 2/3) · 1.12
- **L20** · origem 39.8% 32.9% (rosto 2/3) · 1.00 → 1.12 → 1.00
- **L21** · origem 56.2% 33.8% (rosto 3/4) · 1.12 → 1.00
- **L22** · origem 48.3% 32.5% (rosto 4/4) · 1.12 → 1.00
- **L23** · origem 57.8% 32.6% (rosto 4/4) · 1.12 → 1.00
- **L24** · origem 52.4% 33.8% (rosto 4/4) · 1.12 → 1.00
- **L25** · origem 51.8% 32.8% (rosto 2/3) · 1.12
- **L26** · origem 50.8% 34.1% (rosto 3/3) · 1.00
- **L27** · origem 45.5% 34.4% (rosto 4/4) · 1.12 → 1.00
- **L28** · origem 40.0% 34.4% (rosto 3/4) · 1.12 → 1.00
- **L29** · origem 53.8% 34.1% (rosto 3/3) · 1.12

48 corte(s) com troca de enquadramento · **sem troca: L04**
