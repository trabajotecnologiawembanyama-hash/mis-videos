"""Motor de animación 2D de Brote (Skia): personajes stickman articulados que se mueven dentro de la escena.
Estilo del canal en 2D: cabeza blanca redonda, ojos de punto, cejas expresivas, ropa de colores lisos,
brazos y piernas de palito negro. Fondos ilustrados con luz cálida y profundidad (capas)."""
import math, random
import numpy as np
import skia

W, H, FPS = 1080, 1920, 30
FONT_DIR = "/usr/share/fonts/opentype/inter/"
_tf = {}


def typeface(name):
    if name not in _tf: _tf[name] = skia.Typeface.MakeFromFile(FONT_DIR + name + ".otf")
    return _tf[name]


def C(rgb, a=1.0):
    return skia.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]), int(255 * max(0, min(1, a))))


def fill(rgb, a=1.0, blur=0):
    p = skia.Paint(Color=C(rgb, a), AntiAlias=True)
    if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def stroke(rgb, w, a=1.0, cap=True):
    p = skia.Paint(Color=C(rgb, a), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w)
    if cap:
        p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def lin(p0, p1, cols, pos=None):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)], [C(c) if len(c) == 3 else C(c[:3], c[3]) for c in cols], pos))
    return p


def rad(c, r, cols, pos=None):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial(skia.Point(*c), r, [C(c_) if len(c_) == 3 else C(c_[:3], c_[3]) for c_ in cols], pos))
    return p


def rrect(cv, x, y, w, h, r, paint):
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r), paint)


def path(points, close=True):
    p = skia.Path(); p.moveTo(*points[0])
    for q in points[1:]: p.lineTo(*q)
    if close: p.close()
    return p


def lerp(a, b, t): return a + (b - a) * t
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_in(x): x = clamp(x); return x ** 3


# ============================================================ personajes
# Ropa/aspecto fijo (tabla de personajes del plan)
PEDRITO = dict(hair="curly", shirt=(196, 38, 32), shirt2=(150, 24, 22), pants=(28, 34, 62), shoe=(38, 52, 90), tape=True, h=1.0)
PEDRITO_NUEVAS = dict(PEDRITO, tape=False, shoe=(205, 45, 40), shoe_stripe=(245, 245, 240), socks=True, big_shoes=True)
LUCHO = dict(hair="gray", cap=(52, 78, 112), shirt=(62, 92, 128), shirt2=(46, 70, 100), pants=(62, 92, 128), shoe=(60, 40, 28),
             moustache=(170, 170, 168), h=1.32, belly=1.15)
MAMA = dict(hair="bun", hair_col=(60, 34, 20), shirt=(46, 120, 140), shirt2=(34, 92, 110), pants=(46, 120, 140), skirt=True, shoe=(70, 50, 40), h=1.28)
COACH = dict(cap=(26, 50, 120), shirt=(30, 58, 135), shirt2=(22, 44, 104), pants=(30, 58, 135), shoe=(240, 240, 240), whistle=True, h=1.36, hair="short", hair_col=(40, 28, 20))
TOMAS = dict(hair="spiky", hair_col=(120, 74, 30), shirt=(245, 196, 40), shirt2=(210, 160, 20), pants=(30, 30, 36), shoe=(250, 250, 255), shiny=True, h=1.18)
KIDS = [dict(hair="short", hair_col=(60, 36, 20), shirt=(40, 120, 220), shirt2=(28, 90, 170), pants=(235, 235, 240), shoe=(255, 255, 255), shiny=True, h=1.02),
        dict(hair="pony", hair_col=(120, 60, 20), shirt=(240, 200, 40), shirt2=(200, 160, 20), pants=(30, 30, 40), shoe=(40, 220, 120), shiny=True, h=0.98),
        dict(hair="short", hair_col=(20, 20, 20), shirt=(60, 180, 100), shirt2=(40, 140, 76), pants=(40, 40, 110), shoe=(255, 110, 40), shiny=True, h=1.05),
        dict(hair="pony", hair_col=(20, 14, 10), shirt=(240, 110, 150), shirt2=(200, 80, 120), pants=(30, 40, 90), shoe=(80, 160, 255), shiny=True, h=0.97),
        dict(hair="short", hair_col=(150, 96, 40), shirt=(150, 70, 200), shirt2=(116, 50, 160), pants=(30, 30, 30), shoe=(255, 255, 255), shiny=True, h=1.0)]
