"""Contraste WCAG 2.1 de cada par cor/fundo que o sistema "korvu. painel" usa — calculado, não de olho.

Lê as cores de painel/design/tokens.json (nada digitado aqui além dos pares) e imprime a tabela em Markdown que está em
painel/design/contraste.md. Fórmula: luminância relativa WCAG 2.1 (sRGB, limiar 0,03928) e (L1 + 0,05) / (L2 + 0,05).
Cor com transparência (opacity/rgba) é misturada ao fundo em sRGB, como o navegador faz.

Rodar:  uv run python -I painel/design/verificacao/contraste.py          (tabela)
        uv run python -I painel/design/verificacao/contraste.py --falhas (só o que fica abaixo do mínimo)
"""
import json
import pathlib
import sys

TOKENS = pathlib.Path(__file__).resolve().parents[1] / "tokens.json"
COR = {k: v["valor"] for k, v in json.loads(TOKENS.read_text(encoding="utf-8"))["cor"].items()}
COR["#ffffff"] = "#ffffff"  # só para conferir a frase da fonte "branco sobre o laranja falha"


def rgb(h):
    h = COR.get(h, h).lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def misturar(fg, bg, alfa):
    f, b = rgb(fg), rgb(bg)
    return "#" + "".join(f"{round(alfa * x + (1 - alfa) * y):02x}" for x, y in zip(f, b))


