"""Capas Hinton com FOTO real preenchendo 1080x1920 (sem margem preta, sem blur, sem esticar). Roda sozinho.
uv run python compor_foto.py   -> capa-<nome>-previa.png, grade-<nome>-previa.png, contato.jpg, medidas.json"""
import os, sys, json, math, itertools
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
Image.MAX_IMAGE_PIXELS = None
AQUI = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(AQUI + "/../..")
FOTOS = PROJ + "/material/fotos/"
FRAMES = PROJ + "/capa/modelo-dividido/frames/"
W, H = 1080, 1920
BG = (13, 13, 13); BRANCO = (242, 242, 242); CINZA = (170, 170, 170); LARANJA = (232, 80, 2)

def geist(sz):
    f = ImageFont.truetype(AQUI + "/geist.ttf", sz); f.set_variation_by_axes([800]); return f
def playfair(sz):
    f = ImageFont.truetype(AQUI + "/pf.ttf", sz); f.set_variation_by_axes([700]); return f

def abrir(path):
    return ImageOps.exif_transpose(Image.open(path)).convert("RGB")

def painel(img, box, size):
    """Recorte REAL (sem preenchimento): box dentro da imagem, mesma proporção do destino -> resize."""
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    assert 0 <= x0 < x1 <= img.width and 0 <= y0 < y1 <= img.height, ("recorte fora da foto", box, img.size)
    assert abs((x1 - x0) / (y1 - y0) - size[0] / size[1]) < 0.01, ("proporção", box, size)
    return img.crop((x0, y0, x1, y1)).resize(size, Image.LANCZOS)

def full916(img, cx):
    cw = int(img.height * W / H); x0 = int(cx - cw / 2); x0 = max(0, min(img.width - cw, x0))
    return painel(img, (x0, 0, x0 + cw, img.height), (W, H))

def scrim(cv, y0, y1, forca=0.62, y_sai=1450, y_fim=1820):
    """Degradê escuro suave sobre a foto (não é faixa): sobe em y0->y1, segura, e volta a 0 em y_sai->y_fim,
    para a base da capa continuar sendo a foto."""
    ov = Image.new("L", (W, H), 0); px = ov.load()
    for y in range(y0, H):
        if y <= y1: a = forca * (y - y0) / (y1 - y0)
        elif y <= y_sai: a = forca
        else: a = forca * max(0.0, (y_fim - y) / (y_fim - y_sai))
        v = int(255 * a)
        for x in range(W): px[x, y] = v
    cv.paste(Image.new("RGB", (W, H), (8, 8, 8)), (0, 0), ov)

def titulo(canvas, palavras, cinza, chave, cor_risco, box, tam_max=130, tam_min=56):
    x0, y0, x1, y1 = box; bw, bh = x1 - x0, y1 - y0
    d = ImageDraw.Draw(canvas); n = len(palavras); melhor = None
    for tam in range(tam_max, tam_min - 1, -2):
        fg, fp = geist(tam), playfair(int(tam * 1.18)); sp = tam * 0.28
        ws = [d.textlength(p, font=(fp if i == chave else fg)) for i, p in enumerate(palavras)]
        lh = tam * 1.0
        for nl in range(1, 4):
            if lh * nl > bh: break
            for cuts in itertools.combinations(range(1, n), nl - 1):
                idx = (0,) + cuts + (n,)
                larg = [sum(ws[idx[k]:idx[k + 1]]) + sp * (idx[k + 1] - idx[k] - 1) for k in range(nl)]
                if max(larg) <= bw and (melhor is None or (nl, max(larg)) < melhor[0]): melhor = ((nl, max(larg)), idx)
            if melhor: break
        if melhor: break
    idx = melhor[1]
    linhas = [[(i, palavras[i], (fp if i == chave else fg), ws[i]) for i in range(idx[k], idx[k + 1])] for k in range(len(idx) - 1)]
    y = y0 + (bh - lh * len(linhas)) / 2
    for ln in linhas:
        wl = sum(w for *_, w in ln) + sp * (len(ln) - 1); x = x0 + (bw - wl) / 2
        for i, p, f, w in ln:
            cor = CINZA if i < cinza else BRANCO
            d.text((x + 2, y + 3 + (tam * 0.04 if i != chave else -tam * 0.10)), p, font=f, fill=(0, 0, 0))  # sombra leve
            d.text((x, y + (tam * 0.04 if i != chave else -tam * 0.10)), p, font=f, fill=cor)
            if i == chave:
                by = y + lh * 0.98; pts = []
                for k in range(15): pts.append((x + w * k / 14, by + (5 if k % 2 else -5) + math.sin(k) * 2))
                d.line(pts, fill=cor_risco, width=9, joint="curve")
            x += w + sp
        y += lh
    return tam

def credito(cv, txt, y=1655):
    d = ImageDraw.Draw(cv); f = ImageFont.truetype(AQUI + "/geist.ttf", 22); f.set_variation_by_axes([500])
    d.text((W - 38, y + 2), txt, font=f, fill=(0, 0, 0), anchor="rs"); d.text((W - 40, y), txt, font=f, fill=(215, 215, 215), anchor="rs")

