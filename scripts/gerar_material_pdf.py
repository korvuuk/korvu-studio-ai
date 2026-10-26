#!/usr/bin/env python3
"""Gera o PDF do material do CTA (o que o direct entrega a quem comenta a palavra) com a marca Korvu.

Decisão do Carlos (13/10): "todo vídeo com palavra-chave tem material, e o material é SEMPRE um link para
um PDF". Quem escreve o conteúdo é o agente `produtor-de-material`; este script só diagrama e imprime.
Motor: Chrome headless (não há reportlab/weasyprint no projeto, e o Chrome já está na máquina).

ENTRADA — Markdown com frontmatter YAML (escolhido em vez de JSON: o agente escreve texto corrido,
e o Carlos consegue ler/editar o arquivo à mão). Fica em `videos/<slug>/material/_fonte/material.md`:

    ---
    titulo: "O prompt mestre do atendimento"   # título grande (Bricolage 800, minúsculas, ponto final; " | " quebra a linha)
    destaque: "prompt mestre"                   # aceito por compatibilidade; desde 21/10 o título sai inteiro no acento
    compacto: true                              # opcional: letra/blocos menores (muitos prompts)
    max_paginas: 6                              # opcional: sobe o teto de páginas (padrão 3) — só para listas longas
    rotulo: "Material do vídeo"                 # opcional: linha pequena acima do título
    palavra: PROMPT                             # a palavra do CTA (mesma do roteiro.json → cta_palavra)
    arquivo: prompt-mestre-atendimento          # nome do PDF, sem .pdf (minúsculas, hífens)
    creditos: "Dados: OpenAI, 2026."            # opcional: linha de crédito/limites no fim do texto
    ---
    Texto de abertura…

    ## Seção
    - item, **negrito**, *itálico*, `código`, [link clicável](https://…)
    1. passo numerado
    > nota/aviso (fio laranja à esquerda)
    ```
    bloco de prompt para copiar (caixa "copie e cole")
    ```
    :::colunas                    ← lista longa em 3 colunas (### grupo + - **/comando** o que faz)
    ### entender
    - **/resumo** resumo em tópicos
    :::
    ---                           ← sozinho na linha: começa página nova
    :::caixa Assista de graça no YouTube
    [youtube.com/watch?v=…](https://www.youtube.com/watch?v=…)
    Toque no link para abrir.
    :::
    ## Fontes            ← título exatamente "Fontes": a seção sai em letra menor, no fim
    - [Veículo, data](https://…)

SAÍDA
  videos/<slug>/material/<arquivo>.pdf      ← o ÚNICO arquivo do material que vai para o pacote/R2
  videos/<slug>/material/_fonte/<arquivo>-previa.png   ← 1.ª página (sips), para conferir olhando
Se o .md não estiver numa pasta `_fonte/`, o PDF sai na mesma pasta do .md (ou em --saida).

Confere no fim: nº de páginas (1–2; mais que isso é erro — decisão de 21/10), links clicáveis no PDF, palavra válida.

Uso:
  uv run python scripts/gerar_material_pdf.py videos/<slug>/material/_fonte/material.md
  uv run python scripts/gerar_material_pdf.py conteudo.md --saida /tmp/x/guia.pdf [--sem-previa] [--html]
"""
from __future__ import annotations

