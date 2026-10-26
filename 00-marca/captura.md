# Guia de gravação — Lumix S5IIX (V-Log) para Reels

> Escrito em 2026-09-17 a partir da **medição do seu primeiro vídeo real** (`PRAQ0967.MOV`), não de teoria.
> O que a câmera grava hoje já está no topo: **C4K 4096×2160, H.264 4:2:2 10-bit ALL-Intra 400 Mbps, 25p**,
> áudio PCM 24-bit. **O codec não é o gargalo — a luz é.**

## O que a medição mostrou
| Medida | O que deu | O que devia dar |
|---|---|---|
| Seu rosto no bruto (V-Log) | **32 IRE** | **40–45 IRE** |
| Seu rosto depois de converter V-Log→709 | 29 IRE | 40–50 IRE |
| Seu rosto no vídeo final (com o look da marca) | **13 IRE** | ≥ 35 IRE |
| Parede atrás, no final | 25 IRE | **abaixo** do rosto, não acima |
| Ponto mais claro da imagem final | 70 IRE | ~90 IRE em algum detalhe |
| Preto mínimo no final | abaixo do preto legal (corta sombra) | 0–3 IRE sem cortar |

**Tradução:** você subexpôs cerca de **1 diafragma**, e o fundo ficou mais claro que o seu rosto. Em pele escura,
isso é o que faz aparecer mancha e ruído depois: sobra pouco código para descrever a pele.

## Configuração da câmera (o que mudar)

| Item | Valor | Por quê |
|---|---|---|
| **ISO** | **640** (base do V-Log). Se faltar luz, pule direto para **4000** | O S5IIX tem dois ISOs nativos em V-Log: 640 e 4000. Valores intermediários (ex.: 1250, 2000) são ganho digital — mais ruído sem ganho real |
| **Obturador** | **1/50** | 25p com ângulo de 180°. No Reino Unido a rede é 50 Hz: 1/50 ou 1/100 evitam cintilação; **1/60 treme** |
| **Diafragma** | f/2.8–f/4 | Nítido, com fundo ainda separado. Se estourar de luz, use **filtro ND** em vez de fechar demais ou subir o obturador |
| **Perfil** | V-Log (mantém) | 10-bit 4:2:2 dá margem para a cor |
| **Formato** | C4K 4:2:2 10-bit ALL-I 400M (mantém) | Gravando na vertical, o lado de 2160 px vira a largura: o dobro do que o Reel precisa |
| **Balanço de branco** | **manual, em Kelvin** (ex.: 3200 K se a luz for quente) | Automático varia durante a fala e a cor "anda" entre os takes |
| **Foco** | AF-C com detecção de rosto/olho | O S5IIX acerta bem; manual só se você preferir |
| **Waveform** | **ligado** | É com ele que você acerta o alvo abaixo, sem chutar |

## Como acertar a exposição (30 segundos, antes de gravar)
1. Ligue o **waveform** na câmera.
2. Aponte para o seu rosto e veja onde ele cai. **Alvo: 40–45 IRE.** Hoje estava em 32.
3. Se estiver abaixo: **abra o diafragma, aumente a luz ou aproxime a luz** — nessa ordem. Só suba o ISO se não houver jeito.
4. Olhe o ponto mais claro da cena (a luminária atrás). **Não deixe passar de ~78 IRE** em V-Log — acima disso, estoura e não volta.
5. ~~Grave os 5 s de folha branca perto do rosto (`camera-00-cor`)~~ **Opcional desde 21/10 (Carlos):** luz e câmera ficam na mesma temperatura Kelvin, e a cadeia de cor da marca (`aplicar_cor.py`, primária automática por trecho) **nunca** bate o branco pela folha — tentar isso foi o que estragou o Hinton (15/10) e o livro-chatgpt (21/10). Se gravar, é só para conferir.

## Luz (é aqui que está o salto de qualidade)
- **Chave a 45°**, difusa e **mais perto** — dobrar a distância custa 2 diafragmas. Foi o que faltou.
- **O rosto tem de ser o ponto mais claro do quadro**: hoje a parede está mais clara que você. Deixe o fundo **1 a 2 diafragmas abaixo** — afaste-se da parede ou tire luz dela.
- **Contraluz/recorte** atrás de você separa a silhueta do fundo escuro; com pele escura isso importa mais ainda.
- **Negative fill** (uma superfície preta do lado oposto à chave) aprofunda a sombra **sem** subexpor — é assim que se consegue preto profundo na imagem final sem escurecer o rosto.
- **Não misture temperaturas**: a luminária avermelhada atrás é bonita como cenário, mas se ela também iluminar o seu rosto, a pele fica com cor difícil de corrigir.

## Como isto vira qualidade no Instagram
A entrega já sai como o Instagram pede (1080×1920, 25 fps, H.264 High 8-bit 4:2:0, bt709, faststart, ~10 Mbps, −14 LUFS), e o vídeo é codificado **uma única vez**. Com a exposição certa, o ganho aparece onde dói: pele sem mancha, preto profundo de verdade e imagem que aguenta o recompressor da plataforma.

## Critério de aprovação (o colorista mede, não acha)
- Rosto no vídeo final: **≥ 35 IRE** (ideal 40–50).
- Fundo **abaixo** do rosto.
- Preto: chega a 0–3 IRE **sem cortar** (nada abaixo do preto legal).
- Pelo menos um detalhe perto de 90 IRE, para a imagem não ficar chapada.
