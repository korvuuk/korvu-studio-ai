"""Aplica a cor da marca ao corte e às cenas extras de câmera: [V-Log→709] + primária por take + LUT fixa (+ grão).

Uso (da raiz do projeto):
  uv run python .claude/skills/color-grading/scripts/aplicar_cor.py videos/<slug> \
      [--lut 00-marca/cor/luts/korvu-look-v1.cube] [--intensidade 1.0] [--sem-primaria] [--sem-entrada] \
      [--limite-ev 0.5] [--limite-wb 0.08] [--grao 0.3] [--sem-extras | --so-extras]

Entrada : <video_dir>/edicao/corte.mp4 (+ edicao/edl.json = segmentos; edicao/fontes.json = tipo/perfil por
          fonte e lista de `extras`) e edicao/extras/<ID>.mp4 das cenas extras de tipo `camera`.
Saída   : <video_dir>/edicao/cor/corte-cor.mp4, antes-depois.png, scopes.png, correcoes.json, filtro*.txt
          e edicao/extras/<ID>-cor.mp4 para cada extra de câmera.

Cadeia por segmento, SEMPRE a 16 bits por canal (só o encode final é 8-bit):
  yuv (10-bit 4:2:2 V-Log ou SDR; range limitado) → gbrp16le
  → [LUT de entrada V-Log→Rec.709: só câmera com perfil vlog]
  → primária (curves por canal) → LUT da marca (lut3d tetraédrica) → concat → yuv420p bt709 (+ grão)
- Perfil: edicao/fontes.json ("perfil": "vlog"|"sdr" por fonte/extra); sem ele, câmera usa CAMERA_PERFIL (vlog).
- Cada take (fonte+take do EDL) — e cada extra de câmera, como um take único — é medido DEPOIS da entrada
  (já em Rec.709): luminância média e gray-world nos meios-tons → ganho/curva para o MESMO `alvo_primaria`
  do JSON da LUT (é o que faz o B-roll de câmera ter a mesma cor do principal).
  Limites: --limite-ev (padrão ±0.5 stop) e --limite-wb (padrão ±8%/canal). Curva com roll-off: brancos ficam em 1.0.
- Nunca recebem cor: segmentos `tela-*` do corte e extras de tipo tela/print/imagem/video/animacao.
- LUT padrão (sem --lut): a versão mais alta com "aprovada": true no JSON (senão a mais alta, com aviso).
- Áudio copiado sem recodificar. Vídeo: H.264 CRF 16, yuv420p, tags bt709, mesmo tamanho e mesmos
  frames/timestamps da fonte (fps nunca é convertido).
"""
from __future__ import annotations

import argparse
import datetime as dt
import math
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _comum as C  # noqa: E402
import entrada as E  # noqa: E402
import scopes as SC  # noqa: E402

MAX_STOPS = 0.5   # padrão de --limite-ev
MAX_CANAL = 0.08  # padrão de --limite-wb
XS = [0, 0.0625, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 0.9375, 1.0]
# no ffmpeg 7.1 as opções -color_* de saída não bastam: as tags vêm dos frames do filtergraph
SETPARAMS_709 = "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv"


def _num_versao(p: Path) -> int:
    m = re.search(r"-v(\d+)", p.stem)
    return int(m.group(1)) if m else -1


def escolher_lut(arg: str | None) -> Path:
    if arg:
        p = C.resolver(arg)
        if not p.exists():
            raise SystemExit(f"LUT não encontrada: {p}")
        return p
    cands = sorted(C.LUTS_DIR.glob("korvu-look-v*.cube"), key=_num_versao)
    if not cands:
        raise SystemExit(f"Nenhuma LUT em {C.rel(C.LUTS_DIR)}. Rode /criar-lut primeiro.")
    aprov = [c for c in cands if c.with_suffix(".json").exists()
             and C.ler_json(c.with_suffix(".json")).get("aprovada")]
    if aprov:
        return aprov[-1]
    print(f"⚠ nenhuma LUT marcada como aprovada; a usar {cands[-1].name}")
    return cands[-1]


