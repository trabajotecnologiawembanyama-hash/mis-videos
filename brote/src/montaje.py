"""Montaje de un episodio de Brote: planos 3D + cámara + subtítulos palabra a palabra + textos clave + audio.
Uso: python3 montaje.py <ep01|ep02> <renders_dir> <voz_dir> <salida.mp4>"""
import json, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

EP, RENDERS, VOZ, OUT = sys.argv[1:5]
W, H, FPS, DUR = 1080, 1920, 30, 55.0
N = int(DUR * FPS)
FONT = "/usr/share/fonts/opentype/inter/"
AMARILLO = (255, 200, 61)       # #FFC83D, paleta de Brote

data = json.load(open(os.path.join(VOZ, "palabras.json")))
WORDS = data["words"]


def at(seq, nth=0):
    """Tiempo de inicio de la n-ésima aparición de una secuencia de palabras de la narración."""
    toks = seq.split()
    hits = []
    for i in range(len(WORDS) - len(toks) + 1):
        if all(WORDS[i + k]["w"].strip(",.«»¿?").lower() == toks[k].lower() for k in range(len(toks))):
            hits.append(WORDS[i]["t0"])
    return hits[nth] - 0.12


# ------------------------------------------------------------------ guion de montaje (EDL)
# (toma, inicio, fin, zoom0, zoom1, (cx0, cy0), (cx1, cy1))  cx/cy = centro relativo del encuadre (0.5 = centro)
if EP == "ep01":
    EDL = [
        ("e1_01_cenital", 0.0, at("un par"), 1.0, 1.18, (0.5, 0.5), (0.47, 0.5)),
        ("e1_02_zapatillas", at("un par"), at("Cada"), 1.06, 1.0, (0.5, 0.55), (0.5, 0.5)),
        ("e1_03_cancha_baja", at("Cada"), at("Quería"), 1.0, 1.1, (0.5, 0.55), (0.55, 0.45)),
        ("e1_04_sueno", at("Quería"), at("Pero"), 1.12, 1.0, (0.5, 0.4), (0.5, 0.5)),
        ("e1_05_casa", at("Pero"), at("Unas"), 1.0, 1.1, (0.5, 0.5), (0.42, 0.5)),
        ("e1_06_monedas", at("Unas"), at("Así"), 1.0, 1.12, (0.5, 0.5), (0.5, 0.55)),
        ("e1_07_cinta", at("Así"), at("Esa"), 1.12, 1.0, (0.5, 0.6), (0.5, 0.5)),
        ("e1_08_cartel", at("Esa"), at("Todos"), 1.0, 1.18, (0.5, 0.5), (0.5, 0.36)),
        ("e1_09_brillantes", at("Todos"), at("Pedrito miró"), 1.0, 1.1, (0.45, 0.6), (0.55, 0.6)),
        ("e1_10_mira_pies", at("Pedrito miró"), at("Si no"), 1.0, 1.08, (0.5, 0.5), (0.5, 0.45)),
        ("e1_10_mira_pies", at("Si no"), at("Lanzó"), 1.35, 1.45, (0.5, 0.33), (0.5, 0.32)),
        ("e1_11_lanzamiento", at("Lanzó"), at("Y no"), 1.0, 1.12, (0.5, 0.6), (0.5, 0.4)),
        ("e1_12_reja", at("Y no"), DUR, 1.0, 1.22, (0.5, 0.5), (0.62, 0.45)),
    ]
    TEXTS = [("SUEÑO ENORME", 0.35, at("un par")), ("ZAPATILLAS ROTAS", at("un par"), at("Cada") - 0.1),
             ("PRUEBAS EL VIERNES", at("las pruebas"), at("Todos") - 0.1)]
