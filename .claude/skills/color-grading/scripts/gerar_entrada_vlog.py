"""Gera a LUT de entrada da câmera: Panasonic V-Log / V-Gamut → Rec.709 (BT.1886), 65³.

Uso (da raiz do projeto):
  uv run python .claude/skills/color-grading/scripts/gerar_entrada_vlog.py \
      [--cinza 0.43] [--contraste 1.3] [--toe 0.012] [--forcar]

Saídas: 00-marca/cor/luts/entrada-camera.cube + entrada-camera.json ("provisorio": true).
Se existir uma LUT oficial da Panasonic em 00-marca/cor/luts/panasonic/*V709*.cube, o `entrada.py`
usa-a em vez desta (esta continua a ser o fallback).

── Domínio de ENTRADA (o ponto delicado: range legal vs. full) ──────────────────────────────
A S5IIX grava V-Log em YUV 10-bit com tag de range LIMITADO (tv). A curva V-Log da Panasonic é
definida em *valores de código* 10-bit: V = código/1023 (preto 0% → 128, 18% → 433, 90% → 602).
No filtergraph fazemos `scale=in_color_matrix=bt709:in_range=tv,format=gbrp16le`, ou seja,
o ffmpeg expande 64–940 → 0–1 ANTES do lut3d. O que o lut3d vê é, por canal,
        x = (código − 64) / 876          (0 = código 64, 1 = código 940)
e a LUT desfaz isso exatamente:
        V = (64 + 876·x) / 1023
É a mesma convenção do Resolve/Premiere em "video levels" e das LUTs oficiais da Panasonic,
por isso a LUT oficial pode substituir esta sem mudar mais nada. Códigos acima de 940
(super-brancos, > +6.8 stops acima do cinza 18%) são cortados na conversão; a S5IIX satura
antes disso (~+6 stops em ISO base), portanto não se perde informação útil. Códigos abaixo de
128 (abaixo do preto V-Log = ruído) dão linear ≤ 0 → preto.

── Cadeia (por ponto da grade) ───────────────────────────────────────────────────────────────
  x → V (acima) → colour.models.log_decoding_VLog → linear de cena V-Gamut (18% = 0.18)
    → colour.RGB_to_RGB V-Gamut → ITU-R BT.709 (ambos D65, sem adaptação cromática)
    → exposição: ganho que mantém o cinza 18% em 0.18 (a matriz preserva o branco → ganho 1.0)
    → soft-clip de gamut (estilo ACES RGC: distâncias ao acromático > 0.8 comprimidas; fora do
      709 fica ≥ 0 sem dobras)
    → curva de tom fílmica por canal (Michaelis–Menten com potência + toe):
          f = m·(x/(x+s0))^p ;  g = f²/(f+t)   → g ∈ [0,1), assíntota = branco do ecrã (sem clip duro)
      s0 é resolvido para que o cinza 18% saia com o código --cinza (0.43 ≈ LUT V-709 da Panasonic)
      + reconstrução do canal do meio (--preservar-matiz 0.7): mantém a matiz da pele/amarelos que a
      curva por canal rodaria (+4° na pele clara), sem perder o caminho natural para o branco nas altas
    → codificação Rec.709 para ecrã BT.1886: código = g^(1/2.4)
      (a curva de tom já produz luz de ECRÃ, por isso usa-se o inverso do EOTF BT.1886 — gamma 2.4,
       Lb=0 — e não o OETF de câmera BT.709, que aplicaria o gamma de sistema duas vezes)
    → clamp 0–1.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _comum as C  # noqa: E402

TAMANHO = 65
GAMMA_ECRA = 2.4
CINZA_PADRAO = 0.43       # código de saída do cinza 18% (V-709 da Panasonic ≈ 0.42–0.44)
CONTRASTE_PADRAO = 1.3    # p: declive da curva nos meios-tons
TOE_PADRAO = 0.012        # t: toe (pretos suaves, sem esmagar)
PRESERVAR_MATIZ = 0.7     # 0 = curva puramente por canal; 1 = razão do canal do meio igual à da entrada
# soft-clip de gamut (valores do ACES RGC, simplificados para um limiar comum)
GAMUT_LIMIAR = 0.80
GAMUT_LIMITE = np.array([1.20, 1.30, 1.30])
GAMUT_POT = 1.2


# ───────────────────────── etapas ─────────────────────────

def legal_para_vlog(x: np.ndarray) -> np.ndarray:
    """Valor visto pelo lut3d (0–1 depois de limited→full) → valor de código V-Log (código/1023)."""
    return (64.0 + 876.0 * x) / 1023.0


def vlog_para_legal(v: np.ndarray) -> np.ndarray:
    return (1023.0 * v - 64.0) / 876.0


def matriz_vgamut_709() -> np.ndarray:
    import colour

    vg = colour.RGB_COLOURSPACES["V-Gamut"]
    r709 = colour.RGB_COLOURSPACES["ITU-R BT.709"]
    return colour.matrix_RGB_to_RGB(vg, r709, chromatic_adaptation_transform=None)


def vlog_para_linear709(v: np.ndarray) -> np.ndarray:
    import colour

    lin_vg = colour.models.log_decoding_VLog(v)
    return colour.RGB_to_RGB(lin_vg, "V-Gamut", "ITU-R BT.709", chromatic_adaptation_transform=None)


def soft_clip_gamut(rgb: np.ndarray, limiar: float = GAMUT_LIMIAR, limite=GAMUT_LIMITE,
                    pot: float = GAMUT_POT) -> np.ndarray:
    """Comprime a distância de cada canal ao acromático (max RGB) acima de `limiar`, de modo que a
    distância `limite` passa a 1.0 (canal = 0). Neutros e cores dentro do gamut ficam intactos."""
    rgb = np.asarray(rgb, dtype=np.float64)
    ach = rgb.max(-1, keepdims=True)
    a = np.abs(ach)
    d = np.where(a > 1e-10, (ach - rgb) / np.maximum(a, 1e-10), 0.0)
    lim = np.broadcast_to(np.asarray(limite, dtype=np.float64), d.shape)
    esc = (lim - limiar) / (((1.0 - limiar) / (lim - limiar)) ** (-pot) - 1.0) ** (1.0 / pot)
    e = np.maximum(d - limiar, 0) / esc
    dc = np.where(d > limiar, limiar + esc * e / (1.0 + e ** pot) ** (1.0 / pot), d)
    return ach - dc * a


def parametros_curva(cinza: float, p: float, t: float) -> dict:
    """Resolve s0 e m para: cinza 18% → código `cinza`; assíntota exatamente 1.0 (branco)."""
    m = (1.0 + np.sqrt(1.0 + 4.0 * t)) / 2.0           # g(f=m) = m²/(m+t) = 1
    g0 = cinza ** GAMMA_ECRA                            # luz de ecrã do cinza
    f0 = (g0 + np.sqrt(g0 * g0 + 4.0 * g0 * t)) / 2.0   # inverte o toe
    s0 = 0.18 / (f0 / m) ** (1.0 / p) - 0.18
    return {"m": float(m), "s0": float(s0), "p": float(p), "t": float(t), "cinza": float(cinza)}


def curva_tom(x: np.ndarray, par: dict) -> np.ndarray:
    """Luz de cena (18% = 0.18) → luz de ecrã 0–1, contínua, sem clip duro."""
    x = np.maximum(np.asarray(x, dtype=np.float64), 0.0)
    f = par["m"] * (x / (x + par["s0"])) ** par["p"]
    return f * f / (f + par["t"])


def tom_rgb(lin: np.ndarray, par: dict, preservar: float = PRESERVAR_MATIZ) -> np.ndarray:
    """Curva de tom por canal (dá o caminho natural para o branco nas altas) com reconstrução
    parcial do canal do meio: (meio−min)/(max−min) volta à razão da entrada na proporção `preservar`.
    Sem isto, a curva por canal roda a matiz dos meios-tons claros (pele +4°, amarelo→laranja)."""
    lin = np.maximum(np.asarray(lin, dtype=np.float64), 0.0)
    g = curva_tom(lin, par)
    if preservar <= 0:
        return g
    idx = np.argsort(lin, axis=-1)
    tk = lambda a, i: np.take_along_axis(a, idx[..., i:i + 1], -1)  # noqa: E731
    lo, mi, hi = tk(lin, 0), tk(lin, 1), tk(lin, 2)
    r = np.where(hi - lo > 1e-12, (mi - lo) / np.maximum(hi - lo, 1e-12), 0.0)
    glo, gmi, ghi = tk(g, 0), tk(g, 1), tk(g, 2)
    novo = gmi + (glo + r * (ghi - glo) - gmi) * preservar
    out = g.copy()
    np.put_along_axis(out, idx[..., 1:2], novo, -1)
    return out


def codificar_bt1886(g: np.ndarray) -> np.ndarray:
    return np.maximum(g, 0.0) ** (1.0 / GAMMA_ECRA)


def colour_vlog(l: float) -> float:
    import colour

    return float(colour.models.log_encoding_VLog(l))


def exposicao() -> float:
    """Ganho que mantém o cinza 18% (V-Log 0.4233) em 0.18 depois da matriz (= 1.0: a matriz preserva o branco)."""
    lin = vlog_para_linear709(np.full(3, colour_vlog(0.18)))
    return 0.18 / float(lin @ C.LUMA709)


def transformar(x: np.ndarray, par: dict, preservar: float = PRESERVAR_MATIZ) -> np.ndarray:
    """Cadeia completa: x (como o lut3d vê, 0–1) → código Rec.709/BT.1886 0–1."""
    lin = vlog_para_linear709(legal_para_vlog(np.asarray(x, dtype=np.float64)))
    lin = soft_clip_gamut(lin * exposicao())
    return np.clip(codificar_bt1886(tom_rgb(lin, par, preservar)), 0.0, 1.0)


def cena_para_legal(lin709: np.ndarray) -> np.ndarray:
    """Inverso da entrada (para testes/sintéticos): linear BT.709 de cena → x visto pelo lut3d."""
    import colour

    vg = colour.RGB_to_RGB(np.asarray(lin709, dtype=np.float64), "ITU-R BT.709", "V-Gamut",
                           chromatic_adaptation_transform=None)
    return vlog_para_legal(colour.models.log_encoding_VLog(vg))


def medir(par: dict, preservar: float = PRESERVAR_MATIZ) -> dict:
    """Números de controlo (neutros, em stops relativos ao cinza 18%)."""
    out = {}
    for st in (-6, -4, -2, 0, 1, 2, 2.32, 3, 4, 5, 6, 6.8):
        x = cena_para_legal(np.full(3, 0.18 * 2 ** st))
        out[f"{st:+g} stops"] = round(float(np.clip(transformar(x, par, preservar), 0, 1)[1]), 4)
    x_preto = vlog_para_legal(np.full(3, colour_vlog(0.0)))
    out["preto V-Log (código 128)"] = round(float(transformar(x_preto, par, preservar)[1]), 4)
    return out


# ───────────────────────── main ─────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="Gera entrada-camera.cube (V-Log/V-Gamut → Rec.709).")
    ap.add_argument("--cinza", type=float, default=CINZA_PADRAO, help="código de saída do cinza 18%%")
    ap.add_argument("--contraste", type=float, default=CONTRASTE_PADRAO, help="p da curva (1.1–1.5)")
    ap.add_argument("--toe", type=float, default=TOE_PADRAO, help="toe (0.005–0.03)")
    ap.add_argument("--preservar-matiz", type=float, default=PRESERVAR_MATIZ, help="0–1 (padrão 0.7)")
    ap.add_argument("--tamanho", type=int, default=TAMANHO)
    ap.add_argument("--saida", default=None, help="padrão: 00-marca/cor/luts/entrada-camera.cube")
    ap.add_argument("--forcar", action="store_true", help="sobrescrever se já existir")
    a = ap.parse_args()

    cube = C.resolver(a.saida) if a.saida else C.ENTRADA_CAMERA_CUBE
    meta = cube.with_suffix(".json")
    if cube.exists() and not a.forcar:
        raise SystemExit(f"{C.rel(cube)} já existe (use --forcar para regenerar).")
    if not 0.30 <= a.cinza <= 0.55:
        raise SystemExit("--cinza fora do razoável (0.30–0.55)")

    par = parametros_curva(a.cinza, a.contraste, a.toe)
    n = a.tamanho
    grade = C.lattice(n).reshape(-1, 3)
    lut = transformar(grade, par, a.preservar_matiz).reshape(n, n, n, 3)

    diag = np.array([lut[i, i, i, 1] for i in range(n)])
    if np.any(np.diff(diag) < -1e-7):
        raise SystemExit("curva não monótona na diagonal de cinzentos — parâmetros inválidos")

    agora = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    comentarios = [
        "Korvu — entrada da camera Panasonic Lumix S5IIX: V-Log/V-Gamut -> Rec.709 (BT.1886, gamma 2.4)",
        "PROVISORIO (gerado por gerar_entrada_vlog.py). Preferir a LUT oficial Panasonic em luts/panasonic/.",
        "Entrada: RGB 0-1 como o ffmpeg lut3d ve depois de yuv LIMITED (tv) -> RGB full:",
        "  x = (codigo10bit - 64)/876  ->  V-Log V = (64 + 876x)/1023.",
        f"Cinza 18% -> {a.cinza:.3f}; curva p={a.contraste} toe={a.toe}; soft-clip de gamut; interp=tetrahedral.",
        f"Criada em {agora}",
    ]
    C.escrever_cube(cube, lut, "Korvu V-Log to Rec709 (provisorio)", comentarios)
    C.run([C.FFMPEG, "-v", "error", "-f", "lavfi", "-i", "testsrc2=s=64x64:d=0.1",
           "-vf", f"format=gbrp16le,lut3d=file={C.esc_filtro(cube)}:interp=tetrahedral", "-f", "null", "-"])

    medidas = medir(par, a.preservar_matiz)
    C.escrever_json(meta, {
        "nome": "entrada-camera",
        "provisorio": True,
        "criado_em": agora,
        "camera": "Panasonic Lumix S5IIX",
        "metodo": ("colour.log_decoding_VLog → linear V-Gamut → RGB_to_RGB V-Gamut→BT.709 (D65, sem CAT) → "
                   "exposição (18% fica 18%) → soft-clip de gamut (RGC simplificado) → curva fílmica por canal "
                   "f=m·(x/(x+s0))^p, g=f²/(f+t) com reconstrução parcial da matiz → inverso BT.1886 "
                   "(g^(1/2.4)) → clamp 0–1"),
        "cube": C.rel(cube),
        "tamanho": n,
        "interp": "tetrahedral",
        "entrada": {
            "curva": "Panasonic V-Log", "gamut": "V-Gamut",
            "dominio": "RGB 0–1 como o lut3d vê após yuv limited (tv) → RGB full (in_range=tv)",
            "codigo_para_x": "x = (código10 − 64)/876", "x_para_vlog": "V = (64 + 876·x)/1023",
            "nota": "super-brancos > 940 (> +6.8 stops) cortados; S5IIX satura antes (~+6 stops)",
        },
        "saida": {"espaco": "Rec.709 / BT.1886 (gamma 2.4), RGB 0–1 full range",
                  "intencao": "equivalente técnico à LUT V-709 da Panasonic (não é a oficial)"},
        "parametros": {**{k: round(v, 6) for k, v in par.items()}, "preservar_matiz": a.preservar_matiz,
                       "gamut_limiar": GAMUT_LIMIAR, "gamut_limite": GAMUT_LIMITE.tolist(),
                       "gamut_potencia": GAMUT_POT,
                       "matriz_vgamut_para_709": np.round(matriz_vgamut_709(), 6).tolist()},
        "saida_neutros_codigo": medidas,
    })
    print(f"✓ {C.rel(cube)}  ({n}³, provisório)")
    print(f"✓ {C.rel(meta)}")
    print("  neutros (stops vs. cinza 18% → código de saída):")
    for k, v in medidas.items():
        print(f"    {k:>24}: {v:.4f}")


if __name__ == "__main__":
    main()
