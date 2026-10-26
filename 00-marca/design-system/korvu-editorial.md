# Design System Korvu — editorial (PDF do CTA + textos na tela)

> **Decisão do Carlos, 21/10** (`docs/decisoes.md` §4): molde da referência "portfolio" que ele mandou — papel bege,
> preto e UM acento, títulos em minúsculas com ponto, fotos em P&B, fios finos (o carimbo de bolinha da referência foi tirado em 21/10).
> Fonte de título escolhida por ele: **Bricolage Grotesque**. **Modelo APROVADO pelo Carlos em 21/10** (PDF do LIVRO + cartão do CTA), com a palavra do CTA sem ponto. Este arquivo é a **fonte única dos tokens**; o código
> copia daqui (`scripts/gerar_material_pdf.py` → `CSS`, `remotion/src/brand.ts` → `EDITORIAL`).
> Substitui, no PDF e nos textos de tela, o que `identidade-visual.md` (provisório) e `korvu-video.md` diziam de
> fonte e cor. Legendas faladas ("Texto Selecionado") e grade de vídeo continuam em `korvu-video.md`.

## 1. O que faz o estilo (não negociável)
1. **Três cores e só.** Papel, tinta, acento. Nada de degradê, sombra, brilho, vidro, canto arredondado.
2. **Título em minúsculas, pesado, linhas encostadas, termina em ponto** ("os 50 comandos.", "valeu."). **Exceção: a palavra-chave do CTA nunca leva ponto** ("comenta nobel", não "nobel.").
3. **Números grandes de seção** no acento: "1.", "2.", "3.".
4. **Sem carimbo** (a bolinha com frase em volta da referência): o Carlos tirou do CTA e do PDF em 21/10 — "vai ficar muito poluído". Só o conteúdo.
5. **Muito vazio.** Margem larga, texto em coluna estreita, alinhado à grade. Pouca coisa por página.
6. **Micro-informação nos cantos** (marca, @, página) em letra pequena, e **fios de 0,5 pt** separando áreas.
7. **Fotos em preto e branco**, retangulares, sem moldura.
8. **Sem caixa alta** em título; caixa alta só em rótulo minúsculo (≤ 8 pt), e mesmo assim de leve.
9. **Autoria = "Korvu" / "@korvu_oficial".** O nome pessoal do Carlos não entra no material (decisão de 21/10).

## 2. Cores
| Token | Hex | Uso |
|---|---|---|
| `papel` | `#E7E4D9` | fundo de toda página do PDF e do cartão do CTA |
| `papel-2` | `#DCD8CB` | caixa "copie e cole", código em linha |
| `tinta` | `#111111` | texto, fios, caixa escura |
| `tinta-2` | `#5A5852` | texto secundário, fontes, rodapé |
| `acento` | `#E85002` | laranja da Korvu (aprovado no CTA em 14/10): títulos, números, links. **Só um acento.** |

Regra de uso: título grande no acento **ou** em tinta — nunca os dois no mesmo título, exceto o ponto final.

## 3. Tipografia
| Papel | Fonte | Peso | Detalhe |
|---|---|---|---|
| Título (display) | **Bricolage Grotesque** | 800 | minúsculas · entrelinha 0,88 · tracking −0,03 em · `opsz` automático |
| Número de seção | Bricolage Grotesque | 800 | "1." no acento, do tamanho do título da seção ou maior |
| Texto | **Inter** | 400 / 600 | entrelinha 1,5 · negrito 600 (nunca 800 no corrido) |
| Rótulo / meta | Inter | 500 | 7–8 pt no PDF · minúsculas ou caixa alta com tracking 0,12 em |
| Comando para copiar | Inter | 500 | **sem fonte mono** (mono = cara de terminal, o que ele não quer) |

Google Fonts: `Bricolage+Grotesque:opsz,wght@12..96,400..800` + `Inter:wght@400;500;600`.
Remotion: `@remotion/google-fonts/BricolageGrotesque` + `Inter`.

## 4. PDF do material (A4 em pé — é lido no celular)
| Elemento | Medida |
|---|---|
| Margens | 18 mm laterais · 22 mm topo · 22 mm base |
| Cabeçalho (todas as págs.) | esq. "korvu." · dir. "@korvu_oficial" · Inter 7 pt |
| Rodapé (todas as págs.) | esq. "material gratuito · palavra LIVRO" · dir. "1/5" · fio 0,5 pt em cima |
| Capa (topo da pág. 1) | rótulo 8 pt → **título 56 pt** no acento, minúsculas, ponto final → fio → abertura em 13 pt, coluna de ~125 mm. Sem carimbo |
| Seção (`##`) | fio 0,5 pt em cima · número "1." no acento 30 pt + título em tinta 22 pt, minúsculas |
| Subtítulo (`###`) | Inter 600 11,5 pt |
| Lista numerada | número em Bricolage 800 no acento, alinhado à esquerda, sem bolinha |
| Lista com marcador | traço "–" em tinta-2 |
| Copie e cole (```) | fundo `papel-2`, sem canto, rótulo "copie e cole" 7 pt no acento, texto Inter 500 11 pt |
| Aviso (`>`) | fio de 2 pt no acento à esquerda, sem fundo |
| Caixa (`:::caixa`) | fundo `tinta`, texto `papel`, rótulo no acento, sem canto |
| Fontes | 8 pt em tinta-2, no fim |
| Fecho (última pág.) | "valeu." 40 pt no acento + "material da korvu / @korvu_oficial" — sem carimbo |

## 5. Textos na tela do vídeo (1080×1920)
| Elemento | Estilo |
|---|---|
| **CTA da palavra** | cartão `papel`, sem canto, largura até 860 px, centrado na área útil, base em y 1236 (zona segura). "comenta" Inter 500 42 px em tinta · **palavra em minúsculas, SEM ponto** (a palavra-chave nunca leva ponto: confunde quem vai comentar — Carlos, 21/10), Bricolage 800, acento, até a largura útil do cartão (teto 190 px — com 230 subia até a boca) · fio fino · linha de baixo Inter 500 32 px em tinta. **Sem carimbo** — só o cartão e o texto (Carlos, 21/10: "vai ficar muito poluído") |
| Título / cartela | Bricolage 800, minúsculas, ponto final, entrelinha 0,88; em vídeo claro vai sobre cartão `papel`, nunca com contorno grosso |
| Movimento | cartão sobe 24 px + aparece em 6 frames; palavra entra com mola curta (sem bounce exagerado); nada girando |

## 6. Proibido
- Degradê laranja→rosa, roxo, glassmorphism, contorno grosso em texto, fonte mono, caixa alta em título.
- Mais de um acento; acento em texto longo.
- Nome pessoal do Carlos no material.