def lum(h):
    def c(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (c(v) for v in rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def razao(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# (id, frente, fundo, mínimo, tipo, onde) — frente pode ser ("mistura", cor, fundo, alfa)
# mínimo: 4.5 texto normal · 3.0 texto grande (≥ 24px, ou ≥ 18,66px em negrito) e objeto gráfico/controle (1.4.11)
#         0 = isento ou só informativo (decorativo, logotipo, controle desativado) — medido para registro
#         negativo = uso PROIBIDO pela própria fonte; a medida só confirma a proibição (não conta como falha do sistema)
PARES = [
    # ---------- texto sobre as superfícies claras ----------
    ("T01", "ink", "bg", 4.5, "texto", "corpo, títulos e números sobre o fundo"),
    ("T02", "ink", "surface", 4.5, "texto", "corpo e números dentro de cards e tabelas"),
    ("T03", "ink", "surface-sunken", 4.5, "texto", "botão secundário em hover, item de menu em hover, ícone de nota neutra"),
    ("T04", "ink", "surface-hover", 4.5, "texto", "linha de tabela em hover"),
    ("T05", "ink-2", "bg", 4.5, "texto", "texto secundário sobre o fundo; k-kbd"),
    ("T06", "ink-2", "surface", 4.5, "texto", "descrições, rótulos k-cap 11px, eixos 10px, cabeçalho de tabela"),
    ("T07", "ink-2", "surface-sunken", 4.5, "texto", "chip Agendado (12px/600), delta neutro"),
    ("T08", "ink-2", "surface-hover", 4.5, "texto", "células secundárias numa linha em hover"),
    ("T09", "ink-3", "bg", 4.5, "texto", "meta e horários sobre o fundo"),
    ("T10", "ink-3", "surface", 4.5, "texto", "meta em cards; placeholder da busca"),
    ("T11", "ink-3", "surface-hover", 4.5, "texto", "meta da VideoRow (\"Reel · …\") numa linha em hover"),
    ("T12", "ink-3", "surface-sunken", -4.5, "texto", "NÃO permitido pelo token ink-3 — medido para mostrar por quê"),
    # ---------- laranja ----------
    ("T13", "on-accent", "accent", 4.5, "texto", "rótulo do botão primário (13px/600); ícone do k-thumb laranja"),
    ("T14", "on-accent", "accent-hover", 4.5, "texto", "rótulo do botão primário em hover"),
    ("T15", "#ffffff", "accent", -4.5, "texto", "branco sobre o laranja — proibido pela fonte; conferido"),
    ("T16", "accent-ink", "bg", 4.5, "texto", "texto laranja sobre o fundo"),
    ("T17", "accent-ink", "surface", 4.5, "texto", "chip Portão (contorno), marca ✓ do menu"),
    ("T18", "accent-ink", "accent-soft", 4.5, "texto", "chip Em produção, evento de portão no calendário"),
    ("T19", "accent-ink", "surface-hover", 4.5, "texto", "chip Portão numa linha em hover"),
    ("T20", "accent", "bg", 3.0, "texto grande", "laranja como texto só a partir de 24px (regra da fonte)"),
    ("T21", "accent", "surface", 3.0, "texto grande", "idem, dentro de card"),
    ("T22", "accent", "bg", -4.5, "texto", "laranja como texto PEQUENO sobre o fundo — proibido pela fonte; conferido"),
    # ---------- verde e vermelho ----------
    ("T23", "positive", "bg", 4.5, "texto", "métrica positiva sobre o fundo"),
    ("T24", "positive", "surface", 4.5, "texto", "métrica positiva em card"),
    ("T25", "positive", "positive-soft", 4.5, "texto", "chip Aprovado, delta ▲ (12px/600)"),
    ("T26", "danger", "bg", 4.5, "texto", "alerta sobre o fundo"),
    ("T27", "danger", "surface", 4.5, "texto", "alerta em card"),
    ("T28", "danger", "danger-soft", 4.5, "texto", "chip Bloqueado, delta de custo ▲ (12px/600)"),
    # ---------- invertidos ----------
    ("T29", "bg", "ink", 4.5, "texto", "chip Publicado, chip Opus, botão escuro, ✓ do critério feito"),
    # ---------- barra lateral e dica ----------
    ("T30", "sidebar-ink", "sidebar", 4.5, "texto", "logotipo korvu., texto da dica (tooltip)"),
    ("T31", "sidebar-ink", "sidebar-raised", 4.5, "texto", "item ativo e em hover, avatar do rodapé"),
    ("T32", "sidebar-ink-2", "sidebar", 4.5, "texto", "itens inativos (13px/500), contagens 11px, 2.ª linha da dica"),
    ("T33", "sidebar-ink-2", "sidebar-raised", 4.5, "texto", "contagem dentro do item ativo/hover"),
    ("T34", ("mistura", "sidebar-ink-2", "sidebar", 0.8), "sidebar", 4.5, "texto",
     "k-sidebar-label (10px, opacity .8) — rótulo de grupo da barra lateral"),
    ("T35", "accent", "sidebar", 4.5, "texto", "laranja como texto sobre a barra lateral (permitido pela fonte)"),
    # ---------- objetos gráficos e controles (1.4.11, 3:1) ----------
    ("G01", "line-strong", "bg", 3.0, "controle", "borda de campo, dropdown e botão secundário sobre o fundo (#928874, decisão de 23/10)"),
    ("G02", "line-strong", "surface", 3.0, "controle", "idem dentro de card; caixa do critério (k-check) (decisão de 23/10)"),
    ("G03", "focus", "bg", 3.0, "foco", "anel de foco 2px (afastamento 2px) sobre o fundo — focus = accent-ink (decisão de 23/10)"),
    ("G04", "focus", "surface", 3.0, "foco", "anel de foco sobre card"),
    ("G05", "focus", "surface-sunken", 3.0, "foco", "anel de foco sobre área rebaixada (segmentado, atalho)"),
    ("G06", "focus-on-dark", "sidebar", 3.0, "foco", "anel de foco na barra lateral e na barra de topo (focus-on-dark = accent)"),
    ("G25", "line-strong", "surface-sunken", -3.0, "controle", "NÃO permitido: nenhum controle com borda line-strong sobre surface-sunken — medido para mostrar por quê"),
    ("G26", "focus", "surface-hover", 3.0, "foco", "anel de foco numa linha ou cartão em hover"),
    ("G27", "focus-on-dark", "sidebar-raised", 3.0, "foco", "anel de foco no item ativo da barra lateral"),
    ("G07", "ink", "surface", 3.0, "controle", "borda do campo em foco / dropdown aberto"),
    ("G08", "accent", "surface-sunken", 3.0, "gráfico", "preenchimento da barra de progresso; etapa atual (k-steps .now)"),
    ("G09", "ink", "surface-sunken", 3.0, "gráfico", "etapa concluída (k-steps .on)"),
    ("G10", "positive", "surface-sunken", 3.0, "gráfico", "barra concluída (k-progress.is-done)"),
    ("G11", "danger", "surface-sunken", 3.0, "gráfico", "etapa/barra bloqueada"),
    ("G12", "surface-sunken", "surface", 3.0, "gráfico", "trilho da barra e etapas FUTURAS contra o card"),
    ("G13", "chart-1", "surface", 3.0, "gráfico", "série 1 (laranja)"),
    ("G14", "chart-2", "surface", 3.0, "gráfico", "série 2 (preto)"),
    ("G15", "chart-3", "surface", 3.0, "gráfico", "série 3 (taupe)"),
    ("G16", "chart-4", "surface", 3.0, "gráfico", "série 4 / \"Outros\" (areia)"),
    ("G17", "chart-5", "surface", 3.0, "gráfico", "série 5 (ardósia); barra do evento Facebook"),
    ("G18", "ink-3", "surface-sunken", 3.0, "gráfico", "ícone play do k-thumb neutro"),
    ("G19", "accent-ink", "accent-soft", 3.0, "gráfico", "cadeado do portão (k-gate-icon), ícone de nota de portão"),
    ("G20", "accent-ink", "surface-sunken", 3.0, "gráfico", "✓ do item selecionado com o item em hover"),
    ("G21", "positive", "surface", 3.0, "gráfico", "ponto de presença (k-presence)"),
    ("G22", "accent", "surface", 3.0, "gráfico", "ponto de não lida (k-unread); contorno do chip Portão"),
    ("G23", "accent", "sidebar-raised", 3.0, "gráfico", "ícone e ponto do item ativo na barra lateral"),
    ("G24", "accent", "bg", 0, "não exigido", "contorno do botão primário contra o fundo — o rótulo identifica o botão (1.4.11 não exige)"),
    # ---------- informativos (sem mínimo) ----------
    ("I01", "line", "bg", 0, "decorativo", "borda fina de card (a fonte declara decorativa)"),
    ("I02", "line", "surface", 0, "decorativo", "divisórias de tabela"),
    ("I03", "chart-grid", "surface", 0, "decorativo", "grade dos gráficos"),
    ("I04", "sidebar-line", "sidebar", 0, "decorativo", "divisória do rodapé da barra lateral"),
    ("I05", "sidebar-raised", "sidebar", 0, "decorativo", "fundo do item ativo (o ponto laranja também marca)"),
    ("I06", "surface", "bg", 0, "decorativo", "card contra o fundo (a borda line separa)"),
    ("I07", "ink-2", "bg", 0, "logotipo", "\"painel\" no logotipo claro — logotipo é isento (1.4.3)"),
    ("I08", "sidebar-ink-2", "sidebar", 0, "logotipo", "\"painel\" no logotipo escuro — isento"),
    ("I09", ("mistura", "on-accent", ("mistura", "accent", "bg", 0.45), 0.45), ("mistura", "accent", "bg", 0.45), 0,
     "desativado", "botão primário desativado (opacity .45) — controle inativo é isento (1.4.3)"),
    ("I10", ("mistura", "sidebar-ink-2", "sidebar", 0.45), "sidebar", 0, "desativado",
     "item de menu sem página (proposta: opacity .45, a mesma do botão desativado) — inativo é isento (1.4.3)"),
]


def resolver(x):
    if isinstance(x, tuple):
        _, fg, bg, alfa = x
        return misturar(resolver(fg), resolver(bg), alfa)
    return COR.get(x, x)


def nome(x):
    if isinstance(x, tuple):
        _, fg, bg, alfa = x
        return f"{nome(fg)} a {round(alfa * 100)}% sobre {nome(bg)}"
    return f"`{x}`" if not x.startswith("#") else x


def main():
    so_falhas = "--falhas" in sys.argv
    print("| # | Frente | Fundo | Hex | Razão | Mínimo | Resultado | Onde |")
    print("|---|---|---|---|---|---|---|---|")
    falhas = 0
    for pid, fg, bg, minimo, tipo, onde in PARES:
        f, b = resolver(fg), resolver(bg)
        r = razao(f, b)
        if minimo == 0:
            res = f"— ({tipo})"
        elif minimo < 0:
            res = "falha esperada — uso proibido" if r < -minimo else "passa (uso proibido mesmo assim)"
        elif r + 1e-9 >= minimo:
            res = "passa"
        else:
            res = "**FALHA**"
            falhas += 1
        if so_falhas and res != "**FALHA**":
            continue
        rot_min = "—" if minimo == 0 else f"{abs(minimo):.1f}:1 ({tipo})"
        print(f"| {pid} | {nome(fg)} | {nome(bg)} | {f} / {b} | {r:.2f}:1 | {rot_min} | {res} | {onde} |")
    print(f"\n{falhas} par(es) abaixo do mínimo.")


if __name__ == "__main__":
    main()