NEIGHBORS = [dict(hair=h_, hair_col=hc, shirt=sc, shirt2=tuple(int(v * 0.8) for v in sc), pants=pc, shoe=(60, 60, 60), h=hh)
             for h_, hc, sc, pc, hh in [("short", (40, 30, 20), (200, 90, 60), (60, 60, 80), 1.3), ("bun", (90, 50, 20), (90, 160, 120), (60, 50, 50), 1.25),
                                        ("gray", (150, 150, 150), (160, 140, 100), (70, 70, 70), 1.3), ("pony", (30, 20, 15), (230, 120, 170), (40, 40, 80), 1.2),
                                        ("short", (20, 20, 20), (80, 110, 200), (40, 40, 40), 1.35), ("curly", (30, 20, 10), (240, 180, 60), (50, 50, 60), 1.0),
                                        ("short", (110, 70, 30), (120, 200, 220), (60, 40, 30), 1.28), ("bun", (180, 180, 180), (190, 80, 90), (60, 60, 80), 1.22)]]

CAMILA = dict(hair="braids", hair_col=(70, 40, 24), glasses=(30, 30, 34), shirt=(250, 250, 245), shirt2=(225, 225, 220), pants=(52, 70, 120),
              apron=(255, 200, 61), stains=True, shoe=(200, 60, 60), h=1.0)
CAMILA_PIJAMA = dict(hair="braids", hair_col=(70, 40, 24), glasses=(30, 30, 34), shirt=(150, 190, 235), shirt2=(120, 160, 210), pants=(150, 190, 235),
                     shoe=(240, 220, 200), h=1.0)
ROSA = dict(hair="bun", hair_col=(240, 240, 238), shirt=(170, 120, 190), shirt2=(140, 96, 160), pants=(110, 80, 130), skirt=True,
            apron=(245, 235, 220), shoe=(90, 70, 60), h=1.26)
JUEZ = dict(hair="short", hair_col=(60, 60, 64), glasses=(20, 20, 20), shirt=(60, 70, 90), shirt2=(44, 52, 70), pants=(40, 44, 56), shoe=(30, 30, 30), h=1.34)
JUEZA = dict(hair="bun", hair_col=(90, 50, 30), shirt=(180, 60, 70), shirt2=(140, 44, 54), pants=(60, 50, 60), skirt=True, shoe=(40, 30, 30), h=1.28)
MATEO = dict(hair="short", hair_col=(42, 28, 18), shirt=(52, 168, 88), shirt2=(36, 130, 66), pants=(48, 62, 98), shoe=(236, 236, 236),
             sole=(250, 250, 250), backpack=(140, 144, 152), h=1.08)
ABUELA = dict(hair="bun", hair_col=(238, 238, 234), glasses=(70, 50, 40), shirt=(60, 74, 128), shirt2=(46, 58, 104), pants=(60, 74, 128),
              skirt=True, apron=(250, 248, 242), shoe=(96, 70, 54), h=1.22)
BARROS = dict(hair="gray", glasses=(24, 24, 28), shirt=(84, 88, 100), shirt2=(64, 68, 80), pants=(70, 74, 86), shoe=(26, 24, 24),
              tie=(170, 40, 46), h=1.4)
TIO_LUCHO = dict(cap=(176, 44, 44), hair="short", hair_col=(44, 32, 22), moustache=(44, 32, 22), shirt=(156, 104, 62), shirt2=(126, 82, 48),
                 pants=(62, 62, 72), shoe=(70, 50, 40), belly=1.3, h=1.3)
VALE = dict(hair="pony", hair_col=(28, 18, 14), shirt=(150, 84, 206), shirt2=(120, 62, 170), pants=(40, 44, 64), shoe=(250, 250, 250), h=1.02)
BLACK = (18, 18, 20)
ZERO = dict(lean=0, head=0, ab=(8, -4), af=(-6, -4), lb=(4, 0), lf=(-4, 0), air=0, seat=None, look=(0.6, 0), blink=0, mood="neutral",
            tears=0, squash=1.0, body_rot=0)


