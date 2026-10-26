"""Gera as maquetes das 7 telas em painel/design/telas/*.html a partir de painel/design/dados-2026-10-23.json.

Todo número, nome, data e estado sai do JSON (blocos telas_* e os aprovados). O que não tem fonte vem do bloco
telas_exemplos e leva o selo "exemplo". Classes: só k-* (componentes.css + acrescimos.css) e, na faixa de documentação
depois da tela, .pv-* (previas/previa.css) e .tl-* (telas/telas.css).
Rodar:  uv run python -I painel/trabalho/designer/gerar_telas.py
"""
import datetime as dt
import html
import json
import pathlib
import re
from zoneinfo import ZoneInfo

RAIZ = pathlib.Path(__file__).resolve().parents[3]
D = RAIZ / "painel/design"
T = D / "telas"
DADOS = json.loads((D / "dados-2026-10-23.json").read_text(encoding="utf-8"))
B = {k: v["linhas"] for k, v in DADOS["blocos"].items()}
ICT = json.loads((D / "icones/telas/icones-telas.json").read_text(encoding="utf-8"))["icones"]
LON = ZoneInfo("Europe/London")
HOJE = dt.date(2026, 10, 23)
MES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
MES_LONGO = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
SEM = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
SEM_LONGO = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]


# ------------------------------------------------------------------ formatos (design-system.md §1)
def esc(s):
    return html.escape(str(s), quote=True)


def n(x):
    return f"{int(round(x)):,}".replace(",", ".")


def dec(x, c=1):
    return f"{x:,.{c}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def compacto(x):
    """KPI: até 9.999 inteiro; de 10.000 em diante, compacto com uma casa (482,6K, 12,8M)."""
    if x < 10000:
        return n(x)
    if x < 1e6:
        return dec(x / 1e3) + "K"
    return dec(x / 1e6) + "M"


def usd(x, c=2):
    return "US$ " + dec(x, c)


def gbp(us, c=2):
    """24/10: custo de IA em US$, a moeda da tabela da Anthropic, sem câmbio (substitui a decisão de 23/10 em £)."""
    return usd(us, c)


def pct(x, c=1):
    return dec(x, c) + "%"


def lon(s):
    return dt.datetime.fromisoformat(s).astimezone(LON)


def dm(d):
    return f"{d.day} {MES[d.month - 1]}"


def sem_dm(d):
    return f"{SEM[d.weekday()]} {d.day} {MES[d.month - 1]}"


def relativo(d):
    k = (d - HOJE).days
    return {0: "hoje", 1: "amanhã", -1: "ontem"}.get(k, f"em {k} dias" if k > 0 else f"há {-k} dias")


def dur(s):
    s = int(round(s))
    return f"{s // 60}:{s % 60:02d}"


def ic(nome, tam=16):
    return f'<span data-icon="{nome}" data-size="{tam}" aria-hidden="true"></span>'


def ict(nome, tam=16, extra=""):
    return (f'<svg viewBox="0 0 24 24" width="{tam}" height="{tam}" fill="none" stroke="currentColor" stroke-width="1.5" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"{extra}>{ICT[nome]}</svg>')


EX = '<span class="tl-ex">exemplo</span>'
TAG_EX = '<span class="pv-tag">exemplo · sem fonte hoje</span>'
TAG_REAL = '<span class="pv-tag pv-tag--real">dados reais</span>'
TAG_PROP = '<span class="pv-tag pv-tag--proposta">proposta · vai ao Carlos</span>'

# ------------------------------------------------------------------ dados
MODELO = {m["alias"]: m["rotulo"] for m in B["telas_modelos"]}
MODELO_ID = {m["modelo"]: m["rotulo"] for m in B["telas_modelos"]}
MODELO_ID["claude-fable-5-1"] = "Fable 5.1"
DEPTOS = B["telas_departamentos"]
NOME_DEPTO = {d["id"]: d["nome"][:1].upper() + d["nome"][1:] for d in DEPTOS}
AG = {a["id"]: a for a in B["telas_agentes"]}
RETRATO = {"diretor": "atlas", "portao-pauta": "vera", "revisor-de-roteiro": "otavio", "portao-imagem": "iris",
           "estrategista": "helena", "pesquisador-de-material": "rafael", "buscador-de-videos": "tiago",
           "curador-de-obra": "beatriz", "roteirista": "marina", "produtor-de-material": "livia"}
assert {r["agente"] for r in B["telas_retratos"]} == set(RETRATO), "retratos mudaram: atualize RETRATO"
# nome curto de exibição: o canvas usa o slug sem a data (não existe campo de título curto — handoff §8)
NOME = {
    "2026-09-16-chatgpt-contexto": "ChatGPT contexto", "2026-09-17-demis-hassabis": "Demis Hassabis",
    "2026-09-17-jacob-coxon": "Jacob Coxon", "2026-10-18-jensen-huang": "Jensen Huang",
    "2026-10-20-fei-fei-li": "Fei-Fei Li", "2026-10-20-fei-fei-li-a": "Fei-Fei Li A", "2026-10-20-fei-fei-li-r2": "Fei-Fei Li r2",
    "2026-10-20-geoffrey-hinton": "Geoffrey Hinton", "2026-10-20-geoffrey-hinton-r2": "Geoffrey Hinton r2",
    "2026-10-21-foto-da-loja": "Foto da loja", "2026-10-21-golpes-com-ia": "Golpes com IA",
    "2026-10-22-15-coisas-ia-negocio": "15 coisas IA negócio", "2026-10-22-agente-3-passos": "Agente 3 passos",
    "2026-10-23-livro-chatgpt": "Livro ChatGPT", "2026-10-23-livro-chatgpt-a": "Livro ChatGPT A",
    "2026-10-23-livro-chatgpt-l01c": "Livro ChatGPT L01C", "2026-10-23-livro-chatgpt-l01c-a": "Livro ChatGPT L01C A",
    "2026-10-24-comando-secreto": "Comando secreto"}
CAPA = {  # cópias 270×480 de capa/capa.png (painel/referencias/.../capas → telas/img/capas)
    "2026-09-17-demis-hassabis": "capa-demis.jpg", "2026-10-20-fei-fei-li-r2": "capa-feifei.jpg",
    "2026-10-20-geoffrey-hinton-r2": "capa-hinton.jpg", "2026-10-23-livro-chatgpt": "capa-livro.jpg",
    "2026-10-23-livro-chatgpt-l01c": "capa-livro-l01c.jpg", "2026-10-23-livro-chatgpt-l01c-a": "capa-livro-l01c-a.jpg",
    "2026-09-16-chatgpt-contexto": "capa-chatgpt-contexto.jpg", "2026-10-20-fei-fei-li": "pub-feifei.jpg",
    "2026-10-20-fei-fei-li-a": "pub-feifei-a.jpg", "2026-10-20-geoffrey-hinton": "pub-hinton.jpg",
    "2026-10-23-livro-chatgpt-a": "pub-livro-a.jpg"}
VIDEOS = {v["slug"]: v for v in B["telas_videos"]}
FILA = B["telas_fila"]
PUBS = sorted(B["telas_publicados"], key=lambda p: p["publicado_em"], reverse=True)
PRONTOS = B["telas_prontos"]
PERFIL = B["telas_perfil_arquivo"]
P16, P22 = PERFIL[0], PERFIL[1]
TOK = B["telas_tokens"][0]
HOR = DADOS["blocos"]["telas_melhores_horarios"]
ANALISE = DADOS["blocos"]["telas_analise_trial"]
EXEMPLO_CURVA = B["telas_exemplos"][2]["pontos_exemplo"]
SYNC = lon(B["telas_sincronizacao"][0]["em"])
SYNC_TXT = f"{dm(SYNC)}, {SYNC:%H:%M}"
LEITURA_TOK = lon(TOK["ate"])

# fases (design-system.md §15.1): a fonte de cada uma é a pasta onde o trabalho está
EM_PACOTE = {p["slug"] for p in PRONTOS} | {f["slug"] for f in FILA} | {p["slug"] for p in PUBS}
ROTEIROS = sorted([v for v in VIDEOS.values() if not v["gravado"]], key=lambda v: v["gravacao_prevista"])
ORIGEM = {}
for s in list(EM_PACOTE):
    ORIGEM[s] = next((v for v in VIDEOS if s.startswith(v)), None)
GRAVADOS = [v for v in VIDEOS.values() if v["gravado"] and not any(o == v["slug"] for o in ORIGEM.values())]
PORT_VID = {}
for r in B["telas_portoes_videos"]:
    PORT_VID.setdefault(r["slug"], {})[r["portao"]] = r["status"]
LEGADO = {f["slug"]: f["legado"] for f in B["telas_fila_legado"]}

# mapa único (design-system.md §11.3, família 1)
MAPA = {"aprovado": ("k-chip--aprovado", "Aprovado"), "bloqueado": ("k-chip--bloqueado", "Bloqueado"),
        "escalado": ("k-chip--bloqueado", "Escalado"), "vencido": ("k-chip--bloqueado", "Vencido"),
        "pendente": ("k-chip--agendado", "Ainda não rodou"), "nao_se_aplica": ("k-chip--agendado no-dot", "Não se aplica"),
        "legado": ("k-chip--agendado no-dot", "Legado · sem selo")}
PIOR = ["escalado", "bloqueado", "vencido", "pendente", "nao_se_aplica"]
NOME_PORTAO = {"pauta": "pauta", "roteiro": "roteiro", "imagem": "imagem", "corte": "corte", "publicacao": "publicação"}


def chip_portao(status, tag="span"):
    c, p = MAPA[status]
    return f'<{tag} class="k-chip {c} is-sm">{p}</{tag}>'


def pior_de(estados):
    """estados: {portao: status}. Devolve (status, [portões nesse estado]) — o pior, na ordem da §11.12."""
    for s in PIOR:
        quem = [NOME_PORTAO[p] for p in ("pauta", "roteiro", "imagem", "corte", "publicacao") if estados.get(p) == s]
        if quem:
            return s, quem
    return "aprovado", []


def quem_txt(lista):
    return lista[0] if len(lista) == 1 else f"{lista[0]} e mais {len(lista) - 1}"


# ------------------------------------------------------------------ casca
NAV = [("visao-geral", "Visão geral", "visao-geral.html", None), ("equipe", "Equipe", "equipe.html", (len(AG), "pessoas")),
       ("videos-portoes", "Produção de conteúdo", "producao.html", None), ("calendario", "Calendário", "calendario.html", None),
       ("desempenho", "Desempenho", "desempenho.html", None), ("biblioteca", "Biblioteca", "biblioteca.html", None),
       ("tokens-custos", "Tokens e custos", "tokens-e-custos.html", None)]

N_ROT = len(ROTEIROS)
mais_antigo = ROTEIROS[0]
proximo = next(v for v in ROTEIROS if dt.date.fromisoformat(v["gravacao_prevista"]) >= HOJE)
pronto = PRONTOS[0]
AVISOS = [
    ("gate", ict("camera"), f"{N_ROT} roteiros esperando gravação",
     f"O mais antigo, {NOME[mais_antigo['slug']]}, espera desde {dm(dt.date.fromisoformat(mais_antigo['gravacao_prevista']))}. "
     f"{NOME[proximo['slug']]} está previsto para {relativo(dt.date.fromisoformat(proximo['gravacao_prevista']))}.",
     ("Ver roteiros", "producao.html")),
    ("alert", ic("alert"), "Pronto, mas não vai ao ar",
     f"{NOME[pronto['slug']]} passou no QA em {dm(lon(pronto['criado_em']))}, mas foi um teste de cor: não sai.",
     ("Ver prontos", "producao.html")),
    ("gate", ic("lock"), "Portão do roteiro ainda não rodou",
     f"Os {N_ROT} roteiros são anteriores aos portões (22 out). O {AG['revisor-de-roteiro']['nome']} revisa cada um antes da gravação.",
     ("Ver roteiros", "producao.html")),
]


def avisos_lista():
    out = []
    for tipo, icone, t, corpo, (rot, href) in AVISOS:
        out.append(f'<div class="k-note k-note--{tipo}"><span class="k-note-icon">{icone}</span><div>'
                   f'<div class="k-note-title">{esc(t)}</div><div class="k-note-body">{esc(corpo)}</div>'
                   f'<div class="k-note-actions"><a class="k-btn k-btn-secondary k-btn-sm" href="{href}">{rot}</a></div></div></div>')
    return "\n".join(out)


def botao_avisos():
    return (f'<button type="button" class="k-btn k-btn-ghost k-btn-icon k-avisos tem-aviso" aria-label="Avisos: {len(AVISOS)}">'
            f'{ic("bell", 18)}</button>')


def pedido(rotulo, titulo, texto, comando, primario=True, icone="plus"):
    cls = "k-btn k-btn-primary" if primario else "k-btn k-btn-secondary k-btn-sm"
    return (f'<div class="k-pedido"><button type="button" class="{cls}" data-pedido aria-expanded="false" aria-haspopup="dialog">'
            f'{ic(icone, 16) if icone else ""}{esc(rotulo)}</button>'
            f'<div class="k-menu" role="dialog" aria-label="{esc(titulo)}"><span class="k-pedido-t">{esc(titulo)}</span>'
            f'<p class="k-pedido-p">{texto}</p><code class="k-code">{esc(comando)}</code>'
            f'<button type="button" class="k-btn k-btn-secondary k-btn-sm" data-copiar="{esc(comando)}">Copiar o pedido</button></div></div>')


def casca(ativo, conteudo, doc=""):
    itens = []
    for icone, rot, href, cont in NAV:
        on = icone == ativo
        c = (f'<span class="k-nav-count">{cont[0]}<span class="k-sr-only"> {cont[1]}</span></span>' if cont else "")
        itens.append(f'<a class="k-nav-item{" is-active" if on else ""}" href="{href}"'
                     f'{" aria-current=" + chr(34) + "page" + chr(34) if on else ""}>{ic(icone, 18)}<span>{rot}</span>{c}</a>')
    busca = ('<label class="k-search">' + ic("search", 16) +
             '<input type="search" placeholder="Buscar vídeos, agentes, portões…" aria-label="Buscar no painel"><span class="k-kbd">⌘K</span></label>')
    return f"""<a class="k-skip" href="#conteudo">Pular para o conteúdo</a>
<div class="k-shell">
<header class="k-topbar">
<a href="visao-geral.html" aria-label="korvu. painel — início"><span data-logo="ivory" data-h="19"></span></a>
<div class="k-topbar-fim">{botao_avisos()}<button type="button" class="k-menu-btn" aria-expanded="false" aria-controls="menu">Menu</button></div>
</header>
<nav class="k-sidebar" id="menu" aria-label="Menu principal">
<a class="k-sidebar-logo" href="visao-geral.html" aria-label="korvu. painel — início"><span data-logo="ivory" data-h="19"></span></a>
{busca.replace('aria-label="Buscar no painel"', 'aria-label="Buscar no painel (menu)"')}
{chr(10).join(itens)}
<div class="k-sidebar-foot"><div class="k-sidebar-owner">@korvu_oficial<small>Instagram · Facebook</small></div></div>
</nav>
<div class="k-area">
<header class="k-appbar">
{busca}
<div class="k-appbar-fim">{botao_avisos()}<span class="k-appbar-sep" aria-hidden="true"></span>
<div class="k-dono"><span class="k-avatar" aria-hidden="true">CM</span><span><span class="k-dono-nome">Carlos</span><span class="k-dono-papel">Proprietário</span></span></div></div>
</header>
<main class="k-main is-painel" id="conteudo">
{conteudo}
<p class="k-fonte" style="margin-top:var(--space-48);padding-top:var(--space-16);border-top:1px solid var(--line)">@korvu_oficial · sincronizado em {SYNC_TXT} · o painel só lê os arquivos do projeto</p>
{doc}
</main>
</div>
</div>"""


def pagina(arq, ativo, titulo, conteudo, doc):
    doc_html = f"""<section class="tl-doc" aria-label="Documentação da maquete (fora da tela do app)">
<div class="pv">
<header class="pv-head"><p class="k-cap">Maquete · {esc(titulo)} · fora da tela</p><h2 class="k-h2">Estados de cada bloco e variações</h2>
<p class="pv-lead">Daqui para baixo não é a tela: é o que o engenheiro-frontend implementa quando o bloco não tem dado, está carregando ou falhou, e as vistas que só aparecem ao tocar. Regras: <a href="{arq.replace('.html', '.md')}">{arq.replace('.html', '.md')}</a> e <a href="../design-system.md">design-system.md</a>.</p></header>
{doc}
</div>
</section>"""
    h = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(titulo)} · korvu. painel — maquete</title>
