# Análise de fala — 2026-09-17-demis-hassabis (roteiro v6)

Palavras do Carlos na transcrição: 470 de 1133 (IA: 658, incertas: 5)


## 1. Linha a linha — roteiro × takes do Carlos


### L01 [ok] escolhido: L01-T3 — último take limpo (sim 0.82); muleta cortada internamente, pausa interna encurtada
ROTEIRO: Aprendeu xadrez aos quatro anos. E ganhou um Nobel com IA.
    L01-T1 sim=0.18 cob=0.18 flags=['false_start'] dur=0.7s n=2 wps=2.78 artic=2.78 pausas>0.35s=[]
      DITO: Aprendeu xadrez
    L01-T2 sim=0.55 cob=0.55 flags=['false_start'] dur=2.4s n=6 wps=2.49 artic=2.49 pausas>0.35s=[]
      DITO: Aprendeu xadrez aos 4 anos e...
  ★ L01-T3 sim=0.82 cob=0.91 flags=['muleta', 'pausa_interna'] dur=4.4s n=11 wps=2.49 artic=3.04 pausas>0.35s=[0.8]
      DITO: Aprendeu xadrez aos 4 anos? ganhou um Nobel com E .A.
      DIFF: replace: «quatro» → «4» | delete: «e» → «» | replace: «ia» → «e a»

### L02 [parafrase] escolhido: L02-T1 — paráfrase: melhor sim 0.67 (score 0.75)
ROTEIRO: Demis Hassabis, nascido aqui em Londres.
  ★ L02-T1 sim=0.67 cob=0.67 flags=[] dur=3.8s n=6 wps=1.59 artic=1.76 pausas>0.35s=[0.38]
      DITO: Denis Assabi, nascido aqui em Londres.
      DIFF: replace: «demis hassabis» → «denis assabi»

### L03 [parafrase] escolhido: L03-T2 — paráfrase: melhor sim 0.71 (score 0.82)
ROTEIRO: Aos treze já era mestre de xadrez. Aos dezessete, criava videogame.
    L03-T1 sim=0.58 cob=0.73 flags=['muleta', 'pausa_interna', 'final_cortado', 'sem_ancora'] dur=6.4s n=12 wps=1.88 artic=2.47 pausas>0.35s=[1.53]
      DITO: Aos 13 anos já era mestre de chaves. E aos 17 anos...
  ★ L03-T2 sim=0.71 cob=0.91 flags=['muleta', 'sem_ancora'] dur=6.6s n=14 wps=2.13 artic=2.13 pausas>0.35s=[]
      DITO: Aos 17 anos já era mestre de xadrez e aos 17 anos criava videogames.
      DIFF: replace: «treze» → «17 anos» | insert: «» → «e» | replace: «dezessete» → «17 anos» | replace: «videogame» → «videogames»

### L04 [parafrase] escolhido: L04-T2 — paráfrase: melhor sim 0.75 (score 0.83)
ROTEIRO: Estudou computação em Cambridge e depois neurociência.
    L04-T1 sim=0.43 cob=0.43 flags=['final_cortado'] dur=2.4s n=4 wps=1.69 artic=1.69 pausas>0.35s=[]
      DITO: estudou computações em Cambridge.
  ★ L04-T2 sim=0.75 cob=0.86 flags=[] dur=4.0s n=8 wps=2.00 artic=2.00 pausas>0.35s=[]
      DITO: Estudou computações em Cambridge e depois a Neurociência.
      DIFF: replace: «computação» → «computações» | insert: «» → «a»

