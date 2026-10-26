# Mapa de trechos — *The Thinking Game* → roteiro do Hassabis

> Levantado em 2026-09-18 pela sessão `content-ai-72`. **Arquivo novo, ninguém mais estava a escrever nele.**
> Eu **não** toquei em `roteiro.md`, `fontes.json` nem em `brutos/extras/` — quem manda nessa pasta é a
> sessão que está com o vídeo. Isto aqui é entrega, não edição.

## O que mudou (a decisão que destrava tudo)

O Carlos decidiu em 2026-09-18 que este Reel é **vídeo de comentário/reação**: ele fala **sobre** o
documentário, e os trechos entram como citação. Isso **substitui** o `permitido: null` do E02, que estava
à espera de autorização da Google DeepMind sob a leitura antiga (B-roll). Ver `docs/decisoes.md` §5 e
`.claude/agents/curador-de-obra.md`.

**Condições que continuam de pé:** trecho curto, voz do Carlos por cima (extras **mudos**), crédito na
tela, e o Reel tem de se sustentar sem os trechos.

**Crédito obrigatório:** `The Thinking Game (Google DeepMind / Greg Kohs)`

## Estado

- **Obra baixada e verificada:** `material/obra/the-thinking-game.mp4` — 1920×1080, 84 min, 1,3 GB.
  (O original é VP9/Opus e o QuickTime não toca; há `the-thinking-game-VER.mp4` em H.264 para assistir.)
- **Ficha de procedência:** `material/obra.json`
- **Transcrição com marcas de tempo:** `material/obra/transcricao-obra.json` (1919 segmentos)
- **11 trechos cortados e conferidos**, todos a 25 fps conformados 1:1, todos mudos. Ver tabela abaixo.

## O mapa (verificado olhando os frames, não só a legenda)

Tempos do corte vêm de `edicao/edl.json` (61,4 s). Todos os trechos entram em **`split`** — material
deitado, metade de cima, o Carlos fica embaixo falando.

| ID | Linha | Fala do Carlos | Trecho | Dur | O que se vê |
|---|---|---|---|---|---|
| E02 | L01 | "aprendeu xadrez aos quatro anos" | 23:03–23:07 | 4,0 s | Demis menino num torneio, P&B |
| E11 | L04 | "computação em Cambridge e depois neurociência" | 3:24–3:27 | 3,5 s | Demis jovem + placa do **UCL Institute of Cognitive Neuroscience** |
| E04 | L02 | "nascido aqui em Londres" | 7:08–7:11 | 3,0 s | Hassabis falando, na biblioteca |
| E12 | L05 | "em dois mil e dez… aqui em Londres" | 7:17–7:20 | 3,5 s | Letreiro **2010** sobre rua de Londres com ônibus vermelho |
| E05 | L03 | "aos dezessete criava videogame" | 40:08–40:11 | 3,0 s | Adolescente jogando numa TV antiga |
| E06 | L06 | "o Google comprou" | 13:24–13:28 | 4,0 s | Data center com o letreiro **2014** |
| E07 | L07 | "venceu um dos maiores nomes do Go" | 18:14–18:18 | 4,0 s | Placar do desafio — Lee Sedol desiste |
| E08 | L08 | "mais posições que átomos no universo" | 15:04–15:08 | 4,0 s | Tabuleiro de Go em jogo |
| E09 | L09 | "prever o formato das proteínas" | 46:33–46:37 | 4,0 s | **Animação**: cadeia de aminoácidos dobrando-se na estrutura 3D |
| E10 | L10 | "travava a ciência havia cinquenta anos" | 1:14:08–1:14:12 | 4,0 s | Gráfico do CASP disparando |
| E13 | L12 | "o menino do xadrez virou um dos nomes da IA" | 1:19:06–1:19:10 | 4,0 s | Hassabis adulto diante de um **tabuleiro de xadrez** — fecha o círculo com o E02 |

**Total citado: 41 s — ACIMA do teto de 30 s.** O Carlos mandou usar o máximo de extras e tratou este vídeo
como teste ("se não ficar legal, eu vou regravar"), por isso os 11 ficaram. Mas o número tem de ir à frente
dele: **41 s citados em 66,6 s = 62% do Reel**, o que estica a condição 5 (teste do vídeo órfão).
**L13 (CTA) fica sem extra de propósito**: o pedido para seguir não deve competir com imagem de terceiros.

