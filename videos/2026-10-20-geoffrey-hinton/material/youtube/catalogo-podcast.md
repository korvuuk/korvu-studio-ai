# Catálogo — podcast Diary of a CEO + post do X (Hinton, 2026-10-20)

Minerado em 15/10/2026. Cópias de estudo em `material/youtube/podcast/` (nunca publicadas inteiras); os trechos que podem ir para o Reel estão em
`material/youtube/cortes-podcast/P01…P16` (H.264 1920x1080, 25 fps, **áudio original mantido** no arquivo: vai mudo ou baixo na mixagem).
Nada foi para `brutos/extras/`, nada mexeu em `roteiro.md` nem em `edicao/`.

## 1. As duas fontes

### 1.1 Podcast "Godfather of AI: They Keep Silencing Me But I'm Trying to Warn Them!"
- **Canal:** The Diary of a CEO (Steven Bartlett) · **publicado:** 2025-06-16 · **duração:** 1:30:07 · 25 fps
- **Link:** https://www.youtube.com/watch?v=giT0ytynSqg
- **Arquivo:** `podcast/giT0ytynSqg-podcast.mp4` (H.264 1080p + AAC, não precisou de cópia -VER)
- **Crédito para a tela:** "The Diary of a CEO" (e "The Nobel Prize" no P10). As fotos antigas vêm de arquivos que o programa não credita; credite só o programa.
- **Como foi assistido:** 1 quadro a cada 4 s nos 90 min inteiros (28 folhas de contato) + quadros a cada 0,5–1 s em todos os trechos de arquivo + transcrição automática para identificar quem aparece.

**Resultado honesto: o programa é 95% entrevista (Hinton + Steven alternando) e o "material vivo" é pouco: ~14 momentos úteis.**
Ele está concentrado em 3 lugares: abertura (0:00–0:50, editada com texto grande queimado), a explicação da história da IA (2:26–5:40) e duas passagens soltas (32:30, 1:12, 1:19–1:20, 1:28). Não há: infância, escola, Cambridge/Edimburgo, laboratórios, Google, recorte de jornal dele, nada de Toronto 2012 além da figura do ImageNet.
O que existe de arquivo do Hinton jovem são **3 fotos P&B** (do mesmo ensaio que as F01/F02 da CBS: mesmo suéter listrado, final dos anos 80/início dos 90 pelo monitor CRT; o podcast não dá data, então **não escrever "anos 70" na tela**).

### 1.2 Post do X (status 1336843955619520521)
- yt-dlp funcionou sem login: é um vídeo de **12 s, 512x208, sem áudio**, do pesquisador Andrea Tagliasacchi, sobre o artigo "Canonical Capsules" (Sun et al., 2020): nuvem de pontos de aviões e uma cabeça azul ("mental picture").
- **Não tem o Hinton, nem foto, nem rosto dele.** Só uma animação científica abstrata e minúscula. **Descartado** (arquivo guardado em `podcast/x-1336843955619520521.mp4`, caso queira ver). Se o Carlos mandou este link pensando em outra coisa (ex.: outro tweet do Hinton), me passe o link certo.

## 2. Momentos cortados (arquivo → o que mostra → como usar em 9:16)

Tempos de origem = minuto no vídeo do podcast (aproximado em ±0,3 s: cada corte foi conferido no primeiro, meio e último quadro). "9:16" descreve o que um recorte central 607x1080 (≈ x 34–66% da largura) pega.