### L05 [parafrase] escolhido: L05-T2 — paráfrase: melhor sim 0.71 (score 0.79)
ROTEIRO: Em dois mil e dez juntou tudo numa empresa aqui em Londres: a DeepMind.
    L05-T1 sim=0.64 cob=0.64 flags=['final_cortado'] dur=2.9s n=7 wps=2.38 artic=2.73 pausas>0.35s=[0.38]
      DITO: Em 2016, juntou tudo aqui em Londres
  ★ L05-T2 sim=0.71 cob=0.71 flags=['final_cortado'] dur=3.2s n=7 wps=2.16 artic=2.67 pausas>0.35s=[0.62]
      DITO: Em 2010, juntou tudo aqui em Londres,
      DIFF: replace: «dois mil e dez» → «2010» | delete: «numa empresa» → «» | delete: «a deepmind» → «»

### L06 [parafrase] escolhido: L06-T2 — paráfrase: melhor sim 0.71 (score 0.82)
ROTEIRO: Quatro anos depois, o Google comprou por cerca de 400 milhões de libras.
    L06-T1 sim=0.64 cob=0.77 flags=[] dur=5.0s n=14 wps=2.81 artic=3.17 pausas>0.35s=[0.56]
      DITO: quatro anos depois, o Google comprou a sua empresa por 4 milhões de libras.
  ★ L06-T2 sim=0.71 cob=0.85 flags=[] dur=6.5s n=14 wps=2.15 artic=2.37 pausas>0.35s=[0.59]
      DITO: quatro anos depois, o Google comprou a empresa dele por 400 milhões de libras.
      DIFF: insert: «» → «a empresa dele» | delete: «cerca de» → «»

### L07 [parafrase] escolhido: L07-T1 — paráfrase: melhor sim 0.67 (score 0.64)
ROTEIRO: Em dezesseis, a IA deles venceu um dos maiores nomes do Go.
  ★ L07-T1 sim=0.67 cob=0.67 flags=['muleta'] dur=4.9s n=10 wps=2.02 artic=2.02 pausas>0.35s=[]
      DITO: 2016 o AI deles venceu um dos maiores nomes do
      DIFF: replace: «em dezesseis a ia» → «2016 o ai» | delete: «go» → «»
    L07-T2 sim=0.42 cob=0.42 flags=['pausa_interna'] dur=6.1s n=9 wps=1.47 artic=1.81 pausas>0.35s=[1.13]
      DITO: 2016, a IA deles venceu o maior nome do

### L08 [parafrase] escolhido: L08-T1 — paráfrase: melhor sim 0.64 (score 0.74)
ROTEIRO: Um jogo com mais posições possíveis do que átomos no universo.
  ★ L08-T1 sim=0.64 cob=0.64 flags=[] dur=4.8s n=9 wps=1.88 artic=1.88 pausas>0.35s=[]
      DITO: Um jogo com mais posições com átomos do universo.
      DIFF: replace: «possíveis» → «com átomos» | delete: «que átomos no» → «»

### L09 [parafrase] escolhido: L09-T6 — paráfrase: melhor sim 0.71 (score 0.80)
ROTEIRO: Mas o maior feito veio depois: o AlphaFold passou a prever o formato das proteínas.
    L09-T1 sim=0.27 cob=0.27 flags=['false_start'] dur=1.2s n=4 wps=3.31 artic=3.31 pausas>0.35s=[]
      DITO: Mas o maior feito...
    L09-T2 sim=0.47 cob=0.47 flags=['final_cortado'] dur=3.8s n=9 wps=2.39 artic=2.81 pausas>0.35s=[0.56]
      DITO: Mas o maior feito veio depois. O alfa -fold.
    L09-T3 sim=0.47 cob=0.47 flags=['final_cortado'] dur=3.6s n=9 wps=2.51 artic=2.88 pausas>0.35s=[0.46]
      DITO: Mas o maior feito veio depois. O alfa -folha
    L09-T4 sim=0.40 cob=0.40 flags=['false_start'] dur=1.7s n=6 wps=3.60 artic=3.60 pausas>0.35s=[]
      DITO: mas o maior feito veio depois.
    L09-T5 sim=0.62 cob=0.67 flags=[] dur=9.1s n=16 wps=1.77 artic=1.85 pausas>0.35s=[0.42]
      DITO: Mas o maior feito veio depois. O alfa -foli passou a prever a quebra da proteína.
  ★ L09-T6 sim=0.71 cob=0.80 flags=['pausa_interna'] dur=8.1s n=17 wps=2.10 artic=2.31 pausas>0.35s=[0.76]
      DITO: Mas o maior feito veio depois, onde o alfa -fold passou a prever o formato da proteína.
      DIFF: insert: «» → «onde» | replace: «alphafold» → «alfa fold» | replace: «das proteínas» → «da proteína»