def pose(**kw):
    p = dict(ZERO); p.update(kw); return p


def mix(p1, p2, t):
    out = {}
    for k in p1:
        a, b = p1[k], p2.get(k, p1[k])
        if isinstance(a, tuple): out[k] = tuple(lerp(x, y, t) for x, y in zip(a, b))
        elif isinstance(a, (int, float)) and isinstance(b, (int, float)): out[k] = lerp(a, b, t)
        elif a is None or b is None: out[k] = a if t < 0.5 else b
        else: out[k] = a if t < 0.5 else b
    return out


def keys(t, frames):
    """frames = [(t, pose), ...] -> pose interpolada con suavizado."""
    if t <= frames[0][0]: return frames[0][1]
    for (t0, p0), (t1, p1) in zip(frames, frames[1:]):
        if t0 <= t <= t1: return mix(p0, p1, ease((t - t0) / max(1e-6, t1 - t0)))
    return frames[-1][1]


# ---- poses base
STAND = pose()
HOLD = pose(ab=(30, 75), af=(22, 85))
CROSS = pose(ab=(25, 115), af=(15, 125), mood="neutral")
ARMS_UP = pose(ab=(165, 0), af=(150, 10), head=-10)
CHEER = pose(ab=(150, 15), af=(165, -10), head=-8, mood="happy")
SAD_STAND = pose(lean=8, head=18, ab=(4, 0), af=(-2, 0), mood="sad", look=(0.3, 0.6))
SIT_GROUND = pose(seat=0.07, lb=(115, -95), lf=(110, -90), ab=(70, 40), af=(60, 50), lean=14, head=12, mood="sad")
SIT_BENCH = pose(seat=0.25, lb=(88, -88), lf=(84, -84), ab=(20, 40), af=(15, 45))
CROUCH = pose(lb=(60, -100), lf=(50, -95), lean=16, ab=(35, 80), af=(30, 85), head=-6)
SHOOT_UP = pose(lb=(4, -6), lf=(-4, -4), ab=(155, 15), af=(165, 5), head=-14, air=0.0, mood="determined")
FALL_POSE = pose(seat=0.04, lean=-55, lb=(95, -10), lf=(75, -15), ab=(-70, 20), af=(110, 30), head=12, mood="surprised")
POINT = pose(af=(95, 0), ab=(6, 0), head=-4)
CLAP_OPEN = pose(ab=(55, 50), af=(65, 30), mood="happy")
CLAP_SHUT = pose(ab=(50, 85), af=(55, 80), mood="happy")
WHISTLE = pose(af=(25, 150), ab=(6, 0))
HUG = pose(ab=(80, 60), af=(85, 55), head=8, mood="happy")


def walk(phase, speed=1.0, base=None, amp=1.0):
    s = math.sin(phase * 2 * math.pi); c = math.cos(phase * 2 * math.pi)
    p = dict(base or STAND)
    p.update(lb=(-26 * s * amp, -max(0, 40 * c) * amp), lf=(26 * s * amp, -max(0, -40 * c) * amp),
             lean=4 * amp + p.get("lean", 0) * 0.5)
    if not base or base is STAND:
        p.update(ab=(22 * s * amp, 18), af=(-22 * s * amp, 18))
    return p


def run(phase, amp=1.0, arms=True):
    s = math.sin(phase * 2 * math.pi); c = math.cos(phase * 2 * math.pi)
    p = dict(STAND)
    p.update(lb=(-45 * s * amp, -(20 + max(0, 70 * c) * amp)), lf=(45 * s * amp, -(20 + max(0, -70 * c) * amp)), lean=14 * amp,
             air=0.03 * abs(s) * amp, head=-4, mood="determined")
    if arms: p.update(ab=(40 * s * amp, 75), af=(-40 * s * amp, 75))
    return p


def breathe(p, t):
    p = dict(p); p["lean"] = p.get("lean", 0) + 1.2 * math.sin(t * 2.2)
    return p


