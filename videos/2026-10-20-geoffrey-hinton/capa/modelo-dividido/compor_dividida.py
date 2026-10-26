"""Capa dividida Hinton + Carlos (variante experimental, 15/10). PRÉVIA: cor = só LUT de entrada.
Uso: uv run python compor_dividida.py   (de qualquer pasta; caminhos absolutos abaixo)"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops
import json, math, sys, itertools
import os
AQUI = os.path.dirname(os.path.abspath(__file__))
S = AQUI + "/frames"
OUT = "/Users/teste/Documents/CONTENT AI/videos/2026-10-20-geoffrey-hinton/capa/modelo-dividido"
W, H = 1080, 1920
BG = (13, 13, 13); BRANCO = (242, 242, 242); CINZA = (155, 155, 155); LARANJA = (232, 80, 2)
GEIST = AQUI + "/geist.ttf"; PF = AQUI + "/pf.ttf"

def geist(sz):
    f = ImageFont.truetype(GEIST, sz); f.set_variation_by_axes([800]); return f
def playfair(sz):
    f = ImageFont.truetype(PF, sz); f.set_variation_by_axes([700]); return f

def fade_mask(w, h, left=0, right=0, top=0, bottom=0):
    m = Image.new("L", (w, h), 255); px = m.load()
    for y in range(h):
        for x in range(w):
            v = 1.0
            if left and x < left: v = min(v, x / left)
            if right and x > w - right: v = min(v, (w - x) / right)
            if top and y < top: v = min(v, y / top)
            if bottom and y > h - bottom: v = min(v, (h - y) / bottom)
            px[x, y] = int(255 * v)
    return m

def hinton(src, t=None):
    im = Image.open(src).convert("RGB")
    im = ImageEnhance.Contrast(im).enhance(1.08)
    return ImageEnhance.Brightness(im).enhance(0.95)

def carlos(src):
    im = Image.open(src).convert("RGB")
    return ImageEnhance.Brightness(im).enhance(1.0)

def paste_fade(canvas, img, xy, **fade):
    m = fade_mask(img.width, img.height, **fade)
    canvas.paste(img, xy, m)

def titulo(canvas, palavras, cinza, chave, cor_risco, box, tam_max=130, tam_min=60):
    """palavras: lista; cinza = nº de palavras iniciais em cinza; chave = índice da palavra serifa.
    Quebra balanceada: maior corpo em que (n linhas x entrelinha) cabe na caixa e cada linha cabe na largura."""
    x0, y0, x1, y1 = box; bw, bh = x1 - x0, y1 - y0
    d = ImageDraw.Draw(canvas)
    n = len(palavras)
    for tam in range(tam_max, tam_min - 1, -2):
        fg, fp = geist(tam), playfair(int(tam * 1.18))
        sp = tam * 0.28
        ws = [d.textlength(p, font=(fp if i == chave else fg)) for i, p in enumerate(palavras)]
        lh = tam * 1.0
        melhor = None
        for nl in range(1, 4):
            if lh * nl > bh: break
            for cuts in itertools.combinations(range(1, n), nl - 1):
                idx = (0,) + cuts + (n,)
                larg = [sum(ws[idx[k]:idx[k + 1]]) + sp * (idx[k + 1] - idx[k] - 1) for k in range(nl)]
                if max(larg) <= bw and (melhor is None or (nl, max(larg)) < melhor[0]):
                    melhor = ((nl, max(larg)), idx)
            if melhor: break
        if melhor: break
    idx = melhor[1]
    linhas = [[(i, palavras[i], (fp if i == chave else fg), ws[i]) for i in range(idx[k], idx[k + 1])] for k in range(len(idx) - 1)]
    total = lh * len(linhas); y = y0 + (bh - total) / 2
    for ln in linhas:
        wl = sum(w for *_, w in ln) + sp * (len(ln) - 1); x = x0 + (bw - wl) / 2
        for i, p, f, w in ln:
            cor = CINZA if i < cinza else BRANCO
            yy = y + (tam * 0.04 if i != chave else -tam * 0.10)
            d.text((x, yy), p, font=f, fill=cor)
            if i == chave:  # rabisco sob a palavra-chave
                by = y + lh * 0.98; n = 14; pts = []
                for k in range(n + 1):
                    pts.append((x + w * k / n, by + (5 if k % 2 else -5) + math.sin(k) * 2))
                d.line(pts, fill=cor_risco, width=9, joint="curve")
            x += w + sp
        y += lh
    return tam

def credito(canvas, xy, anchor="la"):
    d = ImageDraw.Draw(canvas)
    f = ImageFont.truetype(GEIST, 22); f.set_variation_by_axes([500])
    d.text(xy, "Imagem de Geoffrey Hinton: 60 Minutes CBS", font=f, fill=(120, 120, 120), anchor=anchor)

def comp_empilhada(hsrc, csrc, tit):
    """Carlos em largura cheia (1440x2560 -> 1080x1920, sem blur/espelho); Hinton recortado sem esticar."""
    cv = Image.new("RGB", (W, H), BG)
    # Hinton: x 320..1920 (fora do logo) e y 0..915 -> 1080x618, escala .675; cabelo no topo do recorte (y=240)
    h = hinton(hsrc).crop((320, 0, 1920, 900)).resize((1080, 608), Image.LANCZOS)
    c = carlos(csrc).resize((1080, 1920), Image.LANCZOS)
    cv.paste(c, (0, 1040 - 225))
    cv.paste(h, (0, 240))  # topo da cabeça (y 225 da fonte) em y=1040; queixo em ~1670
    d = ImageDraw.Draw(cv)
    d.rectangle((0, 848, W, 1036), fill=BG)  # faixa do título (corte seco, sem blur)
    d.rectangle((340, 853, 740, 856), fill=LARANJA)
    titulo(cv, *tit, box=(60, 850, 1020, 1016))
    credito(cv, (W - 40, 836), "rs")
    return cv

def comp_hinton(hsrc, tit):
    """Só Hinton: frame real a 0.9x (sem blur), título abaixo do queixo, sobre a camisa."""
    cv = Image.new("RGB", (W, H), BG)
    h = hinton(hsrc).crop((290, 0, 1490, 1080)).resize((1080, 972), Image.LANCZOS)
    cv.paste(h, (0, 240))
    g = Image.new("L", (W, 190), 0); gp = g.load()
    for y in range(190):
        for x in range(W): gp[x, y] = int(255 * min(1, y / 150))
    cv.paste(Image.new("RGB", (W, 190), BG), (0, 1040), g)
    cv.paste(Image.new("RGB", (W, H - 1212), BG), (0, 1212))
    titulo(cv, *tit, box=(60, 1050, 1020, 1255))
    credito(cv, (W - 40, 1300), "rs")
    return cv

def comp_diagonal(hsrc, csrc, tit):
    cv = Image.new("RGB", (W, H), BG)
    sh = 0.74
    hh = hinton(hsrc).crop((260, 0, 1920, 1080)); hh = hh.resize((int(hh.width * sh), int(hh.height * sh)), Image.LANCZOS)
    hx = 800 - int((732 - 260) * sh)
    hlayer = Image.new("RGB", (W, H), BG); hlayer.paste(hh, (hx, 270))
    sc = 0.78
    cc = carlos(csrc); cc = cc.resize((int(1080 * sc), int(1920 * sc)), Image.LANCZOS)
    cx = 270 - int(540 * sc); cy = 270 - int(225 * sc)
    clayer = Image.new("RGB", (W, H), BG); clayer.paste(cc, (cx, cy))
    xl = lambda y: 590 + (y - 600) * 0.06
    m = Image.new("L", (W * 2, H * 2), 0); dm = ImageDraw.Draw(m)
    dm.polygon([(0, 0), (xl(0) * 2, 0), (xl(H) * 2, H * 2), (0, H * 2)], fill=255)
    m = m.resize((W, H), Image.LANCZOS)
    cv = Image.composite(clayer, hlayer, m)
    d = ImageDraw.Draw(cv)
    d.line([(xl(250), 250), (xl(1000), 1000)], fill=LARANJA, width=5)
    g = Image.new("L", (W, 420), 0); gp = g.load()
    for y in range(420):
        a = 255 if y > 190 else int(255 * y / 170)
        for x in range(W): gp[x, y] = a
    cv.paste(Image.new("RGB", (W, 420), BG), (0, 900), g)
    ImageDraw.Draw(cv).rectangle((0, 1250, W, H), fill=BG)
    titulo(cv, *tit, box=(60, 1010, 1020, 1245), tam_max=124)
    credito(cv, (W - 40, 985), "rs")
    return cv

TITS = {
  "A": (["Quem", "é", "o", "padrinho", "da", "IA"], 3, 3, LARANJA),
  "B": (["50", "anos", "numa", "ideia", "que", "ninguém", "levava", "a", "sério"], 3, 8, (160, 160, 160)),
  "C": (["Ignorado", "por", "quase", "50", "anos", "ele", "ganhou", "o", "Nobel"], 5, 8, LARANJA),
}
HEADS = {k: " ".join(v[0]) for k, v in TITS.items()}

def grade(im):
    return im.crop((0, 240, W, 1680))

if __name__ == "__main__":
    h1 = S + "/h1.png"
    plano = [("A-empilhada", comp_empilhada, (h1, S + "/c49-full.png"), "A")]
    plano += [(f"{t}-hinton", comp_hinton, (h1,), t) for t in "ABC"]
    for nome, fn, args, t in plano:
        p, ch, kw, cr = TITS[t]
        im = fn(*args, (p, ch, kw, cr))
        im.save(f"{OUT}/capa-{nome}-previa.png"); grade(im).save(f"{OUT}/grade-{nome}-previa.png")
        print(nome, HEADS[t])
    th, tw = 640, 480
    sheet = Image.new("RGB", (tw * 4 + 50, th + 20), (30, 30, 30))
    for i, (n, *_r) in enumerate(plano):
        g = Image.open(f"{OUT}/grade-{n}-previa.png").resize((tw, th), Image.LANCZOS)
        sheet.paste(g, (10 + i * (tw + 10), 10))
    sheet.save(f"{OUT}/folha-contato-previa.jpg", quality=92)
