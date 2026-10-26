"""Cria a LUT fixa da marca (korvu-look-<versao>.cube) a partir de referências de cor.

Uso (da raiz do projeto):
  uv run python .claude/skills/color-grading/scripts/criar_lut.py \
      --referencias 00-marca/cor/referencias --amostra <video_ou_pasta_de_frames> --versao v1 \
      [--metodo mkl|hm-mvgd-hm|hm-mkl-hm|reinhard] [--intensidade 0.8] [--proteger-pele 0.7] \
      [--tipo celular|camera] [--perfil vlog|sdr] [--frames 20] [--forcar]

A amostra pode ser o arquivo CRU da câmera (ex.: brutos/camera-00-cor.mov: 4K, rodado, V-Log 10-bit):
a rotação é respeitada, o frame é reduzido no YUV original e a LUT de entrada V-Log→709 (a mesma do
aplicar_cor) é aplicada a 16 bits antes da análise. Perfil: --perfil > fontes.json > CAMERA_PERFIL (vlog).

Como funciona:
  1. Extrai ~20 frames da amostra (material típico do Carlos, já com a transformação de entrada).
  2. Ajusta a transferência amostra → referência com `color_matcher` (estatística das imagens).
  3. Aplica o MESMO modelo (parâmetros) a uma grade identidade 33³ → LUT.
     - mkl       : mapa linear 3×3 + offset (Monge–Kantorovich), aplicado diretamente.
     - hm-*-hm   : curva 1D por canal (quantis) → MKL → curva 1D por canal.
     - reinhard  : médias/desvios no espaço lαβ.
  4. Proteção de pele no domínio da grade (matiz volta para a original; luminância mantém a mudança).
  5. Intensidade global (mistura com identidade) e clamp 0–1.
Saídas: 00-marca/cor/luts/korvu-look-<v>.cube + .json, 00-marca/cor/analises/<v>-antes-depois.png
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter1d

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _comum as C  # noqa: E402
import entrada as E  # noqa: E402

METODOS = ("mkl", "hm-mvgd-hm", "hm-mkl-hm", "reinhard")
TAMANHO = 33
GRADE = np.linspace(0.0, 1.0, 256)
PIX_POR_IMAGEM = 40_000


# ───────────────────────── carregar ─────────────────────────

def carregar_referencias(pasta: Path) -> list[tuple[str, np.ndarray]]:
    if not pasta.is_dir():
        raise SystemExit(f"Pasta de referências não existe: {pasta}")
    refs = []
    for p in sorted(pasta.iterdir()):
        ext = p.suffix.lower()
        if p.name.startswith("."):
            continue
        if ext in C.EXT_IMG:
            refs.append((p.name, C.ler_imagem(p, 720)))
        elif ext in C.EXT_VIDEO:
            dur = C.duracao_de(C.probe(p))
            for k in range(5):
                t = dur * (0.1 + 0.8 * k / 4)
                refs.append((f"{p.name}@{t:.1f}s", C.ler_frame(p, t, 540)))
    if not refs:
        raise SystemExit(f"Nenhuma imagem/vídeo de referência em {pasta}")
    return refs


def carregar_amostra(p: Path, n: int, tipo: str | None,
                     perfil: str | None = None) -> tuple[list[np.ndarray], str, list[str]]:
    if p.is_dir():
        imgs = [x for x in sorted(p.iterdir()) if x.suffix.lower() in C.EXT_IMG and not x.name.startswith(".")]
        if not imgs:
            raise SystemExit(f"Pasta de amostra sem imagens: {p}")
        idx = np.unique(np.linspace(0, len(imgs) - 1, min(n, len(imgs))).round().astype(int))
        return ([C.ler_imagem(imgs[i], 720) for i in idx],
                "pasta de frames (assumidos já em SDR Rec.709; sem transformação de entrada)",
                [imgs[i].name for i in idx])
    if not p.exists():
        raise SystemExit(f"Amostra não encontrada: {p}")
    info = C.probe(p)
    filtro, desc = E.filtro_entrada(p, tipo, info, perfil=perfil)
    dur = C.duracao_de(info)
    tempos = [dur * (0.05 + 0.9 * (k + 0.5) / n) for k in range(n)]
    return [C.ler_frame(p, t, 540, filtro) for t in tempos], desc, [f"{t:.2f}s" for t in tempos]


def pool(frames: list[np.ndarray], rng: np.random.Generator) -> np.ndarray:
    """Mesmo nº de pixels por imagem (imagens grandes não dominam)."""
    partes = []
    for f in frames:
        px = f.reshape(-1, 3).astype(np.float64)
        if len(px) > PIX_POR_IMAGEM:
            px = px[rng.choice(len(px), PIX_POR_IMAGEM, replace=False)]
        partes.append(px)
    return np.concatenate(partes)


# ───────────────────────── modelos de transferência ─────────────────────────

def ajustar_mkl(S: np.ndarray, R: np.ndarray) -> dict:
    from color_matcher import ColorMatcher

    cm = ColorMatcher(src=S[:, None, :].copy(), ref=R[:, None, :].copy(), method="mkl")
    res = np.real(cm.transfer())[:, 0, :]
    p = {"M": np.real(cm.transfer_mat), "mu_s": np.real(cm.mu_r[:, 0]), "mu_r": np.real(cm.mu_z[:, 0])}
    # o modelo paramétrico tem de reproduzir exatamente a transferência da biblioteca
    err = float(np.abs(aplicar_mkl(S, p) - res).max())
    if err > 1e-6:
        raise RuntimeError(f"Modelo MKL não reproduz color_matcher (erro {err:.2e})")
    return p


def aplicar_mkl(x: np.ndarray, p: dict) -> np.ndarray:
    return (x - p["mu_s"]) @ np.asarray(p["M"]).T + p["mu_r"]


def ajustar_curvas(S: np.ndarray, R: np.ndarray) -> np.ndarray:
    """Curva 1D por canal (casamento de histograma por quantis), suavizada e monótona."""
    q = np.linspace(0.001, 0.999, 999)
    curvas = []
    for c in range(3):
        xs = np.quantile(S[:, c], q)
        ys = np.quantile(R[:, c], q)
        xs = np.maximum.accumulate(xs) + np.arange(len(xs)) * 1e-7
        x_ext = np.concatenate([[min(0.0, xs[0] - 1e-6)], xs, [max(1.0, xs[-1] + 1e-6)]])
        y_ext = np.concatenate([[max(0.0, ys[0] - xs[0])], ys, [min(1.0, ys[-1] + (1 - xs[-1]))]])
        cv = np.interp(GRADE, x_ext, y_ext)
        cv = gaussian_filter1d(cv, 4, mode="nearest")
        curvas.append(np.maximum.accumulate(np.clip(cv, 0, 1)))
    return np.array(curvas)


def aplicar_curvas(x: np.ndarray, curvas: np.ndarray) -> np.ndarray:
    return np.stack([np.interp(x[..., c], GRADE, curvas[c]) for c in range(3)], -1)


_B = np.array([[1 / np.sqrt(3), 0, 0], [0, 1 / np.sqrt(6), 0], [0, 0, 1 / np.sqrt(2)]])
_CM = np.array([[1, 1, 1], [1, 1, -2], [1, -1, 0]])


def _lab(px):
    import color_matcher.reinhard_matcher as RM

    lms = np.log10(np.maximum(px, 1 / 255) @ RM.LMS_MAT.T)
    return lms @ (_B @ _CM).T


def _rgb_de_lab(lab):
    import color_matcher.reinhard_matcher as RM

    lms = 10 ** np.clip(lab @ (_CM.T @ _B).T, -6, 1)
    return lms @ RM.LMS_MAT_INV.T


def ajustar_reinhard(S, R) -> dict:
    ls, lr = _lab(S), _lab(R)
    return {"media_s": ls.mean(0), "std_s": ls.std(0), "media_r": lr.mean(0), "std_r": lr.std(0)}


def aplicar_reinhard(x, p):
    lab = (_lab(x) - p["media_s"]) * (p["std_r"] / np.maximum(p["std_s"], 1e-6)) + p["media_r"]
    return _rgb_de_lab(lab)


def ajustar(metodo: str, S: np.ndarray, R: np.ndarray) -> dict:
    if metodo == "mkl":
        return {"metodo": "mkl", "mkl": ajustar_mkl(S, R)}
    if metodo == "reinhard":
        return {"metodo": "reinhard", "reinhard": ajustar_reinhard(S, R)}
    # hm-mvgd-hm / hm-mkl-hm: estágio central sempre MKL (a solução analítica MVGD exige
    # correspondência pixel a pixel entre imagens, o que não existe entre amostra e referência).
    c1 = ajustar_curvas(S, R)
    S1 = aplicar_curvas(S, c1)
    mk = ajustar_mkl(S1, R)
    S2 = np.clip(aplicar_mkl(S1, mk), 0, 1)
    c3 = ajustar_curvas(S2, R)
    return {"metodo": metodo, "curva1": c1, "mkl": mk, "curva3": c3, "estagio_central": "mkl"}


def aplicar_modelo(x: np.ndarray, m: dict) -> np.ndarray:
    if m["metodo"] == "mkl":
        return aplicar_mkl(x, m["mkl"])
    if m["metodo"] == "reinhard":
        return aplicar_reinhard(x, m["reinhard"])
    y = aplicar_curvas(x, m["curva1"])
    y = np.clip(aplicar_mkl(y, m["mkl"]), 0, 1)
    return aplicar_curvas(y, m["curva3"])


# ───────────────────────── pele + LUT ─────────────────────────

def proteger_pele(x: np.ndarray, y: np.ndarray, fator: float) -> np.ndarray:
    """Em tons de pele (detetados na cor de ENTRADA), a matiz volta para a original na proporção
    `fator` e a mudança de saturação é reduzida a metade disso; a luminância (Y) de saída é mantida."""
    if fator <= 0:
        return y
    w = C.peso_pele(np.clip(x, 0, 1)) * fator
    _, cbx, crx = C.ycbcr601(x)
    yy, cby, cry = C.ycbcr601(y)
    hx, hy = np.arctan2(crx - 0.5, cbx - 0.5), np.arctan2(cry - 0.5, cby - 0.5)
    mx, my = np.hypot(cbx - 0.5, crx - 0.5), np.hypot(cby - 0.5, cry - 0.5)
    dh = (hx - hy + np.pi) % (2 * np.pi) - np.pi
    h = hy + dh * w
    m = my + (mx - my) * w * 0.5
    return C.rgb_de_ycbcr601(yy, 0.5 + m * np.cos(h), 0.5 + m * np.sin(h))


def construir_lut(modelo: dict, intensidade: float, pele: float, n: int = TAMANHO) -> np.ndarray:
    x = C.lattice(n).reshape(-1, 3)
    y = aplicar_modelo(x, modelo)
    y = proteger_pele(x, y, pele)
    y = x + (y - x) * intensidade
    return np.clip(y, 0, 1).reshape(n, n, n, 3)


# ───────────────────────── antes/depois ─────────────────────────

def _feat(a: np.ndarray) -> np.ndarray:
    import cv2

    lab = cv2.cvtColor(np.ascontiguousarray(a, dtype=np.float32), cv2.COLOR_RGB2Lab).reshape(-1, 3)
    return np.concatenate([lab.mean(0), lab.std(0)])


def _cover(a: np.ndarray, w: int, h: int) -> Image.Image:
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    s = max(w / im.width, h / im.height)
    im = im.resize((max(w, round(im.width * s)), max(h, round(im.height * s))), Image.LANCZOS)
    x0, y0 = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x0, y0, x0 + w, y0 + h))


def render_antes_depois(frames: list[np.ndarray], rotulos: list[str], cube: Path,
                        refs: list[tuple[str, np.ndarray]], saida: Path, versao: str) -> Path:
    idx = np.unique(np.linspace(0, len(frames) - 1, min(4, len(frames))).round().astype(int))
    fh, fw = frames[0].shape[:2]
    cw = 300
    ch = int(round(cw * fh / fw))
    fonte, fonte_p = C.fonte_png(22), C.fonte_png(16)
    feats = [(nome, _feat(r), r) for nome, r in refs]
    topo, esq, gap = 50, 10, 8
    W = esq + 3 * (cw + gap)
    H = topo + len(idx) * (ch + 34)
    out = Image.new("RGB", (W, H), (22, 22, 22))
    d = ImageDraw.Draw(out)
    for j, t in enumerate(["original (amostra)", f"com LUT {versao}", "referência mais próxima"]):
        d.text((esq + j * (cw + gap), 14), t, fill=(255, 255, 255), font=fonte)
    with tempfile.TemporaryDirectory() as td:
        for row, i in enumerate(idx):
            a_png, b_png = Path(td) / f"a{i}.png", Path(td) / f"b{i}.png"
            C.salvar_png(frames[i], a_png)
            # aplica com o ffmpeg (valida que o .cube é lido como no render real)
            C.run([C.FFMPEG, "-v", "error", "-y", "-i", str(a_png), "-vf",
                   f"lut3d=file={C.esc_filtro(cube)}:interp=tetrahedral", "-frames:v", "1", str(b_png)])
            g = np.asarray(Image.open(b_png).convert("RGB")).astype(np.float32) / 255
            fg = _feat(g)
            nome, _, ref = min(feats, key=lambda f: float(np.linalg.norm(f[1] - fg)))
            y = topo + row * (ch + 34)
            for j, img in enumerate([frames[i], g, ref]):
                out.paste(_cover(img, cw, ch), (esq + j * (cw + gap), y))
            d.text((esq, y + ch + 6), f"amostra {rotulos[i]}", fill=(190, 190, 190), font=fonte_p)
            d.text((esq + 2 * (cw + gap), y + ch + 6), nome[:34], fill=(190, 190, 190), font=fonte_p)
    saida.parent.mkdir(parents=True, exist_ok=True)
    out.save(saida)
    return saida


# ───────────────────────── main ─────────────────────────

def _json_ok(v):
    if isinstance(v, np.ndarray):
        return np.round(v, 6).tolist()
    if isinstance(v, dict):
        return {k: _json_ok(x) for k, x in v.items()}
    if isinstance(v, (np.floating,)):
        return float(v)
    return v


def _sha1(p: Path) -> str:
    return hashlib.sha1(p.read_bytes()).hexdigest()[:12] if p.is_file() else ""


def main() -> None:
    ap = argparse.ArgumentParser(description="Cria a LUT da marca a partir de referências de cor.")
    ap.add_argument("--referencias", default="00-marca/cor/referencias")
    ap.add_argument("--amostra", required=True, help="vídeo típico do Carlos ou pasta de frames")
    ap.add_argument("--versao", required=True, help="ex.: v1")
    ap.add_argument("--metodo", default="mkl", choices=METODOS)
    ap.add_argument("--intensidade", type=float, default=0.8)
    ap.add_argument("--proteger-pele", type=float, default=0.7)
    ap.add_argument("--tipo", choices=["celular", "camera"], default=None,
                    help="tipo da amostra (padrão: pelo nome do arquivo)")
    ap.add_argument("--perfil", choices=["vlog", "sdr"], default=None,
                    help="perfil da câmera (padrão: fontes.json do vídeo, senão CAMERA_PERFIL=vlog)")
    ap.add_argument("--frames", type=int, default=20)
    ap.add_argument("--forcar", action="store_true", help="sobrescreve versão existente")
    a = ap.parse_args()

    if not re.fullmatch(r"v\d+[a-z0-9-]*", a.versao):
        raise SystemExit("--versao deve ser do tipo v1, v2, v3b…")
    if not 0 <= a.intensidade <= 1 or not 0 <= a.proteger_pele <= 1:
        raise SystemExit("--intensidade e --proteger-pele devem estar entre 0 e 1")

    nome = f"korvu-look-{a.versao}"
    cube = C.LUTS_DIR / f"{nome}.cube"
    meta = C.LUTS_DIR / f"{nome}.json"
    png = C.ANALISES_DIR / f"{a.versao}-antes-depois.png"
    if cube.exists() and not a.forcar:
        raise SystemExit(f"{C.rel(cube)} já existe. Crie outra versão (ex.: v2) ou use --forcar.")

    pasta_refs = C.resolver(a.referencias)
    amostra = C.resolver(a.amostra)
    print(f"• referências: {C.rel(pasta_refs)}")
    refs = carregar_referencias(pasta_refs)
    print(f"  {len(refs)} imagem(ns)/frame(s)")
    print(f"• amostra: {C.rel(amostra)}")
    frames, desc_entrada, rotulos = carregar_amostra(amostra, a.frames, a.tipo, a.perfil)
    print(f"  {len(frames)} frames · {desc_entrada}")

    rng = np.random.default_rng(0)
    S, R = pool(frames, rng), pool([r for _, r in refs], rng)
    n = min(len(S), len(R))
    S, R = S[rng.permutation(len(S))[:n]], R[rng.permutation(len(R))[:n]]
    print(f"• ajustando transferência ({a.metodo}) com {n} pixels de cada lado")
    modelo = ajustar(a.metodo, S, R)
    lut = construir_lut(modelo, a.intensidade, a.proteger_pele)

    # sanidade: rampa de cinza deve continuar monótona
    cinza = np.array([lut[i, i, i] @ C.LUMA709 for i in range(TAMANHO)])
    avisos = []
    if np.any(np.diff(cinza) < -1e-4):
        avisos.append("rampa de cinza não monótona (LUT pode inverter tons) — reduza intensidade ou mude método")

    alvo = C.medir_primaria(frames)
    com_lut = [C.aplicar_lut_np(f, lut) for f in frames]
    est = {"referencia": C.estatisticas([r for _, r in refs]), "amostra": C.estatisticas(frames),
           "amostra_com_lut": C.estatisticas(com_lut)}
    if est["amostra_com_lut"]["pretos_esmagados_pct"] > 2.0:
        avisos.append("mais de 2% de pretos esmagados na amostra com LUT")
    if est["amostra_com_lut"]["brancos_estourados_pct"] > 2.0:
        avisos.append("mais de 2% de brancos estourados na amostra com LUT")

    comentarios = [f"Korvu look {a.versao} — {a.metodo}, intensidade {a.intensidade}, pele {a.proteger_pele}",
                   "Entrada/saida: Rec.709 (gamma 2.4) full range 0-1. Aplicar com interp=tetrahedral.",
                   f"Criada em {dt.datetime.now().astimezone().isoformat(timespec='seconds')}"]
    C.escrever_cube(cube, lut, nome, comentarios)

    # o ffmpeg tem de conseguir ler a LUT
    C.run([C.FFMPEG, "-v", "error", "-f", "lavfi", "-i", "testsrc2=s=128x128:d=0.1",
           "-vf", f"lut3d=file={C.esc_filtro(cube)}:interp=tetrahedral", "-f", "null", "-"])

    render_antes_depois(frames, rotulos, cube, refs, png, a.versao)

    params = {k: v for k, v in modelo.items() if k != "metodo"}
    C.escrever_json(meta, _json_ok({
        "nome": nome,
        "versao": a.versao,
        "criado_em": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "aprovada": False,
        "aprovada_em": None,
        "cube": C.rel(cube),
        "tamanho": TAMANHO,
        "interp": "tetrahedral",
        "espaco": "Rec.709 / gamma 2.4 (SDR), valores 0–1",
        "metodo": a.metodo,
        "intensidade": a.intensidade,
        "proteger_pele": a.proteger_pele,
        "referencias": [{"arquivo": x, "sha1": _sha1(pasta_refs / x.split("@")[0])} for x, _ in refs],
        "amostra": {"arquivo": C.rel(amostra), "transformacao_entrada": desc_entrada, "frames": rotulos,
                    "dimensoes_frame": [int(frames[0].shape[1]), int(frames[0].shape[0])]},
        "dominio_entrada": ("Rec.709 depois da LUT de entrada (câmera V-Log passa primeiro por V-Log→709; "
                            "o aplicar_cor aplica a mesma entrada antes desta LUT)"),
        "alvo_primaria": {**alvo, "nota": ("domínio de entrada da LUT: é a exposição/neutro que a LUT leva "
                                           "até à média da referência. aplicar_cor.py ajusta cada take para cá.")},
        "estatisticas": est,
        "cinza_saida": {"0%": round(float(cinza[0]), 4), "18%": round(float(lut[6, 6, 6] @ C.LUMA709), 4),
                        "50%": round(float(cinza[16]), 4), "100%": round(float(cinza[-1]), 4)},
        "avisos": avisos,
        "antes_depois": C.rel(png),
        "parametros": params,
    }))

    print(f"✓ LUT      → {C.rel(cube)}")
    print(f"✓ metadados→ {C.rel(meta)}")
    print(f"✓ antes/depois → {C.rel(png)}")
    r, s, c = est["referencia"], est["amostra"], est["amostra_com_lut"]
    print("               luma  contraste  saturação")
    for rot, e in [("referência", r), ("amostra", s), ("amostra+LUT", c)]:
        print(f"  {rot:<12} {e['luma_media']:.3f}   {e['contraste_std']:.3f}     {e['saturacao_media']:.3f}")
    for av in avisos:
        print(f"⚠ {av}")


if __name__ == "__main__":
    main()