def carregar_segmentos(edl: dict | None, fps: float, dur: float) -> list[dict]:
    if not edl or not edl.get("segmentos"):
        print("⚠ sem edl.json/segmentos: o corte inteiro é tratado como um único take")
        return [{"n": 1, "fonte": "camera-01", "take": None, "linha": None, "ini": 0.0, "fim": dur,
                 "f0": 0, "f1": None, "grupo": "camera-01|n1"}]
    segs = sorted(edl["segmentos"], key=lambda s: float(s["saida_inicio"]))
    out = []
    for k, s in enumerate(segs):
        out.append({"n": s.get("n", k + 1), "fonte": s.get("fonte", "camera-01"), "take": s.get("take"),
                    "linha": s.get("linha"), "ini": float(s["saida_inicio"]), "fim": float(s["saida_fim"]),
                    "f0": int(round(float(s["saida_inicio"]) * fps))})
    out[0]["f0"] = 0
    for k, s in enumerate(out):
        s["f1"] = out[k + 1]["f0"] if k + 1 < len(out) else None
        s["grupo"] = f"{s['fonte']}|{s['take'] or 'n' + str(s['n'])}"
    return [s for s in out if s["f1"] is None or s["f1"] > s["f0"]]


def e_tela(s: dict) -> bool:
    return str(s["fonte"]).lower().startswith("tela-") or s.get("tipo") == "tela"


def e_camera(s: dict) -> bool:
    return (s.get("tipo") or E.tipo_por_nome(str(s["fonte"]))) == "camera"


def anotar_segmentos(segs: list[dict], fontes: dict, usar_entrada: bool = True) -> None:
    """tipo/perfil por segmento (fontes.json → nome/env) e se recebe a LUT de entrada V-Log."""
    for s in segs:
        nome = str(s["fonte"])
        s["tipo"] = "tela" if nome.lower().startswith("tela-") else E.tipo_da_fonte(nome, fontes)
        s["perfil"] = E.perfil_da_fonte(nome, fontes, s["tipo"])
        s["entrada"] = bool(usar_entrada and s["tipo"] == "camera" and s["perfil"] == "vlog")


def decodificar_amostras(video: Path, filtro_pre: str, info: dict, fps_a: int = 4, larg: int = 270):
    """Frames a `fps_a` fps em RGB 0–1. Com `filtro_pre` (tone-map HDR / LUT de entrada), reduz primeiro
    no YUV original e aplica o filtro a 16 bits antes de passar a 8 bits para a medição."""
    s = C.stream_video(info)
    w, h = C.dims_exibidas(s)
    alt = int(round(larg * h / w / 2) * 2)
    vf = ",".join(x for x in [f"fps={fps_a}", f"scale={larg}:{alt}:flags=bicubic" if filtro_pre else "",
                               filtro_pre, f"scale={larg}:{alt}:in_color_matrix=bt709:out_range=pc",
                               "format=rgb24"] if x)
    r = C.run([C.FFMPEG, "-v", "error", "-i", str(video), "-vf", vf, "-f", "rawvideo", "-"], capturar=True)
    arr = np.frombuffer(r.stdout, np.uint8).reshape(-1, alt, larg, 3).astype(np.float32) / 255
    return arr, np.arange(len(arr)) / fps_a


def calcular_correcao(med: dict, alvo: dict | None, max_ev: float = MAX_STOPS,
                      max_wb: float = MAX_CANAL) -> dict:
    if not med["confiavel"]:
        return {"ev": 0.0, "ganhos": [1.0, 1.0, 1.0], "nota": "medição pouco confiável → sem correção"}
    notas = []
    if alvo:
        k = alvo["luma"] / max(med["luma"], 1e-4)
        ev = 2.2 * math.log2(max(k, 1e-4))  # valores codificados (gamma) → stops aproximados
        if abs(ev) > max_ev:
            notas.append(f"exposição limitada ({ev:+.2f} → {math.copysign(max_ev, ev):+.2f} EV)")
        ev = max(-max_ev, min(max_ev, ev))
        t = np.array(alvo["rgb_neutro"], dtype=float)
    else:
        ev, t = 0.0, np.ones(3)
        notas.append("LUT sem alvo_primaria → só balanço de branco para neutro")
    kl = 2 ** (ev / 2.2)
    s = np.array(med["rgb_neutro"], dtype=float)
    t, s = t / (t @ C.LUMA709), s / max(s @ C.LUMA709, 1e-4)
    wb = t / np.maximum(s, 1e-4)
    wb = wb / (wb @ C.LUMA709)
    wb_c = np.clip(wb, 1 - max_wb, 1 + max_wb)
    if np.any(np.abs(wb - wb_c) > 1e-6):
        notas.append(f"balanço de branco limitado a ±{max_wb * 100:g}%/canal")
    g = kl * wb_c
    return {"ev": round(ev, 3), "ganhos": [round(float(v), 4) for v in g], "nota": "; ".join(notas)}