### L10 [ok] escolhido: L10-T2 — último take limpo (sim 0.89)
ROTEIRO: Um problema que travava a ciência havia cinquenta anos.
    L10-T1 sim=0.60 cob=0.67 flags=['locutor_incerto'] dur=4.7s n=9 wps=1.92 artic=1.95 pausas>0.35s=[]
      DITO: O problema que via travado a ciência havia 50 anos.
  ★ L10-T2 sim=0.89 cob=0.89 flags=[] dur=5.1s n=9 wps=1.77 artic=1.77 pausas>0.35s=[]
      DITO: Um problema que travava a ciência havia 50 anos.
      DIFF: replace: «cinquenta» → «50»

### L11 [faltando] escolhido: None — a IA leu a linha (2×), mas não há take do Carlos
ROTEIRO: E isso deu a ele o Nobel de Química, junto com o John Jumper.
  (sem take do Carlos)

### L12 [ok] escolhido: L12-T2 — último take limpo (sim 0.93); pausa interna encurtada
ROTEIRO: Quer dizer: o menino do xadrez virou um dos nomes mais importantes da IA.
    L12-T1 sim=0.50 cob=0.57 flags=[] dur=4.5s n=9 wps=2.02 artic=2.25 pausas>0.35s=[0.46]
      DITO: Quer dizer, o menino do xadrez virou a maior
  ★ L12-T2 sim=0.93 cob=0.93 flags=['pausa_interna'] dur=6.9s n=13 wps=1.87 artic=2.11 pausas>0.35s=[0.8]
      DITO: Quer dizer, o menino do xadrez virou um dos nomes mais importantes da
      DIFF: delete: «ia» → «»

### L13 [parafrase] escolhido: L13-T1 — paráfrase: melhor sim 0.57 (score 0.74)
ROTEIRO: Para mais vídeos como esse, é só me seguir.
  ★ L13-T1 sim=0.57 cob=0.89 flags=['muleta', 'sem_ancora'] dur=4.5s n=14 wps=3.08 artic=3.42 pausas>0.35s=[0.46]
      DITO: Para mais conteúdos como esse, é só me seguir e te vejo na próxima.
      DIFF: replace: «vídeos» → «conteúdos» | insert: «» → «e te vejo na próxima»

### L01B [ok] escolhido: L01B-T1 — último take limpo (sim 0.89)
ROTEIRO: Um jogador de xadrez que acabou ganhando um Nobel.
  ★ L01B-T1 sim=0.89 cob=0.89 flags=[] dur=3.4s n=9 wps=2.64 artic=2.64 pausas>0.35s=[]
      DITO: Um jogador de xadrez que acabou ganhando o Nobel.
      DIFF: replace: «um» → «o»

### L01C [ok] escolhido: L01C-T2 — último take limpo (sim 0.80); pausa interna encurtada
ROTEIRO: A DeepMind nasceu aqui em Londres. E mudou a IA.
    L01C-T1 sim=0.60 cob=0.70 flags=['final_cortado'] dur=3.4s n=8 wps=2.37 artic=2.37 pausas>0.35s=[]
      DITO: DeepMind que nasceu aqui em Londres e mudou
  ★ L01C-T2 sim=0.80 cob=0.80 flags=['pausa_interna'] dur=5.4s n=9 wps=1.68 artic=1.96 pausas>0.35s=[0.77]
      DITO: A DeepMind nasceu aqui em Londres. E mudou a
      DIFF: delete: «ia» → «»

