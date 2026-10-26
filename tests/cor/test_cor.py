"""Teste sintético do skill color-grading (não toca em 00-marca/ real: usa CONTENT_AI_ROOT).

Uso (da raiz do projeto):  uv run python tests/cor/test_cor.py
Saída em tests/cor/_saida/ (root falso com 00-marca/cor e videos/teste-cor/).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

AQUI = Path(__file__).resolve().parent
PROJETO = AQUI.parent.parent
SCRIPTS = PROJETO / ".claude" / "skills" / "color-grading" / "scripts"
SAIDA = AQUI / "_saida"
ROOT = SAIDA / "root"
os.environ["CONTENT_AI_ROOT"] = str(ROOT)
sys.path.insert(0, str(SCRIPTS))
import _comum as C  # noqa: E402
import criar_lut as CL  # noqa: E402
import entrada as E  # noqa: E402

W, H, FPS = 1080, 1920, 30
LUMA = C.LUMA709
RESULTADOS: list[tuple[str, bool, str]] = []


def ok(nome: str, cond: bool, detalhe: str = "") -> None:
    RESULTADOS.append((nome, bool(cond), detalhe))
    print(f"  [{'PASS' if cond else 'FAIL'}] {nome}" + (f" — {detalhe}" if detalhe else ""))


# ───────────────────────── geração de material sintético ─────────────────────────

def desktop(nome: str) -> np.ndarray:
    cache = SAIDA / "_cache"
    cache.mkdir(parents=True, exist_ok=True)
    jpg = cache / f"{nome}.jpg"
    if not jpg.exists():
        for base in ["/System/Library/Desktop Pictures", "/System/Library/Desktop Pictures/.thumbnails"]:
            p = Path(base) / f"{nome}.heic"
            if p.exists():
                subprocess.run(["sips", "-s", "format", "jpeg", "-Z", "2000", str(p), "--out", str(jpg)],
                               capture_output=True)
                break
    if jpg.exists():
        im = Image.open(jpg).convert("RGB")
    else:  # fallback: gradiente
        g = np.linspace(0, 1, 512)[None, :, None] * np.array([0.5, 0.7, 0.9])
        im = Image.fromarray((np.repeat(g, 512, 0) * 255).astype(np.uint8))
    s = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    x0, y0 = (im.width - W) // 2, (im.height - H) // 2
    return np.asarray(im.crop((x0, y0, x0 + W, y0 + H))).astype(np.float32) / 255


_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)


def cena(fundo: np.ndarray, dx: int = 0) -> np.ndarray:
    img = np.roll(fundo, dx, axis=1) * 0.85
    img[1150:, 170:910] = [0.10, 0.18, 0.36]  # camisa
    img[1020:1160, 470:610] = np.array([0.80, 0.58, 0.47]) * 0.8  # pescoço
    e = ((_xx - 540) / 230) ** 2 + ((_yy - 760) / 300) ** 2
    rosto = e < 1
    sombra = (0.70 + 0.30 * np.sqrt(np.clip(1 - e, 0, 1))) * (1 - 0.18 * (_xx - 540) / 230)
    img[rosto] = np.array([0.80, 0.58, 0.47]) * sombra[rosto][:, None]
    img[1450:1650, 60:260] = 0.46  # cartão cinza
    img[1450:1650, 260:360] = 0.92  # branco
    img[1450:1650, 360:460] = 0.035  # preto
    cores = [[0.7, 0.2, 0.2], [0.2, 0.6, 0.25], [0.2, 0.3, 0.7], [0.85, 0.75, 0.2], [0.2, 0.7, 0.75],
             [0.7, 0.25, 0.65]]
    for i, c in enumerate(cores):
        img[1700:1800, 60 + i * 160:200 + i * 160] = c
    return np.clip(img, 0, 1)


def plano(x: np.ndarray, exp: float = 1.0, cast=(0.97, 1.0, 1.03)) -> np.ndarray:
    """Look 'flat' (baixo contraste, dessaturado) com exposição e dominante de cor."""
    x = np.clip(x * exp, 0, 1)
    y = 0.10 + 0.78 * x ** 0.8
    lum = (y @ LUMA)[..., None]
    y = lum + (y - lum) * 0.75
    return np.clip(y * np.array(cast), 0, 1)


def cinematografico(x: np.ndarray) -> np.ndarray:
    """Referência: quente, contrastado, um pouco dessaturado."""
    w = np.clip(x * np.array([1.06, 1.0, 0.88]), 0, 1)
    s = w * w * (3 - 2 * w)
    y = 0.6 * s + 0.4 * w
    lum = (y @ LUMA)[..., None]
    y = lum + (y - lum) * 0.85
    return np.clip(0.02 + 0.96 * y, 0, 1)


def tela_ui() -> np.ndarray:
    img = np.full((H, W, 3), 0.96, np.float32)
    img[:180] = [0.15, 0.35, 0.85]
    for i in range(6):
        y = 260 + i * 260
        img[y:y + 200, 60:1020] = [0.99, 0.99, 0.99]
        img[y + 30:y + 50, 100:700] = 0.35
        img[y + 80:y + 95, 100:900] = 0.6
        img[y + 130:y + 175, 820:990] = [[0.1, 0.7, 0.4], [0.9, 0.3, 0.2], [0.2, 0.4, 0.9]][i % 3]
    return img


def codificar(frames, n: int, saida: Path, audio: bool = False) -> None:
    saida.parent.mkdir(parents=True, exist_ok=True)
    cmd = [C.FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-"]
    if audio:
        cmd += ["-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000"]
    cmd += ["-t", f"{n / FPS:.4f}", "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,"
            "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-colorspace", "bt709",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"]
    if audio:
        cmd += ["-c:a", "aac", "-ar", "48000", "-b:a", "128k"]
    p = subprocess.Popen(cmd + [str(saida)], stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write((np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
    p.stdin.close()
    assert p.wait() == 0, f"ffmpeg falhou a gerar {saida}"


def gerar_fixture() -> dict:
    if SAIDA.exists():
        for d in ["root", "amostra.mp4", "hdr.mp4", "hdr-sdr.mp4"]:
            p = SAIDA / d
            shutil.rmtree(p, ignore_errors=True) if p.is_dir() else p.unlink(missing_ok=True)
    refs = ROOT / "00-marca" / "cor" / "referencias"
    refs.mkdir(parents=True, exist_ok=True)
    print("• gerando referências (look quente/contrastado)…")
    for i, nome in enumerate(["Sonoma", "Big Sur Coastline"]):
        C.salvar_png(cinematografico(cena(desktop(nome))), refs / f"ref-retrato-{i + 1}.png")
    for nome in ["Big Sur Mountains", "Catalina Clouds"]:
        a = cinematografico(desktop(nome))
        Image.fromarray((a * 255).astype(np.uint8)).save(refs / f"ref-{nome.replace(' ', '-').lower()}.jpg",
                                                          quality=92)
    print("• gerando amostra plana (3 s)…")
    f1, f2 = desktop("Big Sur Road"), desktop("Big Sur Mountains")
    amostra = SAIDA / "amostra.mp4"
    codificar((plano(cena(f1 if k < 45 else f2, dx=k * 4)) for k in range(90)), 90, amostra)

    print("• gerando corte.mp4 (take escuro/frio, take claro/quente, tela)…")
    vd = ROOT / "videos" / "teste-cor"
    fundo = desktop("Sonoma")
    ui = tela_ui()

    def frames():
        for k in range(60):
            yield plano(cena(fundo, dx=k * 3), exp=0.72, cast=(0.95, 1.0, 1.07))
        for k in range(60):
            yield plano(cena(fundo, dx=180 + k * 3), exp=1.25, cast=(1.07, 1.0, 0.93))
        for k in range(45):
            yield np.roll(ui, -k * 4, axis=0)

    codificar(frames(), 165, vd / "edicao" / "corte.mp4", audio=True)
    edl = {
        "versao": 1, "slug": "teste-cor", "fps": 30, "sr": 48000, "largura": 1080, "altura": 1920,
        "aprovado": True, "aprovado_em": "2026-09-15T17:00:00+01:00",
        "fontes": {"camera-01": "edicao/fontes/camera-01.mp4", "tela-01": "edicao/fontes/tela-01.mp4"},
        "segmentos": [
            {"n": 1, "linha": "L01", "take": "L01-T1", "fonte": "camera-01", "in": 10.0, "out": 12.0,
             "cortes_internos": [], "saida_inicio": 0.0, "saida_fim": 2.0, "layout": "full", "zoom": None},
            {"n": 2, "linha": "L02", "take": "L02-T3", "fonte": "camera-01", "in": 40.0, "out": 42.0,
             "cortes_internos": [], "saida_inicio": 2.0, "saida_fim": 4.0, "layout": "full", "zoom": None},
            {"n": 3, "linha": "L03", "take": "L03-T1", "fonte": "tela-01", "in": 0.0, "out": 1.5,
             "cortes_internos": [], "saida_inicio": 4.0, "saida_fim": 5.5, "layout": "full", "zoom": None},
        ],
        "overlays": [], "palavras_saida": [], "duracao_saida": 5.5,
        "audio": {"loudnorm_lufs": -14, "true_peak": -1.5, "musica": None, "ducking": True},
    }
    C.escrever_json(vd / "edicao" / "edl.json", edl)
    return {"refs": refs, "amostra": amostra, "vd": vd}


# ───────────────────────── verificações ─────────────────────────

def py(script: str, *args: str) -> subprocess.CompletedProcess:
    r = subprocess.run([sys.executable, str(SCRIPTS / script), *args], capture_output=True, text=True,
                       env=os.environ.copy(), cwd=PROJETO)
    print("\n".join("    │ " + ln for ln in (r.stdout + r.stderr).strip().splitlines()))
    return r


def md5_audio(p: Path) -> str:
    r = subprocess.run([C.FFMPEG, "-v", "error", "-i", str(p), "-map", "0:a", "-c", "copy", "-f", "md5", "-"],
                       capture_output=True, text=True)
    return r.stdout.strip()


def dif(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.abs(a - b).mean())


def main() -> int:
    # bloco "legado": material sintético SDR com nome camera-* → perfil sdr (sem LUT de entrada V-Log)
    os.environ["CAMERA_PERFIL"] = "sdr"
    fx = gerar_fixture()
    vd = fx["vd"]

    print("\n== entrada.py ==")
    hdr = SAIDA / "hdr.mp4"
    subprocess.run([C.FFMPEG, "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=360x640:d=1:r=30",
                    "-c:v", "libx265", "-pix_fmt", "yuv420p10le", "-x265-params",
                    "log-level=error:colorprim=bt2020:transfer=smpte2084:colormatrix=bt2020nc",
                    "-color_primaries", "bt2020", "-color_trc", "smpte2084", "-colorspace", "bt2020nc",
                    str(hdr)], check=True)
    f_hdr, d_hdr = E.filtro_entrada(hdr, "celular")
    ok("celular HDR detectado → zscale+hable", "tonemap=tonemap=hable" in f_hdr, d_hdr)
    sdr = SAIDA / "hdr-sdr.mp4"
    subprocess.run([C.FFMPEG, "-v", "error", "-y", "-i", str(hdr), "-vf", f_hdr, "-c:v", "libx264",
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", str(sdr)],
                   check=True)
    f_sdr, d_sdr = E.filtro_entrada(sdr, "celular")
    ok("celular já convertido (SDR) → não aplica de novo", f_sdr == "", d_sdr)
    ok("tela → sem transformação", E.filtro_entrada(sdr, "tela")[0] == "")

    print("\n== criar_lut.py ==")
    r = py("criar_lut.py", "--referencias", str(fx["refs"]), "--amostra", str(fx["amostra"]),
           "--versao", "v1", "--tipo", "camera")
    ok("criar_lut terminou", r.returncode == 0)
    cube = ROOT / "00-marca/cor/luts/korvu-look-v1.cube"
    meta = C.ler_json(cube.with_suffix(".json"))
    txt = cube.read_text().splitlines()
    dados = [ln for ln in txt if ln and (ln[0].isdigit() or ln[0] == "-")]
    ok(".cube 33³", "LUT_3D_SIZE 33" in txt and len(dados) == 33 ** 3, f"{len(dados)} linhas")
    rr = subprocess.run([C.FFMPEG, "-v", "error", "-f", "lavfi", "-i", "testsrc2=s=64x64:d=0.1", "-vf",
                         f"lut3d=file={C.esc_filtro(cube)}:interp=tetrahedral", "-f", "null", "-"])
    ok("ffmpeg lut3d carrega o .cube", rr.returncode == 0)

    # orientação do .cube: ffmpeg (tetraédrica) ≈ numpy (trilinear)
    teste_png = SAIDA / "_cache" / "frame-teste.png"
    fr = C.ler_frame(fx["amostra"], 1.0, 540)
    C.salvar_png(fr, teste_png)
    out_png = SAIDA / "_cache" / "frame-teste-lut.png"
    subprocess.run([C.FFMPEG, "-v", "error", "-y", "-i", str(teste_png), "-vf",
                    f"lut3d=file={C.esc_filtro(cube)}:interp=tetrahedral", str(out_png)], check=True)
    via_ff = np.asarray(Image.open(out_png).convert("RGB")).astype(np.float32) / 255
    via_np = C.aplicar_lut_np(np.asarray(Image.open(teste_png).convert("RGB")).astype(np.float32) / 255,
                              C.ler_cube(cube))
    ok("orientação R-rápido: ffmpeg ≈ numpy", dif(via_ff, via_np) < 0.006, f"erro médio {dif(via_ff, via_np):.4f}")
    ident = SAIDA / "_cache" / "identidade.cube"
    C.escrever_cube(ident, C.lattice(33), "id")
    subprocess.run([C.FFMPEG, "-v", "error", "-y", "-i", str(teste_png), "-vf",
                    f"lut3d=file={C.esc_filtro(ident)}:interp=tetrahedral", str(out_png)], check=True)
    id_ff = np.asarray(Image.open(out_png).convert("RGB")).astype(np.float32) / 255
    ok("LUT identidade escrita pelo script = identidade no ffmpeg", dif(id_ff, fr) < 0.003,
       f"{dif(id_ff, fr):.4f}")

    e = meta["estatisticas"]
    ref, am, cl = e["referencia"], e["amostra"], e["amostra_com_lut"]
    quente = lambda s: s["rgb_medio"][0] / s["rgb_medio"][2]  # noqa: E731
    ok("contraste aproxima-se da referência",
       abs(cl["contraste_std"] - ref["contraste_std"]) < abs(am["contraste_std"] - ref["contraste_std"]),
       f"ref {ref['contraste_std']} · amostra {am['contraste_std']} · com LUT {cl['contraste_std']}")
    ok("temperatura (R/B) aproxima-se da referência",
       abs(quente(cl) - quente(ref)) < abs(quente(am) - quente(ref)),
       f"ref {quente(ref):.3f} · amostra {quente(am):.3f} · com LUT {quente(cl):.3f}")
    ok("sem pretos esmagados / brancos estourados na amostra com LUT",
       cl["pretos_esmagados_pct"] < 2 and cl["brancos_estourados_pct"] < 2,
       f"{cl['pretos_esmagados_pct']}% / {cl['brancos_estourados_pct']}%")
    ok("alvo_primaria gravado no JSON", "luma" in meta["alvo_primaria"])

    # proteção de pele (unitário)
    pele = np.array([[0.80, 0.58, 0.47], [0.62, 0.44, 0.36], [0.90, 0.72, 0.62]])
    mudado = np.clip(pele * np.array([0.92, 1.0, 1.12]), 0, 1)  # empurra matiz para magenta/azul
    prot = CL.proteger_pele(pele, mudado, 0.7)
    hue = lambda p: np.arctan2(C.ycbcr601(p)[2] - 0.5, C.ycbcr601(p)[1] - 0.5)  # noqa: E731
    ok("proteção de pele reduz desvio de matiz",
       np.all(np.abs(hue(prot) - hue(pele)) < np.abs(hue(mudado) - hue(pele))))
    ok("proteção de pele mantém a luminância nova",
       np.allclose(C.ycbcr601(prot)[0], C.ycbcr601(mudado)[0], atol=1e-6))

    for metodo in ["hm-mvgd-hm", "reinhard"]:
        r = py("criar_lut.py", "--referencias", str(fx["refs"]), "--amostra", str(fx["amostra"]),
               "--versao", f"v9{metodo[:2]}", "--metodo", metodo, "--frames", "8")
        ok(f"método {metodo} gera LUT", r.returncode == 0)

    print("\n== aplicar_cor.py (intensidade 0.6: caminho com blend) ==")
    r = py("aplicar_cor.py", str(vd), "--lut", str(cube), "--intensidade", "0.6", "--preset", "veryfast")
    ok("aplicar_cor --intensidade 0.6", r.returncode == 0)

    print("\n== aplicar_cor.py (intensidade 1.0) ==")
    r = py("aplicar_cor.py", str(vd), "--lut", str(cube), "--preset", "veryfast")
    ok("aplicar_cor terminou", r.returncode == 0)
    corte, cor = vd / "edicao/corte.mp4", vd / "edicao/cor/corte-cor.mp4"
    si, so = C.stream_video(C.probe(corte)), C.stream_video(C.probe(cor))
    ok("1080×1920, 30 fps, yuv420p", (so["width"], so["height"], so["pix_fmt"], so["r_frame_rate"])
       == (1080, 1920, "yuv420p", "30/1"), f"{so['width']}x{so['height']} {so['pix_fmt']} {so['r_frame_rate']}")
    ok("tags bt709", (so.get("color_primaries"), so.get("color_transfer"), so.get("color_space"))
       == ("bt709", "bt709", "bt709"))
    ok("mesmo nº de frames", si.get("nb_frames") == so.get("nb_frames"), f"{si.get('nb_frames')} → {so.get('nb_frames')}")
    ok("áudio copiado bit a bit", md5_audio(corte) == md5_audio(cor) and md5_audio(cor) != "")

    ft = [(C.ler_frame(corte, t, 270), C.ler_frame(cor, t, 270)) for t in (4.3, 5.2)]
    dt_tela = max(dif(a, b) for a, b in ft)
    ok("segmento tela-01 sem cor", dt_tela < 0.01, f"diferença média {dt_tela:.4f}")
    fc = [(C.ler_frame(corte, t, 270), C.ler_frame(cor, t, 270)) for t in (1.0, 3.0)]
    ok("segmentos de câmera graduados", min(dif(a, b) for a, b in fc) > 0.02,
       ", ".join(f"{dif(a, b):.3f}" for a, b in fc))
    rel = C.ler_json(vd / "edicao/cor/correcoes.json")
    s1, s2, s3 = rel["segmentos"]
    ok("take escuro → +EV, take claro → −EV", s1["correcao"]["ev"] > 0 > s2["correcao"]["ev"],
       f"{s1['correcao']['ev']:+.2f} / {s2['correcao']['ev']:+.2f}")
    g1, g2 = s1["correcao"]["ganhos"], s2["correcao"]["ganhos"]
    # os dois takes têm o mesmo cenário: o take frio tem de receber menos azul (relativo ao vermelho)
    # do que o take quente. (O absoluto depende do cenário da amostra, que é outro.)
    ok("take frio recebe correção mais quente que o take quente (B/R)", g1[2] / g1[0] < g2[2] / g2[0],
       f"take1 B/R {g1[2] / g1[0]:.3f} · take2 B/R {g2[2] / g2[0]:.3f}")
    ok("limites ±0.5 EV e ±8%/canal respeitados",
       all(abs(s["correcao"]["ev"]) <= 0.5 for s in (s1, s2)) and
       all(0.92 * 2 ** (-0.5 / 2.2) - 1e-3 <= g <= 1.08 * 2 ** (0.5 / 2.2) + 1e-3 for g in g1 + g2))
    ok("tela marcada como não graduada", s3["graduado"] is False and s3["correcao"] is None)
    luma = lambda a: float((a.reshape(-1, 3) @ LUMA).mean())  # noqa: E731
    antes_d = abs(luma(fc[0][0]) - luma(fc[1][0]))
    depois_d = abs(luma(fc[0][1]) - luma(fc[1][1]))
    ok("takes ficam mais consistentes entre si", depois_d < antes_d,
       f"Δluma antes {antes_d:.3f} → depois {depois_d:.3f}")
    for nome in ["antes-depois.png", "scopes.png", "filtro.txt"]:
        ok(f"gerou edicao/cor/{nome}", (vd / "edicao/cor" / nome).exists())

    print("\n== scopes.py ==")
    r = py("scopes.py", str(cor), "--t", "1.0", "--saida", str(SAIDA / "scopes-standalone.png"))
    ok("scopes standalone", r.returncode == 0 and (SAIDA / "scopes-standalone.png").exists())

    n_legado = len(RESULTADOS)
    vd_v = testes_vlog(fx)
    testes_mosaico()

    falhas = [n for n, c, _ in RESULTADOS if not c]
    print(f"\n{len(RESULTADOS) - len(falhas)}/{len(RESULTADOS)} verificações OK "
          f"({n_legado} do bloco SDR + {len(RESULTADOS) - n_legado} V-Log/mosaico)")
    print(f"Imagens: {ROOT / '00-marca/cor/analises/v1-antes-depois.png'}\n        {vd / 'edicao/cor/antes-depois.png'}"
          f"\n        {vd / 'edicao/cor/scopes.png'}\n        {ROOT / '00-marca/cor/analises/v2-antes-depois.png'}"
          f"\n        {vd_v / 'edicao/cor/antes-depois.png'}\n        {vd_v / 'edicao/cor/scopes.png'}")
    return 1 if falhas else 0


# ───────────────────────── V-Log (Panasonic S5IIX) ─────────────────────────

FPS_V = 25
VL = SAIDA / "vlog"
M = 16  # margem ao medir um patch


def _cc709(nome: str) -> np.ndarray:
    """Patch do ColorChecker em linear BT.709 (D65)."""
    import colour

    cc = colour.CCS_COLOURCHECKERS["ColorChecker24 - After November 2014"]
    return colour.XYZ_to_RGB(colour.xyY_to_XYZ(cc.data[nome]), "ITU-R BT.709", illuminant=cc.illuminant,
                             chromatic_adaptation_transform="Bradford")


def _hue_lab(rgb_lin: np.ndarray) -> float:
    import colour

    lab = colour.XYZ_to_Lab(colour.RGB_to_XYZ(np.asarray(rgb_lin, dtype=np.float64), "ITU-R BT.709"))
    return float(np.degrees(np.arctan2(lab[..., 2], lab[..., 1])))


def carta_vlog() -> tuple[np.ndarray, dict]:
    """Carta de teste em luz de CENA (BT.709 linear, 18% = 0.18) → valores x que o lut3d vê (V-Log/V-Gamut,
    range limitado). Devolve (x H×W×3, patches {nome: (y0, y1, x0, x1, linear)})."""
    import gerar_entrada_vlog as G

    lin = np.full((H, W, 3), 0.05)
    pt: dict[str, tuple] = {}

    def patch(nome, y0, y1, x0, x1, v):
        lin[y0:y1, x0:x1] = v
        pt[nome] = (y0, y1, x0, x1, np.asarray(v, dtype=np.float64))

    lin[0:50] = [0.60, 0.02, 0.02]                                   # marcador vermelho = TOPO (rotação)
    lin[50:750] = (cena(desktop("Sonoma"))[450:1150].astype(np.float64) ** 2.4) * 1.16  # rosto/cenário
    patch("cinza18", 980, 1180, 40, 400, 0.18)
    esc, cla = _cc709("dark skin"), _cc709("light skin")
    patch("pele_escura", 980, 1180, 440, 640, esc)
    patch("pele_media", 980, 1180, 660, 860, (esc + cla) / 2)
    patch("pele_clara", 980, 1180, 880, 1060, cla)
    for k, st in enumerate((3, 4, 5, 6)):
        patch(f"+{st}st", 1200, 1380, 20 + k * 262, 260 + k * 262, 0.18 * 2 ** st)
    import colour

    fora = [colour.RGB_to_RGB(np.array(v), "V-Gamut", "ITU-R BT.709", chromatic_adaptation_transform=None)
            for v in ([0.45, 0.03, 0.03], [0.02, 0.35, 0.03])]
    sat = [_cc709(n) for n in ("red", "green", "blue", "yellow", "magenta", "cyan")] + fora
    for k, v in enumerate(sat):
        patch(f"sat{k}", 1400, 1560, 10 + k * 133, 135 + k * 133, v)
    for k, st in enumerate(range(-6, 7)):
        patch(f"rampa{st:+d}", 1580, 1760, k * 83, k * 83 + 80, 0.18 * 2 ** st)
    x = G.cena_para_legal(lin)
    x[760:960] = np.linspace(0.0, 1.0, W)[None, :, None]  # gradiente 10-bit: códigos 64…940
    return np.clip(x, 0, 1), pt


def _png16(x: np.ndarray, p: Path) -> Path:
    import cv2

    p.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(p), (np.clip(x[..., ::-1], 0, 1) * 65535 + 0.5).astype(np.uint16))
    return p


YUV10 = ("scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv422p10le,"
         "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv")
TAGS = ["-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv"]
PRORES_HQ = ["-c:v", "prores_ks", "-profile:v", "3", "-vendor", "apl0"]
H264_422 = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "10", "-profile:v", "high422"]
# 4K: o libx264 do ffmpeg 7.1 estático escreve um .mov 3840×2160 4:2:2 10-bit sem PPS (ilegível, até pelo ffmpeg 9);
# a S5IIX também grava HEVC 4:2:2 10-bit, que o 7.1 codifica e lê bem.
HEVC_422 = ["-c:v", "libx265", "-preset", "ultrafast", "-x265-params", "log-level=error", "-tag:v", "hvc1"]


def ler_rgb16(video: Path, vf: str, w: int = W, h: int = H, t: float = 0.5) -> np.ndarray:
    """1 frame em RGB float 0–1 a partir de gbrp16le (planos G, B, R)."""
    r = subprocess.run([C.FFMPEG, "-v", "error", "-ss", f"{t}", "-i", str(video), "-frames:v", "1", "-vf", vf,
                        "-f", "rawvideo", "-pix_fmt", "gbrp16le", "-"], capture_output=True, check=True)
    a = np.frombuffer(r.stdout, np.uint16).reshape(3, h, w).astype(np.float64) / 65535
    return np.stack([a[2], a[0], a[1]], -1)


def media(img: np.ndarray, p: tuple, s: float = 1.0) -> np.ndarray:
    y0, y1, x0, x1 = (int(round(v * s)) for v in p[:4])
    m = max(2, int(M * s))
    return img[y0 + m:y1 - m, x0 + m:x1 - m].reshape(-1, 3).mean(0)


def testes_vlog(fx: dict) -> Path:
    import gerar_entrada_vlog as G
    import aplicar_cor as AC

    os.environ["CAMERA_PERFIL"] = "vlog"
    shutil.rmtree(VL, ignore_errors=True)
    VL.mkdir(parents=True)

    print("\n== gerar_entrada_vlog.py ==")
    r = py("gerar_entrada_vlog.py")
    cube_e = ROOT / "00-marca/cor/luts/entrada-camera.cube"
    meta_e = C.ler_json(cube_e.with_suffix(".json")) if cube_e.with_suffix(".json").exists() else {}
    ok("gerar_entrada_vlog terminou", r.returncode == 0 and cube_e.exists())
    ok("entrada-camera.cube 65³ + JSON provisório",
       "LUT_3D_SIZE 65" in cube_e.read_text()[:2000] and meta_e.get("provisorio") is True
       and "metodo" in meta_e and "criado_em" in meta_e)
    print("\n== preferência pela LUT oficial da Panasonic ==")
    pan = ROOT / "00-marca/cor/luts/panasonic/VLog_to_V709_forV35_ver100.cube"
    pan.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(cube_e, pan)
    p_of, d_of = E.lut_entrada_camera()
    pan.unlink()
    p_ge, d_ge = E.lut_entrada_camera()
    ok("entrada.py prefere luts/panasonic/*V709*.cube; sem ela usa a gerada",
       p_of == pan and p_ge == cube_e, f"{d_of} | {d_ge}")

    print("\n== material V-Log sintético (colour: log_encoding_VLog + BT.709→V-Gamut) ==")
    x, pt = carta_vlog()
    png = _png16(x, VL / "carta-vlog.png")
    prores = VL / "carta-vlog-prores.mov"
    subprocess.run([C.FFMPEG, "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS_V), "-i", str(png),
                    "-t", "2", "-vf", YUV10, *PRORES_HQ, *TAGS, str(prores)], check=True)
    sp = C.stream_video(C.probe(prores))
    ok("clip ProRes 422 HQ 10-bit 4:2:2, 25 fps", (sp.get("profile"), sp["pix_fmt"], sp["r_frame_rate"])
       == ("HQ", "yuv422p10le", "25/1"), f"{sp.get('profile')} {sp['pix_fmt']} {sp['r_frame_rate']}")

    print("\n== entrada-camera.cube via ffmpeg lut3d (10-bit → gbrp16le → lut3d) ==")
    out = ler_rgb16(prores, E.filtro_camera(conversao=True))
    antes = ler_rgb16(prores, E.CONVERSAO_RGB16)
    cinza = float(media(out, pt["cinza18"]) @ LUMA)
    ok("cinza 18% → 41–47% (código de saída)", 0.41 <= cinza <= 0.47,
       f"{cinza * 100:.1f}% (V-Log de entrada {float(media(antes, pt['cinza18'])[1]) * 100:.1f}%)")
    dhs = []
    for nome in ("pele_escura", "pele_media", "pele_clara"):
        o = media(out, pt[nome])
        dh = (_hue_lab(o ** 2.4) - _hue_lab(pt[nome][4]) + 180) % 360 - 180
        dhs.append((nome, dh))
    ok("matiz da pele ±5° do linear original (CIELAB, ida e volta V-Log)", all(abs(d) <= 5 for _, d in dhs),
       ", ".join(f"{n} {d:+.1f}°" for n, d in dhs))
    h5, h6, h4 = (media(out, pt[k]) for k in ("+5st", "+6st", "+4st"))
    ok("+5 stops não recortado em 1.0", h5.max() < 0.99, f"+4 {h4[1]:.3f} · +5 {h5[1]:.3f}")
    ok("+6 stops ainda resolvido (< 1.0 e acima de +5)", h6.max() < 0.995 and h6[1] - h5[1] > 0.01,
       f"+6 {h6[1]:.3f}")
    par = G.parametros_curva(G.CINZA_PADRAO, G.CONTRASTE_PADRAO, G.TOE_PADRAO)
    err = max(float(np.abs(G.transformar(media(antes, pt[k]), par) - media(out, pt[k])).max())
              for k in ("cinza18", "pele_clara", "+5st"))
    ok("range legal→V-Log coerente: numpy (transformar) ≈ ffmpeg lut3d", err < 0.01, f"erro máx {err:.4f}")
    sat = np.array([media(out, pt[f"sat{k}"]) for k in range(8)])
    ok("saturados/fora do 709 sem NaN nem canais negativos (soft-clip de gamut)",
       np.isfinite(sat).all() and sat.min() >= 0 and sat.max() <= 1, f"min {sat.min():.3f}")

    print("\n== câmera crua: 3840×2160 rodado, HEVC 4:2:2 10-bit (brutos/camera-00-cor.mov) ==")
    x4 = np.repeat(np.repeat(x, 2, 0), 2, 1)                  # retrato 2160×3840
    png4 = _png16(np.rot90(x4, 1), VL / "carta-4k-deitada.png")  # gravada deitada: topo → coluna da esquerda
    del x4
    tmp4 = VL / "camera-4k-sem-rotacao.mov"
    subprocess.run([C.FFMPEG, "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS_V), "-i", str(png4),
                    "-t", "1", "-vf", YUV10, *HEVC_422, *TAGS, str(tmp4)], check=True)
    cam4k = ROOT / "brutos" / "camera-00-cor.mov"
    cam4k.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([C.FFMPEG, "-v", "error", "-y", "-display_rotation", "-90", "-i", str(tmp4), "-c", "copy",
                    str(cam4k)], check=True)
    s4 = C.stream_video(C.probe(cam4k))
    ok("camera-00-cor.mov: 3840×2160 yuv422p10le com rotação", (s4["width"], s4["height"], s4["pix_fmt"]) ==
       (3840, 2160, "yuv422p10le") and abs(C.rotacao_de(s4)) == 90, f"rotação {C.rotacao_de(s4)}°")
    f4 = C.ler_frame(cam4k, 0.5, 540, E.filtro_entrada(cam4k, "camera")[0])
    topo = f4[:10].reshape(-1, 3).mean(0)
    c4 = float(media(f4, pt["cinza18"], 0.5) @ LUMA)
    ok("ler_frame: auto-rotação + redução + entrada (retrato, marcador no topo, cinza ~43%)",
       f4.shape == (960, 540, 3) and topo[0] > 2 * topo[2] and 0.40 <= c4 <= 0.47,
       f"{f4.shape[1]}×{f4.shape[0]}, topo RGB {np.round(topo, 2)}, cinza {c4:.3f}")

    print("\n== criar_lut.py --tipo camera direto no arquivo cru 4K V-Log ==")
    r = py("criar_lut.py", "--referencias", str(fx["refs"]), "--amostra", str(cam4k), "--versao", "v2",
           "--tipo", "camera", "--frames", "6")
    cube2 = ROOT / "00-marca/cor/luts/korvu-look-v2.cube"
    ok("criar_lut no camera-00-cor.mov (4K rodado 10-bit) terminou", r.returncode == 0 and cube2.exists())
    m2 = C.ler_json(cube2.with_suffix(".json")) if cube2.with_suffix(".json").exists() else {"amostra": {}}
    am = m2["amostra"]
    ok("amostra analisada em Rec.709 via entrada V-Log, em retrato",
       "V-Log" in am.get("transformacao_entrada", "") and am.get("dimensoes_frame") == [540, 960],
       f"{am.get('dimensoes_frame')} · {am.get('transformacao_entrada', '')[:70]}…")

    print("\n== corte 10-bit V-Log 25 fps (camera-01 ×2 takes + tela-01) → aplicar_cor ==")
    vd = ROOT / "videos" / "teste-vlog"
    ed = vd / "edicao"
    ed.mkdir(parents=True, exist_ok=True)
    # take 2: a mesma cena 1 stop abaixo (em V-Log, −1 stop = −0.0727 no código)
    x_m1 = np.clip(G.vlog_para_legal(G.legal_para_vlog(x) - 0.241514 * np.log10(2)), 0, 1)
    x_m1[760:960] = x[760:960]
    png_m1 = _png16(x_m1, VL / "carta-vlog-menos1.png")
    ui = VL / "tela.png"
    C.salvar_png(tela_ui(), ui)
    corte_v = ed / "corte.mp4"
    subprocess.run([C.FFMPEG, "-v", "error", "-y",
                    "-loop", "1", "-framerate", str(FPS_V), "-t", "2", "-i", str(png),
                    "-loop", "1", "-framerate", str(FPS_V), "-t", "1.2", "-i", str(png_m1),
                    "-loop", "1", "-framerate", str(FPS_V), "-t", "1", "-i", str(ui),
                    "-f", "lavfi", "-t", "4.2", "-i", "sine=frequency=440:sample_rate=48000",
                    "-filter_complex", "[0:v]format=rgb48le[a];[1:v]format=rgb48le[b];[2:v]format=rgb48le[c];"
                    f"[a][b][c]concat=n=3:v=1:a=0,{YUV10}[v]", "-map", "[v]", "-map", "3:a",
                    *H264_422, *TAGS, "-c:a", "aac", "-b:a", "128k", str(corte_v)], check=True)
    # cenas extras: E05 = plano de apoio da Lumix (V-Log, −0.4 stop, com som), E06 = gravação de ecrã
    (ed / "extras").mkdir(parents=True, exist_ok=True)
    x_e5 = np.clip(G.vlog_para_legal(G.legal_para_vlog(x) - 0.4 * 0.241514 * np.log10(2)), 0, 1)
    png_e5 = _png16(x_e5, VL / "extra-e05.png")
    subprocess.run([C.FFMPEG, "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS_V), "-t", "1.6",
                    "-i", str(png_e5), "-f", "lavfi", "-t", "1.6", "-i", "sine=frequency=330:sample_rate=48000",
                    "-vf", YUV10, "-map", "0:v", "-map", "1:a", *H264_422, *TAGS, "-c:a", "aac",
                    str(ed / "extras" / "E05.mp4")], check=True)
    subprocess.run([C.FFMPEG, "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS_V), "-t", "1",
                    "-i", str(ui), "-vf", YUV10, *H264_422, *TAGS, str(ed / "extras" / "E06.mp4")], check=True)
    C.escrever_json(ed / "fontes.json", {
        "fontes": {"camera-01": {"arquivo": "edicao/fontes/camera-01.mp4", "tipo": "camera", "perfil": "vlog"},
                   "tela-01": {"arquivo": "edicao/fontes/tela-01.mp4", "tipo": "tela", "perfil": "sdr"}},
        "extras": {"E05": {"arquivo_bruto": "brutos/extras/E05-apoio.mov", "tipo": "camera", "perfil": "vlog"},
                   "E06": {"arquivo_bruto": "brutos/extras/E06-chatgpt.mov", "tipo": "tela", "perfil": "sdr"}}})
    seg = lambda n, take, fonte, a, b: {"n": n, "linha": f"L0{n}", "take": take, "fonte": fonte,  # noqa: E731
                                        "in": 0.0, "out": b - a, "cortes_internos": [], "saida_inicio": a,
                                        "saida_fim": b, "layout": "full", "zoom": None}
    edl = {"versao": 1, "slug": "teste-vlog", "fps": FPS_V, "sr": 48000, "largura": W, "altura": H,
           "aprovado": True, "segmentos": [seg(1, "L01-T1", "camera-01", 0.0, 2.0),
                                           seg(2, "L02-T2", "camera-01", 2.0, 3.2),
                                           seg(3, "L03-T1", "tela-01", 3.2, 4.2)]}
    C.escrever_json(ed / "edl.json", edl)
    si = C.stream_video(C.probe(corte_v))
    ok("corte.mp4 H.264 High 4:2:2 10-bit 25 fps", (si.get("profile"), si["pix_fmt"], si["r_frame_rate"])
       == ("High 4:2:2", "yuv422p10le", "25/1"), f"{si.get('profile')} {si['pix_fmt']} {si.get('nb_frames')} frames")

    r = py("aplicar_cor.py", str(vd), "--lut", str(cube2), "--preset", "veryfast")
    ok("aplicar_cor no corte V-Log terminou", r.returncode == 0)
    cor = ed / "cor" / "corte-cor.mp4"
    so = C.stream_video(C.probe(cor))
    ok("saída 25 fps, mesmo nº de frames, yuv420p 8-bit bt709",
       (so["r_frame_rate"], so.get("nb_frames"), so["pix_fmt"], so.get("color_transfer")) ==
       ("25/1", si.get("nb_frames"), "yuv420p", "bt709"),
       f"{so['r_frame_rate']} · {si.get('nb_frames')} → {so.get('nb_frames')} · {so['pix_fmt']}")
    ft = [(C.ler_frame(corte_v, t, 270), C.ler_frame(cor, t, 270)) for t in (3.4, 4.0)]
    d_tela = max(dif(a, b) for a, b in ft)
    ok("segmento tela-01 intocado", d_tela < 0.01, f"diferença média {d_tela:.4f}")
    rel_v = C.ler_json(ed / "cor/correcoes.json")
    sv1, sv2, sv3 = rel_v["segmentos"]
    ok("entrada V-Log só nos segmentos de câmera (fontes.json perfil vlog)",
       sv1["entrada_vlog"] and sv2["entrada_vlog"] and not sv3["entrada_vlog"]
       and (ed / "cor/filtro.txt").read_text().count("entrada-camera.cube") == 2)
    fa = C.ler_frame(corte_v, 1.0, 1080)
    fd = C.ler_frame(cor, 1.0, 1080)
    pa, pd = float(media(fa, pt["rampa-6"])[1]), float(media(fd, pt["rampa-6"])[1])
    # −6 stops em V-Log: código ≈ 144 → (144−64)/876 ≈ 0.09 visto como vídeo (sombra "levantada")
    ok("V-Log convertido: −6 stops sai do cinza lavado para sombra", pa > 0.07 and pd < 0.04,
       f"−6 stops: V-Log {pa:.3f} → final {pd:.3f}")
    ok("take −1 stop recebe +EV (limitado a +0.5 por padrão)",
       abs(sv2["correcao"]["ev"] - 0.5) < 1e-6 and "limitada" in sv2["correcao"]["nota"]
       and abs(sv1["correcao"]["ev"]) < 0.25,
       f"take1 {sv1['correcao']['ev']:+.2f} · take2 {sv2['correcao']['ev']:+.2f} ({sv2['correcao']['nota']})")
    print("\n== cenas extras (B-roll) ==")
    e5, e6 = ed / "extras" / "E05-cor.mp4", ed / "extras" / "E06-cor.mp4"
    s5i, s5o = C.stream_video(C.probe(ed / "extras" / "E05.mp4")), C.stream_video(C.probe(e5))
    tem_audio = any(s.get("codec_type") == "audio" for s in C.probe(e5)["streams"])
    ok("extra camera E05 → E05-cor.mp4 (25 fps, mesmos frames, yuv420p, áudio copiado)",
       (s5o["r_frame_rate"], s5o.get("nb_frames"), s5o["pix_fmt"]) == ("25/1", s5i.get("nb_frames"), "yuv420p")
       and tem_audio, f"{s5i.get('nb_frames')} → {s5o.get('nb_frames')} frames")
    ok("extra tela E06 nunca graduado (sem E06-cor.mp4)", not e6.exists()
       and {"id": "E06", "tipo": "tela"} in rel_v.get("extras_sem_cor", []))
    ge5 = float(media(C.ler_frame(e5, 0.8, 1080), pt["cinza18"]) @ LUMA)
    gc1 = float(media(fd, pt["cinza18"]) @ LUMA)
    ex5 = rel_v["extras"][0]["correcao"] if rel_v.get("extras") else {"ev": None}
    ok("extra de câmera sai com a mesma cor do principal (cinza ±0.04)", abs(ge5 - gc1) < 0.04,
       f"principal {gc1:.3f} · E05 {ge5:.3f} (E05 −0.4 stop, primária {ex5['ev']:+.2f} EV)")
    mt_c, mt_e = cor.stat().st_mtime_ns, e5.stat().st_mtime_ns

    r = py("aplicar_cor.py", str(vd), "--lut", str(cube2), "--preset", "veryfast", "--limite-ev", "1.5",
           "--limite-wb", "0.15", "--sem-extras")
    ev2 = C.ler_json(ed / "cor/correcoes.json")["segmentos"][1]["correcao"]["ev"]
    ok("--limite-ev 1.5 deixa corrigir o take −1 stop por inteiro", r.returncode == 0 and 0.6 < ev2 <= 1.5,
       f"take2 {ev2:+.2f} EV")
    ok("--sem-extras não toca nos extras", e5.stat().st_mtime_ns == mt_e and cor.stat().st_mtime_ns != mt_c)
    mt_c = cor.stat().st_mtime_ns
    r = py("aplicar_cor.py", str(vd), "--lut", str(cube2), "--preset", "veryfast", "--so-extras")
    rel_x = C.ler_json(ed / "cor/correcoes.json")
    ok("--so-extras: só re-gradua os extras (corte intacto, relatório do corte mantido)",
       r.returncode == 0 and cor.stat().st_mtime_ns == mt_c and e5.stat().st_mtime_ns != mt_e
       and len(rel_x.get("segmentos", [])) == 3 and rel_x["extras"][0]["id"] == "E05")
    h_ad = Image.open(ed / "cor/antes-depois.png").size[1]
    ok("antes-depois.png do corte mantido (+ antes-depois-extras.png à parte)",
       (ed / "cor/antes-depois-extras.png").exists() and h_ad > 2 * 806, f"altura {h_ad}px")

    print("\n== 10 bits preservados até ao encode 8-bit ==")
    fontes = E.carregar_fontes(vd)
    segs = AC.carregar_segmentos(edl, FPS_V, C.duracao_de(C.probe(corte_v)))
    AC.anotar_segmentos(segs, fontes)
    lut_e, _ = E.lut_entrada_camera()
    corr = {segs[0]["grupo"]: {"ganhos": [1.04, 1.0, 0.96]}}  # força o curves na cadeia
    grafo16 = VL / "filtro-16bit.txt"
    grafo16.write_text(AC.montar_filtro(segs, corr, cube2, 1.0, "", lut_e, formato_final="gbrp16le"))
    rr = subprocess.run([C.FFMPEG, "-v", "error", "-i", str(corte_v), "-/filter_complex", str(grafo16),
                         "-map", "[vout]", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gbrp16le", "-"],
                        capture_output=True, check=True)
    g16 = np.frombuffer(rr.stdout, np.uint16).reshape(3, H, W)[0]
    n16 = len(np.unique(g16[860]))
    g8 = len(np.unique((C.ler_frame(cor, 0.5, 1080)[860, :, 1] * 255).round()))
    ok("gradiente 10-bit: > 700 níveis distintos antes do 8-bit (entrada+curves+LUT)", n16 > 700,
       f"{n16} níveis a 16 bits (saída final 8-bit: {g8})")
    return vd


def testes_mosaico() -> None:
    print("\n== dividir_mosaico.py ==")
    pasta = SAIDA / "mosaico"
    shutil.rmtree(pasta, ignore_errors=True)
    pasta.mkdir(parents=True)
    rng = np.random.default_rng(1)
    yy, xx = np.mgrid[0:240, 0:600] / 240.0

    def painel(k):
        base = np.stack([0.25 + 0.15 * k + 0.2 * np.sin(xx * (k + 1)), 0.3 + 0.3 * yy,
                         0.6 - 0.1 * k + 0.1 * np.cos(xx * 2)], -1)
        return np.clip(base + rng.normal(0, 0.03, base.shape), 0, 1)

    preto = np.zeros((14, 600, 3))
    img = np.concatenate([np.zeros((8, 600, 3))] + sum([[painel(k), preto] for k in range(4)], [])[:-1]
                         + [np.zeros((8, 600, 3))])
    src = pasta / "ref-teste-01.jpg"
    Image.fromarray((img * 255).astype(np.uint8)).save(src, quality=92)
    r = py("dividir_mosaico.py", str(src))
    saidas = sorted(pasta.glob("ref-teste-01?.jpg"))
    tam = [Image.open(p).size for p in saidas]
    ok("mosaico de 4 painéis com separadores → 4 imagens (a–d)",
       r.returncode == 0 and [p.name[-5] for p in saidas] == list("abcd")
       and all(abs(w - 600) <= 4 and abs(h - 240) <= 6 for w, h in tam), f"{tam}")
    ok("original movido para _mosaicos/ (fora da leitura do criar_lut)",
       not src.exists() and (pasta / "_mosaicos" / src.name).exists())

    # frames encostados, sem separador (como o mosaico "Tenet" real)
    img2 = np.concatenate([painel(k) * (0.55 if k % 2 else 1.0) for k in range(4)])
    src2 = pasta / "ref-costura.jpg"
    Image.fromarray((img2 * 255).astype(np.uint8)).save(src2, quality=92)
    r = py("dividir_mosaico.py", str(src2), "--manter-original")
    n2 = len(list(pasta.glob("ref-costura?.jpg")))
    ok("frames encostados (costuras) → 4 imagens", r.returncode == 0 and n2 == 4 and src2.exists(), f"{n2}")



if __name__ == "__main__":
    sys.exit(main())
