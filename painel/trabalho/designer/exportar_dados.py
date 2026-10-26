"""Exporta, SÓ LENDO, os números reais que as prévias do design system usam → painel/design/dados-2026-10-23.json.

Cada bloco guarda a consulta SQL exata e as linhas que ela devolveu. Datas em ISO (UTC); as prévias mostram no fuso
de Londres, como o painel faz hoje (painel/web/src/lib/formato.ts, TZ = Europe/London).
Rodar:  uv run python -I painel/trabalho/designer/exportar_dados.py
        uv run python -I painel/trabalho/designer/exportar_dados.py --bloco portoes_fila   (só esse bloco, com a hora
        da leitura dele; os outros ficam como estavam)
"""
import datetime as dt
import decimal
import json
import pathlib

import sys

import psycopg

RAIZ = pathlib.Path(__file__).resolve().parents[3]
SAIDA = RAIZ / "painel/design/dados-2026-10-23.json"
URL = "postgresql://postgres:postgres@127.0.0.1:55322/postgres"

CONSULTAS = {
    "contagens": "select (select count(*) from agentes) as agentes, (select count(*) from videos) as videos, "
                 "(select count(*) from videos where estado = 'publicado') as videos_publicados",
    "agentes_por_modelo": "select modelo, count(*) as n from agentes group by modelo order by n desc",
    "agentes": "select id, nome, cargo, departamento_id, papel, modelo from agentes order by departamento_id, id",
    "videos": "select slug, tema, estado, atualizado from videos order by slug",
    "fila": "select slug, publicar_em, plataformas, estado, trial, palavra, legado from fila order by publicar_em",
    "publicacoes": "select slug, publicado_em, tema from publicacoes order by publicado_em",
    "metricas_demis": "select lido_em, dias, views, alcance, plays_fb, suspeito from metricas "
                      "where slug = '2026-09-17-demis-hassabis' and views is not null order by lido_em",
    "ultima_leitura_confiavel": "select distinct on (slug) slug, lido_em, dias, views, alcance from metricas "
                                "where not suspeito and alcance is not null order by slug, lido_em desc",
    "leituras_suspeitas": "select slug, lido_em, tempo_medio_s from metricas where suspeito order by lido_em",
    "perfil_snapshots": "select lido_em, seguidores, janela_dias, alcance, views, alcance_seguidores, "
                        "alcance_nao_seguidores from perfil_snapshots order by lido_em",
    "portoes_painel": "select alvo, portao, agente, status, motivos from portoes_estado where alvo = 'painel' order by portao",
    "portoes_livro_chatgpt": "select alvo, portao, agente, status from portoes_estado "
                             "where slug = '2026-10-23-livro-chatgpt' order by alvo, portao",
    "portoes_por_status": "select status, count(*) as n from portoes_estado group by status order by n desc",
    "portoes_fila": "select alvo, slug, portao, agente, status from portoes_estado where alvo like '06-publicar/%' order by alvo",
    "veredictos_painel": "select portao, agente, resultado, em, volta from veredictos where alvo = 'painel' order by em",
    "ultima_sincronizacao": "select em from sincronizacoes order by em desc limit 1",
}


def normal(v):
    if isinstance(v, (dt.datetime, dt.date)):
        return v.isoformat()
    if isinstance(v, decimal.Decimal):
        return float(v)
    if isinstance(v, list):
        return [normal(x) for x in v]
    return v


def main():
    so = sys.argv[sys.argv.index("--bloco") + 1:] if "--bloco" in sys.argv else None
    agora = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    blocos = {}
    with psycopg.connect(URL, autocommit=True) as c:
        c.read_only = True  # transação só de leitura: nada é escrito no banco do painel
        with c.cursor() as cur:
            for nome, sql in CONSULTAS.items():
                if so and nome not in so:
                    continue
                cur.execute(sql)
                cols = [d.name for d in cur.description]
                linhas = [{k: normal(v) for k, v in zip(cols, r)} for r in cur.fetchall()]
                blocos[nome] = {"consulta": sql, "linhas": linhas}
                if so:
                    blocos[nome]["lido_em"] = agora
    if so:
        doc = json.loads(SAIDA.read_text(encoding="utf-8"))
        doc["blocos"].update(blocos)
        SAIDA.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("ok (só", ", ".join(so) + "):", SAIDA)
        return
    doc = {
        "o_que_e": "Números reais usados nas prévias de painel/design/previas/ (o painel não inventa nada). "
                   "Lido do banco do painel (Supabase local, 127.0.0.1:55322) em transação só de leitura.",
        "exportado_em": agora,
        "como_gerar": "uv run python -I painel/trabalho/designer/exportar_dados.py",
        "fuso_das_previas": "Europe/London (o mesmo de painel/web/src/lib/formato.ts)",
        "sem_fonte_de_dados": [
            "custos e tokens de IA (KPI 'Custo de IA', 'Tokens por departamento', 'Custo por modelo', bloco 'Orçamento IA')",
            "responsável por vídeo (coluna 'Responsável' da VideoRow)",
            "presença ('agente a trabalhar agora')",
            "vídeos ativos, tokens e custo por pessoa (métricas do TeamMemberCard)",
            "critérios de cada portão para o Carlos (a checklist do ApprovalGate)",
        ],
        "blocos": blocos,
    }
    SAIDA.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("ok:", SAIDA)


if __name__ == "__main__":
    main()