import argparse
import html
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
MAX_PAGINAS = 2   # decisão de 21/10: "as pessoas já não têm paciência para ler"
PALAVRA_RE = re.compile(r"^[A-Z0-9]{2,15}$")
PALAVRAS_PROIBIDAS = {"CORVO", "KORVU", "OI", "SIM", "EU", "TOP"}   # 00-marca/cta.md
ARQUIVO_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# Design system editorial (decisão do Carlos, 21/10): tokens em 00-marca/design-system/korvu-editorial.md — papel,
# tinta e UM acento (laranja da Korvu), título em minúsculas com ponto (Bricolage Grotesque 800), números grandes
# de seção, fios de 0,5 pt, sem carimbo (Carlos, 21/10: "muito poluído"), nada de degradê/sombra/canto/mono. Autoria só "korvu." /
# "@korvu_oficial" — o nome pessoal do Carlos não entra no material (21/10).
PAPEL, PAPEL2, TINTA, TINTA2, ACENTO = "#E7E4D9", "#DCD8CB", "#111111", "#5A5852", "#E85002"
CSS = """
@page { size: A4; margin: 22mm 18mm 22mm; background: __PAPEL__;
  @top-left { content: "korvu."; font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 11pt;
              color: __TINTA__; vertical-align: bottom; padding-bottom: 4mm; }
  @top-right { content: "@korvu_oficial"; font-family: Inter, sans-serif; font-size: 7pt; font-weight: 500;
               color: __TINTA__; vertical-align: bottom; padding-bottom: 5mm; }
  @bottom-left { content: "__RODAPE__"; font-family: Inter, sans-serif; font-size: 7pt; color: __TINTA2__;
                 vertical-align: top; padding-top: 4mm; border-top: 0.5pt solid __TINTA__; }
  @bottom-right { content: counter(page) "/" counter(pages); font-family: Inter, sans-serif; font-size: 7pt;
                  font-weight: 600; color: __TINTA__; vertical-align: top; padding-top: 4mm;
                  border-top: 0.5pt solid __TINTA__; } }
* { box-sizing: border-box; }
html { background: __PAPEL__; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font-family: Inter, -apple-system, sans-serif; color: __TINTA__; font-size: 10.5pt; line-height: 1.5;
       counter-reset: secao; }
.display, h1, h2, .fecho .h { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; letter-spacing: -0.03em;
       text-transform: lowercase; }
.capa { position: relative; padding-top: 6mm; margin-bottom: 9mm; }
.rotulo-topo { font-size: 7.5pt; font-weight: 500; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 5mm; }
h1 { font-size: 54pt; line-height: 0.88; color: __ACENTO__; margin: 0 0 8mm; max-width: 140mm; }
.abertura { border-top: 0.5pt solid __TINTA__; padding-top: 5mm; }
.abertura p { font-size: 12.5pt; line-height: 1.45; max-width: 128mm; }
h2 { font-size: 21pt; line-height: 0.95; margin: 9mm 0 4mm; padding-top: 4mm; border-top: 0.5pt solid __TINTA__;
     break-after: avoid; display: flex; align-items: baseline; gap: 4mm; }
h2::before { counter-increment: secao; content: counter(secao) "."; color: __ACENTO__; font-size: 30pt; line-height: 0.8; }
h3 { font-size: 11pt; font-weight: 600; margin: 5mm 0 1.5mm; break-after: avoid; }
p { margin: 0 0 3.5mm; }
b, strong { font-weight: 600; }
ul, ol { margin: 0 0 4mm; padding: 0; list-style: none; }
li { margin: 0 0 2mm; position: relative; padding-left: 9mm; }
ul > li::before { content: "–"; position: absolute; left: 1mm; color: __TINTA2__; }
ol { counter-reset: item; }
ol > li { counter-increment: item; }
ol > li::before { content: counter(item) "."; position: absolute; left: 0; top: -0.5pt; font-family: 'Bricolage Grotesque', sans-serif;
                  font-weight: 800; font-size: 12pt; color: __ACENTO__; }
a { color: __ACENTO__; text-decoration: underline; text-decoration-thickness: 0.5pt; text-underline-offset: 2pt; }
code { font-family: Inter, sans-serif; font-weight: 600; font-size: 0.95em; background: __PAPEL2__; padding: 0.3pt 3pt; }
pre { background: __PAPEL2__; margin: 0 0 5mm; padding: 4.5mm 6mm 5mm; white-space: pre-wrap; break-inside: avoid;
      font-family: Inter, sans-serif; font-weight: 500; font-size: 11pt; line-height: 1.45; }
pre::before { content: "copie e cole"; display: block; font-size: 7pt; font-weight: 600; letter-spacing: 0.12em;
              text-transform: uppercase; color: __ACENTO__; margin-bottom: 2mm; }
pre code { background: none; padding: 0; font-weight: inherit; font-size: inherit; }
blockquote { border-left: 2pt solid __ACENTO__; margin: 0 0 5mm; padding: 0.5mm 0 0.5mm 5mm; break-inside: avoid; }
blockquote p { margin: 0; }
.caixa { background: __TINTA__; color: __PAPEL__; padding: 7mm 8mm 6mm; margin: 3mm 0 6mm; break-inside: avoid; }
.caixa .rotulo { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 16pt; letter-spacing: -0.02em;
                 text-transform: lowercase; color: __ACENTO__; margin-bottom: 3mm; }
.caixa p { margin: 0 0 2.5mm; font-size: 10pt; color: __PAPEL__; }
.caixa a { color: __PAPEL__; word-break: break-all; }
.caixa code { background: rgba(231,228,217,0.14); color: __PAPEL__; }
.colunas { column-count: 3; column-gap: 7mm; column-rule: 0.5pt solid __TINTA__; margin: 0 0 4mm; }
.colunas h3 { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 12.5pt; letter-spacing: -0.02em;
              text-transform: lowercase; color: __ACENTO__; margin: 0 0 1.5mm; break-after: avoid; }
.colunas h3:not(:first-child) { margin-top: 3.5mm; }
.colunas ul { margin: 0; }
.colunas li { padding-left: 0; margin: 0 0 1.1mm; font-size: 8.4pt; line-height: 1.28; color: __TINTA2__; break-inside: avoid; }
.colunas ul > li::before { content: none; }
.colunas li b { font-weight: 600; font-size: 9pt; color: __TINTA__; margin-right: 1.2mm; }
.quebra { break-after: page; height: 0; }
.fontes { margin-top: 10mm; font-size: 7.5pt; line-height: 1.45; color: __TINTA2__; }
.fontes h2 { font-size: 12pt; margin: 0 0 2mm; }
.fontes h2::before, .sem-numero h2::before { content: none; }
.fontes a { color: __TINTA2__; word-break: break-all; }
.creditos { margin-top: 4mm; font-size: 7.5pt; color: __TINTA2__; line-height: 1.45; }
.fecho { margin-top: 12mm; padding-top: 6mm; border-top: 0.5pt solid __TINTA__; display: flex; align-items: center;
         gap: 6mm; break-inside: avoid; }
.fecho .h { font-size: 40pt; line-height: 0.9; color: __ACENTO__; }
.fecho .assina { font-size: 8pt; line-height: 1.4; }
""".replace("__PAPEL2__", PAPEL2).replace("__PAPEL__", PAPEL).replace("__TINTA2__", TINTA2) \
   .replace("__TINTA__", TINTA).replace("__ACENTO__", ACENTO)

