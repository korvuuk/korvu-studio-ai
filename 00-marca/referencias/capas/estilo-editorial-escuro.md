# Estilo de capa — "editorial escuro" (referência 1)

> Imagem original: coloque o arquivo nesta pasta como `referencia-01.jpg` (o Carlos mandou no chat em 2026-09-16).
> É **inspiração de estilo** — nunca copiar o @, a foto, o selo nem o rodapé do autor da referência.
> Convive com `../legendas/estilo-selecao.md`: aquele manda nas legendas do vídeo, este na **capa**.

## O que a referência tem (leitura da imagem)

| Camada | Descrição |
|---|---|
| **Fundo** | Quase preto (#0A0A0A–#111), com uma letra/marca gigante em relevo muito sutil atrás — textura, não desenho |
| **Assunto** | Um busto de pedra rachado, recortado ao centro, **luz lateral dura**: meio rosto na luz, meio na sombra; fundo limpo, sem cenário |
| **Título** | Sans grotesca **muito bold**, entrelinha apertada, em **duas cores**: cinza (#9B9B9B) na parte de contexto e branco (#F2F2F2) na parte que importa ("não está" / "errado") |
| **Palavra-chave** | Uma única palavra em **serifa itálica gigante** ("vazio.") — o contraste entre grotesca bold e serifa itálica é a assinatura do layout |
| **Apoio** | Frases curtas empilhadas em itálico cinza ("Propósito. Presença. Postura.") num canto, pequenas |
| **Remate** | Linha de fecho centrada embaixo: itálico cinza + bold branco ("Design não é pra ser bonito / É pra ser certeiro") |
| **Molduras de UI** | Barra fina no topo com 3 palavras espaçadas + rodapé em "pílula" arredondada com avatar e @ à esquerda e função/ano à direita |
| **Detalhes** | Selo circular com texto em círculo e um botão redondo com seta — pontuais, pequenos, nunca competem com o rosto |

## Como vira capa da Korvu

- **Assunto = o Carlos**, do frame escolhido do próprio vídeo (regra da marca: nenhuma pessoa real além dele). O busto da referência é só a lógica de recorte e luz: rosto grande, centrado, fundo escuro e limpo.
- **Paleta:** fundo `#0D0D0D`, texto branco `#F2F2F2` + cinza `#9B9B9B`, acento `#E85002` só quando precisar chamar (rabisco ou a palavra-chave). Tokens em `remotion/src/brand.ts`.
- **Tipografia:** o par da referência — grotesca bold (título, Geist) + **uma** palavra em serifa itálica (**Playfair Display itálico**, token `FONTE.serifa` no `brand.ts`; passe a palavra em `serifa` no título da capa ou com `--serifa`). Nunca mais de uma palavra em serifa, e nunca serifa nas legendas do vídeo. Por enquanto a serifa sai no **mesmo corpo** do resto: a medição de largura é feita na sans, então aumentá-la estouraria a linha.
- **Texto:** 3–6 palavras no total, tiradas do hook, **sem pontuação nem caracteres especiais** (mesma regra das legendas, pedido do Carlos em 2026-09-16).
- **Rodapé em pílula** com `@korvu_oficial` é opcional e discreto; a barra de navegação do topo da referência **não** se usa (rouba espaço e o Instagram já tem UI ali).
- O escurecimento do fundo atrás do texto é gradiente suave, nunca uma caixa sólida.

## Formato (o que o Instagram faz com a capa)

| Onde aparece | Recorte | Consequência |
|---|---|---|
| **Arquivo da capa** | **1080×1920 (9:16)**, PNG ou JPG — o mesmo enquadramento do Reel | é o que se envia como `cover_url` |
| **Grade do perfil** | **3:4 central (1080×1440)** | rosto e título **têm que caber aqui**, senão somem na grade |
| **Reels em tela cheia** | 9:16 inteiro, com UI por cima | deixar livre: ~270 px no topo e ~670 px embaixo (@, legenda, botões) |

Zona segura prática: **título e rosto dentro de 1080×1440 centrado**, e nada essencial abaixo de y≈1250.
