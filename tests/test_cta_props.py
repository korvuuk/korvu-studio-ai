#!/usr/bin/env python3
"""Cartão do CTA no reel-props (gerar_props.derivar_cta) — dados de exemplo, sem mídia nem vídeo real.

    uv run python tests/test_cta_props.py
"""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / ".claude" / "skills" / "legendas-animadas" / "scripts"))
import gerar_props as GP  # noqa: E402


def caps_de(linhas: list[tuple[str, str]], t0: float = 0.0, passo: float = 0.3, pausa: float = 0.4) -> list[dict]:
    out, t = [], t0
    for lid, fala in linhas:
        for w in fala.split():
            out.append({"text": " " + GP.limpar_legenda(w), "startMs": round(t * 1000),
                        "endMs": round((t + passo - 0.05) * 1000), "linha": lid})
            t += passo
        t += pausa
    return out


ROTEIRO = {
    "cta_palavra": "NOBEL",
    "linhas": [
        {"id": "L17", "secao": "payoff", "fala": "Ele ganhou o Nobel."},
        {"id": "L18", "secao": "cta", "fala": "Comenta NOBEL que eu te mando o link oficial."},
        {"id": "L19", "secao": "cta", "fala": "E manda pra quem clica em tudo."},
    ],
}

falhas: list[str] = []


def ok(cond: bool, msg: str) -> None:
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        falhas.append(msg)


caps = caps_de([(l["id"], l["fala"]) for l in ROTEIRO["linhas"]], t0=40.0)
cta = GP.derivar_cta(ROTEIRO, caps, duracao=60.0)
com = next(c for c in caps if c["linha"] == "L18" and GP.normalizar(c["text"]) == "comenta")
ult = [c for c in caps if c["linha"] == "L18"][-1]
prox = next(c for c in caps if c["linha"] == "L19")
ok(cta is not None and cta["palavra"] == "NOBEL", "palavra = cta_palavra")
ok(cta["linha"] == "L18", "linha = a de seção cta que contém a palavra")
ok(abs(cta["inicio"] - com["startMs"] / 1000) < 1e-6, "início = 'Comenta' falado")
ok(cta["fim"] <= prox["startMs"] / 1000 + 1e-6 and cta["fim"] > ult["endMs"] / 1000,
   "fim depois da fala do CTA e antes da próxima linha")
ok(cta["rodape"] == "que eu te mando o link oficial", f"rodapé = fim da fala ({cta['rodape']!r})")

# sem linha seguinte: +0,5 s, limitado à duração
caps2 = caps_de([("L18", "Comenta AGENTE que eu te mando o passo a passo no direct.")], t0=50.0)
rot2 = {"cta_palavra": "AGENTE", "linhas": [{"id": "L18", "secao": "cta",
                                               "fala": "Comenta AGENTE que eu te mando o passo a passo no direct."}]}
c2 = GP.derivar_cta(rot2, caps2, duracao=99.0)
ok(abs(c2["fim"] - (caps2[-1]["endMs"] / 1000 + 0.5)) < 1e-6, "fim = última palavra + 0,5 s")
ok(c2["rodape"] == GP.CTA_RODAPE_PADRAO, f"rodapé longo (8 palavras) → padrão ({c2['rodape']!r})")
c3 = GP.derivar_cta(rot2, caps2, duracao=caps2[-1]["endMs"] / 1000 + 0.1)
ok(abs(c3["fim"] - (caps2[-1]["endMs"] / 1000 + 0.1)) < 1e-6, "fim nunca passa da duração")

# rodapé cortado na pontuação
ok(GP._rodape_cta("Comenta LISTA pros quinze pedidos, e salva pra fazer um por dia.", "LISTA") == "pros quinze pedidos",
   "rodapé para na vírgula")

# sem palavra-chave / linha fora do corte → sem cartão
ok(GP.derivar_cta({"cta_palavra": None, "linhas": ROTEIRO["linhas"]}, caps, 60.0) is None, "sem cta_palavra → null")
ok(GP.derivar_cta(ROTEIRO, [c for c in caps if c["linha"] != "L18"], 60.0) is None, "linha do CTA fora do corte → null")

print(f"\n{'OK' if not falhas else 'FALHOU'}: {11 - len(falhas)}/11")
sys.exit(1 if falhas else 0)