def limites_ganho(max_ev: float, max_wb: float) -> tuple[float, float]:
    """Faixa do ganho total por canal na curva (nunca mais estreita que os 0.7–1.3 históricos)."""
    return (min(0.7, 2 ** (-max_ev / 2.2) * (1 - max_wb)), max(1.3, 2 ** (max_ev / 2.2) * (1 + max_wb)))


def curva_pts(k: float, kmin: float = 0.7, kmax: float = 1.3) -> str:
    """Ganho k nos meios-tons com roll-off: y = x·k/(1+(k−1)·xⁿ), y(0)=0, y(1)=1.
    n=4 (histórico) é monótona até k=4/3; acima disso n = 1+1/(k−1) mantém a curva monótona."""
    k = min(kmax, max(kmin, k))
    n = 4.0 if k <= 4 / 3 else 1.0 + 1.0 / (k - 1.0)
    return " ".join(f"{x:.4f}/{min(1.0, max(0.0, x * k / (1 + (k - 1) * x ** n))):.4f}" for x in XS)


def filtro_grao(segs, grao: float) -> str:
    """Grão de luma estilo película (0–1 → noise c0s 0–20), só nos trechos de câmera/celular."""
    trechos = [s for s in segs if not e_tela(s)]
    if grao <= 0 or not trechos:
        return ""
    quando = "+".join(f"between(t,{s['ini']:.3f},{s['fim']:.3f})" for s in trechos)
    return f",noise=c0s={max(1, round(grao * 20))}:c0f=t+u:enable='{quando}'"


def montar_filtro(segs, correcoes, lut: Path, intens: float, filtro_hdr: str, lut_entrada: Path | None,
                  grao: float = 0.0, formato_final: str = "yuv420p",
                  faixa_ganho: tuple[float, float] = (0.7, 1.3), faixa_video: str | None = None) -> str:
    """Filtergraph completo. `formato_final` ≠ yuv420p (ex.: gbrp16le) devolve a imagem ANTES do encode 8-bit
    (usado nos testes para provar que não há quantização a 8 bits antes do lut3d).
    `faixa_video` = color_range do vídeo de entrada ("pc" → lido como full range)."""
    N = len(segs)
    lut_f = f"lut3d=file={C.esc_filtro(lut)}:interp=tetrahedral"
    cam_f = f"lut3d=file={C.esc_filtro(lut_entrada)}:interp=tetrahedral" if lut_entrada else ""
    cab = "[0:v]" + (filtro_hdr + "," if filtro_hdr else "") + E.conversao_rgb16(faixa_video)
    cab += (f",split={N}" + "".join(f"[i{k}]" for k in range(N))) if N > 1 else "[i0]"
    linhas = [cab]
    for k, s in enumerate(segs):
        trim = f"trim=start_frame={s['f0']}" + (f":end_frame={s['f1']}" if s["f1"] is not None else "")
        partes = [trim, "setpts=PTS-STARTPTS"]
        if e_tela(s):
            linhas.append(f"[i{k}]{','.join(partes)}[v{k}]")
            continue
        if cam_f and s.get("entrada"):
            partes.append(cam_f)
        c = correcoes.get(s["grupo"])
        if c and any(abs(g - 1) > 1e-4 for g in c["ganhos"]):
            r, g, b = (curva_pts(x, *faixa_ganho) for x in c["ganhos"])
            partes.append(f"curves=r='{r}':g='{g}':b='{b}':interp=pchip")
        if intens >= 0.999:
            linhas.append(f"[i{k}]{','.join(partes + [lut_f])}[v{k}]")
        elif intens <= 0.001:
            linhas.append(f"[i{k}]{','.join(partes)}[v{k}]")
        else:
            linhas.append(f"[i{k}]{','.join(partes)},split[p{k}a][p{k}b]")
            linhas.append(f"[p{k}b]{lut_f}[l{k}]")
            linhas.append(f"[l{k}][p{k}a]blend=all_mode=normal:all_opacity={intens:.3f}[v{k}]")
    juntar = "".join(f"[v{k}]" for k in range(N)) + f"concat=n={N}:v=1:a=0,"
    if formato_final == "yuv420p":
        linhas.append(juntar + f"scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,"
                               f"{SETPARAMS_709}{filtro_grao(segs, grao)}[vout]")
    else:
        linhas.append(juntar + f"format={formato_final}[vout]")
    return ";\n".join(linhas)


