"""Filmstrips de cada ponto de corte -> edicao/frames/corte-NN.png + edicao/frames/contato.png

uso: uv run python filmstrip.py <video_dir> [--video edicao/corte.mp4]

Para cada fronteira entre peças na timeline de saída (troca de linha ou corte interno):
5 frames em -0,2 / -0,1 / 0 / +0,1 / +0,2 s (216 px de largura cada) + forma de onda de ±0,5 s,
com rótulos (linhas, take, tempo). contato.png = um frame por segmento (meio da linha).
Tempos -> frames no FPS do projeto (FPS_PROJETO, padrão 25).
O corte.mp4 ainda está em V-Log: nos trechos de câmera em log aplica a LUT de visualização
(00-marca/cor/luts/entrada-camera.cube) para não parecer lavado (--lut nao desliga; tela nunca recebe).
Depois, LEIA as imagens (Read) para "ver" os cortes: pulo de enquadramento, boca cortada, clique.
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (FFMPEG, FPS, edicao, ffmpeg, ffprobe_json, filtro_vista_log, fmt_t, ler_json, log,  # noqa: E402
                    pecas_da_edl, rel, resolver_video_dir, run)

LARG = 216
OFFS = [-0.2, -0.1, 0.0, 0.1, 0.2]
ONDA_S = 0.5
FUNDO = (18, 18, 22)
TEXTO = (235, 235, 235)
DESTAQUE = (255, 196, 0)


def fonte(tam: int):
    for f in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc",
              "/Library/Fonts/Arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(f, tam)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=tam)
    except TypeError:
        return ImageFont.load_default()


def extrair_frames(video: Path, numeros: list[int], altura: int, tmp: Path, vista: str = "") -> dict[int, Image.Image]:
    nums = sorted(set(numeros))
    expr = "+".join(f"eq(n\\,{n})" for n in nums)
    script = tmp / "sel.txt"
    # o select mantém o pts original -> o `enable` da LUT (tempo da timeline) continua válido
    script.write_text(f"select='{expr}'," + (f"{vista}," if vista else "")
                      + f"scale={LARG}:{altura}:flags=bicubic,format=rgb24")
    ffmpeg(["-i", str(video), "-filter_script:v", str(script), "-fps_mode", "passthrough",
            str(tmp / "f_%05d.png")])
    arqs = sorted(tmp.glob("f_*.png"))
    out = {}
    for n, a in zip(nums, arqs):
        out[n] = Image.open(a).convert("RGB")
    return out


def audio_mono(video: Path, sr: int = 16000) -> np.ndarray:
    r = run([FFMPEG, "-hide_banner", "-nostdin", "-loglevel", "error", "-i", str(video), "-vn", "-ac", "1",
             "-ar", str(sr), "-f", "f32le", "-"])
    return np.frombuffer(r.stdout, dtype=np.float32)


def desenhar_onda(x: np.ndarray, sr: int, t: float, largura: int, altura: int, marcas: list[float]) -> Image.Image:
    img = Image.new("RGB", (largura, altura), (28, 28, 34))
    d = ImageDraw.Draw(img)
    a, b = int((t - ONDA_S) * sr), int((t + ONDA_S) * sr)
    seg = np.zeros(b - a, dtype=np.float32)
    s0, s1 = max(0, a), min(len(x), b)
    if s1 > s0:
        seg[s0 - a:s1 - a] = x[s0:s1]
    meio = altura // 2
    # faixa coberta pelos frames (±0,2 s)
    fx0 = int((ONDA_S - 0.2) / (2 * ONDA_S) * largura)
    fx1 = int((ONDA_S + 0.2) / (2 * ONDA_S) * largura)
    d.rectangle([fx0, 0, fx1, altura], fill=(38, 38, 48))
    cols = np.array_split(seg, largura)
    pico = max(1e-4, float(np.abs(seg).max()))
    escala = (altura / 2 - 4) / max(pico, 0.05)
    for i, c in enumerate(cols):
        if len(c):
            d.line([(i, meio - float(c.max()) * escala), (i, meio - float(c.min()) * escala)], fill=(90, 200, 255))
    for m in marcas:
        mx = int((m - (t - ONDA_S)) / (2 * ONDA_S) * largura)
        if 0 <= mx < largura:
            d.line([(mx, 0), (mx, altura)], fill=(255, 120, 120), width=1)
    d.line([(largura // 2, 0), (largura // 2, altura)], fill=(255, 60, 60), width=2)
    f = fonte(14)
    d.text((4, 2), f"-{ONDA_S:.1f}s", font=f, fill=TEXTO)
    d.text((largura - 44, 2), f"+{ONDA_S:.1f}s", font=f, fill=TEXTO)
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video_dir")
    ap.add_argument("--video", default="edicao/corte.mp4")
    ap.add_argument("--lut", choices=["auto", "sim", "nao"], default="auto",
                    help="LUT de visualização nos trechos em log (auto = só no edicao/corte.mp4, que ainda não tem cor)")
    args = ap.parse_args()
    vd = resolver_video_dir(args.video_dir)
    ed = edicao(vd)
    video = (vd / args.video) if not Path(args.video).is_absolute() else Path(args.video)
    if not video.exists():
        sys.exit(f"[ERRO] {video} não existe (rode render_corte.py)")
    edl = ler_json(ed / "edl.json")
    sem_cor = video.resolve() == (ed / "corte.mp4").resolve()
    vista = filtro_vista_log(vd, edl) if (args.lut == "sim" or (args.lut == "auto" and sem_cor)) else ""
    if vista:
        log("[filmstrip] câmera em log: frames com a LUT de visualização (entrada-camera.cube)")
    pecas = pecas_da_edl(edl)
    info = ffprobe_json(video)
    vs = next(s for s in info["streams"] if s["codec_type"] == "video")
    alt = int(round(LARG * int(vs["height"]) / int(vs["width"]) / 2) * 2)
    n_total = int(vs.get("nb_frames") or round(float(info["format"]["duration"]) * FPS))
    fronteiras = []
    zoom_ok = bool(edl.get("zoom_no_corte"))          # plano de zoom aplicado no corte (senão, só no Remotion)
    for k in range(1, len(pecas)):
        a, b = pecas[k - 1], pecas[k]
        tipo = "troca de linha" if a.seg != b.seg else "corte interno"
        fronteiras.append({"t": b.saida, "tipo": tipo, "de": a.linha, "para": b.linha,
                           "za": a.escala if zoom_ok else 1.0, "zb": b.escala if zoom_ok else 1.0,
                           "src": f"{a.fonte} {fmt_t(a.b)} | {b.fonte} {fmt_t(b.a)}"})
    segs = edl["segmentos"]
    meios = [int(round((s["saida_inicio"] + s["saida_fim"]) / 2 * FPS)) for s in segs]
    numeros = [min(n_total - 1, max(0, int(round((f["t"] + o) * FPS)))) for f in fronteiras for o in OFFS] + \
              [min(n_total - 1, m) for m in meios]
    outdir = ed / "frames"
    outdir.mkdir(parents=True, exist_ok=True)
    for velho in outdir.glob("corte-*.png"):
        velho.unlink()
    x = audio_mono(video)
    marcas_todas = [p.saida for p in pecas[1:]]
    with tempfile.TemporaryDirectory() as td:
        frames = extrair_frames(video, numeros, alt, Path(td), vista)
    f_tit, f_lab = fonte(22), fonte(16)
    W = LARG * len(OFFS)
    for k, fr in enumerate(fronteiras, start=1):
        topo, onda_h = 40, 150
        img = Image.new("RGB", (W, topo + alt + 24 + onda_h), FUNDO)
        d = ImageDraw.Draw(img)
        mesmo = abs(fr["za"] - fr["zb"]) < 0.04
        titulo = (f"corte {k:02d} · {fr['tipo']} · {fr['de']} → {fr['para']} · saída {fmt_t(fr['t'])} · "
                  f"zoom {fr['za']:.2f}→{fr['zb']:.2f}" + (" MESMO!" if mesmo else ""))
        d.text((8, 8), titulo, font=f_tit, fill=(255, 90, 90) if mesmo else
               DESTAQUE if fr["tipo"] == "corte interno" else TEXTO)
        for j, o in enumerate(OFFS):
            n = min(n_total - 1, max(0, int(round((fr["t"] + o) * FPS))))
            im = frames.get(n)
            if im is not None:
                img.paste(im, (j * LARG, topo))
            if o == 0.0:
                d.rectangle([j * LARG, topo, (j + 1) * LARG - 1, topo + alt - 1], outline=(255, 60, 60), width=3)
            lado = fr["de"] if o < 0 else fr["para"]
            d.text((j * LARG + 6, topo + alt + 3), f"{o:+.1f}s {lado} ×{fr['za'] if o < 0 else fr['zb']:.2f}",
                   font=f_lab, fill=TEXTO)
        onda = desenhar_onda(x, 16000, fr["t"], W, onda_h,
                             [m for m in marcas_todas if abs(m - fr["t"]) <= ONDA_S and m != fr["t"]])
        img.paste(onda, (0, topo + alt + 24))
        d.text((W - 460, 12), fr["src"], font=f_lab, fill=(160, 160, 170))
        img.save(outdir / f"corte-{k:02d}.png")
    # folha de contato
    cols = 5
    th = 30
    rows = max(1, (len(segs) + cols - 1) // cols)
    folha = Image.new("RGB", (cols * LARG, rows * (alt + th)), FUNDO)
    d = ImageDraw.Draw(folha)
    for k, (s, m) in enumerate(zip(segs, meios)):
        r, c = divmod(k, cols)
        im = frames.get(min(n_total - 1, m))
        if im is not None:
            folha.paste(im, (c * LARG, r * (alt + th)))
        d.text((c * LARG + 6, r * (alt + th) + alt + 5),
               f"{s['linha']} {s['take'].split('-')[-1]} · {fmt_t(s['saida_inicio'])}", font=f_lab, fill=TEXTO)
    folha.save(outdir / "contato.png")
    log(f"[filmstrip] {len(fronteiras)} cortes -> {rel(vd, outdir)}/corte-NN.png + contato.png")
    for k, fr in enumerate(fronteiras, start=1):
        log(f"   corte-{k:02d}.png  {fmt_t(fr['t'])}  {fr['tipo']:<14} {fr['de']} → {fr['para']}")


if __name__ == "__main__":
    main()
