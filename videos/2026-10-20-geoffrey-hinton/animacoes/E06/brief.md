# E06 — 2012: o sistema que reconheceu imagens (L12 + L13)

- **Vídeo:** 2026-10-20-geoffrey-hinton · EDL v24 (aprovada)
- **Modo:** `split` — animação deitada 16:9 na **metade de cima** do Reel (caixa **1080×608**, encostada no topo); o Carlos continua falando na metade de baixo.
- **Linhas:** L12 + L13 · saída **63,60 → 74,28 s** · **duração 10,68 s** (267 frames a 25 fps)
- **Vizinhos:** antes vem o E12 (Hinton, "I always thought I was right", CBS) em corte seco; depois a L14 com o Carlos em tela cheia (o painel sobe e some).
- **Tempos DEFINITIVOS:** fala real do Carlos (`edicao/transcricao.json` mapeada pelo corte da EDL v24). O texto do roteiro era outro ("imagens com uma precisão impressionante"); ele disse "imagem de forma precisa e impecável".
- **Dado (com fonte):** desafio ImageNet 2012, taxa de erro top-5 — sistema do Hinton e dos dois alunos (SuperVision/AlexNet) **0,15315 = 15,3 %** × segundo colocado **0,26172 = 26,2 %**. Fonte primária: https://image-net.org/challenges/LSVRC/2012/results.html (`material/fontes.json`, `material/dossie.md`).
- **Crédito na tela:** "Fonte: ImageNet / Stanford Vision Lab (dado)" — **quem desenha é o Remotion** (vem do `credito` do overlay na EDL), no canto inferior esquerdo do painel. A animação **não** escreve o crédito e deixa livre esse canto (ver margens).
- **Atenção à fala:** ele diz "impecável", mas o sistema errava 15,3 %. A tela mostra o número real (menos erro que todo mundo), **nunca** "100 %", "zero erro" ou a palavra "impecável" escrita.
- **Exportar para:** `videos/2026-10-20-geoffrey-hinton/animacoes/E06/export/E06.html` → depois `/animar 2026-10-20-geoffrey-hinton`

Fala real:
- **L12** — "Em 2012, ele juntou com dois alunos"
- **L13** — "Ele desenvolveu um sistema capaz de reconhecer imagem de forma precisa e impecável"

---

## PROMPT PARA COLAR NO CLAUDE DESIGN (claude.ai)

Crie uma animação explicativa para um Reel do Instagram que acompanha a narração palavra a palavra. Um único arquivo HTML/CSS/JavaScript, sem bibliotecas externas (só a fonte Inter do Google Fonts). Textos em português do Brasil.

### Palco e regras técnicas
- Palco **1080 × 608 px (16:9)**, escalado para caber na janela. Ele ocupa a metade de cima de um vídeo vertical 1080×1920 visto no celular, então o tamanho é 1:1 com o vídeo final: **nada de texto menor que 36 px**.
- Margens: nada essencial a menos de **100 px do topo**, **65 px da esquerda**, **120 px da direita** e **50 px da base**. **Deixe livre um retângulo de 460×60 px no canto inferior esquerdo** (lá entra o crédito da fonte, desenhado depois).
- **Duração total: 10,68 s.**
- Toda a animação é calculada a partir de um tempo `t` em segundos: **nada de CSS animation, transition, setTimeout**. Exponha:
  - `window.DURACAO = 10.68`
  - `window.TIMELINE` (abaixo) — todos os tempos derivam dele;
  - `window.seek(t)`, que desenha exatamente o estado do instante `t`. A pré-visualização pode chamar `seek` num loop de `requestAnimationFrame`, mas o desenho vem só de `t`.
- Sem números aleatórios.
- Os primeiros 0,4 s ficam parcialmente cobertos pela transição do vídeo (o painel desliza de cima).

### Tempos (fala real, em segundos desde o início da animação)
```js
window.TIMELINE = {
  // L12 "Em 2012, ele juntou com dois alunos"                                       [0.00 → 3.44]
  inicio: 0.0,
  ano: 0.38,          // "2012"
  juntou: 1.80,       // "juntou" — 1º ponto (ele)
  dois: 2.52,         // "dois"
  alunos: 2.80,       // "alunos" — 2º e 3º pontos
  // L13 "Ele desenvolveu um sistema capaz de reconhecer imagem de forma precisa e impecável" [3.44 → 10.68]
  desenvolveu: 3.92,  // "desenvolveu" — os três se ligam
  sistema: 4.68,      // "sistema" — vira um bloco/cartão
  capaz: 5.54,        // "capaz"
  reconhecer: 6.50,   // "reconhecer" — imagens entram e recebem etiqueta
  imagem: 7.42,       // "imagem"
  forma: 8.42,        // "de forma" — entra o gráfico de erro
  precisa: 8.84,      // "precisa" — a barra dele encolhe
  impecavel: 9.74,    // "e impecável" — rabisco sob 15,3 %
  fim: 10.68
};
```

