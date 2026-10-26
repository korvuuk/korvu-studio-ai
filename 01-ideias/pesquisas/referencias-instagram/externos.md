# Referências externas — os maiores criadores de IA (Instagram, TikTok, YouTube Shorts)

> Pesquisa de **14/10/2026** para as 3 linhas de conteúdo da Korvu. Pedido do Carlos (14/10): priorizar os
> **maiores criadores em inglês** (EUA, Reino Unido, Índia…) com conteúdo bem estruturado e engajamento alto,
> **pegar o que já funcionou lá fora** (estrutura, hook, ângulo, CTA) e adaptar para o português dele. No máximo
> 2–3 brasileiros. Não repete nenhum perfil da lista que ele já mandou (liianjeon, ibrahimwaz_, ocamarggos,
> human___academy, cauetgurgell, oluizsampaio, _quemleenriquece, terencesia, douglasmissura).
>
> **Como os números foram colhidos (todos em 14/10/2026, sem login nem cookies):**
> - Instagram, seguidores: `og:description` da página pública do perfil. Curtidas/comentários de posts: metadados
>   públicos do post (yt-dlp sem login). O Instagram **não mostra visualizações** de Reels sem login, então elas
>   ficam "não confirmado".
> - YouTube: inscritos e visualizações via yt-dlp (`channel_follower_count`, `view_count`). Os "top Shorts" são os
>   mais vistos **entre os 60 Shorts mais recentes** de cada canal, e não o recorde histórico.
> - TikTok: `followerCount` da página pública do perfil + metadados dos vídeos.
> - CreatorDB (`creatordb.app/creatorstats/<conta>`) só para confirmar a tendência e achar os links dos posts.
> - Hooks e CTAs dos 9 vídeos baixados vêm da **transcrição local (mlx-whisper)** e dos frames de 0 a 3 s.
>   Os arquivos ficam no scratchpad da sessão (`refs/externos/`), só para estudo e fora do projeto.
> - ⚠ Curtidas que aparecem como "3" num post significam que a conta **escondeu as curtidas**. Esses números não
>   são confiáveis.

---

## 1. Tabela-resumo

