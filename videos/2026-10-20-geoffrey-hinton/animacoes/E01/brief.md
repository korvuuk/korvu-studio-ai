# E01 — A ligação de madrugada (L20)

- **Vídeo:** 2026-10-20-geoffrey-hinton · EDL v24 (aprovada)
- **Modo:** `split` — animação deitada 16:9 na **metade de cima** do Reel (caixa **1080×608**, encostada no topo); o Carlos continua falando na metade de baixo.
- **Linha:** L20 inteira · saída **107,16 → 113,92 s** · **duração 6,76 s** (169 frames a 25 fps)
- **Vizinhos na faixa 4 (L18–L25):** antes vem o E08 (Hinton na BBC) em corte seco; depois, em corte seco, o E09 (Hinton contando a ligação do Nobel: "could be a prank"). O E01 termina **com o celular ainda tocando** — a resposta de quem ligou é o E09.
- **Tempos DEFINITIVOS:** fala real do Carlos (`edicao/transcricao.json` mapeada pelo corte da EDL v24, take L20-T2 com dois cortes internos).
- **Exportar para:** `videos/2026-10-20-geoffrey-hinton/animacoes/E01/export/E01.html` → depois `/animar 2026-10-20-geoffrey-hinton`

Fala real:
- **L20** — "E um ano e meio depois, ele recebeu uma ligação às duas e meia da manhã."

> **DIVERGÊNCIA DE HORÁRIO — para o Carlos decidir:** o roteiro e o dossiê (entrevista oficial do Nobel por telefone,
> NobelPrize.org) dizem **"duas da manhã"**; na gravação aprovada ele disse **"duas e meia"**. Por isso a animação
> **não mostra número de hora nenhum** (nada de "02:00" nem "02:30", diferente do que a tabela do roteiro pedia):
> a madrugada é contada pela lua, pelo quarto escuro e pela tela acendendo. Assim a imagem não contradiz nem a fala
> nem a fonte. A legenda segue o roteiro ("duas da manhã") e vai divergir da voz — se quiser, troque a legenda ou
> regrave só essa linha.

---

## PROMPT PARA COLAR NO CLAUDE DESIGN (claude.ai)

Crie uma animação explicativa para um Reel do Instagram que acompanha a narração palavra a palavra. Um único arquivo HTML/CSS/JavaScript, sem bibliotecas externas (só a fonte Inter do Google Fonts). Textos em português do Brasil.

### Palco e regras técnicas
- Palco **1080 × 608 px (16:9)**, escalado para caber na janela. Ele ocupa a metade de cima de um vídeo vertical 1080×1920 visto no celular, então o tamanho é 1:1 com o vídeo final: **nada de texto menor que 36 px**.
- Margens: nada essencial a menos de **100 px do topo**, **65 px da esquerda**, **120 px da direita** e **50 px da base**.
- **Duração total: 6,76 s.**
- Toda a animação é calculada a partir de um tempo `t` em segundos: **nada de CSS animation, transition, setTimeout**. Exponha:
  - `window.DURACAO = 6.76`
  - `window.TIMELINE` (abaixo) — todos os tempos derivam dele;
  - `window.seek(t)`, que desenha exatamente o estado do instante `t`. A pré-visualização pode chamar `seek` num loop de `requestAnimationFrame`, mas o desenho vem só de `t`.
- Sem números aleatórios: a vibração do celular é uma função de `t` (ex.: seno com amplitude fixa), não `Math.random`.
- Os primeiros 0,4 s ficam parcialmente cobertos pela transição do vídeo (o painel desliza de cima).

### Tempos (fala real, em segundos desde o início da animação)
```js
window.TIMELINE = {
  // L20 "E um ano e meio depois, ele recebeu uma ligação às duas e meia da manhã."  [0.00 → 6.76]
  inicio: 0.0,
  umAno: 0.32,        // "um ano" — calendário começa a folhear
  meio: 0.86,         // "e meio"
  depois: 1.10,       // "depois" — calendário para; luz cai
  ele: 1.86,          // "ele" — quarto escuro, celular na mesinha
  recebeu: 2.34,      // "recebeu" — tela acende
  ligacao: 3.44,      // "ligação" — chamada recebida, vibrando
  as: 4.24,           // "às"
  duasEMeia: 4.60,    // "duas e meia" (dita devagar, até 5.82)
  manha: 5.96,        // "da manhã." — lua no auge; segue tocando
  fim: 6.76
};
```