## 2. Ritmo nos takes escolhidos

| linha | take | palavras | dur. take (s) | dur. na EDL (s) | wps EDL | wps articulação |
|---|---|---|---|---|---|---|
| L01 | L01-T3 | 11 | 4.43 | 3.95 | 2.78 | 3.04 |
| L02 | L02-T1 | 6 | 3.78 | 2.95 | 2.03 | 1.76 |
| L03 | L03-T2 | 14 | 6.57 | 4.57 | 3.06 | 2.13 |
| L04 | L04-T2 | 8 | 4.00 | 3.49 | 2.29 | 2.00 |
| L05 | L05-T2 | 7 | 3.24 | 5.4 | 1.3 | 2.67 |
| L06 | L06-T2 | 14 | 6.50 | 5.84 | 2.4 | 2.37 |
| L07 | L07-T1 | 10 | 4.94 | 3.7 | 2.7 | 2.02 |
| L08 | L08-T1 | 9 | 4.79 | 4.15 | 2.17 | 1.88 |
| L09 | L09-T6 | 17 | 8.11 | 6.28 | 2.71 | 2.31 |
| L10 | L10-T2 | 9 | 5.09 | 3.81 | 2.36 | 1.77 |
| L12 | L12-T2 | 13 | 6.95 | 5.41 | 2.4 | 2.11 |
| L13 | L13-T1 | 14 | 4.54 | 3.96 | 3.54 | 3.42 |
| L01B | L01B-T1 | 9 | 3.41 | None |  | 2.64 |
| L01C | L01C-T2 | 9 | 5.36 | None |  | 1.96 |

Total: 150 palavras ditas nos takes escolhidos · 71.7 s de take · 53.5 s na EDL
**wps global na EDL (palavras ditas / tempo no corte): 2.80**
wps global nos takes (com pausas internas): 2.09
wps EDL por linha: mediana 2.40, mín 1.30, máx 3.54
wps articulação por linha: mediana 2.12, mín 1.76, máx 3.42
Duração de saída da EDL: 57.84 s · palavras do roteiro nas legendas: 132 → 2.28 palavras de ROTEIRO por segundo de vídeo

## 3. Trocas sistemáticas (takes escolhidos)

### Substituições (roteiro → dito)
- «quatro» → «4» ×1
- «ia» → «e a» ×1
- «demis hassabis» → «denis assabi» ×1
- «treze» → «17 anos» ×1
- «dezessete» → «17 anos» ×1
- «videogame» → «videogames» ×1
- «computação» → «computações» ×1
- «dois mil e dez» → «2010» ×1
- «em dezesseis a ia» → «2016 o ai» ×1
- «possíveis» → «com átomos» ×1
- «alphafold» → «alfa fold» ×1
- «das proteínas» → «da proteína» ×1
- «cinquenta» → «50» ×1
- «vídeos» → «conteúdos» ×1
- «um» → «o» ×1

### Inserções (dito a mais)
- +«e» ×1
- +«a» ×1
- +«a empresa dele» ×1
- +«onde» ×1
- +«e te vejo na próxima» ×1

### Omissões (do roteiro, não dito)
- −«ia» ×2
- −«e» ×1
- −«numa empresa» ×1
- −«a deepmind» ×1
- −«cerca de» ×1
- −«go» ×1
- −«que átomos no» ×1

### Primeira palavra dita nos takes escolhidos
um ×3, aprendeu ×1, denis ×1, aos ×1, estudou ×1, em ×1, quatro ×1, 2016 ×1, mas ×1, quer ×1, para ×1, a ×1

## 4. Fala do Carlos fora das linhas (não mapeado) — improvisos, conversas com a IA, falsos começos

