---
slug: 2026-10-18-jensen-huang
tema: "Quem é Jensen Huang: lavou prato numa lanchonete, planejou a Nvidia numa mesa de outra, quase quebrou, e a empresa virou a primeira de 5 trilhões de dólares"
pilar: perfil
estrutura: "narrativo (00-marca/modelo-roteiro-narrativo.md) com a 1.ª virada e a 1.ª palavra nos primeiros ~22 s (estratégia de alcance §2): gancho → 1.ª virada → história → desafio → virada → clímax → reflexão → CTA"
hook_template: antes-depois
publico: ambos
duracao_alvo: 90
palavras_alvo: 185
wps_ref: 2.1
hooks:
  A: {fala: "Imagina você lavar prato numa lanchonete…", tela: "DO PRATO SUJO AOS 5 TRILHÕES", visual: "abertura com o CONTEÚDO em tela cheia (extra `full`: vídeo do Denny's e dos 5 trilhões), voz do Carlos por cima; par A/B (decisões 17/10): B = conteúdo em tela cheia até o fim do gancho (L01–L02), o Carlos entra na L03 (~9 s); A = o Carlos desde o quadro 0"}
  B: {fala: "Imagina limpar banheiro num internato, ainda criança, longe de casa…", tela: "LIMPAVA BANHEIRO AINDA CRIANÇA", visual: "abertura com o CONTEÚDO em tela cheia (extra `full` do assunto), voz do Carlos por cima; par A/B (decisões 17/10): B = conteúdo em tela cheia até o fim do gancho (L01–L02), o Carlos entra na L03 (~9 s); A = o Carlos desde o quadro 0"}
  C: {fala: "Imagina ser o melhor lavador de pratos da lanchonete…", tela: "O MELHOR LAVADOR DE PRATOS", visual: "abertura com o CONTEÚDO em tela cheia (extra `full`: vídeo do Denny's), voz do Carlos por cima; par A/B (decisões 17/10): B = conteúdo em tela cheia até o fim do gancho (L01–L02), o Carlos entra na L03 (~9 s); A = o Carlos desde o quadro 0"}
hook_escolhido: A
titulo: {contexto: "Lavava prato e criou", impacto: "a primeira empresa de 5 trilhões", cinza: 3, rabisco: "trilhões"}
pose_capa: "segurando um prato branco ao lado do rosto, sobrancelha erguida"
cta_tipo: palavra-material
cta_palavra: PRATO
material: "PDF de 2 páginas com o link oficial do discurso de formatura do Jensen Huang na Carnegie Mellon (10/05/2026, 18 min, canal oficial da CMU; de 2:32 a 5:45 ele conta o internato, o Denny's, a fundação e o quase fim da Nvidia), em inglês, com o passo a passo para ligar a tradução automática da legenda no YouTube; de bônus, o link da entrevista dele em Stanford (56 min)"
material_titulo: "o link do discurso do Jensen Huang"
fontes:
  - "https://www.youtube.com/watch?v=FZh_0uRgrg4"
  - "https://blogs.nvidia.com/blog/nvidia-ceo-carnegie-mellon-commencement-address/"
  - "https://blogs.nvidia.com/blog/nvidia-dennys-trillion/"
  - "https://www.nbcconnecticut.com/news/business/money-report/jensen-huang-started-his-2-trillion-company-nvidia-at-a-dennys-breakfast-booth/3282560/"
  - "https://www.sec.gov/Archives/edgar/data/1045810/000104581026000021/nvda-20260125.htm"
  - "https://fortune.com/2024/03/12/billionaire-nvidia-ceo-first-job-dennys"
  - "https://fortune.com/2025/12/05/jensen-huang-nine-year-old-janitor-before-nvidia-joe-rogan-podcast"
  - "https://www.fortune.com/2024/08/28/nvidias-billionaire-boss-i-used-to-clean-bathrooms-and-now-im-the-ceo"
  - "https://www.gsb.stanford.edu/insights/jensen-huang-how-use-first-principles-thinking-drive-decisions"
  - "https://thenextweb.com/news/nvidia-sega-1995-5-million-rescue"
  - "https://www.dawn.com/news/1952086/ai-chip-giant-nvidia-becomes-worlds-first-5-trillion-firm"
  - "https://finance.yahoo.com/news/nvidia-started-5-trillion-club-172246928.html"
  - "https://raeng.org.uk/news/modern-machine-learning-innovators-win-2025-queen-elizabeth-prize-for-engineering/"
  - "https://qeprize.org/news/king-presentation-qeprize"
  - "https://www.uktech.news/ai/jensen-huang-and-other-ai-leaders-presented-award-by-king-charles-20251106"
  - "https://en.wikipedia.org/wiki/Jensen_Huang"
