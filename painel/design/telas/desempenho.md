# Desempenho — `/desempenho`

> **O Carlos abre isto para** entender o que cresce, quem os vídeos estão alcançando e qual conteúdo funciona.

- Maquete: `desempenho.html`. Fonte do desenho: `painel/referencias/claude-design/telas-2026-10-23/Desempenho.dc.html`.
- Componentes: livro §11.5, §11.18 (gráficos), §15.2 (KPI em linha, barras finas, ranking, medidor, destaque, anel).
- Gráficos seguem a skill `dataviz`: um eixo só, legenda com 2 séries, texto nunca na cor da série, tabela gêmea em todo
  gráfico, hover **e** foco. Paleta validada com o `validate_palette.js` da skill: `chart-1` × `chart-2` separam bem (ΔE CVD
  39,5; contraste ≥ 3:1); o preto "falha" a faixa de luminosidade e croma de cor categórica porque é neutro de propósito
  (o sistema usa preto como "o resto" no destaque).

## Hierarquia
1. **sem título de página** (decisão de 24/10: o item do menu já diz onde se está; o `h1` "Desempenho" fica só para leitor de tela); à direita, numa barra fina, o período escrito: "Últimos 28 dias · 25 set – 22 out · leitura de 22 out, 14:00".
2. Quatro números: Seguidores · Visualizações · Contas alcançadas · Visitas ao perfil (cada um com o delta e o valor anterior).
3. "crescimento." (8 colunas) | "fora da bolha." (4 colunas).
4. "de onde vem o público." | "conteúdo que funciona." (largura toda a 1440; 5 + 7 a partir de 1600).

## Dados
| Bloco | Valores (22 out × 16 out) | Fonte |
|---|---|---|
| Seguidores | 3.631 · −0,1 % (−3) | `perfil_snapshots.seguidores` |
| Visualizações | 2.448 · ▼ 8,6 % (eram 2.677) — vermelho: cair é ruim | `perfil_snapshots.views` |
| Contas alcançadas | 529 · ▲ 11,1 % (eram 476) | `perfil_snapshots.alcance` |
| Visitas ao perfil | 56 · ▲ 3,7 % (eram 54) · 0 toques no link | `perfil_snapshots.visitas_perfil`; toques: `_controle/perfil/2026-10-22.json → profile_links_taps` (não está no banco) |
| crescimento. (totais na legenda) | Visualizações · 2.448; Alcance · 529 contas | `perfil_snapshots` |
| crescimento. (curva por dia) | **exemplo** — forma do artboard (`telas_exemplos`), pontos nas datas reais dos Reels | viria do `perfil.py` lendo todo dia (`period=day`) |
| fora da bolha. | 60 % não seguidores (307) · 40 % seguidores (206); +44 não seguidores em 6 dias, com 3 Trials no ar | `alcance_nao_seguidores`, `alcance_seguidores`; a frase dos 6 dias é a diferença 263 → 307 |
| de onde vem o público. | Quem segue: 3.202 com país, Guiné-Bissau 1.741 … França 29; Quem os vídeos alcançam: 379 com país, Brasil 197 … Luxemburgo 2 | `perfil_demografia` (`dimensao = 'country'`, `publico` = `seguidores` / `alcancados`) |
| conteúdo que funciona. | Demis Hassabis 450 · 338 · ~208 (62 %) · 20,5 % · 6,2 % (21 interações); Fei-Fei Li 45 · 40 · ~40 · 5,4 % · 2,5 %; Geoffrey Hinton 11 · 11 · 11 (100 %) · — · 9,1 %; Fei-Fei Li A 8 · 4 · ~4 · 1,5 % · 0 % | `metricas` (última leitura confiável; Hinton: tempo médio suspeito → "—"), `07-publicados/*/metricas.json`; não seguidores por Reel: `_controle/analise-trial-vs-normal-2026-10-22.md` (a API não separa por post: viria dos prints do app) |
| Destaque | "O único Reel normal, Demis Hassabis, chegou a ~208 não seguidores. Os três Trials somados chegaram a 55." | a mesma análise, item 4 |
| Seguidores ganhos | n/d em todos | a API da Meta não informa por Reel (a dica diz isso) |

