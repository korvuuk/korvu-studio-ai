"""Gera o vídeo de teste sintético videos/_teste-sintetico/ (principal + cenas extras) para o pipeline.

uso: uv run python tests/make_synthetic.py [--limpar] [--voz Luciana]
     uv run python tests/make_synthetic.py --so-e04      # só "entrega" o extra E04 que faltava
     uv run python tests/make_synthetic.py --modo monitor [--limpar] [--voz-ia Luciana] [--voz-carlos "Reed (...)"]
         -> videos/_teste-monitor/ (método "ChatGPT monitor": duas vozes na mesma gravação, ver TIMELINE_MONITOR)

MODO MONITOR (gravação real do Carlos: o ChatGPT Voice, no alto-falante do celular na sala, lê cada linha e o
Carlos repete para a câmera; o ChatGPT também "monitora": "de novo", "repete: …", "faltou a palavra X", "próxima").
  - voz da IA (padrão Luciana) processada como alto-falante de celular longe do microfone: highpass 350 Hz (2×),
    lowpass 7 kHz, −10 dB e reverb curta de sala (aecho); voz do "Carlos" (padrão Reed, masculina) seca/perto.
  - roteiro sem cenas extras (só textos), mesmo texto das linhas do modo clássico.
  - casos: leitura da IA antes de cada linha · erro do Carlos + "De novo. Faltou a palavra contexto. Repete: …" +
    retake limpo · "Próxima." colado numa leitura · IA começando 0,3 s ANTES do fim de um take do Carlos
    (sobreposição, L04-T2 — o L04-T1 limpo tem de ganhar) · "de novo" dito pelo próprio Carlos (separador) ·
    L07 lida pela IA e nunca repetida pelo Carlos (tem de ficar `faltando`).
  - verdade.json: cada pedaço com "locutor" (ia|carlos), início/fim da colocação e início/fim reais (energia,
    com a cauda da reverb) — base da conferência de acerto do locutores.py.

Cria (imitando a Lumix S5IIX do Carlos: 4K 25p 4:2:2 10-bit V-Log, gravada na vertical):
  roteiro.json / roteiro.md   (contrato §1 + §1b: `extras` e `extras_ref`, escrito diretamente)
  brutos/principal/camera-01.mov      3840x2160 com rotação de 90° (vertical), 25 fps, ProRes 422 HQ yuv422p10le
        (como gravação em SSD); imagem "log" (pretos levantados, brancos baixos, pouca saturação), voz TTS pt-BR
        em PCM 24-bit 48 kHz, timer + rótulo do trecho + marcadores de orientação (quadrado branco no canto
        superior esquerdo do quadro em pé, pretos nos outros três)
  brutos/principal/camera-00-cor.mov  2 s de amostra de cor (fica FORA do pipeline)
  brutos/extras/E01-chatgpt.mp4       gravação de ecrã 1920x1080 30 fps, 6 s, sem áudio (split em L03+L04 —
        mais curta que a fala: segura o último quadro; 30 -> 25 fps com aviso)
  brutos/extras/E03-exemplo.png       imagem 1600x1200 (card em L02, com crédito)
  E02 = animação (sem arquivo; componente "_teste-sintetico/E02" no registry do Remotion; full em L05)
  E04 = vídeo declarado no roteiro mas SEM arquivo (split em L06) -> faltando; `--so-e04` cria o arquivo
  verdade.json   (tempo real de cada pedaço, para conferência)

Problemas propositais na fala:
  - L03 falada 3x: T1 cortada no meio, T2 com muleta "é...", T3 limpa  -> esperado: escolhe L03-T3
  - L04 com pausa interna de 1,0 s                                    -> encurtada para 0,25 s
  - L05 falso começo + "de novo" + linha completa                     -> false_start, separador descartado
  - 3 s de silêncio entre L05 e L06                                   -> some no corte
  - frase improvisada fora do roteiro                                 -> nao_mapeado, fora do corte
  - L07 não gravada                                                   -> faltando (e no qa/diff.md)
  - L01B (hook alternativo) gravado no fim                            -> alinhado, fora da EDL principal
Coluna TELA com vários itens (" · " e "|"): EXTRA + TEXTO (L04), TEXTO + ZOOM (L01), GESTO/B-ROLL (ignorados).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude" / "skills" / "corte-por-roteiro" / "scripts"))
from common import FFMPEG, FFPROBE, escrever_json  # noqa: E402

VD = ROOT / "videos" / "_teste-sintetico"
PRINCIPAL = VD / "brutos" / "principal"
EXTRAS_DIR = VD / "brutos" / "extras"
FONTE = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
SR = 48000
FPS_CAMERA = 25
W4K, H4K = 2160, 3840            # quadro "em pé"; gravado deitado (3840x2160) com rotação de 90°
MARCA = 300                      # lado dos marcadores de orientação (px no quadro 2160x3840)
# visual "log": pretos levantados, brancos baixos, pouca saturação
LOOK_LOG = ("colorlevels=romin=0.10:gomin=0.10:bomin=0.10:romax=0.70:gomax=0.70:bomax=0.70,"
            "hue=s=0.55")

LINHAS = [
    # id, secao, fala_original, tela, animacao, alternativa_de
    ("L01", "hook", "Você tá usando o **ChatGPT** do jeito **errado** [pausa]",
     'TEXTO: "CHATGPT ERRADO?" · ZOOM · GESTO: aponta pra câmera', None, None),
    ("L01B", "hook", "Pare de usar o **ChatGPT** desse jeito agora [pausa]", 'TEXTO: "PARE!"', None, "L01"),
    ("L02", "promessa", "Hoje eu vou te mostrar 3 truques simples pra resolver isso",
     "EXTRA: E03 card | GESTO: mostra três dedos", None, None),
    ("L03", "corpo", "O primeiro truque é dar **contexto** antes de pedir qualquer coisa", "EXTRA: E01 split", None, None),
    ("L04", "corpo", "O segundo truque é pedir **exemplos**, e aí a resposta melhora muito",
     'EXTRA: E01 split · TEXTO: "PEÇA EXEMPLOS" · GESTO: aponta pra baixo, pra tela', None, None),
    ("L05", "corpo", "O terceiro truque é revisar o texto com as suas próprias palavras",
     "EXTRA: E02 full · B-ROLL: mãos no teclado", None, None),
    ("L06", "payoff", "Com esses três truques você economiza **horas** toda semana [pausa]", "EXTRA: E04 split",
     None, None),
    ("L07", "cta", "Comenta **PROMPT** que eu te mando o guia completo", 'TEXTO: "COMENTA PROMPT"', None, None),
    ("L08", "cta", "E me segue pra aprender inteligência artificial sem complicação [pausa longa]", "", None, None),
]

EXTRAS = [
    {"id": "E01", "tipo": "tela", "descricao": "ChatGPT: prompt com contexto e exemplos (gravação de ecrã)",
     "fonte": "Carlos grava o ecrã", "credito": None, "som": False, "linhas": ["L03", "L04"]},
    {"id": "E02", "tipo": "animacao", "descricao": "3 caixas Prompt → IA → Resposta", "fonte": "Claude Design",
     "credito": None, "som": False, "linhas": ["L05"]},
    {"id": "E03", "tipo": "imagem", "descricao": "Imagem de exemplo no cartão", "fonte": "gerada pelo teste",
     "credito": "Banco de imagens (teste)", "som": False, "linhas": ["L02"]},
    {"id": "E04", "tipo": "video", "descricao": "Demo oficial do produto (ainda não chegou)", "fonte": "site oficial",
     "credito": "OpenAI (demo)", "som": False, "linhas": ["L06"]},
]
_TC = r"\d{1,2}:\d{2}(?:[.,]\d+)?"
EXTRA_RE = re.compile(rf"EXTRA\s*:\s*(E\d{{2}})(?:\s+(split|full|card))?(?:\s+({_TC})\s*[–-]\s*({_TC}))?", re.I)

# ("fala", texto_tts, rótulo) | ("sil", segundos)   — [[slnc N]] = silêncio de N ms dentro da fala
TIMELINE = [
    ("sil", 0.8),
    ("fala", "Você tá usando o ChatGPT do jeito errado.", "L01-T1"),
    ("sil", 0.9),
    ("fala", "Hoje eu vou te mostrar três truques simples pra resolver isso.", "L02-T1"),
    ("sil", 1.0),
    ("fala", "O primeiro truque é dar contexto", "L03-T1 cortado"),
    ("sil", 0.8),
    ("fala", "O primeiro truque é dar [[slnc 350]] é... [[slnc 450]] contexto antes de pedir qualquer coisa.",
     "L03-T2 muleta"),
    ("sil", 1.0),
    ("fala", "O primeiro truque é dar contexto antes de pedir qualquer coisa.", "L03-T3 limpo"),
    ("sil", 0.9),
    ("fala", "O segundo truque é pedir exemplos,", "L04-T1 parte 1"),
    ("sil", 1.0),
    ("fala", "e aí a resposta melhora muito.", "L04-T1 parte 2"),
    ("sil", 1.0),
    ("fala", "O terceiro truque é revisar", "L05-T1 falso comeco"),
    ("sil", 0.4),
    ("fala", "de novo.", "SEPARADOR"),
    ("sil", 0.7),
    ("fala", "O terceiro truque é revisar o texto com as suas próprias palavras.", "L05-T2"),
    ("sil", 3.0),
    ("fala", "Com esses três truques você economiza horas toda semana.", "L06-T1"),
    ("sil", 1.0),
    ("fala", "Nossa, esqueci de tomar água antes de gravar.", "IMPROVISO"),
    ("sil", 1.2),
    ("fala", "E me segue pra aprender inteligência artificial sem complicação.", "L08-T1"),
    ("sil", 1.5),
    ("fala", "Pare de usar o ChatGPT desse jeito agora.", "L01B-T1"),
    ("sil", 1.0),
]

# MODO MONITOR — ("ia"|"carlos", texto, rótulo[, sobrepor_s]) | ("sil", s). `sobrepor_s`: a fala começa esse
# tanto ANTES do fim real (energia) do pedaço anterior.
VD_MONITOR = ROOT / "videos" / "_teste-monitor"
VOZ_IA = "Luciana"
VOZ_CARLOS = "Reed (Portuguese (Brazil))"
# alto-falante de celular na sala, longe do microfone da câmera
CADEIA_CELULAR = ("highpass=f=350,highpass=f=350,lowpass=f=7000,volume=-10dB,"
                  "aecho=0.8:0.7:23|41|67|113:0.35|0.25|0.15|0.08")
TIMELINE_MONITOR = [
    ("sil", 0.8),
    ("ia", "Você tá usando o ChatGPT do jeito errado.", "IA L01"),
    ("sil", 0.6),
    ("carlos", "Você tá usando o ChatGPT do jeito errado.", "L01-T1"),
    ("sil", 0.9),
    ("ia", "Próxima. Hoje eu vou te mostrar três truques simples pra resolver isso.", "IA proxima + L02"),
    ("sil", 0.6),
    ("carlos", "Hoje eu vou te mostrar três truques simples pra resolver isso.", "L02-T1"),
    ("sil", 1.0),
    ("ia", "O primeiro truque é dar contexto antes de pedir qualquer coisa.", "IA L03"),
    ("sil", 0.6),
    ("carlos", "O primeiro truque é dar exemplo antes de pedir qualquer coisa.", "L03-T1 erro"),
    ("sil", 0.5),
    ("ia", "De novo. Faltou a palavra contexto. Repete: o primeiro truque é dar contexto antes de pedir qualquer coisa.",
     "IA de novo + repete L03"),
    ("sil", 0.6),
    ("carlos", "O primeiro truque é dar contexto antes de pedir qualquer coisa.", "L03-T2 limpo"),
    ("sil", 0.9),
    ("ia", "O segundo truque é pedir exemplos, e aí a resposta melhora muito.", "IA L04"),
    ("sil", 0.6),
    ("carlos", "O segundo truque é pedir exemplos, e aí a resposta melhora muito.", "L04-T1 limpo"),
    ("sil", 0.6),
    ("ia", "Boa. Mais uma vez, com mais energia.", "IA mais uma vez"),
    ("sil", 0.6),
    ("carlos", "O segundo truque é pedir exemplos, e aí a resposta melhora muito.", "L04-T2 sobreposto"),
    ("ia", "Perfeito. Próxima.", "IA sobreposta", 0.3),
    ("sil", 0.9),
    ("ia", "O terceiro truque é revisar o texto com as suas próprias palavras.", "IA L05"),
    ("sil", 0.6),
    ("carlos", "O terceiro truque é revisar", "L05-T1 falso comeco"),
    ("sil", 0.4),
    ("carlos", "de novo.", "SEPARADOR Carlos"),
    ("sil", 0.7),
    ("carlos", "O terceiro truque é revisar o texto com as suas próprias palavras.", "L05-T2"),
    ("sil", 1.0),
    ("ia", "Com esses três truques você economiza horas toda semana.", "IA L06"),
    ("sil", 0.6),
    ("carlos", "Com esses três truques você economiza horas toda semana.", "L06-T1"),
    ("sil", 1.0),
    ("ia", "Comenta PROMPT que eu te mando o guia completo.", "IA L07 (Carlos nao repete)"),
    ("sil", 1.5),
    ("ia", "Tudo bem, vamos pular. Próxima: e me segue pra aprender inteligência artificial sem complicação.",
     "IA pular + L08"),
    ("sil", 0.6),
    ("carlos", "E me segue pra aprender inteligência artificial sem complicação.", "L08-T1"),
    ("sil", 0.8),
    ("ia", "Ótimo, terminamos.", "IA fim"),
    ("sil", 1.0),
]


def sh(cmd):
    r = subprocess.run([str(c) for c in cmd], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"falhou: {' '.join(map(str, cmd[:5]))}\n{r.stderr.decode()[-2000:]}")
    return r


def dur(p: Path) -> float:
    r = sh([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p])
    return float(r.stdout.decode().strip())


def tc_seg(tc: str | None) -> float | None:
    if not tc:
        return None
    m, s = tc.replace(",", ".").split(":")
    return round(int(m) * 60 + float(s), 3)


def limpar_fala(orig: str) -> tuple[str, list[str], list[str], str]:
    pausa = "normal"
    if "[pausa longa]" in orig:
        pausa = "pausa_longa"
    elif "[pausa]" in orig:
        pausa = "pausa"
    fala = re.sub(r"\s*\[pausa( longa)?\]\s*", " ", orig).replace("**", "").strip()
    destaques = re.findall(r"\*\*(.+?)\*\*", orig)
    palavras = [re.sub(r"[^\w-]", "", w.lower()) for w in fala.split()]
    return fala, [p for p in palavras if p], destaques, pausa


def tela_sem_extras(tela: str) -> str:
    """Modo monitor: coluna TELA sem os itens EXTRA (o teste de locutores não usa cenas extras)."""
    itens = [x.strip() for x in re.split(r"[·|]", tela or "") if x.strip() and not x.strip().upper().startswith("EXTRA")]
    return " · ".join(itens)


def gerar_roteiro(monitor: bool = False):
    linhas, t = [], 0.0
    for lid, secao, orig, tela, anim, alt in LINHAS:
        if monitor:
            tela = tela_sem_extras(tela)
        fala, palavras, destaques, pausa = limpar_fala(orig)
        d = round(len(palavras) / 2.3, 2)
        ini = t if not alt else 0.0
        refs = [{"id": x.group(1).upper(), "modo": (x.group(2) or "split").lower(),
                 "in": tc_seg(x.group(3)), "out": tc_seg(x.group(4))} for x in EXTRA_RE.finditer(tela or "")]
        linhas.append({
            "id": lid, "secao": secao, "fala": fala, "fala_original": orig, "palavras": palavras,
            "destaques": destaques, "pausa_depois": pausa, "tela": tela or None, "animacao": anim,
            "extras_ref": refs, "alternativa_de": alt, "tempo_estimado": [round(ini, 2), round(ini + d, 2)],
        })
        if not alt:
            t += d
    extras = [] if monitor else EXTRAS
    roteiro = {
        "slug": VD.name, "versao": 1,
        "tema": "Teste sintético do corte por roteiro" + (" (método ChatGPT monitor)" if monitor else ""),
        "pilar": "teste", "estrutura": "1-ruptura", "duracao_alvo": 30, "wps_ref": 2.3,
        "hook_escolhido": "A", "cta_palavra": "PROMPT", "material": None, "extras": extras, "linhas": linhas,
    }
    escrever_json(VD / "roteiro.json", roteiro)
    md = [f"# Roteiro — {VD.name} (TESTE)", "",
          "> Gerado por `tests/make_synthetic.py`. Não é um vídeo real.", "",
          "| ID | Seção | FALA | TELA |", "|---|---|---|---|"]
    for l in linhas:
        md.append(f"| {l['id']} | {l['secao']} | {l['fala_original']} | {(l['tela'] or '').replace('|', '/')} |")
    md += ["", "## Cenas extras", "", "| ID | Tipo | O que mostrar | Como obter / fonte | Crédito | Som | Linhas |",
           "|---|---|---|---|---|---|---|"]
    for e in extras:
        md.append(f"| {e['id']} | {e['tipo']} | {e['descricao']} | {e['fonte']} | {e['credito'] or '—'} | "
                  f"{'sim' if e['som'] else 'não'} | {', '.join(e['linhas'])} |")
    (VD / "roteiro.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def gerar_audio(tmp: Path, voz: str) -> tuple[Path, list[dict]]:
    partes, verdade, t = [], [], 0.0
    for k, item in enumerate(TIMELINE):
        wav = tmp / f"p{k:03d}.wav"
        if item[0] == "sil":
            sh([FFMPEG, "-hide_banner", "-y", "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono",
                "-t", f"{item[1]:.3f}", "-c:a", "pcm_s16le", wav])
        else:
            aiff = tmp / f"p{k:03d}.aiff"
            sh(["say", "-v", voz, "-r", "175", "-o", aiff, item[1]])
            sh([FFMPEG, "-hide_banner", "-y", "-i", aiff, "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", wav])
        d = dur(wav)
        if item[0] == "fala":
            verdade.append({"rotulo": item[2], "texto": item[1].replace("[[slnc 350]] ", "").replace("[[slnc 450]] ", ""),
                            "inicio": round(t, 3), "fim": round(t + d, 3)})
        else:
            verdade.append({"rotulo": "silencio", "inicio": round(t, 3), "fim": round(t + d, 3)})
        partes.append(wav)
        t += d
    lista = tmp / "lista.txt"
    lista.write_text("".join(f"file '{p}'\n" for p in partes))
    audio = tmp / "voz.wav"
    sh([FFMPEG, "-hide_banner", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c:a", "pcm_s16le", audio])
    return audio, verdade


def _faixa_real(x, sr: int) -> tuple[float, float]:
    """Primeiro/último instante com energia (RMS 10 ms > max(pico − 45 dB, −70 dBFS)) — inclui a cauda da reverb."""
    import numpy as np
    h = sr // 100
    n = max(1, len(x) // h)
    rms = np.sqrt((x[:n * h].reshape(n, h) ** 2).mean(axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    ativo = np.where(db > max(db.max() - 45.0, -70.0))[0]
    if not len(ativo):
        return 0.0, len(x) / sr
    return ativo[0] * h / sr, (ativo[-1] + 1) * h / sr


def gerar_audio_monitor(tmp: Path, voz_ia: str, voz_carlos: str) -> tuple[Path, list[dict]]:
    """Duas faixas (IA pelo 'celular' + Carlos seco) na mesma linha do tempo, somadas. Sobreposição: a fala com
    `sobrepor_s` começa esse tanto antes do fim real do pedaço anterior."""
    import numpy as np
    import soundfile as sf
    pecas, verdade, t, fim_real_ant = [], [], 0.0, 0.0
    for k, item in enumerate(TIMELINE_MONITOR):
        if item[0] == "sil":
            t += item[1]
            continue
        quem, texto, rotulo = item[0], item[1], item[2]
        sobrepor = item[3] if len(item) > 3 else 0.0
        aiff, wav = tmp / f"m{k:03d}.aiff", tmp / f"m{k:03d}.wav"
        sh(["say", "-v", voz_ia if quem == "ia" else voz_carlos, "-r", "175", "-o", aiff, texto])
        seco = tmp / f"m{k:03d}-seco.wav"
        sh([FFMPEG, "-hide_banner", "-y", "-i", aiff, "-ar", str(SR), "-ac", "1", "-c:a", "pcm_f32le", seco])
        x_seco, _ = sf.read(seco, dtype="float32")
        if quem == "ia":      # celular na sala: sem graves, mais baixo, reverb curta (a cauda passa do fim seco)
            sh([FFMPEG, "-hide_banner", "-y", "-i", seco, "-af", f"apad=pad_dur=0.4,{CADEIA_CELULAR}",
                "-ar", str(SR), "-ac", "1", "-c:a", "pcm_f32le", wav])
            x, _ = sf.read(wav, dtype="float32")
        else:
            x = x_seco
        a_seco, b_seco = _faixa_real(x_seco, SR)
        a_real, b_real = _faixa_real(x, SR)
        # `t` = fim do anterior (seco) + silêncios; com sobreposição, ancora no fim real do pedaço anterior
        ini = (fim_real_ant - sobrepor - a_seco) if sobrepor else t
        pecas.append((ini, x))
        verdade.append({"rotulo": rotulo, "locutor": quem, "texto": texto,
                        "inicio": round(ini + a_seco, 3), "fim": round(ini + b_seco, 3),
                        "inicio_real": round(ini + a_real, 3), "fim_real": round(ini + b_real, 3),
                        "sobreposicao": sobrepor or None})
        t = ini + b_seco
        fim_real_ant = ini + b_seco
    total = max(ini + len(x) / SR for ini, x in pecas) + 1.0
    mix = np.zeros(int(total * SR) + 1, dtype=np.float32)
    for ini, x in pecas:
        i0 = int(round(ini * SR))
        mix[i0:i0 + len(x)] += x
    pico = float(np.abs(mix).max())
    if pico > 0.95:
        mix *= 0.95 / pico
    audio = tmp / "voz.wav"
    sf.write(audio, mix, SR, subtype="PCM_24")
    return audio, verdade


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace(",", "\\,")


def marcadores(entrada: str, saida: str) -> str:
    """Quadrado branco no canto superior esquerdo (quadro em pé) e pretos nos outros cantos."""
    m = MARCA
    return (f"[{entrada}]drawbox=x=0:y=0:w={m}:h={m}:color=white:t=fill,"
            f"drawbox=x={W4K - m}:y=0:w={m}:h={m}:color=black:t=fill,"
            f"drawbox=x=0:y={H4K - m}:w={m}:h={m}:color=black:t=fill,"
            f"drawbox=x={W4K - m}:y={H4K - m}:w={m}:h={m}:color=black:t=fill[{saida}]")


def codificar_camera(script: Path, entradas: list, destino: Path, total: float, com_audio: bool):
    """Filtergraph (quadro em pé) -> deitado 3840x2160 + rotação de 90° na displaymatrix (como a S5IIX na vertical).
    ProRes 422 HQ 10-bit (gravação em SSD). Obs.: o libx264 4:2:2 10-bit desta build gera stream inválido depois
    de `transpose`, por isso não há opção H.264 aqui (arquivos H.264 reais da câmera decodificam normalmente)."""
    venc = ["-c:v", "prores_ks", "-profile:v", "3", "-vendor", "apl0", "-pix_fmt", "yuv422p10le"]
    tmp = destino.with_name(".tmp-" + destino.stem + ".mov")
    amap = ["-map", "[a]", "-c:a", "pcm_s24le", "-ar", str(SR)] if com_audio else []
    sh([FFMPEG, "-hide_banner", "-y", *entradas, "-filter_complex_script", script, "-map", "[v]", *amap, *venc,
        "-r", str(FPS_CAMERA), "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
        "-color_range", "tv", "-t", f"{total:.3f}", tmp])
    # rotação: o player gira 90° anti-horário -> o quadro volta a ficar em pé
    sh([FFMPEG, "-hide_banner", "-y", "-display_rotation:v:0", "90", "-i", tmp, "-map", "0", "-c", "copy",
        destino])
    tmp.unlink(missing_ok=True)


def gerar_principal(audio: Path, verdade: list[dict], total: float):
    PRINCIPAL.mkdir(parents=True, exist_ok=True)
    f = [f"testsrc2=size={W4K}x{H4K}:rate={FPS_CAMERA}:duration={total:.3f}[bg]",
         f"[bg]drawtext=fontfile='{FONTE}':text='%{{pts\\:hms}}':fontsize=220:fontcolor=white:"
         f"box=1:boxcolor=black@0.7:boxborderw=40:x=(w-tw)/2:y=520[v0]"]
    last = "v0"
    for k, v in enumerate(verdade):
        if v["rotulo"] == "silencio":
            continue
        nxt = f"v{k + 1}"
        ia = v.get("locutor") == "ia"          # modo monitor: fala da IA em ciano, mais acima
        f.append(f"[{last}]drawtext=fontfile='{FONTE}':text='{esc(v['rotulo'])}':fontsize={120 if ia else 160}:"
                 f"fontcolor={'cyan' if ia else 'yellow'}:box=1:boxcolor=black@0.7:boxborderw=32:x=(w-tw)/2:"
                 f"y={2500 if ia else 3000}:enable='between(t,{v['inicio']:.3f},{v['fim']:.3f})'[{nxt}]")
        last = nxt
    f.append(marcadores(last, "vm"))
    f.append(f"[vm]{LOOK_LOG},transpose=clock,format=yuv422p10le[v]")
    f.append(f"anoisesrc=c=pink:a=0.0015:r={SR}:d={total:.3f}[ruido]")
    f.append("[1:a][ruido]amix=inputs=2:duration=first:normalize=0,aformat=channel_layouts=stereo[a]")
    script = VD / ".graph-sintetico.txt"
    script.write_text(";\n".join(f))
    codificar_camera(script, ["-f", "lavfi", "-i", "nullsrc=s=16x16:d=0.1", "-i", audio],
                     PRINCIPAL / "camera-01.mov", total, com_audio=True)
    # amostra de cor (carta de cores em log) — o pipeline de edição deve ignorá-la
    script.write_text(f"smptehdbars=size={W4K}x{H4K}:rate={FPS_CAMERA}:duration=2[c];"
                      f"[c]{LOOK_LOG},transpose=clock,format=yuv422p10le[v]")
    codificar_camera(script, [], PRINCIPAL / "camera-00-cor.mov", 2.0, com_audio=False)
    script.unlink(missing_ok=True)


def gerar_extras():
    EXTRAS_DIR.mkdir(parents=True, exist_ok=True)
    # E01: gravação de ecrã horizontal, 30 fps, 6 s (mais curta que L03+L04), sem áudio
    sh([FFMPEG, "-hide_banner", "-y", "-f", "lavfi", "-i", "testsrc=size=1920x1080:rate=30:duration=6",
        "-vf", f"drawtext=fontfile='{FONTE}':text='E01 TELA %{{pts\\:hms}}':fontsize=90:fontcolor=white:"
               f"box=1:boxcolor=black@0.6:x=(w-tw)/2:y=(h-th)/2",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", EXTRAS_DIR / "E01-chatgpt.mp4"])
    # E03: imagem 4:3
    sh([FFMPEG, "-hide_banner", "-y", "-f", "lavfi", "-i", "testsrc2=size=1600x1200:rate=1", "-frames:v", "1",
        "-vf", f"drawtext=fontfile='{FONTE}':text='E03 IMAGEM':fontsize=150:fontcolor=white:"
               f"box=1:boxcolor=black@0.6:boxborderw=30:x=(w-tw)/2:y=(h-th)/2",
        EXTRAS_DIR / "E03-exemplo.png"])


def gerar_e04():
    """O extra que 'faltava': demo 1920x1080 25 fps, 5 s, com áudio (som desligado no Reel)."""
    EXTRAS_DIR.mkdir(parents=True, exist_ok=True)
    sh([FFMPEG, "-hide_banner", "-y", "-f", "lavfi", "-i", "testsrc2=size=1920x1080:rate=25:duration=5",
        "-f", "lavfi", "-i", "sine=frequency=330:sample_rate=48000:duration=5",
        "-vf", f"drawtext=fontfile='{FONTE}':text='E04 DEMO %{{pts\\:hms}}':fontsize=100:fontcolor=white:"
               f"box=1:boxcolor=black@0.6:x=(w-tw)/2:y=(h-th)/2",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", "-c:a", "aac",
        "-shortest", EXTRAS_DIR / "E04-demo.mp4"])
    print(f"[sintetico] E04 entregue: {EXTRAS_DIR / 'E04-demo.mp4'}")


def usar_pasta(vd: Path) -> None:
    global VD, PRINCIPAL, EXTRAS_DIR
    VD, PRINCIPAL, EXTRAS_DIR = vd, vd / "brutos" / "principal", vd / "brutos" / "extras"


def main_monitor(args, vozes: str):
    for v in (args.voz_ia, args.voz_carlos):
        if v.split(" (")[0] not in vozes:
            sys.exit(f"voz '{v}' não encontrada (say -v '?' | grep pt_BR)")
    if args.voz_ia == args.voz_carlos:
        sys.exit("use vozes diferentes para a IA e para o Carlos")
    usar_pasta(VD_MONITOR)
    VD.mkdir(parents=True, exist_ok=True)
    if args.limpar:
        for d in ("edicao", "qa", "brutos", "capa"):
            shutil.rmtree(VD / d, ignore_errors=True)
        (VD / "status.json").unlink(missing_ok=True)
    gerar_roteiro(monitor=True)
    with tempfile.TemporaryDirectory() as td:
        audio, verdade = gerar_audio_monitor(Path(td), args.voz_ia, args.voz_carlos)
        total = dur(audio)
        gerar_principal(audio, verdade, total)
    (VD / "verdade.json").write_text(json.dumps(
        {"modo": "monitor", "duracao": round(total, 3), "fps": FPS_CAMERA, "codec": "prores_hq",
         "vozes": {"ia": args.voz_ia, "carlos": args.voz_carlos}, "cadeia_ia": CADEIA_CELULAR,
         "pedacos": verdade}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[sintetico] {VD}  modo monitor ({total:.1f}s de bruto; IA = {args.voz_ia} pelo 'celular', "
          f"Carlos = {args.voz_carlos} seco)")
    for v in verdade:
        print(f"   {v['inicio']:6.2f}-{v['fim']:6.2f}  {v['locutor']:<6} {v['rotulo']}"
              + (f"  (começa {v['sobreposicao']:.1f}s antes do fim do anterior)" if v.get("sobreposicao") else ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limpar", action="store_true", help="apaga edicao/, qa/ e brutos/ do teste antes de gerar")
    ap.add_argument("--modo", choices=["classico", "monitor"], default="classico",
                    help="classico = videos/_teste-sintetico (1 voz + extras); monitor = videos/_teste-monitor "
                         "(IA lê pelo celular + Carlos repete)")
    ap.add_argument("--voz", default="Luciana", help="(clássico) voz do Carlos")
    ap.add_argument("--voz-ia", default=VOZ_IA, help="(monitor) voz do ChatGPT (processada como celular)")
    ap.add_argument("--voz-carlos", default=VOZ_CARLOS, help="(monitor) voz do Carlos (seca)")
    ap.add_argument("--so-e04", action="store_true", help="só cria brutos/extras/E04-demo.mp4 (o extra que faltava)")
    args = ap.parse_args()
    if args.so_e04:
        gerar_e04()
        return
    vozes = subprocess.run(["say", "-v", "?"], capture_output=True, text=True).stdout
    if args.modo == "monitor":
        main_monitor(args, vozes)
        return
    if args.voz not in vozes:
        sys.exit(f"voz '{args.voz}' não encontrada (say -v '?' | grep pt_BR)")
    VD.mkdir(parents=True, exist_ok=True)
    if args.limpar:
        for d in ("edicao", "qa", "brutos", "capa"):
            shutil.rmtree(VD / d, ignore_errors=True)
        for f in ("status.json",):
            (VD / f).unlink(missing_ok=True)
    gerar_roteiro()
    with tempfile.TemporaryDirectory() as td:
        audio, verdade = gerar_audio(Path(td), args.voz)
        total = dur(audio)
        gerar_principal(audio, verdade, total)
    gerar_extras()
    (VD / "verdade.json").write_text(json.dumps({"duracao": round(total, 3), "fps": FPS_CAMERA, "codec": "prores_hq",
                                                 "pedacos": verdade}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[sintetico] {VD}  ({total:.1f}s de bruto, câmera ProRes 422 HQ 3840x2160 rot 90 {FPS_CAMERA} fps 10-bit)")
    print("   extras: E01 tela (6 s, 30 fps) · E02 animação (registry) · E03 imagem · E04 FALTANDO (--so-e04)")
    for v in verdade:
        if v["rotulo"] != "silencio":
            print(f"   {v['inicio']:6.2f}-{v['fim']:6.2f}  {v['rotulo']}")


if __name__ == "__main__":
    main()