else:
    EDL = [
        ("e2_01_gimnasio", 0.0, at("Los otros"), 1.0, 1.22, (0.5, 0.5), (0.62, 0.5)),
        ("e2_02_ninos", at("Los otros"), at("Pedrito se"), 1.08, 1.0, (0.5, 0.5), (0.5, 0.5)),
        ("e2_03_cinta_gym", at("Pedrito se"), at("El entrenador"), 1.0, 1.15, (0.5, 0.5), (0.5, 0.55)),
        ("e2_04_entrenador", at("El entrenador"), at("Pedrito robó"), 1.0, 1.1, (0.5, 0.45), (0.5, 0.4)),
        ("e2_05_corre", at("Pedrito robó"), at("saltó"), 1.08, 1.0, (0.45, 0.5), (0.55, 0.5)),
        ("e2_06_salto", at("saltó"), at("En ese"), 1.0, 1.1, (0.5, 0.55), (0.5, 0.4)),
        ("e2_07_suela", at("En ese"), at("Pedrito cayó"), 1.0, 1.2, (0.5, 0.5), (0.45, 0.55)),
        ("e2_08_caida", at("Pedrito cayó"), at("y el gimnasio"), 1.1, 1.0, (0.5, 0.5), (0.5, 0.5)),
        ("e2_09_risas", at("y el gimnasio"), at("Puedes"), 1.0, 1.06, (0.5, 0.5), (0.5, 0.48)),
        ("e2_10_sentarte", at("Puedes"), at("Pedrito recogió"), 1.0, 1.08, (0.5, 0.45), (0.45, 0.45)),
        ("e2_09_risas", at("Pedrito recogió"), at("Se sentó"), 1.3, 1.42, (0.47, 0.4), (0.47, 0.38)),
        ("e2_11_solo", at("Se sentó"), at("Y entonces"), 1.0, 1.12, (0.5, 0.5), (0.52, 0.55)),
        ("e2_12_sombra", at("Y entonces"), DUR, 1.0, 1.15, (0.5, 0.5), (0.55, 0.55)),
    ]
    TEXTS = [("SE ROMPIÓ", at("la suela"), at("Pedrito cayó") - 0.1), ("TODOS RÍEN", at("estalló"), at("Puedes") - 0.1),
             ("¿FIN DEL SUEÑO?", at("Se sentó"), at("Y entonces") - 0.1)]


# ------------------------------------------------------------------ imagen
_cache = {}


def plate(name):
    if name not in _cache:
        im = Image.open(os.path.join(RENDERS, name + ".png")).convert("RGB")
        a = np.asarray(im, np.float32) / 255
        # gradación de Brote: contraste suave, calidez y saturación ligera
        lum = a.mean(2, keepdims=True)
        a = lum + (a - lum) * 1.18
        a = a * np.array([1.04, 1.0, 0.95], np.float32)
        a = np.clip((a - 0.5) * 1.1 + 0.52, 0, 1)
        _cache[name] = Image.fromarray((a * 255).astype(np.uint8))
        if len(_cache) > 6: _cache.pop(next(iter(_cache)))
    return _cache[name]


def ease(x):
    x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)


def frame_from(name, z, cx, cy):
    im = plate(name)
    pw, ph = im.size
    cw, ch = pw / z, ph / z
    x0 = min(max(cx * pw - cw / 2, 0), pw - cw); y0 = min(max(cy * ph - ch / 2, 0), ph - ch)
    return im.transform((W, H), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BICUBIC)


_vig = None


def vignette(img):
    global _vig
    if _vig is None:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2 * 0.8)
        _vig = (1 - 0.28 * np.clip(r - 0.55, 0, 1) ** 1.5)[..., None]
    a = np.asarray(img, np.float32) * _vig
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


# ------------------------------------------------------------------ textos
def outlined(text, font, fill, stroke, sw, shadow=True):
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    bb = tmp.textbbox((0, 0), text, font=font, stroke_width=sw)
    w, h = bb[2] - bb[0] + 40, bb[3] - bb[1] + 40
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((20 - bb[0], 20 - bb[1]), text, font=font, fill=fill, stroke_width=sw, stroke_fill=stroke)
    if shadow:
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((20 - bb[0], 26 - bb[1]), text, font=font, fill=(0, 0, 0, 150), stroke_width=sw, stroke_fill=(0, 0, 0, 150))
        sh = sh.filter(ImageFilter.GaussianBlur(6)); sh.alpha_composite(im); im = sh
    return im


