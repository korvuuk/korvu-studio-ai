# E04 — "Uma máquina que imita a mente humana" (L08 + L09)

- **Vídeo:** 2026-10-20-geoffrey-hinton · EDL v24 (aprovada)
- **Modo:** `split` — animação deitada 16:9 na **metade de cima** do Reel (caixa **1080×608**, encostada no topo); o Carlos continua falando na metade de baixo.
- **Linhas:** L08 + L09 · saída **38,68 → 48,92 s** · **duração 10,24 s** (256 frames a 25 fps)
- **Vizinhos na faixa 2 (L07–L13):** antes vem o E03 (fotos P&B do jovem Hinton, vídeo da CBS) em corte seco; depois vem o E05 (vídeo da CBS) em corte seco. Não precisa de abertura nem de fecho "de vinheta".
- **Tempos DEFINITIVOS:** tirados da fala real do Carlos (`edicao/transcricao.json` mapeada pelo corte da EDL v24: fonte, in, cortes internos). Não são os do roteiro: ele improvisou e a "trilha no mato" da v2 saiu.
- **Exportar para:** `videos/2026-10-20-geoffrey-hinton/animacoes/E04/export/E04.html` → depois `/animar 2026-10-20-geoffrey-hinton`

Fala real (o que ele diz de fato):
- **L08** — "E se a gente criasse uma máquina que consegue imitar a mente humana?"
- **L09** — "Só que o problema, quase ninguém acreditava nessa ideia."

---

## PROMPT PARA COLAR NO CLAUDE DESIGN (claude.ai)

Crie uma animação explicativa para um Reel do Instagram que acompanha a narração palavra a palavra. Um único arquivo HTML/CSS/JavaScript, sem bibliotecas externas (só a fonte Inter do Google Fonts). Textos em português do Brasil.

### Palco e regras técnicas
- Palco **1080 × 608 px (16:9)**, escalado para caber na janela. Ele ocupa a metade de cima de um vídeo vertical 1080×1920 visto no celular, então o tamanho é 1:1 com o vídeo final: **nada de texto menor que 36 px**.
- Margens: nada essencial a menos de **100 px do topo** (a interface do Instagram cobre o alto da tela), **65 px da esquerda**, **120 px da direita** (botões do Instagram) e **50 px da base**.
- **Duração total: 10,24 s.**
- Toda a animação é calculada a partir de um tempo `t` em segundos: **nada de CSS animation, transition, setTimeout**. Exponha:
  - `window.DURACAO = 10.24`
  - `window.TIMELINE` (abaixo) — todos os tempos derivam dele;
  - `window.seek(t)`, que desenha exatamente o estado do instante `t`. A pré-visualização pode chamar `seek` num loop de `requestAnimationFrame`, mas o desenho vem só de `t`.
- Sem números aleatórios: qualquer "irregularidade" (tremor, ordem de apagar) vem de listas fixas.
- Os primeiros 0,4 s ficam parcialmente cobertos pela transição do vídeo (o painel desliza de cima): nada importante antes de 0,4 s.

### Tempos (fala real, em segundos desde o início da animação)
```js
window.TIMELINE = {
  // L08 "E se a gente criasse uma máquina que consegue imitar a mente humana?"   [0.00 → 5.68]
  inicio: 0.0,
  eSe: 0.15,          // "E se"
  criasse: 0.87,      // "criasse" — pontos começam a surgir
  maquina: 1.63,      // "máquina" — a caixa da máquina se fecha em volta dos pontos
  consegue: 2.65,     // "consegue" — 1º exemplo atravessa a máquina
  imitar: 3.41,       // "imitar" — 2º exemplo; a ligação certa engrossa
  mente: 4.41,        // "mente" — contorno de cabeça se desenha ao lado
  humana: 4.75,       // "humana?" — os dois padrões ficam iguais; "?" em rabisco
  // L09 "Só que o problema, quase ninguém acreditava nessa ideia."              [5.68 → 10.24]
  soQue: 5.81,        // "Só que" — o laranja perde força
  problema: 6.15,     // "problema"
  quase: 6.89,        // "quase"
  ninguem: 7.55,      // "ninguém" — fileira de pontos-plateia vira cinza
  acreditava: 8.45,   // "acreditava" — ligações apagam devagar
  ideia: 9.67,        // "nessa ideia." — sobra um único fio laranja
  fim: 10.24
};
```

