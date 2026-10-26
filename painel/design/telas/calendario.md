# Calendário — `/calendario`

> **O Carlos abre isto para** ver o que sai em cada dia, onde, as vagas que ainda estão livres e
> se cada post da fila vai mesmo sair.

- Maquete: `calendario.html` (vista Mês; a Semana está na faixa "fora da tela"). Fonte do desenho:
  `painel/referencias/claude-design/telas-2026-10-23/Calendario.dc.html`.
- Componentes: livro §11.12 (evento, linha "Portões:"), §15.2 (mês, semana, vaga, colunas, chave-valor, atalho,
  segmentado).

## Hierarquia
1. **sem título de página** (decisão de 24/10: o item do menu já diz onde se está; o `h1` "Calendário" fica só para leitor de tela); a página abre na navegação do mês. Sem "Agendar publicação" (24/10).
2. Navegação (Hoje, ‹ ›, "Outubro 2026" ou "18 – 24 out 2026"), legenda e Mês | Semana.
3. Calendário: **largura toda até 1919 px**; a partir de **1920 px** (a largura do artboard), 9 colunas, como no desenho.
4. Fila · Melhores horários: **até 1919 px descem para baixo do mês, lado a lado** (2 colunas); a partir de 1920 px, a
   coluna de 3 à direita (`.k-xxl-9` / `.k-xxl-3` + `.k-lado--xxl`).
5. **Nenhum evento corta com reticências**: horário · estado, título e canais quebram em até 2 linhas; o `title` do
   evento continua como apoio. Conferido no navegador a 1024, 1280, 1440, 1600, 1919, 1920 e 2200: 0 cortes e nada
   saindo da própria caixa (antes: 6 cortes a 1440, 22 a 1600 com o painel ao lado, 2 a 1920).

## Dados
| O quê | Fonte |
|---|---|
| Publicados (dia, hora, canais) | `07-publicados/*/post.json` (`publicado_em`, `plataformas`); no banco, `publicacoes` (hoje sem o Livro ChatGPT A) |
| Agendados (dia, hora, canais, modo, palavra) | `fila` (`publicar_em`, `plataformas`, `trial`, `palavra`) |
| Linha de portões de cada post da fila | livro §11.12 / §15.1: hoje "Legado · sem selo" nos 5 (`fila.legado`, sem `gauntlet` no `pacote.json`) |
| Vagas | `_controle/calendario.md` → `vagas_semanais` (dom 19:00, ter 21:00, qua 21:00); vaga livre = dia de vaga **daqui para frente** sem post (3 e 4 nov). Na semana, a vaga passada sem post vira nota ("vaga sem post", qua 21) |
| Hora | horário de Londres (`Europe/London`, o mesmo do `publicar.py`); 25 out é o fim do horário de verão e a fila já está em GMT |
| Melhores horários | print 15 de `_controle/perfil/prints-2026-10-17/` (app do Instagram, GMT+1, **dia mostrado: quinta-feira**): altura de cada barra medida em pixels ÷ a mais alta = 72 · 34 · 33 · 69 · 92 · 99 · 100 · 99; picos escritos no próprio app; vagas do `calendario.md` |
| Fila (números) | `fila`: 5 agendados; 0 aguardando portão (os 5 são legado); 0 sem horário (o único pronto é o teste de cor, que não sai) |

## Mês
- 6 semanas a partir do domingo (27 set – 7 nov). Dia de fora do mês em `surface-hover`; passado com o número em `ink-2`;
  hoje com o número em pílula `accent`.
- Evento: capa 18×32, "17:03 · Publicado", nome, canais, e nos posts da fila a linha compacta de portões (cadeado + chip;
  "Portões:" para leitor de tela). Publicado = fundo `surface-hover`. A barra da esquerda é o canal: Instagram `accent`,
  Instagram + Facebook `ink`, Facebook `chart-5` — com o canal escrito e a legenda.
- Vaga livre: tracejado + hora. **Sem gravação** (decisão de 24/10: o calendário mostra só o que está agendado para
  publicar; a gravação prevista e a atrasada ficam só em Produção · Roteiros).
- O evento leva à publicação (Produção · Agendados/Publicados); dica com hora, nome, canais e estado.

## Semana
7 colunas com a capa grande, "19:14 · Publicado", nome, canais, a linha extra ("40 de alcance · Trial", "Normal · palavra
AULA", "métricas em 27 out") e "Portões:" escrito por extenso nos posts da fila. Hoje com fundo `surface-hover`.

## Lado
- **Fila**: Pronto para publicar 5 · Aguardando portão 0 · Sem horário 0, cada um com a frase; atalho "A caminho: 7
  roteiros ainda sem gravação" (→ Produção, Roteiros).
- **Melhores horários**: colunas por faixa de 3 h, as 3 mais altas em `chart-1` (15h, 18h, 21h); "Picos no app" e "Suas
  vagas" em chips; a nota diz a fonte, o dia e que mostra quem já segue. "Ver os números" com a tabela.

## Interações
Mês | Semana (`aria-pressed`) troca a vista e o título do período; ‹ › e "Hoje" navegam (o app troca mês ou semana);
Sem "Agendar publicação" (24/10: o painel só informa; agendar é `/publicar` no Claude Code).

## Estados
| Bloco | Vazio | Carregando | Erro |
|---|---|---|---|
| Calendário | "Nada programado neste mês" + "Ver produção" (as vagas livres continuam aparecendo) | esqueleto da grade | `k-note--alert` + "Tentar de novo" |
| Fila | "Fila vazia" | esqueleto de lista | idem |
| Melhores horários | "Sem print de horários" | esqueleto de gráfico | idem |

## 375 px
O mês vira **agenda**: só os dias com algo (e hoje, com "Nada programado."), com o rótulo "Sáb 24 out"; a semana empilha
os 7 dias; legenda e Mês | Semana quebram em linhas; Fila e Melhores horários em uma coluna. `scrollWidth` 375 conferido.

## Do artboard para a maquete
| No artboard | Na maquete | Motivo |
|---|---|---|
| Barra laranja em todos os eventos | laranja só Instagram; Instagram + Facebook em `ink` | regra do evento (livro §11.12); a legenda ganhou "Instagram e Facebook" |
| Sem a linha de portões | linha compacta em todo post da fila | regra do §11.12 ("em todos os posts da fila, nunca só em alguns") |
| "Sem horário · nenhum pacote pronto esperando data" | "o único pronto (ChatGPT contexto) é teste de cor e não sai" | existe um pronto; a frase anterior dizia que não |
| "Gráfico do app do Instagram (17 out)" | "… dia mostrado: quinta-feira" | o print é de um dia, não da semana |
| Alturas 73 · … · 100 | 72 · … · 99 (medidas de novo no print) | a 21h mede 99,5 %, como a 15h |
| Calendário 9 + lado 3 a 1440 | largura toda até 1919 px; 9 + 3 só a partir de 1920 | a 1440 as células teriam 124 px; a 1600, com o painel ao lado, 22 eventos cortavam ("Demis Hass…", "Public…", "Instagram · Fa…") — pedido do agente principal, 23/10 (livro §15.4) |
| Título e canais do evento numa linha, com reticências | até 2 linhas, sem reticências | a meta é nenhum evento cortado a 1440, 1600 e 1920; o `title` fica como apoio |
| Rótulos 10,5 px | 11 px | caption do sistema |

## Dúvidas para o Carlos
- Nenhuma aberta. (24/10: o calendário mostra só o que está agendado para publicar; gravação, prevista ou atrasada, só em
  Produção · Roteiros.)