FONTES_GOOGLE = ('<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800'
                 '&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">')


def inline(t: str) -> str:
    """Marcação de linha → HTML. Escapa primeiro; os links só aceitam http(s)."""
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\*\w])\*(?!\*)(.+?)\*(?!\w)", r"<i>\1</i>", t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", lambda m: f'<a href="{m.group(2).replace(chr(34), "%22")}">{m.group(1)}</a>', t)
    return t


def md_para_html(md: str) -> str:
    out: list[str] = []
    lista: str | None = None
    para: list[str] = []
    bloco: list[str] = []          # linhas dentro de ``` ou :::caixa
    modo: str | None = None        # None | "code" | "caixa" | "colunas"
    rotulo_caixa = ""
    em_fontes = False
    n_ol = 0                       # itens da última lista numerada: um ``` no meio dos passos não zera a contagem
    continua_ol = False

    def fechar_para():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    def fechar_lista():
        nonlocal lista
        if lista:
            out.append(f"</{lista}>")
            lista = None

    for linha in md.splitlines():
        s = linha.strip()
        if modo == "code":
            if s.startswith("```"):
                out.append("<pre><code>" + html.escape("\n".join(bloco), quote=False) + "</code></pre>")
                bloco.clear(); modo = None; continua_ol = n_ol > 0
            else:
                bloco.append(linha)
            continue
        if modo == "colunas":
            if s == ":::":
                out.append(f'<div class="colunas">{md_para_html(chr(10).join(bloco))}</div>')
                bloco.clear(); modo = None
            else:
                bloco.append(linha)
            continue
        if modo == "caixa":
            if s == ":::":
                ps = "".join(f"<p>{inline(x)}</p>" for x in bloco if x.strip())
                out.append(f'<div class="caixa"><div class="rotulo">{inline(rotulo_caixa)}</div>{ps}</div>')
                bloco.clear(); modo = None
            else:
                bloco.append(s)
            continue
        if s.startswith("```"):
            fechar_para(); fechar_lista(); modo = "code"; continue
        if s and not re.match(r"^\d+[.)]\s", s):
            continua_ol = False
        if s == ":::colunas":
            fechar_para(); fechar_lista(); modo = "colunas"; continue
        if s == "---":
            fechar_para(); fechar_lista(); out.append('<div class="quebra"></div>'); continue
        if m := re.match(r"^:::\s*caixa\s*(.*)$", s):
            fechar_para(); fechar_lista(); modo = "caixa"; rotulo_caixa = m.group(1).strip(); continue
        if not s:
            fechar_para(); fechar_lista(); continue
        if m := re.match(r"^(#{2,3})\s+(.*)", s):
            fechar_para(); fechar_lista()
            n, txt = len(m.group(1)), m.group(2).strip()
            if n == 2 and txt.lower() == "fontes" and not em_fontes:
                out.append('<div class="fontes">'); em_fontes = True
            out.append(f"<h{n}>{inline(txt)}</h{n}>")
        elif m := re.match(r"^[-*]\s+(.*)", s):
            fechar_para()
            if lista != "ul":
                fechar_lista(); out.append("<ul>"); lista = "ul"
            out.append(f"<li>{inline(m.group(1))}</li>")
        elif m := re.match(r"^\d+[.)]\s+(.*)", s):
            fechar_para()
            if lista != "ol":
                fechar_lista()
                if not continua_ol:
                    n_ol = 0
                out.append(f'<ol style="counter-reset: item {n_ol}">'); lista = "ol"
            n_ol += 1
            out.append(f"<li>{inline(m.group(1))}</li>")
        elif s.startswith(">"):
            fechar_para(); fechar_lista()
            out.append(f"<blockquote><p>{inline(s.lstrip('> ').strip())}</p></blockquote>")
        else:
            fechar_lista(); para.append(s)
    if modo:
        raise ValueError(f"bloco {'```' if modo == 'code' else ':::' + modo} aberto e não fechado")
    fechar_para(); fechar_lista()
    if em_fontes:
        out.append("</div>")
    return "\n".join(out)