def blink_at(t, seed=0):
    rnd = random.Random(seed); bt = rnd.uniform(0.5, 2.5)
    while bt < t + 1:
        if 0 <= t - bt < 0.14: return math.sin(math.pi * (t - bt) / 0.14)
        bt += rnd.uniform(2.2, 4.0)
    return 0.0


BROWS = {"neutral": (0, 0), "sad": (-24, 0.04), "determined": (22, -0.03), "surprised": (-6, 0.12), "happy": (-10, 0.06),
         "worried": (-30, 0.06), "focused": (14, -0.02), "kind": (-16, 0.05), "angry": (30, -0.05), "smug": (16, 0.02)}


def _dir(a, face):
    r = math.radians(a)
    return (math.sin(r) * face, math.cos(r))


def draw_char(cv, spec, p, x, y, S, face=1, t=0.0, extras=None):
    """Dibuja un personaje con los pies en (x, y). S = altura de referencia en px (niño ≈ S)."""
    ex = extras or {}
    S = S * spec.get("h", 1.0)
    u = S
    L1, L2 = 0.125 * u, 0.125 * u
    A1, A2 = 0.11 * u, 0.105 * u
    torso = 0.2 * u
    hr = 0.125 * u / (spec.get("h", 1.0) ** 0.35)          # adultos: cabeza proporcionalmente menor
    lw = max(3.0, 0.017 * u)
    big = spec.get("big_shoes")

    def leg_vec(a1, a2):
        d1 = _dir(a1, face); d2 = _dir(a1 + a2, face)
        return d1, d2

    # altura de cadera: el pie más bajo toca el suelo (o asiento)
    drops = []
    for key in ("lb", "lf"):
        a1, a2 = p[key]; d1, d2 = leg_vec(a1, a2)
        drops.append(d1[1] * L1 + d2[1] * L2)
    if p.get("seat") is not None:
        hip = (x, y - p["seat"] * u)
    else:
        hip = (x, y - max(drops) - p.get("air", 0) * u)
    lean = p.get("lean", 0)
    up = _dir(180 - lean, face)
    neck = (hip[0] + up[0] * torso, hip[1] + up[1] * torso)
    perp = (-up[1] * face, up[0] * face)

    def limb(origin, a1, a2, l1, l2):
        d1 = _dir(a1, face); d2 = _dir(a1 + a2, face)
        j = (origin[0] + d1[0] * l1, origin[1] + d1[1] * l1)
        e = (j[0] + d2[0] * l2, j[1] + d2[1] * l2)
        return j, e, d2

    sh_b = (neck[0] - up[0] * 0.02 * u - face * 0.012 * u, neck[1] - up[1] * 0.02 * u)
    sh_f = (neck[0] - up[0] * 0.02 * u + face * 0.012 * u, neck[1] - up[1] * 0.02 * u)
    hip_b = (hip[0] - face * 0.02 * u, hip[1]); hip_f = (hip[0] + face * 0.02 * u, hip[1])
    kb, fb, fdb = limb(hip_b, *p["lb"], L1, L2)
    kf, ff, fdf = limb(hip_f, *p["lf"], L1, L2)
    eb, hb, _ = limb(sh_b, *p["ab"], A1, A2)
    ef, hf, _ = limb(sh_f, *p["af"], A1, A2)
    blk = stroke(BLACK, lw)
    shirt = spec["shirt"]; shirt2 = spec.get("shirt2", shirt)

    def shoe(foot, fd, back):
        sc = spec.get("shoe", (90, 90, 90)); k = 1.35 if big else 1.0
        sw, sh_ = 0.075 * u * k, 0.04 * u * k
        cv.save(); cv.translate(foot[0], foot[1])
        cv.scale(face, 1)
        if spec.get("socks"):
            cv.drawLine(0, -0.03 * u, 0, -0.005 * u, stroke((245, 245, 240), lw * 2.4, cap=False))
        col = tuple(int(v * (0.82 if back else 1)) for v in sc)
        rrect(cv, -sw * 0.35, -sh_ * 0.75, sw, sh_, sh_ * 0.5, fill(col))
        rrect(cv, -sw * 0.36, sh_ * 0.05, sw * 1.02, sh_ * 0.28, sh_ * 0.14, fill((235, 232, 225) if not spec.get("tape") else (190, 185, 175)))
        if spec.get("shiny"):
            cv.drawLine(-sw * 0.1, -sh_ * 0.55, sw * 0.35, -sh_ * 0.55, stroke((255, 255, 255), lw * 0.5, 0.8))
        if spec.get("shoe_stripe"):
            cv.drawLine(-sw * 0.15, -sh_ * 0.1, sw * 0.4, -sh_ * 0.5, stroke(spec["shoe_stripe"], lw * 0.6))
        if spec.get("tape"):
            for tx in (0.05, 0.3):
                rrect(cv, sw * tx - sw * 0.06, -sh_ * 0.82, sw * 0.12, sh_ * 1.1, 2, fill((176, 178, 182)))
                cv.drawLine(sw * tx - sw * 0.03, -sh_ * 0.7, sw * tx - sw * 0.03, sh_ * 0.2, stroke((220, 222, 226), 1.5))
            if ex.get("sole_flap") and not back:
                cv.save(); cv.translate(sw * 0.6, sh_ * 0.2); cv.rotate(ex["sole_flap"])
                rrect(cv, -sw * 0.5, 0, sw * 0.5, sh_ * 0.28, 3, fill((190, 185, 175))); cv.restore()
        cv.restore()

    # ---- capa trasera
    cv.drawPath(path([hip_b, kb, fb], False), blk)
    shoe(fb, fdb, True)
    cv.drawPath(path([sh_b, eb, hb], False), blk)
    cv.drawCircle(hb[0], hb[1], lw * 1.25, fill(BLACK))
    if ex.get("back_hand_item"): ex["back_hand_item"](cv, hb)
    # ---- torso (ropa)
    cv.save(); cv.translate(*hip)
    cv.rotate(lean * face)
    tw = 0.12 * u * spec.get("belly", 1.0); th = torso * 1.02
    if spec.get("backpack"):
        bc = spec["backpack"]
        rrect(cv, -face * tw * 0.5 - face * 0.05 * u - 0.05 * u, -th * 0.95, 0.1 * u, th * 0.78, 0.03 * u, lin((0, -th), (0, 0), [bc, tuple(int(v * 0.75) for v in bc)]))
        rrect(cv, -face * tw * 0.5 - face * 0.085 * u - 0.025 * u, -th * 0.55, 0.05 * u, th * 0.28, 0.015 * u, fill(tuple(int(v * 0.85) for v in bc)))
    if spec.get("skirt"):
        cv.drawPath(path([(-tw * 0.5, -0.02 * u), (tw * 0.5, -0.02 * u), (tw * 0.75, 0.09 * u), (-tw * 0.75, 0.09 * u)]), fill(spec["pants"]))
    else:
        rrect(cv, -tw * 0.5, -0.03 * u, tw, 0.07 * u, 0.02 * u, fill(spec["pants"]))
    shirt_p = lin((0, -th), (0, 0), [shirt, shirt2])
    rrect(cv, -tw / 2, -th - 0.005 * u, tw, th * 0.98, 0.035 * u, shirt_p)
    cv.drawLine(-tw * 0.18, -th * 0.92, tw * 0.18, -th * 0.92, stroke(shirt2, lw * 0.5, 0.8))
    if spec.get("backpack"):
        sc_ = tuple(int(v * 0.7) for v in spec["backpack"])
        cv.drawLine(-tw * 0.22 * face, -th * 0.97, tw * 0.05 * face, -th * 0.35, stroke(sc_, lw * 0.75))
    if spec.get("tie"):
        tc_ = spec["tie"]
        cv.drawPath(path([(-tw * 0.12, -th * 0.98), (tw * 0.12, -th * 0.98), (tw * 0.05, -th * 0.88), (tw * 0.1, -th * 0.4), (0, -th * 0.3), (-tw * 0.1, -th * 0.4), (-tw * 0.05, -th * 0.88)]), fill(tc_))
        cv.drawPath(path([(-tw * 0.32, -th * 1.0), (-tw * 0.1, -th * 0.98), (-tw * 0.2, -th * 0.7)]), fill((245, 245, 245)))
        cv.drawPath(path([(tw * 0.32, -th * 1.0), (tw * 0.1, -th * 0.98), (tw * 0.2, -th * 0.7)]), fill((245, 245, 245)))
    if spec.get("apron"):
        ac = spec["apron"]
        cv.drawLine(-tw * 0.22, -th * 0.95, -tw * 0.3, -th * 0.68, stroke(ac, lw * 0.55)); cv.drawLine(tw * 0.22, -th * 0.95, tw * 0.3, -th * 0.68, stroke(ac, lw * 0.55))
        rrect(cv, -tw * 0.44, -th * 0.72, tw * 0.88, th * 0.72 + 0.085 * u, 0.02 * u, lin((0, -th), (0, 0.08 * u), [ac, tuple(int(v * 0.86) for v in ac)]))
        rrect(cv, -tw * 0.2, -th * 0.3, tw * 0.4, th * 0.2, 0.008 * u, stroke(tuple(int(v * 0.75) for v in ac), lw * 0.3))
        if spec.get("stains"):
            for (sx_, sy_, sr_) in ((-0.22, -0.5, 0.02), (0.18, -0.15, 0.026), (-0.05, 0.12, 0.018), (0.25, -0.55, 0.012)):
                cv.drawCircle(tw * sx_, th * sy_, u * sr_, fill((60, 44, 30), 0.75))
    if spec.get("number"):
        f = skia.Font(typeface("Inter-Black"), 0.06 * u)
        cv.drawString(spec["number"], -f.measureText(spec["number"]) / 2, -th * 0.42, f, fill((255, 255, 255)))
    cv.restore()
    if spec.get("whistle"):
        wx, wy = neck[0] + face * 0.02 * u, neck[1] + 0.06 * u
        cv.drawLine(neck[0] - 0.02 * u, neck[1] + 0.005 * u, wx, wy, stroke((230, 230, 230), 1.5))
        cv.drawCircle(wx, wy, 0.012 * u, fill((200, 200, 205)))
    # ---- capa delantera: pierna
    cv.drawPath(path([hip_f, kf, ff], False), blk)
    shoe(ff, fdf, False)
    # ---- cabeza
    hc = (neck[0] + up[0] * (hr * 0.95) - p.get("head", 0) * face * 0.002 * u, neck[1] + up[1] * (hr * 0.95))
    cv.drawLine(neck[0], neck[1], neck[0] + up[0] * 0.03 * u, neck[1] + up[1] * 0.03 * u, stroke(BLACK, lw))
    cv.save(); cv.translate(*hc); cv.rotate((lean * 0.4 + p.get("head", 0)) * face)
    hair = spec.get("hair")
    hcol = spec.get("hair_col", (22, 18, 16))
    if hair == "pony":
        cv.drawPath(path([(-face * hr * 0.6, -hr * 0.3), (-face * hr * 1.35, hr * 0.25), (-face * hr * 1.1, hr * 0.55), (-face * hr * 0.7, hr * 0.2)]), fill(hcol))
    if hair == "bun":
        cv.drawCircle(-face * hr * 0.55, -hr * 0.85, hr * 0.38, fill(hcol))
    if hair == "braids":
        for sx in (-1, 1):
            sway = math.sin(t * 3 + sx) * hr * 0.05
            for k in range(5):
                cv.drawCircle(sx * hr * (0.98 + 0.03 * k) - face * hr * 0.12 + sway * k * 0.4, hr * (0.25 + 0.3 * k), hr * (0.2 - 0.012 * k), fill(hcol))
            cv.drawCircle(sx * hr * 1.1 - face * hr * 0.12 + sway * 2, hr * 1.72, hr * 0.12, fill(spec.get("ribbon", (230, 70, 80))))
    cv.drawCircle(0, 0, hr, rad((-hr * 0.35, -hr * 0.4), hr * 1.5, [(255, 255, 252), (240, 238, 232), (205, 202, 196)], [0, 0.55, 1]))
    cv.drawCircle(0, 0, hr, stroke((30, 30, 30), max(1.5, lw * 0.18), 0.35))
    if hair == "curly":
        rnd = random.Random(7)
        for k in range(26):
            a = rnd.uniform(-2.7, 0.0) if face > 0 else rnd.uniform(-math.pi + 0.0, -0.45)
            a = rnd.uniform(math.pi * 1.05, math.pi * 2.0)
            rr = hr * rnd.uniform(0.82, 1.02)
            cx_, cy_ = math.cos(a) * rr, math.sin(a) * rr * 0.95
            if face * cx_ > hr * 0.55 and cy_ > -hr * 0.55: continue
            cv.drawCircle(cx_ - face * hr * 0.08, cy_ - hr * 0.08, hr * rnd.uniform(0.2, 0.27), fill((26, 20, 16)))
            cv.drawCircle(cx_ - face * hr * 0.08 - hr * 0.05, cy_ - hr * 0.13, hr * 0.06, fill((70, 60, 54), 0.5))
    elif hair in ("short", "pony", "bun", "spiky", "braids"):
        pth = skia.Path(); pth.addArc(skia.Rect.MakeXYWH(-hr * 1.03, -hr * 1.05, hr * 2.06, hr * 2.06), 180 + (20 if face > 0 else 0), 160)
        pth.close(); cv.drawPath(pth, fill(hcol))
        if hair == "spiky":
            for k in range(5):
                a = math.radians(200 + k * 30)
                cv.drawPath(path([(math.cos(a) * hr * 0.8, math.sin(a) * hr * 0.8), (math.cos(a + 0.2) * hr * 1.35, math.sin(a + 0.2) * hr * 1.35),
                                  (math.cos(a + 0.4) * hr * 0.8, math.sin(a + 0.4) * hr * 0.8)]), fill(hcol))
    elif hair == "gray":
        for sx in (-1, 1):
            cv.drawCircle(sx * hr * 0.82 - face * hr * 0.1, hr * 0.05, hr * 0.28, fill((175, 175, 172)))
    if spec.get("cap"):
        pth = skia.Path(); pth.addArc(skia.Rect.MakeXYWH(-hr * 1.04, -hr * 1.08, hr * 2.08, hr * 2.0), 180, 180); pth.close()
        cv.drawPath(pth, fill(spec["cap"]))
        rrect(cv, (0 if face > 0 else -hr * 1.45), -hr * 0.12, hr * 1.45, hr * 0.16, hr * 0.08, fill(tuple(int(v * 0.8) for v in spec["cap"])))
    # cara
    look = p.get("look", (0.6, 0)); bl = max(p.get("blink", 0), ex.get("blink", 0))
    ecx = face * hr * 0.28 + look[0] * face * hr * 0.12
    for k, sx in enumerate((-1, 1)):
        exx = ecx + sx * hr * 0.3 * (0.85 if sx * face < 0 else 1.0)
        eyy = -hr * 0.02 + look[1] * hr * 0.1
        ew, eh = hr * 0.11, hr * 0.15 * max(0.08, 1 - bl)
        cv.drawOval(skia.Rect.MakeXYWH(exx - ew, eyy - eh, ew * 2, eh * 2), fill((12, 12, 14)))
        if bl < 0.5:
            cv.drawCircle(exx + hr * 0.035, eyy - hr * 0.06, hr * 0.035, fill((255, 255, 255)))
        if spec.get("glasses"):
            cv.drawCircle(exx, eyy, hr * 0.23, fill((190, 225, 255), 0.22))
            cv.drawCircle(exx, eyy, hr * 0.23, stroke(spec["glasses"], max(2.0, hr * 0.055)))
            if sx == 1: cv.drawLine(exx - hr * 0.23, eyy, exx - hr * 0.6 * (0.85 if face < 0 else 1.0) * 0 - hr * 0.37, eyy, stroke(spec["glasses"], max(2.0, hr * 0.05)))
        # cejas
        ang, dy = BROWS.get(p.get("mood", "neutral"), (0, 0))
        a = math.radians(ang) * (-sx)
        bx, by = exx, eyy - hr * 0.3 - dy * hr
        dx_, dy_ = math.cos(a) * hr * 0.17, math.sin(a) * hr * 0.17
        cv.drawLine(bx - dx_, by - dy_, bx + dx_, by + dy_, stroke((14, 14, 14), max(2.5, hr * 0.075)))
        if p.get("tears", 0) > 0:
            ty = eyy + hr * 0.18 + (t * 0.6 % 1.0) * hr * 0.5 * p["tears"]
            cv.drawOval(skia.Rect.MakeXYWH(exx - hr * 0.035, ty - hr * 0.05, hr * 0.07, hr * 0.1), fill((120, 190, 255), 0.85))
    if spec.get("moustache"):
        for sx in (-1, 1):
            cv.drawOval(skia.Rect.MakeXYWH(ecx + sx * hr * 0.16 - hr * 0.2, hr * 0.2, hr * 0.4, hr * 0.17), fill(spec["moustache"]))
    if ex.get("blush"):
        for sx in (-1, 1):
            cv.drawCircle(ecx + sx * hr * 0.42, hr * 0.25, hr * 0.1, fill((255, 120, 120), 0.35))
    cv.restore()
    # ---- brazo delantero
    cv.drawPath(path([sh_f, ef, hf], False), blk)
    cv.drawCircle(hf[0], hf[1], lw * 1.25, fill(BLACK))
    if ex.get("hand_item"): ex["hand_item"](cv, hf)
    return dict(hip=hip, neck=neck, head=hc, hr=hr, hand_f=hf, hand_b=hb, foot_f=ff, foot_b=fb, u=u)


