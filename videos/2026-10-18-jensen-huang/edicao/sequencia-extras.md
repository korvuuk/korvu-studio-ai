# Jensen Huang — sequência de extras · PROPOSTA v1 (17/10, antes da gravação de 18/10)

Padrão aprovado na Fei-Fei v3.2 ("podemos basear nessa versão do layout", `docs/decisoes.md` §4, 17/10) e modelo
`videos/2026-10-20-fei-fei-li/edicao/sequencia-extras.md` (seção "Montagem v3"):

- **Os 4 layouts variam conforme a imagem:** `full` (pessoa/retrato em tela cheia, recorte 9:16 + Ken Burns) ·
  `pilha` (3 faixas topo/meio/base, para imagem deitada ou grupo) · `solo` (imagem de leitura inteira sobre preto,
  legenda embaixo: placa, foto rotulada, tela do ChatGPT) · `split` (cena em cima, o Carlos embaixo: ele falando).
- **Sincronia fala ↔ imagem:** a imagem entra NA palavra (o corte cai no silêncio logo antes dela): "lavar prato",
  "lanchonete", "5 trilhões", "mesa de lanchonete", "Taiwan", "internato", "banheiros", "Denny's", "1993", "dois
  amigos", "inteligência artificial", "ChatGPT", "motor", "Rei Charles", "Hinton".
- **Faixa contínua, sem "entra e sai":** corte seco entre imagens, ordem cronológica, nunca a mesma imagem duas vezes
  (nenhuma mídia se repete no vídeo). Crédito curto no RODAPÉ; o completo vai na descrição do post.
- **Áudio dos extras: mudo.** Logos de canal (60 Minutes, CNBC), legenda chinesa queimada e faixas de TV ficam fora do
  recorte por `enquadrar.area`. Todo o material está em `material/` (nada falta em `brutos/extras/`; o roteiro não tem
  cenas `Exx`).

## Carlos em tela cheia

| Versão | Trechos (estimativa) |
|---|---|
| **B** (conteúdo primeiro) | L03 + L04 "E olha só que interessante:" (9,4–17,2 s) · L10 (45,9–49,4) · L15 (69,2–72,7) · L17–L19 (77,9–fim) |
| **A** (Carlos desde 0) | L01 → L04 "E olha só que interessante:" (0–17,2 s) · L10 · L15 · L17–L19 |

- **Par A/B** (`docs/decisoes.md` §5b): B = B1–B4 cobrem o gancho inteiro (L01–L02) e o Carlos entra na L03, por volta
  de **9,4 s**; A = os mesmos overlays sem B1–B4. Fala, legendas, música e CTA idênticos. O `montar_v1.py` imprime o
  segundo exato da entrada na B: anotar em `_controle/testes-abertura.md` depois do render.
- **L17 também é CTA** (`secao: cta` no `roteiro.json`): fica com o Carlos, pela regra rígida 6. O script recusa extra
  em linha de CTA. O cartão grande do PRATO cai na L18.
- **L05 "comenta PRATO"** (seção `virada`) leva o `split`: o Jensen fala em cima e o Carlos pede a palavra embaixo.

## Tempos

**ESTIMADOS** do `roteiro.json`: `tempo_estimado` de cada linha (total ~92,8 s); dentro da linha, as palavras vão a
2,1/s (um ano, "1993", pesa 4 palavras faladas). Depois do /editar, o `montar_v1.py` passa a ler a EDL: início e fim
de linha pelos segmentos, e o corte no meio da linha pelo silêncio antes da palavra (`palavras_saida`). Quando um clipe
é mais curto que o trecho real, o script resolve sozinho e avisa: até 15 % mais curto vira câmera lenta leve; em
plano quase parado (placa, foto rotulada, tela do ChatGPT, caneca), até 40 %. Mais curto que isso vira **quadro parado**
com Ken Burns. O último quadro nunca fica congelado.

Pastas: Y = `material/youtube/cortes/` (still em `cortes/stills/`) · CAPA/F/N = `material/fotos/`.

## A sequência

