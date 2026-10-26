#!/usr/bin/env python3
"""Procura no YouTube os vídeos de que o roteiro precisa, baixa e cataloga — material de COMENTÁRIO.

Decisão do Carlos (2026-10-01): "a gente não vai baixar o vídeo do YouTube e passar no Reels… a gente vai
analisar o vídeo para falar sobre a pessoa". O Reel da Korvu é narração/análise por cima: os vídeos baixados
são o objeto do comentário (quem é a pessoa, o que fez, o que disse), não imagem bonita de fundo.
Por isso qualquer vídeo pode ser baixado para estudo; o que ENTRA no Reel segue as condições do formato
comentário/reação (docs/decisoes.md §5): trecho curto, mudo por padrão, crédito na tela, teto de citação.

Diferença para os outros scripts:
  baixar_obra.py    UMA obra que o Carlos indicou (o documentário de que o Reel fala)
  buscar_video.py   B-roll com licença legível (archive.org, Commons, press kit)
  ESTE              o agente PROCURA sozinho, a partir do roteiro, vários vídeos sobre o assunto

Como fica no disco:
  videos/<slug>/material/youtube/<id>-<titulo>.mp4   cópia de ESTUDO, inteira — nunca publicada
  videos/<slug>/material/youtube/catalogo.json       procedência + momentos anotados + trechos cortados
  videos/<slug>/material/youtube/catalogo.md         a "página" do material para o Carlos ver
  videos/<slug>/brutos/extras/<ID>-*.mp4             só os TRECHOS curtos que entram no Reel

Uso:
  uv run python scripts/buscar_youtube.py buscar "<consulta>" [--n 8] [--cc]
  uv run python scripts/buscar_youtube.py baixar <url> <slug> --linhas L02,L03 --motivo "..."
  uv run python scripts/buscar_youtube.py momento <slug> <video_id> 12:30 12:38 --linha L05 --o-que "..."
  uv run python scripts/buscar_youtube.py trecho <slug> <ID> <video_id> 12:30 12:38 --o-que "..." [--som]
  uv run python scripts/buscar_youtube.py catalogo <slug>
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baixar_obra as bo  # noqa: E402  (mesmas regras de proxy, tempos e teto de citação)

RAIZ = bo.RAIZ
FPS = bo.FPS


def ytdlp() -> list[str]:
    exe = shutil.which("yt-dlp")
    return [exe] if exe else [sys.executable, "-m", "yt_dlp"]


def pasta(slug: str) -> Path:
    p = bo.pasta_video(slug) / "material" / "youtube"
    p.mkdir(parents=True, exist_ok=True)
    return p


def ler_catalogo(slug: str) -> list[dict]:
    p = pasta(slug) / "catalogo.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else []


def escrever_catalogo(slug: str, cat: list[dict]) -> None:
    d = pasta(slug)
    (d / "catalogo.json").write_text(json.dumps(cat, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (d / "catalogo.md").write_text(catalogo_md(slug, cat), encoding="utf-8")


def achar(cat: list[dict], vid: str) -> dict:
    for v in cat:
        if v["id"] == vid:
            return v
    raise SystemExit(f"[erro] vídeo {vid} não está no catálogo — baixe primeiro com 'baixar'.")


def total_citado(slug: str, excluir: str | None = None) -> float:
    """Soma TUDO o que o Reel cita de terceiros: trechos deste catálogo + trechos da obra (baixar_obra).
    O teto é do Reel, não de cada fonte."""
    total = sum(float(t["duracao_s"]) for v in ler_catalogo(slug) for t in v.get("trechos", [])
                if t["id"] != excluir)
    if bo.caminho_obra_json(slug).is_file():
        total += sum(float(t["duracao_s"]) for t in bo.ler_obra(slug).get("trechos", []) if t["id"] != excluir)
    return total


# ------------------------------------------------------------------ buscar
def cmd_buscar(a: argparse.Namespace) -> int:
    if a.cc:
        # sp=EgIwAQ== é o filtro "Creative Commons" da própria busca do YouTube.
        alvo = f"https://www.youtube.com/results?search_query={a.consulta.replace(' ', '+')}&sp=EgIwAQ%253D%253D"
        cmd = ytdlp() + ["--flat-playlist", "--playlist-end", str(a.n), "--dump-json", "--no-warnings", alvo]
    else:
        cmd = ytdlp() + ["--flat-playlist", "--dump-json", "--no-warnings", f"ytsearch{a.n}:{a.consulta}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"[erro] a busca falhou: {(r.stderr or '').strip().splitlines()[-1:]}")
    achados = [json.loads(l) for l in r.stdout.splitlines() if l.strip().startswith("{")]
    if not achados:
        print("Nada encontrado — tente outra consulta (em inglês costuma haver mais material).")
        return 0
    for i, v in enumerate(achados, 1):
        dur = bo.hms(float(v.get("duration") or 0)) if v.get("duration") else "?"
        vis = v.get("view_count")
        vis = f"{vis:,}".replace(",", ".") + " vis." if vis else ""
        print(f"{i:2d}. [{dur:>8}] {v.get('title')}\n    canal: {v.get('channel') or v.get('uploader')} · {vis}\n"
              f"    https://www.youtube.com/watch?v={v.get('id')}")
    return 0


# ------------------------------------------------------------------ baixar
def fps_de(arq: Path) -> float:
    r = subprocess.run([bo.ffprobe(), "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=avg_frame_rate", "-of", "default=nw=1:nk=1", str(arq)], capture_output=True, text=True)
    try:
        n, d = (r.stdout.strip() or "0/1").split("/")
        return float(n) / float(d)
    except (ValueError, ZeroDivisionError):
        return 0.0


def cmd_baixar(a: argparse.Namespace) -> int:
    destino = pasta(a.slug)
    m = bo.metadados(a.url)
    vid = m.get("id") or re.sub(r"\W", "", a.url)[-11:]
    cat = ler_catalogo(a.slug)
    existente = next((v for v in cat if v["id"] == vid), None)
    if existente and existente.get("arquivo") and (RAIZ / existente["arquivo"]).is_file():
        print(f"[youtube] já baixado: {existente['arquivo']} — só atualizo linhas/motivo.")
        item = existente
    else:
        titulo = m.get("title") or "(sem título)"
        canal = m.get("channel") or m.get("uploader") or "canal não identificado"
        print(f"[youtube] {titulo}\n[youtube] canal: {canal} · {bo.hms(float(m.get('duration') or 0))}")
        if a.max_min and float(m.get("duration") or 0) > a.max_min * 60:
            raise SystemExit(f"[recusa] {bo.hms(float(m['duration']))} passa de {a.max_min} min. "
                             f"Use --max-min maior se for mesmo preciso.")
        saida = destino / f"{vid}-%(title).80B.%(ext)s"
        # H.264/AAC primeiro: VP9/Opus não toca no QuickTime (baixar_obra.py, 2026-09-18).
        r = subprocess.run(ytdlp() + ["-f", "bv*+ba/b", "--merge-output-format", "mp4",
                                      "-S", f"res:{a.res},vcodec:h264,acodec:aac", "--no-playlist",
                                      "--restrict-filenames", "--print", "after_move:filepath", "--no-simulate",
                                      "-o", str(saida), m.get("webpage_url") or a.url],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print((r.stderr or "").strip()[-1500:])
            raise SystemExit("[erro] o download falhou (mensagem do yt-dlp acima).")
        arq = next((Path(l.strip()) for l in reversed(r.stdout.splitlines()) if l.strip().endswith(".mp4")), None)
        if not arq or not arq.is_file():
            raise SystemExit("[erro] o yt-dlp terminou mas não achei o .mp4 gerado.")
        prox = bo.fazer_proxy(arq)
        item = {
            "id": vid, "url": m.get("webpage_url") or a.url, "titulo": titulo, "canal": canal,
            "publicado_em": bo.formatar_data(m.get("upload_date")), "duracao_s": round(float(m.get("duration") or 0), 3),
            "visualizacoes": m.get("view_count"), "licenca": m.get("license") or "todos os direitos reservados",
            "fps": round(fps_de(arq), 3), "arquivo": str(arq.relative_to(RAIZ)),
            "proxy": str(prox.relative_to(RAIZ)) if prox else None,
            "credito": a.credito or f"{titulo} ({canal})", "uso": "comentario",
            "baixado_em": date.today().isoformat(), "linhas": [], "motivo": "", "momentos": [], "trechos": [],
        }
        cat.append(item)
    if a.linhas:
        item["linhas"] = sorted(set(item.get("linhas", [])) | {x.strip() for x in a.linhas.split(",") if x.strip()})
    if a.motivo:
        item["motivo"] = a.motivo
    escrever_catalogo(a.slug, cat)
    print(f"[youtube] pronto: {item['arquivo']}\n[youtube] catálogo: "
          f"{(pasta(a.slug) / 'catalogo.md').relative_to(RAIZ)}")
    return 0


# ------------------------------------------------------------------ momento / trecho
def cmd_momento(a: argparse.Namespace) -> int:
    cat = ler_catalogo(a.slug)
    v = achar(cat, a.video)
    ini, fim = bo.segundos(a.inicio), bo.segundos(a.fim)
    if fim <= ini:
        raise SystemExit("[erro] o fim tem de vir depois do início.")
    v.setdefault("momentos", []).append({"inicio": bo.hms(ini), "fim": bo.hms(fim), "inicio_s": ini, "fim_s": fim,
                                         "linha": a.linha, "o_que": a.o_que})
    v["momentos"].sort(key=lambda x: x["inicio_s"])
    escrever_catalogo(a.slug, cat)
    print(f"[momento] {a.video} {bo.hms(ini)}–{bo.hms(fim)} -> {a.linha or '-'}: {a.o_que}")
    return 0


def cmd_trecho(a: argparse.Namespace) -> int:
    vd = bo.pasta_video(a.slug)
    cat = ler_catalogo(a.slug)
    v = achar(cat, a.video)
    fonte = RAIZ / v["arquivo"]
    if not fonte.is_file():
        raise SystemExit(f"[erro] arquivo não encontrado: {v['arquivo']}")
    ini, fim = bo.segundos(a.inicio), bo.segundos(a.fim)
    if fim <= ini:
        raise SystemExit("[erro] o fim tem de vir depois do início.")

    # Conformar para 25 fps. 23,976/24/25: quadro a quadro (1:1), o clipe corre um pouco mais depressa e o
    # movimento fica liso (mesma lógica do baixar_obra.py). 30/50/60: o filtro fps descarta quadros —
    # 50→25 é exato; 30/60→25 dá um leve judder, aceitável num trecho MUDO e curto.
    fps_src = v.get("fps") or fps_de(fonte)
    um_para_um = 23.0 <= fps_src <= 25.5
    dur_fonte = fim - ini
    dur = dur_fonte * fps_src / FPS if um_para_um else dur_fonte   # duração NA TELA do Reel

    if dur > bo.TRECHO_MAX_S and not a.forcar:
        raise SystemExit(f"[recusa] trecho de {dur:.1f}s — o teto por trecho é {bo.TRECHO_MAX_S:.0f}s. "
                         f"Prefira vários curtos, cada um sob uma frase do Carlos (--forcar só a pedido dele).")
    outros = total_citado(a.slug, excluir=a.id)
    if outros + dur > bo.TOTAL_MAX_S and not a.forcar:
        raise SystemExit(f"[recusa] o total citado no Reel iria a {outros + dur:.1f}s (teto {bo.TOTAL_MAX_S:.0f}s, "
                         f"somando obra + YouTube). Aperte ou tire outro trecho do roteiro.")
    if dur > bo.TRECHO_AVISO_S:
        print(f"[aviso] {dur:.1f}s é longo para uma citação — veja se dá para apertar.")

    nome = f"{a.id}-{a.nome}.mp4" if a.nome else f"{a.id}.mp4"
    destino = vd / "brutos" / "extras" / nome
    destino.parent.mkdir(parents=True, exist_ok=True)
    vf = f"setpts=N/({FPS}*TB)" if um_para_um else f"fps={FPS}"
    # Seek na ENTRADA (-ss antes do -i) — ver o comentário longo em baixar_obra.cmd_trecho.
    cmd = [bo.ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{ini:.3f}", "-i", str(fonte),
           "-t", f"{dur_fonte:.3f}", "-vf", vf, "-r", str(FPS), "-fps_mode", "cfr",
           "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p"]
    if a.som:
        print("[aviso] mantendo o áudio original: é o que mais dispara o Rights Manager.")
        cmd += ["-c:a", "aac", "-b:a", "192k"] + (["-af", f"atempo={FPS / fps_src:.6f}"] if um_para_um else [])
    else:
        cmd += ["-an"]
    cmd.append(str(destino))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print((r.stderr or "").strip()[-1500:])
        raise SystemExit("[erro] o ffmpeg não conseguiu cortar o trecho.")

    for outro in cat:   # um ID de cena extra só pode vir de um lugar
        outro["trechos"] = [t for t in outro.get("trechos", []) if t["id"] != a.id]
    v["trechos"].append({"id": a.id, "inicio": bo.hms(ini), "fim": bo.hms(fim), "inicio_s": round(ini, 3),
                         "fim_s": round(fim, 3), "duracao_s": round(dur, 3), "o_que": a.o_que, "som": bool(a.som),
                         "arquivo": str(destino.relative_to(RAIZ))})
    v["trechos"].sort(key=lambda t: t["id"])
    escrever_catalogo(a.slug, cat)
    bo.entrada_fontes(a.slug, {
        "id": a.id, "tipo": "video", "o_que": a.o_que, "url": v["url"], "licenca": v["licenca"],
        "autor": v["canal"], "credito": v["credito"], "permitido": True, "uso": "comentario",
        "duracao_s": round(dur, 3),
        "motivo": "trecho citado em Reel de comentário/análise (docs/decisoes.md §5, decisão de 2026-10-01)",
        "como_obter": f"scripts/buscar_youtube.py trecho {a.slug} {a.id} {a.video} {a.inicio} {a.fim}",
        "quem_baixa": "buscador-de-videos",
    })
    print(f"[trecho] {a.id}: {bo.hms(ini)}–{bo.hms(fim)} ({dur:.1f}s na tela) -> {destino.relative_to(RAIZ)}")
    print(f"[trecho] total citado no Reel: {outros + dur:.1f}s de {bo.TOTAL_MAX_S:.0f}s")
    print(f"[trecho] crédito obrigatório na tela: {v['credito']}")
    return 0


# ------------------------------------------------------------------ catálogo
def catalogo_md(slug: str, cat: list[dict]) -> str:
    total = sum(float(t["duracao_s"]) for v in cat for t in v.get("trechos", []))
    out = [f"# Material do YouTube — {slug}", "",
           "Cópias de **estudo**: servem para analisar a pessoa/obra e escolher o que citar. Nunca são publicadas",
           "inteiras — só os trechos curtos em `brutos/extras/` entram no Reel, com crédito na tela.", "",
           f"**{len(cat)} vídeo(s)** · trechos cortados daqui: **{total:.1f} s** "
           f"(teto do Reel {bo.TOTAL_MAX_S:.0f} s, somando a obra)", ""]
    for v in cat:
        out += [f"## {v['titulo']}", "",
                f"![](https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg)", "",
                f"- **Canal:** {v['canal']} · **publicado:** {v.get('publicado_em') or '?'} · "
                f"**duração:** {bo.hms(v.get('duracao_s') or 0)} · **{v.get('fps') or '?'} fps**",
                f"- **Link:** {v['url']}",
                f"- **Arquivo:** `{v.get('proxy') or v['arquivo']}`",
                f"- **Crédito na tela:** {v['credito']}",
                f"- **Para as linhas:** {', '.join(v.get('linhas') or []) or '—'} — {v.get('motivo') or ''}", ""]
        if v.get("momentos"):
            out += ["| Momento | Linha | O que mostra |", "|---|---|---|"]
            out += [f"| {m['inicio']}–{m['fim']} | {m.get('linha') or '—'} | {m['o_que']} |" for m in v["momentos"]]
            out.append("")
        if v.get("trechos"):
            out += ["**Cortados para o Reel:** " + "; ".join(
                f"`{t['id']}` {t['inicio']}–{t['fim']} ({t['duracao_s']:.1f} s)" for t in v["trechos"]), ""]
    return "\n".join(out) + "\n"


def cmd_catalogo(a: argparse.Namespace) -> int:
    cat = ler_catalogo(a.slug)
    escrever_catalogo(a.slug, cat)
    print(catalogo_md(a.slug, cat))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("buscar"); b.add_argument("consulta"); b.add_argument("--n", type=int, default=8)
    b.add_argument("--cc", action="store_true", help="só Creative Commons (filtro do YouTube)")
    b.set_defaults(func=cmd_buscar)
    d = sub.add_parser("baixar"); d.add_argument("url"); d.add_argument("slug")
    d.add_argument("--linhas", help="linhas do roteiro que o vídeo sustenta (L02,L03)")
    d.add_argument("--motivo", help="por que este vídeo serve")
    d.add_argument("--credito", help="crédito na tela (padrão: \"título (canal)\")")
    d.add_argument("--res", type=int, default=1080)
    d.add_argument("--max-min", type=float, default=180, help="recusa vídeos mais longos (min)")
    d.set_defaults(func=cmd_baixar)
    m = sub.add_parser("momento"); m.add_argument("slug"); m.add_argument("video")
    m.add_argument("inicio"); m.add_argument("fim"); m.add_argument("--linha")
    m.add_argument("--o-que", dest="o_que", required=True); m.set_defaults(func=cmd_momento)
    t = sub.add_parser("trecho"); t.add_argument("slug"); t.add_argument("id"); t.add_argument("video")
    t.add_argument("inicio"); t.add_argument("fim"); t.add_argument("--o-que", dest="o_que", required=True)
    t.add_argument("--nome"); t.add_argument("--som", action="store_true"); t.add_argument("--forcar", action="store_true")
    t.set_defaults(func=cmd_trecho)
    c = sub.add_parser("catalogo"); c.add_argument("slug"); c.set_defaults(func=cmd_catalogo)
    a = ap.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
