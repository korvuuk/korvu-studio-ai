---
status: "calibrado"
calibrado_em: 2026-10-17
amostras_analisadas: 4
amostras: ["2026-10-20-fei-fei-li (texto dele, narrativo, 12 min de fala, sem EDL ainda)", "2026-10-20-geoffrey-hinton (texto dele, narrativo, 8 min de fala)", "2026-09-17-demis-hassabis (roteirista, 60 s)", "2026-09-16-chatgpt-contexto (roteirista, 60 s)"]
wps_roteiro: 2.1
palavras_60s: 125
palavras_90s: 185
wps_medido: {narrativo_hinton_corte: 2.06, narrativo_feifei_takes: 2.11, hassabis: 2.28, chatgpt_dica: 2.66}
muletas: ["E aí (abre frase, 6× no Hinton)", "Só que (3×)", "assim ('pensou assim:', 'faz o seguinte')", "gagueira/recomeço ('a p-a fase', 'aaa')"]
expressoes: ["Pois é.", "olha só que interessante", "E aí vem uma sacada", "Só que aí que tá o problema", "Foi aí que ele…", "Como o cara é fera", "de forma impecável / de forma precisa", "Para poder fazer o quê? …", "o que que aconteceu?", "Comenta a palavra X que eu vou te enviar…", "E também não esquece de mandar pra alguém que…", "é só me seguir e te vejo na próxima", "Foi aí que ela teve uma sacada", "Por que, então, que…?", "E a partir daí…"]
frase_media_palavras: 10
bloco_entre_pausas_palavras: 3-5
---

# Voz do Carlos — perfil calibrado (17/10/2026)

> **Calibrado com 4 gravações reais** (transcrições dos brutos, só as palavras com `locutor: carlos`, comparadas linha a
> linha com o `roteiro.json` e medidas nos takes que a EDL escolheu). Relatórios completos por vídeo em
> `02-calibracao/analises/2026-10-17-*-fala.md`. **Fei-Fei Li (gravada 17/10) somada às 02:10, sem EDL ainda** — quando a EDL
> sair, medir o wps no corte com `comparar_fala.py`.
>
> Este arquivo **tem prioridade sobre `tom-de-voz.md`** em ritmo, muletas e expressões. A §10 ("Para o roteirista") é o
> resumo que o roteirista aplica. Dicionário do ASR (o que o editor lê): `00-marca/fala-carlos.json`.
>
> Amostras: **Fei-Fei** = texto dele (v4), 34 linhas, 12 min de fala bruta, 12 linhas em paráfrase, 0 perdidas (na 2.ª rodada
> do align, 02:04; a 1.ª, de 02:02, perdia 8). **Hinton** = texto escrito por ele (modelo narrativo), 29 linhas, 8 min de fala bruta, 14 linhas ditas em
> paráfrase, 2 perdidas pelo alinhador. **Hassabis** e **ChatGPT** (setembro) = roteiros do roteirista, 60 s, formato picado
> antigo — servem para ver o que ele faz com um texto que não é dele.

---

## 1. Ritmo

| Medida | Hinton (narrativo, texto dele) | Fei-Fei (narrativo, texto dele) | Hassabis (perfil 60 s) | ChatGPT (dica 60 s) |
|---|---|---|---|---|
| Palavras de ROTEIRO por segundo de vídeo final (`palavras_saida / duracao_saida`) | **2,06** (327 / 158,7 s) | — (sem EDL ainda) | 2,28 (132 / 57,8 s) | 2,66 (143 / 53,7 s) |
| Palavras DITAS por segundo no corte (só os takes escolhidos) | 2,00 (2,05 nos takes) | **2,11** nos takes (375 / 177,7 s) | 2,80 | 2,90 |
| Articulação (sem pausas > 0,35 s), mediana por linha | 2,45 | 2,73 | 2,12 | 3,12 |
| Bloco de fala entre pausas (mediana de palavras) | **3** (p25–p75: 2–5) | **3** (2–6) | 6 | 8 |
| Pausa interna típica | 0,50 s (máx. 1,0 s) | 0,54 s (máx. 1,2 s) | 0,69 s | — |