def shadow(cv, x, y, w, a=0.25):
    cv.drawOval(skia.Rect.MakeXYWH(x - w / 2, y - w * 0.08, w, w * 0.16), fill((0, 0, 0), a, blur=w * 0.06))


def ball(cv, x, y, r, spin=0.0):
    cv.drawCircle(x, y, r, rad((x - r * 0.35, y - r * 0.4), r * 1.5, [(250, 150, 60), (228, 102, 28), (160, 60, 14)], [0, 0.6, 1]))
    cv.save(); cv.translate(x, y); cv.rotate(math.degrees(spin))
    st = stroke((40, 20, 10), max(1.5, r * 0.07))
    cv.drawLine(-r, 0, r, 0, st); cv.drawLine(0, -r, 0, r, st)
    cv.drawArc(skia.Rect.MakeXYWH(-r * 1.6, -r, r * 1.2, r * 2), -60, 120, False, st)
    cv.drawArc(skia.Rect.MakeXYWH(r * 0.4, -r, r * 1.2, r * 2), 120, 120, False, st)
    cv.restore()


def broom(cv, hand, ang=10, L=260):
    a = math.radians(ang)
    top = (hand[0] - math.sin(a) * L * 0.25, hand[1] - math.cos(a) * L * 0.25)
    bot = (hand[0] + math.sin(a) * L * 0.75, hand[1] + math.cos(a) * L * 0.75)
    cv.drawLine(*top, *bot, stroke((150, 100, 50), L * 0.035))
    cv.save(); cv.translate(*bot); cv.rotate(-ang)
    cv.drawPath(path([(-L * 0.12, 0), (L * 0.12, 0), (L * 0.16, L * 0.16), (-L * 0.16, L * 0.16)]), fill((210, 170, 90)))
    for k in range(-6, 7):
        cv.drawLine(k * L * 0.022, L * 0.02, k * L * 0.026, L * 0.16, stroke((170, 130, 60), 1.5))
    cv.restore()


# ============================================================ texto
def text_center(cv, s, cx, cy, size, col=(255, 255, 255), outline=(0, 0, 0), ow=0.09, font="Inter-Black", a=1.0, scale=1.0, shadow_=True):
    f = skia.Font(typeface(font), size * scale)
    w = f.measureText(s)
    x = cx - w / 2; y = cy + size * scale * 0.36
    if shadow_:
        cv.drawString(s, x, y + size * 0.06, f, fill((0, 0, 0), 0.45 * a, blur=size * 0.06))
    if outline:
        p = stroke(outline, size * scale * ow * 2, a); cv.drawString(s, x, y, f, p)
    cv.drawString(s, x, y, f, fill(col, a))


# ============================================================ salida
class Writer:
    def __init__(self, path):
        import subprocess
        self.p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                                   "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                                   "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
        self.surf = skia.Surface(W, H)

    def canvas(self):
        return self.surf.getCanvas()

    def push(self):
        img = self.surf.makeImageSnapshot()
        self.p.stdin.write(img.toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())

    def close(self):
        self.p.stdin.close(); self.p.wait()
