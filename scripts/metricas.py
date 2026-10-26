#!/usr/bin/env python3
"""Métricas de cada Reel publicado, lidas 5 dias depois (Instagram + Facebook) → aprendizados do roteirista.

Decisão do Carlos (13/10, docs/decisoes.md §5b): "um agente lê as métricas de cada vídeo 5 dias depois
(alcance, retenção/tempo assistido, curtidas, salvamentos, comentários, compartilhamentos) e alimenta o
roteirista com o que prende e o que faz comentar". Este script é a parte que LÊ; quem interpreta é o agente
`analista-de-metricas` (escreve _controle/aprendizados.md).

Uso (da raiz do projeto):
  uv run python scripts/metricas.py                          # o que o launchd chama 1×/dia: Reels com ≥ 5 dias ainda sem leitura completa
  uv run python scripts/metricas.py --dias 7                 # outro marco
  uv run python scripts/metricas.py --slug <slug> [--forcar] # só um Reel; --forcar lê já (antes dos 5 dias / de novo)
  uv run python scripts/metricas.py --dry-run                # mostra os pedidos (tokens mascarados), não grava nada
  uv run python scripts/metricas.py verificar                # confere se os tokens têm as permissões de insights

Saídas: 07-publicados/<slug>/metricas.json (histórico de leituras, a mais nova em "ultima") e a tabela
_controle/metricas.md (uma linha por vídeo, reescrita a cada execução).

PERMISSÕES NECESSÁRIAS (além das que o publicar.py/responder_comentarios.py já usam):
  - Instagram (INSTAGRAM_ACCESS_TOKEN): instagram_basic + **instagram_manage_insights** (GET /{media}/insights)
  - Facebook (META_PAGE_ACCESS_TOKEN): pages_read_engagement + **read_insights** (GET /{video}/video_insights)
  Sem elas a Meta responde #10/#200; o script NÃO quebra: grava o que conseguiu (curtidas/comentários vêm do
  GET /{media}, que só pede instagram_basic), escreve "permissão em falta: …" e sai com código 3.

LIMITE DA API: a Meta NÃO dá a curva de retenção segundo a segundo (o gráfico "em que segundo as pessoas
saíram" só existe no app). Pela API há só o tempo MÉDIO assistido (ig_reels_avg_watch_time,
post_video_avg_time_watched) e o tempo total. Daqui sai o "% médio assistido" = tempo médio / duração.

Códigos de saída: 0 ok (ou nada a fazer) · 1 erro · 3 permissão em falta (token sem insights).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import publicar as pub  # noqa: E402  (reaproveita Http, máscara de segredos, log, notificação, .env)

log = pub.log
GRAPH = pub.GRAPH
TABELA = pub.CONTROLE / "metricas.md"
ESTADO_COMENTARIOS = pub.CONTROLE / "comentarios" / "estado.json"
DIAS_PADRAO = 5

# Reels do Instagram (Graph API v22+). follows/profile_visits podem não valer para Reels: se a Meta recusar,
# a métrica vai para "nao_suportadas" e o resto continua.
IG_METRICAS = ["views", "reach", "likes", "comments", "saved", "shares", "total_interactions",
               "ig_reels_avg_watch_time", "ig_reels_video_view_total_time", "follows", "profile_visits"]
IG_CAMPOS = "like_count,comments_count,permalink,timestamp,media_product_type,media_type,is_shared_to_feed"
# Reels do Facebook (vídeo da Página). Os nomes mudam com a versão da API: pede-se tudo e fica o que responder.
FB_METRICAS = ["blue_reels_play_count", "fb_reels_total_plays", "fb_reels_replay_count",
               "post_video_avg_time_watched", "post_video_view_time", "post_impressions_unique",
               "post_video_followers", "post_video_social_actions", "post_video_likes_by_reaction_type"]
ESCOPOS_IG = {"instagram_basic", "instagram_manage_insights"}
ESCOPOS_FB = {"pages_read_engagement", "read_insights"}
CODIGOS_PERMISSAO = {3, 10, 102, 190} | set(range(200, 300))

NOTA_RETENCAO = ("A API da Meta não dá a curva de retenção segundo a segundo — só o tempo MÉDIO assistido. "
                 "'% médio assistido' = tempo médio / duração do vídeo. A curva (em que segundo as pessoas "
                 "saem) só aparece no app do Instagram, em Insights do Reel.")


class ErroPermissao(pub.ErroPublicacao):
    pass


def _msg_permissao(permissao: str, e: pub.ErroMeta) -> str:
    # só a mensagem da Meta: a dica genérica do publicar.py (#200 → content_publish) aqui confunde
    return pub.mascarar(f"permissão em falta: {permissao} — Meta code {e.erro.get('code')}: "
                        f"{e.erro.get('message') or ''}".strip())[:300]


def eh_permissao(e: Exception) -> bool:
    if not isinstance(e, pub.ErroMeta):
        return False
    code = e.erro.get("code")
    msg = str(e.erro.get("message") or "").lower()
    return code in CODIGOS_PERMISSAO or "permission" in msg or "permiss" in msg


# ───────────────────────── leitura na Meta ─────────────────────────

def _valor(item: dict):
    """Insights vêm como values[0].value (lifetime) ou total_value.value, conforme a métrica/versão."""
    if isinstance(item.get("total_value"), dict) and "value" in item["total_value"]:
        return item["total_value"]["value"]
    vals = item.get("values") or []
    return vals[-1].get("value") if vals else None


def ler_insights(http: pub.Http, url: str, metricas: list[str], tok: str, permissao: str,
                 ignorar: set[str], fake_valor=0) -> dict:
    """Pede as métricas juntas; se a Meta recusar (#100, métrica não suportada), pede uma a uma e anota as
    que não valem. Falta de permissão vira ErroPermissao (para a plataforma, não o script)."""
    pedir = [m for m in metricas if m not in ignorar]
    out = {"metricas": {}, "nao_suportadas": {m: "recusada antes nesta execução" for m in metricas if m in ignorar}}

    def pedido(lista: list[str]) -> dict:
        r = http.req("GET", url, params={"metric": ",".join(lista), "access_token": tok},
                     fake={"data": [{"name": m, "period": "lifetime", "values": [{"value": fake_valor}]}
                                    for m in lista]}, tentativas=3)
        return {i.get("name"): _valor(i) for i in r.get("data", []) if i.get("name")}

    try:
        out["metricas"] = pedido(pedir)
        return out
    except pub.ErroMeta as e:
        if eh_permissao(e):
            raise ErroPermissao(_msg_permissao(permissao, e))
        log.info(f"a Meta recusou o pedido conjunto (#{e.erro.get('code')}: "
                 f"{pub.mascarar(e.erro.get('message') or '')[:120]}) — peço uma a uma")
    for m in pedir:
        try:
            out["metricas"].update(pedido([m]))
        except pub.ErroMeta as e:
            if eh_permissao(e):
                raise ErroPermissao(_msg_permissao(permissao, e))
            out["nao_suportadas"][m] = pub.mascarar(e.erro.get("message") or str(e))[:200]
            ignorar.add(m)
    return out


def ler_instagram(http: pub.Http, media: str, tok: str, ignorar: set[str]) -> dict:
    ig: dict = {"media_id": media}
    try:
        ig["campos"] = http.req("GET", f"{GRAPH}/{media}", params={"fields": IG_CAMPOS, "access_token": tok},
                                fake={"id": media, "like_count": 0, "comments_count": 0,
                                      "media_product_type": "REELS"}, tentativas=3)
    except pub.ErroMeta as e:
        if eh_permissao(e):
            ig.update(erro=_msg_permissao("instagram_basic", e), permissao_em_falta="instagram_basic")
            return ig
        ig["erro_campos"] = pub.mascarar(e)[:300]
    # Trial Reel: se a API expuser o estado do teste, fica registrado; se não, diz isso.
    try:
        r = http.req("GET", f"{GRAPH}/{media}", params={"fields": "trial_params", "access_token": tok},
                     fake={"id": media}, tentativas=2)
        ig["trial"] = r.get("trial_params") or "a API não devolveu trial_params (Reel normal ou campo não exposto)"
    except pub.ErroMeta as e:
        ig["trial"] = f"campo trial_params não disponível: {pub.mascarar(e.erro.get('message') or e)[:160]}"
    try:
        ig.update(ler_insights(http, f"{GRAPH}/{media}/insights", IG_METRICAS, tok,
                               "instagram_manage_insights", ignorar))
    except ErroPermissao as e:
        ig["erro"] = str(e)
        ig["permissao_em_falta"] = "instagram_manage_insights"
    return ig


def ler_facebook(http: pub.Http, video: str, tok: str, ignorar: set[str]) -> dict:
    fb: dict = {"video_id": video}
    try:
        fb.update(ler_insights(http, f"{GRAPH}/{video}/video_insights", FB_METRICAS, tok, "read_insights",
                               ignorar))
    except ErroPermissao as e:
        fb["erro"] = str(e)
        fb["permissao_em_falta"] = "read_insights"
    except pub.ErroPublicacao as e:
        fb["erro"] = pub.mascarar(e)[:300]
    return fb


# ───────────────────────── cálculos ─────────────────────────

def _num(v) -> float | None:
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def _taxa(a, b) -> float | None:
    a, b = _num(a), _num(b)
    return round(100 * a / b, 2) if a is not None and b else None


def comentarios_palavra(media: str | None) -> dict:
    """Do estado do responder_comentarios.py: quem comentou a palavra e quantos directs saíram."""
    if not media or not ESTADO_COMENTARIOS.exists():
        return {"com_palavra": 0, "directs": 0, "fonte": "sem registro"}
    est = json.loads(ESTADO_COMENTARIOS.read_text(encoding="utf-8")).get("comentarios", {})
    regs = [c for c in est.values() if str(c.get("media")) == str(media)]
    return {"com_palavra": len(regs), "directs": sum(1 for c in regs if c.get("direct")),
            "pessoas": len({c.get("usuario_id") for c in regs if c.get("usuario_id")}),
            "fonte": "_controle/comentarios/estado.json"}


def calcular(leitura: dict, duracao: float | None) -> dict:
    ig = (leitura.get("instagram") or {})
    m, campos = ig.get("metricas") or {}, ig.get("campos") or {}
    curtidas = m.get("likes", campos.get("like_count"))
    comentarios = m.get("comments", campos.get("comments_count"))
    alcance = m.get("reach")
    media_ms = _num(m.get("ig_reels_avg_watch_time"))
    media_s = round(media_ms / 1000, 2) if media_ms is not None else None
    fbm = ((leitura.get("facebook") or {}).get("metricas") or {})
    fb_media_ms = _num(fbm.get("post_video_avg_time_watched"))
    fb_media_s = round(fb_media_ms / 1000, 2) if fb_media_ms is not None else None
    pal = leitura.get("comentarios_palavra") or {}
    return {
        "instagram": {
            "views": m.get("views"), "alcance": alcance, "curtidas": curtidas, "comentarios": comentarios,
            "salvamentos": m.get("saved"), "compartilhamentos": m.get("shares"),
            "seguidores_ganhos": m.get("follows"), "visitas_perfil": m.get("profile_visits"),
            "tempo_medio_s": media_s,
            "pct_medio_assistido": round(100 * media_s / duracao, 1) if media_s is not None and duracao else None,
            "taxas_sobre_alcance_pct": {
                "salvamentos": _taxa(m.get("saved"), alcance), "comentarios": _taxa(comentarios, alcance),
                "compartilhamentos": _taxa(m.get("shares"), alcance), "curtidas": _taxa(curtidas, alcance),
                "comentarios_palavra": _taxa(pal.get("com_palavra"), alcance),
            },
        },
        "facebook": {
            "plays": fbm.get("blue_reels_play_count", fbm.get("fb_reels_total_plays")),
            "alcance": fbm.get("post_impressions_unique"), "tempo_medio_s": fb_media_s,
            "pct_medio_assistido": round(100 * fb_media_s / duracao, 1) if fb_media_s is not None and duracao else None,
            "seguidores_ganhos": fbm.get("post_video_followers"),
        },
        "palavra": {"comentarios": pal.get("com_palavra"), "directs": pal.get("directs")},
    }


# ───────────────────────── escolha dos Reels ─────────────────────────

def completa(leitura: dict) -> bool:
    ig = leitura.get("instagram") or {}
    return bool(ig.get("metricas")) and not ig.get("erro")


def reels_para_ler(dias: float, so_slug: str | None, forcar: bool) -> list[dict]:
    """Publicados há ≥ `dias` que ainda não têm leitura completa depois desse marco (ou todos com --forcar)."""
    out = []
    for pj in sorted(pub.PUBLICADOS.glob("*/post.json")):
        pasta = pj.parent
        slug = pasta.name
        if so_slug and slug != so_slug:
            continue
        post = json.loads(pj.read_text(encoding="utf-8"))
        quando = pub.ler_iso(post.get("publicado_em"))
        if post.get("estado") != "publicado" or not quando:
            if so_slug:
                log.warning(f"{slug}: post.json não está publicado (estado={post.get('estado')})")
            continue
        idade = (pub.agora() - quando).total_seconds() / 86400
        hist = _ler_json(pasta / "metricas.json") or {}
        ja = any(completa(l) and (l.get("dias_desde_publicacao") or 0) >= dias for l in hist.get("leituras", []))
        if not forcar and (idade < dias or ja):
            if so_slug:
                log.info(f"{slug}: {'já tem leitura completa' if ja else f'só {idade:.1f} dia(s) publicado'}"
                         f" — use --forcar para ler agora")
            continue
        out.append({"slug": slug, "pasta": pasta, "post": post, "idade": round(idade, 2)})
    if so_slug and not out and not (pub.PUBLICADOS / so_slug / "post.json").exists():
        raise pub.ErroPublicacao(f"07-publicados/{so_slug}/post.json não existe")
    return out


def _ler_json(p: Path) -> dict | None:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _gravar_json(p: Path, d: dict) -> None:
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(p)


# ───────────────────────── leitura de um Reel ─────────────────────────

def ler_reel(http: pub.Http, r: dict, ignorar_ig: set[str], ignorar_fb: set[str]) -> dict:
    post, pasta = r["post"], r["pasta"]
    pac = _ler_json(pasta / "pacote.json") or {}
    duracao = _num(pac.get("duracao"))
    media = (post.get("instagram") or {}).get("media_id")
    video = (post.get("facebook") or {}).get("video_id")
    leitura: dict = {"lido_em": pub.iso(pub.agora()), "dias_desde_publicacao": r["idade"]}
    if media:
        leitura["instagram"] = ler_instagram(http, str(media), pub._cred("INSTAGRAM_ACCESS_TOKEN", http.dry),
                                             ignorar_ig)
    else:
        leitura["instagram"] = {"erro": "post.json sem instagram.media_id"}
    if video:
        tok_fb = os.environ.get("META_PAGE_ACCESS_TOKEN") or ("<META_PAGE_ACCESS_TOKEN>" if http.dry else None)
        leitura["facebook"] = (ler_facebook(http, str(video), tok_fb, ignorar_fb) if tok_fb
                               else {"erro": "META_PAGE_ACCESS_TOKEN não configurado"})
    leitura["comentarios_palavra"] = comentarios_palavra(media)
    leitura["resumo"] = calcular(leitura, duracao)
    hist = _ler_json(pasta / "metricas.json") or {}
    hist.update({"slug": r["slug"], "publicado_em": post.get("publicado_em"),
                 "permalink_instagram": (post.get("instagram") or {}).get("permalink"),
                 "permalink_facebook": (post.get("facebook") or {}).get("permalink"),
                 "media_id_instagram": media, "video_id_facebook": video, "duracao_s": duracao,
                 "palavra": (post.get("material") or {}).get("palavra") or pac.get("cta_palavra"),
                 "trial": (post.get("instagram") or {}).get("trial"),
                 "tema": pac.get("tema"), "pilar": pac.get("pilar"), "nota_retencao": NOTA_RETENCAO})
    hist.setdefault("leituras", []).append(leitura)
    hist["ultima"] = leitura
    if http.dry:
        log.info(f"[dry-run] {r['slug']}: metricas.json não gravado — resumo: "
                 + json.dumps(leitura["resumo"], ensure_ascii=False))
    else:
        _gravar_json(pasta / "metricas.json", hist)
    return hist


# ───────────────────────── tabela _controle/metricas.md ─────────────────────────

def _f(v, suf: str = "") -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        v = f"{v:.2f}".rstrip("0").rstrip(".") if not v.is_integer() else int(v)
    return f"{v}{suf}"


def escrever_tabela(dry: bool) -> str:
    cab = ["Slug", "Publicado", "Lido em (dias)", "Duração", "Views IG", "Alcance IG", "Tempo médio IG",
           "% assistido IG", "Curtidas", "Coment.", "Salv.", "Compart.", "Salv./alcance", "Coment./alcance",
           "Compart./alcance", "Palavra (coment./directs)", "Plays FB", "Tempo médio FB", "Obs."]
    linhas = []
    for mj in sorted(pub.PUBLICADOS.glob("*/metricas.json")):
        h = json.loads(mj.read_text(encoding="utf-8"))
        u = h.get("ultima") or {}
        s = u.get("resumo") or {}
        ig, fb, pal = s.get("instagram") or {}, s.get("facebook") or {}, s.get("palavra") or {}
        tx = ig.get("taxas_sobre_alcance_pct") or {}
        obs = [x for x in ((u.get("instagram") or {}).get("erro"), (u.get("facebook") or {}).get("erro")) if x]
        obs = [o.split(" — ")[0] for o in obs]
        if h.get("trial"):
            obs.append("trial reel")
        linhas.append([h.get("slug", mj.parent.name), (h.get("publicado_em") or "")[:10],
                       f"{(u.get('lido_em') or '')[:10]} ({_f(u.get('dias_desde_publicacao'))})",
                       _f(h.get("duracao_s"), " s"), _f(ig.get("views")), _f(ig.get("alcance")),
                       _f(ig.get("tempo_medio_s"), " s"), _f(ig.get("pct_medio_assistido"), "%"),
                       _f(ig.get("curtidas")), _f(ig.get("comentarios")), _f(ig.get("salvamentos")),
                       _f(ig.get("compartilhamentos")), _f(tx.get("salvamentos"), "%"),
                       _f(tx.get("comentarios"), "%"), _f(tx.get("compartilhamentos"), "%"),
                       f"{h.get('palavra') or '—'} ({_f(pal.get('comentarios'))}/{_f(pal.get('directs'))})",
                       _f(fb.get("plays")), _f(fb.get("tempo_medio_s"), " s"), "; ".join(obs) or "ok"])
    txt = "\n".join([
        "# Métricas dos Reels",
        "",
        "Gerado por `scripts/metricas.py` (launchd 1×/dia, 09:30) — **não editar à mão**: é reescrito a cada leitura.",
        "Uma linha por vídeo, com a leitura mais recente (histórico em `07-publicados/<slug>/metricas.json`).",
        "Quem interpreta: agente `analista-de-metricas` → `_controle/aprendizados.md` → roteirista/estrategista.",
        "",
        f"> {NOTA_RETENCAO}",
        "> Taxas = métrica ÷ alcance do Instagram. \"Palavra\" = comentários com a palavra-chave / directs enviados "
        "(do `responder_comentarios.py`).",
        "",
        "| " + " | ".join(cab) + " |",
        "|" + "---|" * len(cab),
        *("| " + " | ".join(c) + " |" for c in linhas),
        "",
    ])
    if dry:
        log.info(f"[dry-run] {TABELA.relative_to(pub.ROOT)} não gravado ({len(linhas)} linha(s))")
    else:
        TABELA.parent.mkdir(parents=True, exist_ok=True)
        TABELA.write_text(txt, encoding="utf-8")
    return txt


# ───────────────────────── comandos ─────────────────────────

def passagem(http: pub.Http, dias: float = DIAS_PADRAO, so_slug: str | None = None, forcar: bool = False) -> dict:
    res = {"lidos": 0, "slugs": [], "permissoes_em_falta": set(), "erros": 0}
    ignorar_ig: set[str] = set()
    ignorar_fb: set[str] = set()
    for r in reels_para_ler(dias, so_slug, forcar):
        try:
            h = ler_reel(http, r, ignorar_ig, ignorar_fb)
        except pub.ErroPublicacao as e:
            res["erros"] += 1
            log.error(f"{r['slug']}: {e}")
            continue
        u = h["ultima"]
        res["lidos"] += 1
        res["slugs"].append(r["slug"])
        for plat in ("instagram", "facebook"):
            p = u.get(plat) or {}
            if p.get("permissao_em_falta"):
                res["permissoes_em_falta"].add(p["permissao_em_falta"])
            if p.get("nao_suportadas"):
                log.info(f"{r['slug']} {plat}: métricas não suportadas: {', '.join(p['nao_suportadas'])}")
            if p.get("erro"):
                log.warning(f"{r['slug']} {plat}: {p['erro']}")
        s = u["resumo"]["instagram"]
        log.info(f"{r['slug']} ({r['idade']} dias): views={_f(s['views'])} alcance={_f(s['alcance'])} "
                 f"tempo médio={_f(s['tempo_medio_s'], ' s')} ({_f(s['pct_medio_assistido'], '%')}) "
                 f"curtidas={_f(s['curtidas'])} coment.={_f(s['comentarios'])} salv.={_f(s['salvamentos'])} "
                 f"compart.={_f(s['compartilhamentos'])}")
    if res["lidos"]:
        escrever_tabela(http.dry)
    return res


def cmd_verificar(http: pub.Http) -> int:
    """Confere se os tokens têm as permissões de insights (debug_token)."""
    app, sec = os.environ.get("META_APP_ID"), os.environ.get("META_APP_SECRET")
    if not (app and sec):
        log.error("META_APP_ID/META_APP_SECRET ausentes — não dá para listar as permissões")
        return 1
    falta_tot: list[str] = []
    for nome, var, precisa in (("token IG", "INSTAGRAM_ACCESS_TOKEN", ESCOPOS_IG),
                               ("token Página", "META_PAGE_ACCESS_TOKEN", ESCOPOS_FB)):
        tok = os.environ.get(var)
        if not tok:
            log.warning(f"{var} em falta")
            falta_tot += sorted(precisa)
            continue
        try:
            d = http.req("GET", f"{GRAPH}/debug_token", params={"input_token": tok, "access_token": f"{app}|{sec}"},
                         fake={"data": {"is_valid": True, "scopes": sorted(precisa)}}).get("data", {})
        except pub.ErroPublicacao as e:
            log.error(f"✗ {nome}: {e}")
            return 1
        falta = sorted(precisa - set(d.get("scopes") or []))
        falta_tot += falta
        log.info(f"{'✓' if d.get('is_valid') and not falta else '✗'} {nome}: válido={d.get('is_valid')}"
                 + (f" | permissão em falta: {', '.join(falta)}" if falta else ""))
    if falta_tot:
        log.error("Adicione ao app/token (Graph API Explorer → Generate Access Token → token da Página novo no .env): "
                  + ", ".join(sorted(set(falta_tot))))
        return 3
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Métricas dos Reels publicados (IG + FB), 5 dias depois.")
    ap.add_argument("acao", nargs="?", choices=["verificar"], help="verificar = confere permissões de insights")
    ap.add_argument("--dias", type=float, default=float(os.environ.get("METRICAS_DIAS", DIAS_PADRAO)),
                    help=f"idade mínima do post para ler (padrão {DIAS_PADRAO})")
    ap.add_argument("--slug", help="só este Reel")
    ap.add_argument("--forcar", action="store_true", help="lê já, mesmo antes dos N dias ou se já houver leitura")
    ap.add_argument("--dry-run", action="store_true", help="mostra os pedidos; não grava nada")
    a = ap.parse_args(argv)
    pub.configurar_log()
    http = pub.Http(a.dry_run)
    try:
        if a.acao == "verificar":
            return cmd_verificar(http)
        r = passagem(http, a.dias, a.slug, a.forcar)
    except pub.ErroPublicacao as e:
        log.error(f"✗ {e}")
        return 1
    if not r["lidos"] and not r["erros"]:
        log.info(f"nada a ler: nenhum Reel com ≥ {a.dias:g} dias sem leitura (use --slug X --forcar para ler já)")
        return 0
    log.info(f"leitura: {r['lidos']} Reel(s) — {', '.join(r['slugs']) or 'nenhum'}; {r['erros']} erro(s)")
    if r["permissoes_em_falta"]:
        falta = ", ".join(sorted(r["permissoes_em_falta"]))
        log.error(f"✗ permissão em falta: {falta}. O token não lê insights — gere um token novo com essas "
                  "permissões (Graph API Explorer) e troque no .env. Gravei só o que a Meta deixou ler.")
        pub.notificar("Korvu — métricas", f"Permissão em falta: {falta}", a.dry_run)
        return 3
    if r["lidos"]:
        pub.notificar("Korvu — métricas", f"Métricas lidas: {', '.join(r['slugs'])} — rode o analista-de-metricas",
                      a.dry_run)
    return 1 if r["erros"] else 0


if __name__ == "__main__":
    sys.exit(main())
