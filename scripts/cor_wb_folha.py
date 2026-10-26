"""Balanço de branco pela FOLHA BRANCA + casamento mínimo por fonte (generalizado: recebe o video_dir).

Decisão do Carlos (15/10): toda gravação abre com a folha branca no 1.º arquivo; o colorista usa a folha para o
balanço de branco. Regra 11 (19/09): o resto é casado POR FONTE, só onde destoa, alvo = mediana dos arquivos.

Uso (da raiz):
  uv run python scripts/cor_wb_folha.py medir     videos/<slug> [--referencia praq0978] [--roi x0,y0,x1,y1]
  uv run python scripts/cor_wb_folha.py verificar videos/<slug>        # mede o corte-cor.mp4 FINAL (não decide nada)

`medir` mede SÓ nas fontes (nunca no resultado), grava edicao/cor/wb-folha.json e faz o teste da folha com um render
novo (curves do ffmpeg, o mesmo filtro da produção). O json alimenta `aplicar_cor.py --ganhos-json`.
Cadeia de medição = a da produção: yuv 10-bit (V-Log) -> gbrp16le -> LUT de entrada -> [WB base] (-> look).
"""
import argparse, json, subprocess, sys
from pathlib import Path
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / ".claude/skills/color-grading/scripts"))
import _comum as C  # noqa: E402
import entrada as E  # noqa: E402

L709 = C.LUMA709
W, H = 360, 640
XS = [0, 0.0625, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 0.9375, 1.0]
LIM_IRE_LUMA = 0.02     # só corrige uma fonte se a pele destoar > 2 IRE da mediana...
LIM_CROMA = 0.02        # ... ou > 2 % em razão R/G ou B/G


def curva(x, k):
    """A mesma curva do aplicar_cor (curva_pts): y = x·k/(1+(k−1)·xⁿ), n=4 (k≤4/3)."""
    n = 4.0 if k <= 4 / 3 else 1.0 + 1.0 / (k - 1.0)
    return x * k / (1 + (k - 1) * x ** n)


def resolver_k(x, alvo):
    lo, hi = 0.7, 1.3
    for _ in range(60):
        m = (lo + hi) / 2
        if curva(x, m) < alvo:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


def filtro_curves(ks):
    kmin, kmax = 0.7, 1.3
    return "curves=" + ":".join(
        f"{c}='" + " ".join(f"{x:.4f}/{min(1.0, max(0.0, curva(x, min(kmax, max(kmin, k))))):.4f}" for x in XS) + "'"
        for c, k in zip("rgb", ks)) + ":interp=pchip"


def decodificar(arq, i, dur, fps, lut_ent, wb=None, extra=""):
    vf = [f"fps={fps}", f"scale={W}:{H}:flags=bicubic", E.CONVERSAO_RGB16,
          f"lut3d=file={C.esc_filtro(lut_ent)}:interp=tetrahedral"]
    if wb:
        vf.append(filtro_curves(wb))
    if extra:
        vf.append(extra)
    vf.append("format=rgb48le")
    r = C.run([C.FFMPEG, "-v", "error", "-ss", f"{i:.3f}", "-t", f"{dur:.3f}", "-i", str(arq), "-vf", ",".join(vf),
               "-f", "rawvideo", "-"], capturar=True)
    return np.frombuffer(r.stdout, np.uint16).reshape(-1, H, W, 3).astype(np.float64) / 65535


def estat_frame(f):
    top = f[:int(.45 * H)].reshape(-1, 3)
    w = C.peso_pele(top) > 0.5
    skin = np.median(top[w], 0) if w.sum() > 400 else None
    sh = f[int(.62 * H):int(.95 * H), 30:330].reshape(-1, 3)
    Y = sh @ L709
    m = (Y >= np.percentile(Y, 80)) & ~(C.peso_pele(sh) > 0.2)
    return skin, np.median(sh[m], 0)