- **`wps_roteiro` = 2,1** para o formato atual (narrativo). 60 s ≈ **125 palavras**; 90 s ≈ **185, no máximo 190**.
  A regra antiga "~190–210 palavras para 90 s" foi estimada com 2,3 wps e estoura: a Fei-Fei v4 tem 331 palavras → ~160 s.
  Dica rápida (formato ChatGPT) corre a ~2,6; vale 2,3 nesse caso.
  **A Fei-Fei confirma**: 2,11 nos takes escolhidos, o mesmo do Hinton (2,05 nos takes → 2,00 no corte). Com 331 palavras
  de roteiro, o corte vai dar ~160 s.
- **Ele desacelera nas frases de impacto** (wps na EDL): L09 "O problema, quase ninguém acreditava" **1,09** · L14 "acabou de
  mudar o rumo da inteligência artificial" 1,26 · L17 "olha só que interessante" 1,30 · L21 "era a comitê do Nobel" 1,26.
  Narração normal 1,8–2,3. **Acelera no gancho e no CTA**: L02 2,26 · L24 2,63 · L22 3,02 · tentativas de CTA 2,6–3,0.
  → Frase de revelação tem de ser **curta** (≤ 6 palavras), porque ele vai gastar 3–4 s nela de qualquer jeito.
