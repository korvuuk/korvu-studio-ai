"""Divide um mosaico vertical de referências (vários frames empilhados numa imagem) em imagens separadas.

Uso (da raiz do projeto):
  uv run python .claude/skills/color-grading/scripts/dividir_mosaico.py <imagem> [--n auto|N] \
      [--ignorar 3] [--saida <pasta>] [--manter-original]

- `--n auto` (padrão): deteta faixas horizontais separadoras — linhas quase uniformes (desvio-padrão baixo
  ao longo da linha), tipicamente pretas/brancas (letterbox + espaço entre frames) — e corta nos blocos de
  conteúdo entre elas. Sem separadores (frames encostados, como no mosaico "Tenet"), procura "costuras":
  linhas com salto forte em quase toda a largura. Barras laterais uniformes também são aparadas.
- `--n N`: se a deteção achar exatamente N painéis usa-os; senão divide em N faixas iguais (e apara bordas
  uniformes de cada uma).
- `--ignorar 3` (ou `2,3`): não grava esses painéis (1 = o de cima); as letras mantêm a posição.
Saída: <nome>a.jpg, <nome>b.jpg, … na pasta da imagem (ou --saida). Se a saída é a pasta da imagem, o
original vai para <pasta>/_mosaicos/ (o criar_lut lê TODAS as imagens da pasta de referências, e o mosaico
com barras pretas contaria em dobro e puxaria os pretos), salvo --manter-original.
"""
from __future__ import annotations

import argparse
import shutil
import string
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _comum as C  # noqa: E402

STD_SEP = 0.025      # desvio-padrão máximo de uma linha separadora (preta/branca)
STD_UNIFORME = 0.006  # linha de qualquer cor praticamente lisa
ESCURO, CLARO = 0.12, 0.92
MIN_PAINEL = 0.06    # painel mínimo = 6% da altura (ou 24 px)
COSTURA_SALTO = 0.06  # salto entre linhas vizinhas (0–1) que conta numa coluna
COSTURA_FRAC = 0.5    # fração mínima de colunas com salto para ser costura entre frames


def _linhas_separadoras(img: np.ndarray) -> np.ndarray:
    g = img @ C.LUMA709
    std = np.maximum(g.std(1), img.std(1).max(-1))
    med = g.mean(1)
    return (std < STD_UNIFORME) | ((std < STD_SEP) & ((med < ESCURO) | (med > CLARO)))


def _corridas(mask: np.ndarray) -> list[tuple[int, int]]:
    """Intervalos [ini, fim) onde mask é False (conteúdo)."""
    out, ini = [], None
    for i, m in enumerate(mask):
        if not m and ini is None:
            ini = i
        elif m and ini is not None:
            out.append((ini, i))
            ini = None
    if ini is not None:
        out.append((ini, len(mask)))
    return out


def _aparar(p: np.ndarray) -> np.ndarray:
    """Remove bordas uniformes (linhas em cima/baixo, colunas à esquerda/direita)."""
    lin = _linhas_separadoras(p)
    col = _linhas_separadoras(p.transpose(1, 0, 2))
    ys, xs = np.where(~lin)[0], np.where(~col)[0]
    if len(ys) == 0 or len(xs) == 0:
        return p
    return p[ys[0]:ys[-1] + 1, xs[0]:xs[-1] + 1]


def detectar_costuras(img: np.ndarray) -> list[int]:
    """Linhas onde os frames se encostam sem separador: salto forte entre linhas vizinhas em quase toda
    a largura (uma aresta natural da imagem — mesa, texto — só cobre parte das colunas)."""
    h = img.shape[0]
    d = np.abs(np.diff(img, axis=0)).max(-1)          # (h−1, w)
    frac = (d > COSTURA_SALTO).mean(1)
    media = d.mean(1)
    cand = np.where((frac > COSTURA_FRAC) & (media > 4 * (np.median(media) + 1e-6)))[0]
    viz = max(3, int(0.02 * h))
    cortes: list[int] = []
    for i in cand[np.argsort(-frac[cand])]:
        if all(abs(int(i) - c) > viz for c in cortes):
            cortes.append(int(i))
    return sorted(c + 1 for c in cortes)


