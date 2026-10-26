"""Gera painel/design/tokens.json e painel/design/tokens.css a partir da cópia exata do Claude Design.

Os VALORES saem do arquivo-fonte por código (nada digitado à mão); só os textos de uso são traduzidos para PT-BR.
Rodar:  uv run python -I painel/trabalho/designer/gerar_tokens.py
"""
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[3]
FONTE = RAIZ / "painel/referencias/claude-design/korvu-painel-2026-10-23/tokens.json"
DESTINO = RAIZ / "painel/design"

USO_COR = {
    "bg": "Fundo principal de todas as telas (marfim quente). Nunca branco puro.",
    "surface": "Fundo de cards, tabelas, popovers e campos — um passo mais claro que `bg`.",
    "surface-sunken": "Áreas rebaixadas: trilho de progresso, chips neutros, células vazias do calendário, hover de linha. Só `ink` e `ink-2` sobre ele.",
    "surface-hover": "Hover discreto de card e de linha de tabela.",
    "line": "Borda fina (1px) de cards, divisórias de tabela e separadores. Decorativa: nunca é a única pista de um controle.",
    "line-strong": "Borda de controles (campos, dropdown, botão secundário): 3,13:1 sobre `bg` e 3,33:1 sobre `surface`. Nenhum controle com esta borda sobre `surface-sunken` (2,94:1).",
    "ink": "Texto principal, títulos, números de métricas. Sobre `bg`, `surface`, `surface-sunken` e `accent`.",
    "ink-2": "Texto secundário (cinza quente): descrições, rótulos, eixos de gráfico. Sobre `bg`, `surface`, `surface-sunken`.",
    "ink-3": "Meta e legendas pequenas (horários, contagens). Só sobre `bg` e `surface`.",
    "sidebar": "Fundo da barra lateral fixa (quase preto) e das dicas (tooltips).",
    "sidebar-raised": "Item ativo e hover dentro da barra lateral.",
    "sidebar-line": "Divisórias dentro da barra lateral.",
    "sidebar-ink": "Texto ativo e o `korvu.` do logotipo sobre `sidebar`.",
    "sidebar-ink-2": "Itens inativos e a palavra `painel` sobre `sidebar` (6:1).",
    "accent": "Laranja Korvu: botão primário, item ativo, foco, série principal dos gráficos. Como texto, só sobre `sidebar` ou a partir de 24px — sobre `bg` use `accent-ink`.",
    "accent-hover": "Hover/pressionado do botão primário.",
    "accent-soft": "Fundo do chip `Em produção` e de destaques laranja suaves.",
    "accent-ink": "Texto laranja sobre `bg`, `surface` e `accent-soft` (≥4.5:1).",
    "on-accent": "Texto e ícones sobre `accent` (5.7:1). Branco sobre o laranja falha o contraste em 14px.",
    "positive": "Só métricas positivas (▲ +12%) e o chip `Aprovado`. Sobre `bg`, `surface`, `positive-soft`.",
    "positive-soft": "Fundo do chip `Aprovado` e do delta positivo.",
    "danger": "Só alertas: chip `Bloqueado`, custo acima do orçamento, erros. Sobre `bg`, `surface`, `danger-soft`.",
    "danger-soft": "Fundo do chip `Bloqueado` e das notificações de alerta.",
    "chart-1": "Série principal de qualquer gráfico (a que está em foco).",
    "chart-2": "Segunda série / comparação (período anterior, Facebook).",
    "chart-3": "Terceira série (taupe).",
    "chart-4": "Quarta série e restos (\"Outros\") em gráficos de rosca (donut).",
    "chart-5": "Quinta série, só quando funcionalmente necessária (ardósia).",
    "chart-grid": "Linhas de grade dos gráficos.",
    "focus": "Anel de foco 2px + afastamento 2px em todos os controles das superfícies claras (`bg`, `surface`, `surface-sunken`): 5,1–5,8:1.",
    "focus-on-dark": "Anel de foco na barra lateral e na barra de topo escuras (`sidebar`): 5,7:1.",
}

# Decisões do Carlos que mudam valores da fonte (docs/decisoes.md §5, 23/10: "Aceito as duas: borda dos campos em #928874
# e anel de foco em laranja escuro (accent-ink) nos fundos claros."). A fonte continua intocada; o fidelidade.py registra
# estas divergências como aprovadas.
DECISOES = {
    "line-strong": {"valor": "#928874", "era": "#a8a090", "decisao": "Carlos, 23/10 — borda dos campos em #928874 (3:1 sobre bg e surface)"},
    "focus": {"alias": "accent-ink", "era": "{accent}", "decisao": "Carlos, 23/10 — anel de foco em accent-ink nos fundos claros"},
}
NOVOS = {  # tokens que não existem na fonte, criados pela mesma decisão
    "focus-on-dark": {"alias": "accent", "depois_de": "focus", "decisao": "Carlos, 23/10 — nos fundos escuros (barra lateral) o anel continua accent; mesmo nome da versão 6 do artefato do Claude Design"},
}

