"""Rascunho do engenheiro-backend (23/10, volta 1 do PORTÃO-DADOS): reconciliação dos tokens e custos REAIS em três partes.

(a) a regra do script — o usage da 1.ª linha de cada resposta (`--regra-do-script`) — contra o próprio tokens-custos.py:
    prova que a leitura do sincronizador é a mesma do script;
(b) a regra certa — o usage da ÚLTIMA linha — que é o que o banco do painel guarda;
(c) a diferença (b) − (a), explicada linha a linha pelas respostas cuja 1.ª linha traz o usage provisório (Claude Code
    2.1.270–2.1.304), contadas direto dos .jsonl por uma conta à parte.

Só lê o projeto e os registros do Claude Code. O sincronizador grava em bancos de TESTE (painel_teste_rec_<pid>_a/_b,
criados com as migrações e apagados no fim, no Postgres 55322); o banco do Carlos não é tocado. A variante do script com o
corte do coordenador é uma cópia numa pasta temporária fora do projeto (o original não é editado).

Uso (da raiz):  uv run python painel/trabalho/engenheiro-backend/reconciliar_tokens.py
"""
from __future__ import annotations

import glob
import json
import os
import subprocess
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

import psycopg

RAIZ = Path(__file__).resolve().parents[3]
REF = RAIZ / "painel" / "referencias" / "claude-design" / "telas-2026-10-23" / "tokens-custos.py"
SYNC = RAIZ / "painel" / "sync" / "sincronizar.py"
REG = Path.home() / ".claude" / "projects" / "-Users-teste-Documents-CONTENT-AI"
SERV = "postgresql://postgres:postgres@127.0.0.1:55322"
JANELA = ("2026-09-24", "2026-10-23")
CORTE = "2026-10-23T15:02:49.958Z"
CAMBIO = Decimal("0.7465")
CORTE_EMBUTIDO = "if o.get('timestamp','') > '2026-10-23T15:00:00Z': continue"
PRECO = {"claude-opus-5-5": ("4", "5", "8", "0.20", "20"), "claude-sonnet-5-5": ("2", "2.5", "4", "0.20", "10"),
         "claude-fable-5-1": ("10", "12.5", "20", "0.25", "50"), "claude-opus-5": ("5", "6.25", "10", "0.50", "25")}


def script_com_corte(corte: str) -> Path:
    src = REF.read_text(encoding="utf-8")
    assert CORTE_EMBUTIDO in src, "o tokens-custos.py mudou: rever a variante"
    p = Path(tempfile.mkdtemp(prefix="korvu-ref-")) / "tokens-custos-corte.py"
    p.write_text(src.replace(CORTE_EMBUTIDO, f"if o.get('timestamp','') > '{corte}': continue"), encoding="utf-8")
    return p


def rodar_script(p: Path) -> dict:
    out, sec = {"modelo": {}, "depto": {}, "agente": {}}, None
    for ln in subprocess.run([sys.executable, str(p)], capture_output=True, text=True, check=True).stdout.splitlines():
        q = ln.split()
        if ln.startswith("TOTAL"):
            out["total"] = (int(q[2]), Decimal(q[4]))
        elif ln.strip() in ("MODELO", "DEPTO", "AGENTE", "VIDEO", "DIA"):
            sec = ln.strip().lower()
        elif sec in ("modelo", "depto"):
            out[sec][q[0]] = (int(q[1]), Decimal(q[2]))
        elif sec == "agente":
            out[sec][q[0]] = (int(q[1]), Decimal(q[2]), int(q[4]))
    return out


SQL = """select {k} as k, sum(c.tokens)::bigint, sum(c.usd), count(distinct c.arquivo)
from consumo c where c.dia between %s and %s group by 1 order by 2 desc"""
AG = "case when c.tipo = 'principal' then 'principal' else coalesce(c.agente_tipo, 'subagente') end"


def banco(sufixo: str, *args: str) -> tuple[dict, str]:
    nome = f"painel_teste_rec_{os.getpid()}_{sufixo}"
    with psycopg.connect(f"{SERV}/postgres", autocommit=True) as a:
        a.execute(f'create database "{nome}" template template0')
    try:
        with psycopg.connect(f"{SERV}/{nome}", autocommit=True) as c:
            for m in sorted((RAIZ / "painel" / "supabase" / "migrations").glob("*.sql")):
                with c.transaction():
                    c.execute(m.read_text(encoding="utf-8"))
        env = {**os.environ, "PAINEL_DB_URL": f"{SERV}/{nome}", "PYTHONDONTWRITEBYTECODE": "1"}
        r = subprocess.run([sys.executable, str(SYNC), *args], env=env, capture_output=True, text=True)
        linha = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:]
        with psycopg.connect(f"{SERV}/{nome}") as c:
            return ({k: {r[0]: r[1:] for r in c.execute(SQL.format(k=e), JANELA).fetchall()}
                     for k, e in (("total", "'total'"), ("modelo", "c.modelo"), ("depto", "c.departamento_id"),
                                  ("agente", AG))}, linha)
    finally:
        with psycopg.connect(f"{SERV}/postgres", autocommit=True) as a:
            a.execute(f'drop database if exists "{nome}" with (force)')


def custo(modelo: str, u: dict) -> Decimal:
    e, c5, c1, cl, s = (Decimal(x) for x in PRECO[modelo])
    um_h = (u.get("cache_creation") or {}).get("ephemeral_1h_input_tokens") or 0
    return (u.get("input_tokens", 0) * e + (u.get("cache_creation_input_tokens", 0) - um_h) * c5 + um_h * c1
            + u.get("cache_read_input_tokens", 0) * cl + u.get("output_tokens", 0) * s) / 1_000_000