<link rel="stylesheet" href="../tokens.css">
<link rel="stylesheet" href="../componentes.css">
<link rel="stylesheet" href="../acrescimos.css">
<link rel="stylesheet" href="../previas/previa.css">
<link rel="stylesheet" href="telas.css">
<script src="../korvu.js"></script>
<script src="../previas/previa.js" defer></script>
<script src="telas.js" defer></script>
</head>
<body>
{casca(ativo, conteudo, doc_html)}
</body>
</html>
"""
    # moeda e número nunca se separam na quebra de linha (PI46): espaço inseparável entre £/US$ e o valor
    h = re.sub(r"(£|US\$) (?=[0-9])", "\\1\u00a0", h)
    (T / arq).write_text(h, encoding="utf-8")


# ------------------------------------------------------------------ estados (vazio · carregando · erro)
SKEL = {
    "kpi": '<div class="k-card k-kpi" aria-hidden="true"><span class="k-skel k-skel-cap"></span><span class="k-skel k-skel-metric"></span><span class="k-skel k-skel-line" style="width:70%"></span></div>',
    "lista": '<div class="k-card k-pad k-stack" aria-hidden="true"><span class="k-skel k-skel-title"></span><span class="k-skel k-skel-line"></span><span class="k-skel k-skel-line"></span><span class="k-skel k-skel-line" style="width:80%"></span><span class="k-skel k-skel-line" style="width:60%"></span></div>',
    "grafico": '<div class="k-card k-pad k-stack" aria-hidden="true"><span class="k-skel k-skel-title"></span><span class="k-skel" style="height:140px"></span></div>',
    "tabela": '<div class="k-card k-pad k-stack" aria-hidden="true"><span class="k-skel k-skel-title"></span><div class="k-row"><span class="k-skel k-skel-thumb"></span><span class="k-skel k-skel-line" style="flex:1"></span></div><div class="k-row"><span class="k-skel k-skel-thumb"></span><span class="k-skel k-skel-line" style="flex:1"></span></div><div class="k-row"><span class="k-skel k-skel-thumb"></span><span class="k-skel k-skel-line" style="flex:1"></span></div></div>',
    "cartoes": '<div class="k-card k-pad k-stack" aria-hidden="true"><div class="k-row"><span class="k-skel k-skel-avatar"></span><span class="k-skel k-skel-line" style="flex:1"></span></div><span class="k-skel k-skel-line" style="width:70%"></span><span class="k-skel k-skel-chip"></span></div>',
}


def estados(blocos):
    out = []
    for nome, vt, vx, icone, skel, acao in blocos:
        botao = f'<button type="button" class="k-btn k-btn-secondary k-btn-sm">{esc(acao)}</button>' if acao else ""
        out.append(f"""<div class="tl-bloco"><h3>{esc(nome)}</h3><div class="tl-estados">
<div class="tl-estado"><span class="k-cap">Vazio</span><div class="k-empty"><div class="k-empty-icon">{ic(icone, 22)}</div><h4>{esc(vt)}</h4><p>{esc(vx)}</p>{botao}</div></div>
<div class="tl-estado"><span class="k-cap">Carregando</span><div role="status">{SKEL[skel]}<span class="k-sr-only">Carregando os dados do painel…</span></div></div>
<div class="tl-estado"><span class="k-cap">Erro</span><div class="k-card"><div class="k-note k-note--alert" role="alert"><span class="k-note-icon">{ic("alert", 16)}</span><div><div class="k-note-title">Não deu para carregar esta parte</div><div class="k-note-body">{esc(nome)} não abriu. O resto da página continua valendo.</div><div class="k-note-actions"><button type="button" class="k-btn k-btn-secondary k-btn-sm">Tentar de novo</button></div></div></div></div></div>
</div></div>""")
    return '<section class="pv-sec"><h2 class="pv-sec-t k-cap">Estados de cada bloco</h2>' + "\n".join(out) + "</section>"


def variacao(titulo, corpo, tags=""):
    return f'<section class="pv-sec"><h2 class="pv-sec-t k-cap">{esc(titulo)} {tags}</h2>{corpo}</section>'


# ------------------------------------------------------------------ peças
def delta(valor, tipo, sr, seta=None):
    """tipo = a cor pelo SIGNIFICADO (up verde, down vermelho, flat neutro); seta = a direção do número (livro §11.5:
    custo subindo é vermelho com a seta para cima)."""
    seta = {"up": ic("arrow-up", 12), "down": ic("arrow-down", 12), "flat": ""}[seta or tipo]
    return f'<span class="k-delta k-delta--{tipo}">{seta}{valor}<span class="k-sr-only"> {sr}</span></span>'


def head(h1, lead=None, ferramentas=""):
    """24/10: sem título de página — o item do menu já diz onde se está. O h1 fica só para leitor de tela (com o nome do
    menu); busca, filtro de período e data, quando a tela tem, ficam numa barra fina no topo."""
    barra = f'<div class="k-page-barra">{ferramentas}</div>' if ferramentas.strip() else ""
    return f'<h1 class="k-sr-only">{esc(h1)}</h1>{barra}'



def capa(slug, tam="", alt=True):
    f = CAPA.get(slug)
    if not f:
        return f'<span class="k-capa {tam}" aria-hidden="true">{ic("play", 14)}</span>'
    a = f'Capa de {NOME.get(slug, slug)}' if alt else ""
    return f'<span class="k-capa {tam}"><img src="img/capas/{f}" alt="{esc(a)}"></span>'


def canais(plataformas, links=None, publicado=False):
    out = []
    for c, nome in (("instagram", "Instagram"), ("facebook", "Facebook"), ("linkedin", "LinkedIn")):
        on = c in (plataformas or [])
        link = (links or {}).get(c)
        if on and link:
            out.append(f'<a class="k-canal" href="{esc(link)}" target="_blank" rel="noopener">{nome}{ict("link-externo", 11)}'
                       f'<span class="k-sr-only"> — abrir o post (abre em outra aba)</span></a>')
        elif on:
            out.append(f'<span class="k-canal">{nome}<span class="k-sr-only"> — vai sair</span></span>')
        else:
            out.append(f'<span class="k-canal is-off">{nome}<span class="k-sr-only"> — {"não saiu" if publicado else "não vai sair"}</span></span>')
    return f'<div class="k-canais">{"".join(out)}</div>'


def modo_chip(trial):
    return ('<span class="k-chip k-chip--modo is-sm">Trial Reel</span>' if trial
            else '<span class="k-chip k-chip--agendado no-dot is-sm">Normal</span>')


def modelo_chip(rot):
    cls = "k-chip--opus" if rot.startswith("Opus") or rot.startswith("Fable") else "k-chip--model"
    return f'<span class="k-chip {cls} is-sm">{rot}</span>'


def avatar(agid, tam=""):
    a = AG[agid]
    r = RETRATO.get(agid)
    if r:
        return f'<span class="k-avatar"{tam}><img src="img/retratos/{r}.jpg" alt="Retrato de {esc(a["nome"])}"></span>'
    p = a["nome"].split()
    ini = (p[0][0] + (p[1][0] if len(p) > 1 else p[0][1])).upper()
    return f'<span class="k-avatar"{tam} aria-hidden="true">{ini}</span>'


def iniciais(nome):
    p = nome.split()
    return (p[0][0] + (p[1][0] if len(p) > 1 else p[0][1])).upper()


def rosca(fatias, centro, rotulo, tam=132, esp=14, aria=""):
    r = (tam - esp) / 2
    circ = 2 * 3.141592653589793 * r
    acc = 0
    partes = [f'<circle cx="{tam/2}" cy="{tam/2}" r="{r:.2f}" fill="none" stroke-width="{esp}" style="stroke:var(--surface-sunken)"></circle>']
    total = sum(v for v, _ in fatias)
    for v, cor in fatias:
        q = v / total
        partes.append(f'<circle cx="{tam/2}" cy="{tam/2}" r="{r:.2f}" fill="none" stroke-width="{esp}" '
                      f'stroke-dasharray="{max(q*circ-2, 0.5):.2f} {circ:.2f}" stroke-dashoffset="{-acc*circ:.2f}" style="stroke:var(--{cor})"></circle>')
        acc += q
    return (f'<div style="position:relative;width:{tam}px;height:{tam}px;flex:none"><svg class="k-anel" viewBox="0 0 {tam} {tam}" width="{tam}" height="{tam}" role="img" aria-label="{esc(aria)}">'
            + "".join(partes) + f'</svg><div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center">'
            f'<span class="k-num k-tokens is-grande" style="font-size:24px;line-height:28px;font-weight:700;letter-spacing:-.02em">{centro}</span>'
            f'<span class="k-cap" style="font-size:11px">{rotulo}</span></div></div>')


def detalhes(cab, linhas, nome):
    th = "".join(f'<th{" class=k-dir" if i else ""}>{esc(c)}</th>' for i, c in enumerate(cab))
    tr = "".join("<tr>" + "".join(f'<td{" class=k-dir" if i else ""}>{c}</td>' for i, c in enumerate(l)) + "</tr>" for l in linhas)
    return (f'<details class="k-details"><summary class="k-btn k-btn-ghost k-btn-sm">Ver os números</summary>'
            f'<div class="k-table-wrap" role="region" aria-label="{esc(nome)}" tabindex="0" style="--table-min:320px"><table class="k-table">'
            f'<thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div></details>')


# ==================================================================================================== VISÃO GERAL
def kpis_visao():
    seg_d = P22["seguidores"] - P16["seguidores"]
    alc_d = (P22["alcance"] / P16["alcance"] - 1) * 100
    fb22 = P22["alcance_nao_seguidores"] / (P22["alcance_nao_seguidores"] + P22["alcance_seguidores"]) * 100
    fb16 = P16["alcance_nao_seguidores"] / (P16["alcance_nao_seguidores"] + P16["alcance_seguidores"]) * 100
    melhor = max((p for p in PUBS if p["metricas"]), key=lambda p: p["metricas"]["alcance"])
    circ = 2 * 3.141592653589793 * 27
    return f"""<section class="k-section" aria-label="Números do perfil"><div class="k-grid k-grid--tiles">
<div class="k-card k-kpi k-span-3"><span class="k-cap">Seguidores no Instagram</span><div class="k-kpi-value">{n(P22['seguidores'])}</div>
<div class="k-kpi-foot" style="justify-content:flex-start;gap:10px">{delta(pct(seg_d / P16['seguidores'] * 100).replace('-', '−'), 'flat', 'quase igual a 16 out')}<span class="k-kpi-note">{str(seg_d).replace('-', '−')} vs. leitura de 16 out</span></div></div>
<div class="k-card k-kpi k-span-3"><span class="k-cap">Alcance · 28 dias</span><div class="k-kpi-value">{n(P22['alcance'])}<small>contas</small></div>
<div class="k-kpi-foot" style="justify-content:flex-start;gap:10px">{delta(pct(alc_d), 'up', 'a mais que em 16 out')}<span class="k-kpi-note">{n(P22['views'])} visualizações</span></div></div>
<div class="k-card k-kpi has-aside k-span-3"><span class="k-cap">Alcance fora da bolha</span><div class="k-kpi-value">{round(fb22)}<small>%</small></div>
<div class="k-kpi-foot" style="justify-content:flex-start;gap:10px">{delta(dec(fb22 - fb16) + ' p.p.', 'up', 'a mais que em 16 out')}<span class="k-kpi-note">{P22['alcance_nao_seguidores']} de {P22['alcance_nao_seguidores'] + P22['alcance_seguidores']} não seguem</span></div>
<svg class="k-kpi-aside k-anel" viewBox="0 0 64 64" width="64" height="64" role="img" aria-label="{round(fb22)}% do alcance vem de quem não segue a conta"><circle class="trilho" cx="32" cy="32" r="27" fill="none" stroke-width="8"></circle><circle class="valor" cx="32" cy="32" r="27" fill="none" stroke-width="8" stroke-dasharray="{fb22/100*circ:.2f} {circ:.2f}"></circle></svg></div>
<a class="k-card k-kpi has-aside k-kpi--capa is-interactive k-span-3" href="desempenho.html" style="text-decoration:none;color:inherit"><span class="k-cap">Melhor vídeo até agora</span><div class="k-kpi-value">{n(melhor['metricas']['alcance'])}<small>alcance</small></div>
<div class="k-kpi-foot" style="justify-content:flex-start;gap:8px;min-width:0;flex-wrap:wrap"><b style="font-size:13px;line-height:18px">{NOME[melhor['slug']]}</b><span class="k-kpi-note">{dm(lon(melhor['publicado_em']))} · {n(melhor['metricas']['views'])} visualizações</span></div>
<span class="k-kpi-aside">{capa(melhor['slug'], 'k-capa--lg')}</span></a>
</div></section>"""


def posts_visao():
    cards = []
    for f in sorted(FILA, key=lambda f: f["publicar_em"]):
        d = lon(f["publicar_em"])
        rel = relativo(d.date())
        onde = " · ".join(c.capitalize() if c != "linkedin" else "LinkedIn" for c in f["plataformas"])
        cards.append(f"""<a class="k-card is-interactive k-post" href="calendario.html">{capa(f['slug'], 'k-capa--md')}<div class="k-post-corpo">
<div class="k-post-quando"><span><span class="k-cap">{sem_dm(d)}</span><span class="k-mono k-ink2">{d:%H:%M}</span></span><span class="k-post-rel{' is-perto' if rel in ('hoje', 'amanhã') else ''}">{rel}</span></div>
<span class="k-post-titulo">{NOME[f['slug']]}</span><span class="k-post-onde">{onde}{modo_chip(f['trial'])}</span></div></a>""")
    return f"""<section class="k-section"><div class="k-section-head"><div class="k-row"><h2 class="k-h3">Próximas publicações</h2><span class="k-section-sub">{len(FILA)} agendadas · horário de Londres</span></div>
<a class="k-btn k-btn-ghost k-btn-sm" href="calendario.html">Ver calendário{ic('chevron-right', 14)}</a></div>
<div class="k-posts">{''.join(cards)}</div></section>"""


def curva_cfg(series, yMax, yTicks, yRot=None, marcos=None, inicio=dt.date(2026, 9, 25), dias=28, ticks=(0, 7, 14, 21, 27)):
    rot = [dm(inicio + dt.timedelta(days=i)) for i in range(dias)]
    return esc(json.dumps({"rotulos": rot, "series": series, "yMax": yMax, "yTicks": yTicks, "yRotulos": yRot,
                           "xTicks": list(ticks), "rotulosEixo": [rot[i] for i in ticks], "marcos": marcos or []},
                          ensure_ascii=False))


MARCOS_REELS = []
for p in sorted(PUBS, key=lambda p: p["publicado_em"]):
    i = (lon(p["publicado_em"]).date() - dt.date(2026, 9, 25)).days
    if 0 <= i < 28:
        MARCOS_REELS.append({"i": i, "rotulo": ""})


def bloco_desempenho_28():
    m = [dict(x) for x in MARCOS_REELS]
    m[0]["rotulo"] = "13 out · Demis Hassabis"
    cfg = curva_cfg([{"nome": "Visualizações (exemplo)", "cor": "chart-1", "area": True, "v": EXEMPLO_CURVA["views"]}], 300, [0, 100, 200, 300], marcos=m)
    return f"""<section class="k-card k-pad k-span-12 k-xl-6" aria-labelledby="t-d28">
<div class="k-card-head"><h2 class="k-card-title" id="t-d28">Desempenho · 28 dias</h2><span class="k-mono k-muted">25 set – 22 out</span></div>
<div class="k-stats is-solto" style="margin-top:16px">
<div class="k-stat"><span class="k-stat-v is-grande">{n(P22['views'])}</span><span class="k-stat-r">visualizações</span></div>
<div class="k-stat"><span class="k-stat-v is-grande">{n(P22['alcance'])}</span><span class="k-stat-r">contas alcançadas</span></div>
<div class="k-stat"><span class="k-stat-v is-grande">{n(P22['visitas_perfil'])}</span><span class="k-stat-r">visitas ao perfil</span></div></div>
<p class="k-fonte" style="margin-top:14px">Visualizações por dia {EX} — a Meta só manda o total de 28 dias; os pontos marcam as datas reais dos Reels.</p>
<div><svg class="k-chart" data-curva="{cfg}" data-altura="170" role="img" aria-label="Exemplo da forma: visualizações por dia nos últimos 28 dias, em alta desde 13 out, quando saiu o Reel de Demis Hassabis"></svg></div>
{detalhes(['O que existe', 'Valor'], [['Visualizações · 28 dias', n(P22['views'])], ['Contas alcançadas · 28 dias', n(P22['alcance'])], ['Visitas ao perfil · 28 dias', n(P22['visitas_perfil'])], ['Por dia', 'ainda não chega (exemplo no gráfico)']], 'Números do desempenho em 28 dias')}
</section>"""


NOME_PAIS = {"GW": "Guiné-Bissau", "BR": "Brasil", "PT": "Portugal", "AO": "Angola", "GB": "Reino Unido", "MZ": "Moçambique",
             "SN": "Senegal", "CV": "Cabo Verde", "US": "Estados Unidos", "FR": "França", "DE": "Alemanha", "CH": "Suíça",
             "LU": "Luxemburgo"}


def paises(publico):
    rows = [r for r in B["telas_paises"] if r["publico"] == publico]
    return rows, sum(r["valor"] for r in rows)


def barras_paises(publico, valor="pct"):
    rows, tot = paises(publico)
    top = rows[:10]
    mx = top[0]["valor"]
    out = []
    for i, r in enumerate(top):
        v = pct(r["valor"] / tot * 100) if valor == "pct" else n(r["valor"])
        out.append(f'<div class="k-bar-row k-bar-row--fino"><span>{NOME_PAIS[r["chave"]]}</span><span class="k-bar-track"><span class="k-bar-fill{" is-focus" if i == 0 else ""}" style="width:{r["valor"]/mx*100:.1f}%"></span></span><span class="k-bar-value">{v}</span></div>')
    return '<div class="k-barras">' + "".join(out) + "</div>", tot


def bloco_publico():
    s, ts = barras_paises("seguidores")
    a, ta = barras_paises("alcancados")
    rs, _ = paises("seguidores")
    ra, _ = paises("alcancados")
    linhas = [[NOME_PAIS[x["chave"]], n(x["valor"]), "quem segue"] for x in rs[:10]] + [[NOME_PAIS[x["chave"]], n(x["valor"]), "alcançados"] for x in ra[:10]]
    return f"""<section class="k-card k-pad k-span-6 k-xl-3" aria-labelledby="t-pub" style="padding:20px">
