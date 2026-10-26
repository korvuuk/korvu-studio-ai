"""Converte o material do CTA (Markdown) em PDF com a identidade Korvu, via Chrome headless.

Uso: uv run python scripts/md_para_pdf.py videos/<slug>/material/guia.md [saida.pdf]
Padrão de saída: mesmo nome com .pdf. Suporta: # títulos, parágrafos, listas (- / 1.),
**negrito**, *itálico*, `código`, blocos ``` (ideal para prompts), > citação, links [x](url).
"""
from __future__ import annotations

import html
import re
import subprocess
import sys
import tempfile
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;600;800&display=swap');
@page { size: A4; margin: 18mm 16mm; }
body { font-family: 'Geist', 'Inter', -apple-system, sans-serif; color: #151515; font-size: 11.5pt; line-height: 1.55; }
header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #111; padding-bottom: 8px; margin-bottom: 18px; font-size: 9pt; color: #555; }
header b { color: #111; letter-spacing: .04em; }
h1 { font-size: 26pt; font-weight: 800; line-height: 1.05; letter-spacing: -0.02em; margin: 6px 0 14px; }
h1 .risco { box-shadow: inset 0 -0.28em 0 #FF7A35; }
h2 { font-size: 15pt; font-weight: 800; margin: 20px 0 6px; }
h3 { font-size: 12pt; font-weight: 600; margin: 14px 0 4px; }
pre { background: #111; color: #F2F2F2; padding: 14px 16px; border-radius: 8px; white-space: pre-wrap; font-size: 10pt; line-height: 1.5; }
code { font-family: 'SF Mono', Menlo, monospace; background: #f1f1f1; padding: 1px 4px; border-radius: 3px; }
pre code { background: none; padding: 0; }
blockquote { border-left: 4px solid #FF7A35; margin: 10px 0; padding: 4px 12px; color: #333; background: #fff7f2; }
li { margin: 3px 0; }
a { color: #c24f14; }
footer { margin-top: 26px; border-top: 1px solid #ddd; padding-top: 8px; font-size: 8.5pt; color: #777; }
"""


def inline(t: str) -> str:
    t = html.escape(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*", r"<i>\1</i>", t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', t)
    return t


def md_para_html(md: str) -> str:
    out, lista, para, em_code, code = [], None, [], False, []

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
        if linha.strip().startswith("```"):
            if em_code:
                out.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>")
                code.clear()
                em_code = False
            else:
                fechar_para(); fechar_lista(); em_code = True
            continue
        if em_code:
            code.append(linha)
            continue
        s = linha.strip()
        if not s:
            fechar_para(); fechar_lista(); continue
        if m := re.match(r"^(#{1,3})\s+(.*)", s):
            fechar_para(); fechar_lista()
            n = len(m.group(1))
            txt = inline(m.group(2))
            if n == 1:
                palavras = txt.rsplit(" ", 1)
                txt = palavras[0] + (f' <span class="risco">{palavras[1]}</span>' if len(palavras) > 1 else "")
            out.append(f"<h{n}>{txt}</h{n}>")
        elif m := re.match(r"^[-*]\s+(.*)", s):
            fechar_para()
            if lista != "ul":
                fechar_lista(); out.append("<ul>"); lista = "ul"
            out.append(f"<li>{inline(m.group(1))}</li>")
        elif m := re.match(r"^\d+[.)]\s+(.*)", s):
            fechar_para()
            if lista != "ol":
                fechar_lista(); out.append("<ol>"); lista = "ol"
            out.append(f"<li>{inline(m.group(1))}</li>")
        elif s.startswith(">"):
            fechar_para(); fechar_lista()
            out.append(f"<blockquote>{inline(s.lstrip('> '))}</blockquote>")
        else:
            fechar_lista(); para.append(s)
    fechar_para(); fechar_lista()
    return "\n".join(out)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    src = Path(sys.argv[1]).resolve()
    dst = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else src.with_suffix(".pdf")
    corpo = md_para_html(src.read_text(encoding="utf-8"))
    doc = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS}</style></head>
<body><header><b>KORVU</b><span>@korvu_oficial</span></header>{corpo}
<footer>Material gratuito da Korvu · korvu.uk · Instagram @korvu_oficial</footer></body></html>"""
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "guia.html"
        page.write_text(doc, encoding="utf-8")
        r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                            f"--print-to-pdf={dst}", "--virtual-time-budget=4000", page.as_uri()],
                           capture_output=True, text=True)
    if r.returncode != 0 or not dst.exists():
        print(f"ERRO ao gerar PDF: {r.stderr[-500:]}")
        return 1
    print(f"PDF: {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