- [praq0969 34.1–34.8] Tchau, tchau.
- [praq0969 73.2–74.7] Ok, eu estou pronto. Vamos ir.
- [praq0969 105.7–106.9] Pronto, pode começar. começar.
- [praq0969 137.5–138.2] o do início.
- [praq0969 143.8–146.7] Não, antes, antes, antes. Primeiro, primeira linha.
- [praq0969 171.5–172.5] Denis Hassabis.
- [praq0969 181.9–183.1] Denis Hassabi.
- [praq0969 184.2–184.7] Nassib.
- [praq0969 215.0–219.4] não precisa dizer respiração tá bom não precisa dizer a respiração
- [praq0969 237.3–238.7] aos 13 anos.
- [praq0969 239.3–239.5] daí.
- [praq0969 296.8–296.9] E
- [praq0969 327.7–330.1] uma empresa chamada DeepMine.
- [praq0969 346.4–348.5] fundou uma empresa, a DeepMind.
- [praq0969 367.7–367.8] E
- [praq0970 8.7–8.8] E
- [praq0970 32.9–33.9] Em 2016,
- [praq0970 34.9–39.7] a EA e deles venceram o maior jogo da competição do gol.
- [praq0970 50.4–51.2] Em 2016,
- [praq0970 53.1–56.4] a EA e deles venceram o maior nome do gol.
- [praq0970 65.1–66.2] vamos repetir antes
- [praq0970 72.3–75.6] não vamos repetir em
- [praq0970 80.6–80.8] gol
- [praq0971 8.2–8.4] Em
- [praq0971 14.5–14.7] gol.
- [praq0971 26.2–26.6] Continua.
- [praq0971 63.2–63.5] Alpha
- [praq0972 0.0–1.0] O maior feito veio depois.
- [praq0972 8.2–10.5] Calma, eu acho que você não está me escutando, você
- [praq0972 10.6–20.1] passando direto, mesmo que eu arrasse, você está passando direto. Vamos repetir, E... mas o maior feito do AlphaFold. isso? Ahn.
- [praq0972 69.5–69.5] previa...
- [praq0972 79.4–82.1] Você tem que me escutar. Quando eu começo a falar...
- [praq0973 0.0–4.0] De uma linha, você vai ter que entender que aquela linha eu quero repetir. Então,
- [praq0973 4.5–6.0] naquela mesma linha que eu estou falando.
- [praq0973 36.1–37.6] mais um maior
- [praq0974 0.4–2.4] Ok, vamos começar no linha A,
- [praq0975 3.2–5.3] Um problema que traba...
- [praq0975 40.7–42.3] história do AI.
- [praq0975 60.7–61.2] AI.
- [praq0975 67.8–70.6] Me segue que eu trago mais histórias assim.
- [praq0976 34.8–34.9] A
- [praq0976 38.3–39.5] a DeepMind.
- [praq0976 58.2–60.0] história da AI.

### Separadores ditos pelo Carlos
- [praq0969 136.0] Repete, repete. Repete
- [praq0969 236.8] Repete
- [praq0969 238.9] Repete
- [praq0971 67.0] De novo.
- [praq0973 4.2] repete

## 5. Toda a fala do Carlos (takes + fora) — muletas e repetições

Minutos de fala do Carlos (aprox., pausas < 2 s incluídas): 6.2
Muletas (contagem bruta, inclui as que estão no roteiro): então ×1, é ×1, assim ×1, bom ×1, tá ×1

Bigramas/trigramas mais ditos (≥3):
- o maior ×11
- maior feito ×8
- o maior feito ×8
- mas o ×7
- mas o maior ×7
- feito veio ×6
- veio depois ×6
- maior feito veio ×6
- feito veio depois ×6
- aqui em ×5
- em londres ×5
- em 2016 ×5
- depois o ×5
- aqui em londres ×5
- a deepmind ×4
- do gol ×4
- o alfa ×4
- aprendeu xadrez ×3
- aos 17 ×3
- 17 anos ×3
- 2016 a ×3
- vamos repetir ×3
- que eu ×3
- problema que ×3
- aos 17 anos ×3
- em 2016 a ×3
- veio depois o ×3
- depois o alfa ×3