| Corte | Origem | Dur | O que mostra | Texto/logo na tela | 9:16 (onde está o assunto) | Linha que ilustra melhor |
|---|---|---|---|---|---|---|
| `P01-hinton-jovem-computador` | 2:26.7–2:30.9 | 4,2 s | **Hinton jovem**, P&B, sentado no teclado de um computador antigo (monitor CRT), olha para a câmera por cima do ombro | nenhum | Hinton em x 10–50% (rosto ~25%). **Recortar à esquerda (x 8–40%)**; o centro pega o monitor, não ele | L11 (não desistiu) · L10 · L07 |
| `P02-hinton-jovem-quadro-redes` | 3:40.2–3:43.9 | 3,7 s | **Hinton jovem** diante de um **quadro com redes desenhadas** (neurônios ligados, curvas), P&B; o melhor "o processo dele" | nenhum | Rosto em x 60–75%, redes em x 0–50%. Recorte à direita (x 52–84%) pega ele; pan da direita p/ esquerda revela os diagramas | **L03** (abertura) · L07 · L08 |
| `P03-hinton-jovem-estante` | 32:31.0–32:37.2 | 6,2 s | **Hinton jovem**, P&B, em pé no escritório entre estantes de papéis e quadro-branco, olhando para a câmera, parado | nenhum | **Centro funciona** (rosto em x 45–55%) | L09 (ninguém acreditava, figura solitária) · L10 · L07 |
| `P04-cerebro-neuronios-animacao` | 3:03.4–3:09.8 | 6,4 s | Animação: faísca que vira um **cérebro de fios luminosos** no escuro | nenhum | Centro (cérebro em x 38–68%) funciona | **L06** (mente humana) · L08 |
| `P05-chip-conexoes-animacao` | 3:10.0–3:16.9 | 6,9 s | Animação: tela/"chip" branca que solta **raios de conexões** em todas as direções (rede se espalhando) | nenhum | Centro funciona | **L14** (mudou o rumo da IA) · L08 · L13 |
| `P06-perceptron-rosenblatt-arquivo` | 5:22.1–5:37.9 | 15,8 s | **Filme de arquivo P&B** (anos 50/60): homem operando o Perceptron de Rosenblatt, mão selecionando "WRONG/RIGHT", cartaz "MAN/WOMAN"; fecha com a palavra "woman" | **Legenda queimada em inglês** ("Frank Rosenblatt's perceptron machine…") no canto inferior esquerdo, até ~x 69% | Homem/máquina em x 45–75%: recorte x 40–72% pega, mas **a legenda invade o rodapé**. Cortar o rodapé (usar só os 85% de cima, zoom 1,2x) ou cobrir com a nossa legenda | **L08** (máquinas que aprendem) · L09 |
| `P07-von-neumann-turing-computadores` | 4:02.0–4:07.6 | 5,6 s | Dois retratos de arquivo: **von Neumann** diante de um computador de válvulas (1945) e **Turing** com a máquina de Enigma (1936) | Legendas queimadas ("John von Neumann, 1945…", "Alan Turing & The Turing Machine, 1936…") no rodapé | Os dois têm o assunto nas pontas (von Neumann à esquerda, Turing à direita): **não recorta bem; usar pan** | L07/L08 (computadores antigos, quem já acreditava em máquinas que aprendem). Só se o roteiro precisar: são outras pessoas |
| `P08-hinton-e-ilya-alunos` | 33:49.1–33:56.9 | 7,8 s | Retrato P&B: **Hinton (direita) e o aluno Ilya Sutskever** (esquerda) | Legenda queimada "Geoffrey Hinton (right) and his student Ilya Sutskever (left), who went on to co-found Open AI" (rodapé) | Os dois rostos ocupam x 14–75%: **não cabem juntos em 9:16**; pan de Ilya para Hinton, ou recorte só no Hinton (x 48–80%) | **L12** (dois alunos) |
| `P09-imagenet-figura-alexnet` | 1:12:31.8–1:12:46.9 | 15,1 s | A **figura do artigo do AlexNet** (oito fotos de teste: ácaro, navio, scooter, leopardo, carro, cogumelo, cereja, gato-de-madagascar, com as barras de palpites) | Logo "DOAC" + legenda em inglês no rodapé (somem nos últimos ~3 s) | Figura em x 22–78% sobre **fundo creme liso**: melhor **encaixar na largura** sobre fundo creme (#FBF8E8 aprox.) do que recortar | **L13** (reconhecer imagens) · L14 |
| `P10-nobel-recebendo-do-rei` | 1:28:22.0–1:28:32.9 | 10,9 s | **Cerimônia do Nobel 2024**: Hinton de casaca recebe a medalha do Rei Carl XVI Gustaf; orquestra, flores azuis, busto do Nobel ao fundo | Legenda queimada "Geoffrey Hinton receiving The Nobel Prize in Physics in 2024" (rodapé esquerdo) | Hinton em x 23–36%, Rei 42–53%, aperto de mão ~x 38%: **recorte x 18–50%**; a legenda fica no canto de baixo (subir o quadro ou cobrir) | **L22** · L21 · L23 |
| `P11-familia-george-boole` | 1:19:56.3–1:20:03.3 | 7,0 s | Gravura de **George Boole** ("avô da era digital", bisavô do Hinton) sobre fundo creme | Legenda em inglês no rodapé (longa) | Rosto em x 45–60%: **centro funciona**; recortar só os 88% de cima tira a legenda | **L04** (família de cientistas) |
| `P12-familia-mary-everest-boole` | 1:20:04.2–1:20:16.2 | 12,0 s | Foto de **Mary Everest Boole** (matemática e educadora), fundo creme | Legenda em inglês no rodapé | Centro funciona (x 28–72%) | **L04** |
| `P13-familia-george-everest` | 1:20:17.1–1:20:20.9 | 3,8 s | Foto de **George Everest** (o do monte Everest; tio da Mary) | Legenda em inglês no rodapé | Centro funciona | L04 (extra, 3,8 s) |
| `P14-familia-joan-hinton` | 1:20:39.9–1:20:48.9 | 9,0 s | Foto de **Joan Hinton**, prima do Hinton, física nuclear (Los Alamos) | Legenda curta no rodapé esquerdo ("Joan Hinton / Nuclear physicist"), fora do recorte central | Centro funciona (x 30–70%) e a legenda fica de fora | **L04** · L05 |
| `P15-hinton-pouca-gente-acreditava` | 3:27.5–3:32.1 | 4,6 s | Hinton **calmo, sentado, plano aberto**, falando "…so few people believed in it, there weren't many good universities…" (entra no meio da frase) | nenhum (o corte pega só a imagem limpa) | Centro funciona (x 40–60%) | L09 (quase ninguém acreditava), só se o Carlos quiser o próprio Hinton |
| `P16-engrenagens-logica-vs-redes` | 2:35.4–2:57.8 | 22,4 s | Animação em papel branco: engrenagens "draw a cat → select method → assemble → print cat" (a IA antiga por regras) terminando num gatinho | Texto desenhado em inglês dentro da animação | Centro funciona, mas sempre mostra palavras em inglês | Opcional: L07/L08 (a ideia "impossível" vs. IA por regras). Menos útil que P04/P05 |

Cada arquivo mostra a **imagem limpa** (primeiro/último quadro conferidos); os fades de entrada/saída do programa ficaram de fora.

### Momentos vistos e **não cortados** (por quê)
- 0:00–0:50 abertura do programa: Hinton em clipes com **texto gigante queimado** ("GEOFFREY HINTON", "NOBEL PRIZE WINNING", "FUTURE OF HUMANITY"), colagem do 0:23–0:29 com fotos dentro de janelas cinzas (inclui a foto do computador, o cérebro e a grade do ImageNet). Bom como referência de ritmo, sem imagem limpa.
- 0:12 Hinton em P&B numa porta com a placa "Artificial Intelligence Laboratory" (só com o título "GEOFFREY HINTON" por cima).
- 3:51–3:54 retrato P&B do Ilya Sutskever sozinho com legenda "Co-Founder of OpenAI" (alternativa curta ao P08).
- 8:22–8:30 Yann LeCun; 8:34 Eliezer Yudkowsky; 9:46 bomba "Little Boy"; 23:54 MSBC; 51:14 Elon Musk/CNBC: não são o Hinton nem o assunto do roteiro.
- 1:14 recorte de jornal "Military uses of AI" (borrado) e 0:46 TV antiga com jornal: riscos, não a história dele.
- Tudo o mais é entrevista (Steven ou Hinton de frente, com "Community Notes" e legendas do programa).
- Limite do método: amostrei a cada 4 s; uma foto que apareça por menos de ~3 s fora dos pontos que revisitei a cada 1 s pode ter passado.

## 3. Quadro linha → opções (tempos de saída do `edicao/edl.md` v24)

Legenda: **P** = corte deste catálogo (`cortes-podcast/`) · **E** = já cortado em `brutos/extras/` (60 Minutes, BBC, Nobel) · **F/N/CAPA** = `material/fotos/`.
Primeira opção = a que eu usaria; "alt" = reserva. Duração = trecho da faixa que a linha ocupa.

| Saída | Linha (fala) | Dur | 1ª opção | Alternativas | Observação |
|---|---|---|---|---|---|
| 12,5–16,5 | **L03** "Essa é a história de Geoffrey Hinton" | 4,0 s | **P02** (jovem diante do quadro de redes, 3,7 s) | F02 (rosto jovem, CBS), F22 | Rosto + diagramas já na abertura |
| 16,5–22,4 | **L04** "nasceu em Londres, em 1947, numa família de cientistas" | 5,9 s | **P11** Boole (2,0) → **P12** Mary Everest Boole (2,0) → **P14** Joan Hinton (1,9) | P13 (George Everest), F03 | Trio de família de cientistas; a ligação (bisavô, prima) vem do próprio Hinton no podcast, confirmar no dossiê antes de qualquer legenda "bisavô" |
| 22,4–28,9 | **L05** "não começou estudando computadores" | 6,5 s | **F02** (3,2) → **F01** (3,3) (jovem pensativo, mão no rosto, CBS) | — | Sem computador na imagem, de propósito |
| 28,9–33,2 | **L06** "como funciona a mente humana" | 4,3 s | **P04** (cérebro de fios luminosos, primeiros 4,3 s) | F06 (cérebro biológico x perceptron) | Animação limpa, sem texto |
| 33,2–38,7 | **L07** "Nos anos 70… ideia que parecia impossível" | 5,5 s | **E03** (fotos P&B Edimburgo, CBS; 5,5 s dos 9) | P03 (jovem na estante, 5,5 s) | Só a CBS data nos anos 70; os cortes P não têm data |
| 38,7–44,4 | **L08** "máquinas que aprendem como o cérebro?" | 5,7 s | **P06** (filme do Perceptron, primeiros 5,7 s) | P05 · F04 (Rosenblatt) · F05/F06 (diagramas, horizontais) · P07 (computadores de 1945) | P06 tem legenda em inglês queimada: cortar o rodapé |
| 44,4–48,9 | **L09** "quase ninguém acreditava" | 4,6 s | **P15** (Hinton calmo: "so few people believed in it") | P03 (jovem sozinho) | Se não quiser Hinton falando: P03 |
| 48,9–59,0 | **L10** "o orientador aconselhou abandonar" | 10,1 s | **E05** (7,5 s, CBS) → **P03** (2,6 s) | F01/F02 | P03 fecha o "jovem sozinho" |
| 59,0–63,6 | **L11** "Hinton não desistiu" | 4,6 s | **E12** (3,1 s "I always thought I was right") → **P01** (1,5 s, olhar por cima do ombro, ao computador) | P01 inteiro (4,2 s) | P01 é a melhor imagem de "continuou trabalhando" |
| 63,6–67,0 | **L12** "junto com dois alunos" | 3,4 s | **P08** (Hinton e Ilya, 3,4 s) | F10 (com Sutskever e Krizhevsky, 2013, horizontal) · F11 (Krizhevsky) | P08/F10 não cabem inteiros em 9:16: pan ou encaixar |
| 67,0–74,3 | **L13** "reconhecer imagens com precisão impressionante" | 7,2 s | **P09** (figura do AlexNet, 7,2 s; encaixada no fundo creme) | F14 (ImageNet) · F15 (artigo) · F16 (arquitetura) · F12/F13 (computador com 2 GPUs) · E06 (animação planejada) | E06 já cobre as barras 26,2 % × 15,3 %; P09 é a prova visual |
| 74,3–80,6 | **L14** "mudou o rumo da inteligência artificial" | 6,4 s | **P05** (rede se espalhando, 6,4 s) | F17 (gráfico do erro, vertical) · F16 | Hoje o roteiro deixa o Carlos em tela cheia aqui |
| 80,6–87,7 | **L15** "o Google comprou a empresa" | 7,0 s | **E07** (sala de servidores, 5,2 s) → **F18** (UBC 2013, 1,8 s) | F12 (computador das GPUs) · F10 | — |
| 87,7–94,8 | **L16** "10 anos com a gigante" | 7,2 s | **F19** (painel Deep Learning 2016, 3,6 s) → **F20** (com Fei-Fei Li, 3,6 s) | F21 | Podcast não tem nada do período Google |
| 94,8–98,0 | **L17** "Mas olha que interessante…" | 3,1 s | Carlos em tela cheia (como está no roteiro) | — | — |
| 98,0–101,3 | **L18** "deixou o Google" | 3,4 s | **CAPA-08** (Collision 2023, vertical) | E08 (BBC) · F18 | — |
| 101,3–107,2 | **L19** "falar livremente sobre os riscos" | 5,8 s | **E08** (BBC, 5,8 s dos 10) | CAPA-07 (Collision 2024) | O podcast só tem riscos em entrevista de frente; nada visual |
| 107,2–113,9 | **L20** "ligação às duas da manhã" | 6,8 s | **E01** (animação do celular, planejada) | — | — |
| 113,9–117,9 | **L21** "Era o comitê do Nobel" | 4,0 s | **N10** (Hinton e Hopfield) ou **E09** (8 s, "could be a prank") | N11 | — |
| 117,9–121,5 | **L22** "Nobel de Física de 2024" | 3,6 s | **P10** (cerimônia, 3,6 s) | N02 (mesmo momento, foto) · N04 (diploma) · N01 | P10 é o único vídeo de cerimônia que achei |
| 121,5–128,7 | **L23** "padrinho da inteligência artificial" | 7,2 s | **N03** (vertical, diploma, 3,6 s) → **F21** (Turing 2019, 3,6 s) | CAPA-02/N16/N17 (verticais) | — |
| 128,7–133,3 | **L24** "o homem que ajudou a desenvolver" | 4,6 s | **E10** (banquete, 4,6 s) | N06 | — |
| 133,3–139,1 | **L25** "o que mais alerta sobre os riscos" | 5,8 s | **E11** (banquete, 5,8 s) | N16 (vertical, 2025) · N15 | — |

Cobertura: L03–L16 e L18–L25 têm pelo menos uma opção que não é o Hinton falando de frente; L17 fica com o Carlos. **Opções vindas do podcast: L03, L04, L06, L08, L09 (ou P03), L10, L11, L12, L13, L14, L22.**

## 4. O que faltou (e onde procurar)
- **Infância, Londres, família dele, escola, Cambridge/Edimburgo, anos 70, Hinton jovem com alunos, laboratórios (Carnegie Mellon, Toronto) e Google:** o podcast não tem; as 3 fotos P&B jovens daqui + F01/F02/E03 são tudo o que há. Procurar: documentário da CBC/TVO/"Hinton" da U of Toronto, Computer History Museum, arquivo da Royal Society.
- **Recortes de jornal / manchetes** da compra pelo Google (2013) e do Nobel: não vieram neste podcast.
- **Hinton conta a própria história (L04–L11):** outras entrevistas já baixadas ainda **não** foram esmiuçadas em busca de inserts (Hanson 59 min e Robot Brains "Best Bits" 3:52 estão no catálogo anterior só com observações curtas). Se o Carlos quiser, passo essas duas e a 60 Minutes inteira no mesmo método.
- **Legendas queimadas em inglês** (P06, P07, P08, P09, P10, P11–P13): o editor precisa cortar o rodapé ou cobrir com a legenda da Korvu; P01–P05, P14, P15 vêm limpos.
- **Áudio:** os cortes mantêm o áudio original do podcast (Steven narrando nos P07–P14, Hinton no P15): na mixagem entra mudo, só música/voz do Carlos.
