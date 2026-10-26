# Referências de fora: histórias de pessoas e tutoriais de IA

> Pesquisa de 14/10/2026 para a sacada do Carlos (`docs/decisoes.md` §1 e §5b): pegar o que já funcionou LÁ FORA e trazer para o português.
> Público: quem **fala português e vive na Europa/Reino Unido** e não consegue aprender IA sozinho. **Não** é o público britânico.
> Complementa `externos.md` (mapa geral de criadores de IA, feito por outra sessão). Este arquivo cobre só duas frentes:
> **(A)** histórias/perfis curtos de pessoas da tecnologia e **(B)** tutoriais de IA que viralizam.

## Como os números foram obtidos (e o que NÃO está confirmado)

- **YouTube:** inscritos, views, likes e comentários lidos com `yt-dlp` sem login, em 14/10/2026 (madrugada). O YouTube não mostra salvamentos.
- **TikTok:** views, likes, comentários e **salvamentos** lidos com `yt-dlp` sem login. Os seguidores vêm da página pública do perfil, lida no mesmo dia.
  - A varredura pega só os **últimos ~300 posts** de cada conta. Um viral antigo pode ter ficado de fora.
- **Instagram:** a API pública recusou todas as consultas sem login. Por isso **nenhum número de seguidores do Instagram está confirmado aqui**.
  - Não usei login nem cookies do navegador.
  - O único número de Instagram citado é o da própria bio (@handlytech, "1.5M"), lido por terceiros (Apify, 31/03/2026). Fica marcado **não confirmado**.
