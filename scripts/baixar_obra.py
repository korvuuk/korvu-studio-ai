#!/usr/bin/env python3
"""Baixa a OBRA de que o Reel vai FALAR (vídeo de comentário/reação) e recorta os trechos citados.

Decisão do Carlos (2026-09-18): "não vamos usar esse conteúdo sozinho... é como se fosse um react.
Vamos falar DO documentário, não usar o conteúdo real". Isto é diferente de B-roll:

  B-roll        o trecho ILUSTRA outra coisa enquanto ele fala  -> precisa de licença de reuso
                -> scripts/buscar_video.py (archive.org, Commons, press kit)
  Comentário    o trecho É aquilo de que ele está falando       -> citação para crítica
                -> ESTE script

Os dois caminhos continuam separados de propósito. Este script NUNCA deve ser usado para arranjar
imagem bonita de fundo: se a fala não for sobre a obra, é B-roll e vai pelo outro caminho.

Como fica no disco:
  videos/<slug>/material/obra/<arquivo>   cópia de ESTUDO, inteira. Nunca é publicada, nunca entra
                                          no pacote, nunca vai para 05-render-pronto.
  videos/<slug>/material/obra.json        procedência (url, autor, plataforma, data, crédito, trechos)
  videos/<slug>/brutos/extras/<ID>-*.mp4  só os TRECHOS CURTOS citados — é só isto que entra no Reel.

Uso:
  uv run python scripts/baixar_obra.py baixar <url> <slug> [--so-metadados]
  uv run python scripts/baixar_obra.py trecho <slug> <ID> <inicio> <fim> --o-que "..." [--som]
  uv run python scripts/baixar_obra.py estado <slug>

Tempos aceitam "MM:SS", "HH:MM:SS" ou segundos. Exemplo:
  uv run python scripts/baixar_obra.py trecho 2026-10-02-deepmind E01 12:30 12:38 \
      --o-que "Hassabis explica por que o AlphaFold mudou a biologia"
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# Limites do formato. Não são jurídicos — são o que separa "citar" de "republicar", e o que reduz a
# chance de o Rights Manager casar o material. Ver docs/decisoes.md §5.
FPS = float(os.environ.get("FPS_PROJETO") or 25)   # o projeto todo roda a 25
TRECHO_AVISO_S = 8.0    # acima disto, avisa
# Desde 14/10 sem teto: decisão escrita do Carlos ("Liberar, áudio deles baixo/mudo" — docs/decisoes.md,
# linha "Trechos de terceiros nas histórias: sem teto de tempo"). O trecho entra mudo/baixo, com crédito.
# Para voltar a ter teto, defina TETO_TRECHO_S / TETO_CITACAO_S no ambiente.
TRECHO_MAX_S = float(os.environ.get("TETO_TRECHO_S") or "inf")
# O teto total nasceu a pensar em extra que SUBSTITUI o Carlos na tela. No formato da Korvu o extra entra
# em `split`: ele fica na metade de baixo, a falar, o tempo todo — o trecho nunca é o vídeo, é ilustração
# do comentário dele. Por isso 30 s num Reel de 60 s. Se algum dia um extra entrar em `full` (tela cheia,
# o Carlos sai), o teto de facto é 20 s: aí o trecho passa a ser o que se está a ver.
# 30 s é a decisão registada (Carlos, 19/09; `docs/decisoes.md`, `CLAUDE.md` regra 4). Ele autorizou
# subir de 20 s SEM dar número — quem pôs 30 foi a sessão que registou a decisão. Em 2026-09-19 eu
# escrevi 45 aqui e chamei-lhe "autorização do Carlos": não era, era número meu. Não repetir — um
# teto só muda por decisão escrita, e quem a escreve diz de onde veio o número.
TOTAL_MAX_S = float(os.environ.get("TETO_CITACAO_S") or "inf")


def ffmpeg() -> str:
    return os.environ.get("FFMPEG_BIN") or shutil.which("ffmpeg") or "ffmpeg"


def ffprobe() -> str:
    return os.environ.get("FFPROBE_BIN") or shutil.which("ffprobe") or "ffprobe"


def log(msg: str) -> None:
    print(msg, flush=True)


def segundos(txt: str) -> float:
    """Aceita 90, 1:30 ou 0:01:30."""
    txt = str(txt).strip()
    if re.fullmatch(r"\d+(\.\d+)?", txt):
        return float(txt)
    partes = txt.split(":")
    if not all(re.fullmatch(r"\d+(\.\d+)?", p) for p in partes) or len(partes) > 3:
        raise SystemExit(f"[erro] tempo inválido: {txt!r} (use 12:30, 1:02:30 ou 750)")
    total = 0.0
    for p in partes:
        total = total * 60 + float(p)
    return total


def hms(s: float) -> str:
    h, resto = divmod(int(s), 3600)
    m, seg = divmod(resto, 60)
    return f"{h}:{m:02d}:{seg:02d}" if h else f"{m}:{seg:02d}"


def pasta_video(slug: str) -> Path:
    vd = RAIZ / "videos" / slug
    if not vd.is_dir():
        raise SystemExit(f"[erro] vídeo não existe: videos/{slug}\n"
                         f"       crie primeiro com /novo-video, ou confira o slug.")
    return vd


def caminho_obra_json(slug: str) -> Path:
    return pasta_video(slug) / "material" / "obra.json"


def ler_obra(slug: str) -> dict:
    p = caminho_obra_json(slug)
    if not p.is_file():
        raise SystemExit(f"[erro] {p.relative_to(RAIZ)} não existe — rode primeiro:\n"
                         f"       uv run python scripts/baixar_obra.py baixar <url> {slug}")
    return json.loads(p.read_text(encoding="utf-8"))


def escrever_obra(slug: str, obra: dict) -> None:
    p = caminho_obra_json(slug)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obra, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ baixar
def metadados(url: str) -> dict:
    """Pergunta ao yt-dlp quem é o dono da obra ANTES de baixar. Sem isto não há crédito, e sem
    crédito o trecho não entra no roteiro."""
    if not shutil.which("yt-dlp"):
        raise SystemExit("[erro] yt-dlp não encontrado. Instale com: brew install yt-dlp")
    r = subprocess.run(["yt-dlp", "--dump-json", "--no-download", "--no-warnings", url],
                       capture_output=True, text=True)
    if r.returncode != 0:
        erro = (r.stderr or "").strip().splitlines()
        cauda = erro[-1] if erro else "(sem detalhe)"
        if "TLSV1_ALERT_ACCESS_DENIED" in (r.stderr or ""):
            raise SystemExit(
                f"[erro] a rede bloqueou o acesso a este site (filtro do operador, não é o yt-dlp).\n"
                f"       {cauda}\n"
                f"       Teste noutra rede (hotspot 4G). Ver docs/decisoes.md — archive.org tem o mesmo sintoma.")
        raise SystemExit(f"[erro] yt-dlp não conseguiu ler a página:\n       {cauda}")
    return json.loads(r.stdout)


def precisa_proxy(src: Path) -> bool:
    """VP9/AV1/Opus dentro de .mp4 é o que o YouTube entrega em 1080p — e o QuickTime do macOS não
    toca nenhum dos três. O ffmpeg lê tudo; quem precisa de dar play é o Carlos."""
    r = subprocess.run([ffprobe(), "-v", "error", "-show_entries", "stream=codec_name",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(src)],
                       capture_output=True, text=True)
    codecs = {c.strip().lower() for c in (r.stdout or "").splitlines() if c.strip()}
    return bool(codecs & {"vp9", "vp8", "av1", "opus", "vorbis"})


def fazer_proxy(src: Path) -> Path | None:
    """Cópia leve em H.264/AAC só para ASSISTIR e escolher os trechos. Os cortes que vão para o Reel
    saem sempre do original, para não perder qualidade duas vezes.

    720p a 1200 kbps é de propósito: serve para percorrer e anotar minutos, não para ver bonito. A 2500
    kbps o proxy de um documentário de 84 min deu 1,58 GB — do tamanho do original, o que anula a ideia."""
    if not precisa_proxy(src):
        return None
    dst = src.with_name(src.stem + "-VER.mp4")
    if dst.is_file():
        return dst
    log(f"[obra] o arquivo está em VP9/Opus — o QuickTime não toca. Gerando cópia para ver: {dst.name}")
    cmd = [ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-i", str(src),
           "-vf", "scale=-2:720", "-c:v", "h264_videotoolbox", "-b:v", "1200k", "-profile:v", "high",
           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(dst)]
    if subprocess.run(cmd, capture_output=True, text=True).returncode != 0:
        # Sem aceleração de hardware (Intel, ou videotoolbox indisponível): cai no libx264.
        cmd[cmd.index("h264_videotoolbox")] = "libx264"
        cmd[cmd.index("-b:v"):cmd.index("-b:v") + 2] = ["-crf", "23"]
        if subprocess.run(cmd, capture_output=True, text=True).returncode != 0:
            log("[aviso] não consegui gerar a cópia de visualização — instale o VLC para ver o original.")
            return None
    return dst


def formatar_data(bruta: str | None) -> str:
    if bruta and re.fullmatch(r"\d{8}", bruta):
        return f"{bruta[:4]}-{bruta[4:6]}-{bruta[6:]}"
    return bruta or ""


def cmd_baixar(args: argparse.Namespace) -> int:
    vd = pasta_video(args.slug)
    destino = vd / "material" / "obra"
    destino.mkdir(parents=True, exist_ok=True)

    log(f"[obra] lendo a página: {args.url}")
    m = metadados(args.url)

    autor = m.get("uploader") or m.get("channel") or m.get("creator") or "autor não identificado"
    titulo = m.get("title") or "(sem título)"
    plataforma = m.get("extractor_key") or "desconhecida"
    licenca = m.get("license") or ""
    duracao = float(m.get("duration") or 0)

    log(f"[obra] {titulo}")
    log(f"[obra] autor: {autor} · plataforma: {plataforma} · duração: {hms(duracao)}")
    if licenca:
        log(f"[obra] licença declarada na página: {licenca}")

    obra = ler_obra(args.slug) if caminho_obra_json(args.slug).is_file() else {}
    obra.update({
        "url": m.get("webpage_url") or args.url,
        "titulo": titulo,
        "autor": autor,
        "plataforma": plataforma,
        "publicado_em": formatar_data(m.get("upload_date")),
        "duracao_s": round(duracao, 3),
        "licenca_declarada": licenca or "não declarada (obra comercial)",
        # Marca o motivo de esta obra estar no projeto. Qualquer agente que leia este arquivo
        # sabe que o material é OBJETO de comentário e não material de ilustração.
        "uso": "comentario",
        "credito": args.credito or f"{titulo} ({autor})",
        "baixado_em": date.today().isoformat(),
        "trechos": obra.get("trechos", []),
    })

    if args.so_metadados:
        escrever_obra(args.slug, obra)
        log(f"[obra] só metadados — nada baixado. Ficha em {caminho_obra_json(args.slug).relative_to(RAIZ)}")
        return 0

    saida = destino / "%(title).120B.%(ext)s"
    log(f"[obra] baixando para {destino.relative_to(RAIZ)}/ (cópia de estudo, nunca publicada)")
    # -S pede H.264 + AAC antes de tudo. Sem isto o YouTube entrega VP9+Opus em 1080p, que o
    # QuickTime do macOS NÃO toca: o Carlos abre e vê tela preta (aconteceu em 2026-09-18).
    # O ffmpeg lê os dois, mas quem escolhe os trechos é uma pessoa, e ela precisa de dar play.
    r = subprocess.run(["yt-dlp", "-f", "bv*+ba/b", "--merge-output-format", "mp4",
                        "-S", "res:1080,vcodec:h264,acodec:aac",
                        "--no-playlist", "--restrict-filenames",
                        "--print", "after_move:filepath", "--no-simulate",
                        "-o", str(saida), args.url], text=True, capture_output=True)
    if r.returncode != 0:
        log((r.stderr or "").strip()[-2000:])
        raise SystemExit("[erro] o download falhou (mensagem do yt-dlp acima).")

    caminhos = [l.strip() for l in (r.stdout or "").splitlines() if l.strip().endswith((".mp4", ".mkv", ".webm"))]
    if caminhos:
        obra["arquivo"] = str(Path(caminhos[-1]).relative_to(RAIZ))
        if not args.sem_proxy:
            prox = fazer_proxy(RAIZ / obra["arquivo"])
            if prox:
                obra["proxy"] = str(prox.relative_to(RAIZ))
    escrever_obra(args.slug, obra)

    log(f"[obra] pronto: {obra.get('arquivo', destino.relative_to(RAIZ))}")
    log(f"[obra] ficha: {caminho_obra_json(args.slug).relative_to(RAIZ)}")
    log("")
    log("  Esta cópia é para ESTUDO. Só os trechos curtos citados entram no Reel:")
    log(f"    uv run python scripts/baixar_obra.py trecho {args.slug} E01 12:30 12:38 --o-que \"...\"")
    return 0


# ------------------------------------------------------------------ trecho
def entrada_fontes(slug: str, item: dict) -> None:
    """Acrescenta o trecho a material/fontes.json, o mesmo arquivo que o produtor-de-extras lê."""
    p = pasta_video(slug) / "material" / "fontes.json"
    dados = json.loads(p.read_text(encoding="utf-8")) if p.is_file() else []
    dados = [d for d in dados if d.get("id") != item["id"]]
    dados.append(item)
    dados.sort(key=lambda d: str(d.get("id", "")))
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def cmd_trecho(args: argparse.Namespace) -> int:
    vd = pasta_video(args.slug)
    obra = ler_obra(args.slug)

    arquivo = obra.get("arquivo")
    if not arquivo:
        raise SystemExit("[erro] a ficha não aponta para nenhum arquivo — rode 'baixar' sem --so-metadados.")
    fonte = RAIZ / arquivo
    if not fonte.is_file():
        raise SystemExit(f"[erro] arquivo da obra não encontrado: {arquivo}")

    ini, fim = segundos(args.inicio), segundos(args.fim)
    if fim <= ini:
        raise SystemExit(f"[erro] o fim ({args.fim}) tem de vir depois do início ({args.inicio}).")
    dur = fim - ini

    # Orçamento de citação — o que separa comentário de republicação.
    outros = sum(float(t["duracao_s"]) for t in obra["trechos"] if t["id"] != args.id)
    # O teto é do Reel: soma também os trechos tirados do YouTube pelo buscar_youtube.py.
    cat = vd / "material" / "youtube" / "catalogo.json"
    if cat.is_file():
        outros += sum(float(t["duracao_s"]) for v in json.loads(cat.read_text(encoding="utf-8"))
                      for t in v.get("trechos", []) if t["id"] != args.id)
    if dur > TRECHO_MAX_S and not args.forcar:
        raise SystemExit(
            f"[recusa] trecho de {dur:.1f}s — o teto por trecho é {TRECHO_MAX_S:.0f}s.\n"
            f"         Num Reel de 60 s, um trecho longo deixa de ser citação e vira republicação:\n"
            f"         é o que o Rights Manager casa e o que enfraquece o argumento de comentário.\n"
            f"         Prefira vários trechos curtos, cada um sob uma frase sua. Se for mesmo preciso: --forcar")
    if outros + dur > TOTAL_MAX_S and not args.forcar:
        raise SystemExit(
            f"[recusa] este trecho levaria o total citado a {outros + dur:.1f}s (teto {TOTAL_MAX_S:.0f}s).\n"
            f"         Já citados: {hms(outros)}. Corte outro trecho antes, ou use --forcar se souber o que faz.")
    if dur > TRECHO_AVISO_S:
        log(f"[aviso] {dur:.1f}s é longo para uma citação — veja se dá para apertar.")

    nome = f"{args.id}-{args.nome}.mp4" if args.nome else f"{args.id}.mp4"
    destino = vd / "brutos" / "extras" / nome
    destino.parent.mkdir(parents=True, exist_ok=True)

    # Corte com seek preciso (-ss depois do -i): reencoda, mas é o único jeito de bater o frame certo.
    # Resolução e fps ficam como estão — quem normaliza para o projeto é o ingest.py.
    # CONFORMAR para FPS_PROJETO em vez de deixar o ingest usar o filtro `fps`.
    # O filtro duplica/descarta quadros e o movimento "pula". Aqui fazemos o que o cinema faz para a TV:
    # cada quadro da fonte vira um quadro de saída (1:1) e o clipe corre 4,3% mais depressa (23,976→25).
    # Em 3-4 s de B-roll MUDO ninguém percebe os 4%, e o movimento fica perfeitamente liso — sem judder.
    # (Só é seguro porque o extra não tem áudio; com áudio isto mudaria o tom da voz.)
    # SEEK NA ENTRADA (-ss antes do -i), nunca na saída. Com o filtro de conformação no meio, o seek de
    # saída aterra noutro sítio: em 2026-09-18 dois cortes saíram nos créditos finais e numa sala errada,
    # embora os frames de verificação (extraídos com seek de entrada) mostrassem o plano certo.
    # Verificar e cortar têm de usar o mesmo método, senão a conferência não vale nada.
    cmd = [ffmpeg(), "-hide_banner", "-loglevel", "error", "-y",
           "-ss", f"{ini:.3f}", "-i", str(fonte), "-t", f"{dur:.3f}",
           "-vf", f"setpts=N/({FPS}*TB)", "-r", str(FPS), "-fps_mode", "cfr",
           "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p"]
    if args.som:
        # O áudio original só entra quando a fala do Carlos depende de ouvir a obra. É também o que
        # mais dispara correspondência automática — por isso não é o padrão.
        cmd += ["-c:a", "aac", "-b:a", "192k", "-af", f"atempo={FPS}/23.976"]
        log("[aviso] mantendo o áudio original: é o que mais dispara o Rights Manager. "
            "Confirme que a voz do Carlos entra por cima.")
        log("[aviso] o clipe foi conformado para 25 fps (4,3% mais rápido) e o áudio acompanhou — "
            "confira se o tom da voz ficou aceitável.")
    else:
        cmd += ["-an"]
    cmd.append(str(destino))

    log(f"[trecho] {args.id}: {hms(ini)}–{hms(fim)} ({dur:.1f}s) -> {destino.relative_to(RAIZ)}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        log((r.stderr or "").strip()[-1500:])
        raise SystemExit("[erro] o ffmpeg não conseguiu cortar o trecho.")

    obra["trechos"] = [t for t in obra["trechos"] if t["id"] != args.id] + [{
        "id": args.id, "inicio_s": round(ini, 3), "fim_s": round(fim, 3), "duracao_s": round(dur, 3),
        "inicio": hms(ini), "fim": hms(fim), "o_que": args.o_que,
        "som": bool(args.som), "arquivo": str(destino.relative_to(RAIZ)),
    }]
    obra["trechos"].sort(key=lambda t: t["id"])
    escrever_obra(args.slug, obra)

    entrada_fontes(args.slug, {
        "id": args.id, "tipo": "video", "o_que": args.o_que,
        "url": obra["url"], "licenca": obra["licenca_declarada"], "autor": obra["autor"],
        "credito": obra["credito"], "permitido": True,
        "uso": "comentario",
        "motivo": "trecho citado no vídeo de comentário sobre a própria obra (docs/decisoes.md §5)",
        "como_obter": f"scripts/baixar_obra.py trecho {args.slug} {args.id} {args.inicio} {args.fim}",
        "quem_baixa": "curador-de-obra",
    })

    total = sum(float(t["duracao_s"]) for t in obra["trechos"])
    log(f"[trecho] total citado: {total:.1f}s de {TOTAL_MAX_S:.0f}s em {len(obra['trechos'])} trecho(s)")
    log(f"[trecho] crédito obrigatório na tela: {obra['credito']}")
    return 0


def cmd_ver(args: argparse.Namespace) -> int:
    obra = ler_obra(args.slug)
    if not obra.get("arquivo"):
        raise SystemExit("[erro] a ficha não aponta para nenhum arquivo.")
    prox = fazer_proxy(RAIZ / obra["arquivo"])
    if prox is None:
        log("[ver] o original já toca no QuickTime — não precisa de cópia.")
        return 0
    obra["proxy"] = str(prox.relative_to(RAIZ))
    escrever_obra(args.slug, obra)
    log(f"[ver] pronto: {prox.relative_to(RAIZ)}")
    return 0


# ------------------------------------------------------------------ estado
def cmd_estado(args: argparse.Namespace) -> int:
    obra = ler_obra(args.slug)
    log(f"Obra comentada em {args.slug}")
    log(f"  título     {obra['titulo']}")
    log(f"  autor      {obra['autor']} ({obra['plataforma']})")
    log(f"  publicada  {obra.get('publicado_em') or '?'} · duração {hms(obra.get('duracao_s') or 0)}")
    log(f"  licença    {obra['licenca_declarada']}")
    log(f"  crédito    {obra['credito']}")
    log(f"  arquivo    {obra.get('arquivo') or '(só metadados)'}")
    trechos = obra.get("trechos", [])
    if not trechos:
        log("  trechos    nenhum ainda")
        return 0
    total = sum(float(t["duracao_s"]) for t in trechos)
    log(f"  trechos    {len(trechos)} · {total:.1f}s de {TOTAL_MAX_S:.0f}s")
    for t in trechos:
        som = "com som" if t.get("som") else "mudo"
        log(f"    {t['id']}  {t['inicio']}–{t['fim']}  {t['duracao_s']:.1f}s  {som}  {t.get('o_que', '')}")
    if total > TOTAL_MAX_S:
        log(f"  [AVISO] acima do teto de {TOTAL_MAX_S:.0f}s — reveja antes de publicar.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("baixar", help="baixa a obra comentada e escreve a ficha de procedência")
    b.add_argument("url")
    b.add_argument("slug")
    b.add_argument("--credito", help="crédito na tela (padrão: \"título (autor)\")")
    b.add_argument("--so-metadados", action="store_true", help="só lê a ficha, não baixa")
    b.add_argument("--sem-proxy", action="store_true", help="não gerar a cópia H.264 de visualização")
    b.set_defaults(func=cmd_baixar)

    t = sub.add_parser("trecho", help="recorta um trecho citado para brutos/extras/")
    t.add_argument("slug")
    t.add_argument("id", help="ID da cena extra (E01, E02…)")
    t.add_argument("inicio")
    t.add_argument("fim")
    t.add_argument("--o-que", dest="o_que", required=True, help="o que este trecho mostra")
    t.add_argument("--nome", help="sufixo do arquivo (E01-<nome>.mp4)")
    t.add_argument("--som", action="store_true", help="manter o áudio original do trecho")
    t.add_argument("--forcar", action="store_true", help="passar por cima dos tetos de duração")
    t.set_defaults(func=cmd_trecho)

    v = sub.add_parser("ver", help="gera a cópia H.264 de visualização de uma obra já baixada")
    v.add_argument("slug")
    v.set_defaults(func=cmd_ver)

    e = sub.add_parser("estado", help="mostra a obra e os trechos já citados")
    e.add_argument("slug")
    e.set_defaults(func=cmd_estado)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
