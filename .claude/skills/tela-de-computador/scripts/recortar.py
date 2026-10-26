"""Recorta uma gravação de tela de computador em CENAS EXTRAS prontas para brutos/extras/ (docs/contratos.md §0).

uso: uv run python .claude/skills/tela-de-computador/scripts/recortar.py <tela.json> [--so E02,E04] [--previa]

tela.json (escrito pelo editor depois do momentos.py):
{
  "video": "material/screnn record/Screen Recording ….mov",     # relativo à pasta do vídeo (ou absoluto)
  "pasta_video": "videos/2026-10-23-livro-chatgpt",             # opcional; padrão = pasta do tela.json
  "recorte_padrao": {"x": 0, "y": 1017, "w": 1716, "h": 965},   # região 16:9 (caixa de digitação + o que está logo acima)
  "largura_saida": 1080,
  "cenas": [
    {"id": "E02", "nome": "tela-mindmap", "trechos": [
        {"inicio": 8.0,  "fim": 12.0, "velocidade": 2.0},        # anexar a capa (acelerado 2×)
        {"inicio": 26.0, "fim": 29.5, "velocidade": 1.0},        # digitar /mindmap e enviar (tempo real)
        {"inicio": 30.0, "fim": 31.0, "velocidade": 1.0}         # 1 s do "gerando…"
      ],
     "recorte": {"x": 0, "y": 1017, "w": 1716, "h": 965}         # opcional; senão recorte_padrao
    }
  ]
}

Regras:
- a saída é DEITADA (16:9) de propósito: o pipeline põe mídia deitada na metade de cima (`split`) e o Carlos
  embaixo — exatamente o layout da referência (caixa do chat em cima, rosto embaixo). O RESULTADO não sai daqui:
  é o PNG que o Carlos baixa do ChatGPT (imagem em pé → `full`; deitada → `split`, ou `full` + `enquadrar` zoom).
- cada trecho é cortado do original, acelerado por `velocidade` (setpts), e os trechos da mesma cena são
  concatenados com corte seco; saída 1080 de largura, FPS_PROJETO (25) CFR, H.264 yuv420p, sem áudio.
- `--previa` grava só o 1.º quadro de cada trecho em <pasta>/edicao/tela-previa/<id>-<n>.jpg para conferir o recorte.
- 120 fps / 60 fps de entrada viram 25 (filtro fps) — é gravação de tela, não há judder a temer.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

FFMPEG = os.environ.get("FFMPEG_BIN", "ffmpeg")
FPS = int(os.environ.get("FPS_PROJETO", "25"))


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"[recortar] ffmpeg falhou:\n{' '.join(cmd)}\n{r.stderr[-2000:]}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("tela_json")
    ap.add_argument("--so", default=None, help="só estes IDs, separados por vírgula")
    ap.add_argument("--previa", action="store_true")
    args = ap.parse_args()

    tj = Path(args.tela_json).resolve()
    cfg = json.loads(tj.read_text(encoding="utf-8"))
    if cfg.get("pasta_video"):
        pasta = Path(cfg["pasta_video"]).resolve()
    else:  # tela.json vive em videos/<slug>/edicao/ (padrão) ou direto em videos/<slug>/
        pasta = (tj.parent.parent if tj.parent.name == "edicao" else tj.parent).resolve()
    video = Path(cfg["video"])
    if not video.is_absolute():
        video = (pasta / video).resolve()
    if not video.exists():
        sys.exit(f"[recortar] gravação não encontrada: {video}")
    largura = int(cfg.get("largura_saida", 1080))
    padrao = cfg.get("recorte_padrao")
    so = set(s.strip().upper() for s in args.so.split(",")) if args.so else None
    extras = pasta / "brutos" / "extras"
    extras.mkdir(parents=True, exist_ok=True)
    previa_dir = pasta / "edicao" / "tela-previa"

    for cena in cfg["cenas"]:
        cid = cena["id"].upper()
        if so and cid not in so:
            continue
        rec_cena = cena.get("recorte") or padrao
        nome = cena.get("nome") or "tela"
        destino = extras / f"{cid}-{nome}.mp4"

        def crop_de(tr: dict) -> str:
            # o trecho pode ter o seu próprio recorte (ex.: o "gerando…" mais aberto que a caixa de digitação);
            # todos os recortes de uma cena devem ter a MESMA proporção, senão a altura de saída muda no meio
            rec = tr.get("recorte") or rec_cena
            if not rec:
                sys.exit(f"[recortar] {cid}: sem 'recorte' no trecho, na cena nem 'recorte_padrao'")
            return f"crop={rec['w']}:{rec['h']}:{rec['x']}:{rec['y']}"

        if args.previa:
            previa_dir.mkdir(parents=True, exist_ok=True)
            for n, tr in enumerate(cena["trechos"], start=1):
                out = previa_dir / f"{cid}-{n}.jpg"
                meio = (float(tr["inicio"]) + float(tr["fim"])) / 2
                run([FFMPEG, "-y", "-loglevel", "error", "-ss", f"{meio:.2f}", "-i", str(video), "-frames:v", "1",
                     "-vf", f"{crop_de(tr)},scale={largura}:-2", str(out)])
                print(f"[recortar] prévia {cid} trecho {n} (meio, {meio:.1f}s) -> {out.relative_to(pasta)}")
            continue
        with tempfile.TemporaryDirectory() as td:
            partes = []
            for n, tr in enumerate(cena["trechos"], start=1):
                vel = float(tr.get("velocidade", 1.0))
                parte = Path(td) / f"{cid}-{n}.mp4"
                vf = f"{crop_de(tr)},scale={largura}:-2,setpts=PTS/{vel},fps={FPS}"
                run([FFMPEG, "-y", "-loglevel", "error", "-ss", str(tr["inicio"]), "-to", str(tr["fim"]), "-i", str(video),
                     "-an", "-vf", vf, "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "16",
                     "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(parte)])
                partes.append(parte)
            lista = Path(td) / "lista.txt"
            lista.write_text("".join(f"file '{p}'\n" for p in partes), encoding="utf-8")
            run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", str(destino)])
        dur = sum((tr["fim"] - tr["inicio"]) / float(tr.get("velocidade", 1.0)) for tr in cena["trechos"])
        print(f"[recortar] {cid} -> {destino.relative_to(pasta)}  ({len(cena['trechos'])} trechos, ~{dur:.1f} s)")


if __name__ == "__main__":
    main()