_wcache = {}
SUB_FONT = ImageFont.truetype(FONT + "Inter-Black.otf", 104)
KEY_FONT = ImageFont.truetype(FONT + "Inter-Black.otf", 78)


def word_img(w):
    t = w.upper().strip()
    if t not in _wcache:
        _wcache[t] = outlined(t, SUB_FONT, (255, 255, 255, 255), (0, 0, 0, 255), 9)
    return _wcache[t]


def draw_center(img, im, cy, scale=1.0, alpha=1.0):
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BICUBIC)
    if alpha < 1.0:
        a = im.getchannel("A").point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    img.alpha_composite(im, (int((W - im.width) / 2), int(cy - im.height / 2)))


def subtitle(img, t):
    for k, w in enumerate(WORDS):
        end = WORDS[k + 1]["t0"] if k + 1 < len(WORDS) and WORDS[k + 1]["t0"] - w["t1"] < 0.35 else w["t1"] + 0.18
        if w["t0"] <= t < end:
            age = t - w["t0"]
            s = 0.86 + 0.14 * ease(age / 0.08)
            draw_center(img, word_img(w["w"].strip("«»")), 1450, s)
            return


def key_text(img, t):
    for txt, t0, t1 in TEXTS:
        if t0 <= t < t1:
            a = min(1, (t - t0) / 0.15) * min(1, (t1 - t) / 0.15)
            s = 0.92 + 0.08 * ease((t - t0) / 0.2)
            draw_center(img, outlined(txt, KEY_FONT, AMARILLO + (255,), (17, 17, 17, 255), 8) if txt not in _wcache else _wcache[txt], 420, s, a)


# ------------------------------------------------------------------ render de video
def render_video(path):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for txt, _, _ in TEXTS:
        _wcache[txt] = outlined(txt, KEY_FONT, AMARILLO + (255,), (17, 17, 17, 255), 8)
    for f in range(N):
        t = f / FPS
        for (name, t0, t1, z0, z1, c0, c1) in EDL:
            if t0 <= t < t1:
                u = ease((t - t0) / (t1 - t0))
                z = z0 + (z1 - z0) * u
                cx = c0[0] + (c1[0] - c0[0]) * u; cy = c0[1] + (c1[1] - c0[1]) * u
                img = frame_from(name, z, cx, cy)
                # micro-fundido de 3 frames en cada corte para suavizar
                if t - t0 < 3 / FPS and t0 > 0:
                    prev = [e for e in EDL if abs(e[2] - t0) < 1e-6]
                    if prev:
                        pn, pt0, pt1, pz0, pz1, pc0, pc1 = prev[0]
                        pim = frame_from(pn, pz1, pc1[0], pc1[1])
                        img = Image.blend(pim, img, (t - t0) * FPS / 3)
                break
        img = vignette(img)
        if t < 0.25: img = Image.blend(Image.new("RGB", (W, H)), img, t / 0.25)
        img = img.convert("RGBA")
        key_text(img, t)
        subtitle(img, t)
        p.stdin.write(img.convert("RGB").tobytes())
        if f % 150 == 0: print("frame", f, flush=True)
    p.stdin.close(); p.wait()


# ------------------------------------------------------------------ audio
SR = 48000
NA = int(DUR * SR)
rng = np.random.default_rng(11 if EP == "ep01" else 12)


def place(b, x, t0, g=1.0, pan=0.0):
    i0 = int(t0 * SR)
    if x.ndim == 1: x = np.stack([x * (1 - max(0, pan)), x * (1 + min(0, pan))], 1)
    n = min(len(x), NA - i0)
    if n > 0 and i0 >= 0: b[i0:i0 + n] += x[:n] * g


