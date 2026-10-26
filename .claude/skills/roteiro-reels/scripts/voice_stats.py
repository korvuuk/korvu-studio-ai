"""Mede o jeito de falar do Carlos a partir de transcrições (contrato docs/contratos.md §2).

Uso:
  uv run python .claude/skills/roteiro-reels/scripts/voice_stats.py <transcricao.json> [mais.json…] [--leitura <transcricao_leitura.json>]

Saída: JSON no stdout + 02-calibracao/analises/AAAA-MM-DD-voz.md
- fala livre → muletas, expressões, tamanho de frase, pausas
- leitura de roteiro (--leitura) → ritmo para dimensionar roteiros (wps_roteiro)
"""
from __future__ import annotations

import json
import re
import statistics
import sys
from collections import Counter
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
MULETAS = {"é", "éé", "ã", "hum", "hã", "tipo", "né", "então", "assim", "bom", "enfim", "sabe", "aí", "cara", "beleza", "tá"}
PARADAS = {"de", "a", "o", "que", "e", "do", "da", "em", "um", "uma", "pra", "para", "com", "não", "no", "na", "os", "as", "se", "é", "eu", "você", "isso", "vai"}


def carregar(caminho: str) -> list[dict]:
    dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    return dados["palavras"]


def limpar(t: str) -> str:
    return re.sub(r"[^\wÀ-ÿ]", "", t.lower())


def medir(palavras: list[dict]) -> dict:
    palavras = sorted(palavras, key=lambda w: (w.get("fonte", ""), w["inicio"]))
    toks = [limpar(w["texto"]) for w in palavras]
    gaps = [b["inicio"] - a["fim"] for a, b in zip(palavras, palavras[1:]) if a.get("fonte") == b.get("fonte")]
    gaps = [g for g in gaps if g >= 0]
    span = sum(max(0.0, g) for g in gaps) + sum(w["fim"] - w["inicio"] for w in palavras)
    fala = span - sum(g for g in gaps if g > 0.35)
    minutos = span / 60 if span else 1

    # frases: pontuação no texto do STT ou pausa > 0.7 s
    frases, atual = [], 0
    for w, g in zip(palavras, gaps + [9.9]):
        atual += 1
        if re.search(r"[.!?]$", w["texto"]) or g > 0.7:
            frases.append(atual)
            atual = 0

    muletas = Counter(t for t in toks if t in MULETAS)
    ngramas = Counter()
    for n in (2, 3):
        for i in range(len(toks) - n + 1):
            g = toks[i:i + n]
            if all(g) and not all(x in PARADAS for x in g):
                ngramas[" ".join(g)] += 1

    c = Counter(toks)
    return {
        "palavras": len(palavras),
        "duracao_s": round(span, 1),
        "wps_geral": round(len(palavras) / span, 2) if span else None,
        "wps_articulacao": round(len(palavras) / fala, 2) if fala else None,
        "pausas": {
            "mediana_s": round(statistics.median(gaps), 2) if gaps else None,
            "acima_0_5s_por_min": round(sum(g > 0.5 for g in gaps) / minutos, 1),
            "acima_1s_por_min": round(sum(g > 1.0 for g in gaps) / minutos, 1),
        },
        "frase_media_palavras": round(statistics.mean(frases), 1) if frases else None,
        "muletas_por_min": round(sum(muletas.values()) / minutos, 1),
        "muletas": dict(muletas.most_common(8)),
        "expressoes": [g for g, n in ngramas.most_common(25) if n >= 2][:15],
        "pra_vs_para": [c["pra"], c["para"]],
        "a_gente_vs_nos": [ngramas.get("a gente", 0), c["nós"]],
        "voce_vs_tu": [c["você"] + c["cê"], c["tu"]],
    }


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    leitura = None
    if "--leitura" in args:
        i = args.index("--leitura")
        leitura = args[i + 1]
        args = args[:i] + args[i + 2:]
    livre = [w for a in args for w in carregar(a)]
    res = {"livre": medir(livre) if livre else None, "leitura": medir(carregar(leitura)) if leitura else None}
    base = res["leitura"] or res["livre"]
    if base and base["wps_geral"]:
        wps = round(base["wps_geral"] * 0.97, 2)  # margem para respirar e interrupções visuais
        res["recomendado"] = {"wps_roteiro": wps, "palavras_60s": int(wps * 60)}

    out = RAIZ / "02-calibracao" / "analises" / f"{date.today().isoformat()}-voz.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("# Análise de voz\n\n```json\n" + json.dumps(res, ensure_ascii=False, indent=2) + "\n```\n", encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print(f"\nSalvo em {out.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