def ler_conteudo(src: Path) -> tuple[dict, str]:
    txt = src.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", txt, re.S)
    if not m:
        raise ValueError("o conteúdo precisa começar com o frontmatter YAML (--- titulo/palavra/arquivo ---)")
    fm = yaml.safe_load(m.group(1)) or {}
    return fm, m.group(2)


def validar(fm: dict, corpo: str) -> tuple[list[str], list[str]]:
    erros, avisos = [], []
    for campo in ("titulo", "palavra", "arquivo"):
        if not str(fm.get(campo) or "").strip():
            erros.append(f"frontmatter sem '{campo}'")
    palavra = str(fm.get("palavra") or "")
    if palavra and not PALAVRA_RE.fullmatch(palavra):
        erros.append(f"palavra '{palavra}' inválida: uma palavra só, MAIÚSCULAS, sem acento (00-marca/cta.md)")
    elif palavra in PALAVRAS_PROIBIDAS:
        erros.append(f"palavra '{palavra}' é proibida em 00-marca/cta.md")
    arquivo = str(fm.get("arquivo") or "")
    if arquivo and not ARQUIVO_RE.fullmatch(arquivo):
        erros.append(f"arquivo '{arquivo}' inválido: minúsculas, números e hífens, sem .pdf")
    if re.search(r"\]\((?!https?://)[^)]*\)", corpo):
        erros.append("há link que não começa com http(s):// — no celular não abre")
    if not re.search(r"^##\s+Fontes\s*$", corpo, re.M | re.I):
        avisos.append("sem seção '## Fontes' — todo fato do material precisa de fonte (regras-legais §3–4)")
    return erros, avisos