def lp(x, f):
    from scipy.signal import butter, sosfilt
    return sosfilt(butter(2, f, "low", fs=SR, output="sos"), x, axis=0)


def bp(x, a, b_):
    from scipy.signal import butter, sosfilt
    return sosfilt(butter(2, [a, b_], "band", fs=SR, output="sos"), x, axis=0)


def midi(m): return 440 * 2 ** ((m - 69) / 12)


def piano(f, dur=3.0, vel=0.5):
    n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for k in range(1, 8):
        fk = f * k * (1 + 0.0004 * k * k) ** 0.5
        x += 0.65 ** (k - 1) * np.sin(2 * np.pi * fk * t) * np.exp(-t * (0.7 + 0.45 * k))
    x *= np.minimum(1, t / 0.004) * vel
    x[-int(0.2 * SR):] *= np.linspace(1, 0, int(0.2 * SR))
    return x.astype(np.float32)


def pluck(f, dur=1.2, vel=0.3):
    """Cuerda pulsada (Karplus-Strong): pizzicato/ukelele cálido."""
    n = int(dur * SR); p = int(SR / f)
    buf = rng.uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * 0.996
    return (lp(out, 3500) * vel).astype(np.float32)


def pad(freqs, dur, att=1.0, rel=1.0, g=0.12, bright=1400):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.zeros((n, 2))
    for f in freqs:
        for v in range(4):
            ph = 2 * np.pi * f * (1 + rng.uniform(-0.004, 0.004)) * t + rng.uniform(0, 6)
            s = np.sin(ph) + 0.3 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)
            x[:, v % 2] += s
    env = np.minimum(1, t / att) * np.minimum(1, (dur - t) / rel)
    return (lp(x, bright) * env[:, None] * g / len(freqs)).astype(np.float32)


def thump(f=110, d=0.25, g=0.6):
    n = int(d * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * (f + 60 * np.exp(-t * 40)) * t) * np.exp(-t * 18)
    x += lp(rng.normal(0, 1, n), 1200) * np.exp(-t * 60) * 0.3
    return (x * g).astype(np.float32)


def whistle(d=0.9):
    n = int(d * SR); t = np.arange(n) / SR
    f = 2900 + 120 * np.sin(2 * np.pi * 34 * t)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.6 + 0.4 * np.sin(2 * np.pi * 34 * t) ** 2)
    x += bp(rng.normal(0, 1, n), 2500, 3500) * 0.15
    env = np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.08)
    return (x * env * 0.25).astype(np.float32)


def squeak(g=0.15):
    n = int(0.12 * SR); t = np.arange(n) / SR
    f = 1800 + 1400 * t / 0.12
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.12) * g).astype(np.float32)


def rip(d=0.35, g=0.35):
    n = int(d * SR); t = np.arange(n) / SR
    crackle = (rng.random(n) < 0.08).astype(float) * rng.uniform(0.3, 1, n)
    x = bp(rng.normal(0, 1, n) * (0.4 + crackle), 900, 6000) * np.minimum(1, t / 0.01) * np.exp(-t * 4)
    return (x * g).astype(np.float32)