def provisorias(corte: str) -> list[dict]:
    """Direto dos .jsonl, sem o sincronizador: respostas (message.id ou uuid, arquivo) de modelo com preço, com o dia da
    1.ª linha na janela, cuja 1.ª linha (até o corte) tem usage diferente da última (até o corte)."""
    out = []
    for f in glob.glob(glob.escape(str(REG)) + "/**/*.jsonl", recursive=True):
        por = {}
        for ln in open(f, encoding="utf-8", errors="ignore"):
            if '"usage"' not in ln:
                continue
            try:
                o = json.loads(ln)
            except ValueError:
                continue
            m = o.get("message") if isinstance(o, dict) else None
            if not isinstance(m, dict) or not isinstance(m.get("usage"), dict) or not m["usage"]:
                continue
            if (o.get("timestamp") or "") > corte:  # as duas usam timestamps no mesmo formato (…Z, com milissegundos)
                continue
            por.setdefault(m.get("id") or o.get("uuid"), []).append(o)
        for ls in por.values():
            a, b = ls[0]["message"], ls[-1]["message"]
            dia = ls[0]["timestamp"][:10]
            if b.get("model") not in PRECO or not JANELA[0] <= dia <= JANELA[1]:
                continue
            ua, ub = a["usage"], b["usage"]
            campos = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")
            if all(ua.get(k) == ub.get(k) for k in campos) and ua.get("cache_creation") == ub.get("cache_creation"):
                continue
            out.append({"tokens": sum(ub.get(k, 0) - ua.get(k, 0) for k in campos if k != "cache_read_input_tokens"),
                        "usd": custo(b["model"], ub) - custo(a["model"], ua),
                        "so_saida": all(ua.get(k) == ub.get(k) for k in campos if k != "output_tokens"),
                        "cresce": all(ub.get(k, 0) >= ua.get(k, 0) for k in campos), "versao": ls[0].get("version")})
    return out


def comparar(titulo: str, s: dict, db: dict) -> None:
    print(f"\n{titulo}")
    print(f"   {'':24} {'tokens script':>14} {'tokens banco':>13}  {'US$ script':>10} {'US$ banco':>11}")
    linhas = [("TOTAL", s["total"][0], db["total"]["total"][0], s["total"][1], db["total"]["total"][1])]
    for sec in ("modelo", "depto"):
        for k, (tk, us) in s[sec].items():
            b = db[sec].get(k, (0, Decimal(0), 0))
            linhas.append((f"{sec}: {k}", tk, b[0], us, b[1]))
    for nome, ts, tb, us, ub in linhas:
        ok = "ok" if ts == tb and abs(us - ub) <= Decimal("0.005") else "DIFERE"
        print(f"   {nome:24} {ts:>14,} {tb:>13,}  {us:>10} {round(ub, 4):>11}  {ok}")
    difs = {k for k, v in s["agente"].items()
            if (v[0], v[2]) != (db["agente"].get(k, (0, 0, 0))[0], db["agente"].get(k, (0, 0, 0))[2])
            or abs(v[1] - db["agente"][k][1]) > Decimal("0.005")}
    print(f"   por agente ({len(s['agente'])} chaves): tokens, US$ e tarefas", "iguais" if not difs else f"DIFEREM {difs}")


def main() -> None:
    print("(1) o script como está (corte embutido '2026-10-23T15:00:00Z', comparação de texto) × sincronizador "
          "--regra-do-script --ate 2026-10-23T15:00:00.999Z")
    a1, linha = banco("a1", "--regra-do-script", "--ate", "2026-10-23T15:00:00.999Z")
    print("   sincronizador:", linha[20:])
    comparar("    (a) regra do script, lado a lado", rodar_script(REF), a1)

    print(f"\n(2) o corte do coordenador, {CORTE} (inclusive)")
    a, linha_a = banco("a", "--regra-do-script", "--ate", CORTE)
    print("   (a) sincronizador --regra-do-script:", linha_a[20:])
    s = rodar_script(script_com_corte(CORTE))
    comparar("    (a) regra do script (1.ª linha) × tokens-custos.py com o mesmo corte", s, a)
    b, linha_b = banco("b", "--ate", CORTE)
    print("\n   (b) sincronizador, regra do painel (última linha):", linha_b[20:])
    ta, tb = a["total"]["total"], b["total"]["total"]
    prov = provisorias(CORTE)
    print("\n   (c) a diferença, explicada pelas respostas com usage provisório (conta à parte, direto dos .jsonl):")
    print(f"       banco (b) − script (a): {tb[0] - ta[0]:,} tokens · US$ {round(tb[1] - ta[1], 4)}")
    print(f"       Σ (última − 1.ª linha):  {sum(d['tokens'] for d in prov):,} tokens · "
          f"US$ {round(sum(d['usd'] for d in prov), 4)} · {len(prov)} respostas afetadas na janela")
    print(f"       só a saída muda: {all(d['so_saida'] for d in prov)} · a última nunca é menor: "
          f"{all(d['cresce'] for d in prov)} · versões: {sorted({str(d['versao']) for d in prov})}")
    print("       por modelo (b − a):", {k: (b["modelo"][k][0] - a["modelo"].get(k, (0, 0))[0],
                                           str(round(b["modelo"][k][1] - a["modelo"].get(k, (0, Decimal(0)))[1], 4)))
                                       for k in b["modelo"]})
    print(f"\n   em libras (taxa {CAMBIO} £/US$, XE, 23/10): (b) US$ {round(tb[1], 2)} → £ {round(tb[1] * CAMBIO, 2)}"
          f" · (a) US$ {round(ta[1], 2)} → £ {round(ta[1] * CAMBIO, 2)}")


if __name__ == "__main__":
    main()
