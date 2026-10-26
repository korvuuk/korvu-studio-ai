"""Ajudante dos testes: aprova portões e sela pacotes num ROOT temporário (CONTENT_AI_ROOT).

Uso (o ROOT vem do ambiente):
  python tests/portoes/fixture_gauntlet.py aprovar <alvo> <portão> [<portão>…]
  python tests/portoes/fixture_gauntlet.py selar <pasta do pacote> <origem videos/<slug>>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import portoes  # noqa: E402


def aprovar(alvo: Path, portao: str) -> dict:
    rel = alvo / "qa" / "portoes" / f"{portao}.md"
    rel.parent.mkdir(parents=True, exist_ok=True)
    rel.write_text(f"PORTÃO-{portao.upper()}: APROVADO (fixture de teste)\n")
    imp = portoes.impressao(portoes.arquivos_da_area(alvo, portao))
    return portoes.registrar(alvo, portao, "APROVADO", imp, str(rel), 0, 0, 0)


def main() -> int:
    cmd, alvo = sys.argv[1], Path(sys.argv[2]).resolve()
    if cmd == "aprovar":
        for p in sys.argv[3:]:
            aprovar(alvo, p)
        return 0
    if cmd == "selar":
        origem = Path(sys.argv[3]).resolve()
        pj = alvo / "pacote.json"
        pac = json.loads(pj.read_text())
        pac["gauntlet"] = portoes.selar(origem, alvo, pac["arquivos"])
        pj.write_text(json.dumps(pac, ensure_ascii=False, indent=2))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