def medir(a):
    vd = C.resolver(a.video_dir)
    ed = vd / "edicao"
    edl = C.ler_json(ed / "edl.json")
    fontes = sorted(C.ler_json(ed / "fontes.json")["fontes"])
    ref = a.referencia or fontes[0]
    lut_ent, desc = E.exigir_lut_vlog()
    out = ed / "cor"
    out.mkdir(exist_ok=True)
    x0, y0, x1, y1 = (float(v) for v in a.roi.split(","))
    ry, rx = slice(int(y0 * H), int(y1 * H)), slice(int(x0 * W), int(x1 * W))
    arq = ed / "fontes" / f"{ref}.mp4"

    # 1) folha: frames em que o ROI é claro e plano
    fr = decodificar(arq, 0, a.tmax, 2, lut_ent)
    linhas, med_f = [], []
    for i, f in enumerate(fr):
        roi = f[ry, rx].reshape(-1, 3)
        m = np.median(roi, 0)
        sd = float(roi.std(0).mean())
        ok = bool(m @ L709 > 0.6 and sd < 0.04)
        linhas.append({"t": i / 2, "rgb": [round(float(v), 4) for v in m], "std": round(sd, 4), "folha": ok})
        if ok:
            med_f.append(m)
    if len(med_f) < 4:
        raise SystemExit("folha não encontrada (ajuste --roi/--tmax)")
    # as 2 primeiras e as 2 últimas amostras ficam de fora (mão a entrar/sair)
    usados = np.array(med_f[2:-2]) if len(med_f) > 8 else np.array(med_f)
    folha = np.median(usados, 0)
    yf = float(folha @ L709)
    alvo = np.array([yf] * 3)
    ks = [resolver_k(float(x), float(t)) for x, t in zip(folha, alvo)]
    ganho_efetivo = [float(t / x) for x, t in zip(folha, alvo)]
    desv = lambda c: float(np.max(np.abs(c - c.mean())))  # noqa: E731
    print(f"folha ({len(usados)} amostras, {ref}): RGB {np.round(folha, 4)}  Y {yf:.4f}  desvio de neutro max|c-média| {desv(folha):.4f}")
    print(f"WB base: k = {np.round(ks, 4)}  (ganho efetivo na folha {np.round(ganho_efetivo, 4)})")

    # 2) teste: render NOVO da referência com a correção; mede de novo
    teste = out / "_teste-folha.mkv"
    ini, dur = 3.0, 8.0
    C.run([C.FFMPEG, "-v", "error", "-y", "-ss", f"{ini}", "-t", f"{dur}", "-i", str(arq), "-vf",
           ",".join([E.CONVERSAO_RGB16, f"lut3d=file={C.esc_filtro(lut_ent)}:interp=tetrahedral", filtro_curves(ks)]),
           "-an", "-c:v", "ffv1", "-pix_fmt", "gbrp16le", str(teste)])
    r = C.run([C.FFMPEG, "-v", "error", "-i", str(teste), "-vf", f"fps=2,scale={W}:{H}:flags=bicubic,format=rgb48le",
               "-f", "rawvideo", "-"], capturar=True)
    fr2 = np.frombuffer(r.stdout, np.uint16).reshape(-1, H, W, 3).astype(np.float64) / 65535
    depois = np.median(np.array([np.median(f[ry, rx].reshape(-1, 3), 0) for f in fr2[2:-2]]), 0)
    teste.unlink()
    print(f"folha DEPOIS (render novo): RGB {np.round(depois, 4)}  desvio max|c-média| {desv(depois):.4f}")

    # 3) por fonte (nas FONTES, depois de entrada + WB base)
    res = {}
    for s in edl["segmentos"]:
        fr = decodificar(ed / "fontes" / f"{s['fonte']}.mp4", s["in"], s["out"] - s["in"], 4, lut_ent, wb=ks)
        d = res.setdefault(s["fonte"], {"skin": [], "shirt": []})
        for f in fr:
            sk, sh = estat_frame(f)
            if sk is not None:
                d["skin"].append(sk)
            d["shirt"].append(sh)
    tab = {f: {"skin": np.median(d["skin"], 0), "shirt": np.median(d["shirt"], 0), "n": len(d["skin"])}
           for f, d in res.items()}
    ref_skin = np.median(np.array([t["skin"] for t in tab.values()]), 0)   # mediana dos arquivos
    rs_y = float(ref_skin @ L709)
    print(f"\nalvo = mediana das fontes (pele após entrada+WB): RGB {np.round(ref_skin, 4)} Y {rs_y:.4f}")
    saida = {}
    for f, t in sorted(tab.items()):
        sk = t["skin"]
        dy = float(sk @ L709) - rs_y
        dc = [float((sk[0] / sk[1]) / (ref_skin[0] / ref_skin[1]) - 1), float((sk[2] / sk[1]) / (ref_skin[2] / ref_skin[1]) - 1)]
        destoa = abs(dy) > LIM_IRE_LUMA or max(abs(dc[0]), abs(dc[1])) > LIM_CROMA
        g = np.clip(ref_skin / sk, 0.9, 1.1) if destoa else np.ones(3)
        total = [float(k * x) for k, x in zip(ks, g)]
        ev = float(2.2 * np.log2(g @ L709)) if destoa else 0.0
        saida[f] = {"ganhos": [round(x, 4) for x in total], "ev": round(ev, 3), "ganho_fonte": [round(float(x), 4) for x in g],
                    "destoa": destoa,
                    "medicao_apos_entrada_wb": {"pele_rgb": [round(float(v), 4) for v in sk], "pele_Y": round(float(sk @ L709), 4),
                                                "camisa_rgb": [round(float(v), 4) for v in t["shirt"]], "n": t["n"],
                                                "d_pele_Y_ire": round(dy * 100, 2), "d_pele_RG_BG_pct": [round(x * 100, 2) for x in dc]}}
        print(f"  {f}: pele Y {sk @ L709:.4f} ({dy * 100:+.2f} IRE vs mediana) R/G {dc[0] * 100:+.2f}% B/G {dc[1] * 100:+.2f}%  "
              f"camisa {np.round(t['shirt'], 4)}  -> {'CORRIGE ' + str(np.round(g, 3)) if destoa else 'so base'}")
    C.escrever_json(out / "wb-folha.json", {
        "referencia": ref, "roi_norm": [x0, y0, x1, y1], "lut_entrada": desc,
        "folha": {"amostras": len(usados), "rgb_antes": [round(float(v), 4) for v in folha], "Y": round(yf, 4),
                  "desvio_neutro_antes": round(desv(folha), 4), "rgb_depois": [round(float(v), 4) for v in depois],
                  "desvio_neutro_depois": round(desv(depois), 4), "k_base": [round(k, 4) for k in ks],
                  "ganho_efetivo_na_folha": [round(g, 4) for g in ganho_efetivo], "frames": linhas},
        "alvo_pele_mediana": [round(float(v), 4) for v in ref_skin],
        "limiares": {"pele_Y_ire": LIM_IRE_LUMA * 100, "razao_croma_pct": LIM_CROMA * 100},
        "fontes": saida})
    print("-> edicao/cor/wb-folha.json")