## 6. Fala contínua do Carlos por arquivo (pausas > 0,7 s marcadas com //; > 2 s com ///)


### praq0969
Tchau, tchau. ///[38.4s] Ok, eu estou pronto. Vamos ir. ///[31.0s] Pronto, pode começar. começar. ///[4.2s] Aprendeu xadrez ///[11.7s] Aprendeu xadrez aos 4 anos e... ///[10.2s] Repete, repete. Repete o do início. ///[5.6s] Não, antes, antes, antes. Primeiro, primeira linha. ///[12.0s] Aprendeu xadrez aos 4 anos? // ganhou um Nobel com E .A. ///[8.4s] Denis Hassabis. ///[9.4s] Denis Hassabi. // Nassib. ///[14.1s] Denis Assabi, nascido aqui em Londres. ///[12.4s] não precisa dizer respiração tá bom não precisa dizer a ///[18.1s] Repete aos 13 anos. Repete daí. ///[19.7s] Aos 13 anos já era mestre de chaves. // E aos 17 anos... ///[13.1s] Aos 17 anos já era mestre de xadrez e aos 17 anos criava videogames. ///[11.5s] E estudou computações em Cambridge. ///[10.0s] Estudou computações em Cambridge e depois a Neurociência. ///[11.5s] Em 2016, juntou tudo aqui em Londres uma empresa chamada DeepMine. ///[12.6s] Em 2010, juntou tudo aqui em Londres, fundou uma empresa, a DeepMind. ///[19.2s] E quatro anos depois, o Google comprou a sua empresa por 4 milhões de libras.

### praq0970
E quatro anos depois, o Google comprou a empresa dele por 400 milhões de libras. ///[17.6s] Em 2016, // a EA e deles venceram o maior jogo da competição do gol. ///[10.6s] Em 2016, // a EA e deles venceram o maior nome do gol. ///[8.7s] vamos repetir antes ///[6.1s] não vamos repetir em 2016 o AI deles venceu um dos maiores nomes do gol

### praq0971
Em 2016, // a IA deles venceu o maior nome do gol. ///[11.4s] Continua. ///[26.2s] Um jogo com mais posições com átomos do universo. ///[9.3s] De novo. ///[12.8s] Mas o maior feito...

### praq0972
O maior feito veio depois. ///[7.2s] Calma, eu acho que você não está me escutando, passando direto, mesmo que eu arrasse, você está passando direto. Vamos repetir, E... mas o maior feito do AlphaFold. isso? Ahn. ///[21.1s] Mas o maior feito veio depois. O alfa -fold. ///[20.9s] Mas o maior feito veio depois. O alfa -folha ///[9.9s] Você tem que me escutar. Quando eu começo a falar...

### praq0973
De uma linha, você vai ter que entender que aquela linha eu quero repetir. Então, repete naquela mesma linha que eu estou falando. ///[30.1s] mais um maior

### praq0974
Ok, vamos começar no linha A, // mas o maior feito veio depois. ///[21.4s] Mas o maior feito veio depois. O alfa -foli passou a prever a quebra da proteína. ///[11.6s] Mas o maior feito veio depois, // onde o alfa -fold passou a prever o formato da proteína. ///[8.1s] problema que via travado a ciência havia 50 anos.

### praq0975
Um problema que traba... ///[14.1s] Um problema que travava a ciência havia 50 anos. ///[11.7s] Quer dizer, o menino do xadrez virou a maior história do AI. ///[11.5s] Quer dizer, // o menino do xadrez virou um dos nomes mais importantes da AI. ///[6.6s] Me segue que eu trago mais histórias assim.

### praq0976
Para mais conteúdos como esse, é só me seguir e te vejo na próxima. ///[8.7s] Um jogador de xadrez que acabou ganhando o Nobel. ///[11.0s] A DeepMind que nasceu aqui em Londres e mudou a DeepMind. ///[13.4s] A DeepMind nasceu aqui em Londres. // E mudou a história da AI.