TIPO = {
    "display": ("Títulos", "Operação de conteúdo", "Só em capas e estados de boas-vindas. No máximo uma por tela."),
    "h1": ("Títulos", "Visão geral", "Título da página (topo da área principal)."),
    "h2": ("Títulos", "Vídeos em produção", "Título de seção dentro da página."),
    "h3": ("Títulos", "Portão de aprovação", "Título de card grande, modal ou painel lateral."),
    "body": ("Texto", "O roteiro foi aprovado e segue para a gravação.", "Texto corrido, células de tabela, descrições."),
    "body-strong": ("Texto", "Marina Costa · Roteiro", "Nomes, títulos de linha e de card pequeno."),
    "small": ("Texto", "Atualizado há 4 min", "Rótulos de botão, chips, barra lateral, texto auxiliar."),
    "caption": ("Texto", "TOKENS · ESTA SEMANA", "Rótulos de seção e de KPI em MAIÚSCULAS, sempre em `ink-2` ou `ink-3`."),
    "metric-xl": ("Números", "128,4K", "Valor principal do KPI card. Algarismos tabulares (`font-variant-numeric: tabular-nums`)."),
    "metric-l": ("Números", "US$ 42,18", "Valores secundários e totais em tabelas e cards de equipe."),
    "mono": ("Números", "claude-sonnet · 1,2M tk", "Modelos, IDs, contagens de tokens e códigos HEX."),
}

USO_ESPACO = {
    "space-4": "Ícone ↔ texto em chips; ajustes finos.",
    "space-8": "Ícone ↔ rótulo em botões e itens da barra lateral; espaço entre chips.",
    "space-12": "Padding vertical de linhas de tabela e itens de lista.",
    "space-16": "Padding de cards pequenos; espaço entre campos.",
    "space-24": "Padding de cards e gutter da grade de 12 colunas.",
    "space-32": "Entre blocos de uma seção; padding lateral da área principal.",
    "space-48": "Entre seções da página.",
    "space-64": "Do topo da página até o H1; respiros editoriais.",
}
USO_RAIO = {
    "radius-sm": "Checkbox, dica (tooltip), células do calendário.",
    "radius-btn": "Botões, campos, busca, dropdown, itens da barra lateral.",
    "radius-card": "Cards, popovers, notificações.",
    "radius-panel": "Painéis grandes e modais.",
    "radius-pill": "Chips de estado, avatares redondos em pilhas, barras de progresso.",
}
USO_SOMBRA = {
    "shadow-card": "Cards em repouso — quase invisível; a borda `line` faz o trabalho.",
    "shadow-hover": "Hover de card clicável (com borda `line-strong`).",
    "shadow-pop": "Dropdowns, popovers, notificações flutuantes.",
}
USO_LAYOUT = {
    "viewport-desktop": "Largura de referência de todas as telas.",
    "sidebar-width": "Barra lateral fixa à esquerda.",
    "content-padding": "Padding lateral da área principal.",
    "grid-columns": "Colunas da área principal.",
    "grid-gutter": "Espaço entre colunas (20px abaixo de 1280px).",
    "row-height": "Altura de linha de tabela (linha de vídeo).",
    "control-height": "Altura de botões, busca e dropdown.",
}

# Acréscimos desta importação (não existem na fonte). Ficam num grupo à parte para nunca se confundirem com o
# sistema do Carlos; os de "layout-estreito" vão a ele como proposta.
ACRESCIMOS = {
    "nota": "Grupo fora do artefato do Claude Design. `movimento` foi LIDO do CSS dos componentes (bundle.css/README); "
            "`layout-estreito` é proposta da designer-de-produto (23/10) para 375 px, que o sistema não cobria — vai ao Carlos.",
    "movimento": {
        "origem": "lido de components/bundle.css e components/Tooltip/README.md (não é token da fonte)",
        "tokens": {
            "duracao-padrao": {"valor": "150ms", "css": "--duracao-padrao", "uso": "Transição de borda, sombra, fundo e cor (cards, botões, itens da barra lateral)."},
            "duracao-linha": {"valor": "120ms", "css": "--duracao-linha", "uso": "Fundo da linha de tabela no hover."},
            "atraso-dica": {"valor": "300ms", "css": "--atraso-dica", "uso": "Tempo de hover/foco até a dica (tooltip) aparecer."},
            "curva": {"valor": "ease", "css": "--curva", "uso": "A fonte não define curva: vale o padrão do CSS (`ease`)."},
        },
    },
    "layout-estreito": {
        "origem": "proposta da designer-de-produto, 23/10 — o sistema veio só para 1440px; vai ao Carlos",
        "tokens": {
            "bp-sm": {"valor": "640px", "css": "--bp-sm", "uso": "Abaixo disto: uma coluna (KPIs, cards de equipe, calendário)."},
            "bp-md": {"valor": "768px", "css": "--bp-md", "uso": "Abaixo disto: padding da área principal `space-16`, h1 no tamanho do h2, topo `space-24`."},
            "bp-lg": {"valor": "1024px", "css": "--bp-lg", "uso": "Abaixo disto: a barra lateral vira barra de topo + menu; KPIs em 2 colunas; gráfico e lateral empilham."},
            "bp-xl": {"valor": "1280px", "css": "--bp-xl", "uso": "Abaixo disto: gutter 20px (regra da fonte)."},
            "topbar-height": {"valor": "56px", "css": "--topbar-height", "uso": "Altura da barra de topo abaixo de 1024px (o mesmo valor de `row-height`)."},
            "content-padding-estreito": {"valor": "16px", "css": "--content-padding-estreito", "uso": "Padding lateral da área principal abaixo de 768px (`space-16`)."},
        },
    },
}


