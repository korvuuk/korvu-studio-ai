"""Confere que painel/design/ é FIEL ao artefato do Claude Design (Carlos, 23/10/2026) — nada arredondado, nada trocado.

  1. tokens.json  = tokens.json da fonte (cor com alias resolvido, tipografia, espaço, raio, sombra, layout)
  2. tokens.css   = tokens.json (cada variável com o mesmo valor; alias como var(--accent))
  3. componentes.css = components/bundle.css, regra por regra (só os comentários mudam, mais as regras aprovadas)
  4. korvu.js     = components/bundle.js, linha de código por linha de código (só os comentários mudam)
  5. icones/*.svg = os 31 caminhos de window.Korvu.icons, traço 1.5, currentColor
  6. fontes, logotipos e os 7 ícones da navegação = byte a byte iguais à fonte
  7. toda var(--…) usada em componentes.css / acrescimos.css existe em tokens.css
  8. nenhuma cor solta (#hex / rgba) em componentes.css e acrescimos.css; nenhum lixo (.DS_Store, ~, .tmp) na pasta

Divergências APROVADAS pelo Carlos (a checagem continua ligada: o valor tem de ser exatamente o aprovado, e a fonte
continua intocada em painel/referencias/claude-design/korvu-painel-2026-10-23/):
  - line-strong #928874 (fonte #a8a090);
  - focus = {accent-ink} (fonte: {accent});
  - token novo focus-on-dark = {accent}, com a regra `.k-sidebar :focus-visible{outline-color:var(--focus-on-dark)}`
    logo abaixo de `:focus-visible` no componentes.css.
  Os nomes são os da versão 6 do artefato do Claude Design. docs/decisoes.md §5, 23/10: "Aceito as duas: borda dos
  campos em #928874 e anel de foco em laranja escuro (accent-ink) nos fundos claros."

Rodar:  uv run python -I painel/design/verificacao/fidelidade.py      (sai com código 1 se algo divergir)
"""
import hashlib
import json
import pathlib
import re
import sys

D = pathlib.Path(__file__).resolve().parents[1]
F = D.parent / "referencias/claude-design/korvu-painel-2026-10-23"
erros = []


def falha(msg):
    erros.append(msg)


def sem_comentarios_css(t):
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    return [x.strip() for x in t.split("\n") if x.strip()]


# Divergências aprovadas (ver o cabeçalho). Valor = o que tokens.json TEM de ter; "{x}" = alias de x.
APROVADAS = {
    "line-strong": ("#928874", "decisão do Carlos, 23/10 (docs/decisoes.md §5)"),
    "focus": ("{accent-ink}", "decisão do Carlos, 23/10 (docs/decisoes.md §5)"),
}
ACRESCIMOS_APROVADOS = {"focus-on-dark": ("{accent}", "decisão do Carlos, 23/10 — anel nos fundos escuros (versão 6 do artefato)")}
# Regras de CSS a mais no componentes.css: (regra que vem logo antes, regra nova). Só estas, só neste lugar.
REGRAS_APROVADAS = [(":focus-visible{outline:2px solid var(--focus);outline-offset:2px}",
                     ".k-sidebar :focus-visible{outline-color:var(--focus-on-dark)}")]

# 1. tokens.json
fonte = json.loads((F / "tokens.json").read_text(encoding="utf-8"))
meu = json.loads((D / "tokens.json").read_text(encoding="utf-8"))
cores = {t["name"]: t["value"] for t in fonte["color"]["tokens"]}
for nome, v in list(cores.items()) + [(k, a[0]) for k, a in ACRESCIMOS_APROVADOS.items()]:
    if nome in APROVADAS:
        v = APROVADAS[nome][0]
    esperado = cores[v[1:-1]] if v.startswith("{") else v
    obtido = meu["cor"].get(nome, {}).get("valor")
    if obtido != esperado:
        falha(f"cor {nome}: fonte {esperado} × tokens.json {obtido}")