def detectar(img: np.ndarray) -> tuple[list[tuple[int, int]], str]:
    h = img.shape[0]
    minimo = max(24, int(MIN_PAINEL * h))
    blocos = [(a, b) for a, b in _corridas(_linhas_separadoras(img)) if b - a >= minimo]
    if len(blocos) >= 2:
        return blocos, "separadores"
    lim = [0, *detectar_costuras(img), h]
    return [(a, b) for a, b in zip(lim[:-1], lim[1:]) if b - a >= minimo], "costuras"


def dividir(img: np.ndarray, n: int | None) -> tuple[list[np.ndarray], str]:
    blocos, metodo = detectar(img)
    if n is None:
        if len(blocos) < 2:
            raise SystemExit("Não encontrei separadores nem costuras horizontais. "
                             "Use --n N para dividir em N faixas iguais.")
        return [_aparar(img[a:b]) for a, b in blocos], f"{len(blocos)} painéis por {metodo}"
    if len(blocos) == n:
        return [_aparar(img[a:b]) for a, b in blocos], f"{n} painéis por {metodo}"
    cortes = np.linspace(0, img.shape[0], n + 1).round().astype(int)
    return ([_aparar(img[cortes[i]:cortes[i + 1]]) for i in range(n)],
            f"{n} faixas iguais (a deteção achou {len(blocos)})")


def main() -> None:
    ap = argparse.ArgumentParser(description="Divide um mosaico vertical de frames em imagens separadas.")
    ap.add_argument("imagem")
    ap.add_argument("--n", default="auto", help="auto (separadores) ou número de painéis")
    ap.add_argument("--ignorar", default="", help="painéis a não gravar, 1 = topo (ex.: 3 ou 2,3)")
    ap.add_argument("--saida", default=None, help="pasta de saída (padrão: a da imagem)")
    ap.add_argument("--manter-original", action="store_true", help="não mover o mosaico para _mosaicos/")
    a = ap.parse_args()

    src = C.resolver(a.imagem)
    if not src.is_file():
        raise SystemExit(f"Imagem não encontrada: {src}")
    n = None if a.n == "auto" else int(a.n)
    if n is not None and not 2 <= n <= 26:
        raise SystemExit("--n deve estar entre 2 e 26")
    ignorar = {int(x) for x in a.ignorar.replace(" ", "").split(",") if x}

    img = np.asarray(Image.open(src).convert("RGB")).astype(np.float32) / 255.0
    paineis, como = dividir(img, n)
    pasta = C.resolver(a.saida) if a.saida else src.parent
    pasta.mkdir(parents=True, exist_ok=True)
    print(f"• {src.name}: {img.shape[1]}×{img.shape[0]} → {como}")
    for i, p in enumerate(paineis):
        letra = string.ascii_lowercase[i]
        if i + 1 in ignorar:
            print(f"  {letra}: ignorado ({p.shape[1]}×{p.shape[0]})")
            continue
        dst = pasta / f"{src.stem}{letra}.jpg"
        Image.fromarray((np.clip(p, 0, 1) * 255 + 0.5).astype(np.uint8)).save(dst, quality=95)
        print(f"  {letra}: {C.rel(dst)} ({p.shape[1]}×{p.shape[0]})")
    if pasta.resolve() == src.parent.resolve() and not a.manter_original:
        dest = src.parent / "_mosaicos"
        dest.mkdir(exist_ok=True)
        shutil.move(str(src), dest / src.name)
        print(f"• original movido para {C.rel(dest / src.name)} (fora da leitura do criar_lut)")


if __name__ == "__main__":
    main()
