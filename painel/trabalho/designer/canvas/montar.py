"""Gera páginas que abrem no Chrome a partir dos .dc.html do Claude Design (só para a designer VER o desenho).
Lê painel/referencias/claude-design/telas-2026-10-23/ (não muda nada lá) e escreve aqui."""
import pathlib, re, sys
RAIZ = pathlib.Path(__file__).resolve().parents[4]
REF = RAIZ / "painel/referencias/claude-design/telas-2026-10-23"
AQUI = pathlib.Path(__file__).resolve().parent
leia = (REF / "LEIA-ME.md").read_text(encoding="utf-8")
mapa = dict(re.findall(r"\|\s*([0-9a-f]{8})\s*\|\s*`([^`]+)`", leia))
# Biblioteca: ids que o LEIA-ME não lista (casados pelo nome do material no renderVals)
mapa.update({"ae21a74d": "biblioteca/b-estilo.jpg", "88920def": "biblioteca/b-50comandos.jpg", "ba8dc420": "biblioteca/b-tela.jpg",
             "428c5d58": "biblioteca/b-feifei.jpg", "9149d496": "biblioteca/b-hinton.jpg", "a3e922b0": "biblioteca/b-demis.jpg",
             "7d58f79a": "biblioteca/b-jacob.jpg"})
for f in sorted(REF.glob("*.dc.html")):
    h = f.read_text(encoding="utf-8")
    h = h.replace('<script src="./support.js"></script>', "")
    h = h.replace('<link rel="stylesheet" href="ds/korvu/components/bundle.css">',
                  '<link rel="stylesheet" href="../../../design/tokens.css"><link rel="stylesheet" href="../../../design/componentes.css">')
    def troca(m):
        i = m.group(1)[:8]
        return "../../../referencias/claude-design/telas-2026-10-23/" + mapa.get(i, "FALTA-" + i)
    h = re.sub(r"/_blob/([0-9a-f]+)", troca, h)
    h = h.replace("</body>", '<script src="dc-runtime.js"></script></body>')
    (AQUI / (f.stem.replace(".dc", "") + ".html")).write_text(h, encoding="utf-8")
    print("ok", f.name)
