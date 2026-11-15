"""Render final: escenas + gradación + títulos + subtítulos -> segmentos MP4 en paralelo."""
import json, math, os, subprocess, sys, unicodedata
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from base import W, H, FPS, NFRAMES, font, grade, clamp01, ease_in_out, text_layer, blur, to_img
import escenas as E

BUILD = os.environ.get("BUILD", "/tmp/claude-0/build")
SUBS = json.load(open(f"{BUILD}/subs.json"))
E.set_key_times(SUBS)

KEYWORDS = {"24", "HORAS", "HUMANIDAD", "EXISTIR", "INTELIGENCIA", "ARTIFICIAL", "ÚLTIMA", "MISIÓN", "IMPORTANTE",
            "GUERRAS", "ERRORES", "LOGROS", "SUEÑOS", "ALGORITMO", "MEDIR", "PERFECTOS", "AMÁNDONOS", "ÚLTIMO",
            "MENSAJE", "UNIVERSO", "TERMINARA", "NOSOTROS", "ESPECIALES"}
SUB_Y = 1400


def norm(w):
    return w.upper().strip(".,…¿?¡!")


def build_chunks():
    chunks = []
    for ln in SUBS:
        cur = []
        if len(ln["text"]) <= 28:
            chunks.append(list(ln["words"])); continue
        for w in ln["words"]:
            cur.append(w)
            txt = " ".join(x["w"] for x in cur)
            end_punct = w["w"][-1] in ",.?…"
            if len(cur) >= 3 or len(txt) >= 15 or end_punct:
                chunks.append(cur); cur = []
        if cur:
            if len(cur) == 1 and chunks and chunks[-1][0] in ln["words"] and len(" ".join(x["w"] for x in chunks[-1])) < 14:
                chunks[-1] = chunks[-1] + cur
            else:
                chunks.append(cur)
    out = []
    for i, c in enumerate(chunks):
        t0 = c[0]["t0"] - 0.06
        t1 = c[-1]["t1"] + 0.25
        if i + 1 < len(chunks):
            t1 = min(max(t1, chunks[i + 1][0]["t0"] - 0.06) if chunks[i + 1][0]["t0"] - c[-1]["t1"] < 0.45 else t1,
                     chunks[i + 1][0]["t0"] - 0.06)
        out.append(dict(words=c, t0=t0, t1=t1))
    return out


CHUNKS = build_chunks()
_sub_cache = {}


def render_chunk(i):
    if i in _sub_cache: return _sub_cache[i]
    c = CHUNKS[i]
    f = font("Inter-Black", 74)
    words = [w["w"].upper() for w in c["words"]]
    space = f.getlength(" ")
    widths = [f.getlength(w) for w in words]
    total = sum(widths) + space * (len(words) - 1)
    lines = [list(range(len(words)))]
    if total > W - 140:   # partir en dos líneas
        best = None
        for k in range(1, len(words)):
            a = sum(widths[:k]) + space * (k - 1); b = sum(widths[k:]) + space * (len(words) - k - 1)
            if best is None or max(a, b) < best[0]: best = (max(a, b), k)
        k = best[1]; lines = [list(range(k)), list(range(k, len(words)))]
    lh = 92
    img = Image.new("RGBA", (W, lh * len(lines) + 60), (0, 0, 0, 0))
    sh = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(img); ds = ImageDraw.Draw(sh)
    for li, ln in enumerate(lines):
        tw = sum(widths[j] for j in ln) + space * (len(ln) - 1)
        x = (W - tw) / 2; y = 30 + li * lh
        for j in ln:
            wd = words[j]
            key = norm(wd) in KEYWORDS
            col = (255, 178, 64, 255) if key else (255, 255, 255, 255)
            ds.text((x, y + 4), wd, font=f, fill=255, stroke_width=10)
            d.text((x, y), wd, font=f, fill=col, stroke_width=5, stroke_fill=(0, 0, 0, 230))
            x += widths[j] + space
    shadow = sh.filter(ImageFilter.GaussianBlur(10))
    base = Image.new("RGBA", img.size, (0, 0, 0, 0))
    base.putalpha(shadow.point(lambda v: int(v * 0.55)))
    base.alpha_composite(img)
    _sub_cache[i] = base
    return base


def draw_subs(frame_img, t):
    for i, c in enumerate(CHUNKS):
        if c["t0"] <= t < c["t1"]:
            im = render_chunk(i)
            age = t - c["t0"]
            s = 0.92 + 0.08 * ease_in_out(age / 0.12)
            a = min(1.0, age / 0.06) * min(1.0, (c["t1"] - t) / 0.06)
            if s != 1.0:
                im = im.resize((int(im.width * s), int(im.height * s)), Image.BILINEAR)
            if a < 1:
                al = im.getchannel("A").point(lambda v: int(v * a)); im = im.copy(); im.putalpha(al)
            frame_img.alpha_composite(im, (int((W - im.width) / 2), int(SUB_Y - im.height / 2)))
            break


_titles = {}


def title(key, lines, fname, size, tracking, cy):
    if key not in _titles:
        _titles[key] = text_layer(lines, font(fname, size), tracking=tracking, cy=cy)
    return _titles[key]


def overlay_titles(a, t):
    # Escena 1: gancho
    if t < 4.0:
        m = title("t1", ["MAÑANA LA HUMANIDAD", "DESAPARECERÁ"], "InterDisplay-Black", 70, 2, 330)
        alpha = min(1, (4.0 - t) / 0.35)
        glow = title("t1g", ["MAÑANA LA HUMANIDAD", "DESAPARECERÁ"], "InterDisplay-Black", 70, 2, 330)
        g = blur(glow, 16, 2)
        a = a * (1 - 0.85 * m[..., None] * alpha) + (m[..., None] * np.array([1, 1, 1.0]) + g[..., None] * np.array([1.0, 0.2, 0.12]) * 1.2) * alpha
    # Escena 7: ESTO FUIMOS.
    if 33.3 <= t < 36.0:
        m = title("t7", ["ESTO FUIMOS."], "InterDisplay-Light", 112, 14, 1080)
        alpha = ease_in_out((t - 33.3) / 0.8) * min(1, (36.0 - t) / 0.3)
        g = blur(m, 18, 2)
        a = a * (1 - 0.7 * m[..., None] * alpha) + (m[..., None] * 1.05 + g[..., None] * np.array([1.0, 0.75, 0.45]) * 0.8) * alpha
    # Escena 8: pregunta final (queda en pantalla para invitar a comentar)
    if t >= 36.4:
        m = title("t8", ["¿QUÉ MENSAJE", "DEJARÍAS TÚ?"], "InterDisplay-Regular", 76, 8, 880)
        alpha = ease_in_out((t - 36.4) / 1.3)
        a = a * (1 - m[..., None] * alpha) + m[..., None] * alpha * 0.98
    return a


def make_frame(f):
    t = f / FPS
    a, gp = E.render_scene(t, f)
    g = grade(a, f, **gp)
    g = overlay_titles(g, t)
    img = to_img(g).convert("RGBA")
    draw_subs(img, t)
    return img.convert("RGB")


def render_range(f0, f1, out):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(f0, f1):
        p.stdin.write(make_frame(f).tobytes())
        if f % 30 == 0: print(f"frame {f}", flush=True)
    p.stdin.close(); p.wait()


if __name__ == "__main__":
    if sys.argv[1] == "still":
        for s in sys.argv[3:]:
            f = int(round(float(s) * FPS))
            make_frame(f).save(f"{sys.argv[2]}/still_{float(s):05.2f}.png")
    else:
        f0, f1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        render_range(f0, f1, out)
