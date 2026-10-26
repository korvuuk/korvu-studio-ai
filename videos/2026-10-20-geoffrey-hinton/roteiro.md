---
slug: 2026-10-20-geoffrey-hinton
tema: "Quem é Geoffrey Hinton: quase 50 anos numa ideia que ninguém levava a sério, até ela mudar o mundo e virar um Nobel"
pilar: perfil
estrutura: "narrativo (00-marca/modelo-roteiro-narrativo.md): gancho → história → desafio → revolução → Nobel → reflexão → CTA"
hook_template: curiosity-gap
publico: ambos
duracao_alvo: 90
palavras_alvo: 200
wps_ref: 2.3
hooks:
  A: {fala: "Imagina você passar quase 50 anos acreditando numa ideia que ninguém levava a sério…", tela: "50 ANOS NUMA IDEIA QUE NINGUÉM LEVAVA A SÉRIO", visual: "Carlos em tela cheia; o Hinton só aparece na L03"}
  B: {fala: "Imagina ouvir que a sua ideia vai acabar com a sua carreira…", tela: "\"ISSO VAI ACABAR COM A SUA CARREIRA\"", visual: "Carlos em tela cheia; o Hinton só aparece na L03"}
  C: {fala: "Imagina você defender uma ideia que todo mundo achava impossível…", tela: "TODO MUNDO ACHAVA IMPOSSÍVEL", visual: "Carlos em tela cheia; o Hinton só aparece na L03"}
hook_escolhido: A
titulo: {contexto: "Ninguém levava a ideia dele a sério,", impacto: "e ela virou um Nobel", cinza: 2, rabisco: "Nobel"}
pose_capa: "braços cruzados, olhar firme na câmera"
cta_tipo: palavra-material
cta_palavra: NOBEL
material: "PDF de 2 páginas com o link oficial da entrevista do Geoffrey Hinton ao 60 Minutes (CBS, 13 min, em inglês), como ligar a tradução automática da legenda no YouTube e o link da transcrição em inglês da CBS"
material_titulo: "o link da entrevista do Hinton"
fontes:
  - "https://www.youtube.com/watch?v=qrvK_KuIeJk"
  - "https://www.cbsnews.com/news/geoffrey-hinton-ai-dangers-60-minutes-transcript/"
  - "https://www.nobelprize.org/prizes/physics/2024/hinton/facts/"
  - "https://www.nobelprize.org/prizes/physics/2024/hinton/interview/"
  - "https://www.nobelprize.org/prizes/physics/2024/hinton/speech/"
  - "https://fortune.com/2024/10/09/openai-sam-altman-geoffrey-hinton-nobel-prize-physics-ilya-sutskever-toronto"
  - "https://image-net.org/challenges/LSVRC/2012/results.html"
  - "https://computerhistory.org/blog/chm-releases-alexnet-source-code/"
  - "https://www.technologyreview.com/2023/05/01/1072478/deep-learning-pioneer-geoffrey-hinton-quits-google/"
  - "https://ny1.com/nyc/all-boroughs/ap-top-news/2023/05/02/godfather-of-ai-leaves-google-warns-of-techs-dangers"
  - "https://en.wikipedia.org/wiki/Geoffrey_Hinton"
status: rascunho
versao: 3
---

# Quem é Geoffrey Hinton