def titulo_html(fm: dict) -> str:
    # O título sai inteiro no acento (o `destaque` antigo não pinta mais nada — molde de 21/10) e termina em ponto.
    t = str(fm["titulo"]).strip()
    if not re.search(r"[.!?…]$", t):
        t += "."
    return html.escape(t, quote=False).replace(" | ", "<br>")


def montar_html(fm: dict, corpo_md: str) -> str:
    palavra = fm["palavra"]
    rotulo = f'<div class="rotulo-topo">{inline(str(fm["rotulo"]))}</div>' if fm.get("rotulo") else ""
    creditos = f'<p class="creditos">{inline(str(fm["creditos"]))}</p>' if fm.get("creditos") else ""
    # O rodapé vai na margem de TODAS as páginas (@page @bottom-*): só aceita texto puro, sem tags.
    rodape = f"material gratuito da korvu · palavra {palavra} · informação para aprender, não promessa de resultado"
    if fm.get("compacto"):  # opcional: muitos blocos de prompt (ex.: lista de 50 comandos)
        css_extra = ("body{font-size:9.8pt;line-height:1.42}h1{font-size:46pt}h2{margin:7mm 0 3mm}"
                     "pre{padding:3mm 5mm;margin:0 0 3mm;font-size:10pt;line-height:1.38}"
                     "pre::before{margin-bottom:1.2mm}p{margin:0 0 2.2mm}p:has(+ pre){break-after:avoid}"
                     "li{margin:0 0 1.4mm}blockquote{margin:0 0 3mm}")
    else:
        css_extra = ""
    css = (CSS + css_extra).replace("__RODAPE__", rodape.replace("\\", "").replace('"', "'"))
    # Abertura = parágrafos antes do primeiro "## ": ficam na capa, em letra maior, abaixo do fio.
    m = re.search(r"^##\s", corpo_md, re.M)
    abertura, resto = (corpo_md[:m.start()], corpo_md[m.start():]) if m else ("", corpo_md)
    abertura_html = f'<div class="abertura">{md_para_html(abertura)}</div>' if abertura.strip() else ""
    # "1." grande só faz sentido com 2+ seções; com uma só (ex.: "como usar") o número confunde com os passos.
    secoes = [t for t in re.findall(r"^##\s+(.+)$", resto, re.M) if t.strip().lower() != "fontes"]
    classe_body = "" if len(secoes) >= 2 else ' class="sem-numero"'
    fecho = (f'<div class="fecho"><div class="h">valeu.</div>'
             f'<div class="assina">material da korvu<br>@korvu_oficial</div>'
             '</div>')
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>{html.escape(str(fm['titulo']))}</title>
{FONTES_GOOGLE}<style>{css}</style></head>
<body{classe_body}>
  <div class="capa">
    {rotulo}<h1>{titulo_html(fm)}</h1>{abertura_html}</div>
  {md_para_html(resto)}
  {creditos}
  {fecho}