- **Onde ele pausa sozinho** (0,5–1,0 s, sem ninguém marcar): depois do conector de abertura ("E aí, //", "Agora, //",
  "E, no final, //", "Pouco depois, //"); entre sujeito e predicado da frase-lição ("uma ideia que ninguém acredita // pode
  mudar o mundo"); antes do detalhe preciso ("uma ligação // às 2:30 da manhã", "era a comitê // do Nobel"); depois da data
  ("Em 2023, // ele…", "Nos anos 70, // ele…"). O `[pausa]` do roteiro só é preciso onde se quer **mais** que isso.
- Em narrativa ele fala em **blocos de 3–5 palavras**: o respiro ` / ` do teleprompter deve vir a cada 4–6 palavras, não só
  nas linhas de 12+.

## 2. Muletas

| Muleta | Onde aparece | Decisão |
|---|---|---|
| **"E aí"** no começo da frase | 6× no Hinton ("E aí, em 2012…", "E aí vem uma sacada", "E aí ele começou a pensar assim") | É conector dele, não vício: **pode entrar no roteiro, até 3× por vídeo**; o editor não corta |
| **"Só que"** | 3× ("Só que aí que tá o problema", "Só que o problema, quase ninguém acreditava") | Conector de desafio; usar em vez de "O problema é que" quando couber |
| "assim" como dois-pontos | "Ele pensou assim: e se…", "Pensa assim, imagina que…", "Faz o seguinte:" | Jeito dele de abrir uma explicação; permitido |
| "é", "ã", "hum" soltos | quase inexistentes dentro das frases (o "é" contado é o verbo) | Nada a fazer |
| Gagueira / recomeço | "a p-a fase", "Vamos repetir aaa, a linha", "Não, não, não, não" | Fala dele (gago). O editor junta ou apara; **nunca** descarta o take por isso |
| "Calma, calma, calma", "Próxima", "Pode avançar", "Repete", "Vambora" | só dirigido ao ChatGPT Voz | Nunca é conteúdo; candidatas a separador no `common.py` |

## 3. Expressões características (ditas por ele, não escritas pelo roteirista)

| Expressão | Contexto real | Usar em roteiro? |
|---|---|---|
| "Pois é." | L03, dito exatamente como escrito | Sim (já é do modelo) |
| "olha só que interessante" | L17 — o roteiro dizia "Mas olha que interessante…"; ele tirou o "Mas" e pôs o "só" | Sim, com "só" |
| "E aí vem uma sacada." | improviso antes da L13 (a virada) | Sim, na virada |
| "Só que aí que tá o problema." | improviso na L09 (o desafio) | Sim, no desafio |
| "Como o cara é fera, ele simplesmente não desistiu." | improviso na L11 ("Mas Hinton não desistiu") — **o alinhador perdeu a linha** | Sim — e escrever já assim, senão some |
| "Foi aí que ele…" | abertura da L14 | Sim |
| "de forma impecável" / "de forma precisa" | L13, 3 takes: ele nunca disse "com uma precisão impressionante" | Preferir "de forma + adjetivo" a "com uma + substantivo" |
| "Para poder fazer o quê? Falar dos riscos…" · "o que que aconteceu? Ele recebeu uma ligação" | L19-T1, L20-T1: pergunta-resposta como ênfase | Sim, 1–2× por vídeo, no clímax |
| "Comenta a palavra NOBEL que eu vou te enviar a entrevista completa." | CTA do Hinton, 4 tentativas, sempre assim | **Escrever o CTA neste formato** (ver §10) |
| "E também não esquece de mandar pra alguém que tá querendo desistir duma grande ideia." | L29 | Sim: "E também não esquece de…" |
| "é só me seguir e te vejo na próxima" | fecho dos dois vídeos de setembro, acrescentado por ele | Fecho padrão quando houver CTA de seguir |
| "Pensa assim, imagina que você tem…" | ChatGPT L06 | Sim, para explicação |
| "Foi aí que ela teve uma sacada." | Fei-Fei, improviso antes da L12 (3×) — o mesmo gesto do Hinton ("E aí vem uma sacada") | Sim, na virada |
| "Por que, então, que um computador não pode fazer o mesmo?" | Fei-Fei L12 (3 tentativas): a pergunta dele é com "por que que" | Sim, pergunta com "por que que" |
| "Ninguém mais do que o Geoffrey Hinton. Foi a pessoa que eu falei no vídeo passado." | Fei-Fei L21, improviso em cima de "de quem eu já falei aqui" | Ponte entre vídeos: escrever "de quem eu já falei aqui" e deixar ele completar |
| "E a partir daí, ela…" | Fei-Fei L10 (o roteiro dizia "E ela começou…") | Sim, como transição |
| "Caramba." | Fei-Fei L29, 2× — quando a frase não sai | Nunca é conteúdo: sinal de linha longa demais |

## 4. Como ele reescreve o que lê (roteiro × dito) — padrões com exemplo

Mesmo lendo **o próprio texto** (Hinton), 14 de 29 linhas saíram em paráfrase (`sim` < 0,80). Os padrões, todos com
linha citada (relatório completo em `02-calibracao/analises/`):

| Padrão | Roteiro escreveu | Ele disse |
|---|---|---|
| **Põe o sujeito** ("ele", "o + nome") | L07 "Nos anos 70, começou a defender…" · L12 "junto com dois alunos" · L16 "E Hinton passou" · L23 "Hoje, Geoffrey Hinton é" | "Nos anos 70, **ele** começou…" · "**ele juntou** com dois alunos" · "E **o** Hinton passou" · "**o** Geoffrey Hinton é" |
| **Expande o telegráfico em frase inteira** | ChatGPT L06 "Pensa no prompt assim: recado pra funcionário novo, no primeiro dia." · Hassabis L06 "o Google comprou por cerca de 400 milhões" | "Pensa assim, imagina que você tem um funcionário novo e você precisa passar um recado para ele no primeiro dia." · "o Google comprou **a empresa dele** por 400 milhões" |
| **Troca subjuntivo/condicional por infinitivo e presente** | L10 "aconselhou que abandonasse essa pesquisa, porque poderia destruir sua carreira" · L08 "E se a gente conseguisse criar máquinas capazes de aprender como o cérebro humano?" | "aconselhou **ele a abandonar** essa pesquisa, porque essa pesquisa **pode comprometer a carreira dele**" · "e se a gente **criasse uma máquina** humana **que conseguiria imitar** o cérebro humano?" |
| **"dele/dela" em vez de "seu/sua"** | L10 "sua carreira" · L25 "os seus riscos" | "a carreira dele" · "os riscos" |
| **Corta "é que"** | L09 "O problema é que quase ninguém…" · L24 "E o mais curioso é que o homem…" | "O problema, quase ninguém acreditava" · "E o mais curioso, o homem que…" |
| **Corta intensificador e advérbio de tempo** | L01 "quase 50 anos" · L07 "naquela época" · L14 "mudou **completamente**" · L09 "acreditava **nisso**" · L13 "com uma precisão **impressionante**" | "50 anos" · (nada) · "acabou de mudar" · "acreditava" · "de forma precisa" |
| **"acabou de" / "acabou + gerúndio" como passado** (4× num vídeo) | L14 "Aquilo mudou" · L15 "o Google comprou a empresa que eles tinham criado" · L18 "ele deixou o Google" | "**acabou de** mudar" · "o Google **acabou de** comprar a empresa que eles **acabaram de** criar" · "ele **acabou deixando** o Google" |
| **Simplifica o plural/comparativo** | L25 "um dos que mais alertam" · L16 "a gigante" | "o que mais alerta" · "gigantes" |
| **Passado na narração** | L06 "como funciona a mente humana" · L05 "muita gente imagina" | "como funciona**va**" · "muitas pessoas imagina**vam**" |
| **"muita gente" → "muitas pessoas"; "Mas" → "Porém"** (2 takes) | L05 "Mas, diferente do que muita gente imagina" | "Porém, diferente que muitas pessoas imaginavam" |
| **Embeleza o número** | L20 "às duas da manhã" · L16 "10 anos" | "às 2:30 da manhã" · "mais de 10 anos" |
| **CTA no formato dele** | L28 "Comenta NOBEL que eu te mando o link oficial da entrevista dele." · Hassabis L13 "Para mais vídeos como esse, é só me seguir." | "Comenta **a palavra** Nobel que eu **vou te enviar** a entrevista completa sobre o Geoffrey Hinton." · "Para mais **conteúdos** como esse, é só me seguir **e te vejo na próxima**." |
| **Abre com conector próprio** | L12 "Em 2012" · L14 "Aquilo" · L23 "Hoje" | "**E aí**, em 2012" · "**Foi aí que** ele" · "**E hoje**, o Geoffrey" |
| **"ela" (a IA) vira "ele"** | ChatGPT L05 "É que ela não conhece o seu café" | "O problema é que **ele** não conhece o seu café" |
| **Pergunta retórica com resposta de uma palavra vira afirmação** | Fei-Fei L06–L07 "…quem atendia o telefone, resolvia cobrança e até falava com o fiscal? / Ela." | "…**ela é que** atendia telefone e até falava com os fiscais" (2 takes); o "Ela." sozinho só saiu quando a IA o leu isolado |
| **Aposto no meio da frase vai para o começo** | Fei-Fei L08 "E foi assim, ela conta, que ajudou a pagar a faculdade." | "E foi assim, **ela contou que** foi assim que ela ajudou a pagar as faculdade." |
| **"e depois" vira "e foi aí que ela"** | Fei-Fei L09 "estudou física em Princeton e depois entrou para o mundo da inteligência artificial" | "estudou Física em Princeton **e foi aí que ela** entrou…" (4 takes, sempre assim) |
| **Lista de 3 itens numa frase não sai** | Fei-Fei L29 "teve o trabalho de mostrar exemplos, organizar informação e ensinar o que cada coisa significa" (20 palavras) | 6 tentativas em 3 arquivos, nenhuma inteira ("…ensinar cada coisa", "…organizar essas ideias, ensinar cada coisa", "Caramba"); melhor sim 0,53 |
| **"quase" vira "mais de" (o dado muda)** | Fei-Fei L15 "quase 50 mil pessoas" | "**mais de** 50 mil pessoas" (2 de 4 takes); "pela internet" muda de lugar |
| **Troca o verbo abstrato pelo concreto** | Fei-Fei L11 "vendo milhões de exemplos" · L14 "dizer ao computador exatamente o que aparecia" · L22 "ajudou a mudar" | "**através de** milhões de exemplos" (4 de 6 takes) · "**passar para o** computador reconhecer" · "**começou a** mudar" |
| **"numa" → "em uma"; "aos" → "nos"; "seria" → "deveria ser"** | Fei-Fei L10/L19 "numa" · L04 "aos Estados Unidos" · L12 "seria diferente" | "em uma coisa", "em uma competição" · "nos Estados Unidos" · "deveria ser diferente" |
| **"IA" sem artigo não sai** | Fei-Fei L28 "IA não aprende por mágica." | "As AI não aprende…" / "A inteligência artificial não aprende…" / "não aprende por mágica" (3 takes) |
| **CTA: "no seu direct", "te envio", e o material vira "entrevista"** | Fei-Fei L32 "Comenta AULA aqui embaixo que eu te mando a palestra dela." | "Comenta 'aula' aqui embaixo, eu **vou te enviar no seu direct** a **entrevista completa** sobre a Fei-Fei Li" (3 takes — o PDF é a palestra TED; ele disse "entrevista" nas 3) |
| **Lê o ano errado quando os dígitos se parecem** | Fei-Fei L13 "Em 2007" | "Em 2027" (2 takes) antes de acertar |

O que ele **mantém igual** quando lê: frases curtas e inteiras com sujeito explícito (L06, L19, L26, L27 saíram 1,00);
"Pois é"; "Imagina você…"; datas em algarismo; "a gente"; "pra" quando escrito (L29), embora leia "para" em metade
das vezes (ChatGPT L03, L04, L07).

## 5. Estrutura de frase

- **Tamanho:** ~10 palavras por linha dita (Hinton: 272 palavras em 27 linhas; ~11 nos vídeos de setembro). Dentro da linha, blocos de 3–5
  palavras entre pausas (narrativo). Frase de impacto: 4–6 palavras ("Era o comitê do Nobel.", "Só que aí que tá o problema.").
- **Começa frases com** (takes escolhidos do Hinton): "E" ×5 ("E aí", "E hoje", "E o mais curioso"), "Imagina" ×3,
  "Ele" ×3, "o" + nome ×3, "Em" + ano ×2, "Pois é", "Só que", "Agora,", "Foi aí que", "Pouco depois". Na Fei-Fei: "E" ×6, "Imagina" ×3, "Então", "Aí chega",
  "E a partir daí"; "Foi aí que" 7× no bruto.
- **Perguntas retóricas:** sim, do tipo pergunta-resposta imediata ("Para poder fazer o quê? Falar dos riscos…";
  "o que que aconteceu? Ele recebeu uma ligação"). 1–2 por vídeo, no clímax.
- **"você" / "a gente" / "meu amigo":** "você" e "a gente" sim ("e se a gente criasse…", "imagina que você tem…").
  **"meu amigo" nunca apareceu** nas 4 gravações — não escrever.
- Terceira pessoa **sempre com artigo**: "o Hinton", "o Geoffrey Hinton", "a empresa dele".

## 6. Pronúncia e termos

| Termo | Como o Carlos fala | O que o ASR escreve | Observação |
|---|---|---|---|
| ChatGPT | "chat GPT", duas palavras | "chat GPT", "CHPT" | dicionário: `chpt`, `gpt` → chatgpt |
| prompt | "pronto"/"promp" (come o fim) | "pronto", "promp" | dicionário (desde 17/09) |
| IA | "IA" **e também "AI"** em inglês (Hassabis ×3, ChatGPT ×1) | "AI", "E.A.", "a EA e", "ZAI" | dicionário só com `zai`, `ea` (ver `_formato` do JSON); legenda segue o roteiro |
| Nomes | "Geoffreys Hinton", "Denis Assabi", "alfa fold", "DeepMine", "ImageMed" (ImageNet) | idem | dicionário: geoffreys, denis, assabi(s), deepmine, imagemed |
| Palavra-chave do CTA | NOBEL sempre "a palavra Nobel"; AULA saiu "aula" 2× e "aulas" 1× | "aulas" | dicionário: aulas → aula; o editor confere a palavra do CTA nos 3 takes |
| Números | lê algarismo; "2:30 da manhã" por "duas"; "mais de 10" por "10"; "mais de 50 mil" por "quase 50 mil"; **2007 lido como 2027** (2 takes) | "2:30" (vira "duzentos e trinta" no alinhador) | número que importa para a fonte: escrever exato e em **negrito** |
| Contrações | "duma", "pro", "pra" (e "para"), "tá", "tô" | "duma", "pro" | `duma`/`dum` ainda não estão em `CONTRACOES` (common.py) — pendente |
| Concordância | "uma sistema", "as imagem", "a comitê", "entrevista completo", "tinha acabado de ganhado" | idem | jeito dele; take válido; legenda segue o roteiro |

## 7. Energia e tom

- **Narrativa (Hinton): grave, pausado, 2,0 wps**, com a voz caindo antes do clímax. É onde ele soa melhor: as linhas da
  reflexão (L26, L27) saíram iguais ao texto, sem tropeço. **Dica (ChatGPT): 3+ wps**, mais aceso, mais improviso.
- **Soa natural:** o que ele acrescenta por conta própria — "Como o cara é fera", "E aí vem uma sacada", "Só que aí que tá o
  problema", "Para poder fazer o quê?". Improviso **é melhor** que o texto na maioria das vezes (decisão de 17/10).
- **Soa forçado / ele tropeça:** subjuntivo e oração subordinada longa (L10 teve 1 take, reescrito), "um dos que mais
  alertam" (virou "o que mais alerta"), nomes estrangeiros ("Hassabis" 3 tentativas, "AlphaFold" 6 takes), frase telegráfica
  sem verbo (ele reconstrói a frase e perde tempo — ChatGPT L06, 5,6 s para 20 palavras), número por extenso, **lista de 3 itens numa frase** (Fei-Fei L29: 6 tentativas,
  nenhuma inteira) e **linha de uma palavra como resposta** (Fei-Fei L07 "Ela.").

## 8. Trechos de referência (transcritos, voz real)

1. *"Só que aí que tá o problema. As pessoas não acreditavam nessa ideia."* (Hinton, improviso na L09)
2. *"E aí, o mais curioso, o próprio orientador dele aconselhou ele a abandonar essa pesquisa, porque essa pesquisa pode
   comprometer a carreira dele."* (Hinton L10 — a frase do roteiro reconstruída do jeito dele)
3. *"Como o cara é fera, ele simplesmente não desistiu. E aí, em 2012, ele juntou com dois alunos. E aí vem uma sacada."*
   (Hinton L11–L13)
4. *"Para poder fazer o quê? Falar dos riscos da inteligência artificial de forma mais livre. E um ano e meio depois, o que
   que aconteceu? Ele recebeu uma ligação às 2:30 da manhã."* (Hinton L19–L20, primeiros takes)
5. *"Comenta a palavra Nobel que eu vou te enviar a entrevista completa sobre o Geoffrey Hinton. E também não esquece de
   mandar pra alguém que tá querendo desistir duma grande ideia."* (Hinton CTA)
6. *"Pensa assim, imagina que você tem um funcionário novo e você precisa passar um recado para ele no primeiro dia."*
   (ChatGPT L06 — o roteiro dizia "Pensa no prompt assim: recado pra funcionário novo, no primeiro dia.")
7. *"Então, na lavanderia da família, ela atendia os telefone e fazia as cobranças e até atendia os fiscais. Ela. E foi
   assim, ela contou que foi assim que ela ajudou a pagar as faculdade."* (Fei-Fei L06–L08)
8. *"Fei-Fei estudou Física em Princeton e foi aí que ela entrou para o mundo da inteligência artificial. E a partir daí,
   ela começou a pensar em uma coisa muito simples."* (Fei-Fei L09–L10)
9. *"Foi aí que ela teve uma sacada. Por que, então, que um computador não pode fazer o mesmo?"* (Fei-Fei, improviso na L12)
10. *"Comenta aula aqui embaixo, eu vou te enviar no seu direct a entrevista completa sobre a Fei-Fei Li."* (Fei-Fei CTA)

## 9. Diferenças em relação ao `tom-de-voz.md`

| Regra do tom-de-voz | O que a voz real mostra | Decisão |
|---|---|---|
| Ritmo 2,3 wps (138 palavras / 60 s) | 2,06 em narrativa; 2,66 em dica | **2,1** no narrativo (125 / 60 s · 185 / 90 s); 2,3 só em dica rápida |
| "pra", nunca "para" | lê "para" em metade das vezes (ChatGPT L03/L04/L07) | Escrever "pra"; não contar com isso para o tamanho |
| "Meu amigo", "Mentira.", "Calma." como assinatura | nunca ditos como conteúdo ("Calma" só para a IA) | Tirar da lista de assinaturas |
| "Olha só" / "Olha que interessante" | diz "olha **só** que interessante" | Manter com "só" |
| Marcar `[pausa]` 2–4× por roteiro | ele pausa sozinho 0,5–1,0 s nos pontos da §1 | `[pausa]` só para a pausa **longa** (> 1 s) |
| Linhas ≤ 12 palavras | ele fala em blocos de 3–5; linhas de 14–17 palavras custam vários takes ou saem com o final cortado (L02: 5 takes; L15: final cortado) | Linha ≤ 12 **e** respiro ` / ` a cada 4–6 palavras |
| Frases telegráficas como ênfase | ele reconstrói a frase inteira e tropeça (ChatGPT L06, L08) | Já é regra desde 14/10: frase inteira, com sujeito e verbo |

## 10. Para o roteirista — 8 regras tiradas das gravações

1. **Escreva a frase com sujeito e verbo, do jeito que ele vai dizer.** Ele acrescenta "ele"/"o Hinton" e reconstrói o
   telegráfico. Texto sem sujeito custa um take a mais (L07, L12, ChatGPT L06).
2. **Nada de subjuntivo nem condicional encadeado.** "que abandonasse… porque poderia destruir sua carreira" virou
   "ele a abandonar… porque pode comprometer a carreira dele". Use infinitivo, presente e "dele/dela" no lugar de "seu/sua".
3. **Corte o "é que" e o intensificador antes dele cortar.** "O problema é que" → "O problema," · "E o mais curioso é que"
   → "E o mais curioso," · "mudou completamente" → "mudou" · "com uma precisão impressionante" → "de forma precisa".
   Deixe só o adjetivo que sobrevive na boca dele.
4. **Use os conectores dele, não os do manual:** "E aí" (até 3×), "Só que", "Agora,", "Foi aí que", "Pois é.",
   "olha só que interessante", "Pouco depois", "E hoje". "Mas" ele às vezes lê "Porém" — os dois valem.
5. **Clímax em pergunta-resposta, 1–2× por vídeo:** "Para poder fazer o quê? Falar dos riscos…" / "E aí, o que que
   aconteceu? Ele recebeu uma ligação às 2:30 da manhã." É o momento em que ele mais acelera e mais acerta. Mas **nunca uma linha de uma palavra como resposta** ("…falava com
   o fiscal? / Ela."): ele diz a afirmação inteira ("ela é que atendia…"), e o "Ela." sozinho confundiu o alinhador
   (27 takes na 1.ª rodada da Fei-Fei).
6. **CTA no formato que ele diz, senão o editor perde a linha** (Hinton L28: sim 0,25):
   "Comenta **a palavra** NOBEL que eu **vou te enviar no seu direct** [o material]." O nome do material tem de ser o que
   ele diz: na Fei-Fei o PDF era a palestra e ele disse "entrevista completa" 3× — escrever "a palestra completa dela" em
   **negrito** ou aceitar "entrevista" e ajustar o PDF/legenda. + "E também não esquece de mandar pra alguém
   que…" + (se houver seguir) "é só me seguir e te vejo na próxima."
7. **Tamanho: 2,1 palavras por segundo de vídeo.** 90 s = 185 palavras, nunca mais de 190. Frase de impacto com ≤ 6
   palavras (ele gasta 3–4 s nela a 1,1–1,3 wps). Linhas ≤ 12 palavras com ` / ` a cada 4–6. **Nunca 3 itens numa frase**: a L29 da Fei-Fei (20 palavras, 3 itens) não
   saiu em 6 tentativas — no máximo 2 itens por frase, ou uma frase por item.
8. **Não escreva "acabou de", "mais de", "2:30":** ele põe sozinho ("acabou de mudar", "mais de 10 anos", "às 2:30").
   Escrever "acabou de" dá "acabou de acabar". O número que importa (ano, valor, fonte) vai exato e em **negrito**; o
   resto ele arredonda e tudo bem. Cuidado com "quase": "quase 50 mil" virou "mais de 50 mil" — se o número tem teto,
   escrever "cerca de" ou o número exato. Anos com dígitos parecidos (2007) ele lê errado (2027): pôr o ano em **negrito**.

**Para o editor (`align.py` / editor-de-video), o que estas gravações ensinaram:** (a) improviso que troca quase todas as
palavras não é achado pelo `sem_ancora` e a linha some (Hinton L11, L28) — antes de dar `faltando`, olhar o `nao_mapeado`
da mesma região por palavra-chave da linha ("desistiu", a palavra do CTA); (b) o dicionário só aceita chave de uma
palavra (bug `a → ia` corrigido em 17/10); (c) separadores que ele usa e o `common.py` não conhece: "Próxima",
"Pode avançar", "Continua", "Calma, calma, calma", "Vamos repetir"; (d) **linha de 1–2 palavras**: na Fei-Fei a L07 "Ela."
ficou com 27 takes na 1.ª rodada do align (02:02) e 8 linhas ditas ficaram `faltando`; a rodada de 02:04 resolveu (0 faltando)
— conferir sempre que uma linha tiver 1–2 palavras; (e) o CTA da Fei-Fei atravessa dois arquivos da câmera (praq0992 → praq0993):
a L32 ficou `final_cortado`.

## 11. Histórico de calibração

| Data | Amostras | O que mudou |
|---|---|---|
| 2026-09-15 | 0 | Arquivo criado como modelo (não calibrado) |
| 2026-10-17 | 4 (Fei-Fei 12 min · Hinton 8 min · Hassabis 6 min · ChatGPT 3 min de fala bruta) | Primeira calibração, com transcrições dos brutos em vez de amostra livre. `wps_roteiro` 2,3 → **2,1** (Hinton 2,06 no corte; Fei-Fei 2,11 nos takes); muletas, expressões, 23 padrões de reescrita com exemplo, §10 para o roteirista. `fala-carlos.json`: bug `a i` removido, 14 entradas novas. Pendente: wps da Fei-Fei no corte quando a EDL existir |