> **Versão 3 (14/10): o texto é do Carlos** (`00-marca/modelo-roteiro-narrativo.md`, exemplo do Hinton), quase literal.
> A v2 foi reprovada por ele: "engessada, picada, sem emoção". Mudanças no texto dele, todas de forma, nenhuma de conteúdo:
> "comité" → "comitê"; números por extenso para a leitura (1947 → "1947", anos 70 →
> "anos 70", 2012/2023/2024 por extenso, 50 → "cinquenta"; regra de `tom-de-voz.md`); duas frases longas
> partidas em duas linhas na vírgula (L12/L13 e L18/L19), para caber na repetição da gravação. Acrescentado: o CTA falado (L28–L29).
> Base factual: `material/dossie.md` + `material/fontes.json`. Pronúncia: **"Jéf-ri Hín-ton"**.
>
> **Blocos do modelo → seção do parser** (o `parse_roteiro.py` só aceita hook/promessa/corpo/payoff/cta/hook-alt):
> GANCHO = L01 (hook) + L02–L03 (promessa) · A HISTÓRIA = L04–L08 · O DESAFIO = L09–L11 · A REVOLUÇÃO = L12–L16 ·
> O NOBEL = L17–L22 (história, desafio, revolução e Nobel = `corpo`) · REFLEXÃO = L23–L27 (`payoff`) · CTA = L28–L29.

## Roteiro

> **PAUSA DA CAPA (antes de falar qualquer coisa).** Fique **parado 3 segundos** olhando para a câmera, em silêncio:
> boca fechada, **braços cruzados, olhar firme na câmera** (`pose_capa`), sem movimento. É desse trecho que sai o
> frame da capa do feed. O ChatGPT Voz lê essa linha em voz alta antes da L01.

| ID | Seção | FALA |
|---|---|---|
| L01 | hook | Imagina você passar quase 50 anos / acreditando numa ideia / que ninguém levava a **sério**… |
| L02 | promessa | E, no final, / essa ideia mudar o mundo / e ainda te dar um **Prêmio Nobel**. [pausa] |
| L03 | promessa | Pois é. / Essa é a história de **Geoffrey Hinton**. |
| L04 | corpo | Hinton nasceu em Londres, / em 1947, / numa família de **cientistas**. |
| L05 | corpo | Mas, diferente do que muita gente imagina, / ele não começou estudando **computadores**. |
| L06 | corpo | Ele queria entender / como funciona a **mente humana**. |
| L07 | corpo | Nos anos 70, / começou a defender uma ideia / que parecia **impossível** naquela época: |
| L08 | corpo | E se a gente conseguisse criar máquinas / capazes de aprender / como o **cérebro humano**? [pausa] |
| L09 | corpo | O problema é que / quase **ninguém** acreditava nisso. |
| L10 | corpo | Até o próprio **orientador** dele / aconselhou que abandonasse essa pesquisa, / porque poderia destruir sua carreira. |
| L11 | corpo | Mas Hinton **não desistiu**. [pausa] |
| L12 | corpo | Em 2012, / junto com dois alunos, |
| L13 | corpo | ele desenvolveu um sistema capaz de **reconhecer imagens** / com uma precisão impressionante. |
| L14 | corpo | Aquilo mudou completamente / o rumo da **inteligência artificial**. |
| L15 | corpo | Pouco depois, / o **Google** comprou a empresa que eles tinham criado. |
| L16 | corpo | E Hinton passou **10 anos** / trabalhando com a gigante da tecnologia. |
| L17 | corpo | Mas olha que interessante… [pausa] |
| L18 | corpo | Em 2023, / ele **deixou o Google** |
| L19 | corpo | para poder falar livremente / sobre os **riscos** da inteligência artificial. |
| L20 | corpo | E, um ano e meio depois, / recebeu uma ligação / às **duas da manhã**. [pausa] |
| L21 | corpo | Era o comitê do **Nobel**. |
| L22 | corpo | Ele tinha acabado de ganhar / o **Nobel de Física** de 2024. [pausa] |
| L23 | payoff | Hoje, Geoffrey Hinton é conhecido / como o **padrinho da inteligência artificial**. |
| L24 | payoff | E o mais curioso é que / o homem que ajudou a desenvolver essa tecnologia |
| L25 | payoff | é também um dos que mais **alertam** / sobre os seus riscos. |
| L26 | payoff | A história dele mostra uma coisa: [pausa] |
| L27 | payoff | Às vezes, / uma ideia que ninguém acredita / pode **mudar o mundo**. [pausa longa] |
| L28 | cta | Comenta **NOBEL** / que eu te mando o link oficial da entrevista dele. |
| L29 | cta | E manda pra alguém / que tá **desistindo** de uma ideia. |
| L01B | hook-alt | Imagina ouvir que a sua ideia / vai acabar com a sua **carreira**… |
| L01C | hook-alt | Imagina você defender uma ideia / que todo mundo achava **impossível**… |