status: rascunho
versao: 1
---

# Quem é Jensen Huang

> **Versão 1 (17/10), escrita no jeito de falar do Carlos** (`00-marca/voz-carlos.md`, calibrado em 17/10): frases
> com sujeito, sem subjuntivo, conectores dele ("Pois é", "E olha só que interessante", "Só que", "E aí"). O improviso
> por cima é a regra (`docs/decisoes.md` §2, 17/10). 3.º perfil da série (Hinton e Fei-Fei já feitos): a ponte é a
> L14, "de quem eu já falei aqui".
> **Revisão de 17/10 (revisor-de-roteiro): APROVADO COM AJUSTES — ver `roteiro-revisao.md`.** Aplicados: visual da abertura (§2.8, par A/B (B: conteúdo até o fim do gancho; A: Carlos desde 0)), `[pausa]` tirado da L12 e da L14 (sobram 5), fonte da L02/legenda (AFP, não Reuters), nota de fonte da L06–L07, data do prêmio.
> Pronúncia: Jensen Huang = **"Djén-sen Huáng"** · Nvidia = **"En-ví-dia"** · Denny's = **"Dé-nis"** ·
> Kentucky = **"Ken-tâ-ki"** · Fei-Fei Li = "fêi-fêi li" · Hinton = "Hín-ton".
>
> **Blocos do modelo → seção do parser:** GANCHO = L01–L03 · 1.ª VIRADA + 1.ª menção da palavra = L04–L05 ·
> A HISTÓRIA = L06–L09 · O DESAFIO = L10 · A VIRADA = L11–L12 · O CLÍMAX = L13–L14 · REFLEXÃO = L15–L16 ·
> CTA = L17–L19.
> **A L05 ("comenta PRATO") fica de propósito na seção `virada`, não em `cta`:** o cartão grande do CTA
> (`gerar_props.py`) é montado na 1.ª linha `cta` que contém a palavra, e ele tem de cair na L18, o CTA final.
> **Frases de ênfase** (o Carlos volta para a tela nelas): L04 "E olha só que interessante:", L10 "Só que a empresa
> quase quebrou.", L15 "A história dele mostra uma coisa:".
> **Tamanho:** 182 palavras ≈ 87 s a 2,1 palavras/s (o teto é 90 s, um vídeo só no IG e no FB). A frase "segundo ele,
> ninguém ali sabia montar uma empresa" saiu para caber; está na fonte e pode voltar no improviso, se o corte deixar.

## Roteiro

> **PAUSA DA CAPA (antes de falar qualquer coisa).** Fique **parado 3 segundos** olhando para a câmera, em silêncio:
> boca fechada, **segurando um prato branco ao lado do rosto, sobrancelha erguida** (`pose_capa`), sem movimento.
> É desse trecho que sai o frame da capa do feed. O ChatGPT Voz lê essa linha em voz alta antes da L01.

| ID | Seção | FALA |
|---|---|---|
| L01 | gancho | Imagina você lavar prato / numa **lanchonete**… |
| L02 | gancho | e, anos depois, / criar a primeira empresa / de **5 trilhões** de dólares. [pausa] |
| L03 | gancho | Pois é. / Essa é a história do **Jensen Huang**, / da Nvidia. |
| L04 | virada | E olha só que interessante: / ela nasceu numa **mesa de lanchonete**. [pausa] |
| L05 | virada | Se quiser ver ele contando, / comenta **PRATO**. |
| L06 | historia | Ele nasceu em Taiwan / e, ainda criança, / foi parar num internato no **Kentucky**. |
| L07 | historia | A família achava que era escola boa… / mas ele limpava os **banheiros**. |
| L08 | historia | Depois, / ele foi lavar prato num **Denny's**. |
| L09 | historia | Em **1993**, / num outro Denny's, / ele e dois amigos planejaram a Nvidia. |
| L10 | desafio | Só que a empresa quase **quebrou**. [pausa] |
| L11 | virada | Anos depois, / chegou a **inteligência artificial**. |
| L12 | virada | Se o ChatGPT é o carro, / a Nvidia faz o **motor**. |
| L13 | climax | Aqui em **Londres**, / ele recebeu do **Rei Charles** o mesmo prêmio |
| L14 | climax | do Hinton e da Fei-Fei Li, / de quem eu já falei aqui. |
| L15 | reflexao | A história dele mostra uma coisa: [pausa] |
| L16 | reflexao | o seu **Denny's** pode ser / onde você está agora. [pausa longa] |
| L17 | cta | Salva pra rever / quando achar que começou **pequeno demais**. |
| L18 | cta | Comenta a palavra **PRATO** / que eu vou te enviar o discurso dele. |
| L19 | cta | E manda pra quem tá **recomeçando** / aqui na Europa. |
| L01B | gancho-alt | Imagina limpar banheiro num internato, / ainda criança, / longe de casa… |
| L01C | gancho-alt | Imagina ser o melhor lavador de pratos / da lanchonete… |

