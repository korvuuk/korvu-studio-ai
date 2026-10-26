"""Teste do scripts/metricas.py contra uma Meta simulada (sem rede).

Uso (da raiz do projeto):  uv run python tests/metricas/test_metricas.py
"""
from __future__ import annotations

import contextlib
import io
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PROJETO = AQUI.parent.parent
ROOT = Path(tempfile.mkdtemp(prefix="korvu-metricas-"))
TOK_IG, TOK_PG = "EAAGtesteIG1234567890SEGREDOabcdefXYZ", "EAAGpaginaPG0987654321SEGREDOqwertyUIO"
os.environ.update(CONTENT_AI_ROOT=str(ROOT), CONTENT_AI_NO_DOTENV="1", CONTENT_AI_AGORA="2026-10-20T10:00:00+01:00",
                  PUBLICAR_SEM_NOTIFICACAO="1", INSTAGRAM_USER_ID="17841400000000000",
                  INSTAGRAM_ACCESS_TOKEN=TOK_IG, META_PAGE_ACCESS_TOKEN=TOK_PG)
sys.path.insert(0, str(PROJETO / "scripts"))
import publicar as pub  # noqa: E402
import metricas as mt  # noqa: E402

pub.dormir = lambda s: None
RES: list[bool] = []


def ok(nome: str, cond, det: str = "") -> None:
    RES.append(bool(cond))
    print(f"  [{'PASS' if cond else 'FAIL'}] {nome}" + (f" — {det}" if det else ""))


def reel(slug: str, media: str, video: str | None, publicado: str, duracao: float = 50.0,
         estado: str = "publicado", trial=None) -> Path:
    p = ROOT / "07-publicados" / slug
    p.mkdir(parents=True)
    (p / "post.json").write_text(json.dumps({
        "slug": slug, "estado": estado, "publicado_em": publicado,
        "instagram": {"media_id": media, "permalink": f"https://ig.test/{media}", "trial": trial},
        "facebook": {"video_id": video} if video else {},
        "material": {"palavra": "PROMPT"}}))
    (p / "pacote.json").write_text(json.dumps({"duracao": duracao, "cta_palavra": "PROMPT", "tema": slug,
                                               "pilar": "tutoriais-rapidos"}))
    return p


IG_VALORES = {"views": 2000, "reach": 1000, "likes": 50, "comments": 20, "saved": 30, "shares": 10,
              "total_interactions": 110, "ig_reels_avg_watch_time": 12500, "ig_reels_video_view_total_time": 25000000}
FB_VALORES = {"blue_reels_play_count": 400, "post_video_avg_time_watched": 8000, "post_impressions_unique": 300}


class MetaFalsa(pub.Http):
    """IG: follows/profile_visits não valem para Reels (#100). FB: só as métricas de FB_VALORES existem.
    sem_ig / sem_fb = token sem instagram_manage_insights / read_insights."""

    def __init__(self, sem_ig: bool = False, sem_fb: bool = False, recusar_ig: tuple = ("follows", "profile_visits")):
        super().__init__(False)
        self.sem_ig, self.sem_fb, self.recusar_ig, self.chamadas = sem_ig, sem_fb, set(recusar_ig), []

    def req(self, metodo, url, *, params=None, data=None, headers=None, fake=None, tentativas=5, timeout=60):
        params = params or {}
        self.chamadas.append((metodo, url, dict(params)))
        assert metodo == "GET", f"metricas.py só pode LER ({metodo} {url})"
        if url.endswith("/insights"):
            if self.sem_ig:
                raise pub.ErroMeta(403, {"code": 10, "message": "(#10) Application does not have permission "
                                                                "for this action"}, url)
            pedidas = params["metric"].split(",")
            ruins = [m for m in pedidas if m in self.recusar_ig]
            if ruins:
                raise pub.ErroMeta(400, {"code": 100, "message": f"(#100) metric[0] must be one of … ({ruins[0]})"}, url)
            return {"data": [{"name": m, "period": "lifetime", "values": [{"value": IG_VALORES.get(m, 0)}]}
                             for m in pedidas]}
        if url.endswith("/video_insights"):
            if self.sem_fb:
                raise pub.ErroMeta(400, {"code": 200, "message": "(#200) requires read_insights permission"}, url)
            pedidas = params["metric"].split(",")
            if any(m not in FB_VALORES for m in pedidas):
                raise pub.ErroMeta(400, {"code": 100, "message": "(#100) The value must be a valid insights metric"},
                                   url)
            return {"data": [{"name": m, "period": "lifetime", "values": [{"value": FB_VALORES[m]}]}
                             for m in pedidas]}
        if params.get("fields") == "trial_params":
            raise pub.ErroMeta(400, {"code": 100, "message": "Tried accessing nonexisting field (trial_params)"}, url)
        if "fields" in params:
            return {"id": url.split("/")[-1], "like_count": 48, "comments_count": 19, "media_product_type": "REELS"}
        raise AssertionError(f"pedido inesperado {metodo} {url}")

    def lidos(self, sufixo: str) -> list[str]:
        return sorted({u.split("/")[-2] for m, u, p in self.chamadas if u.endswith(sufixo)})