## Cenas extras

> **Formato narração por cima** (decisão de 14/10): o vídeo do Hinton corre por baixo da fala do Carlos, com o
> **áudio original baixo ou mudo** e **crédito na tela**, sem teto de tempo. Todos os trechos de vídeo **já estão
> cortados** em `brutos/extras/` (origem em `material/youtube/catalogo.md`).
> **Faixas contínuas, corte seco entre extras encostados:** faixa 1 = L03–L04 · faixa 2 = L07–L13 · faixa 3 = L15 ·
> faixa 4 = L18–L25. **Carlos em tela cheia** (de propósito, é onde a emoção está na cara dele): L01–L02 (gancho),
> L05–L06, L14, L16–L17 ("Mas olha que interessante…"), L26–L27 (a lição) e **L28–L29 (CTA, regra rígida 6)**.
> Trechos mais curtos que as linhas (E07, E10): o editor ajusta o fim da faixa ao corte de fala mais próximo,
> nunca com o extra "subindo e descendo" no meio da frase.

| ID | Tipo | O que mostrar | Como obter / fonte | Crédito | Som | Linhas |
|---|---|---|---|---|---|---|
| E02 | video | Hinton de frente, calmo, respondendo no começo da entrevista (13 s), entra na hora do nome | `brutos/extras/E02-hinton-abertura.mp4` (60 Minutes 0:50–1:03) | 60 Minutes / CBS News | não | L03, L04 |
| E03 | video | Fotos em preto e branco do jovem Hinton (anos 70, Edimburgo), enquanto a CBS conta a ideia do cérebro (9 s) | `brutos/extras/E03-edimburgo-jovem.mp4` (60 Minutes 1:49–1:58) | 60 Minutes / CBS News | não | L07 |
| E04 | animacao | A pergunta da L08 em imagem: pontos ligados em camadas, como neurônios; a cada exemplo a ligação certa engrossa e a errada some. Na L09, as ligações apagam devagar (ninguém acreditava). Sem escrever "rede neural" na tela | Claude Design (brief do animador, `00-marca/design-system/korvu-video.md`) — **refazer o brief**: a "trilha no mato" da v2 saiu do texto | — | não | L08, L09 |
| E05 | video | Rosto do jovem Hinton e ele diante do computador; a CBS conta que o orientador mandou largar (7,5 s) | `brutos/extras/E05-orientador.mp4` (60 Minutes 2:04–2:12) | 60 Minutes / CBS News | não | L10 |
| E12 | video | Hinton: "I always thought I was right" (3,1 s, rosto dele na hora da frase) — casa com "não desistiu" | `brutos/extras/E12-sempre-achei-certo.mp4` (60 Minutes 2:36–2:39) | 60 Minutes / CBS News | não | L11 |
| E06 | animacao | Duas barras de erro na competição de 2012: segundo colocado 26,2 % × o sistema dele 15,3 %; a dele encolhe na fala "precisão impressionante" (os números só na tela, a fala não diz) | Claude Design; números da tabela oficial (ImageNet 2012: 0,15315 × 0,26172) | ImageNet / Stanford Vision Lab (dado) | não | L12, L13 |
| E07 | video | Hinton de suéter verde e de pé na sala de servidores (5,2 s, sem logo do Google) | `brutos/extras/E07-google-toronto.mp4` (60 Minutes 7:33–7:38) | 60 Minutes / CBS News | não | L15 |
| E08 | video | Hinton, calmo, falando do ritmo do progresso da IA, entrevista à BBC quando saiu do Google (10 s; tarja da BBC no rodapé) | `brutos/extras/E08-riscos-bbc.mp4` (BBC News 1:19–1:29) | BBC News | não | L18, L19 |
| E01 | animacao | Tela de celular recebendo ligação de madrugada: "02:00", tocando, vibrando no escuro (toda a L20). Sem nome de pessoa nem número real na tela | Claude Design (brief do animador, `00-marca/design-system/korvu-video.md`) — **atualizar o brief**: na v2 era 1 s no hook, agora cobre a L20 inteira | — | não | L20 |
| E09 | video | Hinton conta a ligação do Nobel: "could be a prank" (8 s), em corte seco depois do E01 | `brutos/extras/E09-ligacao-trote.mp4` (Nobel Prize, entrevista oficial 0:57–1:05) | NobelPrize.org | não | L21, L22 |
| E10 | video | Hinton no discurso do banquete do Nobel, de casaca, no trecho da produtividade (7,5 s) — o "padrinho" no palco | `brutos/extras/E10-banquete-produtividade.mp4` (Nobel Prize, discurso 1:31–1:38) | NobelPrize.org | não | L23, L24 |
| E11 | video | Hinton no discurso do banquete, no trecho dos riscos/phishing (6 s), em corte seco depois do E10 | `brutos/extras/E11-banquete-golpes.mp4` (Nobel Prize, discurso 2:03–2:09) | NobelPrize.org | não | L25 |

