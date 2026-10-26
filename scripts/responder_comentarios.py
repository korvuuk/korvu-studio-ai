#!/usr/bin/env python3
"""Comentou a palavra-chave → resposta no comentário + material no direct (Instagram).

Sem servidor e sem conversa: o launchd roda isto a cada 2 min no Mac. Para cada Reel publicado nos
últimos 7 dias (07-publicados/<slug>/dm-material.json, escrito pelo publicar.py), lê os comentários,
acha os que têm a palavra do CTA e:
  1. manda UMA resposta privada (direct) com o link do material + convite para curtir e seguir;
  2. só depois responde em público no comentário ("já te mandei no direct").
Textos em automacao-meta/respostas.yaml. Estado (quem já recebeu) em _controle/comentarios/estado.json.

Uso (da raiz do projeto):
  uv run python scripts/responder_comentarios.py                 # uma passagem (o que o launchd chama)
  uv run python scripts/responder_comentarios.py --dry-run       # mostra os pedidos, não envia nem grava
  uv run python scripts/responder_comentarios.py --slug <slug>   # só um Reel
  uv run python scripts/responder_comentarios.py verificar       # confere tokens e permissões

Regras da Meta que moldam isto: 1 resposta privada por comentário, até 7 dias depois dele; outra
mensagem só se a pessoa responder. Por isso o material vai como LINK já na primeira mensagem.
Tokens: INSTAGRAM_ACCESS_TOKEN (ler/responder comentários) e META_PAGE_ACCESS_TOKEN (direct; cai no
token do IG se faltar). Nunca imprime tokens (mesma máscara do publicar.py).
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import json
import os
import random
import re
import sys
import unicodedata
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import publicar as pub  # noqa: E402  (reaproveita Http, máscara de segredos, log, notificação)

log = pub.log
ROOT = pub.ROOT
CONFIG = ROOT / "automacao-meta" / "respostas.yaml"
ESTADO = pub.CONTROLE / "comentarios" / "estado.json"
TRAVA = pub.CONTROLE / ".comentarios.lock"
GRAPH = pub.GRAPH
MAX_TENTATIVAS = 5
ESCOPOS = {"instagram_basic", "instagram_manage_comments", "instagram_manage_messages", "pages_read_engagement"}

# Erros DESTA pessoa/comentário em que repetir não adianta (indisponível, bloqueou, fora da janela)
SUBCODIGOS_PESSOA = {2018001, 2018108, 2018278, 2534014, 2534022, 1545041}
CODIGOS_PESSOA = {551}
# Erros de CONFIGURAÇÃO (token, permissão, app sem acesso): param a passagem SEM descartar ninguém
CODIGOS_CONFIG = {3, 10, 102, 190, 200}


class ErroConfig(pub.ErroPublicacao):
    pass


# ───────────────────────── texto ─────────────────────────

def normalizar(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c)).upper()


def tem_palavra(texto: str, palavra: str, plural: bool = True) -> bool:
    alvo = normalizar(palavra).strip()
    if not alvo:
        return False
    for p in re.findall(r"[A-Z0-9]+", normalizar(texto)):
        if p == alvo or (plural and p in (alvo + "S", alvo + "ES")):
            return True
    return False


def preencher(modelo: str, **v: str) -> str:
    out = modelo
    for k, val in v.items():
        out = out.replace("{" + k + "}", val)
    return out.strip()


# ───────────────────────── estado e config ─────────────────────────

def ler_config() -> dict:
    if not CONFIG.exists():
        raise pub.ErroPublicacao(f"Config não encontrada: {CONFIG}")
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}
    for k in ("respostas_publicas", "mensagem_direct"):
        if not cfg.get(k):
            raise pub.ErroPublicacao(f"respostas.yaml sem '{k}'")
    return cfg


def ler_estado() -> dict:
    if ESTADO.exists():
        return json.loads(ESTADO.read_text(encoding="utf-8"))
    return {"comentarios": {}}


def salvar_estado(est: dict, dry: bool) -> None:
    if dry:
        return
    ESTADO.parent.mkdir(parents=True, exist_ok=True)
    tmp = ESTADO.with_suffix(".tmp")
    tmp.write_text(json.dumps(est, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(ESTADO)


@contextlib.contextmanager
def trava():
    TRAVA.parent.mkdir(parents=True, exist_ok=True)
    f = open(TRAVA, "a+")
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        f.close()
        raise pub.Ocupado("Outra execução do responder_comentarios.py está em curso.")
    try:
        yield
    finally:
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()


# ───────────────────────── Reels ativos ─────────────────────────

def reels_ativos(janela_dias: float, so_slug: str | None) -> list[dict]:
    """Reels publicados há menos de `janela_dias` com palavra, media_id e link do material."""
    out = []
    limite = pub.agora() - dt.timedelta(days=janela_dias)
    for dm_arq in sorted(pub.PUBLICADOS.glob("*/dm-material.json")):
        pasta = dm_arq.parent
        slug = pasta.name
        if so_slug and slug != so_slug:
            continue
        dm = json.loads(dm_arq.read_text(encoding="utf-8"))
        post = pub.carregar_post(pasta) or {}
        quando = pub.ler_iso(post.get("publicado_em"))
        if not (dm.get("palavra") and dm.get("media_id_instagram")):
            continue
        if not dm.get("material_url"):
            log.warning(f"{slug}: tem palavra {dm['palavra']} mas nenhum link de material — não respondo")
            continue
        if quando and quando < limite:
            continue
        if str(dm["material_url"]).lower().endswith(".md"):
            log.warning(f"{slug}: o material é .md (não abre bem no celular) — converta para PDF")
        out.append({"slug": slug, "palavra": dm["palavra"], "media": str(dm["media_id_instagram"]),
                    "link": dm["material_url"],
                    "material": ((post.get("material") or {}).get("titulo") or "").strip()})
    return out


def comentarios(http: pub.Http, media: str, tok: str) -> list[dict]:
    url = f"{GRAPH}/{media}/comments"
    params = {"fields": "id,text,timestamp,username,from", "limit": 50, "access_token": tok}
    todos: list[dict] = []
    for _ in range(40):  # até 2000 comentários por Reel por passagem
        r = http.req("GET", url, params=params, fake={"data": []})
        todos += r.get("data", [])
        nxt = (r.get("paging") or {}).get("next")
        if not nxt:
            break
        url, params = nxt, None  # o "next" já traz os parâmetros (e o token, mascarado no log)
    return todos


# ───────────────────────── envio ─────────────────────────

def definitivo(e: Exception) -> bool:
    if isinstance(e, pub.ErroMeta) and not e.transitorio:
        return e.erro.get("error_subcode") in SUBCODIGOS_PESSOA or e.erro.get("code") in CODIGOS_PESSOA
    return False


def de_configuracao(e: Exception) -> bool:
    return isinstance(e, pub.ErroMeta) and not definitivo(e) and e.erro.get("code") in CODIGOS_CONFIG


def enviar_direct(http: pub.Http, uid: str, tok: str, comment_id: str, texto: str) -> str:
    r = http.req("POST", f"{GRAPH}/{uid}/messages",
                 data={"recipient": json.dumps({"comment_id": comment_id}),
                       "message": json.dumps({"text": texto}, ensure_ascii=False), "access_token": tok},
                 fake={"recipient_id": "DRYRUN", "message_id": "DRYRUN_MID"}, tentativas=3)
    return r.get("message_id") or "ok"


def responder_publico(http: pub.Http, comment_id: str, tok: str, texto: str) -> str:
    r = http.req("POST", f"{GRAPH}/{comment_id}/replies", data={"message": texto, "access_token": tok},
                 fake={"id": "DRYRUN_REPLY"}, tentativas=3)
    return r.get("id") or "ok"


def envios_na_ultima_hora(est: dict) -> int:
    lim = pub.agora() - dt.timedelta(hours=1)
    return sum(1 for c in est["comentarios"].values()
               if (t := pub.ler_iso(c.get("direct_em"))) and t >= lim)


def passagem(http: pub.Http, so_slug: str | None = None) -> dict:
    cfg = ler_config()
    res = {"reels": 0, "comentarios": 0, "com_palavra": 0, "directs": 0, "publicas": 0, "erros": 0}
    if not cfg.get("ativo", True):
        log.info("respostas.yaml: ativo=false — nada a fazer")
        return res
    dry = http.dry
    uid = pub._cred("INSTAGRAM_USER_ID", dry)
    tok_ig = pub._cred("INSTAGRAM_ACCESS_TOKEN", dry)
    tok_dm = os.environ.get("META_PAGE_ACCESS_TOKEN") or tok_ig
    # Login do Facebook: a resposta privada sai pela Página (/{page-id}/messages); /{ig-user-id}/messages
    # dá "(#3) Application does not have the capability" (13/10).
    remetente_dm = os.environ.get("META_PAGE_ID") or uid
    est = ler_estado()
    vistos = est["comentarios"]
    max_exec = int(cfg.get("max_envios_por_execucao", 25))
    max_hora = int(cfg.get("max_envios_por_hora", 150))
    pausa = float(cfg.get("intervalo_entre_envios_s", 4))
    janela = float(cfg.get("janela_dias", 7))
    plural = bool(cfg.get("aceitar_plural", True))
    feitos = 0

    reels = reels_ativos(janela, so_slug)
    res["reels"] = len(reels)
    for reel in reels:
        try:
            lista = comentarios(http, reel["media"], tok_ig)
        except pub.ErroPublicacao as e:
            if de_configuracao(e):
                raise ErroConfig(f"Não consigo ler comentários (token/permissão): {e}")
            res["erros"] += 1
            log.error(f"{reel['slug']}: não consegui ler os comentários: {e}")
            continue
        res["comentarios"] += len(lista)
        ja_receberam = {c.get("usuario_id") for c in vistos.values()
                        if c.get("media") == reel["media"] and c.get("direct")}
        for c in sorted(lista, key=lambda x: x.get("timestamp") or ""):
            cid = c.get("id")
            autor = c.get("from") or {}
            autor_id, usuario = str(autor.get("id") or ""), autor.get("username") or c.get("username") or ""
            if not cid or autor_id == str(uid) or not tem_palavra(c.get("text", ""), reel["palavra"], plural):
                continue
            reg = vistos.get(cid)
            if reg and reg.get("final"):
                continue
            res["com_palavra"] += 1
            criado = pub.ler_iso((c.get("timestamp") or "").replace("+0000", "+00:00"))
            if not reg:
                reg = vistos[cid] = {"slug": reel["slug"], "media": reel["media"], "usuario": usuario,
                                     "usuario_id": autor_id, "texto": (c.get("text") or "")[:200],
                                     "comentado_em": c.get("timestamp"), "visto_em": pub.iso(pub.agora()),
                                     "direct": None, "publica": None, "tentativas": 0, "erro": None,
                                     "final": False}
                if autor_id and autor_id in ja_receberam:
                    reg.update(final=True, erro="já recebeu este material")
                    log.info(f"{reel['slug']}: @{usuario} comentou de novo — já recebeu, ignoro")
                    continue
            if criado and pub.agora() - criado > dt.timedelta(days=janela):
                reg.update(final=True, erro="fora da janela de 7 dias")
                continue
            if feitos >= max_exec or envios_na_ultima_hora(est) >= max_hora:
                log.info("limite de envios atingido — continua na próxima passagem")
                salvar_estado(est, dry)
                return res
            nome = f"@{usuario}" if usuario else "você"
            try:
                if not reg["direct"]:
                    texto = preencher(cfg["mensagem_direct"], usuario=usuario or "tudo bem",
                                      material=reel["material"] or cfg.get("material_padrao", "o material"),
                                      link=reel["link"])
                    reg["direct"] = enviar_direct(http, remetente_dm, tok_dm, cid, texto)
                    reg["direct_em"] = pub.iso(pub.agora())
                    res["directs"] += 1
                    feitos += 1
                    ja_receberam.add(autor_id)
                    log.info(f"{reel['slug']}: direct ✓ para {nome} ({reel['palavra']})")
                    salvar_estado(est, dry)
                if not reg["publica"]:
                    texto = preencher(random.choice(cfg["respostas_publicas"]), usuario=usuario or "")
                    reg["publica"] = responder_publico(http, cid, tok_ig, texto)
                    res["publicas"] += 1
                    log.info(f"{reel['slug']}: resposta pública ✓ para {nome}")
                reg.update(final=True, erro=None)
            except pub.ErroPublicacao as e:
                res["erros"] += 1
                if de_configuracao(e):
                    salvar_estado(est, dry)
                    raise ErroConfig(f"Parei a passagem — problema de token/permissão, ninguém foi descartado: {e}")
                reg["tentativas"] += 1
                reg["erro"] = pub.mascarar(str(e))[:300]
                if definitivo(e) or reg["tentativas"] >= MAX_TENTATIVAS:
                    reg["final"] = True
                    log.error(f"{reel['slug']}: desisti de {nome} ({'erro definitivo' if definitivo(e) else 'tentativas esgotadas'}): {e}")
                else:
                    log.warning(f"{reel['slug']}: falhou para {nome}, tento de novo na próxima passagem: {e}")
            salvar_estado(est, dry)
            if not dry:
                pub.dormir(pausa)
    salvar_estado(est, dry)
    return res


def cmd_verificar(http: pub.Http) -> int:
    """Confere se os tokens têm as permissões de comentários e de direct."""
    app, sec = os.environ.get("META_APP_ID"), os.environ.get("META_APP_SECRET")
    problemas = 0
    for nome, var in (("token IG", "INSTAGRAM_ACCESS_TOKEN"), ("token Página", "META_PAGE_ACCESS_TOKEN")):
        tok = os.environ.get(var)
        if not tok:
            log.warning(f"{var} em falta")
            problemas += var == "INSTAGRAM_ACCESS_TOKEN"
            continue
        if not (app and sec):
            log.info("(META_APP_ID/META_APP_SECRET ausentes — não dá para listar as permissões)")
            break
        try:
            d = http.req("GET", f"{GRAPH}/debug_token", params={"input_token": tok, "access_token": f"{app}|{sec}"},
                         fake={"data": {"is_valid": True, "scopes": sorted(ESCOPOS)}}).get("data", {})
        except pub.ErroPublicacao as e:
            problemas += 1
            log.error(f"✗ {nome}: {e}")
            continue
        falta = sorted(ESCOPOS - set(d.get("scopes") or []))
        log.info(f"{'✓' if d.get('is_valid') and not falta else '✗'} {nome}: válido={d.get('is_valid')}"
                 + (f" | falta: {', '.join(falta)}" if falta else ""))
        problemas += bool(falta or not d.get("is_valid"))
    log.info(f"Reels na janela: {[r['slug'] for r in reels_ativos(7, None)] or 'nenhum'}")
    return 1 if problemas else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Palavra-chave no comentário → material no direct.")
    ap.add_argument("acao", nargs="?", choices=["verificar"], help="verificar = confere tokens/permissões")
    ap.add_argument("--dry-run", action="store_true", help="mostra os pedidos; não envia nem grava")
    ap.add_argument("--slug", help="só este Reel")
    a = ap.parse_args(argv)
    pub.configurar_log()
    http = pub.Http(a.dry_run)
    try:
        if a.acao == "verificar":
            return cmd_verificar(http)
        with trava():
            r = passagem(http, a.slug)
    except ErroConfig as e:
        log.error(str(e))
        if not a.dry_run:
            aviso = pub.CONTROLE / "comentarios" / ".ultimo-aviso-erro"
            if not aviso.exists() or (dt.datetime.now().timestamp() - aviso.stat().st_mtime) > 3600:
                aviso.parent.mkdir(parents=True, exist_ok=True)
                aviso.touch()
                pub.notificar("Korvu — comentários", "Token ou permissão da Meta com problema — rode verificar")
        return 1
    except pub.Ocupado as e:
        log.info(str(e))
        return 0
    except pub.ErroPublicacao as e:
        log.error(str(e))
        return 1
    if r["directs"]:
        pub.notificar("Korvu — comentários", f"{r['directs']} material(is) enviado(s) no direct", a.dry_run)
    if r["erros"] and not a.dry_run:
        aviso = pub.CONTROLE / "comentarios" / ".ultimo-aviso-erro"
        if not aviso.exists() or (dt.datetime.now().timestamp() - aviso.stat().st_mtime) > 3600:
            aviso.parent.mkdir(parents=True, exist_ok=True)
            aviso.touch()
            pub.notificar("Korvu — comentários", f"{r['erros']} erro(s) — veja _controle/logs/comentarios.log")
    log.info(f"passagem: {r['reels']} Reel(s), {r['comentarios']} comentário(s), {r['com_palavra']} com a palavra, "
             f"{r['directs']} direct(s), {r['publicas']} resposta(s) pública(s), {r['erros']} erro(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