<div class="k-card-head"><h2 class="k-card-title" id="t-pub">Público · Top 10 países</h2><span class="k-mono k-muted" data-de="pais" data-valor="segue">{n(ts)} contas</span><span class="k-mono k-muted" data-de="pais" data-valor="alcance" hidden>{n(ta)} contas</span></div>
<div class="k-seg is-largo" role="group" aria-label="Qual público" style="margin-top:12px"><button type="button" data-grupo="pais" data-valor="segue" aria-pressed="true">Quem segue</button><button type="button" data-grupo="pais" data-valor="alcance" aria-pressed="false">Quem os vídeos alcançam</button></div>
<div style="margin-top:14px" data-de="pais" data-valor="segue">{s}</div><div style="margin-top:14px" data-de="pais" data-valor="alcance" hidden>{a}</div>
{detalhes(['País', 'Contas', 'Público'], linhas, 'Países em números')}
</section>"""


MOD_ORDEM = ["claude-opus-5-5", "claude-sonnet-5-5", "claude-fable-5-1"]
MOD_COR = {"claude-opus-5-5": "chart-1", "claude-sonnet-5-5": "chart-2", "claude-fable-5-1": "chart-3"}


def tokens_por_modelo():
    pm = {m["modelo"]: m for m in TOK["por_modelo"]}
    return [(pm[k], MOD_COR[k]) for k in MOD_ORDEM if k in pm]


def bloco_tokens_visao():
    fat = tokens_por_modelo()
    T_ = TOK["total_tokens"]
    leg = "".join(f'<div style="display:flex;align-items:center;gap:8px"><i style="width:8px;height:8px;border-radius:2px;background:var(--{c});flex:none"></i><span class="k-mono" style="flex:1">{MODELO_ID[m["modelo"]]}</span><span class="k-mono k-tokens">{round(m["tokens"]/T_*100)}%</span></div>' for m, c in fat)
    aria = "Tokens por modelo: " + ", ".join(f'{MODELO_ID[m["modelo"]]} {round(m["tokens"]/T_*100)}%' for m, c in fat)
    return f"""<section class="k-card k-span-6 k-xl-3" aria-labelledby="t-tok" style="padding:20px;display:flex;flex-direction:column">
<div class="k-card-head"><h2 class="k-card-title" id="t-tok">Tokens e custos · 30 dias</h2><a class="k-btn k-btn-ghost k-btn-sm" href="tokens-e-custos.html" aria-label="Ver tokens e custos">{ic('chevron-right', 14)}</a></div>
<div style="display:flex;align-items:center;flex-wrap:wrap;gap:16px 20px;margin-top:16px">{rosca([(m['tokens'], c) for m, c in fat], compacto(T_), 'tokens', 112, 14, aria)}
<div style="display:flex;flex-direction:column;gap:7px;flex:1;min-width:110px">{leg}</div></div>
<div style="margin-top:auto;padding-top:14px;border-top:1px solid var(--line);display:flex;align-items:flex-end;justify-content:space-between;gap:12px;flex-wrap:wrap">
<div style="display:flex;flex-direction:column;gap:2px"><span class="k-cap">Custo estimado</span><span class="k-kpi-note">equivalente na API · 30 dias · preço de tabela</span></div>
<span class="k-num k-metric-l"><small style="font-size:15px;font-weight:600;color:var(--ink-2);margin-right:4px">US$</small>{n(round(TOK['total_us']))}</span></div>
{detalhes(['Modelo', 'Tokens', 'Custo (US$)'], [[MODELO_ID[m['modelo']], n(m['tokens']), dec(m['us'], 2)] for m, c in fat], 'Tokens por modelo')}
</section>"""


STATUS_EX = {"diretor": True, "designer-de-produto": True}  # telas_exemplos: presença sem fonte
DESTAQUE = ["diretor", "portao-pauta", "revisor-de-roteiro", "portao-imagem", "revisor-de-video"]
ORDEM_CANVAS = {  # ordem das pessoas em cada departamento, como no canvas (gerente primeiro)
    "pesquisa": ["portao-pauta", "curador-de-obra", "estrategista", "pesquisador-de-material", "buscador-de-videos"],
    "roteiro": ["revisor-de-roteiro", "produtor-de-material", "roteirista"],
    "arte": ["portao-imagem", "designer-de-capas", "produtor-de-extras", "animador", "colorista"],
    "pos": ["revisor-de-video", "editor-de-video", "produtor-musical"],
    "distribuicao": ["portao-publicacao", "auditor-de-perfil", "analista-de-metricas", "publicador"],
    "tecnologia": ["portao-interface", "engenheiro-frontend", "designer-de-produto", "engenheiro-backend", "portao-dados"]}
assert sum(len(v) for v in ORDEM_CANVAS.values()) == len(AG) - 1


def cargo_curto(a):
    c = a["cargo"].split(" · ")[0]
    return c[:1].upper() + c[1:]


def portao_de(a):
    if a["papel"] != "portao":
        return ""
    p = a["cargo"].split(" · ")[-1]
    return p[:1].upper() + p[1:]


def cartao_agente(agid):
    a = AG[agid]
    r = RETRATO.get(agid)
    foto = (f'<span class="k-agente-foto"><img src="img/retratos/{r}.jpg" alt="Retrato de {esc(a["nome"])}"></span>' if r
            else f'<span class="k-agente-foto" aria-hidden="true">{iniciais(a["nome"])}</span>')
    on = STATUS_EX.get(agid, False)
    chips = (f'<span class="k-chip k-chip--portao is-sm">{ic("lock", 12)}Portão</span>' if a["papel"] == "portao" else "") + modelo_rodou(agid)
    return f"""<a class="k-card is-interactive k-agente" href="equipe.html">{foto}<div class="k-agente-txt">
<span class="k-agora{' is-on' if on else ''}">{'Trabalhando agora' if on else 'Em espera'}</span>
<h3 class="k-agente-nome">{esc(a['nome'])}</h3><p class="k-agente-funcao">{cargo_curto(a)}</p><p class="k-agente-depto">{NOME_DEPTO[a['departamento_id']]}</p>
<div class="k-agente-chips">{chips}</div></div></a>"""


def bloco_equipe_visao():
    filtros = [("todos", "Todos")] + [(d["id"], NOME_DEPTO[d["id"]]) for d in DEPTOS if d["id"] != "direcao"]
    fb = "".join(f'<button type="button" class="k-filtro" data-grupo="depto" data-valor="{k}" aria-pressed="{"true" if k == "todos" else "false"}">{esc(v)}</button>' for k, v in filtros)
    paineis = [f'<div class="k-agentes" data-de="depto" data-valor="todos">{"".join(cartao_agente(x) for x in DESTAQUE)}</div>']
    for k, _ in filtros[1:]:
        paineis.append(f'<div class="k-agentes" data-de="depto" data-valor="{k}" hidden>{"".join(cartao_agente(x) for x in ORDEM_CANVAS[k][:5])}</div>')
    n_dep = len(DEPTOS) - 1
    return f"""<section class="k-section" id="equipe"><div class="k-section-head">
<div class="k-row"><h2 class="k-h3">Equipe</h2><span class="k-section-sub">{len(AG)} pessoas em {n_dep} departamentos e a direção · status {EX}</span></div>
<div class="k-row" style="gap:8px"><a class="k-btn k-btn-ghost" href="equipe.html">Ver equipe completa{ic('chevron-right', 16)}</a></div></div>
<div class="k-filtros" role="group" aria-label="Filtrar por departamento" style="margin-bottom:12px">{fb}</div>
{''.join(paineis)}</section>"""


def tela_visao():
    hoje_txt = f"{SEM_LONGO[HOJE.weekday()]}, {dm(HOJE)} {HOJE.year}"
    ferr = f'<span class="k-page-meta">{ic("calendario", 16)}{hoje_txt}</span>'
    c = head("Visão geral", None, ferr)
    c += kpis_visao()
    c += posts_visao()
    c += f'<section class="k-section"><div class="k-grid">{bloco_desempenho_28()}{bloco_publico()}{bloco_tokens_visao()}</div></section>'
    c += bloco_equipe_visao()
    doc = estados([
        ("Números do perfil (KPIs)", "Ainda não há leitura do perfil", "Quando o perfil.py ler a conta pela 1.ª vez, os seguidores e o alcance aparecem aqui.", "eye", "kpi", None),
        ("Próximas publicações", "Nada agendado", "Quando um pacote entrar na fila de publicação (06-publicar/), ele aparece aqui com dia, hora e canal.", "calendario", "tabela", "Ver produção"),
        ("Desempenho · 28 dias", "Sem números de 28 dias", "Quando a Meta devolver a 1.ª janela de 28 dias, visualizações, alcance e visitas aparecem aqui.", "desempenho", "grafico", None),
        ("Público · Top 10 países", "Sem dados de país", "A Meta só mostra países a partir de 100 seguidores ou contas alcançadas; quando houver, aparecem aqui.", "users", "lista", None),
        ("Tokens e custos · 30 dias", "Nenhuma sessão nos últimos 30 dias", "Quando o Claude Code rodar neste projeto, os tokens e o custo equivalente aparecem aqui.", "tokens-custos", "grafico", None),
        ("Equipe", "Ninguém neste departamento", "Quando houver um agente neste departamento em .claude/agents/, ele aparece aqui.", "equipe", "cartoes", None),
    ])
    doc += variacao("Avisos (o sino)", f'<div class="k-menu" style="max-width:380px;padding:0"><div style="padding:12px 16px 4px" class="k-card-title">Avisos · {len(AVISOS)}</div>{avisos_lista()}</div>'
                    '<p class="pv-nota">Os mesmos três de "Precisam de atenção" (Produção de conteúdo), calculados dos dados. O ponto laranja do sino aparece quando há aviso; "não lido" não existe porque o painel não guarda o que você viu.</p>', TAG_PROP)
    pagina("visao-geral.html", "visao-geral", "Visão geral", c, doc)


# ==================================================================================================== EQUIPE
AG_TOK = {}
for r in TOK["por_agente"]:
    alvo = "diretor" if r["agente"] in ("principal", "general-purpose", "workflow-subagent", "claude", "Explore", "Plan") else r["agente"]
    x = AG_TOK.setdefault(alvo, {"tokens": 0, "us": 0.0, "tarefas": 0, "modelos": {}})
    x["tokens"] += r["tokens"]; x["us"] += r["us"]; x["tarefas"] += r["tarefas"]
    for m, v in r["modelos"].items():
        x["modelos"][m] = x["modelos"].get(m, 0) + v


# a direção inteira é o Atlas: usa a soma do departamento (uma conta só, sem somar valores já arredondados)
AG_TOK["diretor"]["us"] = next(d["us"] for d in TOK["por_departamento"] if d["departamento"] == "direcao")
AG_TOK["diretor"]["tokens"] = next(d["tokens"] for d in TOK["por_departamento"] if d["departamento"] == "direcao")


def rodou(agid):
    """24/10: o modelo que RODOU (registros do Claude Code, 30 dias), não o configurado. [(rótulo, %), …] do maior para o
    menor; lista vazia = ainda não rodou."""
    t = AG_TOK.get(agid)
    if not t or not t["modelos"]:
        return []
    tot = sum(t["modelos"].values())
    return [(MODELO_ID[m], round(100 * v / tot)) for m, v in sorted(t["modelos"].items(), key=lambda x: -x[1])]


def modelo_rodou(agid):
    """Chip do modelo principal; com mais de um, "90 % · +1" embaixo e a lista no title; sem registro, "ainda não rodou"."""
    r = rodou(agid)
    if not r:
        return '<span class="k-modelo-nada">ainda não rodou</span>'
    if len(r) == 1:
        return modelo_chip(r[0][0])
    lista = " · ".join(f"{m} {q} %" for m, q in r)
    outros = " · ".join(f"{m} {q} %" for m, q in r[1:])
    return (f'<span class="k-modelo-mix" title="Rodou em {lista}">{modelo_chip(r[0][0])}'
            f'<small>{r[0][1]} % · +{len(r) - 1}<span class="k-sr-only"> (também {outros})</span></small></span>')


def linha_pessoa(agid):
    a = AG[agid]
    t = AG_TOK.get(agid)
    ger = any(d["gerente_id"] == agid for d in DEPTOS)
    port = a["papel"] == "portao"
    on = STATUS_EX.get(agid, False)
    r = rodou(agid)
    tags = ["todos", r[0][0].split()[0].lower() if r else "naorodou"] + (["portoes"] if port else []) + (["ativos"] if on else [])
    nome = f'<span class="k-pessoa-nome"><b title="{esc(a["nome"])}">{esc(a["nome"])}</b></span>'
    consumo = (f'<span class="k-pessoa-num k-dir"><span class="k-tokens">{compacto(t["tokens"])}</span><small>{gbp(t["us"])}</small></span>' if t
               else '<span class="k-pessoa-num k-dir"><span class="k-muted">—</span></span>')
    tar = f'<span class="k-pessoa-num k-dir">{t["tarefas"] if t else "—"}</span>'
    return f"""<li data-filtra="equipe" data-tags="{' '.join(tags)}"><a class="k-pessoa-linha{' is-gerente' if ger else ''}" href="#{agid}">{avatar(agid)}
<span class="k-pessoa-id">{nome}<span class="k-pessoa-funcao">{cargo_curto(a)}</span>{'<span class="k-pessoa-portao">' + ic('lock', 12) + ' ' + portao_de(a) + '</span>' if port else ''}</span>
<span class="k-agora{' is-on' if on else ''}" style="font-size:11px">{'Ativo' if on else 'Em espera'}</span>
<span>{modelo_rodou(agid)}</span>{consumo}{tar}<span class="k-pessoa-seta">{ic('chevron-right', 14)}</span></a></li>"""


def tela_equipe():
    ferr = ('<label class="k-search" style="width:300px">' + ic("search", 16) + '<input type="search" placeholder="Buscar agente…" aria-label="Buscar agente" data-busca="equipe"></label>'
           )
    c = head("Equipe", None, ferr)
    principal = {k: (rodou(k)[0][0] if rodou(k) else None) for k in AG}
    n_op = sum(1 for v in principal.values() if v == "Opus 5.5")
    n_so = sum(1 for v in principal.values() if v == "Sonnet 5.5")
    n_nr = sum(1 for v in principal.values() if v is None)
    n_port = sum(1 for a in AG.values() if a["papel"] == "portao")
    n_at = sum(1 for v in STATUS_EX.values() if v)
    filtros = [("todos", "Todos", len(AG), ""), ("ativos", "Ativos", n_at, EX), ("portoes", "Portões", n_port, ""), ("opus", "Opus 5.5", n_op, ""), ("sonnet", "Sonnet 5.5", n_so, ""), ("naorodou", "Ainda não rodou", n_nr, "")]
    fb = "".join(f'<button type="button" class="k-filtro" data-grupo="equipe" data-valor="{k}" aria-pressed="{"true" if k == "todos" else "false"}">{r}<span class="k-filtro-n">{q}</span></button>' for k, r, q, _ in filtros)
    c += f"""<section class="k-section" aria-label="Filtros e números da equipe"><div class="k-section-head" style="margin-top:-8px"><div class="k-filtros" role="group" aria-label="Filtrar agentes">{fb}</div>
<div class="k-cal-legenda"><span class="k-agora is-on">Ativo agora</span><span class="k-agora">Em espera</span><span>status {EX}</span><span>· modelo, consumo e tarefas: 30 dias, registros do Claude Code (o modelo é o que rodou) · custo em US$, preço de tabela da API</span></div></div>"""
    trab = sum(1 for k in AG if AG_TOK.get(k))
    c += f"""<div class="k-grid k-grid--tiles">