TITS = {
  "A": (["Quem", "é", "o", "padrinho", "da", "IA"], 3, 3, LARANJA),
  "C": (["Ignorado", "por", "quase", "50", "anos", "ele", "ganhou", "o", "Nobel"], 5, 8, LARANJA),
}

FOTO = {
  "CAPA01": ("CAPA-01-hinton-2026-retrato-mao-no-rosto.jpg", 2330, "Foto: Cmichel67 / CC BY-SA 4.0"),
  "CAPA02": ("CAPA-02-hinton-2024-nobel-retrato-academia.jpg", 2583, "Foto: John Sears / CC BY-SA 4.0"),
  "N18":    ("N18-hinton-nobel-conferencia-vertical-5.jpg", 2286, "Foto: Jennifer 8. Lee / CC BY-SA 4.0"),
}
# caixa do título e início do degradê por foto (queixo medido na foto)
LAYOUT = {"CAPA01": dict(box=(60, 1110, 1020, 1262), s0=980, s1=1180),
          "CAPA02": dict(box=(60, 900, 1020, 1190), s0=760, s1=900),
          "N18":    dict(box=(60, 900, 1020, 1190), s0=760, s1=900)}

def solo(chave_foto, t):
    arq, cx, cred = FOTO[chave_foto]; L = LAYOUT[chave_foto]
    cv = full916(abrir(FOTOS + arq), cx)
    scrim(cv, L["s0"], L["s1"])
    p, ch, kw, cr = TITS[t]; titulo(cv, p, ch, kw, cr, L["box"]); credito(cv, cred)
    return cv

def dividida(chave_foto, y_seam=1000):
    arq, cx, cred = FOTO[chave_foto]
    h = abrir(FOTOS + arq)
    cw = h.width if chave_foto == "CAPA01" else h.width
    # painel do Hinton: 1080 x y_seam, largura máxima da foto
    ch = int(h.width * y_seam / W)
    assert ch <= h.height
    hp = painel(h, (0, 0, h.width, ch), (W, y_seam))
    c = abrir(FRAMES + "c49.png")   # 1440x2560
    ph = H - y_seam                 # altura do painel do Carlos
    cs = W / c.width                # 0.75
    # cabeça do Carlos a ~40 px abaixo da emenda: topo da cabeça na fonte ~ y 300
    sy0 = 300 - 40 / cs
    cp = painel(c, (0, sy0, c.width, sy0 + ph / cs), (W, ph))
    cv = Image.new("RGB", (W, H)); cv.paste(hp, (0, 0)); cv.paste(cp, (0, y_seam))
    return cv, cred

def split_completo(chave_foto, t, y_seam=1000):
    cv, cred = dividida(chave_foto, y_seam)
    ov = Image.new("L", (W, H), 0); px = ov.load()
    for y in range(y_seam - 230, y_seam):
        v = int(255 * 0.78 * (y - (y_seam - 230)) / 230)
        for x in range(W): px[x, y] = v
    cv.paste(Image.new("RGB", (W, H), (8, 8, 8)), (0, 0), ov)
    ImageDraw.Draw(cv).rectangle((0, y_seam - 2, W, y_seam + 1), fill=LARANJA)
    p, ch, kw, cr = TITS[t]; titulo(cv, p, ch, kw, cr, (60, y_seam - 140, 1020, y_seam - 8))
    credito(cv, cred, y=1655)
    return cv

def grade(im): return im.crop((0, 240, W, 1680))

def medir(im):
    g = ImageOps.grayscale(im); w, h = g.size; px = g.load()
    def media(box): 
        c = g.crop(box); return round(sum(c.tobytes()) / (c.width * c.height), 1)
    return {"topo": media((0, 0, w, 20)), "base": media((0, h - 20, w, h)), "esq": media((0, 0, 20, h)), "dir": media((w - 20, 0, w, h))}

if __name__ == "__main__":
    plano = {}
    plano["A-CAPA01"] = solo("CAPA01", "A"); plano["C-CAPA01"] = solo("CAPA01", "C")
    plano["A-CAPA02"] = solo("CAPA02", "A"); plano["A-N18"] = solo("N18", "A")
    plano["DIV-A-CAPA01"] = split_completo("CAPA01", "A"); plano["DIV-A-CAPA02"] = split_completo("CAPA02", "A")
    json_med = {}
    for n, im in plano.items():
        im.save(f"{AQUI}/capa-{n}-previa.png"); grade(im).save(f"{AQUI}/grade-{n}-previa.png"); json_med[n] = medir(im)
    json.dump(json_med, open(AQUI + "/medidas.json", "w"), indent=1)
    print(json.dumps(json_med))
    # contato
    tw, th = 405, 540; nomes = list(plano)
    sheet = Image.new("RGB", (10 + len(nomes) * (tw + 10), th + 20), (30, 30, 30))
    for i, n in enumerate(nomes): sheet.paste(Image.open(f"{AQUI}/grade-{n}-previa.png").resize((tw, th), Image.LANCZOS), (10 + i * (tw + 10), 10))
    sheet.save(AQUI + "/contato.jpg", quality=92)