### O teto é 30 s — e este vídeo está acima dele
O teto original de 20 s foi escrito a pensar em extra que **substitui** o Carlos na tela. Em `split` ele nunca
sai, fala o tempo todo, e o trecho ilustra o comentário — daí os 30 s que o Carlos autorizou em 19/09
(`docs/decisoes.md`, `CLAUDE.md` regra 4). **Os 45 s que estiveram aqui e no script eram erro meu**: eu
confirmei que havia autorização para subir, inventei o número e apresentei-o como decisão dele. Corrigido.
Se algum dia 30 s não chegar, muda-se por decisão escrita — com o número e de quem veio.

## Três achados que mudam o roteiro

1. **O Nobel não existe no documentário.** A palavra "Nobel" **não aparece uma única vez** nas legendas —
   o filme estreou em Tribeca em 6/2024 e o Nobel foi em 10/2024. A L11 só pode ser servida pelo print
   (E03, NobelPrize.org). Não perder tempo a procurar.
2. **A L11 não está na EDL.** Os segmentos vão da L10 direto para a L12 — a linha do Nobel não foi gravada
   ou não foi escolhida. **Isto precisa de decisão**: é o pagamento do hook ("E ganhou um Nobel com IA"),
   e sem ela o Reel promete Nobel e não entrega.
3. **Só a L13 (CTA) fica sem extra**, de propósito: o pedido para seguir não deve competir com imagem de
   terceiros. L04, L05 e L12 foram cobertas na 2.ª rodada (E11, E12, E13).

## Como refazer um trecho

```bash
uv run python scripts/baixar_obra.py trecho 2026-09-17-demis-hassabis <ID> <inicio> <fim> --nome <nome> --o-que "..."
uv run python scripts/baixar_obra.py estado 2026-09-17-demis-hassabis
```

O comando escreve o `.mp4` em `brutos/extras/`, uma linha em `material/fontes.json` (com `uso: "comentario"`)
e soma no orçamento. Sai **mudo** e **já a 25 fps conformado 1:1** — o filtro `fps` do ingest não lhe toca.
Depois é o caminho normal: `ingest.py` e o `gerar_props.py`, que mede o arquivo e põe em `split` sozinho.

**Conferir sempre abrindo o arquivo** (início, meio e fim), nunca confiando no comando ter passado — ver
armadilhas no fim.

## Ferramentas novas desta sessão (fora da pasta do vídeo, sem risco de colisão)

- `scripts/baixar_obra.py` — baixar obra, ficha de procedência, cortar trechos, orçamento de citação
- `.claude/agents/curador-de-obra.md` — o agente responsável
- `.claude/commands/obra.md` — `/obra`
- `docs/contratos.md` §0b — contrato do `obra.json`
- `docs/decisoes.md` §5 — a decisão do Carlos e as condições


## Armadilhas encontradas ao cortar (2026-09-19)

1. **Seek de saída ≠ seek de entrada.** O script cortava com `-ss` depois do `-i`; com o filtro de
   conformação no meio, dois cortes aterraram nos **créditos finais** e numa sala errada, apesar de os
   frames de verificação mostrarem o plano certo — porque a verificação usava seek de entrada.
   **Cortar e conferir têm de usar o mesmo método.** Corrigido: o script usa seek de entrada.
2. **Conferir o arquivo, não o comando.** Os 4 cortes errados (E09, E11, E12, E13) passaram sem erro
   nenhum. Só apareceram ao abrir o `.mp4` e olhar início, meio e fim.
3. **Planos curtos.** A proteína no ecrã do portátil durava ~1 s — não dava para 4 s. A animação da
   dobragem (46:33) é melhor e tem fôlego.
4. **Tarja com nome de terceiro.** A primeira E11 acabava numa cartela "Eleanor Maguire, Prof of Cognitive
   Neuroscience, UCL" — nome que o público não conhece, a roubar a atenção. Encurtado para acabar na placa.
