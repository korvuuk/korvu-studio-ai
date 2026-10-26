#!/usr/bin/env python3
"""Aperta o ritmo de uma EDL pronta: margens curtas nas bordas de cada linha e pausas internas encurtadas.

As bordas são medidas pela ENERGIA do áudio (decisão de 19/09: "borda de corte mede-se pelo áudio"), não pelas
marcas do ASR: o `in` fica PAD_INI antes do primeiro som acima do limiar e o `out` PAD_FIM depois do último.
Só APERTA — nunca alarga um segmento (alargar poderia trazer de volta a voz da IA ou um falso começo).

Pedido do Carlos (2026-10-01): "teve muita pausa entre a minha fala e a outra… entre uma linha do roteiro e a
outra". Antes: 0,12 s + 0,20 s = ~0,33 s de silêncio entre linhas. Agora: ~0,05 + 0,08 = ~0,13 s.

uso:
  uv run python scripts/apertar_ritmo.py videos/<slug> [--entrada edicao/edl.json] [--saida edicao/edl.json]
         [--pad-ini 0.05] [--pad-fim 0.08] [--pausa-max 0.25] [--pausa-alvo 0.12] [--limiar -40]
"""
import argparse
import json
import os
import subprocess
from pathlib import Path

import numpy as np

FFMPEG = os.environ.get("FFMPEG_BIN") or "/Users/teste/bin/ffmpeg"
JANELA = 0.01

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("video", type=Path)
ap.add_argument("--entrada", default="edicao/edl.json")
ap.add_argument("--saida", default=None, help="padrão: igual à entrada")
ap.add_argument("--pad-ini", type=float, default=0.05)
ap.add_argument("--pad-fim", type=float, default=0.08)
ap.add_argument("--pausa-max", type=float, default=0.25, help="pausa interna maior que isto é encurtada")
ap.add_argument("--pausa-alvo", type=float, default=0.12, help="...para esta duração")
ap.add_argument("--limiar", type=float, default=-40.0, help="dBFS: acima disto é som da fala")
a = ap.parse_args()

E = a.video / "edicao"
cache = {}


def env(f):
    if f not in cache:
        raw = subprocess.run([FFMPEG, "-v", "error", "-i", str(E / "audio48k" / f"{f}.wav"), "-ac", "1", "-ar", "16000",
                              "-af", "highpass=f=80", "-f", "f32le", "-"], capture_output=True).stdout
        x = np.frombuffer(raw, np.float32)
        h = int(16000 * JANELA)
        n = len(x) // h
        rms = 20 * np.log10(np.sqrt((x[:n * h].reshape(n, h) ** 2).mean(1)) + 1e-12)
        cache[f] = np.convolve(rms, np.ones(3) / 3, mode="same")
    return cache[f]


edl = json.load(open(a.video / a.entrada))
antes = 0.0
depois = 0.0
print(f"{'linha':6} {'in':>8} {'out':>8}  {'cortes':>6}  ganho")
for s in edl["segmentos"]:
    e = env(s["fonte"])
    ja = sorted(s.get("cortes_internos") or [])
    i0, o0 = s["in"], s["out"]
    dur0 = (o0 - i0) - sum(b - x for x, b in ja)
    antes += dur0
    k0, k1 = int(i0 / JANELA), int(o0 / JANELA)
    som = e[k0:k1] > a.limiar
    if not som.any():
        depois += dur0
        continue
    idx = np.where(som)[0]
    p0, p1 = i0 + idx[0] * JANELA, i0 + (idx[-1] + 1) * JANELA
    s["in"] = round(max(i0, p0 - a.pad_ini), 3)          # só aperta
    s["out"] = round(min(o0, p1 + a.pad_fim), 3)
    ja = [[x, b] for x, b in ja if x >= s["in"] and b <= s["out"]]
    novos = list(ja)
    k0, k1 = int(s["in"] / JANELA), int(s["out"] / JANELA)
    som = e[k0:k1] > a.limiar
    i = 0
    while i < len(som):
        if som[i]:
            i += 1
            continue
        j = i
        while j < len(som) and not som[j]:
            j += 1
        x, b = s["in"] + i * JANELA, s["in"] + j * JANELA
        if b - x > a.pausa_max and i > 0 and j < len(som):
            ca, cb = round(x + a.pausa_alvo / 2, 3), round(b - a.pausa_alvo / 2, 3)
            # não sobrepor um corte interno já existente
            if cb - ca >= 0.06 and not any(not (cb <= y0 or ca >= y1) for y0, y1 in ja):
                novos.append([ca, cb])
        i = j
    # Peça do meio com menos de MIN_PECA (0,8 s) é ABSORVIDA pelo render (common.pecas_do_segmento) — ou seja,
    # a fala dela some. Um corte novo só entra se as duas peças à volta continuarem com ≥ 0,8 s.
    # (2026-10-01: sem isto a L07 perdia 0,75 s de fala.)
    def pecas(cortes):
        cur, partes = s["in"], []
        for c0, c1 in sorted(cortes):
            if c0 > cur:
                partes.append((cur, c0))
            cur = max(cur, c1)
        partes.append((cur, s["out"]))
        return partes
    aceitos = list(ja)
    for c in sorted(x for x in novos if x not in ja):
        teste = pecas(aceitos + [c])
        meio = teste[1:-1] if len(teste) > 2 else []
        if all(b - x >= 0.8 for x, b in meio) and all(b - x > 0.08 for x, b in teste):
            aceitos.append(c)
    s["cortes_internos"] = sorted(aceitos)
    dur1 = (s["out"] - s["in"]) - sum(b - x for x, b in s["cortes_internos"])
    depois += dur1
    print(f"{s.get('linha', '?'):6} {s['in']:8.2f} {s['out']:8.2f}  {len(s['cortes_internos']):6d}  {dur1 - dur0:+.2f}s")

saida = a.video / (a.saida or a.entrada)
json.dump(edl, open(saida, "w"), ensure_ascii=False, indent=1)
print(f"\nfala: {antes:.2f}s -> {depois:.2f}s ({depois - antes:+.2f}s) · gravado em {saida}")
print("Próximo: render_corte.py -> cor -> gerar_props -> render_reel -> audio (a duracao_saida é recalculada no render).")