def escolher_tempos(segs: list[dict], n: int = 3) -> list[tuple[float, dict]]:
    grad = [s for s in segs if not e_tela(s)]
    if not grad:
        return []
    cands = [((s["ini"] + s["fim"]) / 2, s) for s in grad]
    if len(cands) < n:
        cands += [(s["ini"] + f * (s["fim"] - s["ini"]), s) for s in grad for f in (0.2, 0.8)]
    cands.sort(key=lambda c: c[0])
    idx = np.unique(np.linspace(0, len(cands) - 1, n).round().astype(int))
    return [cands[i] for i in idx]


# ───────────────────────── medir + renderizar (corte e extras) ─────────────────────────

def graduar(video: Path, saida: Path, segs: list[dict], lut: Path, lut_ent: Path | None, alvo: dict | None,
            a: argparse.Namespace, filtro_txt: Path, faixa: tuple[float, float]) -> dict:
    """Mede cada grupo (take), monta o filtergraph e renderiza `video` → `saida`. Serve ao corte e aos extras."""
    info = C.probe(video)
    sv = C.stream_video(info)
    fps = C.fps_de(sv)
    trc = E.detectar_hdr(sv)
    filtro_hdr = E.filtro_hdr_para_sdr(trc) if trc else ""
    if trc:
        print(f"⚠ {video.name} ainda está em HDR ({trc}) → tone-map para SDR bt709 antes da cor")
    faixa_video = (sv.get("color_range") or "tv").lower()
    if lut_ent and any(s.get("entrada") for s in segs) and faixa_video == "pc":
        print(f"• {video.name} em full range: V-Log lido como full (Lumix 0–1023)")
    pre_ent = ",".join(x for x in [filtro_hdr, E.filtro_camera(conversao=True, faixa=faixa_video)] if x) \
        if lut_ent else ""

    correcoes: dict[str, dict] = {}
    medicoes: dict[str, dict] = {}
    if getattr(a, "ganhos_json", None):
        # ganhos FIXOS por fonte (ex.: scripts/cor_wb_folha.py: balanço de branco da folha + casamento mínimo):
        # substituem a primária automática (que mira o alvo_primaria da LUT, não um neutro medido)
        gj = C.ler_json(C.resolver(a.ganhos_json))["fontes"]
        for s in segs:
            if e_tela(s):
                continue
            g = gj.get(str(s["fonte"]))
            if g is None:
                raise SystemExit(f"--ganhos-json sem a fonte {s['fonte']}")
            correcoes[s["grupo"]] = {"ev": g.get("ev", 0.0), "ganhos": g["ganhos"],
                                     "nota": f"ganhos fixos ({Path(a.ganhos_json).name})"}
    elif not a.sem_primaria:
        amostras, tempos = decodificar_amostras(video, filtro_hdr, info)
        amostras_e = (decodificar_amostras(video, pre_ent, info)[0]
                      if pre_ent and any(s.get("entrada") for s in segs) else None)
        grupos: dict[str, list[dict]] = {}
        for s in segs:
            if not e_tela(s):
                grupos.setdefault(s["grupo"], []).append(s)
        for gk, ss in grupos.items():
            usa = ss[0]["entrada"] and amostras_e is not None
            base = amostras_e if usa else amostras
            n_ok = min(len(base), len(tempos))
            fim = lambda x: x["fim"] if x["fim"] is not None else 1e9  # noqa: E731
            fr = [base[i] for i in range(n_ok) if any(x["ini"] <= tempos[i] < fim(x) for x in ss)]
            if not fr:
                x = ss[0]
                fr = [C.ler_frame(video, (x["ini"] + fim(x)) / 2 if x["fim"] else 0.0, 270,
                                  pre_ent if usa else filtro_hdr)]
            med = C.medir_primaria(fr)
            medicoes[gk] = {**med, "frames_medidos": len(fr)}
            correcoes[gk] = calcular_correcao(med, alvo, a.limite_ev, a.limite_wb)

    grafo = montar_filtro(segs, correcoes, lut, a.intensidade, filtro_hdr, lut_ent, a.grao, faixa_ganho=faixa,
                          faixa_video=faixa_video)
    filtro_txt.write_text(grafo + "\n")
    print(f"• a renderizar {C.rel(saida)} …")
    # fps nunca é convertido: fonte CFR (o normal: 25 fps do projeto) → -r = o PRÓPRIO fps da fonte (mesmos frames,
    # duração exata do contentor); fonte VFR → -fps_mode passthrough (mesmos timestamps, sem duplicar/descartar).
    rf = sv.get("r_frame_rate") or ""
    cfr = rf not in ("", "0/0") and rf == sv.get("avg_frame_rate")
    taxa = ["-r", rf] if cfr else ["-fps_mode", "passthrough"]
    C.run([C.FFMPEG, "-v", "error", "-y", "-i", str(video), "-/filter_complex", str(filtro_txt),
           "-map", "[vout]", "-map", "0:a?", *taxa, "-c:v", "libx264", "-preset", a.preset,
           "-crf", "16", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-colorspace", "bt709", "-color_range", "tv", "-c:a", "copy", "-movflags", "+faststart",
           str(saida)])
    so = C.stream_video(C.probe(saida))
    n_in, n_out = sv.get("nb_frames"), so.get("nb_frames")
    if n_in and n_out and abs(int(n_in) - int(n_out)) > 1:
        print(f"⚠ nº de frames mudou em {saida.name}: {n_in} → {n_out}")
    if so.get("r_frame_rate") != rf or abs(C.fps_de(so) - fps) > 0.05:
        print(f"⚠ fps mudou em {saida.name}: {rf} ({fps:g}) → {so.get('r_frame_rate')} ({C.fps_de(so):g})")
    return {"info": info, "sv": sv, "so": so, "filtro_hdr": filtro_hdr, "pre_ent": pre_ent, "trc": trc,
            "correcoes": correcoes, "medicoes": medicoes}