<div class="k-card k-kpi k-kpi--linha k-span-3"><span class="k-cap">Agentes</span><div class="k-kpi-linha"><span class="k-kpi-value">{len(AG)}</span><span class="k-kpi-note">rodaram em Opus 5.5: {n_op} · Sonnet 5.5: {n_so} · ainda não: {n_nr}</span></div></div>
<div class="k-card k-kpi k-kpi--linha k-span-3"><span class="k-cap">Departamentos</span><div class="k-kpi-linha"><span class="k-kpi-value">{len(DEPTOS) - 1}</span><span class="k-kpi-note">mais a direção</span></div></div>
<div class="k-card k-kpi k-kpi--linha k-span-3"><span class="k-cap">Portões</span><div class="k-kpi-linha"><span class="k-kpi-value">{n_port}</span><span class="k-kpi-note">um gerente por departamento + dados</span></div></div>
<a class="k-card k-kpi k-kpi--linha is-interactive k-span-3" href="tokens-e-custos.html" style="text-decoration:none;color:inherit"><span class="k-cap">Tokens · 30 dias</span><div class="k-kpi-linha"><span class="k-kpi-value k-tokens is-grande">{dec(TOK['total_tokens'] / 1e6)}<small>M</small></span><span class="k-kpi-note">{usd(TOK['total_us'], 0)} equivalente na API</span></div></a>
</div></section>"""
    at = AG["diretor"]
    t = AG_TOK["diretor"]
    mods = " ".join(f'<span class="k-row" style="gap:4px">{modelo_chip(m)}<small class="k-mono k-ink2">{q} %</small></span>' for m, q in rodou("diretor"))
    c += f"""<section class="k-section" aria-label="Direção"><a class="k-card is-interactive k-direcao" href="#diretor" data-filtra="equipe" data-tags="todos opus ativos">
<div class="k-direcao-quem">{avatar('diretor')}<div style="display:flex;flex-direction:column;gap:2px;min-width:0"><span class="k-cap">Direção</span>
<div class="k-row" style="gap:8px"><h2 class="k-h3">{at['nome']}</h2><span class="k-chip k-chip--agendado no-dot is-sm">Claude principal</span></div>
<span class="k-small k-ink2">{cargo_curto(at)}</span></div></div>
<p class="k-direcao-texto">{esc(at['resumo'].replace('O Claude principal. ', ''))}</p>
<div class="k-stats">
<div class="k-stat"><span class="k-cap">Status {EX}</span><span class="k-agora is-on" style="font-size:14px;font-weight:600;color:var(--ink)">Ativo agora</span></div>
<div class="k-stat"><span class="k-cap">Tarefas · 30 dias</span><span class="k-stat-v">{t['tarefas']}</span></div>
<div class="k-stat"><span class="k-cap">Tokens · 30 dias</span><span class="k-stat-v k-tokens">{compacto(t['tokens'])}</span></div>
<div class="k-stat"><span class="k-cap">Custo estimado</span><span class="k-stat-v"><small>US$</small>{dec(t['us'], 2)}</span></div>
<div class="k-stat"><span class="k-cap">Rodou em</span><span class="k-row" style="gap:4px">{mods}</span></div>
</div></a></section>"""
    cards = []
    for d in DEPTOS:
        if d["id"] == "direcao":
            continue
        ids = ORDEM_CANVAS[d["id"]]
        tk = sum(AG_TOK.get(i, {}).get("tokens", 0) for i in ids)
        us = sum(AG_TOK.get(i, {}).get("us", 0) for i in ids)
        cards.append(f"""<section class="k-card k-depto" aria-label="{esc(NOME_DEPTO[d['id']])}" data-filtra-pai="equipe">
<div class="k-depto-head"><div><h3 class="k-card-title">{NOME_DEPTO[d['id']]}</h3><span class="k-kpi-note">{len(ids)} agentes</span></div><span class="k-depto-soma"><span class="k-tokens">{compacto(tk)} tokens</span> · {gbp(us)}</span></div>
<ul class="k-pessoas"><li aria-hidden="true"><div class="k-pessoa-linha k-pessoa-cab"><span></span><span>Agente</span><span>Status</span><span>Modelo</span><span class="k-dir">Consumo</span><span class="k-dir">Tarefas</span><span></span></div></li>
{''.join(linha_pessoa(i) for i in ids)}</ul></section>""")
    c += f'<section class="k-section"><div class="k-deptos">{"".join(cards)}</div><div class="k-empty" data-filtra-vazio="equipe" hidden><div class="k-empty-icon">{ic("search", 22)}</div><h4>Ninguém com esse filtro</h4><p>Limpe a busca ou escolha outro filtro.</p></div></section>'
    doc = estados([
        ("Números da equipe (KPIs)", "Equipe ainda não sincronizada", "Quando o sincronizador ler .claude/agents/ e painel/equipe.yaml, as contagens aparecem aqui.", "equipe", "kpi", None),
        ("Direção", "Sem a ficha do Atlas", "A direção aparece aqui quando o painel/equipe.yaml tiver o diretor.", "users", "cartoes", None),
        ("Departamento", "Ninguém neste departamento", "Quando houver um agente deste departamento em .claude/agents/, ele aparece aqui com o modelo que rodou e o consumo.", "equipe", "lista", None),
        ("Consumo por agente", "Este agente ainda não rodou", "Quando ele trabalhar numa sessão do Claude Code, os tokens, o custo e as tarefas aparecem na linha dele.", "tokens-custos", "lista", None),
    ])
    doc += variacao("Filtro sem resultado e busca", '<div class="k-empty"><div class="k-empty-icon">' + ic("search", 22) + '</div><h4>Ninguém com esse filtro</h4><p>Limpe a busca ou escolha outro filtro.</p><button type="button" class="k-btn k-btn-secondary k-btn-sm">Limpar filtros</button></div>'
                    '<p class="pv-nota">O artboard apagava (opacidade .3) quem não passava no filtro; aqui a linha some e o departamento vazio também — texto a 30% de opacidade não passa no contraste.</p>')
    def caso(titulo, quem, agid):
        return (f'<li><div class="k-pessoa-linha">{avatar(agid)}<span class="k-pessoa-id"><span class="k-pessoa-nome"><b>{titulo}</b></span>'
                f'<span class="k-pessoa-funcao">{quem}</span></span><span></span><span>{modelo_rodou(agid)}</span><span></span><span></span><span></span></div></li>')
    doc += variacao("Modelo que rodou: os três casos", (
        '<ul class="k-pessoas" style="max-width:560px">'
        + caso("Um modelo", "Otávio Reis: só Sonnet 5.5", "revisor-de-roteiro")
        + caso("Mais de um", "Atlas: " + " · ".join(f"{m} {q} %" for m, q in rodou("diretor")), "diretor")
        + caso("Ainda não rodou", "Vera Campos: nenhuma sessão em 30 dias", "portao-pauta")
        + '</ul><p class="pv-nota">Dados reais (registros do Claude Code, 30 dias até 23/10 16:02). O modelo configurado em .claude/agents/ não aparece: quem escolhe o modelo são os orquestradores, pela tarefa (decisão de 24/10). Os 11 agentes que rodaram em Sonnet 5.5 passaram a Opus em 24/10; na tela, isso aparece quando eles rodarem de novo. Com mais de um modelo, o chip é o principal e embaixo vai a fatia dele e "+N"; a lista inteira fica no title e no leitor de tela.</p>'), TAG_REAL)
    pagina("equipe.html", "equipe", "Equipe", c, doc)


# ==================================================================================================== PRODUÇÃO
def celula_video(slug, doc=False):
    th = (f'<span class="k-capa k-capa--doc" aria-hidden="true">{ict("documento", 15)}</span>' if doc else capa(slug))
    return f'<div class="k-video">{th}<div><span class="k-video-title">{NOME[slug]}</span><span class="k-video-slug">{slug}</span></div></div>'


def tabela(cab, linhas, nome, minimo, direita=()):
    th = "".join(f'<th{" class=k-dir" if i in direita else ""}>{c}</th>' for i, c in enumerate(cab))
    tr = "".join("<tr" + (f' {l[0]}' if l[0] else "") + ">" + "".join(f'<td{" class=k-dir" if i in direita else ""}>{x}</td>' for i, x in enumerate(l[1:])) + "</tr>" for l in linhas)
    return (f'<div class="k-table-wrap" role="region" aria-label="{esc(nome)}" tabindex="0" style="--table-min:{minimo}px">'
            f'<table class="k-table k-table--denso"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>')


def duas(a, b):
    return f'<div style="display:flex;flex-direction:column"><span>{a}</span><span class="k-sub">{b}</span></div>'


def fase_roteiros():
    ls = []
    for v in ROTEIROS:
        g = dt.date.fromisoformat(v["gravacao_prevista"])
        at = lon(v["atualizado"])
        ex = f'{v["extras_prontas"]} de {v["extras_planejadas"]}' if v["extras_planejadas"] else ("Nenhuma" if not v["extras_prontas"] else f'{v["extras_prontas"]} prontas')
        pal = f'<span class="k-palavra">{v["palavra"]}</span>' if v["palavra"] else '<span class="k-muted" aria-label="sem palavra-chave">—</span>'
        st = PORT_VID[v["slug"]]["roteiro"]
        pauta = PORT_VID[v["slug"]].get("pauta")
        ls.append(("data-filtra=\"producao\" data-tags=\"todos\"", celula_video(v["slug"], doc=True), "Reels", f'<span class="k-mono">v{v["versao"]}</span>', pal,
                   "Pronto" if v["pdfs"] else '<span class="k-muted">—</span>', ex,
                   f'<span data-dica="Portão do roteiro: {MAPA[st][1]}|Pauta: {MAPA[pauta][1] if pauta else "—"}">{chip_portao(st)}</span>',
                   duas(dm(g), relativo(g)), duas(dm(at), f'<span class="k-mono">{at:%H:%M}</span>')))
    return tabela(["Roteiro", "Formato", "Versão", "Palavra-chave", "PDF", "Cenas extras", "Portão do roteiro", "Gravação prevista", "Atualizado"], ls, "Roteiros", 1000)


def fase_gravados():
    if not GRAVADOS:
        return (f'<div class="k-empty" style="margin:20px"><div class="k-empty-icon">{ict("camera", 22)}</div><h4>Nada em edição agora</h4>'
                f'<p>Os próximos a entrar aqui são os {N_ROT} roteiros. Assim que você grava, o roteiro vira vídeo e fica nesta lista até o pacote ficar pronto: corte, cor, legendas, áudio, capa e QA.</p></div>')
    return ""


def fase_prontos():
    ls = []
    for p in PRONTOS:
        v = PORT_VID.get(p["slug"], {})
        s, quem = pior_de(v)
        port = f'<div class="k-event-portao">{chip_portao(s)}<span class="k-sub" style="display:inline">{quem_txt(quem)}</span></div>' if quem else chip_portao("aprovado")
        obs = ('<span class="k-small">Teste de cor · <span class="k-segura">não sai</span></span>' if p["nota_continuar"] else "—")
        ls.append(("data-filtra=\"producao\" data-tags=\"todos\"", celula_video(p["slug"]), f'<span class="k-mono">{dur(p["duracao_s"])}</span>',
                   f'<span class="k-palavra">{p["palavra"]}</span>', '<span class="k-chip k-chip--aprovado is-sm">QA aprovado</span>',
                   duas(dm(lon(p["criado_em"])), f'<span class="k-mono">{lon(p["criado_em"]):%H:%M}</span>'), port, obs))
    t = tabela(["Vídeo", "Duração", "Palavra-chave", "QA", "Pacote criado", "Portões do vídeo", "Observação"], ls, "Prontos", 900, direita=(1,))
    return t + '<p class="k-fonte" style="padding:12px 20px;border-top:1px solid var(--line)">Pacote pronto espera aqui até ser agendado no Claude Code (/publicar): vídeo final, capa, legendas e o PDF da palavra. Agendado, ele passa para Agendados.</p>'


def linha_portoes_fila(f):
    if LEGADO.get(f["slug"]) and not f["selo"]:
        return f'<div class="k-event-portao">{chip_portao("legado")}</div>'
    return ""


def fase_agendados():
    ls = []
    for f in sorted(FILA, key=lambda f: f["publicar_em"]):
        d = lon(f["publicar_em"])
        ls.append(("data-filtra=\"producao\" data-tags=\"todos\"", celula_video(f["slug"]), duas(f'{sem_dm(d)} · <span class="k-mono">{d:%H:%M}</span>', relativo(d.date())),
                   canais(f["plataformas"]), modo_chip(f["trial"]), f'<span class="k-palavra">{f["palavra"]}</span>',
                   linha_portoes_fila(f), '<span class="k-chip k-chip--agendado is-sm">Agendado</span>'))
    return tabela(["Publicação", "Data e hora", "Onde vai sair", "Modo", "Palavra-chave", "Portões", "Estado"], ls, "Agendados", 980)


def fase_publicados():
    ls = []
    mx = max(p["metricas"]["alcance"] for p in PUBS if p["metricas"])
    for p in PUBS:
        d = lon(p["publicado_em"])
        m = p["metricas"]
        links = {"instagram": p["permalink_instagram"], "facebook": p["permalink_facebook"], "linkedin": p["permalink_linkedin"]}
        if m:
            alc = f'<span class="k-n{" k-valor-foco" if m["alcance"] == mx else ""}">{n(m["alcance"])}</span>'
            vals = [alc, f'<span class="k-n">{n(m["views"])}</span>', f'<span class="k-n">{n(m["curtidas"])}</span>', f'<span class="k-n">{n(m["salvamentos"])}</span>']
        else:
            le = dm(d.date() + dt.timedelta(days=5))
            vals = [f'<span class="k-sub">lê em {le}</span>', '<span class="k-muted">—</span>', '<span class="k-muted">—</span>', '<span class="k-muted">—</span>']
        ls.append(("data-filtra=\"producao\" data-tags=\"todos\"", celula_video(p["slug"]), duas(dm(d), f'<span class="k-mono">{d:%H:%M}</span>'), modo_chip(p["trial"]),
                   f'<span class="k-mono">{dur(p["duracao_s"])}</span>', *vals, canais(p["plataformas"], links, publicado=True)))
    leit = max(lon(p["metricas"]["lido_em"]) for p in PUBS if p["metricas"])
    t = tabela(["Publicação", "Publicado em", "Modo", "Duração", "Alcance", "Visualizações", "Curtidas", "Salvos", "Onde foi publicado"], ls, "Publicados", 1080, direita=(3, 4, 5, 6, 7))
    return t + f'<p class="k-fonte" style="padding:12px 20px;border-top:1px solid var(--line)">Alcance e visualizações do Instagram, última leitura em {dm(leit)}, {leit:%H:%M}. A leitura completa sai 5 dias depois de cada post. Clique no canal para abrir o post.</p>'


def tela_producao():
    ferr = ('<label class="k-search" style="width:300px">' + ic("search", 16) + '<input type="search" placeholder="Buscar conteúdo…" aria-label="Buscar conteúdo" data-busca="producao"></label>'
           )
    c = head("Produção de conteúdo", None, ferr)
    fmt = "".join(f'<button type="button" class="k-filtro" data-grupo="formato" data-valor="{k}" aria-pressed="{"true" if k == "todos" else "false"}">{r}</button>'
                  for k, r in (("todos", "Todos"), ("reels", "Reels"), ("stories", "Stories"), ("carrossel", "Carrossel")))
    c += f"""<div class="k-section-head" style="margin-top:-8px"><div class="k-row" style="gap:10px"><span class="k-cap">Formato</span><div class="k-filtros" role="group" aria-label="Filtrar por formato">{fmt}</div></div>
<p class="k-fonte">Lido de <span class="k-mono">videos/</span>, <span class="k-mono">05-render-pronto/</span>, <span class="k-mono">06-publicar/</span> e <span class="k-mono">07-publicados/</span> · sincronizado em {SYNC_TXT}</p></div>"""
    vids_ag = len({ORIGEM[f["slug"]] for f in FILA})
    vids_pub = len({ORIGEM[p["slug"]] for p in PUBS})
    prox = lon(sorted(FILA, key=lambda f: f["publicar_em"])[0]["publicar_em"])
    melhor = max((p for p in PUBS if p["metricas"]), key=lambda p: p["metricas"]["alcance"])
    com_pdf = sum(1 for v in ROTEIROS if v["pdfs"])
    fases = [("roteiros", "Roteiros", len(ROTEIROS), "Só o roteiro. Ainda não gravados.", f"{com_pdf} com PDF · o mais antigo espera desde {dm(dt.date.fromisoformat(mais_antigo['gravacao_prevista']))}"),
             ("gravados", "Gravados", len(GRAVADOS), "Em edição e pós-produção.", "Nenhum em edição agora" if not GRAVADOS else ""),
             ("prontos", "Prontos", len(PRONTOS), "Pacote pronto, ainda sem data.", f"{NOME[pronto['slug']]} · teste, não sai"),
             ("agendados", "Agendados", len(FILA), "Na fila, com data e hora.", f"{vids_ag} vídeos · próxima {sem_dm(prox).lower()}, {prox:%H:%M}"),
             ("publicados", "Publicados", len(PUBS), "No ar no Instagram e no Facebook.", f"{vids_pub} vídeos · melhor: {NOME[melhor['slug']]}")]
    elos = ["você grava", "pós e QA", "você agenda", "publica no horário"]
    fx = []
    for i, (k, r, q, d_, m_) in enumerate(fases):
        fx.append(f'<button type="button" class="k-fase" data-grupo="fase" data-valor="{k}" aria-pressed="{"true" if i == 0 else "false"}" aria-controls="fase-tabela"><span class="k-cap">{r}</span><span class="k-fase-n">{q}</span><span class="k-fase-d">{d_}</span><span class="k-fase-m">{m_}</span></button>')
        if i < 4:
            fx.append(f'<div class="k-fase-elo" aria-hidden="true">{ict("seta-direita", 18)}{elos[i]}</div>')
    c += f'<section class="k-section" aria-label="Fases"><div class="k-fases">{"".join(fx)}</div></section>'
    tabs = {"roteiros": ("Roteiros", "na ordem de gravação prevista", "Um roteiro vira vídeo quando você grava.", fase_roteiros()),
            "gravados": ("Gravados", "em pós-produção", "Do corte ao QA: cor, legendas, áudio e capa.", fase_gravados()),
            "prontos": ("Prontos", "pacotes em 05-render-pronto/", "Agendado no Claude Code (/publicar), o pacote vai para a fila de publicação.", fase_prontos()),
            "agendados": ("Agendados", "pela data de publicação", "Publica sozinho no horário marcado.", fase_agendados()),
            "publicados": ("Publicados", "do mais recente ao mais antigo", "Clique no canal para abrir o post.", fase_publicados())}
    cont = {"roteiros": len(ROTEIROS), "gravados": len(GRAVADOS), "prontos": len(PRONTOS), "agendados": len(FILA), "publicados": len(PUBS)}
    paineis = []
    for k, (t_, o_, d_, corpo) in tabs.items():
        paineis.append(f"""<div data-de="fase" data-valor="{k}"{'' if k == 'roteiros' else ' hidden'}>
