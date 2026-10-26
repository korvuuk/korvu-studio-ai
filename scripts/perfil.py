#!/usr/bin/env python3
"""Fotografia do PERFIL @korvu_oficial (Instagram) e da Página do Facebook — para o agente `auditor-de-perfil`.

Pedido do Carlos (16/10): "sair da bolha" do público antigo (Guiné-Bissau/PALOP) e chegar aos lusófonos de
Londres/Reino Unido. O metricas.py lê cada Reel; este lê a CONTA: bio, link, seguidores, de que países/cidades
vêm os seguidores e quem foi alcançado, quanto do alcance é de não-seguidores, e os últimos posts.

Uso (da raiz do projeto):
  uv run python scripts/perfil.py              # lê tudo e grava _controle/perfil/AAAA-MM-DD.json
  uv run python scripts/perfil.py --dias 28    # janela das métricas diárias da conta (máx. 30)
  uv run python scripts/perfil.py --dry-run    # mostra os pedidos (tokens mascarados), não grava

Só LEITURA (GET). Cada pedido é independente: se a Meta recusar um (métrica que não existe nesta versão,
permissão em falta, conta com < 100 seguidores para demografia), o erro fica em "erros" e o resto continua.
Permissões: instagram_basic + instagram_manage_insights (IG); pages_read_engagement + read_insights (FB).
Códigos de saída: 0 ok · 1 erro geral (sem credenciais / sem rede) · 2 leu, mas com pedidos recusados.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import publicar as pub  # noqa: E402  (Http, máscara de segredos, log, .env)

log = pub.log
GRAPH = pub.GRAPH
PASTA = pub.CONTROLE / "perfil"

IG_CAMPOS_CONTA = "username,name,biography,website,followers_count,follows_count,media_count,profile_picture_url"
IG_CAMPOS_MEDIA = ("id,caption,timestamp,media_type,media_product_type,permalink,like_count,comments_count,"
                   "is_shared_to_feed")
IG_METRICAS_MEDIA = ["reach", "views", "saved", "shares", "ig_reels_avg_watch_time"]
# Métricas diárias da conta (metric_type=total_value, janela since/until ≤ 30 dias)
IG_METRICAS_CONTA = ["reach", "views", "accounts_engaged", "total_interactions", "profile_views",
                     "profile_links_taps", "website_clicks", "follows_and_unfollows", "likes", "comments",
                     "saves", "shares"]
DEMOGRAFIA = ["follower_demographics", "reached_audience_demographics", "engaged_audience_demographics"]
QUEBRAS = ["country", "city", "age", "gender"]
FB_CAMPOS_PAGINA = ("name,username,about,description,category,fan_count,followers_count,link,website,"
                    "verification_status,instagram_business_account")
FB_METRICAS_PAGINA = ["page_follows", "page_impressions_unique", "page_media_view", "page_post_engagements",
                      "page_video_views", "page_daily_follows_unique", "page_daily_unfollows_unique"]


class Leitor:
    def __init__(self, http: pub.Http):
        self.http = http
        self.erros: list[dict] = []

    def get(self, rotulo: str, url: str, params: dict, fake=None):
        try:
            return self.http.req("GET", url, params=params, fake=fake or {}, tentativas=3)
        except pub.ErroMeta as e:
            self.erros.append({"pedido": rotulo, "codigo": e.erro.get("code"),
                               "mensagem": pub.mascarar(e.erro.get("message") or str(e))[:300]})
            log.info(f"  recusado: {rotulo} (#{e.erro.get('code')})")
            return None


def _total(r: dict | None):
    """Valor de uma métrica total_value / lifetime / day (soma os dias)."""
    if not r:
        return None
    out = {}
    for item in r.get("data", []):
        nome = item.get("name")
        if "total_value" in item:
            tv = item["total_value"]
            out[nome] = {"valor": tv.get("value")}
            if tv.get("breakdowns"):
                out[nome]["quebras"] = [
                    {"dimensao": b.get("dimension_keys"),
                     "resultados": sorted(({"chave": x.get("dimension_values"), "valor": x.get("value")}
                                           for x in b.get("results", [])), key=lambda x: -(x["valor"] or 0))}
                    for b in tv["breakdowns"]]
        elif item.get("values"):
            vals = [v.get("value") for v in item["values"]]
            num = [v for v in vals if isinstance(v, (int, float))]
            out[nome] = {"valor": sum(num) if len(num) == len(vals) and len(vals) > 1 else vals[-1],
                         "por_dia": item["values"] if len(vals) > 1 else None}
    return out


def ler_instagram(L: Leitor, uid: str, tok: str, dias: int) -> dict:
    ig: dict = {}
    ig["conta"] = L.get("ig conta", f"{GRAPH}/{uid}", {"fields": IG_CAMPOS_CONTA, "access_token": tok})

    hoje = dt.datetime.now(dt.timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    since, until = int((hoje - dt.timedelta(days=dias)).timestamp()), int(hoje.timestamp())
    ig["janela"] = {"dias": dias, "desde": (hoje - dt.timedelta(days=dias)).date().isoformat(),
                    "ate": hoje.date().isoformat()}
    conta: dict = {}
    for m in IG_METRICAS_CONTA:  # uma a uma: os nomes mudam entre versões e uma recusa não derruba as outras
        r = L.get(f"ig insights {m}", f"{GRAPH}/{uid}/insights",
                  {"metric": m, "period": "day", "metric_type": "total_value", "since": since, "until": until,
                   "access_token": tok})
        conta.update(_total(r) or {})
    # Alcance por tipo de seguidor = a medida direta de "furar a bolha"
    for quebra in ("follow_type", "media_product_type"):
        r = L.get(f"ig reach por {quebra}", f"{GRAPH}/{uid}/insights",
                  {"metric": "reach", "period": "day", "metric_type": "total_value", "breakdown": quebra,
                   "since": since, "until": until, "access_token": tok})
        t = _total(r)
        if t and "reach" in t:
            conta[f"reach_por_{quebra}"] = t["reach"]
    ig["metricas_conta"] = conta

    demo: dict = {}
    for m in DEMOGRAFIA:
        for q in QUEBRAS:
            p = {"metric": m, "period": "lifetime", "metric_type": "total_value", "breakdown": q,
                 "access_token": tok}
            if m != "follower_demographics":
                p["timeframe"] = "this_month"
            t = _total(L.get(f"ig {m} {q}", f"{GRAPH}/{uid}/insights", p))
            if t and m in t:
                demo.setdefault(m, {})[q] = (t[m].get("quebras") or [{}])[0].get("resultados")
    ig["demografia"] = demo

    r = L.get("ig posts", f"{GRAPH}/{uid}/media", {"fields": IG_CAMPOS_MEDIA, "limit": 30, "access_token": tok})
    posts = (r or {}).get("data", [])
    for p in posts:
        ins = {}
        for m in IG_METRICAS_MEDIA:
            t = _total(L.get(f"ig post {p.get('id')} {m}", f"{GRAPH}/{p['id']}/insights",
                             {"metric": m, "access_token": tok}))
            if t and m in t:
                ins[m] = t[m]["valor"]
        p["insights"] = ins
    ig["posts"] = posts
    return ig


def ler_facebook(L: Leitor, pid: str, tok: str, dias: int) -> dict:
    fb: dict = {"pagina": L.get("fb pagina", f"{GRAPH}/{pid}", {"fields": FB_CAMPOS_PAGINA, "access_token": tok})}
    hoje = dt.datetime.now(dt.timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    since, until = int((hoje - dt.timedelta(days=dias)).timestamp()), int(hoje.timestamp())
    ins: dict = {}
    for m in FB_METRICAS_PAGINA:
        t = _total(L.get(f"fb insights {m}", f"{GRAPH}/{pid}/insights",
                         {"metric": m, "period": "day", "since": since, "until": until, "access_token": tok}))
        ins.update(t or {})
    fb["metricas_pagina"] = ins
    r = L.get("fb posts", f"{GRAPH}/{pid}/posts",
              {"fields": "id,message,created_time,permalink_url,shares,"
                         "reactions.summary(total_count).limit(0),comments.summary(total_count).limit(0)",
               "limit": 25, "access_token": tok})
    fb["posts"] = (r or {}).get("data", [])
    r = L.get("fb videos", f"{GRAPH}/{pid}/videos",
              {"fields": "id,title,description,created_time,permalink_url,length,views", "limit": 25,
               "access_token": tok})
    fb["videos"] = (r or {}).get("data", [])
    return fb


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Fotografia do perfil IG + Página FB (só leitura).")
    ap.add_argument("--dias", type=int, default=28, help="janela das métricas diárias da conta (máx. 30)")
    ap.add_argument("--dry-run", action="store_true", help="mostra os pedidos; não grava")
    a = ap.parse_args(argv)
    pub.configurar_log()
    http = pub.Http(a.dry_run)
    L = Leitor(http)
    dias = max(1, min(30, a.dias))
    try:
        uid, igt = pub._cred("INSTAGRAM_USER_ID", http.dry), pub._cred("INSTAGRAM_ACCESS_TOKEN", http.dry)
        pid, pgt = pub._cred("META_PAGE_ID", http.dry), pub._cred("META_PAGE_ACCESS_TOKEN", http.dry)
        foto = {"lido_em": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
                "instagram": ler_instagram(L, uid, igt, dias),
                "facebook": ler_facebook(L, pid, pgt, dias)}
    except pub.ErroPublicacao as e:
        log.error(f"✗ {e}")
        return 1
    foto["erros"] = L.erros
    if a.dry_run:
        log.info(f"dry-run: {http.n} pedidos; nada gravado")
        return 0
    PASTA.mkdir(parents=True, exist_ok=True)
    destino = PASTA / f"{dt.date.today().isoformat()}.json"
    destino.write_text(json.dumps(foto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    log.info(f"gravado {destino.relative_to(pub.ROOT)} — {len(L.erros)} pedido(s) recusado(s)")
    return 2 if L.erros else 0


if __name__ == "__main__":
    sys.exit(main())