> **Alternativas:** `brutos/extras/_alternativas/E09-ligacao-nobel.mp4`; retrato vertical do Nobel (Arthur Petron,
> CC BY-SA 4.0) ou foto do Collision 2024 (Vaughn Ridley/Collision via Sportsfile, CC BY 2.0) — `material/fontes.json`.

## Checklist de gravação
- [ ] Lumix S5IIX vertical: V-Log, 4K 25p, 4:2:2 10-bit, 1/50, ISO base, WB fixo, "Vertical Position Info" ligado
- [ ] Primeira tomada do dia: `camera-00-cor.mov` (5 s folha branca perto do rosto + 5 s rosto parado)
- [ ] Pausa da capa: 3 s parado, em silêncio, boca fechada, braços cruzados, olhar firme, antes da L01
- [ ] Gravar cada linha; se errar, **repetir a linha inteira** (pode dizer "de novo" antes)
- [ ] Gravar também L01B e L01C
- [ ] Vídeo principal → `videos/2026-10-20-geoffrey-hinton/brutos/principal/` (`camera-01.mov`…)
- [ ] Cenas extras de vídeo já estão em `brutos/extras/`; faltam só as animações E01, E04 e E06 (`/extras 2026-10-20-geoffrey-hinton`)

## Legenda do post (rascunho)
Geoffrey Hinton, o "padrinho da IA": quase 50 anos numa ideia que ninguém levava a sério.

Nasceu em Londres, numa família de cientistas, e queria entender a mente humana. O orientador mandou largar a pesquisa. Ele não largou.
Em 2012, com dois alunos, fez um sistema que reconhece imagens e mudou o rumo da IA. Em 2024, ganhou o Nobel de Física (dividido com John Hopfield).

→ Comenta NOBEL que eu te mando o link oficial da entrevista dele.
→ Manda pra alguém que tá desistindo de uma ideia.

Fontes: 60 Minutes/CBS (out/2023), NobelPrize.org (2024), ImageNet (2012), MIT Technology Review (mai/2023).

#inteligenciaartificial #geoffreyhinton #nobel #iaparainiciantes #historiadaia

## Hashtags (máx. 5)
#inteligenciaartificial #geoffreyhinton #nobel #iaparainiciantes #historiadaia

