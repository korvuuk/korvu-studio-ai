"""Faz as miniaturas dos materiais da Biblioteca a partir do próprio arquivo de cada um (só lê a origem).

Lê painel/design/dados-2026-10-23.json → telas_biblioteca (recentes + seguintes, campo miniatura_de) e grava
painel/design/telas/img/biblioteca/<id>.jpg (480 px de largura, JPEG 80). Imagem: redimensiona; vídeo: um quadro aos 2 s
(ffmpeg em /Users/teste/bin/ffmpeg). Apaga as miniaturas que nenhum material usa.
Rodar:  uv run --with pillow python -I painel/trabalho/designer/miniaturas_biblioteca.py
"""
import json
import pathlib
import subprocess
import tempfile

from PIL import Image

RAIZ = pathlib.Path(__file__).resolve().parents[3]
DADOS = json.loads((RAIZ / "painel/design/dados-2026-10-23.json").read_text(encoding="utf-8"))
SAIDA = RAIZ / "painel/design/telas/img/biblioteca"
FFMPEG = "/Users/teste/bin/ffmpeg"

bib = DADOS["blocos"]["telas_biblioteca"]["linhas"][0]
usados = set()
for m in bib["recentes"] + bib["seguintes"]:
    if not m.get("miniatura_de"):
        continue
    origem = RAIZ / m["miniatura_de"]
    destino = SAIDA / f"{m['id']}.jpg"
    usados.add(destino.name)
    if origem.suffix.lower() in (".mp4", ".mov"):
        with tempfile.TemporaryDirectory() as tmp:
            quadro = pathlib.Path(tmp) / "q.png"
            subprocess.run([FFMPEG, "-v", "error", "-ss", "2", "-i", str(origem), "-frames:v", "1", str(quadro)], check=True)
            im = Image.open(quadro)
            im.load()
    else:
        im = Image.open(origem)
    im = im.convert("RGB")
    im.thumbnail((480, 480 * 3))
    im.save(destino, "JPEG", quality=80, optimize=True)
    print("ok", destino.name, im.size, "←", m["miniatura_de"])
for f in SAIDA.glob("*.jpg"):
    if f.name not in usados:
        f.unlink()
        print("apagada (sem uso):", f.name)