### Cenas (cada elemento entra na palavra que o nomeia)
| tempo (s) | palavra falada | o que aparece |
|---|---|---|
| 0,00 | — | fundo `#0D0D0D` + grade vertical fina (6 colunas, branco 5%); à esquerda, um **calendário de parede** em vidro (cartão 28 px de canto) com o mês em MAIÚSCULAS nude: **"MAI 2023"** |
| 0,32 | "um ano" | as folhas do calendário **viram rápido** de baixo para cima, uma por mês (MAI 2023 → JUN → … → OUT 2024, 17 folhas, ritmo acelerando) |
| 0,86 | "e meio" | as folhas continuam virando |
| 1,10 | "depois" | o calendário para em **"OUT 2024"**; selecionado com o realce de "texto selecionado" (caixa `#2E3033`, alças de cursor) |
| 1,86 | "ele" | a cena escurece (o calendário recua em fade); à direita, uma **janela** com **lua crescente** nude e 5 estrelinhas fixas; embaixo, o tampo de uma mesinha de cabeceira com um **celular genérico deitado, tela apagada** (retângulo preto de cantos arredondados, sem marca) |
| 2,34 | "recebeu" | a tela do celular **acende** com um brilho laranja suave que ilumina a mesinha (gradiente radial `rgba(232,80,2,0.25)`) |
| 3,44 | "ligação" | na tela: ícone de telefone grande + **"Chamada recebida"** (36–40 px, `#F2F2F2`); dois botões redondos (verde-acinzentado dessaturado para atender, cinza para recusar — sem vermelho/verde saturados, nada de interface de marca); o celular **vibra** (tremor lateral de 3 px, função de `t`) com 3 arcos de vibração dos dois lados, em pulsos de 0,5 s |
| 4,24 | "às" | o brilho da tela pulsa no ritmo do toque |
| 4,60 | "duas e meia" | a **lua** ganha destaque (escala 1 → 1,1, halo nude); o quarto fica mais escuro em volta da tela — a madrugada. **Nenhum número de hora em lugar nenhum** |
| 5,96 | "da manhã." | segue tocando e vibrando; rabisco laranja à mão em volta do celular (pincel seco, 0,5 s) |
| 6,76 | — | último quadro **ainda tocando** (o vídeo corta seco para o Hinton contando a ligação) |

### Design system (Korvu)
- Fundo `#0D0D0D` com linhas verticais finas de grade (6 colunas, 1 px, branco 5%).
- Texto `#F2F2F2`; secundário `#9B9B9B`; rótulos, lua e meses em nude `#D9C3AB`; **acento único laranja `#E85002`**. Proibido violeta/índigo e fundo branco puro.
- Vidro: fundo `rgba(255,255,255,0.04)`, borda 1,5 px `rgba(255,255,255,0.09)`, blur 12 px, cantos 28 px.
- Inter: texto 500, rótulos MAIÚSCULOS 600 com tracking 0,14em. **Nada menor que 36 px.**
- Estilo "texto selecionado": realce `#2E3033` crescendo da esquerda para a direita, com duas alças (linha 2 px + bolinha 8 px).
- Rabisco à mão (2–3 traços irregulares + rabicho), 0,5 s, easing cubic-bezier(.45,.05,.25,1).
- Entradas: fade + subida 12 px em 0,2 s, easing cubic-bezier(.16,1,.3,1). Sem bounce.

### Proibido
- Qualquer horário escrito ("02:00", "02:30", "2h"…), relógio com ponteiros numa hora específica.
- Nome de quem liga, número de telefone, código de país, bandeira, "Suécia", "Nobel" — a revelação vem na cena seguinte.
- Pessoas, mãos realistas, logos de fabricante ou de sistema operacional no celular.

Entregue o código completo num único arquivo.
