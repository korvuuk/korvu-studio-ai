# Design System Korvu — versão para vídeo (Reels 1080×1920)

> **21/10:** PDF do CTA e cartão do CTA passaram para o design system editorial (`korvu-editorial.md`). Legendas, títulos e animações ainda seguem este arquivo.

Fonte: skill `korvu-design-system` (Korvu 2.0) + estilo de legenda "Texto Selecionado" (`00-marca/referencias/legendas/estilo-selecao.md`), adaptados para vídeo vertical visto no celular. Tokens implementados em `remotion/src/brand.ts`.

## Cores
| Token | Hex / valor | Uso no vídeo |
|---|---|---|
| Fundo | `#0D0D0D` | fundo de animações, cartelas e títulos (+ grade vertical `rgba(255,255,255,0.05)`, 6 colunas) |
| Primária (laranja) | `#E85002` | **acento único**: etapa ativa, palavra-chave, rabisco de destaque, CTA ("comenta PROMPT") |
| Secundária (roxo) | `#C108D1` | uso raro: detalhe decorativo, nunca em texto longo |
| Nude | `#D9C3AB` | números de etapa (01, 02…), rótulos, subtítulos quentes |
| Texto principal | `#F2F2F2` | títulos e palavras ditas |
| Texto secundário | `#9B9B9B` | subtítulos, palavras ainda não ditas (karaokê) |
| Seleção de texto | `#2E3033` | caixa do realce "texto selecionado" |
| Gradiente de marca | `#000000 → #C108D1 → #F16001 → #D9C3AB` | só em elementos decorativos pontuais (logo, fecho) |
- **Proibido:** fundo branco puro, violeta/índigo (paleta antiga), mais de um acento por cena.

## Superfícies (glassmorphism)
| Superfície | Estilo |
|---|---|
| Cartão padrão | fundo `rgba(255,255,255,0.04)` · borda 1.5 px `rgba(255,255,255,0.09)` · `backdrop-filter: blur(12px)` · raio **28 px** (14 px da web × 2 para vídeo) |
| Cartão ativo | fundo `rgba(232,80,2,0.12)` · borda `rgba(232,80,2,0.25)` → realça para `#E85002` no pico |
| Linha de acento no topo | 4 px `#E85002` (informação) |

## Tipografia (vídeo — legível no celular)
Fonte: **Inter** (design system) · alternativa atual do Remotion: Geist/Inter Tight (decisão pendente — ver nota).
| Nível | Tamanho | Peso | Uso |
|---|---|---|---|
| Impacto | 120–150 px, entrelinha 0.95, tracking −2% | 800 | frase-chave, fecho da animação |
| Título de etapa | 64–72 px | 800 | "Contexto", "Público"… |
| Contexto / subtítulo | 36–50 px | 500 | "quem você é" |
| Rótulo | 26–30 px, MAIÚSCULAS, tracking 0.14em | 600 | "AS 4 PARTES", "01" |
| Mínimo absoluto | 36 px | — | nada menor que isso no vídeo |

## Movimento
- Entrada: fade + subida de 12 px em 0,2 s, easing `cubic-bezier(.16,1,.3,1)`.
- Seleção "arrastada": 0,4 s, `cubic-bezier(.2,.8,.2,1)`.
- Rabisco (stroke-draw): 0,5 s, `cubic-bezier(.45,.05,.25,1)`.
- Cada elemento entra **na palavra falada que o nomeia**. Nada de movimento contínuo sem motivo; nada de bounce exagerado.

## CTA final
**Desde 21/10 no visual editorial** — tokens e medidas em `00-marca/design-system/korvu-editorial.md` §5 (fonte única).
Resumo: cartão de papel `#E7E4D9` sem canto nem sombra, centrado na área útil, base em y 1236; "comenta" em Inter 500;
a **palavra em minúsculas, SEM ponto** ("nobel"; Carlos, 21/10: o ponto pode confundir quem vai comentar) em Bricolage Grotesque 800 no acento `#E85002` (até 190 px); fio
fino e a linha de baixo em Inter 500; **sem carimbo** (Carlos, 21/10: só o cartão e o texto). Entra na palavra
"comenta" falada; as legendas da janela somem. A automação de comentários aceita "nobel", "NOBEL" e "nobel."
(`responder_comentarios.py` ignora caixa e pontuação).
Implementação: `remotion/src/components/CtaPalavra.tsx`, tokens `CTA` / `CTA_COR` / `EDITORIAL` em
`remotion/src/brand.ts`, dados em `reel-props.json.cta` (`docs/contratos.md` §7, gerado pelo `gerar_props.py`).
O estilo anterior (Geist 900 com contorno escuro e aspas, 14/10) foi substituído.

## Área útil (zonas seguras do Instagram)
Tela 1080×1920 · conteúdo importante entre **x 65–960** e **y 270–1250** (topo 270 px e base 670 px ficam para a interface do app).
Modos das cenas extras: `full` (tela cheia) · `split` (caixa 895×560 em y 905) · `card` (900×820 centralizado) — `00-marca/layouts.md`.

> Nota: o design system do CRM usa Inter; os gráficos do vídeo usam hoje Geist (parecida). Confirmar com o Carlos se o vídeo passa para Inter.