## Cenas extras

> **Padrão de perfil (`docs/decisoes.md` §4, 15/10 e 17/10 — aprovado na Fei-Fei v3.1, "podemos basear nessa versão
> do layout"):** faixa CONTÍNUA de imagens do Jensen Huang da 1.ª menção a ele (L03) até a reflexão (L16), imagem
> atrás de imagem, corte seco, sem "entra e sai", com **sincronia fala ↔ imagem** (o internato entra quando ele diz
> "internato", o Denny's quando diz "Denny's", o Rei Charles quando diz "Rei Charles"). **4 layouts, variando conforme
> a imagem:** `full` (retrato/pessoa, tela cheia) · `pilha` (3–4 faixas, para imagem deitada ou quadrada) · `solo`
> (imagem de leitura inteira sobre preto: print, manchete, documento) · `split` (cena em cima, o Carlos embaixo).
> O **Carlos volta** nas frases de ênfase (L04, L10, L15) e no **CTA (L17–L19, sem extra — regra rígida 6)**;
> **Abertura (`_controle/estrategia-de-alcance.md` §2.8, 17/10): L01–L02 (gancho) cobertos por um extra em `full` — vídeo do
> Denny's e dos 5 trilhões, voz do Carlos por cima, sem o rosto dele; variante do rodízio = par A/B (o Carlos entra na L03, por
> volta dos 10 s; o editor anota em `_controle/testes-abertura.md`).** Nunca a mesma imagem duas vezes seguidas; misturar fotos dele (jovem e
> hoje), o Denny's, a sede, prints e trechos dele falando. Trechos de vídeo com **áudio original baixo ou mudo, crédito
> na tela, sem teto de tempo** (14/10). Ponto forte para as linhas L06–L10: no discurso da Carnegie Mellon
> (`FZh_0uRgrg4`, de 2:32 a 5:45) ele mesmo conta o internato, o Denny's, a fundação e o quase fim da Nvidia.
> Material de partida em `material/fontes.json` (fotos Commons E01–E05, prints E06–E10). **A sequência por imagem
> (arquivos, ordem, tempos, layout de cada uma) é montada depois pelo editor em `edicao/sequencia-extras.md`.**

## Checklist de gravação
- [ ] Lumix S5IIX vertical: V-Log, 4K 25p, 4:2:2 10-bit, 1/50, ISO base, WB fixo, "Vertical Position Info" ligado
- [ ] Primeira tomada do dia: `camera-00-cor.mov` (5 s folha branca perto do rosto + 5 s rosto parado)
- [ ] Ter um **prato branco** à mão para a pose da capa
- [ ] Pausa da capa: 3 s parado, em silêncio, boca fechada, segurando o prato branco ao lado do rosto, sobrancelha erguida, antes da L01
- [ ] Gravar cada linha; se errar, **repetir a linha inteira** (pode dizer "de novo" antes)
- [ ] Gravar também L01B e L01C
- [ ] Pronúncia: "Djén-sen Huáng", "En-ví-dia", "Dé-nis", "Ken-tâ-ki"
- [ ] L18: o PDF é o **discurso** da Carnegie Mellon; se sair "entrevista", tudo bem — o PDF leva também a entrevista de Stanford
- [ ] Vídeo principal → `videos/2026-10-18-jensen-huang/brutos/principal/` (`camera-01.mov`…)
- [ ] Cenas extras → `videos/2026-10-18-jensen-huang/brutos/extras/` (o buscador-de-videos e o `/extras 2026-10-18-jensen-huang` dizem o que falta)

## Legenda do post (rascunho)
Jensen Huang lavava prato numa lanchonete e planejou a Nvidia numa mesa de outra. Ela virou a 1.ª empresa de US$ 5 trilhões.

Com 9 anos, foi parar num internato no Kentucky: a família achava que era escola boa, e ele limpava os banheiros. Depois, lavou prato num Denny's, perto de Portland.
Em 1993, num Denny's de San Jose, planejou a Nvidia com dois amigos. "A gente não fazia ideia de como montar uma empresa", ele contou. O primeiro chip não funcionou e a empresa quase quebrou.
Hoje os chips da Nvidia são o motor da IA: em 29/10/2025 ela passou dos 5 trilhões de dólares, e em novembro ele recebeu do Rei Charles, aqui em Londres, o mesmo prêmio de engenharia do Hinton e da Fei-Fei Li.

→ Comenta PRATO que eu te mando o link do discurso dele na Carnegie Mellon (18 min, em inglês, com tradução automática da legenda).
→ Salva pra rever quando achar que começou pequeno demais, e manda pra quem tá recomeçando aqui na Europa.

Fontes: discurso na Carnegie Mellon (10/05/2026); blog da Nvidia (26/09/2023); AFP e AP (29/10/2025); QEPrize e Royal Academy of Engineering (2025).

#inteligenciaartificial #jensenhuang #nvidia #historiadaia #empreendedorismo

## Hashtags (máx. 5)
#inteligenciaartificial #jensenhuang #nvidia #historiadaia #empreendedorismo

## Material do CTA
**PRATO → "o link do discurso do Jensen Huang"** (PDF de 2 páginas, a gerar pelo `produtor-de-material` em
`material/`): o link oficial do discurso de formatura na Carnegie Mellon, "2026 CMU Commencement Keynote Speaker:
Jensen Huang" — https://www.youtube.com/watch?v=FZh_0uRgrg4 (canal oficial Carnegie Mellon University, 10/05/2026,
18 min 22 s). **De 2:32 a 5:45 ele conta a história do vídeo** (conferido nas legendas em 17/10): mandado aos 9 anos
com o irmão para os EUA, o internato batista em Oneida (Kentucky), o primeiro emprego de lavador de pratos no Denny's
("que na época parecia uma grande promoção"), a fundação com Chris Malachowsky e Curtis Priem, "a gente não fazia ideia
de como montar uma empresa", o primeiro chip que não funcionou e o pedido à Sega. **Legenda: só inglês automático**
(não há português oficial) → o PDF ensina a ligar "Legendas > Traduzir automaticamente > Português" no YouTube e
**nunca** diz "com legenda em português". **Bônus** (cobre o caso de o Carlos dizer "entrevista" na L18): Stanford GSB,
*View From The Top* — https://www.youtube.com/watch?v=lXLBTBBil2U (56 min 27 s, onde ele diz que foi "provavelmente o
melhor lavador de pratos do Denny's"; transcrição oficial na página do GSB). A fala promete exatamente isto: "ver ele
contando" (L05) e "o discurso dele" (L18).

