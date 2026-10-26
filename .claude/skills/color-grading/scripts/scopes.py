"""Scopes (ffmpeg waveform + parade RGB + vectorscope) num PNG legível.

Uso:
  uv run python .claude/skills/color-grading/scripts/scopes.py <imagem_ou_video> [--t 3.2] [--saida x.png]

No vectorscope há uma linha laranja tracejada = linha de tom de pele (skin line):
a pele natural fica encostada nela, entre o vermelho e o amarelo.
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _comum as C  # noqa: E402

LARG = 720  # largura dos waveforms


def _ffmpeg_img(entrada: Path, vf: str, saida: Path) -> Image.Image:
    C.run([C.FFMPEG, "-v", "error", "-y", "-i", str(entrada), "-vf", vf, "-frames:v", "1", str(saida)])
    return Image.open(saida).convert("RGB")


def _linha_pele(vs: Image.Image) -> Image.Image:
    """Desenha a skin line. Vectorscope ffmpeg: x = Cb, y = 255 − Cr (8 bits, 256×256)."""
    d = ImageDraw.Draw(vs)
    # tom de pele médio (qualquer etnia fica próxima desta direção)
    y = 0.299 * 0.80 + 0.587 * 0.58 + 0.114 * 0.47
    cb = ((0.47 - y) * 0.564 + 0.5) * 255
    cr = ((0.80 - y) * 0.713 + 0.5) * 255
    cx, cy = 128.0, 128.0
    dx, dy = cb - cx, (255 - cr) - cy
    k = 120 / max(1e-6, (dx * dx + dy * dy) ** 0.5)
    ex, ey = cx + dx * k, cy + dy * k
    for i in range(0, 12):
        t0, t1 = i / 12, (i + 0.5) / 12
        d.line([(cx + (ex - cx) * t0, cy + (ey - cy) * t0), (cx + (ex - cx) * t1, cy + (ey - cy) * t1)],
               fill=(255, 150, 40), width=1)
    return vs


def scopes_de(img: Path, tmp: Path, tag: str) -> dict[str, Image.Image]:
    base = f"scale={LARG}:-2:flags=bicubic"
    yuv = "scale=out_color_matrix=bt709:out_range=tv,format=yuv444p"
    wf = _ffmpeg_img(img, f"{base},{yuv},waveform=m=column:c=1:d=overlay:g=green:fl=numbers+dots:s=ire:i=0.06",
                     tmp / f"{tag}-wf.png")
    par = _ffmpeg_img(img, f"{base},format=gbrp,waveform=m=column:c=7:d=parade:g=green:fl=numbers:i=0.08",
                      tmp / f"{tag}-par.png")
    vs = _ffmpeg_img(img, f"scale=540:-2,{yuv},vectorscope=m=color3:g=green:flags=name+white+black:i=0.02:b=1",
                     tmp / f"{tag}-vs.png")
    vs = _linha_pele(vs).resize((360, 360), Image.BICUBIC)
    return {"thumb": Image.open(img).convert("RGB"), "waveform": wf, "parade": par, "vectorscope": vs}


def montar(colunas: list[tuple[str, Path]], saida: Path, titulo: str = "") -> Path:
    """colunas = [(rótulo, png_da_imagem)], lado a lado."""
    fonte, fonte_p = C.fonte_png(30), C.fonte_png(18)
    blocos = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for i, (rot, img) in enumerate(colunas):
            s = scopes_de(img, tmp, f"c{i}")
            thumb = s["thumb"]
            thumb.thumbnail((LARG, 420))
            pecas = [("", thumb), ("Waveform luma (IRE)", s["waveform"].resize((LARG, 300))),
                     ("Parade RGB", s["parade"].resize((LARG, 300))),
                     ("Vectorscope (laranja = linha de pele)", s["vectorscope"])]
            alt = 60 + sum(p.height + 34 for _, p in pecas)
            col = Image.new("RGB", (LARG + 20, alt), (18, 18, 18))
            d = ImageDraw.Draw(col)
            d.text((10, 12), rot, fill=(255, 255, 255), font=fonte)
            y = 60
            for leg, p in pecas:
                if leg:
                    d.text((10, y + 4), leg, fill=(180, 180, 180), font=fonte_p)
                y += 30
                col.paste(p, (10 + (LARG - p.width) // 2, y))
                y += p.height + 4
            blocos.append(col)
    topo = 50 if titulo else 0
    W = sum(b.width for b in blocos) + 10 * (len(blocos) - 1)
    H = max(b.height for b in blocos) + topo
    out = Image.new("RGB", (W, H), (40, 40, 40))
    if titulo:
        ImageDraw.Draw(out).text((12, 10), titulo, fill=(255, 255, 255), font=C.fonte_png(26))
    x = 0
    for b in blocos:
        out.paste(b, (x, topo))
        x += b.width + 10
    saida.parent.mkdir(parents=True, exist_ok=True)
    out.save(saida)
    return saida


def mosaico(frames: list[np.ndarray], saida: Path) -> Path:
    """Junta frames lado a lado (para o scope refletir vários segmentos)."""
    h = min(f.shape[0] for f in frames)
    fr = [f[:h] for f in frames]
    C.salvar_png(np.concatenate(fr, axis=1), saida)
    return saida


def main() -> None:
    ap = argparse.ArgumentParser(description="PNG com waveform, parade RGB e vectorscope.")
    ap.add_argument("entrada", help="imagem ou vídeo")
    ap.add_argument("--t", type=float, default=None, help="tempo (s) se for vídeo; padrão = meio")
    ap.add_argument("--saida", default=None)
    a = ap.parse_args()
    p = C.resolver(a.entrada)
    saida = Path(a.saida) if a.saida else p.with_name(p.stem + "-scopes.png")
    with tempfile.TemporaryDirectory() as td:
        img = Path(td) / "frame.png"
        if p.suffix.lower() in C.EXT_VIDEO:
            info = C.probe(p)
            t = a.t if a.t is not None else C.duracao_de(info) / 2
            C.salvar_png(C.ler_frame(p, t, 1080), img)
            rot = f"{p.name} @ {t:.2f}s"
        else:
            C.salvar_png(C.ler_imagem(p, 1920), img)
            rot = p.name
        montar([(rot, img)], saida)
    print(f"scopes → {saida}")


if __name__ == "__main__":
    main()