def _decode_final(arq, t0, dur, fps=4):
    vf = f"fps={fps},scale={W}:{H}:flags=bicubic:in_color_matrix=bt709:out_range=pc,format=rgb24"
    r = C.run([C.FFMPEG, "-v", "error", "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", str(arq), "-vf", vf, "-f", "rawvideo", "-"],
              capturar=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, H, W, 3).astype(np.float64) / 255


def face_stats(f):
    top = f[:int(.45 * H)]
    w = C.peso_pele(top.reshape(-1, 3)).reshape(top.shape[:2]) > 0.5
    if w.sum() < 300:
        return None
    Y = f @ L709
    lat = np.zeros(Y.shape, bool)
    lat[:int(.45 * H), :int(.15 * W)] = True
    lat[:int(.45 * H), int(.85 * W):] = True
    return {"rosto": float(np.median(top[w] @ L709) * 100), "pele": np.median(top[w], 0),
            "fundo": float(np.median(Y[lat]) * 100), "preto": float(np.percentile(Y, 0.5) * 100),
            "p99_5": float(np.percentile(Y, 99.5) * 100), "max": float(Y.max() * 100)}


def verificar(a):
    vd = C.resolver(a.video_dir)
    ed = vd / "edicao"
    edl = C.ler_json(ed / "edl.json")
    arq = ed / "cor" / "corte-cor.mp4"
    por = {}
    for s in edl["segmentos"]:
        a0, a1 = s["saida_inicio"] + 0.2, s["saida_fim"] - 0.2
        for f in _decode_final(arq, a0, a1 - a0):
            st = face_stats(f)
            if st:
                por.setdefault(s["fonte"], []).append(st)
    print("fonte      n  rosto  fundo  preto  p99.5  max   pele RGB")
    for fo, v in sorted(por.items()):
        m = lambda k: float(np.median([x[k] for x in v]))  # noqa: E731
        p = np.median([x["pele"] for x in v], 0)
        print(f"{fo} {len(v):3d} {m('rosto'):6.1f} {m('fundo'):6.1f} {m('preto'):6.1f} {m('p99_5'):6.1f} {m('max'):6.1f}  {np.round(p * 255, 1)}")
    segs = edl["segmentos"]
    print("\nemendas entre FONTES (±0,32 s, 8 quadros cada lado):")
    for k in range(1, len(segs)):
        if segs[k]["fonte"] == segs[k - 1]["fonte"]:
            continue
        t = segs[k]["saida_inicio"]
        ant = [face_stats(f) for f in _decode_final(arq, t - 0.4, 0.4, 20)]
        dep = [face_stats(f) for f in _decode_final(arq, t, 0.4, 20)]
        ant, dep = [x for x in ant if x], [x for x in dep if x]
        if not ant or not dep:
            print(f"  {segs[k - 1]['fonte']}->{segs[k]['fonte']} @{t:.2f}s: sem pele medida"); continue
        ma, md = np.median([x["rosto"] for x in ant]), np.median([x["rosto"] for x in dep])
        pa, pd = np.median([x["pele"] for x in ant], 0) * 255, np.median([x["pele"] for x in dep], 0) * 255
        fa, fd = np.median([x["fundo"] for x in ant]), np.median([x["fundo"] for x in dep])
        print(f"  {segs[k - 1]['fonte']}->{segs[k]['fonte']} @{t:.2f}s: rosto {ma:.1f} -> {md:.1f} IRE (d {md - ma:+.2f}); "
              f"fundo {fa:.1f} -> {fd:.1f}; pele RGB {np.round(pa, 1)} -> {np.round(pd, 1)} (d {np.round(pd - pa, 1)})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("modo", choices=["medir", "verificar"])
    ap.add_argument("video_dir")
    ap.add_argument("--referencia", default=None)
    ap.add_argument("--roi", default="0.17,0.21,0.83,0.41", help="x0,y0,x1,y1 normalizados da folha")
    ap.add_argument("--tmax", type=float, default=20.0)
    a = ap.parse_args()
    (medir if a.modo == "medir" else verificar)(a)