## Fontes
Cada linha → fonte (graus de confirmação em `material/dossie.md`; o discurso da CMU foi conferido nas legendas
automáticas do vídeo oficial em 17/10):
- **L02** — Nvidia, a primeira empresa a passar de US$ 5 trilhões, em 29/10/2025 (fechou em US$ 5,03 tri): [Dawn, texto da AFP](https://www.dawn.com/news/1952086/ai-chip-giant-nvidia-becomes-worlds-first-5-trillion-firm) + [AP via Yahoo Finance](https://finance.yahoo.com/news/nvidia-started-5-trillion-club-172246928.html). A fala não diz valor de hoje nem ranking (dossiê §9).
- **L04, L09** — a Nvidia foi decidida numa mesa de Denny's, em 1993, por três amigos (Huang, Chris Malachowsky e Curtis Priem): [blog da Nvidia, 26/09/2023](https://blogs.nvidia.com/blog/nvidia-dennys-trillion/) ("three friends") + [CNBC/NBC, mar/2024](https://www.nbcconnecticut.com/news/business/money-report/jensen-huang-started-his-2-trillion-company-nvidia-at-a-dennys-breakfast-booth/3282560/); constituída em abril de 1993: [10-K da Nvidia na SEC](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000021/nvda-20260125.htm). **"Num outro Denny's"**: ele trabalhou num Denny's perto de Portland (Oregon) e a Nvidia nasceu num de San Jose — nunca "o mesmo Denny's" (dossiê §0).
- **L06–L07** — nasceu em Taiwan; aos 9 anos foi mandado com o irmão para os EUA e foi parar num internato batista em Oneida, no Kentucky, que a família achava que era escola boa; lá limpava os banheiros: [discurso da CMU, 2:32](https://www.youtube.com/watch?v=FZh_0uRgrg4) [primária] + [Fortune, 05/12/2025](https://fortune.com/2025/12/05/jensen-huang-nine-year-old-janitor-before-nvidia-joe-rogan-podcast) + [Fortune, 28/08/2024](https://www.fortune.com/2024/08/28/nvidias-billionaire-boss-i-used-to-clean-bathrooms-and-now-im-the-ceo). A fala diz "ainda criança" (a idade diverge entre 9 e 10 nas fontes secundárias; ele diz 9). **"A família achava que era escola boa"** não está nas páginas da Fortune citadas: vem da [Wikipedia](https://en.wikipedia.org/wiki/Jensen_Huang) (tios o matricularam por engano, "a prestigious boarding school") e da Bloomberg Billionaires (que cita o perfil da Wired de 2002) — por isso a fala diz "a família" (tios) e não atribui a ele. Nascimento em Taiwan: Wikipedia (Taipei); a fala diz só "Taiwan".
- **L08** — lavador de pratos num Denny's (perto de Portland, aos 15): [discurso da CMU, 3:10](https://www.youtube.com/watch?v=FZh_0uRgrg4) [primária] + [Fortune, 12/03/2024](https://fortune.com/2024/03/12/billionaire-nvidia-ceo-first-job-dennys) + [blog da Nvidia](https://blogs.nvidia.com/blog/nvidia-dennys-trillion/) ("I was a dishwasher, I was a busboy, I waited tables").
- **L10** — o primeiro chip (NV1) não funcionou e a empresa quase ficou sem dinheiro; a Sega converteu um pagamento em investimento de US$ 5 mi: [discurso da CMU, 5:00](https://www.youtube.com/watch?v=FZh_0uRgrg4) ("Our first technology didn't even work… we nearly ran out of money… Without the money, Nvidia would vaporize") [primária] + [TNW, 15/07/2026](https://thenextweb.com/news/nvidia-sega-1995-5-million-rescue) + [Wikipedia](https://en.wikipedia.org/wiki/Jensen_Huang).
- **L11–L12** — a Nvidia faz o hardware em que a IA de hoje roda ("o motor"; o ChatGPT é o "carro" — tradução do dossiê §1/§4): o QEPrize 2025 premiou Huang e Bill Dally por "the hardware that underpins the operation of modern machine learning algorithms" ([Royal Academy of Engineering](https://raeng.org.uk/news/modern-machine-learning-innovators-win-2025-queen-elizabeth-prize-for-engineering/)).
- **L13–L14** — Queen Elizabeth Prize for Engineering 2025 (aprendizado de máquina moderno), dividido entre sete pessoas, entre elas Huang, Geoffrey Hinton e Fei-Fei Li; entregue pelo rei Charles III no St James's Palace, em Londres, em 5 de novembro de 2025: [QEPrize](https://qeprize.org/news/king-presentation-qeprize) + [Royal Academy of Engineering](https://raeng.org.uk/news/modern-machine-learning-innovators-win-2025-queen-elizabeth-prize-for-engineering/) + [UKTech.news, 06/11/2025](https://www.uktech.news/ai/jensen-huang-and-other-ai-leaders-presented-award-by-king-charles-20251106). A fala não diz quantos laureados (dossiê: a contagem diverge na imprensa).
- **L15–L16** — lição do Carlos (opinião, não fato), sem promessa de resultado nem de renda (`regras-legais.md` §5).
- **L18** — discurso da CMU, 18 min 22 s, canal oficial, só legenda automática em inglês: dossiê §6.
- **L01C** — "I was probably Denny's best dishwasher": [Stanford GSB](https://www.gsb.stanford.edu/insights/jensen-huang-how-use-first-principles-thinking-drive-decisions).
- **Fora do roteiro (não dito):** "segundo ele, ninguém ali sabia montar uma empresa" (*"We had absolutely no idea how to build a company"*, [discurso da CMU, 4:45](https://www.youtube.com/watch?v=FZh_0uRgrg4); *"None of us knew how to do anything"*, [CNBC](https://www.nbcconnecticut.com/news/business/money-report/jensen-huang-started-his-2-trillion-company-nvidia-at-a-dennys-breakfast-booth/3282560/)) — saiu só para caber nos 90 s, pode voltar no improviso; os "30 dias de falir" (frase dele em apresentações; fica na `historia-completa.txt` para o improviso, sempre como "ele costuma dizer"); o pedido à Sega e o chip RIVA 128 (1997); CUDA e o AlexNet de 2012 (não estão no dossiê; a ponte com o Hinton e a Fei-Fei foi feita pelo prêmio, que está confirmado); a jaqueta de couro; capital inicial (US$ 600 / US$ 40 mil, sem fonte sólida); valor de mercado de hoje, fortuna e ranking; China e exportação; a carta do rei (não conferida na BBC).
