#!/usr/bin/env python3
"""Jensen Huang — camada de extras v1 (proposta de 17/10, antes da gravação de 18/10).

Copiado e adaptado de `videos/2026-10-20-fei-fei-li/edicao/extras-v2/montar_v3.py` (o padrão aprovado na Fei-Fei v3.2):
os 4 LAYOUTS variando conforme a imagem (docs/decisoes.md §4, 17/10) — `full` (pessoa/retrato em tela cheia),
`pilha` (3 faixas topo/meio/base), `solo` (imagem de leitura inteira sobre preto) e `split` (cena em cima, o Carlos
embaixo); sincronia fala ↔ imagem (a imagem entra NA palavra: "Denny's", "5 trilhões", "Rei Charles", "Hinton"…);
crédito no RODAPÉ (Reel.tsx); faixa contínua sem "entra e sai"; o Carlos volta só nas frases de ênfase e no CTA.

PAR A/B (docs/decisoes.md §5b, 17/10): B = o conteúdo cobre o gancho inteiro (L01–L02, overlays B1–B4) e o Carlos entra
na L03; A = o Carlos desde o quadro 0 (os mesmos overlays, sem B1–B4). Fala, legendas, música e CTA idênticos.

TEMPOS
- Com `edicao/edl.json` (depois do /editar): tempos REAIS — início/fim de linha pelos segmentos e o corte no meio da linha
  no silêncio logo antes da palavra (palavras_saida), como na Fei-Fei.
- Sem EDL (hoje): ESTIMATIVA do `roteiro.json` (`tempo_estimado` de cada linha; palavras a 2,1/s a partir do início
  da linha). Serve para a proposta e para a folha de contato; o vídeo se monta com a EDL.
- Clipe mais curto que o trecho: até 15 % mais curto → câmera lenta leve (re-encode, aviso); mais que isso → quadro
  parado (Ken Burns no Remotion), nunca o último quadro congelado (decisão de 19/09).

USO (sempre da raiz do projeto)
  uv run python videos/2026-10-18-jensen-huang/edicao/extras-v2/montar_v1.py            # monta (precisa da EDL)
  uv run python …/montar_v1.py --seco                                                    # só mostra o plano
  uv run python …/montar_v1.py --seco --contato                                          # + qa/sequencia-extras-contato.jpg
  uv run python …/montar_v1.py --estimativa --seco                                       # força os tempos estimados
Saída: edicao/extras-v2/overlays-v1.json (B) e overlays-v1-A.json (A) → gerar_props.py --overlays <json>.
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
VIDEO = AQUI.parents[1]
RAIZ = VIDEO.parents[1]
FFMPEG = "/Users/teste/bin/ffmpeg"
FFPROBE = shutil.which("ffprobe") or "/opt/homebrew/bin/ffprobe"
FPS = 25
WPS = 2.1                 # palavras/s do Carlos (voz-carlos.md, wps_ref do roteiro)
LENTO_MIN = 0.85          # clipe até 15 % mais curto que o trecho → câmera lenta; abaixo disso → quadro parado
Y = VIDEO / "material/youtube/cortes"
F = VIDEO / "material/fotos"

# --- escolhas que o Carlos pode trocar ------------------------------------------------------------------------------
# L04 "E olha só que interessante: / ela nasceu numa mesa de lanchonete." — a frase de ênfase é a 1.ª metade (roteiro,
# "Frases de ênfase"); a placa do booth entra em "ela nasceu…" (sincronia). False = o Carlos na L04 inteira.
L04_PLACA = True
# L14 "…de quem eu já falei aqui.": True = as capas dos Reels do Hinton e da Fei-Fei (pilha de 2) nessa meia frase.
L14_CAPAS = False

# --- créditos curtos (rodapé; os completos vão na descrição do post) -------------------------------------------------
CBS60 = "60 Minutes / CBS News"
AP360 = "AP 360 Productions"
BBG = "Bloomberg Television"
CMU = "Carnegie Mellon University"
PD = "Wikimedia Commons (domínio público)"
HOOVER = "Hoover Institution / NVIDIA"
OBI = "Oneida Baptist Institute"
GSB = "Stanford GSB"
EXPLORIST = "Explorist"
CNBC = "CNBC"
CHM = "University of Toronto / CHM"
ROYAL = "The Royal Family Channel"
HAI = "Stanford HAI"
SEB = "Seb Frey (YouTube)"

# --- áreas úteis (px da fonte): o que fica FORA do recorte (logos, legendas queimadas, faixas) -----------------------
A_60 = {"x": 0, "y": 90, "largura": 1920, "altura": 990}          # 60 Minutes: sem o "60" do canto sup. esq.
A_CNBC = {"x": 0, "y": 140, "largura": 1920, "altura": 940}       # CNBC: sem o pavão do canto sup. dir.
A_CNBC_SOLO = {"x": 100, "y": 60, "largura": 1620, "altura": 1000}  # idem, no solo (corta a direita)
A_PLACA = {"x": 380, "y": 40, "largura": 1180, "altura": 1000}    # Y041: a placa do booth grande e inteira
A_OBI = {"x": 0, "y": 0, "largura": 852, "altura": 360}           # Y014: sem a legenda chinesa queimada


# ====================================================================================================================
# Modelo de tempo: EDL (real) ou roteiro.json (estimado)
# ====================================================================================================================
def _norm(t: str) -> str:
    return t.lower().strip(" \"'.,;:!?…*()[]")


def quadro(t: float) -> float:
    return round(round(t * FPS) / FPS, 2)


class Tempos:
    def __init__(self, forcar_estimativa: bool) -> None:
        self.rot = json.loads((VIDEO / "roteiro.json").read_text(encoding="utf-8"))
        self.secao = {l["id"]: l.get("secao") for l in self.rot["linhas"]}
        edl_p = VIDEO / "edicao/edl.json"
        self.real = edl_p.exists() and not forcar_estimativa
        self.lin: dict[str, list[float]] = {}
        if self.real:
            edl = json.loads(edl_p.read_text(encoding="utf-8"))
            if not edl.get("aprovado"):
                print("AVISO: edl.json ainda não está aprovada — tempos reais, mas provisórios", file=sys.stderr)
            for s in edl["segmentos"]:
                self.lin.setdefault(s["linha"], [s["saida_inicio"], s["saida_fim"]])
                self.lin[s["linha"]][0] = min(self.lin[s["linha"]][0], s["saida_inicio"])
                self.lin[s["linha"]][1] = max(self.lin[s["linha"]][1], s["saida_fim"])
            self.pal = edl["palavras_saida"]
            self.duracao = float(edl.get("duracao_saida") or max(b for _, b in self.lin.values()))
        else:
            self.pal = []
            for l in self.rot["linhas"]:
                te = l.get("tempo_estimado")
                if not te:
                    continue            # hooks alternativos (L01B/L01C)
                a, b = te
                self.lin[l["id"]] = [a, b]
                # as palavras ocupam len/WPS s a partir do início da linha (o resto é a pausa); um ano ("1993")
                # pesa 4 palavras faladas ("mil novecentos e noventa e três"), o total da linha não muda
                pesos = [4 if w.isdigit() and len(w) == 4 else 1 for w in l["palavras"]]
                u = (len(pesos) / WPS) / sum(pesos)
                t = a
                for w, pw in zip(l["palavras"], pesos):
                    self.pal.append({"texto": w, "inicio": round(t, 3), "fim": round(t + pw * u - 0.08, 3),
                                     "linha": l["id"]})
                    t += pw * u
            self.duracao = float(self.rot.get("duracao_estimada") or max(b for _, b in self.lin.values()))
        self.modo = "EDL (real)" if self.real else f"ESTIMADO (roteiro.json, {WPS} palavras/s)"

    def ini(self, l: str) -> float:
        return quadro(self.lin[l][0])

    def fim(self, l: str) -> float:
        return quadro(self.lin[l][1])

    def palavra(self, txt: str, linha: str, n: int = 1) -> float:
        """Onde a imagem da palavra entra: no silêncio logo antes dela (no máx. 0,15 s antes), nunca depois."""
        ps = [p for p in self.pal if p["linha"] == linha]
        k = 0
        for i, p in enumerate(ps):
            if _norm(p["texto"]) != txt.lower():
                continue
            k += 1
            if k < n:
                continue
            if i == 0:
                return self.ini(linha)
            q = ps[i - 1]
            vao = p["inicio"] - q["fim"]
            t = max((q["fim"] + p["inicio"]) / 2, p["inicio"] - 0.15) if vao >= 0.06 else p["inicio"]
            return quadro(t)
        raise SystemExit(f"palavra {txt!r} (n={n}) não está na {linha}: {[p['texto'] for p in ps]}")


# ====================================================================================================================
# Mídias
# ====================================================================================================================
def _um(pasta: Path, nome: str, ext: str = "") -> Path:
    achados = sorted(pasta.glob(f"{nome}-*{ext}")) or sorted(pasta.glob(f"{nome}*{ext}"))
    if not achados:
        raise SystemExit(f"não achei {nome}*{ext} em {pasta}")
    return achados[0]


def foto(nome: str, pasta: Path = F) -> dict:
    return {"tipo": "foto", "id": nome, "src": _um(pasta, nome)}


def vid(nome: str, tin: float = 0.0, ate: float | None = None, ss: float | None = None,
        lento: float = LENTO_MIN) -> dict:
    """Vídeo de `cortes/`; `ate` = fim útil do clipe (ex.: antes de uma transição); `ss` = quadro do recuo para still;
    `lento` = menor velocidade aceita antes de virar quadro parado (plano quase parado aguenta 0,6)."""
    return {"tipo": "video", "id": nome, "src": _um(Y, nome, ".mp4"), "tin": tin, "ate": ate, "ss": ss,
            "lento": lento}


def still(nome: str, ss: float) -> dict:
    return {"tipo": "still", "id": nome, "src": _um(Y, nome, ".mp4"), "ss": ss}


def capa(slug: str, nome: str) -> dict:
    return {"tipo": "foto", "id": nome, "src": RAIZ / "videos" / slug / "capa/capa.png"}


_DUR: dict[Path, float] = {}


def dur_video(p: Path) -> float:
    if p not in _DUR:
        r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                           capture_output=True, text=True)
        _DUR[p] = float(r.stdout.strip())
    return _DUR[p]


def resolver(m: dict, dur: float) -> dict:
    """Decide como a mídia cobre `dur` segundos: vídeo inteiro, câmera lenta leve ou quadro parado."""
    if m["tipo"] != "video":
        return dict(m, plano=m["tipo"])
    total = dur_video(m["src"])
    util = (m["ate"] if m["ate"] is not None else total) - m["tin"]
    if util >= dur - 0.02:
        return dict(m, plano="video")
    if util / dur >= m.get("lento", LENTO_MIN):
        return dict(m, plano="lento", fator=round(dur / util * 1.02 + 0.005, 3), util=util)   # 2 % de folga (quadros)
    ss = m["ss"] if m["ss"] is not None else m["tin"] + util / 2
    return dict(m, plano="still", ss=round(ss, 2), aviso=f"clipe {util:.2f}s < trecho {dur:.2f}s → quadro parado")


def rodar(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"falhou: {' '.join(cmd[:8])}…\n{r.stderr[-1500:]}")


def preparar(m: dict, tag: str) -> tuple[Path, str, float | None]:
    """Copia/gera a mídia em extras-v2/ → (arquivo, extra_tipo, in)."""
    p = m["plano"]
    if p == "foto":
        arq = AQUI / f"{m['id']}{m['src'].suffix.lower()}"
        shutil.copyfile(m["src"], arq)
        return arq, "imagem", None
    if p == "still":
        arq = AQUI / f"{tag}-{m['id']}.png"
        rodar([FFMPEG, "-hide_banner", "-y", "-ss", str(m["ss"]), "-i", str(m["src"]), "-frames:v", "1", str(arq)])
        return arq, "imagem", None
    if p == "lento":
        arq = AQUI / f"{tag}-{m['id']}-lento.mp4"
        rodar([FFMPEG, "-hide_banner", "-y", "-ss", str(m["tin"]), "-t", f"{m['util']:.3f}", "-i", str(m["src"]),
               "-an", "-vf", f"setpts={m['fator']}*PTS,fps={FPS}", "-c:v", "libx264", "-crf", "16",
               "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(arq)])
        return arq, "video", 0.0
    arq = AQUI / f"{tag}-{m['id']}.mp4"
    rodar([FFMPEG, "-hide_banner", "-y", "-i", str(m["src"]), "-an", "-c:v", "copy", "-movflags", "+faststart",
           str(arq)])
    return arq, "video", m["tin"]


# ====================================================================================================================
# A sequência (ordem cronológica da fala)
# ====================================================================================================================
def faixa(m: dict, enq: dict, cred: str | None) -> dict:
    return {"midia": m, "enq": enq, "cred": cred}


def sequencia(T: Tempos) -> list[dict]:
    ini, fim, pal = T.ini, T.fim, T.palavra
    S: list[dict] = []

    def add(tag, t0, t1, linhas, modo, midia=None, enq=None, cred=None, faixas=None, so_b=False, nota=""):
        S.append({"tag": tag, "t0": t0, "t1": t1, "linhas": linhas, "modo": modo, "midia": midia, "enq": enq,
                  "cred": cred, "faixas": faixas, "so_b": so_b, "nota": nota})

    # --- ABERTURA B (só na versão B): o conteúdo cobre o gancho inteiro; o Carlos entra na L03 ------------------------
    add("B1", ini("L01"), pal("numa", "L01"), ["L01"], "full", vid("Y051"), {"x": 0.5, "y": 0.45}, AP360,
        so_b=True, nota="'Imagina você lavar prato' — ele de avental vermelho do Denny's (GTC 2025)")
    add("B2", pal("numa", "L01"), pal("anos", "L02"), ["L01", "L02"], "full", vid("Y036"), {"x": 0.53, "y": 0.5},
        CBS60, so_b=True, nota="'numa lanchonete…' — o Denny's de San Jose à noite")
    add("B3", pal("anos", "L02"), pal("de", "L02"), ["L02"], "full", vid("Y077"), {"x": 0.5, "y": 0.5}, CBS60,
        so_b=True, nota="'anos depois, criar a primeira empresa' — ele entra no palco do GTC")
    # Y101: altura inteira e sem Ken Burns (o próprio plano já aproxima) — o "$5.10T" fica em y≈800–1070, ACIMA da
    # legenda (≈1150); a faixa vermelha da Bloomberg sobra no pé, sob a UI do Instagram
    add("B4", pal("de", "L02"), fim("L02"), ["L02"], "full", vid("Y101", tin=1.2),
        {"x": 0.5, "y": 0.5, "kenBurns": 1.0}, BBG, so_b=True, nota="'de 5 trilhões de dólares' — $5.09T → $5.10T")

    # --- L03 "Pois é. Essa é a história do Jensen Huang, da Nvidia." = Carlos (A e B) ---------------------------------
    # --- L04 "E olha só que interessante:" = Carlos (ênfase) ---------------------------------------------------------
    if L04_PLACA:
        add("V01", pal("ela", "L04"), fim("L04"), ["L04"], "solo", vid("Y041", ss=1.3, lento=0.6), {"area": A_PLACA}, CBS60,
            nota="'ela nasceu numa mesa de lanchonete' — a placa 'The booth that launched a $2 trillion company'")
    # L05 "Se quiser ver ele contando, comenta PRATO." — ele falando no discurso da CMU (o que o PDF entrega)
    add("V02", ini("L05"), fim("L05"), ["L05"], "split", vid("Y113"), None, CMU,
        nota="'ver ele contando' — o discurso da Carnegie Mellon; o Carlos embaixo pede o PRATO")
    # L06 "Ele nasceu em Taiwan / e, ainda criança, / foi parar num internato no Kentucky."
    add("V03", ini("L06"), pal("e", "L06"), ["L06"], "full", foto("F01"), {"x": 0.5, "y": 0.45, "xFim": 0.55}, PD,
        nota="'Ele nasceu em Taiwan' — Taipei nos anos 60 (P&B, vertical)")
    add("V04", pal("e", "L06"), fim("L06"), ["L06"], "pilha", faixas=[
        faixa(vid("Y011"), {"x": 0.5, "y": 0.5}, HOOVER),                       # o campus de Oneida visto do alto
        faixa(vid("Y013"), {"x": 0.42, "y": 0.4}, HOOVER),                      # ele numa cerimônia em Oneida
        faixa(vid("Y014", tin=0.3), {"x": 0.45, "y": 0.45, "area": A_OBI}, OBI),  # ele contando da escola (2020)
    ], nota="'e, ainda criança, foi parar num internato no Kentucky' — Oneida")
    # L07 "A família achava que era escola boa… / mas ele limpava os banheiros."
    add("V05", ini("L07"), pal("mas", "L07"), ["L07"], "solo", foto("F03"), None, PD,
        nota="'escola boa' — a placa do Oneida Baptist Institute")
    add("V06", pal("mas", "L07"), fim("L07"), ["L07"], "full", vid("Y016"), {"x": 0.42, "y": 0.4}, GSB,
        nota="'limpava os banheiros' — ele em Stanford: 'limpei mais banheiros do que todos vocês juntos'")
    # L08 "Depois, / ele foi lavar prato num Denny's."
    add("V07", ini("L08"), fim("L08"), ["L08"], "pilha", faixas=[
        faixa(vid("Y044"), {"x": 0.35, "y": 0.4}, HOOVER),                      # o letreiro do Denny's
        faixa(vid("Y043"), {"x": 0.55, "y": 0.4, "area": A_60}, CBS60),         # ele no booth: "a normal dishwasher…"
        faixa(vid("Y039", lento=0.6), {"x": 0.5, "y": 0.5, "area": A_60}, CBS60),          # a caneca do Denny's
    ], nota="'lavar prato num Denny's'")
    # L09 "Em 1993, / num outro Denny's, / ele e dois amigos planejaram a Nvidia."
    add("V08", ini("L09"), pal("num", "L09"), ["L09"], "full", vid("Y029", ate=4.0), {"x": 0.48, "y": 0.4},
        EXPLORIST, nota="'Em 1993' — ele jovem, anos 90")
    add("V09", pal("num", "L09"), pal("ele", "L09"), ["L09"], "full", vid("Y037", tin=0.3),
        {"x": 0.74, "xFim": 0.57, "y": 0.5}, CBS60, nota="'num outro Denny's' — ele entra no Denny's de San Jose")
    add("V10", pal("ele", "L09"), fim("L09"), ["L09"], "solo", vid("Y023", tin=0.3, ss=3.4, lento=0.6), None, EXPLORIST,
        nota="'ele e dois amigos planejaram a Nvidia' — os 3 fundadores, os nomes aparecem um a um")
    # L10 "Só que a empresa quase quebrou." = Carlos (ênfase)
    # L11 "Anos depois, / chegou a inteligência artificial."
    add("V11", ini("L11"), fim("L11"), ["L11"], "pilha", faixas=[
        faixa(vid("Y095", tin=0.3), {"x": 0.5, "y": 0.42, "zoom": 1.5, "area": A_CNBC}, CNBC),  # AlexNet, vencedor do ImageNet 2012
        faixa(foto("F14"), {"x": 0.5, "y": 0.5}, CHM),                          # o PC com 2 GPUs Nvidia da AlexNet
        faixa(vid("Y084"), {"x": 0.5, "y": 0.5, "area": A_60}, CBS60),          # data center
    ], nota="'chegou a inteligência artificial'")
    # L12 "Se o ChatGPT é o carro, / a Nvidia faz o motor."
    add("V12", ini("L12"), pal("a", "L12"), ["L12"], "solo", vid("Y093", lento=0.6), {"area": A_CNBC_SOLO}, CNBC,
        nota="'Se o ChatGPT é o carro' — a tela do ChatGPT")
    add("V13", pal("a", "L12"), fim("L12"), ["L12"], "full", vid("Y079", tin=1.6), {"x": 0.5, "y": 0.4}, CBS60,
        nota="'a Nvidia faz o motor' — ele com os chips na mão")
    # L13 "Aqui em Londres, / ele recebeu do Rei Charles o mesmo prêmio"
    add("V14", ini("L13"), fim("L13"), ["L13"], "full", vid("Y105"), {"x": 0.52, "y": 0.45}, ROYAL,
        nota="'Londres… Rei Charles' — o Rei entrega a medalha a ele (St James's Palace, nov/2025)")
    # L14 "do Hinton e da Fei-Fei Li, / de quem eu já falei aqui."
    t_l14 = pal("de", "L14") if L14_CAPAS else fim("L14")
    add("V15", ini("L14"), t_l14, ["L14"], "pilha", faixas=[
        faixa(vid("Y104"), {"x": 0.46, "y": 0.45, "zoom": 1.3}, ROYAL),                     # o Rei entrega a medalha ao Hinton
        faixa(vid("Y106"), {"x": 0.42, "y": 0.45}, ROYAL),                     # ele e a Fei-Fei com o Rei
        faixa(foto("N18"), {"x": 0.5, "y": 0.4}, HAI),                         # os sete laureados
    ], nota="'do Hinton e da Fei-Fei Li'")
    if L14_CAPAS:
        add("V15b", t_l14, fim("L14"), ["L14"], "pilha", faixas=[
            faixa(capa("2026-10-20-geoffrey-hinton", "capa-hinton"), {"x": 0.5, "y": 0.42}, None),
            faixa(capa("2026-10-20-fei-fei-li", "capa-fei-fei"), {"x": 0.5, "y": 0.42}, None),
        ], nota="'de quem eu já falei aqui' — as capas dos dois Reels")
    # L15 "A história dele mostra uma coisa:" = Carlos (ênfase)
    # L16 "o seu Denny's pode ser / onde você está agora." — o Denny's de San Jose ao pôr do sol
    add("V16", ini("L16"), fim("L16"), ["L16"], "full", vid("Y048", tin=3.0), {"x": 0.68, "y": 0.5}, SEB,
        nota="'o seu Denny's pode ser onde você está agora'")
    # L17–L19 = CTA: o Carlos em tela cheia (regra rígida 6)
    return S


# ====================================================================================================================
# Montagem
# ====================================================================================================================
def resolver_tudo(S: list[dict]) -> None:
    for o in S:
        dur = o["t1"] - o["t0"]
        if o["faixas"]:
            for f in o["faixas"]:
                f["plano"] = resolver(f["midia"], dur)
        else:
            o["plano"] = resolver(o["midia"], dur)


def conferir(S: list[dict], T: Tempos) -> None:
    for x, y in zip(S, S[1:]):
        assert y["t0"] >= x["t1"] - 1e-6, f"{x['tag']} e {y['tag']} se sobrepõem"
        ids_x = {f["midia"]["id"] for f in x["faixas"]} if x["faixas"] else {x["midia"]["id"]}
        ids_y = {f["midia"]["id"] for f in y["faixas"]} if y["faixas"] else {y["midia"]["id"]}
        assert not (ids_x & ids_y) or y["t0"] - x["t1"] > 1e-6, f"mesma imagem seguida: {x['tag']}/{y['tag']}"
    usados: dict[str, str] = {}
    for o in S:
        assert o["t1"] - o["t0"] > 0.2, f"{o['tag']} com {o['t1'] - o['t0']:.2f}s"
        if o["t1"] - o["t0"] < 0.8:
            print(f"AVISO: {o['tag']} dura só {o['t1'] - o['t0']:.2f}s", file=sys.stderr)
        for l in o["linhas"]:
            assert T.secao.get(l) != "cta", f"{o['tag']}: extra no CTA ({l}) — regra rígida 6"
        for f in (o["faixas"] or [{"midia": o["midia"]}]):
            i = f["midia"]["id"]
            if i in usados:
                print(f"AVISO: {i} aparece duas vezes ({usados[i]} e {o['tag']})", file=sys.stderr)
            usados[i] = o["tag"]


def montar(S: list[dict]) -> list[dict]:
    overlays = []
    for o in S:
        a, b = o["t0"], o["t1"]
        base = {"linhas": o["linhas"], "tipo": "extra", "extra": o["tag"], "som": False, "faltando": False,
                "saida_inicio": a, "saida_fim": b}
        if o["faixas"]:
            itens = []
            for f in o["faixas"]:
                arq, tipo, tin = preparar(f["plano"], o["tag"])
                item = {"id": f["midia"]["id"], "arquivo": str(arq.relative_to(VIDEO)), "extra_tipo": tipo,
                        "som": False, "enquadrar": f["enq"], "credito": f["cred"]}
                if tipo == "video":
                    item["in"] = tin or 0.0
                itens.append(item)
            ov = {**base, "extra_tipo": itens[0]["extra_tipo"], "arquivo": itens[0]["arquivo"], "modo": "pilha",
                  "credito": None, "pilha": itens,
                  "descricao": f"v1 {o['tag']} pilha " + "+".join(i["id"] for i in itens)}
        else:
            arq, tipo, tin = preparar(o["plano"], o["tag"])
            ov = {**base, "extra_tipo": tipo, "arquivo": str(arq.relative_to(VIDEO)), "modo": o["modo"],
                  "credito": o["cred"], "descricao": f"v1 {o['tag']} {o['modo']} {o['midia']['id']}"}
            if o["modo"] in ("full", "solo") and o["enq"]:
                ov["enquadrar"] = o["enq"]
            if tipo == "video":
                ov["in"] = tin or 0.0
        overlays.append(ov)
    return overlays


def carlos(S: list[dict], dur: float) -> list[tuple[float, float]]:
    livres, t = [], 0.0
    for o in S:
        if o["t0"] - t > 1e-6:
            livres.append((t, o["t0"]))
        t = max(t, o["t1"])
    if dur - t > 1e-6:
        livres.append((t, dur))
    return livres


def descrever(o: dict) -> str:
    def um(m: dict) -> str:
        p = m["plano"]
        if p == "video":
            return f"{m['id']}" + (f"@{m['tin']:g}" if m.get("tin") else "")
        if p == "lento":
            return f"{m['id']} LENTO×{1 / m['fator']:.2f}"
        if p == "still":
            return f"{m['id']} parado@{m['ss']:g}"
        return m["id"]
    if o["faixas"]:
        return " / ".join(um(f["plano"]) for f in o["faixas"])
    return um(o["plano"])


# ====================================================================================================================
# Folha de contato (1 quadro por cena, maquete 9:16 com a mesma geometria do Reel.tsx)
# ====================================================================================================================
W, H = 1080, 1920
SPLIT_H, SOLO_BASE, SOLO_MAX, VAO, RODAPE_Y = 608, 1000, 700, 6, 1262


def _fonte(tam: int):
    from PIL import ImageFont
    for p in ("/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/SFNS.ttf"):
        try:
            return ImageFont.truetype(p, tam)
        except OSError:
            pass
    return ImageFont.load_default()


def _quadro_da_midia(m: dict, dur: float, tmp: Path):
    from PIL import Image
    p = m["plano"]
    if p == "foto":
        return Image.open(m["src"]).convert("RGB")
    if p == "still":
        t = m["ss"]
    elif p == "lento":
        t = m["tin"] + m["util"] * 0.5
    else:
        t = m["tin"] + min(dur, (m["ate"] or dur_video(m["src"])) - m["tin"]) * 0.5
    png = tmp / f"q-{m['id']}-{t:.2f}.png"
    rodar([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t:.2f}", "-i", str(m["src"]),
           "-frames:v", "1", str(png)])
    return Image.open(png).convert("RGB")


def _enquadrada(img, e: dict | None, jw: int, jh: float, p: float = 0.5):
    """MidiaEnquadrada (Reel.tsx): cover da área + foco + zoom + Ken Burns/pan, presa na área."""
    e = e or {}
    Wf, Hf = img.size
    a = e.get("area") or {"x": 0, "y": 0, "largura": Wf, "altura": Hf}
    kb = 1 + (e.get("kenBurns", 1.1) - 1) * p
    s = max(jw / a["largura"], jh / a["altura"]) * max(1, e.get("zoom", 1)) * kb
    vw, vh = jw / s, jh / s
    q = (1 - math.cos(math.pi * p)) / 2
    x0, y0 = e.get("x", 0.5), e.get("y", 0.5)
    fx = x0 + (e.get("xFim", x0) - x0) * q
    fy = y0 + (e.get("yFim", y0) - y0) * q

    def prender(c, ini, tam, jan):
        return min(ini + tam - jan / 2, max(ini + jan / 2, c))
    cx = prender(a["x"] + fx * a["largura"], a["x"], a["largura"], vw)
    cy = prender(a["y"] + fy * a["altura"], a["y"], a["altura"], vh)
    caixa = (cx - vw / 2, cy - vh / 2, cx + vw / 2, cy + vh / 2)
    return img.resize((jw, round(jh)), box=caixa)


def _texto(d, xy, txt, tam, cor=(255, 255, 255), centro=False):
    f = _fonte(tam)
    if centro:
        l, t, r, b = d.textbbox((0, 0), txt, font=f)
        xy = (xy[0] - (r - l) / 2, xy[1] - (b - t) / 2)
    d.text(xy, txt, font=f, fill=cor)


def _credito(d, txt: str | None, y: int = RODAPE_Y) -> None:
    if not txt:
        return
    f = _fonte(24)
    t = f"Fonte: {txt}"
    l, tp, r, b = d.textbbox((60, y), t, font=f)
    d.rectangle((l - 10, tp - 4, r + 10, b + 4), fill=(0, 0, 0))
    d.text((60, y), t, font=f, fill=(242, 242, 242))


def _carlos(d, box, rotulo: str) -> None:
    d.rectangle(box, fill=(58, 52, 48))
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    _texto(d, (cx, cy - 40), "CARLOS", 110, (235, 205, 170), centro=True)
    if rotulo:
        _texto(d, (cx, cy + 70), rotulo, 46, (235, 205, 170), centro=True)


def maquete(o: dict | None, tmp: Path, rotulo_carlos: str = ""):
    from PIL import Image, ImageDraw
    tela = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(tela)
    if o is None:
        _carlos(d, (0, 0, W, H), rotulo_carlos)
        return tela
    dur = o["t1"] - o["t0"]
    if o["modo"] == "pilha":
        n = len(o["faixas"])
        hf = (H - VAO * (n - 1)) / n
        tela.paste((14, 14, 14), (0, 0, W, H))
        for i, f in enumerate(o["faixas"]):
            img = _quadro_da_midia(f["plano"], dur, tmp)
            tela.paste(_enquadrada(img, f["enq"], W, hf), (0, round(i * (hf + VAO))))
        creds = " · ".join(dict.fromkeys(c for c in (f["cred"] for f in o["faixas"]) if c))
        _credito(d, creds or None)
        return tela
    img = _quadro_da_midia(o["plano"], dur, tmp)
    if o["modo"] == "full":
        tela.paste(_enquadrada(img, o["enq"], W, H), (0, 0))
        _credito(d, o["cred"])
    elif o["modo"] == "solo":
        a = (o["enq"] or {}).get("area") or {"x": 0, "y": 0, "largura": img.size[0], "altura": img.size[1]}
        esc = min(W / a["largura"], SOLO_MAX / a["altura"])
        w, h = round(a["largura"] * esc), round(a["altura"] * esc)
        rec = img.resize((w, h), box=(a["x"], a["y"], a["x"] + a["largura"], a["y"] + a["altura"]))
        tela.paste(rec, ((W - w) // 2, SOLO_BASE - h))
        _credito(d, o["cred"])
    elif o["modo"] == "split":
        tela.paste(img.resize((W, SPLIT_H)), (0, 0))
        _carlos(d, (0, SPLIT_H, W, H), "embaixo")
        _credito(d, o["cred"], SPLIT_H - 16 - 31)
    return tela


def folha_de_contato(S: list[dict], T: Tempos, saida: Path) -> None:
    from PIL import Image, ImageDraw
    TW, TH, FAIXA = 270, 480, 92
    ordem: list[tuple[dict | None, str, str, str]] = []   # (overlay|None, cabeçalho, linha 2, linha 3)
    livres = carlos([o for o in S], T.duracao)
    eventos = [(o["t0"], o) for o in S] + [(a, (a, b)) for a, b in livres]
    for t, ev in sorted(eventos, key=lambda x: x[0]):
        if isinstance(ev, tuple):
            a, b = ev
            ls = [l for l, (x, y) in T.lin.items() if x < b - 0.05 and y > a + 0.05]
            rot = f"{ls[0]}–{ls[-1]}" if len(ls) > 1 else (ls[0] if ls else "")
            extra = " (A: desde 0)" if a > 0 and ls and ls[0] == "L03" else ""
            ordem.append((None, f"CARLOS · {a:.1f}–{b:.1f}s", f"{rot}{extra}", "tela cheia"))
        else:
            o = ev
            cab = f"{o['tag']} · {o['t0']:.1f}–{o['t1']:.1f}s · {','.join(o['linhas'])}"
            ordem.append((o, cab, f"{o['modo']}{' · só B' if o['so_b'] else ''}", descrever(o)))
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        (tmp / "tiles").mkdir()
        for i, (o, l1, l2, l3) in enumerate(ordem):
            tela = maquete(o, tmp, l2 if o is None else "")
            tile = Image.new("RGB", (TW, TH + FAIXA), (255, 255, 255))
            tile.paste(tela.resize((TW, TH)), (0, 0))
            d = ImageDraw.Draw(tile)
            d.rectangle((0, TH, TW, TH + FAIXA), fill=(20, 20, 20))
            cor = (255, 214, 102) if o is not None and o["so_b"] else (255, 255, 255)
            _texto(d, (8, TH + 6), l1, 17, cor)
            _texto(d, (8, TH + 34), l2, 17, (200, 200, 200))
            _texto(d, (8, TH + 60), l3[:34], 16, (170, 220, 255))
            tile.save(tmp / "tiles" / f"{i + 1:02d}.png")
        cols = 8
        linhas = math.ceil(len(ordem) / cols)
        saida.parent.mkdir(parents=True, exist_ok=True)
        rodar([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-framerate", "1", "-start_number", "1",
               "-i", str(tmp / "tiles" / "%02d.png"),
               "-vf", f"tile={cols}x{linhas}:padding=6:margin=6:color=white", "-frames:v", "1", "-q:v", "3",
               str(saida)])
    print(f"folha de contato ({len(ordem)} quadros) → {saida}")


# ====================================================================================================================
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--seco", action="store_true", help="só mostra o plano (não copia mídia nem grava overlays)")
    ap.add_argument("--estimativa", action="store_true", help="usa os tempos estimados mesmo com a EDL")
    ap.add_argument("--contato", action="store_true", help="gera qa/sequencia-extras-contato.jpg")
    args = ap.parse_args()

    T = Tempos(args.estimativa)
    if not T.real and not args.seco:
        raise SystemExit("sem edicao/edl.json: rode com --seco (plano/contato) ou depois do /editar")
    S = sequencia(T)
    resolver_tudo(S)
    conferir(S, T)

    print(f"tempos: {T.modo} · duração {T.duracao:.2f}s · L04_PLACA={L04_PLACA} · L14_CAPAS={L14_CAPAS}")
    for o in S:
        print(f"{o['tag']:4} {o['t0']:6.2f}–{o['t1']:6.2f} ({o['t1'] - o['t0']:4.2f}s) {','.join(o['linhas']):8} "
              f"{o['modo']:5} {descrever(o)}{'  [só B]' if o['so_b'] else ''}")
        for m in ([f["plano"] for f in o["faixas"]] if o["faixas"] else [o["plano"]]):
            if m.get("aviso"):
                print(f"      ↳ {m['id']}: {m['aviso']}")
    sa = [o for o in S if not o["so_b"]]
    print("Carlos em tela cheia — B: " + ", ".join(f"{a:.2f}–{b:.2f}" for a, b in carlos(S, T.duracao)))
    print("Carlos em tela cheia — A: " + ", ".join(f"{a:.2f}–{b:.2f}" for a, b in carlos(sa, T.duracao)))
    entra = max(o["t1"] for o in S if o["so_b"])
    print(f"B: o Carlos entra aos {entra:.2f}s (anotar em _controle/testes-abertura.md depois do render)")

    if args.contato:
        folha_de_contato(S, T, VIDEO / "qa/sequencia-extras-contato.jpg")
    if args.seco:
        return
    ov = montar(S)
    origem = f"edicao/sequencia-extras.md (v1, tempos {T.modo})"
    (AQUI / "overlays-v1.json").write_text(json.dumps({"origem": origem + " — versão B", "overlays": ov},
                                                      ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ov_a = [o for o in ov if not o["extra"].startswith("B")]          # A = sem a abertura B1–B4
    (AQUI / "overlays-v1-A.json").write_text(json.dumps({"origem": origem + " — versão A", "overlays": ov_a},
                                                        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(ov)} overlays → {AQUI / 'overlays-v1.json'} (B) · {len(ov_a)} → overlays-v1-A.json (A)")


if __name__ == "__main__":
    main()
