# Estilo de legenda e título — "Texto Selecionado" (referência 1)

> Imagem original: coloque o arquivo nesta pasta como `referencia-01.jpg`.
> É **inspiração de estilo** — nunca copiar o @, a foto ou o rodapé do autor da imagem.
> Status: **ativo, provisório** até o design system (`00-marca/design-system/`) confirmar fonte e cor de acento.

## Anatomia (3 níveis de texto)

| Nível | Uso | Tipografia | Cor | Detalhe |
|---|---|---|---|---|
| **1. Contexto** | frase que prepara a ideia | sans regular/medium, ~44–52 px (1080 de largura), 1–2 linhas, centrada | branco `#F2F2F2` | Algumas palavras com **realce de seleção de texto**: caixa `#2E3033` atrás das palavras + 2 alças de cursor (linha vertical 2 px + bolinha 8 px) no início e no fim |
| **2. Impacto** | a frase que fica na cabeça | sans grotesca **muito bold** (800–900), ~120–150 px, entrelinha 0,95, tracking −2% | início em cinza `#9B9B9B`, palavras-chave em branco `#F2F2F2` | no máximo 2 linhas, 3–6 palavras |
| **3. Rabisco** | sublinhar a palavra de destaque | traço à mão (SVG, pincel seco) | cinza `#A0A0A0` (ou acento do design system) | desenhado por baixo da palavra-chave, levemente inclinado, com "rabicho" final |

- **Fundo (títulos, cartelas e animações em tela cheia):** quase preto `#111111` com linhas verticais finas de grade (1 px, branco a 4–6% de opacidade, 6–7 colunas).
- **Legendas sobre o vídeo:** sem caixa de fundo; sombra suave (`0 2px 12px rgba(0,0,0,.55)`) para leitura.
- **Fonte provisória:** Geist (Google Fonts) — alternativa Inter Tight 800. Confirmar com o design system.

## Animação (Remotion, sincronizada com as palavras faladas)

1. **Palavras entram no ritmo da fala** (timestamps da transcrição): fade + subida de 12 px em 6 frames.
2. **Karaokê de cor:** a palavra sendo dita passa de `#9B9B9B` para `#F2F2F2` (4 frames).
3. **Seleção "arrastada":** o realce do nível 1 cresce da esquerda para a direita como um cursor selecionando texto (10–14 frames, easing `cubic-bezier(.2,.8,.2,1)`), com as alças acompanhando.
4. **Rabisco:** stroke-draw (`strokeDashoffset`) em 12–16 frames, começando quando a palavra-chave é dita.
5. **Saída:** fade 4 frames na troca de página.

## Onde aplicar

| Peça | Como |
|---|---|
| **Legendas do Reel** | **texto = o roteiro, não a transcrição** (ele come sílabas: o ASR ouviu "pronto" onde o roteiro diz "PROMPT"); **sem pontuação nem caracteres especiais** (`"`, `,`, `.`, `(`, `)`…) — regra do Carlos, 2026-09-16. Página de 2–4 palavras, **78 px** (destaque **132 px**), centro do bloco em y 1150 (zona baixa, acima da UI do Instagram); palavras-chave do roteiro (marcadas `**assim**` na FALA) sobem para o nível 2. Páginas de uma palavra curta juntam-se à vizinha. *(tamanhos aumentados 20% a pedido do Carlos, 2026-09-16)* |
| **Título do hook (0–3 s)** | nível 1 (setup) + nível 2 (impacto) + rabisco na palavra-chave |
| **Cartelas / cards** | fundo `#111` com grade, níveis 1 e 2 |
| **Capa** | nível 2 + rabisco, dentro da zona central 1080×1440 |

## Zonas seguras (1080×1920)
Topo livre ~270 px · base livre ~670 px (legenda do post e botões) · laterais ~65 px (direita ~120 px). Legendas do vídeo entre **y 1150–1250** (acima da zona de UI) ou centradas no terço médio quando o rosto permitir.