### Cenas (cada elemento entra na palavra que o nomeia)
| tempo (s) | palavra falada | o que aparece |
|---|---|---|
| 0,00 | — | fundo `#0D0D0D` + grade vertical fina (6 colunas, branco 5%) |
| 0,15 | "E se" | um único ponto nude `#D9C3AB` acende no centro-esquerdo, pulsando de leve (é o "e se…" — uma ideia) |
| 0,87 | "criasse" | o ponto se multiplica: surgem 3 colunas de pontos (3 · 4 · 2), um a um da esquerda para a direita, ligados por linhas finas cinza `#9B9B9B` (todas com a mesma espessura) |
| 1,63 | "máquina" | em volta dos pontos se fecha um cartão de vidro (cantos 28 px, borda `rgba(255,255,255,0.09)`) com rótulo pequeno em MAIÚSCULAS **"MÁQUINA"** no canto superior — é a única palavra escrita nesta parte |
| 2,65 | "consegue" | 1º exemplo: um pulso de luz entra pela esquerda (bolinha) e percorre um caminho pelas ligações até um ponto da última coluna; o caminho percorrido fica laranja `#E85002` por um instante; as ligações que não foram usadas ficam um pouco mais fracas |
| 3,41 | "imitar" | 2º exemplo pelo mesmo caminho: agora a ligação certa **engrossa** (1 px → 4 px, laranja) e duas ligações erradas **somem** (opacidade → 0) — a máquina está aprendendo |
| 4,41 | "mente" | à direita do cartão, um **contorno de cabeça humana genérica de perfil** (traço fino nude, estilo ícone, sem rosto, sem nenhuma pessoa real) se desenha em 0,5 s (stroke-draw); dentro dele acendem pontos e ligações no **mesmo desenho** da máquina |
| 4,75 | "humana?" | entre o cartão e a cabeça aparece um sinal "≈" e, em cima, um **"?" grande em rabisco laranja** (pincel seco, 0,5 s) — a pergunta |
| 5,81 | "Só que" | tudo congela; o laranja das ligações começa a perder saturação (laranja → nude) |
| 6,15 | "problema" | a cabeça e o "≈" recuam (fade + escala 0,96); a máquina fica sozinha no centro |
| 6,89 | "quase" | embaixo da máquina entra uma fileira de **12 pontos-plateia** (círculos nude 22 px, abstratos, nada de rostos), da esquerda para a direita |
| 7,55 | "ninguém" | 11 dos 12 pontos ficam cinza escuro, um a um (ordem fixa, 0,08 s entre cada); **um só continua laranja** (quase ninguém = um acreditava) |
| 8,45 | "acreditava" | as ligações da máquina **apagam devagar**, uma por vez (ordem fixa), até 9,6 s |
| 9,67 | "nessa ideia." | resta acesa só **uma ligação laranja fina**, pulsando fraco, ligada ao único ponto laranja da plateia — a ideia não morreu (é a ponte para "ele não desistiu" logo depois) |
| 10,24 | — | segura esse quadro até o fim (o vídeo corta seco para a cena seguinte) |

### Design system (Korvu)
- Fundo `#0D0D0D` com linhas verticais finas de grade (6 colunas, 1 px, branco 5%).
- Texto `#F2F2F2`; secundário `#9B9B9B`; rótulos e pontos em nude `#D9C3AB`; **acento único laranja `#E85002`**. Proibido violeta/índigo e fundo branco puro.
- Vidro: fundo `rgba(255,255,255,0.04)`, borda 1,5 px `rgba(255,255,255,0.09)`, blur 12 px, cantos 28 px.
- Inter: rótulos MAIÚSCULOS 600, tracking 0,14em, 36 px.
- Rabisco à mão (pincel seco, 2–3 traços irregulares), desenhado em 0,5 s, easing cubic-bezier(.45,.05,.25,1).
- Entradas: fade + subida de 12 px em 0,2 s, easing cubic-bezier(.16,1,.3,1). Sem bounce, sem movimento contínuo sem motivo.

### Proibido
- Escrever "rede neural", "neurônio", "IA" ou repetir a fala em texto (a legenda já faz isso, logo abaixo do painel).
- Pessoas reais, fotos, rostos realistas. A cabeça é um contorno de ícone genérico.
- Logos de qualquer empresa.

Entregue o código completo num único arquivo.