### Cenas (cada elemento entra na palavra que o nomeia)
| tempo (s) | palavra falada | o que aparece |
|---|---|---|
| 0,00 | — | fundo `#0D0D0D` + grade vertical fina (6 colunas, branco 5%) |
| 0,38 | "2012" | **"2012"** grande (Inter 800, ~150 px, `#F2F2F2`) no centro, com o realce de "texto selecionado" (caixa `#2E3033` crescendo da esquerda para a direita, alças de cursor) |
| 1,80 | "juntou" | o "2012" encolhe e sobe para o canto superior esquerdo como rótulo (36 px); no centro acende **um ponto laranja** `#E85002` (ele) |
| 2,52 | "dois" | ao lado entram **dois pontos nude** `#D9C3AB` (os alunos) — círculos abstratos de 40 px, sem rostos, sem nomes |
| 2,80 | "alunos" | os três se aproximam, formando um triângulo |
| 3,92 | "desenvolveu" | linhas finas ligam os três pontos e se ramificam em 3 colunas de pontos (o mesmo desenho de "máquina" usado antes no vídeo: 3 · 4 · 2) |
| 4,68 | "sistema" | em volta fecha-se um cartão de vidro (cantos 28 px) com rótulo MAIÚSCULO **"SISTEMA"** |
| 5,54 | "capaz" | o cartão desliza para a esquerda e ocupa ~40 % da largura |
| 6,50 | "reconhecer" | da direita entram 4 **ícones planos de imagem** em fila (gato, carro, flor, cachorro — traço simples nude, estilo ícone, nada de foto); cada um passa pelo cartão e sai com uma **etiqueta** com ✓ laranja ("gato", "carro", "flor", "cachorro"), 0,2 s entre cada |
| 7,42 | "imagem" | o último ícone recebe a etiqueta e os quatro ficam alinhados, um pouco apagados |
| 8,42 | "de forma" | cartão e ícones saem para a esquerda (fade + 12 px); entra o gráfico: rótulo **"DESAFIO IMAGENET 2012 · TAXA DE ERRO"** (36 px, nude) e **duas barras horizontais do mesmo tamanho**: "2º colocado" (cinza `#9B9B9B`, valor **26,2 %**) e "Sistema dele" (laranja `#E85002`, contando de 26,2 %) |
| 8,84 | "precisa" | a barra laranja **encolhe** em 0,6 s até a proporção de 15,3 / 26,2, e o número dela desce contando até **15,3 %**; abaixo, pequeno, "menos é melhor" (cinza, 36 px) |
| 9,74 | "e impecável" | **rabisco laranja à mão** sob o "15,3 %" (pincel seco, 0,5 s) |
| 10,68 | — | segura o gráfico até o fim |

### Design system (Korvu)
- Fundo `#0D0D0D` com linhas verticais finas de grade (6 colunas, 1 px, branco 5%).
- Texto `#F2F2F2`; secundário `#9B9B9B`; rótulos e números em nude `#D9C3AB`; **acento único laranja `#E85002`**. Proibido violeta/índigo e fundo branco puro.
- Vidro: fundo `rgba(255,255,255,0.04)`, borda 1,5 px `rgba(255,255,255,0.09)`, blur 12 px, cantos 28 px.
- Inter: números/impacto 800 (tracking −2%), texto 500, rótulos MAIÚSCULOS 600 com tracking 0,14em. **Nada menor que 36 px.**
- Estilo "texto selecionado": realce `#2E3033` crescendo da esquerda para a direita, com duas alças (linha 2 px + bolinha 8 px).
- Rabisco à mão (2–3 traços irregulares + rabicho), 0,5 s, easing cubic-bezier(.45,.05,.25,1).
- Entradas: fade + subida 12 px em 0,2 s, easing cubic-bezier(.16,1,.3,1). Sem bounce.

### Proibido
- Pessoas reais, fotos, rostos, nomes dos alunos.
- Logos (nem do ImageNet, nem de Stanford, nem de universidades ou empresas). "ImageNet" aparece só como nome do desafio, em texto da marca.
- Escrever "impecável", "100 %" ou "zero erro". Escrever o crédito (vem depois).

Entregue o código completo num único arquivo.