</body></html>"""


def contar_paginas(pdf: bytes) -> int:
    return len(re.findall(rb"/Type\s*/Page(?![s\w])", pdf))


def imprimir(html_doc: str, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        pagina = Path(tmp) / "material.html"
        pagina.write_text(html_doc, encoding="utf-8")
        tmp_pdf = Path(tmp) / "saida.pdf"
        # --virtual-time-budget dá tempo às fontes do Google; sem ele o Chrome imprime com a fonte de sistema.
        r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                            "--run-all-compositor-stages-before-draw", "--virtual-time-budget=6000",
                            f"--print-to-pdf={tmp_pdf}", pagina.as_uri()],
                           capture_output=True, text=True, timeout=120)
        if r.returncode != 0 or not tmp_pdf.exists() or tmp_pdf.stat().st_size < 1000:
            raise RuntimeError(f"Chrome não gerou o PDF (rc {r.returncode}): {r.stderr[-500:]}")
        dst.write_bytes(tmp_pdf.read_bytes())


def previa_png(pdf: Path, png: Path) -> None:
    # sips rasteriza só a 1.ª página; -Z 1400 deixa legível para conferir sem pesar.
    r = subprocess.run(["sips", "-s", "format", "png", "-Z", "1400", str(pdf), "--out", str(png)],
                       capture_output=True, text=True)
    if r.returncode != 0 or not png.exists():
        raise RuntimeError(f"sips falhou ao gerar a prévia: {r.stderr[-300:]}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Conteúdo (Markdown + frontmatter) → PDF do material, design editorial da Korvu.")
    ap.add_argument("conteudo", type=Path)
    ap.add_argument("--saida", type=Path, help="caminho do PDF (padrão: material/<arquivo>.pdf, ver docstring)")
    ap.add_argument("--sem-previa", action="store_true", help="não gera o PNG da 1.ª página")
    ap.add_argument("--html", action="store_true", help="guarda também o HTML ao lado do conteúdo (depuração)")
    a = ap.parse_args()

    src = a.conteudo.resolve()
    try:
        fm, corpo = ler_conteudo(src)
    except (OSError, ValueError, yaml.YAMLError) as e:
        print(f"ERRO: {e}")
        return 1
    erros, avisos = validar(fm, corpo)
    for av in avisos:
        print(f"AVISO: {av}")
    if erros:
        for e in erros:
            print(f"ERRO: {e}")
        return 1

    pasta_pdf = src.parent.parent if src.parent.name == "_fonte" else src.parent
    dst = (a.saida.resolve() if a.saida else pasta_pdf / f"{fm['arquivo']}.pdf")
    try:
        doc = montar_html(fm, corpo)
    except ValueError as e:
        print(f"ERRO: {e}")
        return 1
    if a.html:
        (src.parent / f"{fm['arquivo']}.html").write_text(doc, encoding="utf-8")
    try:
        imprimir(doc, dst)
    except (RuntimeError, subprocess.TimeoutExpired) as e:
        print(f"ERRO: {e}")
        return 1

    dados = dst.read_bytes()
    paginas, links = contar_paginas(dados), len(re.findall(rb"/URI\s*\(", dados))
    print(f"PDF: {dst}  ({paginas} página(s), {links} link(s), {len(dados) / 1024:.0f} KB)")
    rc = 0
    limite = int(fm.get("max_paginas") or MAX_PAGINAS)  # opcional no frontmatter (ex.: lista de 50 comandos = 6)
    if paginas > limite:
        print(f"ERRO: {paginas} páginas — o material tem de caber em 1–{limite}. Corte texto e gere de novo.")
        rc = 1
    if "](http" in corpo and links == 0:
        print("ERRO: o conteúdo tem links mas o PDF saiu sem nenhum link clicável")
        rc = 1
    if not a.sem_previa:
        png = src.parent / f"{fm['arquivo']}-previa.png"
        try:
            previa_png(dst, png)
            print(f"Prévia: {png}  ← abra e confira a 1.ª página antes de seguir")
        except RuntimeError as e:
            print(f"AVISO: {e}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
