"""LUT criativo PARAMÉTRICO (split-toning), para quando a transferência estatística (criar_lut.py) não serve —
ex.: referência com fundo teal e pele quente aplicada a um cenário claro/quente: o mkl deixa os brancos verdes.

Uso (da raiz):
  uv run python .claude/skills/color-grading/scripts/criar_look.py --versao v6 [parâmetros] [--preview videos/<slug>]

Domínio: RGB Rec.709 (gamma) 0–1, o mesmo do lut3d criativo (depois da LUT de entrada V-Log→709).
Operações (todas contínuas e suaves — nada de máscaras duras, que criam manchas na pele):
  1. peso de pele = gaussiana no ângulo de matiz (centro ~35°, σ largo) × rampa suave de croma
  2. saturação: ambiente × --sat, pele × --pele-sat (+ --pele-calor empurra a pele para o laranja/dourado)
  3. split-toning: sombras → --sombra (RGB, ex. teal/sálvia), altas → --alta (quente leve); pele protegida do tom de sombra
  4. contraste em S na luminância (pivô --pivo), preservando matiz; --preto/--branco = piso e teto de saída
Saída: 00-marca/cor/luts/korvu-look-<versao>.cube (+ .json com os parâmetros).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _comum as C  # noqa: E402

N = 33
LUMA = np.array([0.2126, 0.7152, 0.0722])


def vec(txt: str) -> np.ndarray:
    return np.array([float(x) for x in txt.split(",")], dtype=np.float64)


def peso_pele(rgb: np.ndarray, centro: float, sigma: float, croma_min: float = 0.015,
              rampa: float = 0.06) -> np.ndarray:
    y = rgb @ LUMA
    cb = (rgb[..., 2] - y) / 1.8556
    cr = (rgb[..., 0] - y) / 1.5748
    croma = np.hypot(cb, cr)
    ang = np.degrees(np.arctan2(cr, cb))            # laranja/pele ≈ 100–130° neste plano → convertido abaixo
    matiz = (90.0 - ang) % 360.0                    # 0° = vermelho-ish; pele ≈ 20–50°
    d = np.minimum(np.abs(matiz - centro), 360 - np.abs(matiz - centro))
    w_h = np.exp(-0.5 * (d / sigma) ** 2)
    w_c = np.clip((croma - croma_min) / rampa, 0, 1)    # pele escura tem pouco croma em gamma: rampa baixa
    w_c = w_c * w_c * (3 - 2 * w_c)                 # smoothstep
    return w_h * w_c


def curva_s(y: np.ndarray, contraste: float, pivo: float) -> np.ndarray:
    # S suave: log-contrast em torno do pivô, com ombro e pé naturais
    eps = 1e-6
    t = np.clip(y, eps, 1 - eps)
    logit = np.log(t / (1 - t)) - np.log(pivo / (1 - pivo))
    return 1 / (1 + np.exp(-(logit * contraste + np.log(pivo / (1 - pivo)))))


def aplicar(rgb: np.ndarray, p: argparse.Namespace) -> np.ndarray:
    rgb = rgb.astype(np.float64) * 2 ** (p.exposicao / 2.2)     # exposição aproximada no domínio gamma
    y = rgb @ LUMA
    w = peso_pele(rgb, p.pele_centro, p.pele_sigma, p.pele_croma_min, p.pele_croma_rampa)[..., None]
    # 2. saturação diferenciada
    cor = rgb - y[..., None]
    s = p.sat * (1 - w) + p.pele_sat * w
    rgb = y[..., None] + cor * s
    rgb = rgb + w * p.pele_calor * np.array([1.0, 0.35, -0.8])
    # 2b. neutros de meio-tom (paredes, fundo) → tom do ambiente (ex. sálvia), sem tocar pele nem brancos
    y = np.clip(rgb @ LUMA, 0, 1)
    croma = np.linalg.norm(rgb - y[..., None], axis=-1)
    wn = (1 - w[..., 0]) * np.exp(-(croma / p.neutro_croma) ** 2) * (4 * y * (1 - y)) ** 2
    rgb = rgb + wn[..., None] * vec(p.neutro)
    # 3. split-toning (pele recebe só 30% do tom de sombra)
    y = np.clip(rgb @ LUMA, 0, 1)[..., None]
    ws = (1 - y) ** 2 * (1 - 0.7 * w)
    wh = y ** 2
    rgb = rgb + ws * vec(p.sombra) + wh * vec(p.alta)
    # 4. contraste em S na luminância, preservando matiz
    y = np.clip(rgb @ LUMA, 1e-4, 1)
    y2 = curva_s(y, p.contraste, p.pivo)
    rgb = rgb * (y2 / y)[..., None]
    rgb = p.preto + np.clip(rgb, 0, 1) * (p.branco - p.preto)
    return np.clip(rgb, 0, 1)


def escrever_cube(caminho: Path, lut: np.ndarray, titulo: str) -> None:
    with open(caminho, "w") as f:
        f.write(f'TITLE "{titulo}"\nLUT_3D_SIZE {N}\nDOMAIN_MIN 0.0 0.0 0.0\nDOMAIN_MAX 1.0 1.0 1.0\n')
        for b in range(N):          # .cube: R varia mais rápido
            for g in range(N):
                for r in range(N):
                    v = lut[r, g, b]
                    f.write(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--versao", required=True)
    ap.add_argument("--nome", default="look paramétrico")
    ap.add_argument("--sat", type=float, default=0.72, help="saturação do ambiente (1 = igual)")
    ap.add_argument("--pele-sat", type=float, default=1.0, help="saturação da pele")
    ap.add_argument("--pele-calor", type=float, default=0.012, help="empurrão da pele para o dourado")
    ap.add_argument("--pele-centro", type=float, default=35.0, help="matiz central da pele (graus)")
    ap.add_argument("--pele-sigma", type=float, default=28.0, help="largura da proteção (graus) — larga = sem manchas")
    ap.add_argument("--sombra", default="-0.030,0.012,0.004", help="tom somado às sombras (R,G,B)")
    ap.add_argument("--alta", default="0.010,0.004,-0.010", help="tom somado às altas (R,G,B)")
    ap.add_argument("--pele-croma-min", type=float, default=0.015, help="croma a partir do qual conta como pele")
    ap.add_argument("--pele-croma-rampa", type=float, default=0.06, help="rampa de croma da pele (menor = pele escura reconhecida)")
    ap.add_argument("--neutro", default="0,0,0", help="tom somado aos neutros de meio-tom (R,G,B), ex. sálvia -0.02,0.015,0.006")
    ap.add_argument("--neutro-croma", type=float, default=0.06, help="até que croma um tom conta como neutro")
    ap.add_argument("--exposicao", type=float, default=0.0, help="stops (negativo = mais escuro)")
    # Com --base, os padrões viram NEUTROS. Senão a curva em S e o remapeamento de preto/branco são aplicados
    # DE NOVO por cima de um look já pronto: em 2026-09-17 isso engoliu inteiro um +0,6 stop de exposição
    # (o rosto estava em 0,2, abaixo do pivô 0,42, e o contraste 1,18 puxava de volta para baixo).
    ap.add_argument("--contraste", type=float, default=None)
    ap.add_argument("--pivo", type=float, default=0.42)
    ap.add_argument("--preto", type=float, default=None)
    ap.add_argument("--branco", type=float, default=None)
    ap.add_argument("--base", default=None,
                    help="LUT .cube de partida (o ajuste é aplicado DEPOIS dela; ex.: corrigir a pele do WAY v5)")
    ap.add_argument("--forcar", action="store_true")
    p = ap.parse_args()
    # Sobre um look aprovado (--base), o padrão é NÃO repetir contraste nem remapear preto/branco;
    # sozinho, mantém a curva de sempre. Valor passado na linha de comando sempre vence.
    padrao = {"contraste": 1.0, "preto": 0.0, "branco": 1.0} if p.base else {"contraste": 1.18, "preto": 0.025, "branco": 0.95}
    for k, v in padrao.items():
        if getattr(p, k) is None:
            setattr(p, k, v)

    g = np.linspace(0, 1, N)
    r, gg, b = np.meshgrid(g, g, g, indexing="ij")
    grade = np.stack([r, gg, b], axis=-1)
    if p.base:                                   # aplica o ajuste EM CIMA de uma LUT já aprovada (ex.: WAY v5)
        base = C.ler_cube(C.resolver(p.base))
        grade = C.aplicar_lut_np(grade.reshape(N * N, N, 3), base).reshape(N, N, N, 3)
    lut = aplicar(grade, p)
    destino = C.LUTS_DIR / f"korvu-look-{p.versao}.cube"
    if destino.exists() and not p.forcar:
        raise SystemExit(f"{C.rel(destino)} já existe (use --forcar)")
    escrever_cube(destino, lut, f"Korvu {p.versao} — {p.nome}")
    meta = {"versao": p.versao, "tipo": "parametrico", "nome": p.nome, "aprovada": False,
            "criado_em": date.today().isoformat(),
            "parametros": {k: v for k, v in vars(p).items() if k not in ("versao", "forcar")}}
    destino.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(f"✓ LUT paramétrica → {C.rel(destino)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
