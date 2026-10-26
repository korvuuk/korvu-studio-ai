# Charts

Gráficos em SVG desenhados com os tokens `chart-1`…`chart-5` e a classe `k-chart`.

| Forma | Uso no painel |
|---|---|
| Linha / área | Evolução no tempo (visualizações, alcance, seguidores). Série em foco `chart-1` 2px + área a 14%; comparação `chart-2` tracejada 1.5px. |
| Barras horizontais | Ranking por categoria (tokens por departamento, vídeos por agente). Barra em destaque `chart-1`, restantes `chart-2`, trilho `surface-sunken`, valor à direita. |
| Donut | Partes de um todo com ≤4 fatias (custo por modelo). Espessura 14px, total no centro. |
| Sparkline | Tendência dentro de KPI cards, 120×28, sem eixos, ponto final marcado. |

- Grelha `chart-grid` 1px, eixos em 10px `ink-2`, sem bordas de eixo.
- Ordem das cores fixa: laranja → preto → taupe → areia → ardósia. Verde/vermelho nunca como série.
- Valor exato no `k-tooltip`.