<div class="k-card-head" style="padding:14px 20px"><div class="k-row" style="gap:10px"><h2 class="k-card-title">{t_} · {cont[k]}</h2><span class="k-kpi-note">{o_}</span></div><span class="k-fonte" style="color:var(--ink-2)">{d_}</span></div>{corpo}</div>""")
    vazio_fmt = "".join(f'<div data-de="formato" data-valor="{k}" hidden><div class="k-empty" style="margin:20px"><div class="k-empty-icon">{ic("inbox", 22)}</div><h4>Nenhum {r} ainda</h4><p>Hoje a operação produz Reels. Quando houver {pl}, eles passam pelas mesmas fases e aparecem aqui.</p></div></div>'
                        for k, r, pl in (("stories", "story", "stories"), ("carrossel", "carrossel", "carrosséis")))
    tabela_card = f'<section class="k-card k-span-12 k-xl-9" id="fase-tabela" aria-label="Lista da fase" style="overflow:hidden"><div data-de="formato" data-valor="todos reels">{"".join(paineis)}</div>{vazio_fmt}</section>'
    pa = {r["portao"]: {} for r in B["telas_portoes_por_area"]}
    for r in B["telas_portoes_por_area"]:
        pa[r["portao"]][r["status"]] = r["n"]
    def area(p):
        x = pa.get(p, {})
        if p == "publicacao":
            leg = sum(1 for f in FILA if LEGADO.get(f["slug"]) and not f["selo"])
            return f"{leg} legado · sem selo"
        partes = []
        if x.get("pendente"): partes.append(f'{x["pendente"]} ainda não rodaram')
        if x.get("nao_se_aplica"): partes.append(f'{x["nao_se_aplica"]} não se aplicam')
        for s in ("aprovado", "bloqueado", "escalado", "vencido"):
            if x.get(s): partes.append(f'{x[s]} {MAPA[s][1].lower()}')
        return " · ".join(partes)
    kv = "".join(f'<li><span>{r}</span><span class="k-kv-v">{area(p)}</span></li>' for p, r in (("pauta", "Pauta"), ("roteiro", "Roteiro"), ("imagem", "Imagem"), ("corte", "Corte"), ("publicacao", "Publicação")))
    lado = f"""<div class="k-span-12 k-xl-3 k-lado">
<section class="k-card" aria-labelledby="t-aten" style="padding:16px 16px 8px"><div class="k-card-head" style="padding:0 4px"><h2 class="k-card-title" id="t-aten">Precisam de atenção</h2><span class="k-chip k-chip--producao no-dot is-sm">{len(AVISOS)}<span class="k-sr-only"> avisos</span></span></div>
<div style="display:flex;flex-direction:column">{avisos_lista()}</div></section>
<section class="k-card k-pad" aria-labelledby="t-port" style="padding:16px 20px"><div class="k-card-head"><h2 class="k-card-title" id="t-port">Portões</h2><span class="k-mono k-muted">5 áreas</span></div>
<p class="k-fonte" style="margin:6px 0 10px;color:var(--ink-2)">Nenhum veredicto nos vídeos ainda: os portões começaram em 22 out.</p><ul class="k-kv">{kv}</ul></section></div>"""
    c += f'<section class="k-section"><div class="k-grid">{tabela_card}{lado}</div></section>'
    doc = estados([
        ("Fases (os 5 cartões)", "Nada em produção", "Quando houver um roteiro em videos/, ele aparece em Roteiros e anda pelas fases até Publicados.", "videos-portoes", "kpi", None),
        ("Tabela da fase", "Nada nesta fase", "Cada fase tem a sua frase: Gravados diz o que entra ali e quando; Prontos, que o pacote espera até você agendar.", "inbox", "tabela", None),
        ("Precisam de atenção", "Nada pede atenção agora", "Quando um roteiro atrasar, um portão parar um vídeo ou um pronto não puder sair, aparece aqui.", "check", "lista", None),
        ("Portões", "Nenhum portão no banco", "Quando o portoes.py registrar o estado de um vídeo, as cinco áreas aparecem aqui com a contagem.", "lock", "lista", None),
    ])
    corpo = ""
    for k in ("gravados", "prontos", "agendados", "publicados"):
        t_, o_, d_, cp = tabs[k]
        corpo += f'<div class="tl-variacao"><h3 class="k-card-title" style="margin-bottom:8px">{t_} · {cont[k]} <span class="k-kpi-note">({o_})</span></h3><div class="k-card" style="overflow:hidden">{cp}</div></div>'
    doc += variacao("As outras fases (como aparecem ao tocar no cartão)", corpo, TAG_REAL)
    doc += variacao("Estados de portão que hoje não acontecem (exemplo de cada fase)", f"""<div class="pv-grade pv-grade-2">
<div class="k-card k-pad"><span class="k-cap">Roteiros · portão do roteiro bloqueado</span><p class="pv-nota" style="margin:8px 0">{chip_portao('bloqueado')} — o vídeo não sai da fase até o roteiro voltar ao portão; o aviso entra em "Precisam de atenção".</p></div>
<div class="k-card k-pad"><span class="k-cap">Agendados · post não legado com portão vencido</span><div class="k-event-portao" style="margin:8px 0">{chip_portao('vencido')}<span class="k-small k-ink2">imagem ·</span><span class="k-small k-segura">não sai</span></div><p class="pv-nota" style="margin:0">Estado do vídeo: <span class="k-chip k-chip--bloqueado is-sm">Bloqueado</span> (vem antes de Agendado).</p></div>
<div class="k-card k-pad"><span class="k-cap">Agendados · tudo aprovado</span><div class="k-event-portao" style="margin:8px 0">{chip_portao('aprovado')}</div></div>
<div class="k-card k-pad"><span class="k-cap">Publicados · portão venceu depois de sair</span><p class="pv-nota" style="margin:8px 0">A linha continua em Publicados, com o link; ao lado do nome, {chip_portao('vencido')} <span class="k-small k-ink2">imagem</span> — nunca no lugar do "publicado" (PI40).</p></div>
</div>""", TAG_EX)
    pagina("producao.html", "videos-portoes", "Produção de conteúdo", c, doc)


# ==================================================================================================== CALENDÁRIO
EV = {}
for p in PUBS:
    d = lon(p["publicado_em"])
    m = p["metricas"]
    extra = (f'{n(m["alcance"])} de alcance' + (" · Trial" if p["trial"] else "")) if m else f'métricas em {dm(d.date() + dt.timedelta(days=5))}'
    EV.setdefault(d.date(), []).append({"slug": p["slug"], "hora": f"{d:%H:%M}", "status": "Publicado", "plat": p["plataformas"], "extra": extra, "fila": None})
for f in FILA:
    d = lon(f["publicar_em"])
    EV.setdefault(d.date(), []).append({"slug": f["slug"], "hora": f"{d:%H:%M}", "status": "Agendado", "plat": f["plataformas"],
                                        "extra": ("Trial Reel" if f["trial"] else "Normal") + f' · palavra {f["palavra"]}', "fila": f})
GRAV = {}  # 24/10: o calendário mostra só o que está agendado para publicar; gravação prevista fica só em Produção · Roteiros
VAGAS_DIA = {6: HOR["vagas_semanais"]["domingo"], 1: HOR["vagas_semanais"]["terca"], 2: HOR["vagas_semanais"]["quarta"]}


def canal_cls(plat):
    if plat == ["instagram"]:
        return " k-event--ig"
    if plat == ["facebook"]:
        return " k-event--fb"
    return ""


def canais_txt(plat):
    return " · ".join({"instagram": "Instagram", "facebook": "Facebook", "linkedin": "LinkedIn"}[c] for c in plat)


def evento_mes(e):
    port = ""
    if e["fila"]:
        port = f'<div class="k-event-portao is-compacto">{ic("lock", 12)}<span class="k-sr-only">Portões:</span>{linha_portoes_fila(e["fila"]).replace("<div class=" + chr(34) + "k-event-portao" + chr(34) + ">", "").replace("</div>", "")}</div>'
    return (f'<div class="k-event k-event--mes{canal_cls(e["plat"])}{" is-publicado" if e["status"] == "Publicado" else ""}" title="{e["hora"]} · {NOME[e["slug"]]} · {canais_txt(e["plat"])} · {e["status"]}">'
            f'<div class="k-event-linha">{capa(e["slug"], "k-capa--xs", alt=False)}<div class="k-event-txt"><span><b class="k-mono">{e["hora"]}</b> · {e["status"]}</span>'
            f'<b>{NOME[e["slug"]]}</b><span>{canais_txt(e["plat"])}</span></div></div>{port}</div>')


def mes():
    ini = dt.date(2026, 9, 27)
    cells = []
    for i in range(42):
        d = ini + dt.timedelta(days=i)
        evs = EV.get(d, [])
        gs = GRAV.get(d, [])
        vaga = VAGAS_DIA.get(d.weekday()) if (d >= HOJE and d.weekday() in VAGAS_DIA and not evs) else None
        cls = "k-mes-dia" + (" is-fora" if d.month != 10 else "") + (" is-passado" if d < HOJE else "") + (" is-hoje" if d == HOJE else "")
        if not evs and not gs and not vaga and d != HOJE:
            cls += " is-vazio"
        rot = f"{d.day} {MES[d.month - 1]}" if d.day == 1 else str(d.day)
        dl = sem_dm(d) + (" · hoje" if d == HOJE else "")
        corpo = "".join(evento_mes(e) for e in evs)
        if vaga:
            corpo += f'<span class="k-vaga"><span>Vaga livre</span><span class="k-mono">{vaga}</span></span>'
        if d == HOJE and not corpo:
            corpo = '<span class="k-mes-dl k-mes-nada">Nada programado.</span>'
        cells.append(f'<div class="{cls}"><span class="k-mes-n"{" aria-current=" + chr(34) + "date" + chr(34) if d == HOJE else ""}>{rot}</span><span class="k-mes-dl">{dl}</span>{corpo}</div>')
    cab = "".join(f'<span class="k-cap">{s}</span>' for s in ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"])
    return f'<div class="k-mes-cab" aria-hidden="true">{cab}</div><div class="k-mes">{"".join(cells)}</div>'


def semana():
    ini = dt.date(2026, 10, 18)
    cols = []
    for i in range(7):
        d = ini + dt.timedelta(days=i)
        evs = EV.get(d, [])
        gs = GRAV.get(d, [])
        vaga_livre = d < HOJE and d.weekday() in VAGAS_DIA and not evs
        nota = "hoje" if d == HOJE else ("vaga sem post" if vaga_livre else "")
        corpo = ""
        for e in evs:
            port = ""
            if e["fila"]:
                port = f'<div class="k-event-portao"><span>Portões:</span>{linha_portoes_fila(e["fila"]).replace("<div class=" + chr(34) + "k-event-portao" + chr(34) + ">", "").replace("</div>", "")}</div>'
            f_ = CAPA.get(e["slug"])
            img = f'<img src="img/capas/{f_}" alt="Capa de {esc(NOME[e["slug"]])}">' if f_ else ""
            corpo += (f'<div class="k-event k-event--semana{canal_cls(e["plat"])}{" is-publicado" if e["status"] == "Publicado" else ""}">{img}'
                      f'<span><b class="k-mono">{e["hora"]}</b> · {e["status"]}</span><b>{NOME[e["slug"]]}</b><span>{canais_txt(e["plat"])}</span><span>{e["extra"]}</span>{port}</div>')
        if not evs and not gs:
            corpo = f'<span class="k-semana-vazio">{"A vaga de " + SEM_LONGO[d.weekday()].split("-")[0].lower() + " " + VAGAS_DIA[d.weekday()] + " ficou livre." if vaga_livre else "Nada programado."}</span>'
        cols.append(f'<div class="k-semana-dia{" is-hoje" if d == HOJE else ""}"><div class="k-semana-cab"><span class="k-mes-n">{SEM[d.weekday()]} {d.day}</span><span class="k-semana-nota">{nota}</span></div>{corpo}</div>')
    return f'<div class="k-semana">{"".join(cols)}</div>'


def tela_calendario():
    c = head("Calendário")
    leg = ('<div class="k-cal-legenda"><span><i style="background:var(--accent)"></i>Instagram</span><span><i style="background:var(--ink)"></i>Instagram e Facebook</span>'
           '<span><i class="is-contorno"></i>Publicado</span><span><i class="is-tracejado"></i>Vaga livre</span><span>' + ic("lock", 13) + 'Portões</span></div>')
    seg = ('<div class="k-seg is-alto" role="group" aria-label="Visualização"><button type="button" data-grupo="vista" data-valor="mes" aria-pressed="true">Mês</button>'
           '<button type="button" data-grupo="vista" data-valor="semana" aria-pressed="false">Semana</button></div>')
    topo = f"""<div class="k-cal-topo" style="margin-bottom:16px"><div class="k-cal-nav"><button type="button" class="k-btn k-btn-secondary k-btn-sm">Hoje</button>
<button type="button" class="k-btn k-btn-ghost k-btn-sm k-btn-icon" aria-label="Mês anterior"><span data-icon="chevron-right" data-size="16" aria-hidden="true" style="transform:rotate(180deg)"></span></button>
<button type="button" class="k-btn k-btn-ghost k-btn-sm k-btn-icon" aria-label="Próximo mês">{ic('chevron-right', 16)}</button>
<h2 class="k-h3" data-de="vista" data-valor="mes">Outubro 2026</h2><h2 class="k-h3" data-de="vista" data-valor="semana" hidden>18 – 24 out 2026</h2></div>
<div class="k-row" style="gap:20px">{leg}{seg}</div></div>"""
    c += topo
    cal = f'<section class="k-card k-span-12 k-xxl-9" aria-label="Calendário" style="overflow:hidden"><div data-de="vista" data-valor="mes">{mes()}</div><div data-de="vista" data-valor="semana" hidden>{semana()}</div></section>'
    leg_n = sum(1 for f in FILA if LEGADO.get(f["slug"]) and not f["selo"])
    rel_cols = "".join(f'<span class="{"is-foco" if h["relativo"] >= 99 else ""}" style="height:{h["relativo"]}%"></span>' for h in HOR["linhas"])
    rel_rot = "".join(f'<span class="{"is-foco" if h["relativo"] >= 99 else ""}">{h["faixa"]}</span>' for h in HOR["linhas"])
    picos = "".join(f'<span class="k-chip k-chip--agendado no-dot is-sm">{p}</span>' for p in HOR["picos_no_app"])
    vagas = "".join(f'<span class="k-chip k-chip--producao no-dot is-sm">{r} {HOR["vagas_semanais"][k]}</span>' for k, r in (("domingo", "Dom"), ("terca", "Ter"), ("quarta", "Qua")))
    lado = f"""<div class="k-span-12 k-xxl-3 k-lado k-lado--xxl">
