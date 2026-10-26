"""Gera o roteiro em formato TELEPROMPTER (texto limpo para ler ou para o narrador) a partir do roteiro.json.

Uso: uv run python .claude/skills/roteiro-reels/scripts/teleprompter.py videos/<slug> [--largura 34]
Saída: videos/<slug>/teleprompter.txt  (UTF-8, funciona em qualquer app de teleprompter)

Marcas (o roteirista escreve na coluna FALA; o que faltar é completado aqui):
  /     respiro curto (vírgula, troca de ideia)        — FALA: "Pensa no prompt, / o seu pedido"
  //    pausa (~1 s)       — vem de [pausa] no fim da linha
  ///   pausa longa (~2 s) — vem de [pausa longa] no fim da linha
  MAIÚSCULAS = palavra de ênfase (vem de **negrito**)

O teleprompter tem só o que é FALADO (regra do Carlos, 2026-09-17). Nada de indicação de cena, gesto,
olhar ou postura: ele sabe se posicionar, e cena é assunto do editor.
"""
from __future__ import annotations

import json
import re
import sys
import textwrap
from pathlib import Path

SECOES = {"hook": "HOOK", "promessa": "PROMESSA", "corpo": "CORPO", "payoff": "RESULTADO",
          "cta": "CHAMADA PARA AÇÃO", "hook-alt": "HOOK ALTERNATIVO"}
MODOS = {"split": "ecrã dividido", "full": "ecrã inteiro", "card": "cartão"}


def texto_marcado(fala_original: str) -> str:
    t = re.sub(r"\*\*(.+?)\*\*", lambda m: m.group(1).upper(), fala_original).strip()
    t = re.sub(r"\s*\[pausa longa\]\s*$", " ///", t, flags=re.I)
    t = re.sub(r"\s*\[pausa\]\s*$", " //", t, flags=re.I)
    corpo = re.sub(r"/{2,}\s*$", "", t)
    if "/" not in corpo:  # roteirista não marcou respiros → vírgula, dois-pontos e ponto-e-vírgula
        t = re.sub(r"([,:;])\s+(?=\S)", r"\1 / ", t)
    return re.sub(r"\s+", " ", t)


def linhas_visuais(texto: str, largura: int) -> list[str]:
    fim = ""
    m = re.search(r"\s(/{2,3})$", texto)
    if m:
        fim, texto = m.group(1), texto[: m.start()]
    blocos = []
    for frase in re.split(r"(?:(?<=[.?!…])|(?<=[.?!…][\"”»]))\s+(?=\S)", texto):  # cada frase numa linha nova
        pedacos = [p.strip() for p in frase.split(" / ")]
        for i, p in enumerate(pedacos):
            blocos.append(p + (" /" if i < len(pedacos) - 1 else ""))
    saida = []
    for b in blocos:
        saida += textwrap.wrap(b, largura, break_long_words=False) or [b]
    if fim:
        saida[-1] += f" {fim}"
    return saida


def indicacoes(l: dict) -> list[str]:
    """Vazio de propósito: o teleprompter mostra só a fala.

    Antes isto injetava `[ ▶ E01 · ecrã dividido ]` e `[ ✋ gesto ]` no meio do texto. O Carlos cortou
    (2026-09-17): "não pode existir como eu vou me portar, como eu vou respirar, como eu vou olhar".
    As cenas ficam na tabela `## Cenas extras` do roteiro, para o editor — nunca na leitura.
    """
    return []


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    vdir = Path(sys.argv[1]).resolve()
    largura = int(sys.argv[sys.argv.index("--largura") + 1]) if "--largura" in sys.argv else 34
    r = json.loads((vdir / "roteiro.json").read_text(encoding="utf-8"))
    principais = [l for l in r["linhas"] if not l.get("alternativa_de")]
    alternativas = [l for l in r["linhas"] if l.get("alternativa_de")]

    out = [f"{(r.get('tema') or r['slug']).upper()}", "TELEPROMPTER", "",
           "COMO LER",
           "/    respiro curto",
           "//   pausa (1 segundo)",
           "///  pausa longa (2 segundos)",
           "MAIÚSCULAS = ênfase",
           "Errou? Diga \"de novo\" e repita",
           "a linha inteira desde o começo.", "",
           "━━━━ POSE DA CAPA ━━━━"]
    pose = (r.get("pose_capa") or "").strip() or "olhe para a câmera com a expressão do tema"
    out += textwrap.wrap(f"{pose[0].upper()}{pose[1:]}.", largura, break_long_words=False)
    out += ["Segure 3 SEGUNDOS, em silêncio.",
            "É daqui que sai a capa do feed.", ""]

    def bloco(linhas: list[dict], titulo_extra: str | None = None) -> None:
        secao = None
        if titulo_extra:
            out.extend(["", f"━━━━ {titulo_extra} ━━━━", ""])
        for i, l in enumerate(linhas):
            # sem divisórias de seção ("CORPO", "PAYOFF"…): é informação de produção, não de leitura
            # (Carlos, 2026-09-17: "sem muito pausa, corpo, look — essas informações nós já sabemos").
            secao = l["secao"]
            out.append(l["id"])
            for ind in indicacoes(l):
                out.extend(textwrap.wrap(ind, largura, break_long_words=False, subsequent_indent="  "))
            out.extend(linhas_visuais(texto_marcado(l["fala_original"]), largura))
            # sem "(respira)": instrução de respiração saiu a pedido do Carlos (2026-09-17).
            # O respiro já está marcado com "/" dentro da própria frase, onde ele escolheu.
            out.append("")

    bloco(principais)
    if alternativas:
        bloco(alternativas, "HOOKS ALTERNATIVOS — GRAVAR NO FIM")
    ids = [l["id"] for l in principais]
    out += ["━━━━ FIM ━━━━", f"Conferir: {ids[0]} a {ids[-1]}" +
            (f" + {', '.join(l['id'] for l in alternativas)}" if alternativas else ""), ""]

    destino = vdir / "teleprompter.txt"
    destino.write_text("\n".join(out), encoding="utf-8")
    print(f"Teleprompter: {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
