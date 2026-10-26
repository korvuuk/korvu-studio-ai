"""Teste do scripts/responder_comentarios.py contra uma Meta simulada (sem rede).

Uso (da raiz do projeto):  uv run python tests/comentarios/test_responder.py
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PROJETO = AQUI.parent.parent
ROOT = Path(tempfile.mkdtemp(prefix="korvu-coment-"))
IG_ID, TOKEN = "17841400000000000", "EAAGtesteIG1234567890SEGREDOabcdefXYZ"
os.environ.update(CONTENT_AI_ROOT=str(ROOT), CONTENT_AI_NO_DOTENV="1", CONTENT_AI_AGORA="2026-10-09T12:00:00+01:00",
                  PUBLICAR_SEM_NOTIFICACAO="1", INSTAGRAM_USER_ID=IG_ID, INSTAGRAM_ACCESS_TOKEN=TOKEN)
os.environ.pop("META_PAGE_ACCESS_TOKEN", None)
sys.path.insert(0, str(PROJETO / "scripts"))
import publicar as pub  # noqa: E402
import responder_comentarios as rc  # noqa: E402

pub.dormir = lambda s: None
RES: list[bool] = []


def ok(nome: str, cond, det: str = "") -> None:
    RES.append(bool(cond))
    print(f"  [{'PASS' if cond else 'FAIL'}] {nome}" + (f" — {det}" if det else ""))


def reel(slug: str, media: str, palavra: str, publicado: str, url: str | None = "https://m.test/guia.pdf") -> None:
    p = ROOT / "07-publicados" / slug
    p.mkdir(parents=True)
    (p / "dm-material.json").write_text(json.dumps({"palavra": palavra, "media_id_instagram": media,
                                                    "material_url": url}))
    (p / "post.json").write_text(json.dumps({"publicado_em": publicado,
                                             "material": {"palavra": palavra, "titulo": "o guia do prompt"}}))


def com(cid: str, texto: str, uid: str, user: str, ts: str = "2026-10-09T10:00:00+0000") -> dict:
    return {"id": cid, "text": texto, "timestamp": ts, "username": user, "from": {"id": uid, "username": user}}


class MetaFalsa(pub.Http):
    def __init__(self, comentarios: dict, falhas: dict | None = None):
        super().__init__(False)
        self.coments, self.falhas, self.chamadas = comentarios, falhas or {}, []

    def req(self, metodo, url, *, params=None, data=None, headers=None, fake=None, tentativas=5, timeout=60):
        self.chamadas.append((metodo, url, data))
        if metodo == "GET" and url.endswith("/comments"):
            media = url.split("/")[-2]
            return {"data": self.coments.get(media, [])}
        if url.endswith("/messages"):
            cid = json.loads(data["recipient"])["comment_id"]
            if cid in self.falhas:
                raise pub.ErroMeta(400, self.falhas[cid], url)
            return {"recipient_id": "x", "message_id": f"mid-{cid}"}
        if url.endswith("/replies"):
            return {"id": f"rep-{url.split('/')[-2]}"}
        raise AssertionError(f"pedido inesperado {metodo} {url}")

    def directs(self):
        return [json.loads(d["recipient"])["comment_id"] for m, u, d in self.chamadas if u.endswith("/messages")]

    def publicas(self):
        return [u.split("/")[-2] for m, u, d in self.chamadas if u.endswith("/replies")]


def main() -> int:
    (ROOT / "_controle").mkdir()
    (ROOT / "automacao-meta").mkdir()
    shutil.copy(PROJETO / "automacao-meta" / "respostas.yaml", ROOT / "automacao-meta" / "respostas.yaml")
    reel("2026-10-07-prompt", "M1", "PROMPT", "2026-10-07T19:00:00+01:00")
    reel("2026-09-20-velho", "M2", "GUIA", "2026-09-20T19:00:00+01:00")      # fora dos 7 dias
    reel("2026-10-08-semlink", "M3", "LISTA", "2026-10-08T19:00:00+01:00", url=None)

    print("palavra-chave")
    ok("acento/maiúscula/pontuação", rc.tem_palavra("quero o prómpt!!! 🙏", "PROMPT"))
    ok("plural aceito", rc.tem_palavra("prompts por favor", "PROMPT"))
    ok("plural recusado se desligado", not rc.tem_palavra("prompts", "PROMPT", plural=False))
    ok("dentro de outra palavra não conta", not rc.tem_palavra("superprompting", "PROMPT"))
    ok("sem a palavra", not rc.tem_palavra("adorei o vídeo", "PROMPT"))

    meta = MetaFalsa({
        "M1": [com("c1", "PROMPT", "u1", "ana"),
               com("c2", "adorei", "u2", "bia"),
               com("c3", "Prompt 🙏", IG_ID, "korvu_oficial"),           # a própria conta
               com("c4", "prompt de novo", "u1", "ana", "2026-10-09T10:05:00+0000"),  # mesma pessoa
               com("c5", "prompt", "u5", "caio"),                          # DM fechado (definitivo)
               com("c6", "PROMPT", "u6", "duda")],                         # falha transitória
        "M2": [com("v1", "GUIA", "u9", "eva")],
        "M3": [com("s1", "LISTA", "u9", "eva")],
    }, falhas={"c5": {"code": 100, "error_subcode": 2534022, "message": "fora da janela"},
               "c6": {"code": 2, "is_transient": True, "message": "temporário"}})
    print("primeira passagem")
    r = rc.passagem(meta)
    ok("só lê o Reel dentro da janela e com link", [u.split("/")[-2] for m, u, d in meta.chamadas if m == "GET"] == ["M1"])
    ok("direct para ana", "c1" in meta.directs())
    ok("não responde quem não comentou a palavra", "c2" not in meta.directs())
    ok("não responde a própria conta", "c3" not in meta.directs())
    ok("mesma pessoa não recebe duas vezes", "c4" not in meta.directs())
    ok("resposta pública só depois do direct", meta.publicas() == ["c1"], str(meta.publicas()))
    txt = json.loads(next(d for m, u, d in meta.chamadas if u.endswith("/messages"))["message"])["text"]
    ok("direct tem link, material, @ e convite para seguir",
       all(x in txt for x in ("https://m.test/guia.pdf", "o guia do prompt", "@ana", "@korvu_oficial")), txt[:80])
    ok("sem token no estado", TOKEN not in rc.ESTADO.read_text())
    est = json.loads(rc.ESTADO.read_text())["comentarios"]
    ok("erro definitivo encerra (c5)", est["c5"]["final"] and est["c5"]["direct"] is None)
    ok("erro transitório fica para tentar de novo (c6)", not est["c6"]["final"] and est["c6"]["tentativas"] == 1)
    ok("contagem", r["directs"] == 1 and r["publicas"] == 1, str(r))

    print("segunda passagem (c6 volta a funcionar)")
    meta2 = MetaFalsa(meta.coments)
    rc.passagem(meta2)
    ok("não reenvia para ana", "c1" not in meta2.directs())
    ok("não tenta de novo o definitivo", "c5" not in meta2.directs())
    ok("c6 recebe agora", meta2.directs() == ["c6"] and meta2.publicas() == ["c6"], str(meta2.directs()))

    print("sem permissão (app ainda não liberado)")
    meta_p = MetaFalsa({"M1": [com("p1", "prompt", "w1", "fe"), com("p2", "prompt", "w2", "gi")]},
                       falhas={"p1": {"code": 10, "message": "Application does not have permission"}})
    try:
        rc.passagem(meta_p)
        ok("erro de permissão para a passagem", False)
    except rc.ErroConfig:
        ok("erro de permissão para a passagem", True)
    est = json.loads(rc.ESTADO.read_text())["comentarios"]
    ok("ninguém descartado por falta de permissão", not est["p1"]["final"] and est["p1"]["tentativas"] == 0)
    ok("não tentou o resto na mesma passagem", meta_p.directs() == ["p1"])
    meta_p2 = MetaFalsa(meta_p.coments)
    rc.passagem(meta_p2)
    ok("depois de liberado, os dois recebem", meta_p2.directs() == ["p1", "p2"], str(meta_p2.directs()))

    print("limite por execução")
    (ROOT / "07-publicados" / "2026-10-07-prompt" / "dm-material.json").unlink()
    reel("2026-10-09-muitos", "M4", "IA", "2026-10-09T08:00:00+01:00")
    cfg = rc.CONFIG.read_text().replace("max_envios_por_execucao: 25", "max_envios_por_execucao: 3")
    rc.CONFIG.write_text(cfg)
    meta3 = MetaFalsa({"M4": [com(f"m{i}", "ia", f"x{i}", f"p{i}") for i in range(10)]})
    rc.passagem(meta3)
    ok("para em 3 envios", len(meta3.directs()) == 3)

    print("desligado")
    rc.CONFIG.write_text(cfg.replace("ativo: true", "ativo: false"))
    meta4 = MetaFalsa({"M4": [com("z1", "ia", "z", "zz")]})
    rc.passagem(meta4)
    ok("ativo=false não chama a Meta", not meta4.chamadas)

    shutil.rmtree(ROOT, ignore_errors=True)
    print(f"\n{sum(RES)}/{len(RES)} verificações OK")
    return 0 if all(RES) else 1


if __name__ == "__main__":
    sys.exit(main())