<section class="k-card" aria-labelledby="t-fila" style="padding:18px 20px"><div class="k-card-head"><h2 class="k-card-title" id="t-fila">Fila</h2><span class="k-mono k-muted">06-publicar/</span></div>
<ul class="k-kv k-kv--grande" style="margin-top:8px">
<li><span class="k-kv-t"><b>Pronto para publicar</b><small>agendadas, saem sozinhas no horário</small></span><span class="k-kv-n">{len(FILA)}</span></li>
<li><span class="k-kv-t"><b>Aguardando portão</b><small>as {leg_n} da fila são legado: publicam sem selo</small></span><span class="k-kv-n is-zero">0</span></li>
<li><span class="k-kv-t"><b>Sem horário</b><small>o único pronto ({NOME[pronto['slug']]}) é teste de cor e não sai</small></span><span class="k-kv-n is-zero">0</span></li></ul>
<a class="k-atalho" href="producao.html">A caminho: {N_ROT} roteiros ainda sem gravação{ic('chevron-right', 14)}</a></section>
<section class="k-card" aria-labelledby="t-hor" style="padding:18px 20px;display:flex;flex-direction:column"><div class="k-card-head"><h2 class="k-card-title" id="t-hor">Melhores horários</h2><span class="k-kpi-note">atividade de quem segue</span></div>
<div class="k-colunas" role="img" aria-label="Atividade dos seguidores por faixa de 3 horas: mais alta às 15h, 18h e 21h" style="margin-top:16px">{rel_cols}</div><div class="k-colunas-rot" aria-hidden="true">{rel_rot}</div>
<div style="display:flex;flex-direction:column;gap:8px;margin-top:16px;padding-top:14px;border-top:1px solid var(--line)"><span class="k-cap">Picos no app</span><div class="k-row" style="gap:6px">{picos}</div>
<span class="k-cap" style="margin-top:6px">Suas vagas</span><div class="k-row" style="gap:6px">{vagas}</div></div>
<p class="k-fonte" style="margin-top:12px">Print do app do Instagram (17 out, GMT+1), dia mostrado: quinta-feira. Faixas de 3 h, altura relativa à mais alta. Mostra quem já segue; os Trial Reels vão dizer o melhor horário para quem ainda não segue.</p>
{detalhes(['Faixa', 'Atividade (relativa)'], [[h['faixa'], str(h['relativo']) + '%'] for h in HOR['linhas']], 'Atividade por faixa de horário')}</section></div>"""
    c += f'<section class="k-section"><div class="k-grid">{cal}{lado}</div></section>'
    doc = estados([
        ("Calendário (mês e semana)", "Nada programado neste mês", "Quando houver post agendado, publicado ou gravação prevista, aparece no dia. As vagas livres das próximas semanas aparecem tracejadas.", "calendario", "grafico", "Ver produção"),
        ("Fila", "Fila vazia", "Quando um pacote for agendado, ele entra na fila (06-publicar/) e é contado aqui.", "inbox", "lista", None),
        ("Melhores horários", "Sem print de horários", "Os horários de atividade só existem no app do Instagram; quando houver um print novo em _controle/perfil/, ele aparece aqui.", "clock", "grafico", None),
    ])
    doc += variacao("Vista Semana (18 – 24 out)", f'<div class="k-card" style="overflow:hidden">{semana()}</div>', TAG_REAL)
    doc += variacao("Linha de portões no evento (casos que hoje não acontecem)", f"""<div class="pv-grade pv-grade-3">
<div class="k-event k-event--mes k-event--ig"><div class="k-event-linha"><span class="k-capa k-capa--xs" aria-hidden="true"></span><div class="k-event-txt"><span><b class="k-mono">21:00</b> · Agendado</span><b>Reel com a cor refeita</b><span>Instagram</span></div></div><div class="k-event-portao is-compacto">{ic('lock', 12)}{chip_portao('vencido')}<span>imagem ·</span><span class="k-segura">não sai</span></div></div>
<div class="k-event k-event--mes"><div class="k-event-linha"><span class="k-capa k-capa--xs" aria-hidden="true"></span><div class="k-event-txt"><span><b class="k-mono">19:00</b> · Agendado</span><b>Reel recém-posto na fila</b><span>Instagram · Facebook</span></div></div><div class="k-event-portao is-compacto">{ic('lock', 12)}{chip_portao('pendente')}<span>publicação ·</span><span class="k-segura">não sai</span></div></div>
<div class="k-event k-event--mes"><div class="k-event-linha"><span class="k-capa k-capa--xs" aria-hidden="true"></span><div class="k-event-txt"><span><b class="k-mono">19:00</b> · Agendado</span><b>Reel com tudo aprovado</b><span>Instagram · Facebook</span></div></div><div class="k-event-portao is-compacto">{ic('lock', 12)}{chip_portao('aprovado')}</div></div>
</div><p class="pv-nota">No mês, o cadeado faz o papel da palavra "Portões:" (que fica para o leitor de tela); na semana, a palavra aparece. O "não sai" é danger também dentro do evento (PI38).</p>""", TAG_EX)
    pagina("calendario.html", "calendario", "Calendário", c, doc)


# ==================================================================================================== DESEMPENHO
def tela_desempenho():
    per = f'{ic("calendario", 16)}Últimos 28 dias · 25 set – 22 out · leitura de {dm(lon(P22["lido_em"]))}, {lon(P22["lido_em"]):%H:%M}'
    c = head("Desempenho", None, f'<span class="k-page-meta">{per}</span>')
    def kpi(cap, val, dl, nota):
        return f'<div class="k-card k-kpi k-kpi--linha k-span-3"><span class="k-cap">{cap}</span><div class="k-kpi-linha"><span class="k-kpi-value">{val}</span><span class="k-kpi-lado">{dl}<span class="k-kpi-note">{nota}</span></span></div></div>'
    sd = P22["seguidores"] - P16["seguidores"]
    vd = (P22["views"] / P16["views"] - 1) * 100
    ad = (P22["alcance"] / P16["alcance"] - 1) * 100
    pd = (P22["visitas_perfil"] / P16["visitas_perfil"] - 1) * 100
    c += f"""<section class="k-section" aria-label="Números do perfil"><div class="k-grid k-grid--tiles">
{kpi('Seguidores', n(P22['seguidores']), delta(pct(sd / P16['seguidores'] * 100).replace('-', '−'), 'flat', 'quase igual a 16 out'), f'{str(sd).replace("-", "−")} vs. leitura de 16 out')}
{kpi('Visualizações', n(P22['views']), delta(pct(abs(vd)), 'down', 'a menos que em 16 out'), f'eram {n(P16["views"])}')}
{kpi('Contas alcançadas', n(P22['alcance']), delta(pct(ad), 'up', 'a mais que em 16 out'), f'eram {n(P16["alcance"])}')}
{kpi('Visitas ao perfil', n(P22['visitas_perfil']), delta(pct(pd), 'up', 'a mais que em 16 out'), f'eram {n(P16["visitas_perfil"])} · {P22["toques_no_link"]} toques no link')}
</div></section>"""
    marcos = []
    nomes_m = {"2026-09-17-demis-hassabis": "13 out · Demis Hassabis"}
    for p in sorted(PUBS, key=lambda p: p["publicado_em"]):
        i = (lon(p["publicado_em"]).date() - dt.date(2026, 9, 25)).days
        if 0 <= i < 28:
            marcos.append({"i": i, "rotulo": nomes_m.get(p["slug"], "")})
    cfg = curva_cfg([{"nome": "Visualizações", "cor": "chart-1", "area": True, "v": EXEMPLO_CURVA["views"]},
                     {"nome": "Alcance", "cor": "chart-2", "v": EXEMPLO_CURVA["alcance"]}], 300, [0, 100, 200, 300], marcos=marcos)
    fb22 = P22["alcance_nao_seguidores"] / (P22["alcance_nao_seguidores"] + P22["alcance_seguidores"]) * 100
    circ = 2 * 3.141592653589793 * 66
    c += f"""<section class="k-section"><div class="k-grid">
<section class="k-card k-span-8" aria-labelledby="t-cres" style="padding:20px 24px;display:flex;flex-direction:column">
<div class="k-card-head" style="align-items:baseline;flex-wrap:wrap"><div class="k-row" style="gap:12px;align-items:baseline"><h2 class="k-h3" id="t-cres">crescimento.</h2><span class="k-kpi-note">visualizações e alcance por dia {EX}</span></div>
<div class="k-legend"><span><i style="background:var(--chart-1)"></i>Visualizações · {n(P22['views'])}</span><span><i style="background:var(--chart-2)"></i>Alcance · {n(P22['alcance'])} contas</span></div></div>
<div style="margin-top:12px"><svg class="k-chart" data-curva="{cfg}" data-altura="210" role="img" aria-label="Exemplo da forma: visualizações e alcance por dia, 25 set a 22 out, em alta desde 13 out, quando saiu o Reel de Demis Hassabis. Os pontos marcam os dias dos Reels."></svg></div>
<p class="k-fonte" style="margin-top:8px">Totais reais da API. O dia a dia ainda não chega pelo sincronizador: a forma da curva é exemplo e os pontos marcam as datas reais dos Reels.</p>
{detalhes(['O que existe', 'Valor'], [['Visualizações · 28 dias', n(P22['views'])], ['Alcance · 28 dias', n(P22['alcance'])], ['Por dia', 'ainda não chega']], 'Crescimento em números')}</section>
<section class="k-card k-span-4" aria-labelledby="t-bolha" style="padding:20px 24px;display:flex;flex-direction:column">
<div class="k-row" style="gap:12px;align-items:baseline"><h2 class="k-h3" id="t-bolha">fora da bolha.</h2><span class="k-kpi-note">quem os conteúdos alcançaram</span></div>
<div style="display:flex;align-items:center;flex-wrap:wrap;gap:16px 22px;margin-top:18px">
<div style="position:relative;width:150px;height:150px;flex:none"><svg class="k-anel" viewBox="0 0 150 150" width="150" height="150" role="img" aria-label="{round(fb22)}% do alcance são não seguidores ({P22['alcance_nao_seguidores']} contas) e {100 - round(fb22)}% seguidores ({P22['alcance_seguidores']} contas)"><circle class="trilho" cx="75" cy="75" r="66" fill="none" stroke-width="18"></circle><circle class="valor" cx="75" cy="75" r="66" fill="none" stroke-width="18" stroke-dasharray="{fb22/100*circ:.2f} {circ:.2f}"></circle></svg>
<div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center"><span class="k-num k-tokens is-grande" style="font-size:32px;line-height:36px;font-weight:700;letter-spacing:-.03em">{round(fb22)}%</span><span class="k-kpi-note" style="color:var(--ink-2)">não seguidores</span></div></div>
<div style="display:flex;flex-direction:column;gap:14px;min-width:0">
<div><span class="k-legend"><span><i style="background:var(--chart-1)"></i>Não seguidores</span></span><span class="k-metric-l" style="display:block">{P22['alcance_nao_seguidores']} <small class="k-kpi-note">{round(fb22)}%</small></span></div>
<div><span class="k-legend"><span><i style="background:var(--surface-sunken);box-shadow:inset 0 0 0 1px var(--line-strong)"></i>Seguidores</span></span><span class="k-metric-l" style="display:block">{P22['alcance_seguidores']} <small class="k-kpi-note">{100 - round(fb22)}%</small></span></div></div></div>
<div style="margin-top:auto;padding-top:14px;border-top:1px solid var(--line);display:flex;align-items:baseline;justify-content:space-between;flex-wrap:wrap;gap:4px 12px"><span class="k-kpi-note" style="color:var(--ink-2)">Em 6 dias (16 → 22 out), com 3 Trials no ar</span><span class="k-num" style="font-size:13px;font-weight:600;color:var(--positive)">+{P22['alcance_nao_seguidores'] - P16['alcance_nao_seguidores']} não seguidores</span></div>
{detalhes(['Quem foi alcançado', '16 out', '22 out'], [['Não seguidores', n(P16['alcance_nao_seguidores']), n(P22['alcance_nao_seguidores'])], ['Seguidores', n(P16['alcance_seguidores']), n(P22['alcance_seguidores'])]], 'Fora da bolha em números')}</section>
</div></section>"""
    s, ts = barras_paises("seguidores", "n")
    a, ta = barras_paises("alcancados", "n")
    rs, _ = paises("seguidores")
    ra, _ = paises("alcancados")
    pos_s = {r["chave"]: i + 1 for i, r in enumerate(rs)}
    pos_a = {r["chave"]: i + 1 for i, r in enumerate(ra)}
    primeiro = rs[0]["chave"]
    nota_pub = (f"Quem segue e quem os vídeos alcançam vêm de lugares diferentes: o 1.º país de quem segue ({NOME_PAIS[primeiro]}, "
                f"{pct(rs[0]['valor'] / ts * 100)}) é o {pos_a.get(primeiro, '—')}.º de quem foi alcançado ({pct(next(r['valor'] for r in ra if r['chave'] == primeiro) / ta * 100)}).")
    # ranking
    rk = sorted([p for p in PUBS if p["metricas"]], key=lambda p: -p["metricas"]["alcance"])
    an = {x["slug"]: x for x in ANALISE["linhas"]}
    linhas = []
    for i, p in enumerate(rk):
        m = p["metricas"]
        a_ = an.get(p["slug"], {})
        nao = a_.get("nao_seguidores", "—")
        nao_pct = (pct(a_["pct_nao_seguidores"], 0) if a_.get("pct_nao_seguidores") else ("Trial" if p["trial"] else ""))
        ret = (f'<span class="k-medidor" data-dica="Tempo médio assistido ÷ duração|{dec(m["tempo_medio_s"])} s de {dur(p["duracao_s"])}"><span class="k-medidor-trilho"><span style="width:{min(100, m["pct_assistido"]):.1f}%"></span></span><span class="k-n">{pct(m["pct_assistido"])}</span></span>'
               if not m["suspeito"] else '<span class="k-medidor" data-dica="A API devolveu um tempo médio impossível|1.513 s num vídeo de 2:39 — fora da conta"><span class="k-medidor-trilho"></span><span class="k-n k-muted">—</span></span>')
        eng = m["interacoes"] / m["alcance"] * 100 if m["alcance"] else 0
        meta = f'{dm(lon(p["publicado_em"]))} · {"Trial" if p["trial"] else "Normal"} · {dur(p["duracao_s"])}'
        linhas.append((f'class="{"is-top" if i < 3 else ""}"', f'<span class="k-rank-pos is-{i + 1}">{i + 1}</span>',
                       f'<div class="k-video">{capa(p["slug"], "k-capa--sm")}<div><span class="k-video-title">{NOME[p["slug"]]}</span><span class="k-video-meta">{meta}</span></div></div>',
                       f'<span class="k-n">{n(m["views"])}</span>', f'<span class="k-n{" k-valor-foco" if i == 0 else ""}">{n(m["alcance"])}</span>',
                       f'<span class="k-n">{nao}</span><span class="k-sub">{nao_pct}</span>', ret,
                       f'<span class="k-n">{pct(eng)}</span><span class="k-sub">{m["interacoes"]} {"interação" if m["interacoes"] == 1 else "interações"}</span>',
                       '<span class="k-n k-muted" data-dica="A API da Meta não informa seguidores ganhos por Reel">n/d</span>'))
    pend = [p for p in PUBS if not p["metricas"]]
    tab = tabela(["#", "Vídeo", "Views", "Alcance", "Não seguidores", "% assistido", "Engajamento", "Seg. ganhos"], linhas, "Ranking dos Reels", 760, direita=(2, 3, 4, 6, 7))
    c += f"""<section class="k-section"><div class="k-grid">