def main() -> int:
    (ROOT / "_controle" / "comentarios").mkdir(parents=True)
    (ROOT / "_controle" / "comentarios" / "estado.json").write_text(json.dumps({"comentarios": {
        "c1": {"media": "M1", "usuario_id": "u1", "direct": "mid1"},
        "c2": {"media": "M1", "usuario_id": "u2", "direct": "mid2"},
        "c3": {"media": "M1", "usuario_id": "u3", "direct": None},
        "c9": {"media": "OUTRO", "usuario_id": "u9", "direct": "mid9"}}}))
    reel("2026-10-10-velho", "M1", "V1", "2026-10-10T19:00:00+01:00", duracao=50.0)   # 9,6 dias
    reel("2026-10-15-cinco", "M2", None, "2026-10-15T09:00:00+01:00")                 # 5,04 dias
    reel("2026-10-18-novo", "M3", "V3", "2026-10-18T19:00:00+01:00")                  # 1,6 dia
    reel("2026-10-10-erro", "M4", None, "2026-10-10T19:00:00+01:00", estado="erro")   # não publicado

    print("escolha dos Reels")
    escolhidos = [r["slug"] for r in mt.reels_para_ler(5, None, False)]
    ok("só os com ≥ 5 dias e publicados", escolhidos == ["2026-10-10-velho", "2026-10-15-cinco"], str(escolhidos))
    ok("--slug sem --forcar respeita os 5 dias", mt.reels_para_ler(5, "2026-10-18-novo", False) == [])
    ok("--slug --forcar lê já", [r["slug"] for r in mt.reels_para_ler(5, "2026-10-18-novo", True)] == ["2026-10-18-novo"])
    ok("--dias 1 inclui o novo", "2026-10-18-novo" in [r["slug"] for r in mt.reels_para_ler(1, None, False)])

    print("dry-run (não grava nada)")
    buf = io.StringIO()
    pub.configurar_log()
    h = logging.StreamHandler(buf)
    pub.log.addHandler(h)
    rc = mt.main(["--dry-run"])
    ok("dry-run sai 0", rc == 0, str(rc))
    ok("dry-run não grava metricas.json nem a tabela",
       not list((ROOT / "07-publicados").glob("*/metricas.json")) and not mt.TABELA.exists())
    ok("dry-run mascara o token", TOK_IG not in buf.getvalue() and "access_token" in buf.getvalue())

    print("leitura completa")
    meta = MetaFalsa()
    r = mt.passagem(meta)
    ok("leu os dois Reels com ≥ 5 dias", r["slugs"] == ["2026-10-10-velho", "2026-10-15-cinco"], str(r["slugs"]))
    hist = json.loads((ROOT / "07-publicados" / "2026-10-10-velho" / "metricas.json").read_text())
    u = hist["ultima"]
    s = u["resumo"]["instagram"]
    ok("métricas do IG gravadas", u["instagram"]["metricas"]["reach"] == 1000 and s["views"] == 2000)
    ok("métrica não suportada não quebra (follows/profile_visits)",
       set(u["instagram"]["nao_suportadas"]) == {"follows", "profile_visits"} and len(u["instagram"]["metricas"]) == 9,
       str(u["instagram"]["nao_suportadas"]))
    ok("não suportada não é pedida de novo no 2.º Reel",
       not any("follows" in p.get("metric", "") for m, url, p in meta.chamadas[-12:] if "M2" in url))
    ok("tempo médio 12,5 s e 25% assistido (vídeo de 50 s)",
       s["tempo_medio_s"] == 12.5 and s["pct_medio_assistido"] == 25.0, f"{s['tempo_medio_s']} {s['pct_medio_assistido']}")
    tx = s["taxas_sobre_alcance_pct"]
    ok("taxas sobre o alcance", tx == {"salvamentos": 3.0, "comentarios": 2.0, "compartilhamentos": 1.0,
                                       "curtidas": 5.0, "comentarios_palavra": 0.3}, str(tx))
    ok("palavra-chave: 3 comentários, 2 directs (só deste media)",
       u["comentarios_palavra"]["com_palavra"] == 3 and u["comentarios_palavra"]["directs"] == 2)
    fb = u["resumo"]["facebook"]
    ok("FB: fica só o que respondeu", fb["plays"] == 400 and fb["tempo_medio_s"] == 8.0 and fb["pct_medio_assistido"] == 16.0
       and "fb_reels_total_plays" in u["facebook"]["nao_suportadas"], str(fb))
    ok("trial_params ausente registrado sem quebrar", "trial_params" in str(u["instagram"]["trial"]))
    ok("nota sobre a curva de retenção", "segundo a segundo" in hist["nota_retencao"])
    ok("sem token no metricas.json", TOK_IG not in json.dumps(hist) and TOK_PG not in json.dumps(hist))
    tab = mt.TABELA.read_text()
    ok("tabela com uma linha por vídeo", tab.count("| 2026-10-10-velho |") == 1 and tab.count("| 2026-10-15-cinco |") == 1)
    ok("tabela mostra % assistido e taxa de salvamento", "| 25% |" in tab and "| 3% |" in tab)
    ok("só leituras (nenhum POST)", all(m == "GET" for m, u_, p in meta.chamadas))

    print("histórico")
    meta2 = MetaFalsa()
    r2 = mt.passagem(meta2)
    ok("não relê quem já tem leitura completa", r2["lidos"] == 0 and not meta2.chamadas)
    IG_VALORES["reach"] = 1500
    mt.passagem(MetaFalsa(), so_slug="2026-10-10-velho", forcar=True)
    hist = json.loads((ROOT / "07-publicados" / "2026-10-10-velho" / "metricas.json").read_text())
    ok("--forcar acrescenta leitura e mantém a antiga",
       len(hist["leituras"]) == 2 and hist["leituras"][0]["instagram"]["metricas"]["reach"] == 1000
       and hist["ultima"]["instagram"]["metricas"]["reach"] == 1500)
    tab = mt.TABELA.read_text()
    ok("tabela continua com uma linha por vídeo", tab.count("| 2026-10-10-velho |") == 1 and "| 1500 |" in tab)

    print("permissão em falta")
    os.environ["CONTENT_AI_AGORA"] = "2026-10-25T10:00:00+01:00"
    meta_p = MetaFalsa(sem_ig=True, sem_fb=True)
    mt.pub.Http = lambda dry: meta_p  # main() cria o Http
    try:
        rc = mt.main([])
    finally:
        mt.pub.Http = MetaFalsa.__mro__[1]
    novo = json.loads((ROOT / "07-publicados" / "2026-10-18-novo" / "metricas.json").read_text())["ultima"]
    ok("sai com código 3", rc == 3, str(rc))
    ok("registra 'permissão em falta' (IG e FB)",
       novo["instagram"]["erro"].startswith("permissão em falta: instagram_manage_insights")
       and novo["facebook"]["permissao_em_falta"] == "read_insights", novo["instagram"].get("erro", "")[:80])
    ok("grava o que deu para ler (curtidas/comentários do GET /media)",
       novo["resumo"]["instagram"]["curtidas"] == 48 and novo["resumo"]["instagram"]["comentarios"] == 19)
    ok("leitura sem insights não conta como completa (tenta de novo amanhã)",
       [x["slug"] for x in mt.reels_para_ler(5, None, False)] == ["2026-10-18-novo"])
    ok("mensagem clara em PT-BR", "permissão em falta: instagram_manage_insights, read_insights" in buf.getvalue())
    ok("tabela marca a permissão em falta", "permissão em falta" in mt.TABELA.read_text())

    print("launchd")
    gerado = ROOT / "uk.korvu.metricas.plist"
    p = subprocess.run(["bash", str(PROJETO / "scripts/launchd/instalar.sh"), "--so-gerar", str(gerado),
                        "uk.korvu.metricas"], capture_output=True, text=True)
    txt = gerado.read_text() if gerado.exists() else ""
    ok("plist gerado e válido, 1×/dia às 09:30, sem instalar",
       p.returncode == 0 and "__" not in txt and "scripts/metricas.py" in txt and "<integer>9</integer>" in txt
       and "<integer>30</integer>" in txt and "_controle/logs/metricas.log" in txt, p.stderr.strip())
    ok("instalar.sh/desinstalar.sh conhecem o label",
       all("uk.korvu.metricas" in (PROJETO / "scripts/launchd" / f).read_text()
           for f in ("instalar.sh", "desinstalar.sh")))

    pub.log.removeHandler(h)
    with contextlib.suppress(Exception):
        shutil.rmtree(ROOT, ignore_errors=True)
    print(f"\n{sum(RES)}/{len(RES)} verificações OK")
    return 0 if all(RES) else 1


if __name__ == "__main__":
    sys.exit(main())