## Material do CTA
**NOBEL → "o link da entrevista do Hinton"** (PDF de 2 páginas, **já gerado**: `material/entrevista-geoffrey-hinton.pdf`):
- Link oficial: "Godfather of AI" Geoffrey Hinton: The 60 Minutes Interview — https://www.youtube.com/watch?v=qrvK_KuIeJk
  (canal oficial 60 Minutes/CBS, grátis, 13 min 12 s, em inglês; transmitida em 08/10/2023).
- **Legenda:** não existe legenda oficial em português. O PDF explica a tradução automática do YouTube
  (engrenagem → Legendas → Tradução automática → Português), com o aviso de que pode errar.
- Transcrição em inglês da CBS: https://www.cbsnews.com/news/geoffrey-hinton-ai-dangers-60-minutes-transcript/
- A fala promete "o link oficial da entrevista dele" — é exatamente o que o PDF entrega.

## Fontes
Afirmação por linha (detalhe em `material/dossie.md`):
- L01–L02 ("quase 50 anos" numa ideia → Nobel): anos 70 em Edimburgo → Nobel 2024; o próprio Hinton fala em "uns 50 anos" até funcionar bem ([60 Minutes/CBS](https://www.cbsnews.com/news/geoffrey-hinton-ai-dangers-60-minutes-transcript/), dossiê M2)
- L04 (Londres, 1947): [Nobel, Facts](https://www.nobelprize.org/prizes/physics/2024/hinton/facts/) [primária] + Wikipedia. "Família de cientistas": pai entomologista (dossiê M1) e capítulo "crescer numa família de pesquisadores" da [entrevista oficial do Nobel](https://www.nobelprize.org/prizes/physics/2024/hinton/interview/)
- L05–L06 (não começou por computadores; queria entender a mente): formou-se em psicologia experimental em Cambridge (1970) — Wikipedia; Edimburgo, simular rede neural para estudar o cérebro — 60 Minutes
- L07–L11 (anos 70; a ideia do cérebro; orientador mandou largar antes que arruinasse a carreira; não desistiu): 60 Minutes [primária] + Wikipedia
- L12–L14 (2012, com dois alunos; reconhecimento de imagens; 15,3 % × 26,2 % de erro, só na tela): [ImageNet, resultados oficiais](https://image-net.org/challenges/LSVRC/2012/results.html) [primária] + [Computer History Museum](https://computerhistory.org/blog/chm-releases-alexnet-source-code/)
- L15–L16 (Google compra a DNNresearch em 2013; dez anos no Google): [MIT Technology Review, 01/05/2023](https://www.technologyreview.com/2023/05/01/1072478/deep-learning-pioneer-geoffrey-hinton-quits-google/) + [AP, 02/05/2023](https://ny1.com/nyc/all-boroughs/ap-top-news/2023/05/02/godfather-of-ai-leaves-google-warns-of-techs-dangers) + 60 Minutes. Valor da compra fica **fora**
- L18–L19 (sai em 2023 para falar dos riscos sem amarra — fala dele): MIT Technology Review + AP
- L20–L22 (17 meses depois; ligação às duas da manhã; Comitê Nobel; Nobel de Física 2024): [Nobel, entrevista por telefone](https://www.nobelprize.org/prizes/physics/2024/hinton/interview/) [primária] + [Fortune, 09/10/2024](https://fortune.com/2024/10/09/openai-sam-altman-geoffrey-hinton-nobel-prize-physics-ilya-sutskever-toronto) + Nobel Facts
- L23 ("padrinho da IA" = apelido de imprensa): MIT Technology Review + AP (títulos)
- L24–L25 (alerta sobre os riscos): MIT Technology Review + [discurso do banquete Nobel](https://www.nobelprize.org/prizes/physics/2024/hinton/speech/)
- L27: lição do Carlos (opinião, não fato)

**Fora de propósito (dossiê §9):** "inventou a IA", número/prazo de extinção, "protesto" contra o Google, o filho,
os US$ 44 milhões, consciência da IA, Boole.