if set(meu["cor"]) != set(cores) | set(ACRESCIMOS_APROVADOS):
    falha(f"cores a mais/a menos: {set(meu['cor']) ^ (set(cores) | set(ACRESCIMOS_APROVADOS))}")
for nome, (v, motivo) in list(APROVADAS.items()) + list(ACRESCIMOS_APROVADOS.items()):
    if v.startswith("{") and meu["cor"].get(nome, {}).get("alias") != v[1:-1]:
        falha(f"cor {nome}: a decisão aprovada é alias de {v[1:-1]} ({motivo})")
for g in fonte["type"]["groups"]:
    for s in g["styles"]:
        m = meu["tipografia"].get(s["name"], {})
        for k in ("fontSize", "lineHeight", "fontWeight"):
            if m.get(k) != s[k]:
                falha(f"tipografia {s['name']}.{k}: fonte {s[k]} × {m.get(k)}")
        if m.get("letterSpacing") != s.get("letterSpacing", "normal"):
            falha(f"tipografia {s['name']}.letterSpacing: fonte {s.get('letterSpacing')} × {m.get('letterSpacing')}")
for fam in ("sans", "mono"):
    if meu["fonte"]["familias"][fam]["valor"] != fonte["type"]["families"][fam]:
        falha(f"família {fam} diferente")
for chave_f, chave_m in (("spacing", "espaco"), ("radius", "raio"), ("shadow", "sombra"), ("layout", "layout")):
    for t in fonte[chave_f]["tokens"]:
        if meu[chave_m].get(t["name"], {}).get("valor") != t["value"]:
            falha(f"{chave_m} {t['name']}: fonte {t['value']} × {meu[chave_m].get(t['name'], {}).get('valor')}")

# 2. tokens.css
css = (D / "tokens.css").read_text(encoding="utf-8")
raiz = re.search(r":root\s*\{(.*?)\n\}", css, flags=re.S).group(1)
decl = dict(re.findall(r"(--[\w-]+):\s*([^;]+);", raiz))
for grupo in ("cor", "espaco", "raio", "sombra", "layout"):
    for nome, t in meu[grupo].items():
        if not isinstance(t, dict):
            continue
        esperado = f"var(--{t['alias']})" if t.get("alias") else t["valor"]
        if decl.get(f"--{nome}") != esperado:
            falha(f"tokens.css --{nome}: {decl.get('--' + nome)} × {esperado}")
for fam, t in meu["fonte"]["familias"].items():
    if decl.get(t["css"]) != t["valor"]:
        falha(f"tokens.css {t['css']} diferente")

# 3. componentes.css = bundle.css + só as regras aprovadas, cada uma logo depois da regra indicada
esperado_css = sem_comentarios_css((F / "components/bundle.css").read_text(encoding="utf-8"))
for antes, nova in REGRAS_APROVADAS:
    if esperado_css.count(antes) != 1:
        falha(f"componentes.css: a regra de referência '{antes}' não está (uma vez) no bundle.css")
        continue
    esperado_css.insert(esperado_css.index(antes) + 1, nova)
if esperado_css != sem_comentarios_css((D / "componentes.css").read_text(encoding="utf-8")):
    falha("componentes.css: as regras não são as mesmas do bundle.css (mais as aprovadas, no lugar aprovado)")

# 4. korvu.js
orig = (F / "components/bundle.js").read_text(encoding="utf-8").split("\n")[1:]
novo = [l for l in (D / "korvu.js").read_text(encoding="utf-8").split("\n") if not l.startswith("//")]
i = next((k for k, l in enumerate(novo) if l.startswith("(function(){")), None)
if i is None or novo[i:] != orig:
    falha("korvu.js: o código não é o mesmo do bundle.js")

