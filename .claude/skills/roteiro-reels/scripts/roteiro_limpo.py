#!/usr/bin/env python3
"""Roteiro LIMPO — só as frases, para o Carlos ler e aprovar.

Uma fonte, duas saídas (pedido dele, 2026-09-17):
  roteiro.md        → técnico: IDs L01…, seção, [pausa], **negrito**, tabela de cenas. É o que o EDITOR usa
                      (alinhar a fala linha a linha, escolher take, cortar erro, montar a EDL e as legendas).
  roteiro-limpo.txt → o que ele lê: as frases, na ordem, e nada mais.

Uso: uv run python .claude/skills/roteiro-reels/scripts/roteiro_limpo.py videos/<slug>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    vdir = Path(sys.argv[1]).resolve()
    r = json.loads((vdir / "roteiro.json").read_text(encoding="utf-8"))

    principais = [l for l in r["linhas"] if not l.get("alternativa_de")]
    alternativas = [l for l in r["linhas"] if l.get("alternativa_de")]

    pose = (r.get("pose_capa") or "").strip() or "olhe para a câmera com a expressão do tema"
    out = [(r.get("tema") or r["slug"]), "",
           f"Pose da capa (antes de falar): {pose}. Segure 3 segundos, em silêncio.",
           "É daqui que sai a capa do feed.", ""]
    out += [l["fala"] for l in principais]
    if alternativas:
        out += ["", "Outras aberturas (gravar no fim):"]
        out += [l["fala"] for l in alternativas]

    palavras = sum(len(l["palavras"]) for l in principais)
    out += ["", f"{palavras} palavras · ~{palavras / float(r.get('wps_ref') or 2.3):.0f} segundos"]

    destino = vdir / "roteiro-limpo.txt"
    destino.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Roteiro limpo: {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