| # | ~Tempo (s) | Linha (fala) | Layout | Mídia | Enquadrar | Crédito |
|---|---|---|---|---|---|---|
| — | 0,0–9,4 | **A:** L01–L02 | **Carlos** | — | — | — |
| B1 | 0,0–1,9 | **B:** L01 "Imagina você lavar prato" | full | **Y051**: ele de avental vermelho do Denny's (GTC 2025) | x 0,50 (rosto no quadro 0) | AP 360 Productions |
| B2 | 1,9–3,5 | **B:** L01–L02 "numa lanchonete… e," | full | **Y036**: o Denny's de San Jose à noite | x 0,53 (letreiro) | 60 Minutes / CBS News |
| B3 | 3,5–6,4 | **B:** L02 "anos depois, criar a primeira empresa" | full | **Y077**: ele entra no palco do GTC e acena | x 0,50 | 60 Minutes / CBS News |
| B4 | 6,4–9,4 | **B:** L02 "de 5 trilhões de dólares." | full | **Y101** a partir de 1,2 s: o telão da Bloomberg sobe de $5.09T para **$5.10T** | x 0,50, altura inteira, sem Ken Burns: o número fica em y≈800–1070, acima da legenda | Bloomberg Television |
| — | 9,4–17,2 | L03 "Pois é. Essa é a história do Jensen Huang, da Nvidia." + L04 "E olha só que interessante:" | **Carlos** (na B ele entra aqui) | — | — | — |
| V01 | 17,2–20,6 | L04 "ela nasceu numa mesa de lanchonete." | solo | **Y041**: a placa "The booth that launched a $2 trillion company" | área só na placa (x 380–1560): grande e legível | 60 Minutes / CBS News |
| V02 | 20,6–24,2 | L05 "Se quiser ver ele contando, comenta PRATO." | **split** | **Y113**: ele abre o discurso na Carnegie Mellon (o discurso que o PDF entrega) | — (16:9 inteiro em cima) | Carnegie Mellon University |
| V03 | 24,2–26,0 | L06 "Ele nasceu em Taiwan" | full | **F01**: Taipei nos anos 60, P&B, vertical | centro, pan leve | Wikimedia Commons (domínio público) |
| V04 | 26,0–30,6 | L06 "e, ainda criança, foi parar num internato no Kentucky." | pilha | **Y011** o campus de Oneida do alto / **Y013** ele numa cerimônia em Oneida / **Y014** ele contando da escola (2020) | Y013 x 0,42 · Y014 sem a legenda chinesa (área 852×360) | Hoover Institution / NVIDIA · Oneida Baptist Institute |
| V05 | 30,6–33,9 | L07 "A família achava que era escola boa…" | solo | **F03**: a placa do Oneida Baptist Institute | inteira | Wikimedia Commons (domínio público) |
| V06 | 33,9–36,5 | L07 "mas ele limpava os banheiros." | full | **Y016**: ele em Stanford ("limpei mais banheiros do que todos vocês juntos") | x 0,42 | Stanford GSB |
| V07 | 36,5–40,0 | L08 "Depois, ele foi lavar prato num Denny's." | pilha | **Y044** o letreiro do Denny's / **Y043** ele no booth ("a normal dishwasher busboy…") / **Y039** a caneca do Denny's | sem o logo "60" (área y 90–1080) | Hoover Institution / NVIDIA · 60 Minutes / CBS News |
| V08 | 40,0–41,9 | L09 "Em 1993," | full | **Y029**: ele jovem, anos 90 (até 4,0 s, antes da transição do clipe) | x 0,48 | Explorist |
| V09 | 41,9–43,0 | L09 "num outro Denny's," | full | **Y037**: ele entra no Denny's de San Jose | pan x 0,74 → 0,57 (acompanha ele) | 60 Minutes / CBS News |
| V10 | 43,0–45,9 | L09 "ele e dois amigos planejaram a Nvidia." | solo | **Y023**: a foto dos 3 fundadores; os nomes aparecem um a um | inteira | Explorist |
| — | 45,9–49,4 | L10 "Só que a empresa quase quebrou." | **Carlos** | — | — | — |
| V11 | 49,4–52,4 | L11 "Anos depois, chegou a inteligência artificial." | pilha | **Y095** cartão "AlexNet, Winner of ImageNet 2012" / **F14** o PC com 2 GPUs Nvidia da AlexNet (o mesmo do Hinton e da Fei-Fei) / **Y084** data center | Y095 zoom 1,5 no cartão, sem o logo CNBC | CNBC · University of Toronto / CHM · 60 Minutes / CBS News |
| V12 | 52,4–55,3 | L12 "Se o ChatGPT é o carro," | solo | **Y093**: a tela do ChatGPT | sem o logo CNBC (área x 100–1720) | CNBC |
| V13 | 55,3–57,9 | L12 "a Nvidia faz o motor." | full | **Y079** a partir de 1,6 s: ele mostra os dois chips | x 0,50 | 60 Minutes / CBS News |
| V14 | 57,9–63,3 | L13 "Aqui em Londres, ele recebeu do Rei Charles o mesmo prêmio" | full | **Y105**: o Rei Charles entrega a medalha a ele (St James's Palace, nov/2025) | x 0,52 (os dois no quadro) | The Royal Family Channel |
| V15 | 63,3–69,2 | L14 "do Hinton e da Fei-Fei Li, de quem eu já falei aqui." | pilha | **Y104** o Rei entrega a medalha ao Hinton / **Y106** ele e a Fei-Fei com o Rei / **N18** os sete laureados | Y104 zoom 1,3 | The Royal Family Channel · Stanford HAI |
| — | 69,2–72,7 | L15 "A história dele mostra uma coisa:" | **Carlos** | — | — | — |
| V16 | 72,7–77,9 | L16 "o seu Denny's pode ser onde você está agora." | full | **Y048** a partir de 3,0 s: o Denny's de San Jose ao pôr do sol (o letreiro passa em "Denny's", depois o prédio) | x 0,68 | Seb Frey (YouTube) |
| — | 77,9–92,8 | L17–L19 (CTA) "Salva pra rever… Comenta a palavra PRATO… E manda pra quem tá recomeçando…" | **Carlos** + cartão PRATO | — | — | — |

Na estimativa de hoje, o script já usa quadro parado em V04 (Y011 e Y013) e V07 (Y044 e Y039), e câmera lenta leve em
V01, V12, V13 e V16. Com os tempos reais, isso muda sozinho.

Folha de contato: `qa/sequencia-extras-contato.jpg`. Cada quadro é uma maquete 9:16 de cada cena, no meio do trecho,
com a mesma geometria do `Reel.tsx` (recorte, faixas da pilha, caixa do solo, split com o Carlos embaixo e crédito no
rodapé). Os quadros com rótulo amarelo são só da B; os quadros "CARLOS" marcam onde ele volta.

## O que o Carlos decide

1. **L04: placa no meio da frase (proposta) ou Carlos na linha inteira.** O roteiro marca como ênfase só
   "E olha só que interessante:". Por isso a placa do booth (V01) entra em "ela nasceu numa mesa de lanchonete"
   (sincronia), como na Fei-Fei ("Mas olha que interessante:" com o Carlos e a imagem na frase seguinte). Se ele
   preferir a L04 inteira com ele: `L04_PLACA = False` no script. Assim a A fica com ~20,6 s de Carlos seguidos, e a B
   com ~11 s.
2. **Quadro 0 da B:** **Y051**, ele de avental do Denny's comendo (proposta: pessoa reconhecível + "lavar prato"), ou
   **Y037**, ele entrando no Denny's (hoje em V09), ou **Y036**, a fachada à noite.
3. **"5 trilhões" (B4) em tela cheia ou em solo.** Em tela cheia o número fica enorme, mas sobra no pé um pedaço da
   faixa vermelha da Bloomberg ("…ECOMES FIRST STOCK IN / …TO TOP $5 TRILLION IN VAL…"), quase toda sob a UI do
   Instagram. Em solo, a tela da Bloomberg aparece inteira e legível, menor, sobre preto. Proposta: tela cheia.
4. **L14 "de quem eu já falei aqui":** se quiser as **capas dos Reels do Hinton e da Fei-Fei** nessa meia frase (pilha
   de 2, chama para o perfil): `L14_CAPAS = True`. Hoje a pilha dos laureados cobre a linha inteira.
5. **Elon Musk (Y097/Y098) não entra.** A L12 usa a tela do ChatGPT (Y093) e ele com os chips (Y079). Só volta se o
   Carlos pedir.
6. **A versão A fica ~17 s com o Carlos na abertura** (L01–L04a), por desenho do teste: L03 e L04a são iguais nas duas
   versões.
7. Nota, sem mudar a sequência: nos vídeos ele diz que Oneida era o internato que os pais **conseguiam pagar**
   (`catalogo-insert.md`, "Fatos ditos nos vídeos", item 6). A L07 ("achava que era escola boa") vem da Wikipedia e da
   Bloomberg. O Y014 (ele contando da escola) entra mudo e sem a legenda chinesa.

## Reservas (trocar no olho, sem repetir imagem seguida)

- **Abertura/Denny's:** Y037 (se for para o quadro 0, a L09 usa F09 ou Y049), Y040 (booth vazio), Y042 (ele no booth,
  "none of us knew how to do anything"), Y049 (o booth, vlog), F09 (o Denny's de San Jose de dia, Commons), N06 (ele
  com a CEO do Denny's e a caneca, 2023), N07 (a placa de US$ 1 tri, vertical, 2023: valor antigo), Y050 (a van do
  Denny's, GTC 2025: legenda queimada, só em faixa de pilha).
- **Ele contando (split):** Y017 (CMU: "aos 9 anos… Oneida, Kentucky"), Y114 (CMU: "meu irmão me arrumou um emprego
  de lavador de pratos no Denny's"), Y045/Y046/Y047 (Stanford GSB: "provavelmente o melhor lavador de pratos").
- **Taiwan/Kentucky:** Y004, Y005, Y007 (ele nos mercados noturnos de Taipei, faixa da Formosa: só em pilha),
  Y010 (a placa "Oneida" na estrada), Y012 (o campus), F02 (ele com os pais, 468 px).
- **1993/fundação:** Y024 e F07 (ele jovem no escritório, 1994), Y032, Y033 (ele sob o letreiro nVIDIA), Y027 (1993,
  Fremont), Y028 (o nome Nvidia).
- **Quase quebrou** (se a L10 ganhar imagem): Y064 (cartão "We're only 30 days away from going outta' business", a
  partir de 2,8 s), Y055 (250 mil placas enviadas, 249 mil devolvidas), Y053/Y054 (a placa NV1), Y063 (os US$ 5 mi da
  Sega), Y066–Y068 (ele agradece à Sega, Tóquio 2026).
- **IA/motor:** Y091 (CUDA, depois do clarão inicial), Y092 (serial × paralelo), Y094 (slide "From graphics to AI and
  ChatGPT"), Y080 (chip Blackwell), Y081 (racks Nvidia), Y085 (ele com a RTX 4090), F17 (ele com a GPU no palco), N02
  (idem, 1280 px), N24 (H100).
- **Londres/prêmio:** Y102 (anúncio com os 7 nomes), Y103 (animação "Hardware: Jensen Huang e Bill Dally"), Y107 (painel
  do FT em Londres), N16 e N17 (fotos do Rei com ele e com os laureados).
- **Retratos calmos:** Y117–Y126. CAPA-01 a 08 ficam para a capa (designer).
- **Evitar:** Y097/Y098 (Musk), Y090 (CBS Sunday Morning, política), Y008 e Formosa em tela cheia (faixa larga), Y015
  (banheiros, com legenda chinesa no meio da imagem).

## Como montar depois da gravação

```
# 1. /editar → edicao/edl.json aprovada (o script avisa se ainda não estiver)
uv run python videos/2026-10-18-jensen-huang/edicao/extras-v2/montar_v1.py --seco --contato   # confere com tempos reais
uv run python videos/2026-10-18-jensen-huang/edicao/extras-v2/montar_v1.py                    # mídia + overlays
# 2. props das duas versões (B = overlays-v1.json, A = overlays-v1-A.json)
uv run python .claude/skills/legendas-animadas/scripts/gerar_props.py videos/2026-10-18-jensen-huang --sem-titulo --overlays edicao/extras-v2/overlays-v1.json
```

O script copia ou gera a mídia em `edicao/extras-v2/` (vídeo `Vnn-Yxxx.mp4` mudo, still `Vnn-Yxxx.png`, câmera lenta
`…-lento.mp4`, fotos) e grava `overlays-v1.json` (B) e `overlays-v1-A.json` (A). Antes de gravar, ele recusa overlays sobrepostos, imagem
repetida em seguida e extra no CTA, e avisa trecho com menos de 0,8 s.