# 5. ícones
m = re.search(r"var I=(\{.*?\});", (F / "components/bundle.js").read_text(encoding="utf-8"))
icones = json.loads(m.group(1))
svgs = sorted(p for p in (D / "icones").glob("*.svg"))
if len(svgs) != len(icones) or len(icones) != 31:
    falha(f"ícones: {len(svgs)} arquivos para {len(icones)} na fonte")
for p in svgs:
    t = p.read_text(encoding="utf-8")
    corpo = re.search(r"<svg[^>]*>(.*)</svg>", t, flags=re.S).group(1)
    if corpo != icones.get(p.stem):
        falha(f"ícone {p.stem}: caminho diferente da fonte")
    if 'stroke="currentColor"' not in t or 'stroke-width="1.5"' not in t:
        falha(f"ícone {p.stem}: sem currentColor ou traço 1.5")
js = json.loads((D / "icones/icones.json").read_text(encoding="utf-8"))
if js["icones"] != icones:
    falha("icones.json diferente da fonte")


# 6. arquivos copiados
def h(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


pares = [(F / "fonts/Geist-Variable.woff2", D / "fontes/Geist-Variable.woff2"),
         (F / "fonts/GeistMono-Variable.woff2", D / "fontes/GeistMono-Variable.woff2"),
         (F / "assets/Logos/korvu-painel-ink.svg", D / "marca/korvu-painel-ink.svg"),
         (F / "assets/Logos/korvu-painel-ivory.svg", D / "marca/korvu-painel-ivory.svg")]
pares += [(p, D / "icones/navegacao" / p.name) for p in (F / "assets/Icons").glob("*.svg")]
for a, b in pares:
    if not b.exists() or h(a) != h(b):
        falha(f"cópia diferente: {b.relative_to(D)}")

# 7. variáveis usadas existem
locais = {"--s", "--table-min", "--seta-x"}
definidas = set(re.findall(r"(--[\w-]+):", css))
for arq in ("componentes.css", "acrescimos.css"):
    usadas = set(re.findall(r"var\((--[\w-]+)", (D / arq).read_text(encoding="utf-8")))
    for v in sorted(usadas - definidas - locais):
        falha(f"{arq} usa {v}, que não existe em tokens.css")

# 8. cor solta e lixo
for arq in ("componentes.css", "acrescimos.css"):
    t = "\n".join(sem_comentarios_css((D / arq).read_text(encoding="utf-8")))
    soltas = re.findall(r"#[0-9a-fA-F]{3,8}\b|rgba?\(", t)
    if soltas:
        falha(f"{arq}: cor solta {soltas[:5]}")
lixo = [p for p in D.rglob("*") if p.name == ".DS_Store" or p.name.endswith(("~", ".tmp", ".bak", ".orig"))
        or p.name.startswith("._") or p.name == "__pycache__"]
for p in lixo:
    falha(f"lixo na pasta: {p.relative_to(D)}")

if erros:
    print("✗ divergências:")
    for e in erros:
        print("  -", e)
    sys.exit(1)
print(f"✓ fiel à fonte (com {len(APROVADAS) + len(ACRESCIMOS_APROVADOS)} divergências aprovadas pelo Carlos em 23/10: "
      f"{', '.join(list(APROVADAS) + list(ACRESCIMOS_APROVADOS))}, e {len(REGRAS_APROVADAS)} regra de CSS a mais no lugar aprovado): {len(cores)} cores, {sum(len(g['styles']) for g in fonte['type']['groups'])} estilos de texto, "
      f"{len(fonte['spacing']['tokens'])} espaços, {len(fonte['radius']['tokens'])} raios, {len(fonte['shadow']['tokens'])} sombras, "
      f"{len(fonte['layout']['tokens'])} medidas de layout; componentes.css = bundle.css + a regra aprovada; korvu.js = bundle.js; "
      f"{len(icones)} ícones; {len(pares)} arquivos copiados byte a byte; nenhuma variável faltando; nenhum lixo.")
