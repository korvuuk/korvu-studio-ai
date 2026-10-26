"""Atualiza status.json do vídeo + a linha correspondente em _controle/tracker.md

uso: uv run python status.py <video_dir> <estado> [--tracker caminho.md]

Estados: roteiro gravacao edicao edl_aprovada revisao cor legendas capa qa pronto agendado publicado
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, escrever_json, ler_json, log, resolver_video_dir  # noqa: E402

ESTADOS = ["roteiro", "gravacao", "edicao", "edl_aprovada", "revisao", "cor", "legendas",
           "capa", "qa", "pronto", "agendado", "publicado"]
CABECALHO = "| Slug | Tema | Pilar | Estrutura | Hook | CTA | Estado | Atualizado |"
SEPARADOR = "|---|---|---|---|---|---|---|---|"


def agora() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def celula(v) -> str:
    return str(v if v not in (None, "") else "—").replace("|", "/").replace("\n", " ")


def atualizar_tracker(tracker: Path, slug: str, estado: str, quando: str, roteiro: dict) -> str:
    tracker.parent.mkdir(parents=True, exist_ok=True)
    linhas = tracker.read_text(encoding="utf-8").splitlines() if tracker.exists() else \
        ["# Tracker de vídeos", ""]
    data = quando[:16].replace("T", " ")
    idx_cab = next((i for i, l in enumerate(linhas) if l.strip().startswith("| Slug")), None)
    if idx_cab is None:
        linhas += ["", CABECALHO, SEPARADOR]
        idx_cab = len(linhas) - 2
    cab = [c.strip() for c in linhas[idx_cab].strip().strip("|").split("|")]
    col = {nome: i for i, nome in enumerate(cab)}
    fim_tabela = idx_cab + 2
    while fim_tabela < len(linhas) and linhas[fim_tabela].strip().startswith("|"):
        fim_tabela += 1
    for i in range(idx_cab + 2, fim_tabela):
        cells = [c.strip() for c in linhas[i].strip().strip("|").split("|")]
        if cells and cells[0].strip("`") == slug:
            while len(cells) < len(cab):
                cells.append("—")
            cells[col.get("Estado", 6)] = estado
            cells[col.get("Atualizado", 7)] = data
            linhas[i] = "| " + " | ".join(cells) + " |"
            tracker.write_text("\n".join(linhas) + "\n", encoding="utf-8")
            return "atualizada"
    valores = {"Slug": slug, "Tema": roteiro.get("tema"), "Pilar": roteiro.get("pilar"),
               "Estrutura": roteiro.get("estrutura"), "Hook": roteiro.get("hook_escolhido"),
               "CTA": roteiro.get("cta_palavra"), "Estado": estado, "Atualizado": data}
    nova = "| " + " | ".join(celula(valores.get(c)) for c in cab) + " |"
    linhas.insert(fim_tabela, nova)
    tracker.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return "criada"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video_dir")
    ap.add_argument("estado", choices=ESTADOS)
    ap.add_argument("--tracker", default=str(ROOT / "_controle" / "tracker.md"))
    args = ap.parse_args()
    vd = resolver_video_dir(args.video_dir)
    roteiro = ler_json(vd / "roteiro.json", padrao={})
    slug = roteiro.get("slug") or vd.name
    sj = vd / "status.json"
    st = ler_json(sj, padrao={"slug": slug, "estado": None, "atualizado": None, "historico": []})
    quando = agora()
    st["slug"] = slug
    if st.get("estado") != args.estado:
        st.setdefault("historico", []).append({"estado": args.estado, "em": quando})
    st["estado"] = args.estado
    st["atualizado"] = quando
    escrever_json(sj, st)
    acao = atualizar_tracker(Path(args.tracker), slug, args.estado, quando, roteiro)
    log(f"[status] {slug}: {args.estado}  (status.json ok; tracker: linha {acao})")


if __name__ == "__main__":
    main()