def linhas_ad(video: Path, saida: Path, tempos: list[tuple[float, dict]], res: dict, prefixo: str = "") -> list[dict]:
    out = []
    for t, s in tempos:
        a0 = C.ler_frame(video, t, 540, res["filtro_hdr"])
        c = res["correcoes"].get(s["grupo"], {"ev": 0, "ganhos": [1, 1, 1]})
        g = c["ganhos"]
        rot = s["fonte"] if not prefixo else ""
        out.append({"antes": a0, "meio": C.ler_frame(video, t, 540, res["pre_ent"]) if s["entrada"] and res["pre_ent"]
                    else a0, "depois": C.ler_frame(saida, t, 540), "entrada": s["entrada"],
                    "legenda": f"{prefixo}t={t:.2f}s · {rot} {s['take'] or ''}{' · V-Log' if s['entrada'] else ''} · "
                               f"{c['ev']:+.2f} EV · R×{g[0]:.3f} G×{g[1]:.3f} B×{g[2]:.3f}"})
    return out


def render_antes_depois(linhas: list[dict], titulo_depois: str, destino: Path) -> None:
    """Uma linha por frame (corte e extras; cada linha com a sua proporção)."""
    fonte, fonte_p = C.fonte_png(24), C.fonte_png(17)
    com_entrada = any(ln["entrada"] for ln in linhas)
    cols = ([("ANTES (V-Log)", "antes"), ("ENTRADA → Rec.709", "meio")] if com_entrada
            else [("ANTES", "antes")]) + [(titulo_depois, "depois")]
    cw = 405
    alts = [int(round(cw * ln["antes"].shape[0] / ln["antes"].shape[1])) for ln in linhas]
    W, H = 10 + len(cols) * (cw + 10), 50 + sum(h + 36 for h in alts)
    img = Image.new("RGB", (W, H), (22, 22, 22))
    d = ImageDraw.Draw(img)
    for j, (rot, _) in enumerate(cols):
        d.text((10 + j * (cw + 10), 12), rot, fill=(255, 255, 255), font=fonte)
    yy = 50
    for ln, ch in zip(linhas, alts):
        for j, (_, k) in enumerate(cols):
            im = Image.fromarray((np.clip(ln[k], 0, 1) * 255).astype(np.uint8)).resize((cw, ch), Image.LANCZOS)
            img.paste(im, (10 + j * (cw + 10), yy))
        cor_leg = (255, 190, 90) if ln["legenda"].startswith("EXTRA") else (190, 190, 190)
        d.text((10, yy + ch + 6), ln["legenda"], fill=cor_leg, font=fonte_p)
        yy += ch + 36
    img.save(destino)