| # | Canal | Plataforma principal | Linha | Seguidores (14/10/2026) | Por que é referência |
|---|---|---|---|---|---|
| 1 | **Varun Mayya** — [@thevarunmayya](https://www.instagram.com/thevarunmayya/) · [YT @VarunMayya](https://www.youtube.com/@VarunMayya) | IG + YT (Índia, inglês) | 1 · 2 | IG 1M · YT 1,18M | É o melhor exemplo do formato **"uma pessoa + uma história"**, com cenas cinematográficas geradas por IA alternadas com o apresentador |
| 2 | **Rowan Cheung** (The Rundown AI) — [@rowancheung](https://www.instagram.com/rowancheung/) | IG + TikTok | 1 · 2 | IG 504K · TikTok 79,7K | **"Pessoa comum que prosperou com IA"**, narrado por cima das imagens da própria pessoa. É o molde exato da série de perfis |
| 3 | **Cleo Abram** — [@cleoabram](https://www.instagram.com/cleoabram/) · [YT](https://www.youtube.com/@CleoAbram) · [TikTok](https://www.tiktok.com/@cleoabram) | YT + IG + TikTok | 1 · 3 | YT 8,86M · IG 3M · TikTok 2,5M | É a maior narradora de tecnologia otimista. Faz um explicativo em forma de história, com pergunta no hook |
| 4 | **ColdFusion** — [YT @ColdFusion](https://www.youtube.com/@ColdFusion) | YouTube | 1 | YT 5,25M | Faz minidocumentários de tecnologia, como as origens do DeepSeek e as histórias de empresas, com narração em off sobre imagens de arquivo |
| 5 | **Fireship** — [YT @Fireship](https://www.youtube.com/@Fireship) · [@fireship_dev](https://www.instagram.com/fireship_dev/) | YouTube | 1 · 2 | YT 4,3M · IG 137K | Conta a "história de X em 50 s" com uma **linha do tempo seca**, repetição e humor. É o recorde de retenção do nicho |
| 6 | **Startup Archive** — [@startuparchive_](https://www.instagram.com/startuparchive_/) · [YT](https://www.youtube.com/@startuparchive_) | IG | 1 | IG 255K · YT 37,6K | Recorta falas de fundadores (Altman, Jobs, Bezos) com legenda e contexto. É curadoria pura de arquivo |
| 7 | **Kallaway** — [@kallaway](https://www.instagram.com/kallaway/) | IG | 1 · 2 | IG 461K · YT 40,4K | É o mestre do hook: usa a fórmula "esta empresa faz X impossível" com um rótulo-metáfora na tela ("Uber Eats do sol") |
| 8 | **Evolving AI** — [@evolving.ai](https://www.instagram.com/evolving.ai/) | IG | 2 | IG 5M (CreatorDB: 4,83M em 06/10) | É a **maior página de IA do Instagram**. Publica notícias e vídeos virais de IA cerca de 38 vezes por semana, com legenda-artigo |
| 9 | **AI / Tech** — [@chatgptricks](https://www.instagram.com/chatgptricks/) | IG | 2 | IG 3M | É página de notícias/curadoria. Serve de referência de volume, mas o engajamento atual é baixo (veja a seção) |
| 10 | **AI researches** — [@airesearches](https://www.instagram.com/airesearches/) | IG | 2 | IG 1M | Faz curadoria de vídeos gerados por IA ("filme que não existe") |
| 11 | **The AI Field** — [@theaifield](https://www.instagram.com/theaifield/) | IG | 2 | IG 629K | Faz notícia de robótica/IA com ângulo de cultura pop ("o filme de 2004 previu isto") |
| 12 | **The AI Page** — [@theaipage](https://www.instagram.com/theaipage/) | IG | 2 | IG 578K | É página de curadoria de notícias de IA. Posts não confirmados |
| 13 | **God of Prompt** — [@godofprompt](https://www.instagram.com/godofprompt/) | IG | 2 | IG 351K | **Todo post começa com "Comment 'X' and I'll send you…"**. É o modelo mais puro do funil palavra-chave → direct |
| 14 | **Tiff in Tech** — [@tiffintech](https://www.instagram.com/tiffintech/) · [TikTok](https://www.tiktok.com/@tiffintech) · [YT](https://www.youtube.com/@TiffInTech) | IG + TikTok + YT | 2 · 3 | IG 813K · YT 648K · TikTok 342K | Faz notícia de tecnologia com rosto e voz próprios, e conseguiu entrevista com Zuckerberg. Tem o melhor engajamento do grupo |
| 15 | **Greg Isenberg** — [YT @GregIsenberg](https://www.youtube.com/@GregIsenberg) · [@gregisenberg](https://www.instagram.com/gregisenberg/) | YT + IG | 2 · 3 | YT 727K · IG 153K | Ensina IA para negócio e Claude Code em menos de 1 minuto, com títulos "como 10x seu…" |
| 16 | **Kevin Stratvert** — [YT](https://www.youtube.com/@KevinStratvert) · [@kevinstratvert](https://www.instagram.com/kevinstratvert/) · [TikTok](https://www.tiktok.com/@kevinstratvert) | YT + IG + TikTok | 3 | YT 4,46M · IG 924K · TikTok 488K | É o maior canal de tutorial de software. Traz passo a passo calmo, sem jargão |
| 17 | **Jeff Su** — [YT @JeffSu](https://www.youtube.com/@JeffSu) | YT | 3 | YT 1,92M | É a **referência de didática**: "X explicado em 3 passos/níveis", com tela limpa e tipografia forte |
| 18 | **Futurepedia** — [YT @futurepedia_io](https://www.youtube.com/@futurepedia_io) | YT | 3 | YT 759K | Faz tutorial de ferramentas de IA (escrita, animação, imagem) |
| 19 | **Nate Herk** — [YT @nateherk](https://www.youtube.com/@nateherk) · [TikTok](https://www.tiktok.com/@nateherk) | YT | 3 | YT 1,07M · TikTok 17,9K | Ensina agentes e automação (n8n, Claude Code) para negócio |
| 20 | **Matt Wolfe** — [YT @mreflow](https://www.youtube.com/@mreflow) | YT | 2 · 3 | YT 1,02M | Junta notícia e demonstração de ferramentas novas. É criador do diretório Future Tools |
| 21 | **The AI Advantage** — [YT @aiadvantage](https://www.youtube.com/@aiadvantage) | YT | 3 | YT 487K | Mostra na tela uma ferramenta nova sendo usada no dia do lançamento |
| 22 | **Allie K. Miller** — [@alliekmiller](https://www.instagram.com/alliekmiller/) | IG (+ LinkedIn) | 3 | IG 215K | Fala com **iniciantes de 40+ anos** e pequenos negócios, e corta trechos de entrevistas na TV |
| 23 | **Dot CSV** (espanhol) — [YT @DotCSV](https://www.youtube.com/@DotCSV) · [@dotcsv](https://www.instagram.com/dotcsv/) | YT | 1 · 3 | YT 920K · IG 106K | Divulgador de IA numa língua latina: prova que o formato funciona fora do inglês |
| 24 | 🇧🇷 **Bruno Picinini** — [@brunopicinini](https://www.instagram.com/brunopicinini/) · [YT](https://www.youtube.com/@brunopicinini) | IG + YT | 2 · 3 | IG 238K · YT 446K | Ensina agentes de IA para marketing e infoprodutos. Usa CTA de palavra-chave ("Digite AROS24") |
| 25 | 🇧🇷 **Rafael Milagre** — [@rafaelmilagre](https://www.instagram.com/rafaelmilagre/) · [YT](https://www.youtube.com/@RafaelMilagre) | IG | 2 · 3 | IG 121K · YT 9,47K | Faz comparativos e "tier list" de IAs em PT-BR. Posts no IG não confirmados |

**Ficaram de fora por falta de dado confiável:** Riley Brown (não achei o @ certo) e Paulo Faustino (🇵🇹, IG 420K). O
perfil de Paulo Faustino é de marketing digital e não confirmei conteúdo de IA. Também saiu o Thiago Finch (IG 3M),
cujo conteúdo é de negócios e estilo de vida, não de IA.

---

## 2. Linha 1 — Histórias e perfis de pessoas da IA

### Varun Mayya — [@thevarunmayya](https://www.instagram.com/thevarunmayya/) · [YouTube](https://www.youtube.com/@VarunMayya)
- **Seguidores:** IG 1M · YT 1,18M (14/10/2026).
- **Formato típico:** 60–95 s. Ele aparece no fundo de estúdio, a câmera alterna com **cenas cinematográficas geradas
  por IA** (quarto escuro, computador antigo) e as legendas vêm em 2 tamanhos, com a palavra-chave em negrito. Também
  usa cortes de entrevistas dele com Sundar Pichai e Satya Nadella.
- **Posts virais:**
  - [This Engineer Saved The Internet From The Worst Cyber Attack](https://www.youtube.com/shorts/FdmpR0-XvvU), de 03/08/2026, com **507.765 views, 19.951 likes e 155 comentários**, em 92 s. ✅ baixado e transcrito.
    - **Hook literal (0–4 s):** "This one person saved the internet from one of the worst cyber attacks in history. All because he noticed his computer was 0.5 seconds slower than usual."
    - **Tela:** um homem de costas diante de um computador verde, com o texto "This Person Saved / **the internet from** / one of the **Worst Cyberattacks** in history".
    - **Estrutura:** hook com o detalhe absurdo (0,5 s), depois o nome e a profissão ("Andres Freund, a Microsoft engineer"), a investigação passo a passo, a virada ("wasn't a bug… it was a backdoor"), o vilão (2 anos ganhando confiança) e o desfecho.
    - **CTA:** nenhum falado. Fecha com a moral: "If that one person hadn't noticed…".
  - [Ben Affleck Went From Batman to Writing Python and Building With GPUs](https://www.youtube.com/shorts/ImXJXYCvBjY), de 09/10/2026, com 286.644 views, 12.464 likes e 122 comentários, em 96 s.
  - Reel com Sundar Pichai ([C7CPlnDLW9W](https://www.instagram.com/p/C7CPlnDLW9W/)), com 98.496 curtidas e 451 comentários.
- **O que o torna forte:** escolhe a **pessoa desconhecida por trás de algo enorme** e conta com tensão de thriller. A
  imagem gerada por IA resolve a falta de vídeo de arquivo.

### Rowan Cheung — [@rowancheung](https://www.instagram.com/rowancheung/)
- **Seguidores:** IG 504K · TikTok 79,7K (14/10/2026). É fundador da newsletter The Rundown AI.
- **Formato típico:** narração em off, sem aparecer, **sobre as imagens da própria pessoa/empresa**, com legenda
  palavra a palavra em branco simples. Alterna com entrevistas exclusivas (Zuckerberg, Sam Altman).
- **Posts virais:**
  - [O agricultor de brócolis do Japão que automatizou a fazenda com ChatGPT e Codex](https://www.instagram.com/p/DZddnLvOmMC/), de 11/06/2026, com **90.741 curtidas e 336 comentários**, em ~73 s (views não confirmado). ✅ baixado e transcrito.
    - **Hook literal:** "So this broccoli farmer in northern Japan automated his own farm by writing software. And the craziest part is that he's never even studied engineering or even agriculture."
    - **Tela 0–3 s:** o próprio agricultor no campo e depois na estufa com um notebook, com legenda curta palavra a palavra.
    - **Estrutura:** quem é (ex-servidor público que aprendeu a plantar sozinho), o tamanho do desafio (250 acres, difícil de contratar), a virada (ChatGPT + Codex, "um engenheiro de elite ao lado"), **3–4 usos concretos** (foto da doença → diagnóstico, bot da estufa, satélite, piloto GPS) e a moral.
    - **CTA literal:** "If you want to stay in the loop with the latest in AI and robotics, follow for more."
  - [Startup Transfyr: IA para descobrir por que o experimento falha num laboratório e funciona noutro](https://www.instagram.com/p/DdXVicFBYb1/), de 16/09/2026, com 91.373 curtidas e 503 comentários.
  - [Sam Altman sobre o Sora](https://www.instagram.com/p/DPo6Y-zCQlN/), de 10/10/2025, com 6.849 curtidas e **1.287 comentários**. Entrevista exclusiva gera muito comentário.
- **O que o torna forte:** a **"pessoa comum + IA = resultado"** é a tese inteira da imersão da Korvu, e o vídeo usa
  só material da própria pessoa.

### Cleo Abram — [@cleoabram](https://www.instagram.com/cleoabram/) · [YouTube](https://www.youtube.com/@CleoAbram) · [TikTok](https://www.tiktok.com/@cleoabram)
- **Seguidores:** YT 8,86M · IG 3M · TikTok 2,5M (14/10/2026).
- **Formato:** série "Huge If True". Ela apresenta e anda pelo cenário, com animação limpa. O hook é uma **pergunta ou
  afirmação contraintuitiva** ("The Sun Isn't The Center of the Solar System").
- **Shorts mais vistos (entre os 60 recentes):** [Why The World Cup Ball Looks Like That](https://www.youtube.com/shorts/Y4dzIWxFqp8) com 14M views. [The Weather System Is About To Break](https://www.youtube.com/shorts/8NwZBXvI8kg) com 7,7M. Os de IA específicos não foram confirmados.
- **Força:** é **otimista** e foge do "a IA vai roubar seu emprego". Fala de tecnologia para quem não é técnico.

### ColdFusion — [YouTube @ColdFusion](https://www.youtube.com/@ColdFusion)
- **Seguidores:** YT 5,25M.
- **Formato:** documentário longo (15–30 min) e Shorts recortados dele, com voz grave em off sobre arquivo, manchetes e
  música ambiente.
- **Post de referência:** [The Origins of DeepSeek](https://www.youtube.com/shorts/dUqfSHOUgP0), de 09/06/2026, com 47.754 views, 1.198 likes e 26 comentários, em 131 s.
- **Força:** credibilidade e trilha. ⚠ Nos Shorts rende pouco, porque o formato longo não se adapta bem ao vertical.
  **Lição:** narração documental pura precisa de hook mais rápido que o do ColdFusion.

### Fireship — [YouTube @Fireship](https://www.youtube.com/@Fireship)
- **Seguidores:** YT 4,3M · IG [@fireship_dev](https://www.instagram.com/fireship_dev/) 137K.
- **Post viral:** [the untold history of web development](https://www.youtube.com/shorts/aXcuz6fn8_w), de 20/12/2023, com **5.224.424 views, 291.688 likes e 4.000 comentários**, em 53 s. ✅ transcrito.
  - **Hook literal:** "1990, HTML is invented." Começa direto, sem introdução, com o ano em pixel art gigante na tela.
  - **Estrutura:** uma **linha do tempo com refrão** ("invented to fix…") repetido 15 vezes. O punchline final é "2024, jQuery is still used on 75% of websites".
  - **CTA:** nenhum. O vídeo é feito para ser compartilhado.
- **Força:** cabe uma **história inteira em 50 s** com ritmo de piada. Copiar para "A história do ChatGPT em 60 s: 2015…, 2017…".

### Startup Archive — [@startuparchive_](https://www.instagram.com/startuparchive_/)
- **Seguidores:** IG 255K · YT 37,6K.
- **Formato:** recorte de 30–90 s de fala de fundador (entrevista/palestra), com legenda e título-citação.
- **Exemplos (YT):** [Sam Altman explains how he decides to invest in a startup after 10 minutes](https://www.youtube.com/shorts/zccRD7iIXoA) com 15K views. [Steve Jobs: "My model of business is The Beatles"](https://www.youtube.com/shorts/rUhGkYTLxL8) com 13K. Os números do IG não foram confirmados.
- **Força:** curadoria de arquivo com **título = citação forte da pessoa**. A Korvu faz o mesmo, mas **com o Carlos
  narrando o contexto**, que é o diferencial.

### Kallaway — [@kallaway](https://www.instagram.com/kallaway/)
- **Seguidores:** IG 461K · YT 40,4K.
- **Post viral:** [This company lets you order sunlight on demand](https://www.instagram.com/p/DA8kxupvEzk/), de 10/10/2024, com **412.268 curtidas e 3.903 comentários**, em ~57 s. ✅ transcrito.
  - **Hook literal:** "Check this out. This company lets you order sunlight on demand. It's like Uber Eats for the sun."
  - **Tela 0–3 s:** o apresentador sobreposto a um globo, depois a Terra à noite, com um **rótulo vermelho e amarelo "UBER EATS FOR SUNLIGHT"**.
  - **Estrutura:** a coisa absurda, depois a **metáfora conhecida**, o "But that's not even the craziest part", o nome da empresa, como funciona, a prova (pedidos no site) e a **aplicação humana** (vítimas do furacão).
  - **CTA:** nenhum falado.
  - Outros: [Lifesize Floor Plans](https://www.instagram.com/p/C_iVgDcJLd1/) com 679.589 curtidas e 2.156 comentários. [plástico → biscoito](https://www.instagram.com/p/DdRJVg4OYso/), de 14/09/2026, com 137.405 curtidas e 3.488 comentários.
- **Força:** o **rótulo-metáfora** na tela e a frase-ponte "but that's not even the craziest part" seguram a retenção.

---

## 3. Linha 2 — Conteúdo rápido de engajamento e salvamento

### Evolving AI — [@evolving.ai](https://www.instagram.com/evolving.ai/)
- **Seguidores:** IG 5M no perfil público. Segundo o [CreatorDB](https://creatordb.app/creatorstats/evolvingai/), eram 4.827.758 em 06/10/2026, com +29K em 30 dias, engajamento de 3,5% e cerca de 38 posts por semana.
- **Formato:** vídeo viral de IA/tecnologia (de terceiros, com crédito) e **legenda-artigo** com o 1.º parágrafo de impacto.
- **Posts:** [Tesla a 285 km/h](https://www.instagram.com/p/Dd9g140zMcc/) com 85.567 curtidas e 3.101 comentários. [Curta "Star Wars" feito por 1 criador com IA](https://www.instagram.com/p/Dd68s44gQsR/) com 72.163 curtidas e 1.591 comentários. Hook: "And the worst part for Disney? This came from one creator with a vision, not a $200M production."
- **Força:** volume e velocidade. Publica a notícia no mesmo dia, com a frase de abertura em tom de "fofoca".

### AI / Tech — [@chatgptricks](https://www.instagram.com/chatgptricks/) · AI researches — [@airesearches](https://www.instagram.com/airesearches/) · The AI Field — [@theaifield](https://www.instagram.com/theaifield/) · The AI Page — [@theaipage](https://www.instagram.com/theaipage/)
- **Seguidores:** 3M · 1M · 629K · 578K (14/10/2026).
- **Posts recentes:**
  - chatgptricks: [Trump liga para Jensen Huang no palco](https://www.instagram.com/p/DdSiDCNg9qp/) com 4.665 curtidas e 145 comentários. [Neuralink "I love you"](https://www.instagram.com/p/Ddae3bYx3ov/) com 4.336 curtidas e 57 comentários.
  - airesearches: [criatura gigante gerada por IA](https://www.instagram.com/p/DdwetZ1q7cF/) com 19.883 curtidas e 182 comentários. ["4 billion women. One man."](https://www.instagram.com/p/DdpBUHzM7wD/) com 7.733 curtidas e 644 comentários.
  - theaifield: [Olimpíadas de robôs na China](https://www.instagram.com/p/Dcn5DP9jOHs/) com 24.999 curtidas e 329 comentários. Ângulo "I, Robot came out in 2004 and it is aging strangely well".
- **Lição:** essas páginas faceless crescem por volume, mas **o engajamento por post é baixo** (0,1–0,8% dos
  seguidores). Muitos posts escondem as curtidas. **Não copiar o modelo de página-sem-rosto.** Copiar só os ângulos
  ("o filme previu isto", "1 criador vs. Hollywood").

### God of Prompt — [@godofprompt](https://www.instagram.com/godofprompt/)
- **Seguidores:** IG 351K.
- **Formato:** a moldura é um "print de post do X" (avatar + texto) com o vídeo embaixo. A **1.ª linha de toda legenda é
  o CTA de palavra-chave**.
- **Posts:**
  - [Coca-Cola vs. FedEx: anúncios feitos com IA](https://www.instagram.com/p/DFO8iWMOFjC/), de 25/01/2025, com **65.879 curtidas e 438 comentários**. ✅ baixado.
    - **Tela:** moldura de tweet com o texto "Coca-Cola is going all-in on AI ads. Meanwhile, FedEx…", e o vídeo é o anúncio da FedEx.
    - **CTA literal (legenda):** "Comment 'Prompt' and I will send you a FREE ChatGPT guide!"
  - Posts de 08/2026 com "Comment 'AI' and I'll send you the full prompt" ([campanha a partir de 1 foto](https://www.instagram.com/p/DcBa1OJyLsY/), com 74 comentários e curtidas ocultas).
- **Força / lição:** o **comparativo "marca A × marca B"** gera debate. A palavra-chave sozinha não basta: os posts
  recentes têm pouco comentário. **O CTA precisa ser falado e a promessa, específica** (como a Korvu já decidiu em 13/10).

### Tiff in Tech — [@tiffintech](https://www.instagram.com/tiffintech/) · [TikTok](https://www.tiktok.com/@tiffintech)
- **Seguidores:** IG 813K · YT 648K · TikTok 342,1K (4,6M curtidas no total).
- **Posts:**
  - [E se os computadores usassem luz em vez de eletricidade?](https://www.instagram.com/p/DQO_cyuEaUr/), de 25/10/2025, com 85.205 curtidas e 694 comentários. **Hook em pergunta.**
  - [Construindo um modelo de ML para prever o GP do Japão de F1](https://www.instagram.com/p/DHvpvxTg2ci/) com 38.756 curtidas e 349 comentários.
  - YT: [Mark Zuckerberg on building the most private personal AI agent](https://www.youtube.com/shorts/SZPZ_AZnfRg) com 595K views.
  - TikTok: [ASML's 20-year monopoly…](https://www.tiktok.com/@tiffintech/video/7673353329811950856) com 140,6K views, 8.590 likes e 687 comentários.
- **Força:** rosto e voz constantes, notícia traduzida em "o que isso muda", alto engajamento relativo e acesso a CEOs.

### Greg Isenberg — [YouTube @GregIsenberg](https://www.youtube.com/@GregIsenberg)
- **Seguidores:** YT 727K · IG 153K.
- **Posts:** [How to 10x your Claude with 4 .md files](https://www.youtube.com/shorts/ovLAIhbk3ek), de 31/03/2026, com **833.468 views, 39.108 likes e 255 comentários**, em 47 s. [Claude Code + Obsidian in under 1 minute](https://www.youtube.com/shorts/yJK5GueSHmU) com 646K views.
- **Força:** **número + resultado + tempo** no título ("10x", "4 arquivos", "em 1 minuto"). É o que faz salvar.

---

## 4. Linha 3 — Aprendizado e tutorial

### Jeff Su — [YouTube @JeffSu](https://www.youtube.com/@JeffSu)
- **Seguidores:** YT 1,92M.
- **Post viral:** [AI Agents explained in 3 steps](https://www.youtube.com/shorts/BF2k_fKuCVM), de 08/05/2025, com **854.593 views, 19.609 likes e 291 comentários**, em 51 s. ✅ transcrito.
  - **Hook literal:** "AI agents explained in three simple steps."
  - **Tela:** ele no microfone com o título gigante "AI AGENTS EXPLAINED (in 3 simple steps)", e logo **tela preta com "LEVEL 1: LARGE LANGUAGE MODELS"**.
  - **Estrutura:** **3 níveis** (LLM → workflow → agente), cada um com um exemplo do dia a dia (e-mail, agenda) e a mesma frase-régua: "at this level, the LLM is passive / has tools / acts autonomously".
  - **CTA:** nenhum. É conteúdo de salvar.
- Outros: [When to use ChatGPT, Gemini, and Claude](https://www.youtube.com/shorts/sfwax2dVPvI) com 228K views.
- **Força:** é a **melhor estrutura didática do nicho** e funciona com iniciante absoluto.

### Allie K. Miller — [@alliekmiller](https://www.instagram.com/alliekmiller/)
- **Seguidores:** IG 215K.
- **Post:** [If I woke up brand new to AI tomorrow… first agent by Friday](https://www.instagram.com/p/DdHibHQzGZy/), de 10/09/2026, com 7.689 curtidas e **706 comentários**, em ~2 min (views não confirmado). ✅ transcrito.
  - **Tela:** corte da entrevista no Yahoo Finance (*Power Players*), com uma caixa branca "How a total beginner builds their first AI agent".
  - **Hook (pergunta do apresentador):** "Let's say I am new to AI today. How do I create an agent?… Let's say I'm my mom."
  - **Estrutura:** passo 1 (abrir o notebook), passo 2 (Claude/ChatGPT, baixar o app), passo 3 ("rant about a problem… interview me"). A prova social vem no fim ("diretores de RH me disseram: ninguém me contou que era só escrever 'build me an AI agent that'").
  - **CTA (legenda):** "If you want to actually start using it, my free 5-day email…" (curso grátis por e-mail).
  - Outro: [Gen X women and AI](https://www.instagram.com/p/DdE-qOWztxp/) com **1.159 comentários**, falando com mulheres de 46–61 anos que tocam negócios.
- **Força:** é o **público mais parecido com o da Korvu** (iniciante, mais velho, dono de negócio). O "e se fosse a
  sua mãe?" transforma o tutorial em algo acessível.

### Kevin Stratvert — [YouTube](https://www.youtube.com/@KevinStratvert) · [@kevinstratvert](https://www.instagram.com/kevinstratvert/)
- **Seguidores:** YT 4,46M · IG 924K · TikTok 487,9K.
- **Post:** [Stop Paying for 5 AI Tools (Use This Instead)](https://www.youtube.com/shorts/1fA5j5_5TRY), de 09/03/2026, com 4.699.919 views mas só 1.029 likes e 5 comentários, em 38 s. ✅ transcrito.
  - **Hook literal:** "You don't need separate subscriptions for ChatGPT, Claude, Gemini, slide builders, website builders, and image generators."
  - É um **publi da Genspark**. A proporção de 0,02% de likes indica **views impulsionadas por anúncio**, então não serve de prova de viralidade orgânica.
  - O hook "pare de pagar por X" é ótimo para dono de negócio.
- **Força:** a calma e o passo a passo do canal longo, de fato o maior de tutorial de software.

### Futurepedia — [YouTube @futurepedia_io](https://www.youtube.com/@futurepedia_io)
- **Seguidores:** YT 759K.
- **Post:** [Make AI Writing Sound Actually Human](https://www.youtube.com/shorts/BAE03hKz9Zo), de 07/01/2026, com 3.232.939 views, 2.674 likes e 27 comentários, em 65 s. ✅ transcrito.
  - **Hook literal:** "Have you ever tried using a humanizer for something you wrote with the help of AI?"
  - É um **publi do Grammarly**. A proporção de likes é baixa, então provavelmente teve impulsionamento pago.
  - Orgânico de referência: [6 AI Animation Tools you won't Believe are FREE](https://www.youtube.com/shorts/NVYOpb7umLA) com 358K views.

### Nate Herk · Matt Wolfe · The AI Advantage
- **Nate Herk** ([YT](https://www.youtube.com/@nateherk), 1,07M): [How I Build $10,000 Apple-Style Websites with Claude Code](https://www.youtube.com/shorts/AUoYldwt_sA) com 174K views. Hook de **valor em dinheiro**.
- **Matt Wolfe** ([YT](https://www.youtube.com/@mreflow), 1,02M): [Midjourney Built What?!?](https://www.youtube.com/shorts/Qy25rSEXpPQ) com 337K views. Hook de **surpresa com a novidade**.
- **The AI Advantage** ([YT](https://www.youtube.com/@aiadvantage), 487K): [GPT-6 Astra is Unbelievable](https://www.youtube.com/shorts/GK0LIn0u_qA) com 104K views. Demonstra a ferramenta no dia do lançamento.

### Dot CSV (espanhol) — [YouTube @DotCSV](https://www.youtube.com/@DotCSV)
- **Seguidores:** YT 920K · IG 106K.
- **Força:** é o maior divulgador de IA em língua latina. Prova que explicar IA com rigor e humor funciona fora do
  inglês. Shorts recentes têm pouco volume (o maior com 131K).

### 🇧🇷 Bruno Picinini — [@brunopicinini](https://www.instagram.com/brunopicinini/) · [YouTube](https://www.youtube.com/@brunopicinini)
- **Seguidores:** IG 238K · YT 446K.
- **Posts:** Short "Onde criar agentes de IA" com 123K views ([fSgOJSiQrqw](https://www.youtube.com/shorts/fSgOJSiQrqw); o YouTube exibe o título traduzido). Reel com [CTA "Digite AROS24"](https://www.instagram.com/p/C_neHuEO4B9/) com 1.276 curtidas e **1.021 comentários**: o CTA de palavra-chave gera quase 1 comentário por curtida.
- **Força:** IA aplicada a marketing e vendas para empreendedor, em PT-BR.

### 🇧🇷 Rafael Milagre — [@rafaelmilagre](https://www.instagram.com/rafaelmilagre/)
- **Seguidores:** IG 121K · YT 9,47K.
- **YT:** [tier list das melhores IAs](https://www.youtube.com/shorts/R_OG1bdfwUY) e "Claude Code ou Lovable?", ambos com cerca de 2K views. Os números dos posts no IG não foram confirmados.
- **Força:** comparativo e ranking em PT-BR. É o formato "X vs Y", que gera comentário.

---

## 5. O que a Korvu deve copiar de cada linha

**Para quem estamos adaptando:** o público da Korvu **não é o britânico**. São **portugueses, brasileiros e PALOP que
moram na Europa e no Reino Unido** e não conseguem aprender IA sozinhos pela internet. Eles são o alvo da **imersão
presencial de 1 dia, em português**. Isso muda três coisas em relação aos originais:
1. **O exemplo tem de ser do mundo deles:** o restaurante, o salão, a obra, a limpeza, a contabilidade, o envio de
   dinheiro para casa, a papelada em inglês. Nada de Vale do Silício como exemplo de uso.
2. **A barreira é dupla: a IA e o inglês.** Todo tutorial deve mostrar que dá para falar com a IA **em português**, e
   que ela também resolve o inglês do dia a dia (e-mail ao senhorio, carta do HMRC, conversa com cliente).
3. **O "não consigo sozinho" é a ponte para a imersão.** O CTA do PDF entrega o 1.º passo e o PDF aponta para o
   "venha fazer comigo num dia".

### Linha 1 — Perfis e histórias (até 90 s, narração do Carlos sobre vídeo de arquivo)
| Copiar | De quem | Como fica na Korvu |
|---|---|---|
| **Hook = detalhe absurdo + consequência gigante**, nos primeiros 4 s | Varun Mayya ("0.5 seconds slower… saved the internet") | "Esse homem percebeu um atraso de meio segundo e salvou a internet." Ou: "Ele era funcionário público e hoje toca uma fazenda de 100 hectares com o ChatGPT." |
| **Pessoa comum que prosperou com IA**, narrada sobre as imagens dela | Rowan Cheung (agricultor de brócolis, 90,7K curtidas) | Série "Gente como a gente que usou IA". Prioridade para **imigrantes e pequenos negócios**: é o espelho do público |
| **Estrutura:** quem é → de onde veio → o problema → a virada com IA → **3 usos concretos** → moral | Rowan Cheung, Varun Mayya | Bate com a decisão de 17/09 ("quem é, de onde veio, o que fez → só então a notícia") |
| **Frase-ponte de retenção** a cada ~15 s | Kallaway ("But that's not even the craziest part") | "Mas o mais louco não é isso…", "E aí vem a parte que ninguém conta…" |
| **Rótulo-metáfora fixo na tela** | Kallaway ("UBER EATS FOR SUNLIGHT") | "O DEEPSEEK É O RYANAIR DA IA", sempre com uma referência que o lusófono na Europa conhece |
| **História em linha do tempo com refrão** | Fireship (5,2M views) | "A história da OpenAI em 60 s: 2015… 2019… 2022…", com o ano gigante na tela |
| **Cena gerada por IA quando não há arquivo** | Varun Mayya | Usar só quando não houver vídeo do YouTube, já que a regra de 13/10 diz que o tema com vídeo vence |
| **Moral no fim + CTA** | Rowan ("follow for more") | Moral de 1 frase e **CTA falado de palavra-chave** → PDF com o link do documentário (decisão de 13/10) |
- **Duração:** os virais desta linha têm 73–96 s (Rowan com 73 s, Varun com 92 e 96 s). Confirma o teto de **90 s**.
- **Ritmo:** corte ou troca de imagem a cada 2–4 s e legenda de 2–4 palavras por vez (Rowan).

### Linha 2 — Rápido para salvar e comentar (30–60 s)
| Copiar | De quem | Como fica na Korvu |
|---|---|---|
| **Número + resultado + tempo** no título falado | Greg Isenberg ("10x your Claude with 4 .md files", 833K) | "3 prompts que fazem o seu orçamento em 2 minutos" |
| **"Pare de pagar por X"** | Kevin Stratvert (hook de publi) | "Pare de pagar contabilista para isto: a IA faz em português" |
| **Comparativo A × B** com debate | God of Prompt (Coca-Cola × FedEx), Rafael Milagre (tier list) | "ChatGPT ou Gemini para quem tem negócio em Londres?" ("comenta qual você usa") |
| **CTA de palavra-chave falado + promessa específica** | God of Prompt, Bruno Picinini (1.021 comentários) | "Comenta PROMPT que eu te mando os 10 prompts em PDF." Sempre falado, nunca só na legenda |
| **Notícia no mesmo dia, com "o que muda para você"** | Tiff in Tech, Evolving AI | Para lançamentos grandes, mas **sempre com rosto** (as páginas faceless têm engajamento fraco) |
| **Hook em pergunta** | Tiff in Tech (85K curtidas) | "E se a IA preenchesse a sua papelada do Home Office?" |

### Linha 3 — Tutorial (45–90 s)
| Copiar | De quem | Como fica na Korvu |
|---|---|---|
| **"X explicado em 3 passos/níveis"** + tela preta "NÍVEL 1" | Jeff Su (854K views, 51 s) | "Agente de IA explicado em 3 níveis", com exemplos de agenda e WhatsApp de cliente |
| **"E se fosse a sua mãe?"**: o iniciante absoluto como personagem | Allie K. Miller (706 comentários) | "Se a minha tia que tem um café em Lisboa/Londres quisesse usar IA amanhã, eu faria isto…" |
| **Passo a passo na tela** com a ferramenta real | Kevin Stratvert, AI Advantage | Gravação de tela em português, mostrando o app em PT |
| **Valor em dinheiro no hook** | Nate Herk ("$10,000 websites") | "O site que custaria 2 mil libras, feito em 10 minutos" |
| **Prova social no fim** | Allie ("diretores de RH me disseram…") | "Na nossa última turma, a Dona Fátima saiu com…", somente quando houver caso real |

### Os 5 formatos mais replicáveis (ordem de prioridade)
1. **"Pessoa comum que prosperou com IA"** (Rowan Cheung): narração sobre as imagens da própria pessoa, 70–90 s, com
   moral e CTA. Usa o pipeline atual de perfil sem mudança.
2. **"Pessoa desconhecida por trás de algo enorme"** (Varun Mayya): hook de detalhe absurdo, estrutura de thriller,
   até 90 s.
3. **"X explicado em 3 níveis"** (Jeff Su): 50–60 s, tela preta numerada e exemplos do dia a dia. É o formato que faz
   salvar, e o PDF entrega os 3 níveis com exemplos.
4. **"Número + resultado + tempo" / "Pare de pagar por X"** (Greg Isenberg, Kevin Stratvert): 30–45 s, com CTA de
   palavra-chave falado entregando a lista em PDF.
5. **"História em linha do tempo com refrão"** (Fireship): 50–60 s, ano gigante na tela e punchline final. Formato
   feito para compartilhar.

### O que NÃO copiar
- **Página sem rosto e só de repost** (chatgptricks, theaifield): muito seguidor e pouco engajamento por post. O ativo
  da Korvu é o Carlos.
- **Views de publi impulsionada** (Kevin Stratvert com 4,7M e 1K likes, Futurepedia com 3,2M e 2,7K likes) não são
  referência de viralidade. Medir sempre a proporção de likes e comentários.
- **CTA só na legenda** (God of Prompt 2026: dezenas de comentários). Confirma a decisão de 13/10 de falar o CTA.
- **Documentário lento no vertical** (ColdFusion: 47K views num canal de 5,25M). Na Korvu, o hook tem de vir em
  até 3 s, e não depois de uma introdução.