def main() -> int:
    fonte = json.loads(FONTE.read_text(encoding="utf-8"))
    cores_fonte = {t["name"]: t["value"] for t in fonte["color"]["tokens"]}
    faltam = (set(cores_fonte) | set(NOVOS)) ^ set(USO_COR)
    if faltam:
        print("cores sem tradução / a mais:", faltam, file=sys.stderr)
        return 1

    def resolver(v: str) -> tuple[str, str | None]:
        if v.startswith("{") and v.endswith("}"):
            alvo = v[1:-1]
            return cores_fonte[alvo], alvo
        return v, None

    cor = {}
    for nome, bruto in cores_fonte.items():
        if nome in DECISOES:
            d = DECISOES[nome]
            bruto = d.get("valor") or "{" + d["alias"] + "}"
        valor, alias = resolver(bruto)
        item = {"valor": valor, "css": f"--{nome}", "uso": USO_COR[nome]}
        if alias:
            item["alias"] = alias
        if nome in DECISOES:
            item["fonte_era"] = DECISOES[nome]["era"]
            item["decisao"] = DECISOES[nome]["decisao"]
        cor[nome] = item
        for novo, d in NOVOS.items():
            if d["depois_de"] == nome:
                v, a = resolver("{" + d["alias"] + "}")
                cor[novo] = {"valor": v, "css": f"--{novo}", "uso": USO_COR[novo], "alias": a, "acrescimo": True, "decisao": d["decisao"]}

    estilos = {}
    for grupo in fonte["type"]["groups"]:
        for s in grupo["styles"]:
            g, amostra, uso = TIPO[s["name"]]
            assert g == grupo["name"], (g, grupo["name"])
            estilos[s["name"]] = {
                "grupo": g,
                "familia": s.get("family", grupo["family"]),
                "fontSize": s["fontSize"],
                "lineHeight": s["lineHeight"],
                "fontWeight": s["fontWeight"],
                "letterSpacing": s.get("letterSpacing", "normal"),
                **({"textTransform": "uppercase"} if s["name"] == "caption" else {}),
                "amostra": amostra,
                "uso": uso,
            }
    assert set(estilos) == set(TIPO)

    def grupo_simples(chave: str, usos: dict) -> dict:
        toks = {t["name"]: t["value"] for t in fonte[chave]["tokens"]}
        assert set(toks) == set(usos), (chave, set(toks) ^ set(usos))
        return {n: {"valor": v, "css": f"--{n}", "uso": usos[n]} for n, v in toks.items()}

    tokens = {
        "nome": fonte["name"],
        "versao": fonte["version"],
        "origem": {
            "artefato": "Claude Design — design system \"korvu. painel\", feito pelo Carlos (23/10/2026)",
            "copia_exata": "painel/referencias/claude-design/korvu-painel-2026-10-23/tokens.json",
            "regra": "Valores idênticos à fonte, com DUAS decisões do Carlos de 23/10 (campos `fonte_era` e `decisao`): "
                     "`line-strong` #928874 e `focus` = alias de `accent-ink` (nos fundos claros); `focus-on-dark` (alias de "
                     "`accent`) é acréscimo da mesma decisão. `chart-1` é alias de `accent`: vem resolvido (campo `valor`) e com o "
                     "alias anotado (campo `alias`). Textos de uso traduzidos para PT-BR.",
            "conferir": "uv run python -I painel/design/verificacao/fidelidade.py",
        },
        "tema": {"id": fonte["color"]["themes"][0]["id"], "nome": fonte["color"]["themes"][0]["name"],
                 "nota": "Único tema do sistema. Não existe modo escuro."},
        "cor": cor,
        "fonte": {
            "familias": {
                "sans": {"valor": fonte["type"]["families"]["sans"], "css": "--font-sans"},
                "mono": {"valor": fonte["type"]["families"]["mono"], "css": "--font-mono"},
            },
            "arquivos": [
                {"familia": f["family"], "arquivo": f["file"].replace("fonts/", "fontes/"), "peso": f["weight"],
                 "estilo": f["style"], "licenca": "SIL Open Font License 1.1 — fontes/OFL.txt"}
                for f in fonte["type"]["fonts"]
            ],
        },
        "tipografia": estilos,
        "espaco": grupo_simples("spacing", USO_ESPACO),
        "raio": grupo_simples("radius", USO_RAIO),
        "sombra": grupo_simples("shadow", USO_SOMBRA),
        "layout": {"nota": "Desktop 1440px · barra lateral fixa de 208px · área principal fluida com grade de 12 colunas.",
                   **grupo_simples("layout", USO_LAYOUT)},
        "acrescimos": ACRESCIMOS,
    }
    (DESTINO / "tokens.json").write_text(json.dumps(tokens, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # ---------- tokens.css ----------
    L = []
    L.append("/* korvu. painel — variáveis de design (tokens).")
    L.append("   Gerado de painel/design/tokens.json, que copia os valores do Claude Design (Carlos, 23/10/2026), com duas")
    L.append("   decisões dele de 23/10: --line-strong #928874 e --focus = accent-ink nos fundos claros (--focus-on-dark = accent).")
    L.append("   Os nomes das variáveis são exatamente os que componentes.css usa (var(--bg), var(--ink-2), var(--space-24)…).")
    L.append("   Não edite à mão: mude tokens.json (com decisão do Carlos) e gere de novo. */")
    L.append("")
    for f in tokens["fonte"]["arquivos"]:
        L.append("@font-face {")
        L.append(f'  font-family: "{f["familia"]}";')
        L.append(f'  src: url("{f["arquivo"]}") format("woff2");')
        L.append(f"  font-weight: {f['peso']};")
        L.append(f"  font-style: {f['estilo']};")
        L.append("  font-display: swap;")
        L.append("}")
        L.append("")
    L.append(":root {")
    L.append("  /* Cor — não alterar sem decisão do Carlos. Tema único: claro, \"Marfim\". */")
    for n, t in cor.items():
        if t.get("alias"):
            L.append(f"  --{n}: var(--{t['alias']}); /* alias de {t['alias']} = {t['valor']} */")
        else:
            L.append(f"  --{n}: {t['valor']};")
    L.append("")
    L.append("  /* Famílias */")
    for n, t in tokens["fonte"]["familias"].items():
        L.append(f"  {t['css']}: {t['valor']};")
    L.append("")
    L.append("  /* Espaçamento (base 4) */")
    for n, t in tokens["espaco"].items():
        L.append(f"  --{n}: {t['valor']};")
    L.append("")
    L.append("  /* Raios */")
    for n, t in tokens["raio"].items():
        L.append(f"  --{n}: {t['valor']};")
    L.append("")
    L.append("  /* Sombras */")
    for n, t in tokens["sombra"].items():
        L.append(f"  --{n}: {t['valor']};")
    L.append("")
    L.append("  /* Layout */")
    for n, t in tokens["layout"].items():
        if n == "nota":
            continue
        L.append(f"  --{n}: {t['valor']};")
    L.append("")
    L.append("  /* Escala tipográfica (tokens.json → tipografia). Usada pelas classes .k-display…k-metric-l de acrescimos.css. */")
    for n, s in estilos.items():
        L.append(f"  --type-{n}-size: {s['fontSize']};")
        L.append(f"  --type-{n}-line: {s['lineHeight']};")
        L.append(f"  --type-{n}-weight: {s['fontWeight']};")
        L.append(f"  --type-{n}-tracking: {s['letterSpacing']};")
    L.append("")
    L.append("  /* Acréscimos (fora da fonte): movimento lido do CSS dos componentes; layout estreito = proposta 23/10. */")
    for g in ("movimento", "layout-estreito"):
        for n, t in ACRESCIMOS[g]["tokens"].items():
            L.append(f"  {t['css']}: {t['valor']};")
    L.append("}")
    L.append("")
    L.append("/* Regra da fonte: gutter 20px abaixo de 1280px. */")
    L.append("@media (max-width: 1279px) {")
    L.append("  :root { --grid-gutter: 20px; }")
    L.append("}")
    (DESTINO / "tokens.css").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("ok:", DESTINO / "tokens.json", DESTINO / "tokens.css")
    return 0


if __name__ == "__main__":
    sys.exit(main())