def localizar_extra(vd: Path, eid: str, inf: dict) -> Path | None:
    cands = []
    if inf.get("arquivo"):
        cands.append(vd / inf["arquivo"])
    cands += [vd / "edicao" / "extras" / f"{eid}{ext}" for ext in (".mp4", ".mov")]
    for p in cands:
        if p.is_file() and p.suffix.lower() in C.EXT_VIDEO and not p.stem.endswith("-cor"):
            return p
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description="[V-Log→709] + primária por take + LUT da marca no corte e extras de câmera.")
    ap.add_argument("video_dir")
    ap.add_argument("--lut", default=None)
    ap.add_argument("--intensidade", type=float, default=1.0, help="0–1: mistura da LUT com a imagem")
    ap.add_argument("--sem-primaria", action="store_true", help="não fazer a correção automática por take")
    ap.add_argument("--sem-entrada", action="store_true",
                    help="não aplicar a LUT de entrada V-Log→709 (só se a ingestão já a aplicou)")
    ap.add_argument("--limite-ev", type=float, default=MAX_STOPS,
                    help=f"exposição máxima corrigida por take, em stops (padrão ±{MAX_STOPS})")
    ap.add_argument("--limite-wb", type=float, default=MAX_CANAL,
                    help=f"ganho máximo por canal no balanço de branco, fração (padrão {MAX_CANAL} = ±8%%)")
    ap.add_argument("--ganhos-json", default=None,
                    help="JSON {fontes:{<fonte>:{ganhos:[r,g,b],ev}}} com ganhos fixos por fonte (substitui a primária automática)")
    ap.add_argument("--preset", default="medium")
    ap.add_argument("--grao", type=float, default=0.0,
                    help="0–1: grão fino de película só na câmera/celular (0.2–0.4 recomendado; 0 = sem)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sem-extras", action="store_true", help="só o corte; não mexe nas cenas extras")
    g.add_argument("--so-extras", action="store_true", help="só as cenas extras de câmera; não re-renderiza o corte")
    a = ap.parse_args()
    if not 0 <= a.limite_ev <= 2 or not 0 <= a.limite_wb <= 0.3:
        raise SystemExit("--limite-ev deve estar entre 0 e 2 e --limite-wb entre 0 e 0.3")

    vd = C.resolver(a.video_dir)
    corte = vd / "edicao" / "corte.mp4"
    if not a.so_extras and not corte.exists():
        raise SystemExit(f"Não encontrei {corte}")
    out_dir = vd / "edicao" / "cor"
    out_dir.mkdir(parents=True, exist_ok=True)
    saida = out_dir / "corte-cor.mp4"
    lut = escolher_lut(a.lut)
    meta_lut = C.ler_json(lut.with_suffix(".json")) if lut.with_suffix(".json").exists() else {}
    alvo = meta_lut.get("alvo_primaria")
    edl_p = vd / "edicao" / "edl.json"
    edl = C.ler_json(edl_p) if edl_p.exists() else None
    fontes = E.carregar_fontes(vd)
    extras_json = E.carregar_extras(vd)
    faixa = limites_ganho(a.limite_ev, a.limite_wb)

    # ── plano: segmentos do corte + extras de câmera ──
    segs: list[dict] = []
    if not a.so_extras:
        info_c = C.probe(corte)
        sv_c = C.stream_video(info_c)
        segs = carregar_segmentos(edl, C.fps_de(sv_c), C.duracao_de(info_c))
        anotar_segmentos(segs, fontes, usar_entrada=not a.sem_entrada)
        print(f"• {corte.relative_to(vd)}: {sv_c['width']}×{sv_c['height']} {sv_c.get('pix_fmt', '?')} @ "
              f"{C.fps_de(sv_c):g} fps, {C.duracao_de(info_c):.2f}s, {len(segs)} segmentos")
    extras, extras_sem_cor = [], []
    if not a.sem_extras:
        for eid, inf in sorted(extras_json.items()):
            tipo = str((inf or {}).get("tipo") or "").lower()
            if tipo != "camera":
                extras_sem_cor.append({"id": eid, "tipo": tipo or "?"})
                continue
            perfil = E.perfil_da_fonte(eid, extras_json, "camera")
            arq = localizar_extra(vd, eid, inf or {})
            if arq is None:
                print(f"⚠ extra {eid} (camera) sem arquivo em edicao/extras/ → ignorado (faltando)")
                extras_sem_cor.append({"id": eid, "tipo": tipo, "faltando": True})
                continue
            extras.append({"id": eid, "arquivo": arq, "perfil": perfil,
                           "entrada": bool(perfil == "vlog" and not a.sem_entrada)})
    print(f"• perfis: {'edicao/fontes.json' if fontes or extras_json else 'sem fontes.json'} "
          f"(câmera sem perfil → CAMERA_PERFIL={E.perfil_camera_padrao()})")
    if extras or extras_sem_cor:
        print(f"• extras de câmera a graduar: {', '.join(x['id'] for x in extras) or 'nenhum'}"
              + (f" · sem cor: {', '.join(x['id'] + ' (' + x['tipo'] + ')' for x in extras_sem_cor)}"
                 if extras_sem_cor else ""))
    lut_ent, desc_ent = None, ""
    if any(s["entrada"] for s in segs) or any(x["entrada"] for x in extras):
        lut_ent, desc_ent = E.exigir_lut_vlog()
        print(f"• entrada V-Log→Rec.709: {desc_ent}")
    elif a.sem_entrada and (any(e_camera(s) and s["perfil"] == "vlog" for s in segs)
                            or any(x["perfil"] == "vlog" for x in extras)):
        print("⚠ --sem-entrada: V-Log vai direto para a primária/LUT (só se já vier em Rec.709!)")
    print(f"• LUT: {C.rel(lut)} (intensidade {a.intensidade})")
    if (a.limite_ev, a.limite_wb) != (MAX_STOPS, MAX_CANAL):
        print(f"• limites da primária: ±{a.limite_ev} EV, ±{a.limite_wb * 100:g}%/canal")
    if a.grao > 0:
        print(f"• grão de película: {a.grao} (só câmera/celular)")

    linhas: list[dict] = []
    relatorio: dict = {}
    if a.so_extras and (out_dir / "correcoes.json").exists():
        relatorio = C.ler_json(out_dir / "correcoes.json")
    scopes_frames: tuple[list, list] | None = None

    # ── corte ──
    if not a.so_extras:
        res = graduar(corte, saida, segs, lut, lut_ent, alvo, a, out_dir / "filtro.txt", faixa)
        lc = linhas_ad(corte, saida, escolher_tempos(segs), res)
        linhas += lc
        if lc:
            scopes_frames = ([ln["meio"] for ln in lc], [ln["depois"] for ln in lc])
        sv, so = res["sv"], res["so"]
        relatorio = {
            "criado_em": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "entrada": C.rel(corte), "saida": C.rel(saida), "lut": C.rel(lut), "intensidade": a.intensidade,
            "alvo_primaria": alvo, "hdr_para_sdr": bool(res["trc"]),
            "lut_entrada_camera": any(s["entrada"] for s in segs), "lut_entrada": C.rel(lut_ent) if lut_ent else None,
            "lut_entrada_desc": desc_ent or None, "fontes_json": bool(fontes),
            "primaria": not a.sem_primaria, "limites_primaria": {"ev": a.limite_ev, "wb": a.limite_wb},
            "grao": a.grao,
            "formato_entrada": {"pix_fmt": sv.get("pix_fmt"), "fps": sv.get("r_frame_rate"),
                                "color_range": sv.get("color_range")},
            "segmentos": [{"n": s["n"], "fonte": s["fonte"], "take": s["take"], "linha": s["linha"],
                           "tipo": s["tipo"], "perfil": s["perfil"], "entrada_vlog": s["entrada"],
                           "saida_inicio": s["ini"], "saida_fim": s["fim"], "frames": [s["f0"], s["f1"]],
                           "graduado": not e_tela(s), "medicao": res["medicoes"].get(s["grupo"]),
                           "correcao": res["correcoes"].get(s["grupo"])} for s in segs],
        }
        print(f"✓ {C.rel(saida)}  ({so['width']}×{so['height']}, {so.get('nb_frames', '?')} frames, "
              f"{so.get('r_frame_rate')} fps)")
        for s in relatorio["segmentos"]:
            c = s["correcao"]
            tag = " V-Log→709 +" if s["entrada_vlog"] else ""
            if not s["graduado"]:
                print(f"  seg {s['n']:>2} {s['fonte']:<10} tela → sem cor")
            elif c:
                print(f"  seg {s['n']:>2} {s['fonte']:<10}{tag} {c['ev']:+.2f} EV  ganhos RGB {c['ganhos']}"
                      + (f"  ({c['nota']})" if c.get("nota") else ""))
            else:
                print(f"  seg {s['n']:>2} {s['fonte']:<10}{tag} só LUT")

    # ── cenas extras de câmera (mesma entrada + primária para o mesmo alvo + mesma LUT + mesmo grão) ──
    rel_extras = []
    for x in extras:
        info_x = C.probe(x["arquivo"])
        dur = C.duracao_de(info_x)
        sx = [{"n": 1, "fonte": x["id"], "take": "extra", "linha": None, "ini": 0.0, "fim": dur, "f0": 0,
               "f1": None, "grupo": f"{x['id']}|extra", "tipo": "camera", "perfil": x["perfil"],
               "entrada": x["entrada"]}]
        destino = x["arquivo"].with_name(f"{x['id']}-cor.mp4")
        rx = graduar(x["arquivo"], destino, sx, lut, lut_ent, alvo, a, out_dir / f"filtro-{x['id']}.txt", faixa)
        c = rx["correcoes"].get(sx[0]["grupo"])
        linhas += linhas_ad(x["arquivo"], destino, [(dur / 2, sx[0])], rx, prefixo=f"EXTRA {x['id']} · ")
        rel_extras.append({"id": x["id"], "tipo": "camera", "perfil": x["perfil"], "entrada_vlog": x["entrada"],
                           "arquivo": C.rel(x["arquivo"]), "saida": C.rel(destino),
                           "frames": [rx["sv"].get("nb_frames"), rx["so"].get("nb_frames")],
                           "fps": rx["so"].get("r_frame_rate"), "medicao": rx["medicoes"].get(sx[0]["grupo"]),
                           "correcao": c})
        print(f"✓ extra {x['id']}: {C.rel(destino)} ({rx['so'].get('nb_frames', '?')} frames, "
              f"{rx['so'].get('r_frame_rate')} fps)" + (f"  {c['ev']:+.2f} EV ganhos {c['ganhos']}" if c else ""))
    for x in extras_sem_cor:
        if not x.get("faltando"):
            print(f"  extra {x['id']} ({x['tipo']}) → sem cor (só tipo camera é graduado)")
    if scopes_frames is None and linhas:
        scopes_frames = ([ln["meio"] for ln in linhas], [ln["depois"] for ln in linhas])

    # ── antes/depois + scopes + relatório ──
    if linhas:
        # --so-extras não apaga a vista do corte: grava antes-depois-extras.png / scopes-extras.png
        suf = "-extras" if a.so_extras else ""
        ad, sc = out_dir / f"antes-depois{suf}.png", out_dir / f"scopes{suf}.png"
        render_antes_depois(linhas, f"DEPOIS ({lut.stem}, {a.intensidade:g})", ad)
        com_entrada = any(ln["entrada"] for ln in linhas)
        with tempfile.TemporaryDirectory() as td:
            ma = SC.mosaico(scopes_frames[0], Path(td) / "antes.png")
            md = SC.mosaico(scopes_frames[1], Path(td) / "depois.png")
            SC.montar([("ANTES (após V-Log→709)" if com_entrada else "ANTES", ma), ("DEPOIS", md)],
                      sc, titulo=f"{vd.name} — scopes de {len(scopes_frames[0])} frames")
        print(f"✓ {C.rel(ad)}\n✓ {C.rel(sc)}")
    if not a.sem_extras:
        relatorio["extras"] = rel_extras
        relatorio["extras_sem_cor"] = extras_sem_cor
        relatorio["extras_atualizado_em"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    C.escrever_json(out_dir / "correcoes.json", relatorio)


if __name__ == "__main__":
    main()
