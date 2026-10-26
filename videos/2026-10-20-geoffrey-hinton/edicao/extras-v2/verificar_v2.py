#!/usr/bin/env python3
"""Verificação da v2 no ponto do defeito.

1. qa/v2/contato-meio.jpg  — 1 quadro no MEIO de cada uma das 29 entradas (com nº, tempo e mídia).
2. qa/v2/contato-trocas.jpg — para cada troca (12,48 … 139,12): último quadro antes | primeiro quadro depois.
3. Carlos visível? Compara CADA quadro do vídeo com o corte-cor.mp4 no mesmo instante (cinza 64×114, diferença média
   absoluta). Carlos = diferença < LIMIAR (só legenda por cima). Relata os quadros com Carlos dentro de 12,48–139,12
   e os quadros SEM Carlos fora dessa janela (fora o cartão do CTA).
4. Borda preta: em cada quadro do meio, fração de colunas/linhas da borda (20 px) quase pretas (< 16).

Uso: uv run python videos/2026-10-20-geoffrey-hinton/edicao/extras-v2/verificar_v2.py [video.mp4]
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
VIDEO = AQUI.parents[1]
FF = "/Users/teste/bin/ffmpeg"
ALVO = Path(sys.argv[1]) if len(sys.argv) > 1 else VIDEO / "edicao/render-remotion.mp4"
COR = VIDEO / "edicao/cor/corte-cor.mp4"
SAIDA = VIDEO / "qa/v2"
FPS = 25
LIMIAR = 14.0


def quadro(arq: Path, t: float, w: int = 360, h: int = 640) -> Image.Image:
    r = subprocess.run([FF, "-v", "error", "-ss", f"{t:.3f}", "-i", str(arq), "-frames:v", "1",
                        "-vf", f"scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       capture_output=True, check=True)
    return Image.frombytes("RGB", (w, h), r.stdout)


def todos_cinza(arq: Path, w: int = 64, h: int = 114) -> np.ndarray:
    r = subprocess.run([FF, "-v", "error", "-i", str(arq), "-vf", f"fps={FPS},scale={w}:{h}", "-f", "rawvideo",
                        "-pix_fmt", "gray", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, h, w).astype(np.float32)


def fonte():
    try:
        return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 22)
    except Exception:
        return ImageFont.load_default()


def rotular(im: Image.Image, txt: str) -> Image.Image:
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, im.width, 30], fill=(0, 0, 0))
    d.text((6, 4), txt, fill=(255, 220, 0), font=fonte())
    return im


def folha(ims: list[Image.Image], cols: int, destino: Path) -> None:
    w, h = ims[0].size
    linhas = (len(ims) + cols - 1) // cols
    o = Image.new("RGB", (cols * w, linhas * h), (60, 60, 60))
    for i, im in enumerate(ims):
        o.paste(im, ((i % cols) * w, (i // cols) * h))
    o.save(destino, quality=88)


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    ov = json.loads((AQUI / "overlays.json").read_text())["overlays"]
    rel: dict = {"video": str(ALVO), "entradas": [], "trocas": []}

    meios = []
    for o in ov:
        t = (o["saida_inicio"] + o["saida_fim"]) / 2
        im = quadro(ALVO, t)
        a = np.asarray(im.convert("L")).astype(np.float32)
        borda = {"esq": float((a[:, :8].mean(0) < 16).mean()), "dir": float((a[:, -8:].mean(0) < 16).mean()),
                 "topo": float((a[:8].mean(1) < 16).mean()), "base": float((a[-8:].mean(1) < 16).mean())}
        rel["entradas"].append({"n": o["extra"], "desc": o.get("descricao"), "t_meio": round(t, 2), "borda_preta": borda})
        meios.append(rotular(im, f"{o['extra']} {t:.1f}s {o.get('descricao', '')[6:]}"))
    folha(meios, 6, SAIDA / "contato-meio.jpg")

    cortes = [ov[0]["saida_inicio"]] + [o["saida_fim"] for o in ov]
    pares = []
    for c in cortes:
        antes = quadro(ALVO, c - 1 / FPS, 240, 427)
        depois = quadro(ALVO, c, 240, 427)
        pares += [rotular(antes, f"{c:.2f}- antes"), rotular(depois, f"{c:.2f}+ depois")]
    folha(pares, 10, SAIDA / "contato-trocas.jpg")

    # Carlos visível quadro a quadro
    v = todos_cinza(ALVO)
    c = todos_cinza(COR)
    n = min(len(v), len(c))
    dif = np.abs(v[:n] - c[:n]).mean(axis=(1, 2))
    t = np.arange(n) / FPS
    ini, fim = cortes[0], cortes[-1]
    dentro = (t >= ini - 1e-6) & (t < fim - 1e-6)
    carlos = dif < LIMIAR
    rel["carlos_dentro_da_faixa"] = [round(float(x), 2) for x in t[dentro & carlos]]
    fora = ~dentro
    rel["sem_carlos_fora_da_faixa"] = [round(float(x), 2) for x in t[fora & ~carlos]]
    rel["dif_min_dentro"] = round(float(dif[dentro].min()), 2)
    rel["dif_max_fora"] = round(float(dif[fora].max()), 2)
    rel["quadros"] = {"render": int(len(v)), "corte_cor": int(len(c))}
    (SAIDA / "verificacao.json").write_text(json.dumps(rel, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps({k: rel[k] for k in ("dif_min_dentro", "dif_max_fora", "quadros")}, ensure_ascii=False))
    print("Carlos dentro da faixa (s):", rel["carlos_dentro_da_faixa"][:40], "total", len(rel["carlos_dentro_da_faixa"]))
    sem = rel["sem_carlos_fora_da_faixa"]
    print("Sem Carlos fora da faixa (s):", (sem[:5], sem[-5:]) if sem else [], "total", len(sem))
    ruins = [e for e in rel["entradas"] if max(e["borda_preta"].values()) > 0.5]
    print("Entradas com borda quase preta > 50 %:", [(e["n"], e["desc"], e["borda_preta"]) for e in ruins])


if __name__ == "__main__":
    main()
