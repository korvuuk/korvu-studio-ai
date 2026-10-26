# KPICard

KPI card: `k-card k-kpi` com três linhas.

1. Rótulo em `caption` (`k-cap`), `ink-2`.
2. Valor em `metric-xl` (40px/700, tabular). Unidades (K, M, €) em `<small>` a 18px `ink-2`.
3. Rodapé: delta (`k-delta--up` verde, `--down` vermelho, `--flat` neutro) + contexto ou sparkline.

- A cor do delta segue o **significado**, não a direção: custo a subir é `k-delta--down` (vermelho).
- Linha de KPIs: 3 ou 4 cards em grelha de 12 colunas (span 4 ou 3).
- Números em formato PT: vírgula decimal, ponto de milhar (482,6K · 1.284.910).