<section class="k-card k-span-12 k-xl-5" aria-labelledby="t-pais" style="padding:20px 24px;display:flex;flex-direction:column">
<h2 class="k-h3" id="t-pais">de onde vem o público.</h2>
<div class="k-grid" style="grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:28px;margin-top:16px">
<div><div class="k-card-head" style="margin-bottom:8px"><span class="k-body-strong" style="font-size:13px">Quem segue</span><span class="k-mono k-muted">{n(ts)} com país</span></div>{s}</div>
<div><div class="k-card-head" style="margin-bottom:8px"><span class="k-body-strong" style="font-size:13px">Quem os vídeos alcançam</span><span class="k-mono k-muted">{n(ta)} com país</span></div>{a}</div></div>
<p class="k-fonte" style="margin-top:auto;padding-top:12px">{esc(nota_pub)}</p></section>
<section class="k-card k-span-12 k-xl-7" aria-labelledby="t-rank" style="padding:20px 24px;display:flex;flex-direction:column">
<div class="k-card-head" style="align-items:baseline;flex-wrap:wrap"><div class="k-row" style="gap:12px;align-items:baseline"><h2 class="k-h3" id="t-rank">conteúdo que funciona.</h2><span class="k-kpi-note">ranking por alcance · Reels com leitura</span></div><span class="k-kpi-note">{' · '.join(NOME[p['slug']] + ' entra em ' + dm(lon(p['publicado_em']).date() + dt.timedelta(days=5)) for p in pend)}</span></div>
<div style="margin-top:12px">{tab}</div>
<div class="k-destaque" style="margin-top:16px">{ic('sparkle', 18)}<div><span class="k-destaque-t">O único Reel normal, {NOME[rk[0]['slug']]}, chegou a {an[rk[0]['slug']]['nao_seguidores']} não seguidores. Os três Trials somados chegaram a {sum(int(an[p['slug']]['nao_seguidores'].strip('~')) for p in rk[1:])}.</span><span class="k-destaque-m">Análise de 22 out · % assistido = tempo médio ÷ duração · seguidores ganhos: a API não informa por Reel</span></div></div></section>
</div></section>"""
    doc = estados([
        ("Números do perfil (KPIs)", "Ainda não há leitura do perfil", "Quando o perfil.py ler a conta, seguidores, visualizações, alcance e visitas aparecem aqui, comparados com a leitura anterior.", "eye", "kpi", None),
        ("Crescimento", "Ainda não há dia a dia", "Quando o perfil.py ler a conta todo dia, a curva de visualizações e alcance aparece aqui.", "desempenho", "grafico", None),
        ("Fora da bolha", "Sem divisão seguidor × não seguidor", "A Meta separa quem segue de quem não segue na janela de 28 dias; quando vier, aparece aqui.", "users", "grafico", None),
        ("De onde vem o público", "Sem dados de país", "A Meta só mostra países a partir de 100 contas; quando houver, as duas listas aparecem aqui.", "users", "lista", None),
        ("Conteúdo que funciona", "Nenhum Reel com leitura ainda", "A 1.ª leitura sai 5 dias depois de cada post; os Reels lidos aparecem aqui, do maior alcance para o menor.", "play", "tabela", None),
    ])
    pagina("desempenho.html", "desempenho", "Desempenho", c, doc)


# ==================================================================================================== BIBLIOTECA
def gb(b, c=2):
    return dec(b / 1e9, c) + " GB"


def tam(b):
    if b >= 1e9:
        return gb(b)
    if b >= 1e6:
        return dec(b / 1e6, 1 if b < 1e7 else 0) + " MB"
    return n(b / 1e3) + " KB"


def tela_biblioteca():
    """24/10: a Biblioteca é o ACERVO DE ESTILOS (canvas aprovado, painel/referencias/claude-design/biblioteca-2026-10-24/)."""
    A = B["telas_acervo"][0]
    L = A["looks"]["luts"]
    ativa = A["looks"]["versao_ativa"]
    c = head("Biblioteca")
    # 24/10 (aba Sistema aprovada): nome, tipo e o que faz aqui vêm do painel/biblioteca.yaml (ferramentas, modelos)
    import yaml
    BY = yaml.safe_load((D.parent / "biblioteca.yaml").read_text(encoding="utf-8"))
    FER = BY["ferramentas"]
    DESC_MOD = {m["modelo"]: m["desc"] for m in BY["modelos"]}
    # Frases corrigidas no canvas v24 (portão design-2026-10-24-v5: S1 Opus, PI72 R2); valem enquanto o biblioteca.yaml
    # não tiver as mesmas (o backend troca lá). Quando tiver, este bloco não muda nada.
    # canvas v26 (PORTÃO-DADOS, 25/10): Opus, Fable e Claude Code
    DESC_MOD["claude-opus-5-5"] = "O padrão do dia a dia. A maior parte do trabalho; desde 24 out, o padrão de todos os agentes, portões incluídos."
    DESC_MOD["claude-fable-5-1"] = "O mais capaz da Anthropic, e o mais caro. Usado pelo Atlas (a direção) em parte das sessões."
    for f in FER:
        if f["nome"] == "Cloudflare R2":
            f["desc"] = "Guarda o vídeo e a capa que a Meta baixa para publicar, e o PDF da palavra-chave, com o link que vai no direct."
        if f["nome"] == "Claude Code":
            f["desc"] = "Onde a equipe trabalha: o Atlas (a direção) e os 25 agentes rodam aqui, leem e escrevem os arquivos do projeto e chamam os scripts."
    def dmx(iso):
        return dm(dt.date.fromisoformat(iso[:10]))
    looks = [  # (nome, meta, descrição, imagem, etiqueta, tipo, filtro)
        ("Original da câmera", "V-Log, sem conversão", "Como a S5IIX grava: plano e acinzentado.", "look-original-v-log", "Referência", "ref"),
        ("Só a conversão", "Rec.709 · entrada-camera.cube", "V-Log para Rec.709, ainda sem look.", "look-conversao-rec709", "Base", "ref"),
        ("Look v4", f"korvu-look-v4 · {dmx(L['korvu-look-v4']['criado_em'])}", "O look “Tenet”, frio e contido; nunca aprovado.", "look-v4", "Arquivado", "arq"),  # cor.md: arquivados: [v4] (decisão de 24/10)
        ("Look v5 · WAY", "rosto 23,2 IRE · medido em 18 set", "O escolhido: “a cor da pele ficou muito boa”.", "look-v5", "Em uso" if ativa == "v5" else "Alternativa", "uso" if ativa == "v5" else "alt"),
        ("Look v11", "rosto 40,9 IRE · medido em 18 set", "v5 com a pele recuperada (+1 stop). Aprovado como alternativa.", "look-v11", "Alternativa", "alt"),
    ]
    cards = "".join(f"""<article class="k-card k-look{' is-uso' if t == 'uso' else ''}"><div class="k-look-foto"><img src="img/biblioteca/{img}.jpg" alt="Carlos com {esc(nome)}"><span class="k-etiqueta k-etiqueta--{t}">{et}</span></div>
<div class="k-estilo-corpo"><span class="k-estilo-nome">{esc(nome)}</span><span class="k-estilo-meta">{esc(meta)}</span><span class="k-estilo-desc">{esc(desc).replace("--lut", "<span style=" + chr(34) + "white-space:nowrap" + chr(34) + ">--lut</span>")}</span></div></article>""" for nome, meta, desc, img, et, t in looks)
    n_looks = sum(1 for x in looks if x[5] != "ref")
    sec_looks = f"""<section class="k-acervo-sec" data-de="bib" data-valor="todos looks" aria-labelledby="t-looks"><div class="k-acervo-head"><h2 id="t-looks">looks de cor.</h2><span>a sua imagem com cada look · o mesmo quadro da gravação de 16 set, sem outra correção</span></div>
<div class="k-looks">{cards}</div></section>"""
    sec_capas = """<section class="k-acervo-5" data-de="bib" data-valor="todos capas" aria-labelledby="t-capas"><div class="k-acervo-head"><h2 id="t-capas">capas.</h2><span>2 estilos, sempre com a sua foto</span></div>
<div class="k-card k-capas-estilos">
<div class="k-capa-estilo"><img src="img/biblioteca/capa-demis-hassabis.jpg" alt="Capa do Reel do Demis Hassabis: Quem é o gênio que ganhou o Nobel com IA"><div class="k-estilo-corpo"><span class="k-estilo-nome">Serifa + rabisco</span><span class="k-estilo-desc">A palavra-chave em Playfair itálico, com um rabisco por baixo.</span><span class="k-estilo-meta">usado em 17 set · Demis Hassabis</span></div></div>
<div class="k-capa-estilo"><img src="img/biblioteca/capa-livro-chatgpt.jpg" alt="Capa do Reel do livro: Joga o livro no ChatGPT e escreve isso"><img src="img/biblioteca/capa-livro-chatgpt-l01c.jpg" alt="Capa da variante: Nunca mais leia um livro sem fazer isso"><div class="k-estilo-corpo"><span class="k-estilo-nome">Grotesca + sublinhado</span><span class="k-estilo-desc">Título grotesco, a última palavra sublinhada (cinza ou laranja). Uma capa por variante.</span><span class="k-estilo-meta">em uso desde 23 out</span></div></div>
</div></section>"""
    sec_leg = """<section class="k-acervo-4" data-de="bib" data-valor="todos legendas" aria-labelledby="t-leg"><div class="k-acervo-head"><h2 id="t-leg">legendas.</h2><span>1 estilo</span></div>
<div class="k-card k-legenda-estilo"><img src="img/biblioteca/legenda-texto-selecionado.png" alt="Amostra do estilo Texto Selecionado: a gente joga o livro no ChatGPT, e ele resume tudo"><div class="k-estilo-corpo"><span class="k-estilo-nome">Texto Selecionado</span><span class="k-estilo-desc">As palavras entram no ritmo da fala, com um realce de seleção, a frase de impacto em grotesca pesada e o rabisco na palavra-chave.</span><span class="k-estilo-meta">em todos os Reels</span></div></div></section>"""
    fontes = [("Geist", "fonte-geist", "Títulos e legendas dos Reels; o painel."), ("Bricolage Grotesque", "fonte-bricolage-grotesque", "Cartão do CTA e o PDF da palavra."),
              ("Inter", "fonte-inter", "Texto editorial dos cartões."), ("Playfair Display", "fonte-playfair-display", "A palavra em itálico da capa.")]
    sec_fontes = (f"""<section class="k-acervo-5" data-de="bib" data-valor="todos fontes" aria-labelledby="t-fontes"><div class="k-acervo-head"><h2 id="t-fontes">fontes.</h2><span>{len(fontes)} famílias em uso</span></div>
<div class="k-tipos">""" + "".join(f'<div class="k-card k-tipo"><img src="img/biblioteca/{img}.png" alt="Aa em {nome}"><span class="k-estilo-nome">{nome}</span><span class="k-estilo-desc">{uso}</span></div>' for nome, img, uso in fontes) + "</div></section>")
    NOMES_AN = {"E01": "Ligação de madrugada", "E04": "Máquina que imita a mente", "E06": "2012: reconhecer imagens"}
    an = A["animacoes"]["itens"]
    rows = "".join(f"""<div class="k-anim"><span class="k-anim-i">{ic('play', 16)}</span><div style="display:flex;flex-direction:column;min-width:0"><span class="k-anim-nome">{NOMES_AN.get(x['arquivo'].split('/')[-2], x['titulo'])}</span><span class="k-estilo-meta">metade de cima · {x['duracao_s'].replace('.', ',')[:4].rstrip('0').rstrip(',') if False else dec(float(x['duracao_s'].replace(',', '.')), 1)} s · {NOME.get(x['video'], x['video'])}</span></div><span class="k-etiqueta k-etiqueta--{'uso' if x['renderizada'] else 'alt'}">{'Renderizada' if x['renderizada'] else 'Roteirizada'}</span></div>""" for x in an)
    sec_anim = f"""<section class="k-acervo-4" data-de="bib" data-valor="todos anim" aria-labelledby="t-anim"><div class="k-acervo-head"><h2 id="t-anim">animações.</h2><span>estilos para os próximos vídeos</span></div>
<div class="k-card k-anims">{rows}</div></section>"""
    cards_mod = "".join(f"""<div class="k-card k-sis-modelo"><div class="k-sis-modelo-topo"><span class="k-estilo-nome">{MODELO_ID[m['modelo']]}</span><span class="k-etiqueta k-etiqueta--tipo">Modelo de IA</span></div>
<span class="k-sis-modelo-pct">{dec(m['pct'], 1)} %</span><span class="k-estilo-desc">{esc(DESC_MOD.get(m['modelo'], ''))}</span></div>""" for m in A["sistema"]["modelos"])
    linhas_sis = "".join(f'<div class="k-sis"><span class="k-estilo-nome">{esc(f["nome"])}</span><span><span class="k-etiqueta k-etiqueta--tipo">{esc(f["tipo"])}</span></span><span class="k-estilo-desc">{esc(f["desc"])}</span></div>' for f in FER)
    sec_sis = f"""<section class="k-acervo-sec" data-de="bib" data-valor="sistema" hidden aria-labelledby="t-sis-aba"><div class="k-acervo-head"><h2 id="t-sis-aba">sistema.</h2><span>o que cada peça é e o que faz neste estúdio · para quem chegar pelo GitHub</span></div>
<div class="k-sis-modelos">{cards_mod}</div><div class="k-card k-sis-lista">{linhas_sis}</div></section>"""
    nada = """<div class="k-empty" data-de="bib" data-valor="vazio" hidden><h4>Nada aqui ainda.</h4><p>Quando a equipe criar um estilo novo, ele aparece nesta lista.</p></div>"""
    principal = f"""<div class="k-span-12 k-xl-9" style="min-width:0">{sec_looks}
<div class="k-acervo-par">{sec_capas}{sec_leg}</div>
<div class="k-acervo-par">{sec_fontes}{sec_anim}</div>{sec_sis}{nada}</div>"""
    ar = A["armazenamento"]
    # 25/10 (decisão do Carlos): o HD externo não aparece no painel — foi só a cópia de segurança; fica o que está no Mac
    mac_g, mat_g = ar["gravacao_mac_bytes"], ar["material_bytes"]
    tot = mac_g + mat_g
    partes = [("Gravações da câmera", mac_g, "chart-1"), ("Material e cenas extras", mat_g, "chart-2")]
    barra = "".join(f'<span style="width:{100 * b / tot:.1f}%;background:var(--{cor})"></span>' for _, b, cor in partes)
    leg = "".join(f'<li><i style="background:var(--{cor})"></i><span>{r}</span><span class="k-estilo-meta">{dec(b / 1e9, 1)} GB</span></li>' for r, b, cor in partes)
    aria_ar = ", ".join(f"{r} {dec(b / 1e9, 1)} GB" for r, b, _ in partes)
    S = A["sistema"]
    mods = "".join(f'<li><span>{MODELO_ID[m["modelo"]]}</span><span class="k-estilo-meta"{" style=" + chr(34) + "color:var(--accent-ink);font-weight:600" + chr(34) if i == 0 else " style=" + chr(34) + "color:var(--ink)" + chr(34)}>{dec(m["pct"], 1)} %</span></li>' for i, m in enumerate(S["modelos"]))
    stack = "".join(f'<li><span>{esc(f["nome"])}</span><span class="k-etiqueta k-etiqueta--tipo">{esc(f["tipo"])}</span></li>' for f in FER)
    lado = f"""<div class="k-span-12 k-xl-3 k-lado">
<section class="k-card k-armazem" aria-labelledby="t-arm" style="padding:18px 20px"><div class="k-card-head"><h2 class="k-card-title" id="t-arm">Armazenamento</h2></div>
<div class="k-armazem-n"><b>{dec((mac_g + mat_g) / 1e9, 1)}</b><span>GB no Mac</span></div>
<div class="k-empilhada" role="img" aria-label="{aria_ar}">{barra}</div><ul class="k-armazem-leg">{leg}</ul>
{detalhes(['Onde', 'GB', '% do total'], [[r, dec(b / 1e9, 2), pct(100 * b / tot)] for r, b, _ in partes], 'Armazenamento')}</section>
<section class="k-card k-sistema" aria-labelledby="t-sis" style="padding:18px 20px;display:flex;flex-direction:column"><div class="k-card-head"><h2 class="k-card-title" id="t-sis">Sistema</h2><span class="k-kpi-note">o que faz o estúdio rodar</span></div>
<span class="k-sistema-sub" style="margin-top:10px">Modelos de IA · tokens dos últimos 30 dias</span><ul class="k-kv">{mods}</ul>
<span class="k-sistema-sub">Ferramentas · a aba Sistema explica cada uma</span><ul class="k-kv">{stack}</ul>
<span class="k-sistema-sub" style="padding-top:10px">{S['agentes']} agentes (mais o Atlas) · {S['habilidades']} habilidades · {S['comandos']} comandos</span></section></div>"""
    abas = [("todos", "Tudo", ""), ("looks", "Looks de cor", str(n_looks)), ("capas", "Capas", "2"), ("legendas", "Legendas", "1"), ("fontes", "Fontes", str(len(fontes))), ("anim", "Animações", str(len(an))), ("sistema", "Sistema", str(len(FER)))]
    fb = "".join(f'<button type="button" class="k-filtro" data-grupo="bib" data-valor="{k}" aria-pressed="{"true" if k == "todos" else "false"}">{r}{"<span class=" + chr(34) + "k-filtro-n" + chr(34) + ">" + q + "</span>" if q else ""}</button>' for k, r, q in abas)
    c += f'<div class="k-filtros" role="group" aria-label="Mostrar" style="margin-bottom:18px">{fb}</div>'
    c += f'<section class="k-section" aria-label="Acervo de estilos"><div class="k-grid">{principal}{lado}</div></section>'
    doc = estados([
        ("Looks de cor", "Nenhum look registrado", "Quando houver um look em 00-marca/cor/luts/, ele aparece aqui com a sua foto.", "eye", "cartoes", None),
        ("Capas", "Nenhum estilo de capa", "Quando houver uma capa publicada ou na fila, o estilo dela aparece aqui.", "biblioteca", "cartoes", None),
        ("Legendas", "Nenhum estilo de legenda", "Quando houver uma ficha de legenda em 00-marca/referencias/legendas/, ela aparece aqui.", "biblioteca", "cartoes", None),
        ("Fontes", "Nenhuma fonte registrada", "As famílias usadas nos Reels e no painel aparecem aqui.", "biblioteca", "cartoes", None),
        ("Animações", "Nenhuma animação ainda", "Quando um vídeo tiver o brief de uma animação, ela aparece aqui.", "play", "lista", None),
        ("Armazenamento", "Sem leitura do disco", "Quando o sincronizador somar as gravações e o material, o espaço aparece aqui.", "cpu", "lista", None),
        ("Sistema (cartão da lateral)", "Sem consumo para mostrar", "Quando o Claude Code rodar neste projeto, a fatia de cada modelo aparece aqui.", "cpu", "lista", None),
        ("Aba Sistema · modelos", "Nenhum modelo rodou nos 30 dias", "Quando o Claude Code rodar neste projeto, cada modelo aparece aqui com a fatia dos tokens e o que faz.", "cpu", "cartoes", None),
        ("Aba Sistema · ferramentas", "Nenhuma ferramenta descrita", "As peças do estúdio aparecem aqui quando o painel/biblioteca.yaml listar as ferramentas.", "settings", "lista", None),
    ])
    doc += variacao("Aba Sistema (aberta)", f'<div>{sec_sis.replace(" hidden", "").replace(' data-de="bib" data-valor="sistema"', '').replace("t-sis-aba", "t-sis-doc")}</div>', TAG_REAL)
    doc += variacao("Aba sem nada (por exemplo, Animações vazia)", '<div class="k-empty"><h4>Nada aqui ainda.</h4><p>Quando a equipe criar um estilo novo, ele aparece nesta lista.</p></div>')
    # PI70: uma data de leitura só — o rodapé diz a sincronização de onde vieram os números desta tela (24/10)
    global SYNC_TXT
    antes, so = SYNC_TXT, lon(ar["sincronizado_em"])
    SYNC_TXT = f"{dm(so)}, {so:%H:%M}"
    pagina("biblioteca.html", "biblioteca", "Biblioteca", c, doc)
    SYNC_TXT = antes


def tela_tokens():
    per = f'{ic("calendario", 16)}24 set – 23 out · registros das sessões do Claude Code · leitura de {dm(LEITURA_TOK)}, {LEITURA_TOK:%H:%M} · custo em US$, preço de tabela da API'
    c = head("Tokens e custos", None, f'<span class="k-page-meta">{per}</span>')
    trab = sum(1 for k in AG if AG_TOK.get(k))
    c += f"""<section class="k-section" aria-label="Números do consumo"><div class="k-grid k-grid--tiles">