def coins(g=0.2):
    n = int(0.5 * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for f in (3150, 4720, 6890, 8340):
        x += np.sin(2 * np.pi * f * t) * np.exp(-t * rng.uniform(9, 16))
    return (x * g / 4).astype(np.float32)


def murmur(d, g=0.05):
    n = int(d * SR)
    x = bp(rng.normal(0, 1, (n, 2)), 250, 1800)
    mod = 0.6 + 0.4 * np.abs(np.sin(np.arange(n) / SR * 2.3))[:, None]
    return (x * mod * g).astype(np.float32)


def laughs(d=2.5, g=0.12):
    """Risas de grupo estilizadas (ráfagas 'ja' con formantes)."""
    n = int(d * SR); out = np.zeros((n, 2))
    for v in range(7):
        f0 = rng.uniform(220, 380); start = rng.uniform(0, 0.4)
        for k in range(int(rng.uniform(4, 8))):
            t0 = start + k * rng.uniform(0.16, 0.22)
            m = int(0.12 * SR); tt = np.arange(m) / SR
            src = np.sign(np.sin(2 * np.pi * f0 * (1 - 0.15 * k / 8) * tt)) * 0.5
            syl = (bp(src, 700, 1300) + 0.6 * bp(src, 1100, 1700)) * np.sin(np.pi * tt / 0.12) ** 2
            i0 = int(t0 * SR)
            if i0 + m < n: out[i0:i0 + m, v % 2] += syl * (1 - k / 10)
    return (out * g).astype(np.float32)


def wind(d, g=0.05):
    n = int(d * SR)
    x = lp(rng.normal(0, 1, (n, 2)), 500)
    mod = 0.5 + 0.5 * np.sin(np.arange(n) / SR * 0.7)[:, None]
    return (x * mod * g).astype(np.float32)


def reverb(x, secs=1.8, wet=0.25):
    from scipy.signal import fftconvolve
    n = int(secs * SR)
    ir = rng.normal(0, 1, (n, 2)) * np.exp(-np.arange(n) / (SR * secs / 6))[:, None]
    ir = lp(ir, 4000); ir /= np.sqrt((ir ** 2).sum(0))
    y = np.stack([fftconvolve(x[:, c], ir[:, c])[:len(x)] for c in range(2)], 1)
    return x * (1 - wet) + y * wet


def build_audio(path):
    mus = np.zeros((NA, 2), np.float32); fx = np.zeros((NA, 2), np.float32)
    if EP == "ep01":
        # Do mayor / La menor: esperanza con melancolía; plucks cálidos tipo ukelele
        prog = [[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]]   # C Am F G
        t = 0.0; bar = 2.4
        while t < at("Y no") - 0.5:
            ch = prog[int(t / bar) % 4]
            place(mus, pad([midi(m - 12) for m in ch], bar + 0.6, 0.6, 0.8, 0.10), t)
            for j, m in enumerate([ch[0], ch[2], ch[1] + 12, ch[2]]):
                place(mus, pluck(midi(m), 1.2, 0.18), t + j * bar / 4, pan=(-0.3 if j % 2 else 0.3))
            if 12 <= t < 46:
                place(mus, piano(midi(ch[0] + 12), 2.4, 0.18), t + bar / 2)
            t += bar
        # gancho final: misterio (acorde suspendido) + nota grave
        place(mus, pad([midi(m) for m in (50, 57, 62, 64)], DUR - at("Y no") + 0.2, 0.8, 2.5, 0.16, 900), at("Y no") - 0.2)
        place(mus, piano(midi(38), 6.0, 0.4), at("Y no"))
        place(mus, piano(midi(74), 4.0, 0.22), at("mirándolo") + 1.0)
        # efectos
        for k, tt in enumerate(np.arange(0.4, 2.8, 0.55)): place(fx, thump(105, 0.25, 0.35), tt)
        for tt in np.arange(at("Cada") + 0.3, at("Quería"), 0.6): place(fx, thump(95, 0.25, 0.25), tt)    # pelota casi sin aire
        for tt in (at("Unas") + 0.2, at("Unas") + 0.9, at("Unas") + 1.7): place(fx, coins(0.25), tt)
        place(fx, rip(0.45, 0.4), at("Así") + 0.6); place(fx, rip(0.35, 0.3), at("Así") + 2.4)
        place(fx, thump(130, 0.2, 0.3), at("Lanzó") + 0.25)
        place(fx, wind(DUR - at("Lanzó"), 0.03), at("Lanzó") + 1.0)
        place(fx, thump(150, 0.15, 0.25), at("Lanzó") + 1.25)
    else:
        # La menor: tensión del gimnasio; corte seco cuando se rompe la suela; piano triste; grave de misterio
        place(fx, murmur(at("Los otros") + 0.5 - 0.0, 0.035), 0.0)
        place(fx, murmur(at("En ese") - at("Los otros"), 0.05), at("Los otros"))
        for tt in (1.2, 2.9, 6.1, at("Los otros") + 1.2, at("Los otros") + 2.7, at("Pedrito robó") + 0.5, at("Pedrito robó") + 1.6): place(fx, squeak(0.08), tt, pan=rng.uniform(-0.5, 0.5))
        prog = [[57, 60, 64], [53, 57, 60], [55, 59, 62], [52, 55, 59]]   # Am F G Em
        t = 0.0; bar = 2.0
        while t < at("En ese") + 0.1:
            ch = prog[int(t / bar) % 4]
            place(mus, pad([midi(m - 12) for m in ch], bar + 0.4, 0.4, 0.5, 0.09), t)
            for j in range(4):
                place(mus, pluck(midi(ch[j % 3] + (12 if j == 3 else 0)), 0.9, 0.16 + 0.04 * (t / 26)), t + j * bar / 4)
            t += bar
        place(fx, whistle(0.9), at("tocó") + 0.1)
        for tt in np.arange(at("Pedrito robó") + 0.1, at("saltó"), 0.42): place(fx, thump(115, 0.22, 0.35), tt)
        place(fx, rip(0.5, 0.55), at("la suela") + 0.1)
        place(fx, thump(70, 0.5, 0.9), at("Pedrito cayó") + 0.15)
        for k, tt in enumerate((0.4, 0.95, 1.4, 1.75)): place(fx, thump(120, 0.2, 0.4 / (k + 1)), at("el balón rebotó") + tt)
        place(fx, laughs(3.2, 0.13), at("estalló") - 0.1)
        # piano triste
        for k, m in enumerate([69, 67, 64, 62, 60, 64, 62, 57]):
            place(mus, piano(midi(m), 2.6, 0.24), at("Pedrito cayó") + 1.0 + k * 1.15)
        place(mus, pad([midi(m) for m in (45, 52, 57, 60)], 14, 1.5, 3, 0.12, 800), at("Pedrito recogió"))
        place(fx, wind(12, 0.035), at("Se sentó") - 0.2)
        # la sombra: nota grave + pulso de suspenso
        place(mus, pad([midi(m) for m in (33, 40, 45)], 7.0, 0.3, 2.5, 0.2, 500), at("Y entonces"))
        place(mus, piano(midi(33), 5.0, 0.5), at("una sombra"))
        place(mus, piano(midi(75), 3.0, 0.2), at("sol") + 0.4)
    mus = reverb(mus, 2.4, 0.3); fx = reverb(fx, 1.4 if EP == "ep02" else 0.9, 0.18)
    w = wave.open(os.path.join(VOZ, "voz.wav")); v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    v = np.pad(v[:NA], (0, max(0, NA - len(v))))
    e = np.sqrt(np.convolve(v ** 2, np.ones(4800) / 4800, "same")); e = np.clip(e / 0.04, 0, 1)
    k = np.ones(int(0.2 * SR)) / int(0.2 * SR); e = np.convolve(e, k, "same")
    mix = mus * (0.55 * (1 - 0.5 * e))[:, None] + fx * 0.8 + np.stack([v, v], 1) * 0.95
    fo = int(0.6 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
    mix = np.tanh(mix * 1.05); mix = mix / np.abs(mix).max() * 0.95
    o = wave.open(path, "wb"); o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR)
    o.writeframes((mix * 32767).astype(np.int16).tobytes()); o.close()


if __name__ == "__main__":
    tmpv = OUT + ".video.mp4"; tmpa = OUT + ".audio.wav"
    if os.environ.get("ONLY") != "video": build_audio(tmpa)
    if os.environ.get("ONLY") == "audio": sys.exit()
    render_video(tmpv)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmpv, "-i", tmpa, "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "256k", "-af", "loudnorm=I=-14:TP=-1.0", "-ar", "48000",
                    "-t", str(DUR), "-movflags", "+faststart", OUT], check=True)
    os.remove(tmpv); os.remove(tmpa)
    print("ok", OUT)