## Regras dos gráficos
- **crescimento.**: 2 séries no **mesmo eixo** (0–300): visualizações em `chart-1` com área, alcance em `chart-2`; marcos
  nos 5 dias de Reel (o 1.º com rótulo "13 out · Demis Hassabis"); faixa de hover/foco por dia com a dica. **No app, até a
  fonte existir**: mostrar os dois totais e a frase "A curva por dia aparece quando o perfil for lido todo dia." — sem
  desenhar curva inventada.
- **fora da bolha.**: **anel-medidor** de uma proporção (60 % em `chart-1` sobre o trilho), não rosca de 2 fatias.
- **de onde vem o público.**: duas listas de barras finas; a 1.ª de cada uma em `chart-1`; valor em contas (inteiro).
  A frase do pé diz só o que os dados dizem ("o 1.º país de quem segue (Guiné-Bissau, 54,4 %) é o 4.º de quem foi
  alcançado (5,8 %)") — não define público por país (decisão de 21/10).
- **conteúdo que funciona.**: ranking por alcance (posição escrita; top 3 com fundo `surface-hover`); "% assistido" =
  tempo médio ÷ duração, medidor de **0 a 100 %**; engajamento = interações ÷ alcance. O post sem leitura ainda (Livro
  ChatGPT A) aparece no cabeçalho: "entra em 27 out".

## Interações
Dica (hover e foco) em cada dia do gráfico e no medidor; "Ver os números" em cada gráfico; o vídeo do ranking leva à
publicação (Produção · Publicados).

## Estados
| Bloco | Vazio | Carregando | Erro |
|---|---|---|---|
| Números | "Ainda não há leitura do perfil" | esqueleto de KPIs | `k-note--alert` + "Tentar de novo" |
| crescimento. | "Ainda não há dia a dia" | esqueleto de gráfico | idem |
| fora da bolha. | "Sem divisão seguidor × não seguidor" | esqueleto de gráfico | idem |
| de onde vem o público. | "Sem dados de país" (a Meta só mostra a partir de 100 contas) | esqueleto de lista | idem |
| conteúdo que funciona. | "Nenhum Reel com leitura ainda" (a 1.ª sai 5 dias depois do post) | esqueleto de tabela | idem |

## 375 px
KPIs em uma coluna (valor e contexto embaixo); gráficos na largura do card; as duas listas de país uma embaixo da outra; o
ranking rola dentro do card. `scrollWidth` 375 conferido.

## Do artboard para a maquete
| No artboard | Na maquete | Motivo |
|---|---|---|
| "2,4 mil" e "1,7 mil" | "2.448" e "1.741" | livro §1: até 9.999, inteiro |
| Seletor "Últimos 28 dias" | o período escrito, sem seletor | a Meta só dá a janela de 28 dias; seletor com uma opção é controle falso (livro §11.15) |
| Rosca de 2 fatias, seguidores em `chart-4` | anel-medidor sobre o trilho | dataviz: 2 fatias = um número; `chart-4` fica a 1,52:1 do card |
| "Retenção", barra escalada até 25 % | "% assistido", escala 0–100 % | é o que o número é; a escala de 25 % aumentava 4× as barras |
| "A base que segue está na Guiné-Bissau; o conteúdo novo já chega mais ao Brasil, ao Reino Unido e a Portugal." | a frase só com os números (1.º de um lado, 4.º do outro) | decisão de 21/10: nada de definir público por país no texto |
| Trial só na Fei-Fei A | "Trial" nas duas Fei-Fei | as duas saíram como Trial MANUAL (`post.json`) |
| Lista e ranking em 5 + 7 a 1440 | largura toda a 1440 | o ranking tem 8 colunas (livro §15.4) |