<div class="k-card k-kpi k-kpi--linha k-span-3"><span class="k-cap">Tokens utilizados</span><div class="k-kpi-linha"><span class="k-kpi-value k-tokens is-grande">{dec(TOK['total_tokens'] / 1e6)}<small>M</small></span><span class="k-kpi-note">+ {dec(TOK['cache_lido'] / 1e9)} bilhão lidos do cache</span></div></div>
<div class="k-card k-kpi k-kpi--linha k-span-3"><span class="k-cap">Custo estimado</span><div class="k-kpi-linha"><span class="k-kpi-value"><small class="k-prefixo">US$</small>{n(round(TOK['total_us']))}</span><span class="k-kpi-note">equivalente na API, preço de tabela</span></div></div>
<div class="k-card k-kpi k-kpi--linha k-span-3"><span class="k-cap">Agentes</span><div class="k-kpi-linha"><span class="k-kpi-value">{len(AG)}</span><span class="k-kpi-note">{trab} trabalharam nos 30 dias</span></div></div>
<div class="k-card k-kpi k-kpi--linha k-span-3"><span class="k-cap">Custo médio por agente</span><div class="k-kpi-linha"><span class="k-kpi-value"><small class="k-prefixo">US$</small>{dec(TOK['total_us'] / trab, 2)}</span><span class="k-kpi-note">entre os {trab} que trabalharam</span></div></div>
</div></section>"""
    dias = TOK["por_dia"]
    ini = dt.date.fromisoformat(dias[0]["dia"])
    rot_tk = [x["tokens"] / 1e6 for x in dias]
    rot_us = [x["us"] for x in dias]
    pico = max(range(len(dias)), key=lambda i: dias[i]["tokens"])
    cfg_tk = curva_cfg([{"nome": "Tokens", "cor": "chart-1", "area": True, "v": rot_tk, "fmt": [compacto(x["tokens"]) for x in dias]}], 9, [0, 3, 6, 9], ["0", "3M", "6M", "9M"],
                       [{"i": pico, "rotulo": f'{dm(ini + dt.timedelta(days=pico))} · {compacto(dias[pico]["tokens"])}'}], inicio=ini, dias=30, ticks=(0, 10, 19, 29))
    pico_us = max(range(len(dias)), key=lambda i: dias[i]["us"])
    cfg_us = curva_cfg([{"nome": "Custo", "cor": "chart-1", "area": True, "v": rot_us, "fmt": [gbp(x["us"]) for x in dias]}], 120, [0, 40, 80, 120], ["0", "US$ 40", "US$ 80", "US$ 120"],
                       [{"i": pico_us, "rotulo": f'{dm(ini + dt.timedelta(days=pico_us))} · {gbp(dias[pico_us]["us"])}'}], inicio=ini, dias=30, ticks=(0, 10, 19, 29))
    fat = tokens_por_modelo()
    T_, U_ = TOK["total_tokens"], TOK["total_us"]
    leg = "".join(f"""<li><span class="k-row" style="gap:8px"><i style="width:8px;height:8px;border-radius:2px;background:var(--{cor});display:inline-block"></i><span class="k-mono">{MODELO_ID[m['modelo']]}</span></span><span class="k-kv-v"><span class="k-mono k-tokens">{round(m['tokens']/T_*100)}% dos tokens</span><br><span class="k-mono">{gbp(m['us'])} · {round(m['us']/U_*100)}% do custo</span></span></li>""" for m, cor in fat)
    fab = next((m for m, _ in fat if m["modelo"] == "claude-fable-5-1"), None)
    c += f"""<section class="k-section"><div class="k-grid">
<section class="k-card k-span-8" aria-labelledby="t-cons" style="padding:20px 24px;display:flex;flex-direction:column">
<div class="k-card-head" style="flex-wrap:wrap"><div class="k-row" style="gap:12px;align-items:baseline"><h2 class="k-h3" id="t-cons">consumo.</h2><span class="k-kpi-note" data-de="medida" data-valor="tk">tokens por dia · {compacto(T_)} em 30 dias</span><span class="k-kpi-note" data-de="medida" data-valor="us" hidden>custo por dia · {gbp(U_, 0)} em 30 dias</span></div>
<div class="k-seg" role="group" aria-label="Medida do gráfico"><button type="button" data-grupo="medida" data-valor="tk" aria-pressed="true">Tokens</button><button type="button" data-grupo="medida" data-valor="us" aria-pressed="false">Custo</button></div></div>
<div style="margin-top:12px" data-de="medida" data-valor="tk"><svg class="k-chart" data-curva="{cfg_tk}" data-altura="200" role="img" aria-label="Tokens por dia nos últimos 30 dias, com pico em {dm(ini + dt.timedelta(days=pico))}"></svg></div>
<div style="margin-top:12px" data-de="medida" data-valor="us" hidden><svg class="k-chart" data-curva="{cfg_us}" data-altura="200" role="img" aria-label="Custo por dia nos últimos 30 dias, com pico em {dm(ini + dt.timedelta(days=pico_us))}"></svg></div>
<p class="k-fonte" style="margin-top:8px">Sessões do Claude Code neste Mac, nesta pasta. Dia em zero = nenhuma sessão registrada. Custo = preço de tabela da API em dólar (Opus 5.5 US$ 4/20 por milhão, Sonnet 5.5 US$ 2/10, Fable 5.1 US$ 10/50); com assinatura, a fatura é outra.</p>
{detalhes(['Dia', 'Tokens', 'Custo (US$)'], [[dm(dt.date.fromisoformat(x['dia'])), n(x['tokens']), dec(x['us'], 2)] for x in dias if x['tokens']], 'Consumo por dia')}</section>
<section class="k-card k-span-4" aria-labelledby="t-mod" style="padding:20px 24px;display:flex;flex-direction:column">
<h2 class="k-h3" id="t-mod">por modelo.</h2>
<div style="display:flex;align-items:center;flex-wrap:wrap;gap:16px 20px;margin-top:16px">{rosca([(m['tokens'], cor) for m, cor in fat], compacto(T_), 'tokens', 140, 18, 'Tokens por modelo: ' + ', '.join(f"{MODELO_ID[m['modelo']]} {round(m['tokens']/T_*100)}%" for m, cor in fat))}
<ul class="k-kv" style="flex:1;min-width:170px">{leg}</ul></div>
<p class="k-fonte" style="margin-top:auto;padding-top:14px;border-top:1px solid var(--line)">O Fable 5.1 é {round(fab['tokens']/T_*100)}% dos tokens e {round(fab['us']/U_*100)}% do custo. ElevenLabs (transcrição e música) fica de fora: ainda sem medição.</p>
{detalhes(['Modelo', 'Tokens', 'Custo (US$)'], [[MODELO_ID[m['modelo']], n(m['tokens']), dec(m['us'], 2)] for m, cor in fat], 'Tokens por modelo')}</section>
</div></section>"""
    NOME_DP = {"direcao": "Direção (Atlas)"}
    dps = TOK["por_departamento"]
    mx = dps[0]["tokens"]
    barras = "".join(f'<div class="k-bar-row k-bar-row--fino k-bar-row--larga"><span>{NOME_DP.get(d["departamento"], NOME_DEPTO[d["departamento"]])}</span><span class="k-bar-track"><span class="k-bar-fill{" is-focus" if i == 0 else ""}" style="width:{d["tokens"]/mx*100:.1f}%"></span></span><span class="k-bar-value k-tokens">{compacto(d["tokens"])}</span><span class="k-bar-value">{gbp(d["us"])}</span><span class="k-bar-value">{pct(d["tokens"]/T_*100)}</span></div>' for i, d in enumerate(dps))
    dir_ = dps[0]
    rot_ = next(d for d in dps if d["departamento"] == "roteiro")
    def linha_q(i, agid):
        t = AG_TOK.get(agid)
        a = AG[agid]
        dep = NOME_DEPTO[a["departamento_id"]] + (" · portão" if a["papel"] == "portao" else "")
        if t:
            mods = " ".join(modelo_chip(MODELO_ID[m]) for m in sorted(t["modelos"], key=lambda m: -t["modelos"][m]))
            vals = [f'<span class="k-n k-tokens">{compacto(t["tokens"])}</span>', f'<span class="k-n">{gbp(t["us"])}</span>', f'<span class="k-n">{t["tarefas"]}</span>', f'<span class="k-n">{gbp(t["us"] / t["tarefas"])}</span>']
        else:
            mods = '<span class="k-muted">—</span>'
            vals = ['<span class="k-muted">—</span>', '<span class="k-muted">—</span>', '<span class="k-muted">—</span>', '<span class="k-sub">não rodou</span>']
        return ("", f'<span class="k-rank-pos{" is-1" if i == 0 else ""}">{i + 1}</span>',
                f'<div class="k-video">{avatar(agid, " style=" + chr(34) + "--s:28px" + chr(34))}<div><span class="k-video-title">{a["nome"]}</span><span class="k-video-meta">{dep}</span></div></div>', mods, *vals)
    gerentes = ["diretor"] + sorted([d["gerente_id"] for d in DEPTOS if d["id"] != "direcao"], key=lambda g: -AG_TOK.get(g, {}).get("tokens", 0))
    geral = sorted(AG_TOK, key=lambda g: -AG_TOK[g]["tokens"])[:7]
    cab = ["#", "Agente", "Rodou em", "Tokens", "Custo", "Tarefas", "Por tarefa"]
    t_ger = tabela(cab, [linha_q(i, g) for i, g in enumerate(gerentes)], "Gerentes por consumo", 600, direita=(3, 4, 5, 6))
    t_ger_n = [AG[g]["nome"].split()[0] for g in gerentes if not AG_TOK.get(g)]
    t_ger += f'<p class="k-fonte" style="margin-top:10px">{", ".join(t_ger_n[:-1]) + " e " + t_ger_n[-1] if len(t_ger_n) > 1 else "".join(t_ger_n)} ainda não rodaram: os portões começaram em 22 out. "Rodou em" é o modelo que aparece nos registros, que pode ser diferente do configurado hoje.</p>'
    t_all = tabela(cab, [linha_q(i, g) for i, g in enumerate(geral)], "Ranking geral por consumo", 600, direita=(3, 4, 5, 6))
    t_all += '<p class="k-fonte" style="margin-top:10px">Tarefa = uma execução do agente. O Atlas soma as sessões e os ajudantes (general-purpose, workflow, Explore).</p>'
    vids = [v for v in TOK["por_video"] if v["slug"] in VIDEOS][:5]
    mv = vids[0]["us"]
    vrows = "".join(f'<div class="k-video" style="gap:10px">{capa(v["slug"], "k-capa--sm") if v["slug"] in CAPA or v["slug"] + "" in CAPA else ""}{"" if v["slug"] in CAPA else "<span class=" + chr(34) + "k-capa k-capa--sm" + chr(34) + " aria-hidden=" + chr(34) + "true" + chr(34) + "></span>"}<div style="flex:1;min-width:0"><span class="k-row" style="justify-content:space-between;gap:8px"><span class="k-video-title" style="font-size:13px">{NOME[v["slug"]]}</span><span class="k-mono" style="font-size:12px">{gbp(v["us"])}</span></span><span class="k-bar-track" style="display:block;height:6px;border-radius:999px;margin-top:4px"><span class="k-bar-fill{" is-focus" if i == 0 else ""}" style="width:{v["us"]/mv*100:.1f}%;border-radius:999px"></span></span></div></div>' for i, v in enumerate(vids))
    media_dia = U_ / len(dias)  # 24/10: projeção pelos últimos 30 dias (não 7); dia sem sessão entra como zero
    proj = media_dia * 30
    c += f"""<section class="k-section"><div class="k-grid">
<section class="k-card k-span-6 k-xl-4" aria-labelledby="t-dep" style="padding:20px 24px;display:flex;flex-direction:column"><div class="k-card-head"><h2 class="k-h3" id="t-dep">por departamento.</h2><span class="k-kpi-note">tokens · custo · %</span></div>
<div class="k-barras" style="margin-top:16px;gap:12px">{barras}</div>
<div class="k-destaque" style="margin-top:20px">{ic('sparkle', 18)}<span class="k-destaque-t">A direção (o Atlas conversando com você e coordenando a equipe) responde por {round(dir_['tokens']/T_*100)}% dos tokens e {round(dir_['us']/U_*100)}% do custo. O roteiro fica com {round(rot_['tokens']/T_*100)}%.</span></div>
{detalhes(['Departamento', 'Tokens', 'Custo (US$)'], [[NOME_DP.get(d['departamento'], NOME_DEPTO[d['departamento']]), n(d['tokens']), dec(d['us'], 2)] for d in dps], 'Consumo por departamento')}</section>
<section class="k-card k-span-12 k-xl-5 k-fim-ate-xl" aria-labelledby="t-quem" style="padding:20px 24px;display:flex;flex-direction:column"><div class="k-card-head" style="flex-wrap:wrap"><h2 class="k-h3" id="t-quem">quem mais consome.</h2>
<div class="k-seg" role="group" aria-label="Quem mostrar"><button type="button" data-grupo="quem" data-valor="ger" aria-pressed="true">Gerentes</button><button type="button" data-grupo="quem" data-valor="todos" aria-pressed="false">Ranking geral</button></div></div>
<div style="margin-top:12px" data-de="quem" data-valor="ger">{t_ger}</div><div style="margin-top:12px" data-de="quem" data-valor="todos" hidden>{t_all}</div></section>
<div class="k-span-6 k-xl-3 k-pilha">
<section class="k-card" aria-labelledby="t-vid" style="padding:20px 24px;display:flex;flex-direction:column;gap:12px"><h2 class="k-h3" id="t-vid">custo por vídeo.</h2>{vrows}
<p class="k-fonte" style="margin-top:auto">Só o trabalho dos agentes especialistas, pelo vídeo citado no pedido. A conversa do Atlas não entra.</p></section>
<section class="k-card k-kpi" aria-labelledby="t-proj" style="padding:20px 24px"><span class="k-cap" id="t-proj">Projeção mensal</span>
<div class="k-row" style="justify-content:space-between;align-items:center"><span class="k-kpi-value"><small class="k-prefixo">US$</small>{n(round(proj))}</span></div>
<span class="k-kpi-note">média dos últimos 30 dias ({usd(media_dia)} por dia, dias sem sessão contam como zero) × 30. É estimativa: a mensalidade já está paga.</span></section></div>
</div></section>"""
    doc = estados([
        ("Números de consumo (KPIs)", "Nenhuma sessão nos últimos 30 dias", "Quando o Claude Code rodar neste projeto, os tokens e o custo equivalente aparecem aqui.", "tokens-custos", "kpi", None),
        ("Consumo por dia", "Nenhum dia com consumo", "Cada dia com sessão do Claude Code vira um ponto; dia sem sessão fica em zero.", "desempenho", "grafico", None),
        ("Por modelo e por departamento", "Sem consumo para dividir", "Quando houver consumo, ele aparece dividido por modelo e por departamento.", "cpu", "grafico", None),
        ("Quem mais consome", "Ninguém rodou ainda", "Quando um agente trabalhar numa sessão, ele entra no ranking com tokens, custo e tarefas.", "users", "tabela", None),
        ("Custo por vídeo", "Nenhum pedido citou um vídeo", "Quando um especialista trabalhar com videos/<slug> no pedido, o custo aparece no vídeo.", "play", "lista", None),
    ])
    doc += variacao("Ranking geral (a 2.ª vista do controle)", f'<div class="k-card k-pad">{t_all}</div>', TAG_REAL)
    pagina("tokens-e-custos.html", "tokens-custos", "Tokens e custos", c, doc)


if __name__ == "__main__":
    tela_visao()
    tela_equipe()
    tela_producao()
    tela_calendario()
    tela_desempenho()
    tela_biblioteca()
    tela_tokens()
    print("ok:", ", ".join(sorted(p.name for p in T.glob("*.html"))))