- **⚠ Alcance comprado:**
  - Vídeos com milhões de views e quase nenhum comentário são **patrocinados ou impulsionados**, e não servem de modelo orgânico.
  - Exemplos: @rpn (37 milhões de views, 0 comentários), @rowancheung (22,6 milhões, 0 comentários) e o vídeo de agentes do Kallaway (929 mil views, 1 comentário, #CopilotPartner).
  - Também estão marcados como publi o Cleo Abram × Meta (#MetaRayBanPartner) e o Awa K. Penn (#ZapierPartner).
- **Transcrições:**
  - Feitas com mlx-whisper local (large-v3-turbo) a partir de 8 vídeos baixados em `/private/tmp/…/scratchpad/refs/externos-historias/`, que é só cópia de estudo, temporária e fora do projeto.
  - Os quadros dos 3 primeiros segundos foram tirados com ffmpeg.
  - Os "cortes" de cada vídeo foram contados com o `scdet` do ffmpeg (limiar 12). É uma medida aproximada: zoom digital não conta como corte.
- **Os hooks abaixo citam só a abertura** (≤ 15 palavras) para identificar o vídeo. As versões Korvu **não copiam texto**: copiam o esqueleto.

---

## 1. Tabela-resumo

### A — Histórias e perfis (minidocumentário curto)

| # | Canal | Plataforma | Seguidores (fonte, 14/10/26) | Formato | Viral de referência (views) |
|---|---|---|---|---|---|
| A1 | **Kallaway** | YT Shorts / IG / TikTok | YT 40,4 mil inscritos (yt-dlp) · IG e TikTok: não confirmado | Cara + B-roll em janela, "lista de façanhas" de uma pessoa | Nolan/Oppenheimer **8,68 M** · "Animated content just changed forever" 7,5 M |
| A2 | **How Money Works** | YT Shorts | 1,76 M (yt-dlp) | Narração em off sobre clipe de entrevista e arquivo, padrão "How this man…" | David Choe/Facebook **5,49 M** |
| A3 | **Cleo Abram** | TikTok / YT / IG | TikTok 2,5 M · YT 8,86 M | Entrevistadora + explicação rápida + arquivo | Jensen Huang/Nvidia 759 mil (TikTok) |
| A4 | **Starter Story** | YT Shorts / TikTok | YT 887 mil · TikTok 159 mil | Apresentador em fundo verde conta a história de um fundador | "$1M business out of a van" **2,2 M** |
| A5 | **MagnatesMedia** | YT Shorts | 1,86 M | Minidoc com voz grave, arquivo e música tensa | Branson 267 mil · Masa Son 146 mil |
| A6 | **Fireship** | YT Shorts | 4,3 M | História de tecnologia em ritmo de meme, voz rápida | "the untold history of web development" **5,22 M** |
| A7 | **Logically Answered** | YT Shorts | 928 mil | Pergunta-título sobre um CEO ou empresa | "Will Sundar Pichai Get Fired?" 71 mil |
| A8 | **ColdFusion** | YT Shorts | 5,25 M | Minidoc de tecnologia, narração calma | "The Origins of DeepSeek" 48 mil |
| A9 | **Fortune** | TikTok | 422,7 mil | Recorte de entrevista com legenda e contexto | Jensen/Denny's 69 mil · Chesky 1,2 M |
| A10 | **60 Minutes** | TikTok | 3,5 M | Recorte da entrevista de TV | Hassabis "exponential curve" 47,5 mil |
| A11 | **Mo News** | TikTok | não confirmado | Notícia + arquivo de entrevista antiga | Stephen Hawking sobre IA 218 mil (1,5 mil salvamentos) |
| A12 | **Business Insider** | TikTok | 546,1 mil | Explicador com arquivo | "Sam Altman texts" 244 mil |

### B — Tutoriais e aprendizado de IA

| # | Canal | Plataforma | Seguidores (fonte, 14/10/26) | Formato | Viral de referência |
|---|---|---|---|---|---|
| B1 | **Sabrina Ramonov** | TikTok / YT / IG | TikTok 859,9 mil · YT 429 mil | Lista numerada falada para a câmera + palavra-chave | "10 secret codes to learn anything" 593 mil, **54,5 mil salvamentos** |
| B2 | **Jeff Su** | YT Shorts / IG | YT 1,92 M | "Explicado em 3 níveis", estúdio limpo | "AI Agents explained in 3 steps" 855 mil |
| B3 | **Nate Herk** | YT Shorts | 1,07 M | Tela do n8n em cima, rosto embaixo, demo real | "Ultimate team of agents in n8n" **1,41 M** |
| B4 | **Handlytech (Ayham Joukhadar)** | TikTok / IG | TikTok 483,5 mil · IG "1.5M" na bio (**não confirmado**) | Antes/depois visual + prompt + "comenta X" | "Turn ANY photo into 4K" 760 mil · "Comment JOB" 506 mil, **3 mil comentários, 21,3 mil salvamentos** |
| B5 | **Nate B. Jones** | TikTok | 492,1 mil | Dica de prompt de 1 minuto | "It takes 5 seconds" 864 mil, 14 mil salvamentos |
| B6 | **Harper Carroll** | TikTok / IG | TikTok 91,2 mil | Série "10 dias de IA básica" para iniciantes | Day 1 "What is AI" 356 mil, 7,9 mil salvamentos |
| B7 | **Dan Martell** | YT Shorts / IG | YT 3,12 M | Empresário dá ordem direta ("pare de fingir…") | Claude Code para negócio 477 mil |
| B8 | **Tiff in Tech** | TikTok / YT | TikTok 342,1 mil · YT 648 mil | "O que é X e por que as empresas usam" | "What is a Raspberry Pi…" 723 mil (YT) |
| B9 | **Matt Wolfe** | YT Shorts / IG | YT 1,02 M | Novidade de ferramenta comentada | "Nvidia's $20B loophole explained" 157 mil |
| B10 | **The AI Advantage (Igor Pogany)** | YT Shorts | 487 mil | Ferramenta grátis + demo | "This FREE AI tool removes watermarks" 121 mil |

---

## 2. Frente A: histórias e perfis, canal por canal

### A1. Kallaway

**Conta:** @kallaway, YT Shorts. Os números do Instagram e do TikTok não foram confirmados, porque o handle `@kallaway` no TikTok é de outra pessoa.

**Por que performa:**
- Abre com algo que você **já viu** ("sabe aquela cena…").
- Promete que aquilo é só o **4.º item** de uma lista ainda mais louca.
- Encadeia 4–5 provas curtas e fecha com o **porquê**, a revelação guardada para o fim.
- O ritmo é de cerca de 1 corte por segundo.

**Viral 1:** [Nolan/Oppenheimer](https://www.youtube.com/shorts/R1bn__sNAaM)
- 8.676.490 views · 689 mil likes · 2,7 mil comentários · 60 s · 01/08/2023.
- **Hook (0–3 s):** pergunta-reconhecimento ("Você conhece essa cena…?") e, logo depois, o nome da pessoa + a façanha absurda.
- **Blocos:**
  1. Hook com a cena famosa (0–7 s).
  2. Virada: "e isso é só o 4.º da lista" (7–12 s).
  3. Prova 1, com número (12–26 s).
  4. Prova 2 (26–41 s).
  5. Metralhadora de mais 2 provas em uma frase cada (41–47 s).
  6. "O mais assustador é…": o motivo real (47–54 s).
- **CTA:** nenhum. Termina na revelação, o que faz o vídeo recomeçar em loop.
- **Edição** (quadros 0–3 s):
  - Rosto dele na metade de baixo, com o clipe do filme numa janela em cima.
  - Foto da pessoa recortada entra quando o nome é dito.
  - Legenda de 2–3 palavras em amarelo-mostarda serifado no centro.
  - 58 cortes em 60 s.

**Viral 2:** ["Animated content just changed forever"](https://www.youtube.com/shorts/0uZ6GSHKW44)
- 7.499.580 views · 409 mil likes · 8,9 mil comentários · 60 s.
- Mesmo molde, aplicado a uma tecnologia. Não foi baixado.

> **Versão Korvu: "Demis Hassabis, a lista"** · palavra-chave **DOC** → PDF com o link do documentário *The Thinking Game* e de uma entrevista longa
> - **Hook:** "Sabe a IA que ganhou um Nobel? O cara que fez ela… e isso nem é a coisa mais louca que ele já fez."
> - **Bloco 1:** quem ele é, em uma frase (Londres, DeepMind, Google).
> - **Bloco 2:** façanha 1, a do xadrez quando criança.
> - **Bloco 3:** façanha 2, o videogame que ele ajudou a criar ainda adolescente.
> - **Bloco 4:** metralhadora — "a IA que venceu o campeão de Go", "o mapa de 200 milhões de proteínas".
> - **Bloco 5:** "Mas o mais impressionante é o motivo…" e aí a frase dele sobre por que faz isso (tirada da entrevista).
> - **CTA (≤ 12 palavras):** "Comenta DOC que eu te mando o documentário inteiro."
> - Cada fato e número precisa de fonte no dossiê antes de entrar no roteiro (regra 7). O roteirista confere.

### A2. How Money Works

**Conta:** @HowMoneyWorks, YT Shorts, 1,76 M de inscritos.

**Por que performa:**
- Fórmula "**Este é [pessoa], que tomou a decisão mais inteligente da vida em [ano]**".
- A história se resolve num **número enorme e concreto**, sempre na mesma sequência: escolha → anos depois → valor.

**Viral:** [David Choe pinta o escritório do Facebook](https://www.youtube.com/shorts/jJ0i4JxY-tE)
- 5.493.257 views · 315 mil likes · 1,3 mil comentários · 53 s · 2021.
- **Hook (0–3 s):** "This is David Choe…" sobre o rosto dele num podcast, com o NOME em letras brancas gigantes no centro.
- **Blocos:**
  1. Quem é + "a decisão mais inteligente" (0–8 s).
  2. Contexto: startup pequena, precisava de algo (8–16 s).
  3. A escolha: dinheiro OU ações (16–34 s).
  4. O desfecho em número: 60 mil → 200 milhões (34–46 s).
  5. CTA (46–52 s).
- **CTA:** "like + subscribe pra aprender…". É fraco, e a Korvu troca pela palavra-chave.
- **Edição:**
  - Voz em off.
  - Arquivo real (podcast, vídeo dele pintando).
  - Texto grande só nos nomes e números.
  - 22 cortes em 53 s.

> **Versão Korvu: "a decisão de [pessoa] que valeu [número]"** · palavra-chave **VIDEO** → PDF com o link da entrevista em que a pessoa conta
> - **Hook:** "Esse é [pessoa]. Em [ano], ele tomou a decisão mais inteligente da vida dele."
> - **Bloco 1:** quem era antes, ainda pequeno.
> - **Bloco 2:** a encruzilhada (vender ou não, aceitar ou recusar, largar o emprego).
> - **Bloco 3:** o que ele escolheu e por quê, com a frase dele na entrevista.
> - **Bloco 4:** o número de hoje.
> - **Bloco 5:** a lição para quem tem um pequeno negócio.
> - **CTA:** "Comenta VIDEO que eu te mando a entrevista onde ele conta tudo."
> - Candidatos com material: a venda da DeepMind ao Google; Jensen Huang no Denny's (Fortune e Stanford GSB); o dinheiro da Microsoft na OpenAI. **Confirmar cada número com fonte.**

### A3. Cleo Abram

**Conta:** @cleoabram. TikTok 2,5 M · YT 8,86 M.

**Por que performa:**
- Começa com **ela ao lado da pessoa famosa** ("Essa sou eu com…").
- Depois faz uma pergunta que todo mundo tem ("mas por quê, exatamente?") e responde com **uma ideia simples** e imagens de antes/depois.
- É o formato mais próximo do Carlos, porque ele também é o narrador visível.

**Viral:** [Jensen Huang / Nvidia](https://www.tiktok.com/@cleoabram/video/7464683554446953774)
- 758.500 views · 18,3 mil likes · 135 comentários · 1.410 salvamentos · 55 s · 27/01/2025.
- **Hook (0–3 s):** "That's me with Jensen Huang, the CEO of NVIDIA…", com uma seta verde apontando para ele.
- **Blocos:**
  1. Quem é + "uma das empresas mais valiosas do mundo" (0–7 s).
  2. "Mas por quê?" (7–9 s).
  3. Resposta em 1 palavra: a GPU (9–11 s).
  4. Explicação com analogia — os 10% do código que fazem 99% do trabalho, processar tudo ao mesmo tempo (11–29 s).
  5. Antes/depois visual nos games (29–34 s).
  6. A virada: "uma década depois, perfeito para treinar IA" (34–40 s).
  7. O que ele vai construir agora (40–53 s).
  8. CTA (54 s).
- **CTA:** "vai ver o episódio longo" (link na bio).
- **Edição:**
  - Legenda branca pequena embaixo.
  - Setas e destaque verde-limão em print de manchete.
  - Recorte da pessoa sobre fundo de texto.
  - 44 cortes em 55 s.
- **Outro vídeo dela:** [Meta Ray-Ban Display](https://www.tiktok.com/@cleoabram/video/7571461682065673503), 3,9 M de views e 37 mil salvamentos. É **publi** (#MetaRayBanPartner).

> **Versão Korvu: "por que todo mundo fala de [empresa/pessoa]?"** · palavra-chave **NVIDIA** → PDF com o link da entrevista longa (Cleo Abram, *Huge Conversations*) e do painel em Stanford
> - **Hook:** "Esse é o Jensen Huang. A empresa dele virou uma das mais valiosas do mundo. Mas por quê?"
> - **Bloco 1:** a resposta numa palavra: um chip.
> - **Bloco 2:** a explicação em linguagem de dono de negócio (fazer 100 tarefas pequenas ao mesmo tempo em vez de uma de cada vez).
> - **Bloco 3:** antes, servia para videogame.
> - **Bloco 4:** a virada — o mesmo chip era perfeito para treinar IA.
> - **Bloco 5:** o que isso muda no ChatGPT que você usa.
> - **CTA:** "Comenta NVIDIA que eu te mando a entrevista completa dele."
> - Narração do Carlos por cima da entrevista, com crédito na tela (decisão de 14/10).

### A4. Starter Story

**Conta:** @starterstory. YT 887 mil · TikTok 159,1 mil.

**Por que performa:**
- Começa pelo **resultado em dinheiro + um detalhe improvável** ("numa van", "vendendo cascas de ovo").
- Depois conta a história em ordem cronológica, com "**mas tudo mudou no dia em que…**".

**Viral:** ["He Started $1M Business Out Of A Van"](https://www.youtube.com/shorts/wUx3M5eP20k)
- 2.200.475 views · 128,5 mil likes · 372 comentários · 60 s · 2022.
- **Hook (0–3 s):** "This guy built a $1.2 million business out of his van…", com o valor em verde dentro da legenda branca.
- **Blocos:**
  1. Resultado + detalhe absurdo (0–5 s).
  2. "Olha isso": ano e cenário (5–9 s).
  3. O ponto de partida: largou o emprego, sem ideia (9–17 s).
  4. Pequena tração (17–23 s).
  5. "**Mas tudo mudou um dia**" (23–29 s).
  6. A descoberta e a ideia (29–39 s).
  7. A execução em 3 passos — receita, loja, post (42–52 s).
  8. Número final (52–56 s).
  9. Moral (56–60 s).
- **CTA:** só a moral ("tudo começa contando a sua história"). Nos posts mais novos, o Starter Story manda para o canal.
- **Edição:**
  - Apresentador em fundo verde.
  - Legenda caixa-alta numa pílula branca, com o número em verde.
  - 54 cortes em 60 s.

> **Versão Korvu: "esse cara montou [negócio] usando IA"** · palavra-chave **CASO** → PDF com o link da entrevista ou do artigo original e as ferramentas usadas
> - **Hook:** "Esse cara faz [valor] por mês com um negócio que ele montou usando só [ferramenta de IA]."
> - **Bloco 1:** quem era, num emprego comum.
> - **Bloco 2:** "Mas tudo mudou no dia em que…"
> - **Bloco 3:** a ideia.
> - **Bloco 4:** os 3 passos com a ferramenta.
> - **Bloco 5:** o número.
> - **Bloco 6:** a moral: "você não precisa saber programar".
> - **CTA:** "Comenta CASO que eu te mando a entrevista e as ferramentas."
> - **Atenção:** só caso real, com fonte (o próprio Starter Story tem entrevistas escritas). Número de fonte única não entra (`docs/decisoes.md` §6).

### A5. MagnatesMedia

**Conta:** @MagnatesMedia, YT, 1,86 M.

**Por que performa:**
- Usa o adjetivo extremo no título ("The Craziest Billionaire").
- A voz é grave e o ritmo de trailer.
- Cada short é o trailer do vídeo longo (link na descrição).

**Virais:**
- [Masa Son: The Craziest Billionaire](https://www.youtube.com/shorts/6VQCGzXMTL8): 145.640 views · 7,9 mil likes · 74 comentários · 56 s.
- [Crazy Richard Branson Airline Story](https://www.youtube.com/shorts/xxO81tbylKs): 267.477 views · 10,3 mil likes · 79 comentários · 42 s.
- Não foram baixados. O hook literal **não foi confirmado**: só o título e a descrição foram lidos.

**Leitura:** o adjetivo extremo vai na capa e na primeira frase, e o vídeo vira uma prova em 3 atos (ascensão → queda → aposta absurda).

> **Versão Korvu: "o bilionário mais louco da IA"** · palavra-chave **SON** → PDF com o link de uma entrevista longa do Masayoshi Son
> - **Hook:** "Esse é o investidor mais maluco da era da IA."
> - **Bloco 1:** ganhou fortunas.
> - **Bloco 2:** perdeu boa parte na crise das empresas de internet.
> - **Bloco 3:** agora aposta alto em IA, inclusive na OpenAI.
> - **Bloco 4:** o que isso diz sobre para onde vai o dinheiro.
> - **CTA:** "Comenta SON que eu te mando a entrevista dele."
> - Números só com fonte.

### A6. Fireship

**Conta:** @Fireship, YT, 4,3 M.

**Por que performa:**
- Conta a "história não contada" de uma tecnologia **em linha do tempo e com humor**: um ano por frase, com piada no fim de cada uma.
- É muito compartilhado entre quem trabalha na área.

**Viral:** ["the untold history of web development"](https://www.youtube.com/shorts/aXcuz6fn8_w)
- 5.224.424 views · 291,7 mil likes · 4 mil comentários · 53 s · 2023.
- Não foi baixado, então o hook literal **não foi confirmado**. Formato pela descrição: "a totally comprehensive history…" com #humor.

> **Versão Korvu: "a história não contada do ChatGPT em 50 segundos"** · palavra-chave **HISTORIA** → PDF com a linha do tempo e os links (vídeos oficiais da OpenAI e entrevistas)
> - **Hook:** "A história completa da IA que você usa todo dia, em 50 segundos."
> - **Blocos:** ano → o que aconteceu → piada curta do Carlos, de 1950 até hoje, em 6–8 batidas.
> - **CTA:** "Comenta HISTORIA que eu te mando a linha do tempo com os vídeos."

### A7–A12. Recortes de entrevista (Logically Answered, ColdFusion, Fortune, 60 Minutes, Mo News, Business Insider)

**Leitura comum:**
- O vídeo é **a fala da própria pessoa**, com uma frase de contexto antes e legenda forte.
- Os números são menores (47 mil – 1,2 M), mas é **exatamente o material que o Carlos narra por cima**.

**Virais:**
- [Fortune, Jensen/Denny's](https://www.tiktok.com/@fortune/video/7339978373806017822): 69,4 mil views · 2,4 mil likes · 41 comentários · 32 s.
- [60 Minutes, Hassabis](https://www.tiktok.com/@60minutes/video/7495556995882405166): 47,5 mil views · 1,4 mil likes · 34 comentários · 96 salvamentos · 32 s.
- [Mo News, Hawking avisou sobre a IA](https://www.tiktok.com/@mosheh/video/7685506228730072333): 218 mil views · 9 mil likes · 336 comentários · **1,5 mil salvamentos** · 47 s.
  - Molde: "**Antes do ChatGPT, [pessoa] já avisava que…**".
- [Logically Answered, "Will Sundar Pichai Get Fired?"](https://www.youtube.com/shorts/E7Br8dJjvxg): 71 mil views · 60 s.
  - Molde: pergunta-título sobre um CEO.
- [ColdFusion, origens da DeepSeek](https://www.youtube.com/shorts/dUqfSHOUgP0): 47,8 mil views · 131 s.
- [Business Insider, mensagens de Sam Altman](https://www.tiktok.com/@businessinsider/video/7637649344274992398): 244 mil views · 1,2 mil salvamentos · 78 s.

> **Versão Korvu: "antes de todo mundo, ele já avisava"** (molde Mo News) · palavra-chave **AVISO** → PDF com o link da entrevista original (ex.: Hinton deixando o Google; Hawking na BBC em 2014)
> - **Hook:** "Muito antes do ChatGPT, [pessoa] já avisava isso aqui."
> - **Bloco 1:** a frase dele, no arquivo, com legenda em português.
> - **Bloco 2:** quem é ele, em 1 frase.
> - **Bloco 3:** o que aconteceu desde então.
> - **Bloco 4:** o que isso muda pra você hoje.
> - **CTA:** "Comenta AVISO que eu te mando a entrevista completa."

---

## 3. Frente B: tutoriais, canal por canal

### B1. Sabrina Ramonov

**Conta:** @sabrina_ramonov. TikTok 859,9 mil · YT 429 mil. Na bio do Instagram: "Teaching 10M people AI for free" (Apify), **não confirmado**.

**Por que performa:**
- Lista numerada de **coisas para digitar** (códigos ou atalhos), cada uma com print do resultado.
- No final, palavra-chave para receber "centenas a mais".
- A proporção de **salvamentos (54,5 mil) por views (593 mil) é de 9,2%**, a mais alta da pesquisa.

**Viral:** ["10 secret codes to learn anything"](https://www.tiktok.com/@sabrina_ramonov/video/7694694514350361869)
- 592.900 views · 44,4 mil likes · 1.636 comentários · 54.513 salvamentos · 58 s · 09/10/2026.
- **Hook (0–3 s):** "10 secret codes to learn anything", com o mesmo texto num cartão branco no topo e emoji 😳.
- **Blocos:**
  1. Promessa numerada (0–2 s).
  2. Dez itens de ~5 s cada, no formato "número + nome do código + o que o ChatGPT faz" (2–54 s).
  3. CTA (54–58 s).
- **CTA:** "hit follow and comment CODES and I'll DM you". É palavra-chave + seguir.
- **Edição:**
  - Celular, luz natural, cartão-título fixo no topo que muda por item ("#1 ELI5").
  - Legenda de 1 palavra no peito.
  - Jump cut a cada frase: 50 cortes em 58 s.

> **Versão Korvu: "10 códigos para aprender qualquer coisa com o ChatGPT"** · palavra-chave **CODIGOS** → PDF com os 10 códigos, o texto pronto para copiar e um exemplo de cada
> - **Hook:** "Dez códigos secretos pra aprender qualquer coisa com o ChatGPT."
> - **Blocos:** 10 itens de ~5 s. Exemplos de nomes em português:
>   - "explica como se eu tivesse 5 anos"
>   - "80/20"
>   - "me faz uma prova"
>   - "mapa mental"
>   - "método Feynman"
>   - "me ensina com perguntas"
>   - "folha de estudo de 1 página"
>   - "primeiros princípios"
>   - "post-its"
>   - "esquema"
> - Pode cair para 7 itens se passar de 60 s.
> - **CTA:** "Comenta CODIGOS que eu te mando os dez prontos pra copiar."
> - É o que mais combina com o público da imersão: iniciante, prático, salvável.

### B2. Jeff Su

**Conta:** @JeffSu, YT, 1,92 M.

**Por que performa:**
- "**Explicado em 3 passos/níveis**": cada nível acrescenta UMA coisa ao anterior, com o mesmo exemplo do começo ao fim (o calendário).
- Zero jargão sem tradução.

**Viral:** ["AI Agents explained in 3 steps"](https://www.youtube.com/shorts/BF2k_fKuCVM)
- 854.593 views · 19,6 mil likes · 291 comentários · 52 s · 08/05/2025.
- **Hook (0–3 s):** "AI agents explained in three simple steps", com o título em amarelo + branco e "(in 3 simple steps)" embaixo.
- **Blocos:**
  1. Nível 1, LLM: você pede, ele responde, é passivo (2–14 s).
  2. Nível 2, workflow: ganha acesso a uma ferramenta, mas ainda depende de você (14–29 s).
  3. Nível 3, agente: você dá um **objetivo**, ele raciocina e age sozinho (29–51 s).
- **CTA:** nenhum.
- **Edição:**
  - Estúdio, microfone visível.
  - Título fixo nos primeiros segundos.
  - Pouco corte de cena (o `scdet` contou 2; o ritmo vem de zoom e gráfico).

> **Versão Korvu: "agente de IA explicado em 3 níveis"** · palavra-chave **AGENTE** → PDF com os 3 níveis, um exemplo de negócio pequeno em cada e o link do tutorial gratuito
> - **Hook:** "Agente de IA, explicado em três níveis — sem complicação."
> - **Nível 1:** o ChatGPT que você já usa — pede, ele responde.
> - **Nível 2:** você liga ele à sua agenda, mas ainda é você quem manda cada coisa.
> - **Nível 3:** você dá o objetivo ("cuida da minha agenda de clientes") e ele decide e faz.
> - **Fecho:** "é isso que a gente monta na imersão" (só se o Carlos quiser citar).
> - **CTA:** "Comenta AGENTE que eu te mando o exemplo dos três níveis."

### B3. Nate Herk

**Conta:** @nateherk, YT, 1,07 M.

**Por que performa:**
- "**Eu acabei de construir X sem código**" e, logo em seguida, a demo funcionando de verdade: manda um áudio e o evento aparece na agenda.
- É prova, não promessa.

**Viral:** ["I Built the Ultimate Team of Agents in n8n"](https://www.youtube.com/shorts/2aC2ly7vKtM)
- 1.414.629 views · 52,6 mil likes · 561 comentários · 56 s · 03/02/2025.
- **Hook (0–3 s):** "I just built the ultimate personal assistant in n8n using absolutely no code", com a tela do n8n animando em cima e o rosto + legenda em caixa branca embaixo.
- **Blocos:**
  1. O que construí (0–8 s).
  2. As peças, apontando cada agente (8–15 s).
  3. Pedido real por voz (15–19 s).
  4. Bastidor: ele decide, chama os agentes (19–35 s).
  5. Prova: o evento e o e-mail enviados (35–49 s).
  6. CTA (49–55 s).
- **CTA:** "baixe o workflow de graça no vídeo do canal". É material grátis, o mesmo mecanismo da palavra-chave.
- **Edição:**
  - Tela dividida, tela em cima e rosto embaixo (= o `split` da Korvu).
  - Quase sem cortes (4): a ação na tela segura a atenção.

> **Versão Korvu: "montei um assistente que marca reunião por áudio"** · palavra-chave **ASSISTE** (≤ 8 letras) ou **TIME** → PDF com o passo a passo e o link do tutorial ou do modelo gratuito
> - **Hook:** "Eu montei um assistente que marca reunião e manda e-mail só com um áudio meu."
> - **Bloco 1:** as 3 peças.
> - **Bloco 2:** grava o áudio na frente da câmera.
> - **Bloco 3:** a tela mostrando a agenda e o e-mail chegando.
> - **Bloco 4:** "não escrevi uma linha de código".
> - **CTA:** "Comenta TIME que eu te mando o passo a passo."
> - Exige gravação de ecrã real, sem LUT (regra 8).

### B4. Handlytech (Ayham Joukhadar)

**Conta:** @handlytech. TikTok 483,5 mil. No Instagram, "1.5M" na bio, **não confirmado**.

**Por que performa:**
- **Antes/depois visual nos primeiros 2 s** (144p → 4K), sem fala.
- Depois, o prompt e "comenta X".
- O post "6 remote job websites" teve **3 mil comentários e 21,3 mil salvamentos** em 506 mil views: palavra-chave + lista é a combinação que mais gera comentário.

**Virais:**
- ["Turn ANY photo into 4K with this prompt"](https://www.tiktok.com/@handlytech/video/7627825322297134368): 760.400 views · 28,6 mil likes · 362 comentários · 6.694 salvamentos · 28 s · 12/04/2026.
  - **Hook (0–3 s):** visual — rótulo grande "144p" sobre um vídeo borrado, que vira "4k". Só música, nenhuma fala até 20 s.
  - **Blocos:**
    1. Antes/depois (0–20 s).
    2. Instrução: "abre o Gemini, sobe a foto, usa este prompt" (20–24 s).
    3. CTA (24–28 s).
  - **CTA:** "comment AI and I'll send it to you".
  - **Edição:** 32 cortes em 28 s, texto gigante no centro, música em alta.
- ["6 remote job websites… Comment JOB"](https://www.tiktok.com/@handlytech/video/7532082415339048214): 506 mil views · 3.005 comentários · 21.347 salvamentos · 19 s.

> **Versão Korvu: "foto velha → foto nova com um prompt"** · palavra-chave **FOTO** → PDF com o prompt exato e o passo a passo no Gemini
> - **Hook:** antes/depois na tela (foto antiga de família → nítida) e o Carlos fala logo no segundo 1: "Olha o que um prompt faz com uma foto velha."
> - **Bloco 1:** onde fazer, de graça.
> - **Bloco 2:** os 3 cliques.
> - **Bloco 3:** mais um antes/depois.
> - **CTA:** "Comenta FOTO que eu te mando o prompt exato."
> - **Ajuste:** a Korvu não pode usar foto realista de pessoa real além do Carlos (regra 3). Usar foto do próprio Carlos ou de objeto/lugar.

### B5. Nate B. Jones

**Conta:** @nate.b.jones, TikTok, 492,1 mil.

**Viral:** ["It takes 5 seconds"](https://www.tiktok.com/@nate.b.jones/video/7694081567911693598)
- 864.100 views · 22,4 mil likes · **2.254 comentários** · 13.992 salvamentos · 63 s · 08/10/2026.
- Não foi baixado, então o hook literal **não foi confirmado**.
- **Leitura:** a promessa de **esforço mínimo** ("leva 5 segundos") + "testa e me conta" gera comentário sem pedir palavra-chave.

> **Versão Korvu:** "Leva 5 segundos e muda as respostas do ChatGPT"
> - Uma instrução para colar nas configurações.
> - Mostra a resposta antes e depois.
> - **CTA:** "Comenta CINCO que eu te mando o texto pra colar."

### B6. Harper Carroll

**Conta:** @harpercarrollai, TikTok, 91,2 mil.

**Viral:** ["10 Days of AI Basics — Day 1"](https://www.tiktok.com/@harpercarrollai/video/7464689388274879790)
- 355.900 views · 16,8 mil likes · 297 comentários · 7.934 salvamentos · 89 s.
- **Leitura:**
  - **Série numerada para iniciantes** ("Dia 1 de 10").
  - A credencial vem logo no começo (Stanford).
  - Funciona porque promete continuidade, e quem salva volta.
  - É o formato mais alinhado com a **imersão**: "Dia 1 de 10 — IA do zero, em português".

> **Versão Korvu:** série "IA do zero em 10 dias", com 1 Reel por conceito
> - **Dia 1:** o que é IA vs. ChatGPT.
> - **Dia 2:** o que é prompt.
> - **Dia 3:** agente…
> - **CTA:** "Comenta ZERO que eu te mando o guia do Dia 1."
> - O PDF acumula os dias.

### B7. Dan Martell

**Conta:** @DanMartell, YT, 3,12 M.

**Viral:** ["Stop pretending not to know how to start a business with Claude Code"](https://www.youtube.com/shorts/JpLgVf8Alys)
- 477.144 views · 18,6 mil likes · 184 comentários · 42 s · 02/06/2026.
- Hook literal **não confirmado** (só o título foi lido).
- **Leitura:** é um **puxão de orelha** ao empreendedor ("pare de fingir que não sabe…") seguido de 3 passos. Funciona com dono de pequeno negócio.

> **Versão Korvu:** "Para de dizer que IA não é pra você"
> - 3 passos para o primeiro uso no negócio.
> - **CTA:** "Comenta PASSOS que eu te mando os três por escrito."

### B8–B10. Tiff in Tech, Matt Wolfe, The AI Advantage

- **Tiff in Tech** ([Raspberry Pi](https://www.youtube.com/shorts/dH9HsMg5BGw), 723 mil): "O que EXATAMENTE é X e por que as empresas usam?". É o molde para "O que é o n8n?" e "O que é um agente?".
  - Atenção: os dois maiores virais dela no TikTok (15,8 M e 10,2 M) têm poucos comentários e parecem impulsionados.
- **Matt Wolfe** ([Nvidia's $20B loophole explained](https://www.youtube.com/shorts/6RAbKg-yUg8), 157 mil): notícia de IA explicada em 1 minuto, com tom de "entenda o que aconteceu".
- **The AI Advantage** ([free AI tool removes watermarks](https://www.youtube.com/shorts/GK1_BX0iZBw), 121 mil): "ferramenta GRÁTIS que faz X em segundos (não é publi)". O "não é publi" aumenta a confiança.

---

## 4. Esqueletos prontos para traduzir

Cada esqueleto tem o hook (0–3 s), os blocos e o CTA. Todos pedem **material real em PDF** (`00-marca/cta.md`), CTA falado com ≤ 12 palavras e palavra-chave sem acento.

| # | Nome | Original | Hook (molde PT-BR) | Blocos | CTA / palavra | Duração |
|---|---|---|---|---|---|---|
| 1 | **A lista de façanhas** | [Kallaway/Nolan](https://www.youtube.com/shorts/R1bn__sNAaM) | "Sabe [coisa famosa]? Foi [pessoa]… e isso nem é o mais louco que ele fez." | quem é (1 frase) → façanha 1 com número → façanha 2 → metralhadora de 2 → "o mais impressionante é o porquê" + frase dele | DOC → documentário/entrevista | 60–75 s |
| 2 | **A decisão que valeu milhões** | [How Money Works/Choe](https://www.youtube.com/shorts/jJ0i4JxY-tE) | "Esse é [pessoa]. Em [ano], ele tomou a decisão mais inteligente da vida." | antes (pequeno) → encruzilhada → escolha + frase dele → número de hoje → lição p/ pequeno negócio | VIDEO → entrevista | 50–60 s |
| 3 | **"Mas por quê?"** | [Cleo Abram/Jensen](https://www.tiktok.com/@cleoabram/video/7464683554446953774) | "Esse é [pessoa]. [Empresa] virou [feito]. Mas por quê, exatamente?" | resposta em 1 palavra → analogia simples → antes/depois → a virada para a IA → o que muda pra você | NVIDIA / nome → entrevista longa | 55–75 s |
| 4 | **Do nada ao número** | [Starter Story/van](https://www.youtube.com/shorts/wUx3M5eP20k) | "Esse cara faz [valor] com [coisa improvável] usando IA." | emprego comum → "mas tudo mudou no dia em que…" → ideia → 3 passos → número → moral | CASO → entrevista + ferramentas | 60 s |
| 5 | **A linha do tempo com humor** | [Fireship](https://www.youtube.com/shorts/aXcuz6fn8_w) | "A história inteira de [tecnologia] em 50 segundos." | 6–8 batidas ano → fato → piada | HISTORIA → linha do tempo com links | 50–60 s |
| 6 | **Antes de todo mundo, ele avisou** | [Mo News/Hawking](https://www.tiktok.com/@mosheh/video/7685506228730072333) | "Muito antes do ChatGPT, [pessoa] já dizia isso aqui." | a frase no arquivo → quem é → o que aconteceu → o que muda hoje | AVISO → entrevista original | 45–60 s |
| 7 | **N códigos/atalhos numerados** | [Sabrina Ramonov](https://www.tiktok.com/@sabrina_ramonov/video/7694694514350361869) | "Dez códigos secretos pra [resultado] com o ChatGPT." | 7–10 itens de 5 s (nome + o que faz + print) | CODIGOS → lista pronta para copiar | 55–60 s |
| 8 | **Explicado em 3 níveis** | [Jeff Su](https://www.youtube.com/shorts/BF2k_fKuCVM) | "[Conceito] explicado em três níveis." | nível 1 (o que você já usa) → nível 2 (+ ferramenta) → nível 3 (+ autonomia), sempre o mesmo exemplo | AGENTE → exemplos por nível | 50–60 s |
| 9 | **Construí e funciona** | [Nate Herk](https://www.youtube.com/shorts/2aC2ly7vKtM) | "Eu montei [assistente] que faz [tarefa] sem uma linha de código." | as peças → pedido real → bastidor na tela → prova (resultado chegando) | TIME → passo a passo/modelo | 55–60 s |
| 10 | **Antes/depois + prompt** | [Handlytech](https://www.tiktok.com/@handlytech/video/7627825322297134368) | (visual) antes → depois + "Olha o que um prompt faz com [coisa]." | onde (grátis) → 3 cliques → 2.º antes/depois | FOTO → prompt exato | 25–35 s |

**Como os de fora fecham, e o que muda na Korvu:**
- Os maiores virais de história **não têm CTA**: terminam na revelação e o vídeo entra em loop.
- Os de tutorial usam **palavra-chave + DM** (Sabrina, Handlytech, Awa K. Penn) ou "material grátis no canal" (Nate Herk).
- Na Korvu, a palavra-chave entra **depois da revelação**, nos últimos 4–5 s, para não matar o loop.

---

## 5. O que copiar no estilo de edição

- **Nome e número em letra gigante** no momento em que são ditos (How Money Works, Starter Story). O resto da legenda fica pequeno.
- **A pessoa recortada entra quando o nome é dito** (Kallaway, Cleo). Combina com o `split` da Korvu: Carlos embaixo, arquivo em cima.
- **Seta e destaque verde-limão** em print de manchete (Cleo). Na Korvu, trocar pelo laranja da marca.
- **Ritmo:** história em ~1 corte por segundo (Kallaway, 58 cortes/60 s; Starter Story, 54/60). Tutorial de tela aguenta poucos cortes quando a tela está **acontecendo** (Nate Herk, 4 cortes).
- **Cartão-título fixo no topo que muda a cada item** (Sabrina). Ajuda quem chega no meio e incentiva a salvar.
- **Duração:** todos os 8 baixados têm entre 28 e 60 s. Para os perfis de até 90 s (decisão de 13/10), vale o esqueleto 1 ou 3, que comportam mais provas.

## 6. Lacunas desta pesquisa

- Seguidores no Instagram: **nenhum confirmado** (sem acesso anônimo).
- Contas de minidoc só de Instagram ou TikTok, sem YouTube, ficaram de fora: a busca por handle exige saber o nome, e as buscas na web não as revelaram.
- O hook literal só foi confirmado nos 8 vídeos baixados e transcritos. Nos outros (Fireship, MagnatesMedia, Dan Martell, Nate B. Jones), está **não confirmado**.
