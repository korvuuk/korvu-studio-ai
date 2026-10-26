"""Rascunho do engenheiro-backend (24/10, volta 2): o critério de aceite do ARQUIVADO.json com os vídeos REAIS, no formato
EXATO do escritor real, sem tocar nos vídeos.

O escritor é o scripts/limpeza/finalizar_g3.py (não importado: ele lê sys.argv, confere o HD e apaga). Replicado aqui:
os arquivos não ocultos da RAIZ de brutos/principal/ (linha 16: pr.iterdir()), o nome SEM pasta e as datas em UTC com
isoformat(timespec="seconds") (linha 8) — corta a fração. Para cada vídeo (Hassabis, Hinton), numa raiz temporária fora
do projeto, a gravacao() do sincronizador é comparada campo a campo em três momentos:
  antes      o disco de hoje (os .MOV de verdade);
  depois     só o ARQUIVADO.json (os .MOV saíram);
  transição  o ARQUIVADO.json + parte dos .MOV ainda no disco, com o nome em minúsculas (um link simbólico para o
             original: o stat() é o do original e nada nele muda; nenhum arquivo é aberto nem copiado).
O sha256 vai como marcador (a sessão de limpeza escreve o de verdade, lido na cópia). Mostra também o banco de hoje (a
regra antiga, com fração de segundo: a próxima passagem trunca, menos de 1 s, uma vez) e as partes no Mac × no HD.

Uso (da raiz):  uv run python painel/trabalho/engenheiro-backend/prova_arquivado.py [arquivo do sincronizador]
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import sys
import tempfile
import unicodedata
from pathlib import Path

import psycopg

sys.dont_write_bytecode = True
RAIZ = Path(__file__).resolve().parents[3]
SYNC = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "painel" / "sync" / "sincronizar.py"
VIDEOS = {"2026-09-17-demis-hassabis": 4, "2026-10-20-geoffrey-hinton": 3}  # vídeo → quantos ficam no disco na transição
COLS = ("gravado", "gravacao_arquivos", "gravacao_bytes", "gravacao_ultima", "gravacao_chegou", "gravacao_data_suspeita")
PARTES = ("gravacao_arquivos_no_mac", "gravacao_bytes_no_mac", "gravacao_arquivados", "gravacao_arquivados_bytes")


def iso_finalizar_g3(t: float) -> str:  # scripts/limpeza/finalizar_g3.py:8
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat(timespec="seconds")


def manifesto(principal: Path, slug: str) -> dict:
    arquivos = []
    for f in sorted(principal.iterdir()):  # finalizar_g3.py:16 — a raiz, não oculto, sem o ARQUIVADO.json
        if not f.is_file() or f.name.startswith(".") or f.name == "ARQUIVADO.json":
            continue
        st = os.stat(f)  # só o stat: o arquivo não é aberto
        arquivos.append({"nome": f.name, "bytes": st.st_size, "sha256": "0" * 64,
                         "mtime": iso_finalizar_g3(st.st_mtime), "ctime": iso_finalizar_g3(st.st_ctime)})
    return {"arquivado_em": "2026-10-24T07:00:00+01:00", "motivo": "PROVA do painel (raiz temporária)",
            "destino": {"volume": "KORVU V01", "volume_uuid": "-", "formato": "exFAT", "pasta": f"{slug}/brutos/principal"},
            "conferencia": "marcador: o sha256 de verdade é escrito pela sessão de limpeza",
            "intermediarios": "edicao/fontes/ + edicao/audio48k/", "arquivos": arquivos}


def main() -> int:
    temp = Path(tempfile.mkdtemp(prefix="korvu-prova-arquivado-")).resolve()
    with psycopg.connect("postgresql://postgres:postgres@127.0.0.1:55322/postgres") as c:
        c.read_only = True
        banco = {r[0]: r[1:] for r in c.execute(f"select slug, {', '.join(COLS)} from videos where slug = any(%s)",
                                                [list(VIDEOS)]).fetchall()}
    os.environ["PAINEL_PROJETO"] = str(temp)
    spec = importlib.util.spec_from_file_location("sync_prova", SYNC)
    s = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s)
    falhas = 0
    for slug, ficam in VIDEOS.items():
        real = RAIZ / "videos" / slug / "brutos" / "principal"
        man = manifesto(real, slug)
        print(f"\n{slug}: o ARQUIVADO.json do finalizar_g3.py tem {len(man['arquivos'])} itens "
              f"({', '.join(a['nome'] for a in man['arquivos'])}); ex.: {man['arquivos'][0]['mtime']} · "
              f"{man['arquivos'][0]['ctime']}")
        so = temp / "depois" / "videos" / slug / "brutos" / "principal"
        tr = temp / "transicao" / "videos" / slug / "brutos" / "principal"
        for pasta in (so, tr):
            pasta.mkdir(parents=True)
            (pasta / "ARQUIVADO.json").write_text(json.dumps(man, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        no_disco = [a["nome"] for a in man["arquivos"]][:ficam]
        for nome in no_disco:  # ainda no disco, com outra caixa no nome (e a forma NFD, que nos nomes ASCII é a mesma)
            (tr / unicodedata.normalize("NFD", nome.lower())).symlink_to(real / nome)
        antes, depois, transicao = (s.gravacao(RAIZ / "videos" / slug), s.gravacao(so.parent.parent),
                                    s.gravacao(tr.parent.parent))
        print(f"   transição: no disco {', '.join(n.lower() for n in no_disco)} (links para os originais) + o manifesto")
        print(f"   {'campo':24} {'banco hoje (regra antiga)':34} {'antes (disco)':27} {'depois (só manifesto)':27} "
              f"{'transição':27}")
        for i, col in enumerate(COLS):
            a, d, t = antes[col], depois[col], transicao[col]
            ok = a == d == t
            falhas += not ok
            print(f"   {col:24} {str(banco[slug][i]):34} {str(a):27} {str(d):27} {str(t):27} {'ok' if ok else 'DIFERE'}")
        for col in PARTES:
            print(f"   {col:24} {'':34} {str(antes[col]):27} {str(depois[col]):27} {str(transicao[col]):27}")
    print("\n" + ("antes = depois = transição, campo a campo, nos dois vídeos" if not falhas else f"{falhas} campos diferem"))
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
