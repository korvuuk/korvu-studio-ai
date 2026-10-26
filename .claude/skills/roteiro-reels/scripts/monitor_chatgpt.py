"""Gera o texto para colar no ChatGPT Voz, que vira o "monitor" da gravação: lê cada linha do roteiro,
espera o Carlos repetir e pede para repetir quando ele erra.

Uso: uv run python .claude/skills/roteiro-reels/scripts/monitor_chatgpt.py videos/<slug>
Saída: videos/<slug>/monitor-chatgpt.txt

A voz do ChatGPT fica gravada no áudio da câmera — o editor (corte-por-roteiro/locutores.py) separa as
duas vozes e corta tudo o que é da IA. Por isso as regras pedem: ler sem mudar palavras, nunca falar
por cima do Carlos e falas curtas.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REGRAS = """Você vai ser o meu monitor de gravação por voz. Eu vou gravar um vídeo repetindo este roteiro, linha por linha, olhando para a câmera.

REGRAS (siga sempre):
1. Leia UMA linha de cada vez, EXATAMENTE como está escrita. Não mude, não resuma, não acrescente nenhuma palavra. Não leia o código da linha (L01, L02…).
2. Depois de ler, fique em silêncio total e espere eu repetir a linha inteira.
3. Se eu repetir certo, diga só "próxima" e leia a linha seguinte.
4. Se eu errar, trocar ou esquecer uma palavra, diga só "de novo" e leia a MESMA linha outra vez. Não explique o erro.
5. Se eu disser "de novo", leia a mesma linha outra vez.
6. Nunca fale enquanto eu estiver falando. Espere eu terminar e conte 1 segundo de silêncio antes de falar.
7. Nada de comentários, elogios ou perguntas. Frases suas sempre curtas.
8. Quando terminar as linhas principais, leia os hooks alternativos do mesmo jeito.
9. No fim, diga só "fim do roteiro".

10. Quando eu disser "começar", **leia em voz alta a linha POSE DA CAPA** (abaixo), exatamente como está escrita. Depois **espere 4 segundos em silêncio** — é quando eu faço a pose para a capa do vídeo — e só então leia a L01. Não comente nada.

Quando eu disser "começar", leia a POSE DA CAPA, espere 4 segundos e leia a linha L01."""


def limpa(l: dict) -> str:
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", l.get("fala_original") or l["fala"])
    t = re.sub(r"\s*\[pausa( longa)?\]\s*$", "", t, flags=re.I)
    return re.sub(r"\s*/\s*", " ", t).strip()


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    vdir = Path(sys.argv[1]).resolve()
    r = json.loads((vdir / "roteiro.json").read_text(encoding="utf-8"))
    principais = [l for l in r["linhas"] if not l.get("alternativa_de")]
    alternativas = [l for l in r["linhas"] if l.get("alternativa_de")]
    pose = (r.get("pose_capa") or "").strip() or "olhe para a câmera com a expressão do tema"
    out = [REGRAS, "", "POSE DA CAPA (ler em voz alta antes da L01)",
           f"Faça a pose da capa: {pose}. Segure três segundos.", "", "ROTEIRO — LINHAS PRINCIPAIS"]
    out += [f"{l['id']}: {limpa(l)}" for l in principais]
    if alternativas:
        out += ["", "HOOKS ALTERNATIVOS (ler depois das principais)"]
        out += [f"{l['id']}: {limpa(l)}" for l in alternativas]
    destino = vdir / "monitor-chatgpt.txt"
    destino.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Monitor ChatGPT: {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
