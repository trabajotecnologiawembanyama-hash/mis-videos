"""Semana 2 de Brote: Camila y el robot de chatarra (episodios 6 a 10). Usa los ayudantes de episodios.py."""
import math, random, sys
import skia
from motor import *
import motor as Mo
import escenarios as E
import escenarios_c as EC
from escenarios import Cam, cam_move, draw_bg, BW, BH, particles, paper

H_ = sys.modules["__main__"]
RX, GY = 760, 1930            # posición del robot en el patio
XYWH = skia.Rect.MakeXYWH


def A(s, n=0): return H_.at(s, n)
def stage(cv, cam, name): cv.save(); cam.apply(cv); draw_bg(cv, name)
def done(cv): cv.restore()
def ch(*a, **k): return H_.ch(*a, **k)
def shade(*a, **k): return H_.shade(*a, **k)
def walker(*a, **k): return H_.walker(*a, **k)


KNEEL = pose(seat=0.125, lb=(0, -90), lf=(12, -90), lean=12, ab=(40, 50), af=(50, 40), head=10)
HIPS = pose(ab=(-35, 110), af=(35, 100), mood="happy")


# ============================================================ utilería
def heart_path(hx, hy, hs):
    p = skia.Path()
    p.addCircle(hx - hs * 0.5, hy - hs * 0.3, hs * 0.56); p.addCircle(hx + hs * 0.5, hy - hs * 0.3, hs * 0.56)
    p.addPath(path([(hx - hs * 1.02, hy - hs * 0.08), (hx + hs * 1.02, hy - hs * 0.08), (hx, hy + hs * 1.05)]))
    return p


def robot(cv, x, y, S=600, eyes=0.0, eye_col=(110, 200, 255), arm=0.0, wave=0.0, step=None, heart=0.0, motor=False, wet=0.0,
          smoke=0.0, T=0.0, face=1, parts=5.0, shake=0.0, arm_b=0.0):
    """Robot de chatarra: pies y cuerpo de latas, colador por cabeza, tapas de botella por ojos."""
    u = S
    if shake: x += math.sin(T * 70) * shake
    bob = 0.0; lift_l = lift_r = 0.0; tilt = 0.0
    if step is not None:
        s = math.sin(step * 2 * math.pi)
        lift_l = max(0, s) * 0.05 * u; lift_r = max(0, -s) * 0.05 * u; bob = abs(s) * 0.012 * u; tilt = s * 3

    def pop(k): return ease_out(clamp(parts - (k - 1)))
    cv.save(); cv.translate(x, y - bob); cv.rotate(tilt)
    out = {}
    if pop(1) > 0:
        p1 = pop(1)
        for sx, lift in ((-1, lift_l), (1, lift_r)):
            fx = sx * 0.1 * u
            for k in range(6):
                yy = -0.07 * u - lift - k * 0.036 * u * p1
                rrect(cv, fx - 0.028 * u, yy - 0.034 * u, 0.056 * u, 0.03 * u, 0.01 * u, fill((130, 136, 148) if k % 2 else (166, 172, 184)))
            fx0 = fx - 0.075 * u + face * 0.015 * u
            rrect(cv, fx0, -0.07 * u - lift, 0.15 * u, 0.07 * u, 0.02 * u, lin((0, -0.07 * u - lift), (0, -lift), [(214, 92, 70), (160, 60, 46)]))
            cv.drawRect(XYWH(fx0 + 0.02 * u, -0.05 * u - lift, 0.11 * u, 0.012 * u), fill((250, 240, 220), 0.8))
    bw, bh = 0.36 * u, 0.38 * u
    if pop(2) > 0:
        cv.save(); cv.translate(0, -0.29 * u); cv.scale(pop(2), pop(2))
        rrect(cv, -bw / 2, -bh, bw, bh, 0.03 * u, lin((-bw / 2, 0), (bw / 2, 0), [(168, 174, 186), (216, 222, 232), (138, 144, 156)], [0, 0.35, 1]))
        for k in range(1, 5): cv.drawLine(-bw / 2 + 4, -bh * k / 5, bw / 2 - 4, -bh * k / 5, stroke((0, 0, 0), 2, 0.14))
        cv.drawRect(XYWH(-bw / 2, -bh * 0.86, bw, bh * 0.2), fill((204, 64, 52), 0.9)); cv.drawRect(XYWH(-bw / 2, -bh * 0.79, bw, bh * 0.045), fill((250, 240, 220), 0.9))
        rrect(cv, -bw / 2 - 3, -bh - 6, bw + 6, 0.03 * u, 0.01 * u, fill((120, 126, 138))); rrect(cv, -bw / 2 - 3, -0.02 * u, bw + 6, 0.03 * u, 0.01 * u, fill((120, 126, 138)))
        for (ox, oy, orr) in ((-0.1, -0.1, 0.03), (0.12, -0.2, 0.02), (0.06, -0.05, 0.022)): cv.drawCircle(ox * u, oy * u, orr * u, fill((170, 96, 50), 0.5))
        hx, hy, hs = 0, -bh * 0.36, 0.05 * u
        rrect(cv, hx - hs * 1.5, hy - hs * 1.3, hs * 3, hs * 2.9, hs * 0.3, fill((70, 74, 84)))
        if motor:   # motor de la máquina de coser en el pecho
            cv.drawCircle(hx, hy, hs * 1.0, fill((196, 160, 70))); cv.drawCircle(hx, hy, hs * 0.5, fill((120, 90, 40)))
            cv.save(); cv.translate(hx, hy); cv.rotate(T * 400 * heart)
            for k in range(4): cv.drawLine(0, 0, hs * 0.95 * math.cos(k * 1.57), hs * 0.95 * math.sin(k * 1.57), stroke((90, 66, 30), 3))
            cv.restore()
        else:
            cv.drawPath(heart_path(hx, hy, hs), fill((24, 24, 30)))
            cv.drawPath(heart_path(hx, hy, hs), stroke((255, 120, 110), 3, 0.35 + 0.35 * math.sin(T * 3)))
        if heart > 0:
            cv.drawCircle(hx, hy, hs * 4, rad((hx, hy), hs * 4, [(255, 190, 90, 0.55 * heart), (255, 190, 90, 0.0)]))
        cv.restore()
    sh_y = -0.6 * u
    if pop(3) > 0:
        for sx, av, wv in ((-face, arm_b, 0.0), (face, arm, wave)):
            a = math.radians(14 + av * 150); a2 = a + math.radians(26 * math.sin(T * 10) * wv + (10 if av < 0.1 else 0))
            s0 = (sx * 0.2 * u, sh_y)
            e = (s0[0] + math.sin(a) * sx * 0.15 * u * pop(3), s0[1] + math.cos(a) * 0.15 * u * pop(3))
            h = (e[0] + math.sin(a2) * sx * 0.15 * u * pop(3), e[1] + math.cos(a2) * 0.15 * u * pop(3))
            cv.drawPath(path([s0, e, h], False), stroke((150, 156, 168), 0.05 * u))
            cv.drawPath(path([s0, e, h], False), stroke((200, 206, 216), 0.02 * u, 0.7))
            cv.drawCircle(e[0], e[1], 0.03 * u, fill((110, 116, 128))); cv.drawCircle(s0[0], s0[1], 0.036 * u, fill((110, 116, 128)))
            ang = math.degrees(math.atan2(h[1] - e[1], h[0] - e[0]))
            cv.drawArc(XYWH(h[0] - 0.04 * u, h[1] - 0.04 * u, 0.08 * u, 0.08 * u), ang - 120, 240, False, stroke((90, 96, 108), 0.022 * u))
            if sx == face: out["hand"] = (x + h[0], y - bob + h[1])
            else: out["hand_b"] = (x + h[0], y - bob + h[1])
    if pop(4) > 0:
        cv.save(); cv.translate(0, -0.7 * u); cv.scale(pop(4), pop(4))
        for k in range(3): cv.drawOval(XYWH(-0.04 * u, -0.012 * u + k * 0.012 * u, 0.08 * u, 0.016 * u), stroke((120, 126, 138), 3))
        dome = skia.Path(); dome.addArc(XYWH(-0.18 * u, -0.235 * u, 0.36 * u, 0.44 * u), 180, 180); dome.close()
        cv.drawPath(dome, lin((-0.18 * u, 0), (0.18 * u, 0), [(176, 182, 194), (226, 230, 238), (146, 152, 164)], [0, 0.4, 1]))
        rnd = random.Random(2)
        for r in range(3):
            for k in range(9 - r * 2):
                hx_ = (-0.14 + 0.035 * r + k * 0.035) * u; hy_ = (-0.2 + r * 0.0) * u - 0.0
                cv.drawCircle(hx_, -0.215 * u + (abs(hx_) / (0.18 * u)) ** 2 * 0.1 * u + r * 0.028 * u, 0.006 * u, fill((70, 74, 84)))
        rrect(cv, -0.21 * u, -0.03 * u, 0.42 * u, 0.034 * u, 0.012 * u, fill((120, 126, 138)))
        for sx in (-1, 1): cv.drawArc(XYWH(sx * 0.21 * u - 0.035 * u, -0.05 * u, 0.07 * u, 0.06 * u), 0, 360, False, stroke((120, 126, 138), 0.014 * u))
        if pop(5) > 0:
            for sx in (-1, 1):
                ex_, ey_ = sx * 0.075 * u + face * 0.02 * u, -0.095 * u; er = 0.046 * u * pop(5)
                for k in range(14): cv.drawCircle(ex_ + er * math.cos(k * 0.449), ey_ + er * math.sin(k * 0.449), er * 0.2, fill((96, 100, 112)))
                cv.drawCircle(ex_, ey_, er * 0.92, fill((60, 64, 74)))
                if eyes > 0:
                    cv.drawCircle(ex_, ey_, er * 3.2, rad((ex_, ey_), er * 3.2, [eye_col + (0.6 * eyes,), eye_col + (0.0,)]))
                    cv.drawCircle(ex_, ey_, er * 0.8, fill(eye_col, eyes)); cv.drawCircle(ex_ - er * 0.2, ey_ - er * 0.25, er * 0.25, fill((255, 255, 255), eyes))
                else:
                    cv.drawCircle(ex_, ey_, er * 0.5, stroke((96, 100, 112), 2))
            for k in range(5): cv.drawRect(XYWH((-0.05 + k * 0.022) * u + face * 0.02 * u, -0.052 * u, 0.012 * u, 0.012 * u), fill((70, 74, 84)))
            cv.drawPath(path([(0, -0.235 * u), (0.01 * u, -0.29 * u), (0.04 * u, -0.31 * u)], False), stroke((110, 116, 128), 0.012 * u))
            cv.drawCircle(0.04 * u, -0.31 * u, 0.018 * u, fill((230, 190, 80)))
        cv.restore()
    cv.restore()
    if smoke > 0:
        for k in range(9):
            age = (T * 0.5 + k / 9) % 1
            cv.drawCircle(x + math.sin(k * 2.3 + T) * 30 * age, y - 0.52 * u - age * 0.6 * u, (0.03 + 0.07 * age) * u, fill((70, 70, 78), smoke * (1 - age) * 0.7, blur=8))
    if wet > 0:
        rnd = random.Random(8)
        for k in range(12):
            dx = rnd.uniform(-0.2, 0.2) * u; y0 = y - rnd.uniform(0.3, 0.9) * u; ph = (T * rnd.uniform(0.8, 1.6) + rnd.random()) % 1
            cv.drawOval(XYWH(x + dx - 4, y0 + ph * 0.25 * u, 8, 14), fill((150, 200, 255), wet * (1 - ph)))
        cv.drawOval(XYWH(x - 0.34 * u, y - 0.02 * u, 0.68 * u, 0.07 * u), fill((110, 140, 210), 0.45 * wet))
    out["chest"] = (x, y - 0.29 * u - bh * 0.36); out["head"] = (x, y - 0.8 * u)
    return out


def sewing(cv, x, y, s=1.0, old=False, T=0.0, run=0.0, dust=1.0, face=1):
    body = (34, 34, 40) if old else (250, 250, 246); acc = (200, 170, 80) if old else (70, 170, 180)
    cv.save(); cv.translate(x, y); cv.scale(s * face, s)
    rrect(cv, -170, -30, 340, 30, 8, fill(body)); rrect(cv, 90, -200, 70, 175, 14, fill(body))
    rrect(cv, -150, -210, 310, 70, 24, fill(body)); rrect(cv, -160, -200, 70, 110, 12, fill(body))
    ny = 12 * math.sin(T * 40) * run
    cv.drawLine(-125, -92, -125, -50 + ny, stroke((190, 190, 196), 4)); cv.drawRect(XYWH(-146, -42, 42, 8), fill((150, 150, 156)))
    cv.drawCircle(178, -150, 40, fill(acc)); cv.drawCircle(178, -150, 40, stroke((60, 60, 66), 6))
    cv.save(); cv.translate(178, -150); cv.rotate(T * 500 * run)
    for k in range(3): cv.drawLine(0, 0, 34 * math.cos(k * 2.09), 34 * math.sin(k * 2.09), stroke((60, 60, 66), 4))
    cv.restore()
    rrect(cv, -74, -246, 28, 38, 5, fill((220, 60, 70) if not old else (120, 40, 40)))
    if old:
        cv.drawOval(XYWH(-90, -196, 180, 40), stroke(acc, 3, 0.8)); cv.drawLine(-130, -12, 130, -12, stroke(acc, 3, 0.8))
        if dust > 0:
            for (rx, ry, rw, rh, rr) in ((-170, -30, 340, 30, 8), (90, -200, 70, 175, 14), (-150, -210, 310, 70, 24), (-160, -200, 70, 110, 12)):
                rrect(cv, rx, ry, rw, rh, rr, fill((200, 196, 186), 0.5 * dust))
    else:
        cv.drawRect(XYWH(-140, -192, 30, 8), fill(acc)); cv.drawCircle(40, -176, 9, fill(acc)); cv.drawCircle(70, -176, 9, fill((230, 90, 90)))
    cv.restore()


def battery(cv, x, y, s=1.0, dead=False, rot=0.0):
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s, s)
    rrect(cv, -18, -40, 36, 80, 6, fill((44, 44, 50))); cv.drawRect(XYWH(-18, -40, 36, 28), fill((236, 166, 44) if not dead else (130, 130, 134)))
    cv.drawRect(XYWH(-8, -48, 16, 10), fill((196, 196, 202)))
    if dead:
        cv.drawLine(-10, 0, 10, 26, stroke((230, 60, 60), 5)); cv.drawLine(10, 0, -10, 26, stroke((230, 60, 60), 5))
    else:
        cv.drawPath(path([(4, -6), (-8, 14), (0, 14), (-4, 30), (9, 8), (1, 8)]), fill((255, 240, 120)))
    cv.restore()


def caja(cv, x, y, s=1.0, junk=True):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    if junk:
        for j, col in enumerate(((220, 60, 60), (40, 40, 40), (60, 140, 220), (240, 200, 60))):
            p = skia.Path(); p.moveTo(-50 + j * 30, -100); p.quadTo(-80 + j * 44, -180 - j * 10, -30 + j * 26, -130)
            cv.drawPath(p, stroke(col, 6))
        cv.drawCircle(40, -116, 26, stroke((120, 124, 134), 10)); rrect(cv, -60, -150, 36, 56, 6, fill((176, 182, 192)))
    rrect(cv, -80, -110, 160, 110, 6, lin((0, -110), (0, 0), [(206, 160, 104), (170, 126, 78)]))
    cv.drawPath(path([(-80, -110), (-104, -134), (-20, -134), (0, -110)]), fill((186, 142, 90)))
    cv.drawPath(path([(80, -110), (104, -134), (20, -134), (0, -110)]), fill((196, 152, 98)))
    cv.drawRect(XYWH(-14, -110, 28, 110), fill((225, 200, 150), 0.6))
    cv.restore()


def gear(cv, x, y, r, rot=0.0, col=(150, 156, 168)):
    cv.save(); cv.translate(x, y); cv.rotate(rot)
    for k in range(8):
        cv.save(); cv.rotate(k * 45); cv.drawRect(XYWH(-r * 0.2, -r * 1.25, r * 0.4, r * 0.5), fill(col)); cv.restore()
    cv.drawCircle(0, 0, r, fill(col)); cv.drawCircle(0, 0, r * 0.4, fill((70, 74, 84)))
    cv.restore()


def screwdriver(col=(255, 200, 61), L=90):
    def f(cv, h):
        cv.drawLine(h[0], h[1], h[0] + L * 0.55, h[1] - L * 0.2, stroke((170, 174, 184), 6))
        cv.drawLine(h[0] - L * 0.25, h[1] + L * 0.09, h[0] + L * 0.1, h[1] - L * 0.04, stroke(col, 16))
    return f


def rain(cv, T, n=230, a=0.5, seed=5):
    rnd = random.Random(seed)
    for k in range(n):
        x0 = rnd.uniform(-100, BW + 400); sp = rnd.uniform(1500, 2300); y0 = rnd.uniform(0, BH); L = rnd.uniform(40, 90); al = rnd.uniform(0.4, 1.0)
        y = (y0 + T * sp) % BH; x = x0 - y * 0.18
        cv.drawLine(x, y, x - L * 0.18, y + L, stroke((190, 210, 255), 3, a * al))


def flash(lt, times):
    return max([math.exp(-(lt - t) * 7) for t in times if lt >= t] + [0.0])


def bolt(cv, x, seed, a):
    rnd = random.Random(seed); pts = [(x, 0)]; y = 0
    while y < 1050:
        y += rnd.uniform(70, 140); x += rnd.uniform(-90, 90); pts.append((x, y))
    cv.drawPath(path(pts, False), stroke((255, 255, 240), 10, a)); cv.drawPath(path(pts, False), stroke((200, 220, 255), 26, a * 0.3))


def trophy(cv, x, y, s=1.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    g = lin((-40, 0), (40, 0), [(236, 170, 40), (255, 230, 120), (220, 150, 30)])
    for sx in (-1, 1): cv.drawArc(XYWH(sx * 34 - 22, -104, 44, 50), 0, 360, False, stroke((236, 170, 40), 8))
    cv.drawPath(path([(-42, -116), (42, -116), (32, -54), (10, -36), (10, -16), (-10, -16), (-10, -36), (-32, -54)]), g)
    rrect(cv, -36, -16, 72, 16, 4, fill((120, 80, 40))); rrect(cv, -26, -22, 52, 8, 3, g)
    cv.drawCircle(0, -84, 12, fill((255, 250, 210)))
    cv.restore()


def star(cv, x, y, r, a=1.0, col=(255, 255, 255)):
    cv.drawLine(x - r, y, x + r, y, stroke(col, max(2, r * 0.22), a)); cv.drawLine(x, y - r, x, y + r, stroke(col, max(2, r * 0.22), a))


def sparkles(cv, T, pts, r=22):
    for k, (x, y) in enumerate(pts):
        star(cv, x, y, r * max(0, math.sin(T * 5 + k * 1.7)), 0.9)


def confetti(cv, T, t0, n=70, area=(150, 1050)):
    rnd = random.Random(3)
    for k in range(n):
        x = rnd.uniform(*area) + math.sin(T * 3 + k) * 30; y = 300 + ((T - t0) * rnd.uniform(200, 380) + rnd.uniform(0, 1600)) % 1750
        cv.save(); cv.translate(x, y); cv.rotate(T * 200 + k * 30)
        cv.drawRect(XYWH(-9, -5, 18, 10), fill([(255, 200, 61), (46, 158, 79), (255, 255, 255), (230, 80, 60), (70, 130, 220)][k % 5]))
        cv.restore()


def onomatopeya(cv, s, x, y, age, size=90, col=(255, 240, 200)):
    if age < 0 or age > 0.7: return
    a = min(1, age / 0.08) * clamp((0.7 - age) / 0.25)
    cv.save(); cv.translate(x, y - age * 60); cv.rotate(-10)
    text_center(cv, s, 0, 0, size, col, (60, 30, 20), 0.09, a=a, scale=0.8 + 0.3 * ease_out(age / 0.2))
    cv.restore()


def puerta_abierta(cv, o, T, abuela=False):
    """Puerta de la casa del patio abriéndose con luz cálida (o = 0..1)."""
    if o <= 0: return
    w = 184 * o
    cv.drawRect(XYWH(1078, 1084, w, 496), lin((0, 1084), (0, 1580), [(255, 226, 160), (255, 190, 110)]))
    cv.drawPath(path([(1078, 1580), (1078 + w, 1580), (1078 + w - 260 * o, BH), (1078 - 560 * o, BH)]), fill((255, 210, 130), 0.2 * o))
    cv.drawCircle(1170, 1330, 420, rad((1170, 1330), 420, [(255, 214, 140, 0.35 * o), (255, 214, 140, 0.0)]))
    if abuela:
        cv.save(); cv.clipRect(XYWH(1078, 1084, w, 496))
        H_.silhouette_begin(cv)
        Mo.draw_char(cv, ROSA, dict(STAND, af=(70, 60)), 1168, 1580, 390, -1, T)
        H_.silhouette_end(cv, (70, 40, 30), 0.88)
        cv.restore()
    cv.drawPath(path([(1078 + w, 1084), (1262, 1070), (1262, 1594), (1078 + w, 1580)]), lin((0, 1084), (0, 1580), [(130, 80, 46), (100, 60, 34)]))


# ============================================================ EPISODIO 6 — El robot de chatarra
def ep06():
    S = []

    def s1(cv, lt, d, T):  # feria: Camila encuentra una caja de cables
        cam = cam_move(lt, d, (560, 1440, 1.45), (600, 1420, 1.75)); stage(cv, cam, "feria")
        x, ph, mv = walker(lt, 0, 180, 520, 1.5, 1.5)
        caja(cv, 700, 1720, 1.0)
        if mv: p = walk(ph)
        elif lt < d * 0.62:
            dig = math.sin(T * 7); p = dict(STAND, lean=16, af=(70 + 14 * dig, 20), ab=(60 - 14 * dig, 30), head=16, look=(0.7, 0.9), mood="focused")
        else: p = dict(STAND, af=(150, 12), ab=(20, 30), head=-10, look=(0.8, -0.7), mood="happy")
        shade(cv, x, 1720); info = ch(cv, CAMILA, p, x, 1720, T=T, seed=21, ex=dict(blush=lt > d * 0.62))
        if not mv and lt >= d * 0.62:
            h = info["hand_f"]; pth = skia.Path(); pth.moveTo(*h); pth.cubicTo(h[0] + 60, h[1] + 80, h[0] - 20, h[1] + 150, h[0] + 70, h[1] + 230)
            cv.drawPath(pth, stroke((220, 60, 60), 7)); sparkles(cv, T, [(h[0] + 40, h[1] - 50), (h[0] - 50, h[1] - 20), (h[0] + 80, h[1] + 40)], 26)
        done(cv)
    S.append((0.0, s1))

    def desk(cv, T):
        rrect(cv, 620, 1590, 460, 26, 6, fill((150, 104, 66)))
        for px in (640, 1040): cv.drawRect(XYWH(px, 1614, 20, 180), fill((120, 82, 50)))
        rrect(cv, 880, 1500, 130, 90, 10, fill((150, 96, 60))); cv.drawCircle(915, 1545, 24, fill((60, 44, 34)))      # radio rota
        for j, col in enumerate(((220, 60, 60), (60, 140, 220), (240, 200, 60))):
            p = skia.Path(); p.moveTo(990, 1520 + j * 10); p.quadTo(1050 + j * 14, 1470, 1040 + j * 12, 1588); cv.drawPath(p, stroke(col, 5))
        cv.drawRect(XYWH(1034, 1470, 8, 120), fill((90, 90, 96))); cv.drawPath(path([(990, 1470), (1080, 1470), (1062, 1420), (1010, 1420)]), fill((255, 200, 61)))
        cv.drawPath(path([(990, 1470), (1080, 1470), (1140, 1590), (900, 1590)]), fill((255, 236, 170), 0.2))

    def s2(cv, lt, d, T):  # vivió entre cables, tornillos y radios rotos: su cuarto-taller
        cam = cam_move(lt, d, (720, 1450, 1.5), (760, 1470, 1.8)); stage(cv, cam, "cuarto_camila")
        rrect(cv, 680, 1640, 110, 18, 6, fill((120, 82, 50))); cv.drawRect(XYWH(726, 1656, 16, 136), fill((104, 70, 42)))
        w = math.sin(T * 9)
        info = ch(cv, CAMILA, dict(SIT_BENCH, af=(62 + 10 * w, 40 + 16 * w), ab=(50, 60), head=12, look=(0.8, 0.7), mood="focused"), 735, 1790, S=600, T=T, seed=21,
                  persp_on=False, ex=dict(hand_item=screwdriver()))
        desk(cv, T)
        particles(cv, T, 10, 2, (255, 240, 200), (860, 1400, 240, 180), 20, (2, 4), 0.7)
        done(cv)
    S.append((A("camila de trece"), s2))

    def s3(cv, lt, d, T):  # cada domingo recorría la feria buscando piezas
        cam = cam_move(lt, d, (480, 1440, 1.4), (800, 1440, 1.4)); stage(cv, cam, "feria")
        stop = d * 0.55
        x, ph, mv = walker(lt, 0, 150, 760, stop, 1.5)
        shade(cv, 1010, 1720); v = ch(cv, Mo.NEIGHBORS[2], dict(STAND, af=(80 if lt > stop - 0.5 else 10, 10), mood="kind"), 1010, 1720, face=-1, T=T, seed=33)
        shade(cv, x, 1720)
        info = ch(cv, CAMILA, walk(ph, base=dict(HOLD, mood="happy")) if mv else dict(HOLD, mood="happy", look=(0.9, -0.2)), x, 1720, T=T, seed=21)
        bx, by = (info["hand_f"][0] + info["hand_b"][0]) / 2 + 30, info["hand_f"][1] + 60
        u = clamp((lt - stop) / 0.8)
        if lt < stop + 0.8:
            g = H_.arc((v["hand_f"][0] - 30, v["hand_f"][1]), (bx, by - 120), 120, u) if lt > stop else (v["hand_f"][0] - 30, v["hand_f"][1])
            if lt > stop - 0.5: gear(cv, g[0], g[1], 26, T * 200)
        caja(cv, bx, by, 0.75)
        if lt > stop + 0.8: sparkles(cv, T, [(bx, by - 170), (bx + 60, by - 130)], 22)
        done(cv)
    S.append((A("cada domingo"), s3))

    def s4(cv, lt, d, T):  # su sueño: construir un robot y llevarlo a la feria de ciencias
        cam = cam_move(lt, d, (460, 1350, 1.55), (330, 900, 2.5)); stage(cv, cam, "cuarto_camila")
        info = ch(cv, CAMILA, breathe(dict(HIPS, head=-16, look=(0.7, -0.9), mood="happy"), T), 600, 1840, S=600, face=-1, T=T, seed=21, persp_on=False, ex=dict(blush=True))
        cv.drawCircle(275, 780, 260, rad((275, 780), 260, [(255, 240, 170, 0.35 * ease(lt / d)), (255, 240, 170, 0.0)]))
        sparkles(cv, T, [(140, 640), (410, 620), (120, 900), (420, 930), (275, 560)], 26)
        done(cv)
    S.append((A("su sueño"), s4))

    def s5(cv, lt, d, T):  # un robot cuesta caro
        cam = cam_move(lt, d, (690, 1420, 2.0), (670, 1470, 2.3)); stage(cv, cam, "feria")
        cv.drawRect(XYWH(600, 1250, 180, 150), fill((255, 255, 255), 0.92)); cv.drawRect(XYWH(600, 1250, 180, 150), stroke((70, 130, 220), 6))
        robot(cv, 690, 1392, 120, eyes=1.0, T=T, arm=0.2)
        sparkles(cv, T, [(620, 1270), (760, 1290), (700, 1240)], 16)
        cv.save(); cv.translate(820, 1300); cv.rotate(8); rrect(cv, -60, -34, 120, 68, 8, fill((255, 240, 120)))
        text_center(cv, "$$$", 0, 0, 46, (200, 40, 30), None, shadow_=False); cv.restore()
        t1 = d * 0.45
        p = dict(STAND, head=-10, look=(0.8, -0.7), mood="surprised") if lt < t1 else dict(SAD_STAND, af=(55, 70), look=(0.6, 0.9))
        shade(cv, 500, 1720); info = ch(cv, CAMILA, p, 500, 1720, T=T, seed=21)
        if lt >= t1:
            for k in range(2): cv.drawOval(XYWH(info["hand_f"][0] - 16 + k * 14, info["hand_f"][1] - 22 - k * 4, 26, 12), fill((225, 175, 70)))
        done(cv)
    S.append((A("pero un robot"), s5))

    def s6(cv, lt, d, T):  # con una caja de chatarra empieza a armar en el patio
        cam = cam_move(lt, d, (640, 1640, 1.3), (700, 1660, 1.5)); stage(cv, cam, "patio_tarde")
        x, ph, mv = walker(lt, 0, 250, 560, d * 0.5, 1.4)
        robot(cv, RX, GY, 600, parts=clamp((lt - d * 0.6) / (d * 0.4)) * 1.0, T=T)
        shade(cv, x, GY)
        if mv:
            info = ch(cv, CAMILA, walk(ph, base=dict(HOLD, mood="determined")), x, GY, T=T, seed=21)
            caja(cv, info["hand_f"][0] + 30, info["hand_f"][1] + 70, 0.8)
        else:
            caja(cv, 470, GY + 10, 0.9)
            w = math.sin(T * 8)
            ch(cv, CAMILA, dict(CROUCH, af=(60 + 12 * w, 40), ab=(50 - 12 * w, 50), mood="determined", look=(0.8, 0.5)), 610, GY, T=T, seed=21, ex=dict(hand_item=screwdriver()))
        done(cv)
    S.append((A("con una caja"), s6))

    def s7(cv, lt, d, T):  # latas, tuercas, un colador viejo como cabeza
        cam = cam_move(lt, d, (700, 1560, 1.6), (720, 1500, 1.85)); stage(cv, cam, "patio_tarde")
        caja(cv, 440, GY + 10, 0.9, junk=lt < d * 0.7)
        t2, t3 = A("tuercas") - A("latas"), A("un colador") - A("latas")
        parts = 1 + clamp(lt / 0.5) + clamp((lt - t2) / 0.5) + clamp((lt - t3) / 0.5) + clamp((lt - t3 - 0.6) / 0.4)
        r = robot(cv, RX, GY, 600, parts=parts, T=T)
        w = math.sin(T * 10)
        up = clamp((lt - t3) / 0.4)
        shade(cv, 560, GY)
        ch(cv, CAMILA, dict(STAND, af=(80 + 60 * up + 10 * w, 20), ab=(70 + 50 * up - 10 * w, 30), head=-6 - 8 * up, look=(0.9, -0.3 - 0.5 * up), mood="determined"),
           560, GY, T=T, seed=21, ex=dict(hand_item=screwdriver()))
        for k, tt in enumerate((0.0, t2, t3)):
            if 0 <= lt - tt < 0.5:
                yy = GY - (360, 300, 520)[k]
                for j in range(8):
                    a = j * 0.785; rr = 60 + 160 * (lt - tt)
                    star(cv, RX + math.cos(a) * rr, yy + math.sin(a) * rr, 14, 1 - (lt - tt) / 0.5, (255, 240, 170))
        done(cv)
    S.append((A("latas"), s7))

    def s8(cv, lt, d, T):  # último tornillo; el robot queda inmóvil
        cam = cam_move(lt, d, (720, 1560, 1.9), (700, 1600, 1.5)); stage(cv, cam, "patio_tarde")
        robot(cv, RX, GY, 600, T=T)
        back = A("el robot quedó") - A("cuando terminó") - 0.3
        if lt < back:
            w = lt * 8
            x = 580; p = dict(STAND, af=(92 + 6 * math.sin(w), 6 * math.cos(w)), ab=(30, 30), look=(0.9, 0.1), mood="focused")
        else:
            x, ph, mv = walker(lt, back, 580, 440, 0.9, 1.6)
            p = walk(-ph, amp=0.6) if mv else dict(STAND, look=(0.9, -0.2), mood="worried")
        shade(cv, x, GY); ch(cv, CAMILA, p, x, GY, T=T, seed=21, ex=dict(hand_item=screwdriver()) if lt < back else None)
        done(cv)
    S.append((A("cuando terminó"), s8))

    def s9(cv, lt, d, T):  # le faltaba algo: Camila lo contempla de brazos cruzados
        cam = cam_move(lt, d, (640, 1640, 1.3), (660, 1620, 1.42)); stage(cv, cam, "patio_tarde")
        robot(cv, RX, GY, 600, T=T)
        shade(cv, 440, GY); ch(cv, CAMILA, breathe(dict(CROSS, head=-6 + 6 * math.sin(T * 0.9), look=(0.9, -0.2), mood="worried"), T), 440, GY, T=T, seed=21)
        done(cv)
    S.append((A("le faltaba"), s9))

    def s10(cv, lt, d, T):  # «necesitas un corazón»: los ojos apagados
        cam = cam_move(lt, d, (760, 1440, 2.3), (760, 1560, 2.9)); stage(cv, cam, "patio_tarde")
        r = robot(cv, RX, GY, 600, T=T)
        tq = A("necesitas") - A("camila lo miró")
        u = ease((lt - tq) / 0.8)
        if u > 0:
            hx, hy = lerp(480, r["chest"][0] - 50, u), lerp(1780, r["chest"][1] + 10, u)
            cv.drawLine(hx - 240, hy + 90, hx, hy, stroke(BLACK, 12)); cv.drawCircle(hx, hy, 16, fill(BLACK))
        cv.drawRect(XYWH(0, 0, BW, BH), fill((30, 20, 60), 0.18 * ease(lt / d)))
        done(cv)
    S.append((A("camila lo miró"), s10))
    texts = [("BASURA O TESORO", 0.3, A("camila de trece") - 0.1), ("ROBOT DE CHATARRA", A("empezó a armar"), A("cuando terminó") - 0.1),
             ("«NECESITAS UN CORAZÓN»", A("necesitas"), 54.6)]
    return S, texts


# ============================================================ EPISODIO 7 — El primer intento
def ep07():
    S = []

    def s1(cv, lt, d, T):  # el robot se encendió
        cam = cam_move(lt, d, (700, 1600, 1.4), (730, 1540, 1.65)); stage(cv, cam, "patio_tarde")
        fl = 0.75 + 0.25 * math.sin(T * 23)
        robot(cv, RX, GY, 600, eyes=ease(lt / 0.4) * fl, arm=ease((lt - 0.5) / 1.2), T=T)
        hop = abs(math.sin(T * 7)) * 0.06
        shade(cv, 470, GY); ch(cv, CAMILA, dict(CHEER, air=hop), 470, GY, T=T, seed=21, ex=dict(blush=True))
        done(cv)
    S.append((0.0, s1))

    def s2(cv, lt, d, T):  # había conectado un motor pequeño con una pila vieja
        cam = cam_move(lt, d, (640, 1740, 1.8), (680, 1720, 2.05)); stage(cv, cam, "patio_tarde")
        robot(cv, RX, GY, 600, T=T, motor=True)
        battery(cv, 500, GY - 30, 1.3, rot=-90)
        p = skia.Path(); p.moveTo(546, GY - 30); p.cubicTo(600, GY - 160, 640, GY - 60, RX - 20, GY - 310)
        cv.drawPath(p, stroke((220, 60, 60), 6)); cv.drawPath(p, stroke((255, 255, 255), 2, 0.3))
        w = math.sin(T * 7)
        ch(cv, CAMILA, dict(KNEEL, af=(70 + 8 * w, 30 + 10 * w), ab=(60, 40), look=(0.9, 0.2), mood="focused"), 590, GY + 30, T=T, seed=21)
        done(cv)
    S.append((A("camila había"), s2))

    def s3(cv, lt, d, T):  # las tapas brillaron, el brazo subió... ¡chispazo!
        t0 = A("las tapas"); tz = A("un chispazo") - t0
        cam = Cam(730, 1520, 1.7 + 0.1 * lt / d, shake=14 * max(0, 1 - abs(lt - tz - 0.1) / 0.4) if lt > tz else 0, t=T); stage(cv, cam, "patio_tarde")
        on = lt < tz
        r = robot(cv, RX, GY, 600, eyes=(ease(lt / 0.3) if on else max(0, 1 - (lt - tz) * 4)), arm=ease((lt - (A("el brazo") - t0)) / 0.9) if on else 0.9, T=T, motor=True,
                  heart=1.0 if on else 0, shake=6 if lt > tz and lt < tz + 0.4 else 0)
        shade(cv, 470, GY); ch(cv, CAMILA, dict(CHEER, air=0.03) if on else dict(ARMS_UP, mood="surprised", lean=-10), 470, GY, T=T, seed=21)
        if lt >= tz:
            a = max(0, 1 - (lt - tz) / 0.5); c = r["chest"]
            for j in range(10):
                ang = j * 0.628 + 0.3; r0, r1 = 40, 40 + 260 * (1 - a) + 80
                pts = [(c[0] + math.cos(ang) * r0, c[1] + math.sin(ang) * r0), (c[0] + math.cos(ang + 0.12) * (r0 + r1) / 2, c[1] + math.sin(ang + 0.12) * (r0 + r1) / 2),
                       (c[0] + math.cos(ang) * r1, c[1] + math.sin(ang) * r1)]
                cv.drawPath(path(pts, False), stroke((255, 240, 120), 9, a))
            cv.drawCircle(c[0], c[1], 150 * a, fill((255, 255, 230), a))
            cv.drawRect(XYWH(0, 0, BW, BH), fill((255, 255, 240), 0.7 * max(0, 1 - (lt - tz) / 0.15)))
        done(cv)
    S.append((A("las tapas"), s3))

    def s4(cv, lt, d, T):  # el motor echó humo y todo quedó en silencio
        cam = cam_move(lt, d, (720, 1560, 1.6), (680, 1620, 1.35)); stage(cv, cam, "patio_tarde")
        robot(cv, RX, GY, 600, smoke=1.0, arm=max(0, 0.9 - lt * 1.5), T=T, motor=True)
        x, ph, mv = walker(lt, 0, 470, 380, 0.8, 1.6)
        shade(cv, x, GY); ch(cv, CAMILA, walk(-ph, amp=0.6, base=dict(STAND, mood="surprised")) if mv else dict(SAD_STAND, look=(0.9, 0.2), head=8), x, GY, T=T, seed=21)
        done(cv)
    S.append((A("el motor echó"), s4))

    def s5(cv, lt, d, T):  # los compañeros se ríen desde la reja
        cam = cam_move(lt, d, (300, 1420, 2.0), (330, 1430, 2.2)); stage(cv, cam, "patio_tarde")
        for k, x in enumerate((70, 185, 300)):
            j = math.sin(T * 14 + k * 2)
            p = dict(STAND, lean=-6 + 5 * j, ab=(60, 70), af=(55, 75) if k != 1 else (95, 0), head=-10, mood="happy")
            Mo.draw_char(cv, Mo.KIDS[k], p, x, 1600 + abs(j) * -8, 430, 1, T)
        EC.reja_bars(cv, "tarde")
        t1 = A("tu robot") - A("sus compañeros")
        for k in range(3): onomatopeya(cv, "JA", 110 + k * 90, 1150 - (k % 2) * 60, (lt - 0.9 - k * 0.35) % 1.4, 70)
        done(cv)
    S.append((A("sus compañeros"), s5))

    def s6(cv, lt, d, T):  # deja el destornillador, se sienta junto al robot y esconde la cara
        cam = cam_move(lt, d, (660, 1640, 1.45), (680, 1700, 1.7)); stage(cv, cam, "patio_tarde")
        robot(cv, RX, GY, 600, smoke=0.5, T=T, motor=True)
        t1 = A("dejó el destornillador") - A("ella no"); t2 = A("se sentó") - A("ella no"); t3 = A("y escondió") - A("ella no")
        if lt < t2:
            x, ph, mv = walker(lt, t1 + 0.6, 400, 560, max(0.4, t2 - t1 - 0.6), 1.3)
            p = walk(ph, amp=0.7, base=SAD_STAND) if mv else SAD_STAND
        else:
            x = 560; u = ease((lt - t3) / 0.6)
            p = mix(dict(SIT_GROUND, head=14), dict(SIT_GROUND, head=46, lean=30, ab=(80, 60), af=(75, 70), look=(0.3, 1.0)), u)
            p = mix(SAD_STAND, p, ease((lt - t2) / 0.5))
        shade(cv, x, GY + 10); ch(cv, CAMILA, p, x, GY + 10, T=T, seed=21)
        dy = min(1.0, max(0, lt - t1) / 0.35)
        if lt > t1:
            cv.save(); cv.translate(400, lerp(GY - 300, GY + 6, dy * dy)); cv.rotate(20 + 70 * dy)
            cv.drawLine(0, 0, 50, 0, stroke((170, 174, 184), 6)); cv.drawLine(-36, 0, 0, 0, stroke((255, 200, 61), 16)); cv.restore()
        done(cv)
    S.append((A("ella no"), s6))

    def s7(cv, lt, d, T):  # calendario: inscripción en 4 días
        cv.drawRect(skia.Rect.MakeWH(W, H), lin((0, 0), (0, H), [(232, 196, 150), (196, 150, 104)]))
        cv.save(); cv.translate(W / 2, 880); cv.rotate(-2 + math.sin(T) * 0.4); cv.scale(1 + 0.03 * lt / d, 1 + 0.03 * lt / d)
        cv.drawRect(XYWH(-390, -470, 800, 980), fill((0, 0, 0), 0.3, blur=18))
        cv.drawRect(XYWH(-400, -490, 800, 980), fill((252, 250, 244))); cv.drawRect(XYWH(-400, -490, 800, 170), fill((200, 50, 40)))
        text_center(cv, "FERIA DE CIENCIAS", 0, -405, 64, (255, 255, 255), None, shadow_=False)
        for k, dname in enumerate("LMXJVSD"): text_center(cv, dname, -330 + k * 110, -270, 40, (120, 120, 130), None, font="Inter-Bold", shadow_=False)
        n = 1
        for r in range(4):
            for c in range(7):
                cx_, cy_ = -330 + c * 110, -170 + r * 120
                cv.drawRect(XYWH(cx_ - 50, cy_ - 54, 100, 108), stroke((220, 216, 208), 3))
                text_center(cv, str(n), cx_, cy_ - 8, 44, (60, 60, 70) if n != 20 else (200, 40, 30), None, font="Inter-Bold", shadow_=False)
                if n < 16: cv.drawLine(cx_ - 30, cy_ - 34, cx_ + 30, cy_ + 26, stroke((120, 120, 130), 5, 0.6))
                if n == 20:
                    sw = 360 * ease((lt - 0.5) / 0.8)
                    cv.drawArc(XYWH(cx_ - 62, cy_ - 66, 124, 124), -90, sw, False, stroke((220, 40, 40), 9))
                n += 1
        text_center(cv, "INSCRIPCIÓN:", 0, 330, 60, (60, 60, 70), None, shadow_=False)
        pulse = 1 + 0.05 * math.sin(T * 6)
        text_center(cv, "4 DÍAS", 0, 420, 110, (210, 40, 36), None, shadow_=False, scale=pulse)
        cv.restore()
    S.append((A("la feria cerraba"), s7))

    def s8(cv, lt, d, T):  # ya no había pila, ni motor, ni esperanza
        cam = cam_move(lt, d, (680, 1700, 1.6), (660, 1640, 1.25)); stage(cv, cam, "patio_tarde")
        robot(cv, RX, GY, 600, smoke=0.3, T=T, motor=True)
        battery(cv, 400, GY + 40, 1.2, dead=True, rot=-70)
        gear(cv, 950, GY + 50, 30, 20, (90, 80, 76)); cv.drawCircle(950, GY + 50, 44, fill((30, 30, 30), 0.3, blur=8))
        shade(cv, 560, GY + 10)
        ch(cv, CAMILA, breathe(dict(SIT_GROUND, head=46, lean=30, ab=(80, 60), af=(75, 70), look=(0.3, 1.0)), T), 560, GY + 10, T=T, seed=21)
        cv.drawRect(XYWH(0, 0, BW, BH), fill((20, 20, 70), 0.3 * ease(lt / d)))
        done(cv)
    S.append((A("ya no había"), s8))

    def s9(cv, lt, d, T):  # desde la casa: tac, tac, tac... «mijita, ven»
        t0 = A("entonces"); tv = A("mijita") - t0
        if lt < tv: cam = cam_move(lt, tv, (1000, 1500, 1.5), (1120, 1380, 1.95))
        else: cam = cam_move(lt - tv, d - tv, (1120, 1380, 1.95), (930, 1560, 1.45))
        stage(cv, cam, "patio_tarde")
        cv.drawRect(XYWH(0, 0, BW, BH), fill((20, 20, 70), 0.3))
        o = ease((lt - (A("se escuchó") - t0)) / 1.2)
        puerta_abierta(cv, o, T, abuela=lt > tv - 0.3)
        robot(cv, RX, GY, 600, T=T, motor=True)
        look = lt > A("se escuchó") - t0
        shade(cv, 560, GY + 10)
        ch(cv, CAMILA, dict(SIT_GROUND, head=-8, look=(0.9, -0.4), mood="surprised") if look else dict(SIT_GROUND, head=46, lean=30, ab=(80, 60), af=(75, 70)), 560, GY + 10, T=T, seed=21)
        for k in range(3):
            onomatopeya(cv, "TAC", 1000 + k * 90, 1080 - k * 50, lt - (A("tac", k) - t0), 84)
        done(cv)
    S.append((A("entonces"), s9))
    texts = [("CHISPAZO", A("un chispazo"), A("sus compañeros") - 0.1), ("«ES PURA BASURA»", A("tu robot"), A("ella no") - 0.1),
             ("4 DÍAS", A("cuatro días"), A("ya no había") - 0.1)]
    return S, texts


# ============================================================ EPISODIO 8 — La máquina de la abuela
def mesa_costura(cv, T, run=0.0, tela=True):
    rrect(cv, 500, 1530, 420, 28, 6, fill((150, 104, 66)))
    for px in (522, 878): cv.drawRect(XYWH(px, 1556, 22, 236), fill((120, 82, 50)))
    if tela:
        off = (T * 50 * run) % 40
        cv.drawPath(path([(498, 1520), (720, 1520), (720, 1532), (560, 1532), (548, 1680), (500, 1650)]), fill((120, 170, 220)))
        for k in range(5): cv.drawLine(520 + k * 40 - off, 1525, 540 + k * 40 - off, 1525, stroke((255, 255, 255), 4, 0.85))
    sewing(cv, 710, 1530, 0.95, old=False, T=T, run=run, face=1)


def rincon(cv, T, old=True, dust=1.0):
    rrect(cv, 950, 1560, 330, 26, 6, fill((130, 90, 58)))
    for px in (966, 1244): cv.drawRect(XYWH(px, 1584, 20, 208), fill((104, 70, 42)))
    if old: sewing(cv, 1115, 1560, 0.85, old=True, T=T, dust=dust)
    sp_y = 700 + 30 * math.sin(T * 1.3)
    cv.drawLine(1250, 520, 1250, sp_y, stroke((255, 255, 255), 2, 0.5)); cv.drawCircle(1250, sp_y, 9, fill((30, 30, 34)))


def motor_item(cv, x, y, s=1.0, glow=0.0, T=0.0):
    if glow > 0: cv.drawCircle(x, y, 150 * s, rad((x, y), 150 * s, [(255, 220, 130, 0.6 * glow), (255, 220, 130, 0.0)]))
    rrect(cv, x - 50 * s, y - 34 * s, 100 * s, 68 * s, 16 * s, lin((0, y - 34 * s), (0, y + 34 * s), [(226, 190, 90), (170, 130, 50)]))
    for k in range(5): cv.drawLine(x - 34 * s + k * 17 * s, y - 30 * s, x - 34 * s + k * 17 * s, y + 30 * s, stroke((120, 86, 30), 3 * s))
    cv.drawRect(XYWH(x + 50 * s, y - 8 * s, 30 * s, 16 * s), fill((150, 156, 168))); gear(cv, x + 88 * s, y, 16 * s, T * 300)


def ep08():
    S = []
    FY = 1840

    def abuela_sentada(cv, T, run=1.0, look=(0.7, 0.6), mood="focused"):
        rrect(cv, 380, 1630, 130, 20, 6, fill((120, 82, 50))); cv.drawRect(XYWH(436, 1648, 18, 144), fill((104, 70, 42)))
        w = math.sin(T * 6) * run
        ch(cv, ROSA, dict(SIT_BENCH, af=(60 + 5 * w, 40), ab=(50 - 5 * w, 50), head=10, look=look, mood=mood), 445, 1790, S=600, T=T, seed=50, persp_on=False)

    def s1(cv, lt, d, T):  # el corazón estaba en la casa de la abuela
        cam = cam_move(lt, d, (700, 1480, 1.15), (640, 1460, 1.35)); stage(cv, cam, "casa_abuela")
        rincon(cv, T); abuela_sentada(cv, T); mesa_costura(cv, T, 1.0)
        x, ph, mv = walker(lt, 0.2, 1420, 900, d * 0.7, 1.3)
        ch(cv, CAMILA, walk(ph, amp=0.8, base=SAD_STAND) if mv else dict(SAD_STAND, look=(-0.8, 0)), x, FY, S=600, face=-1, T=T, seed=21, persp_on=False)
        done(cv)
    S.append((0.0, s1))

    def s2(cv, lt, d, T):  # Abuela Rosa cose frente a su máquina nueva
        cam = cam_move(lt, d, (520, 1420, 1.8), (560, 1400, 2.1)); stage(cv, cam, "casa_abuela")
        abuela_sentada(cv, T, mood="kind"); mesa_costura(cv, T, 1.0)
        for k in range(3): onomatopeya(cv, "tac", 620 + k * 60, 1250 - k * 30, (lt - 0.4 - k * 0.3) % 1.6, 50)
        done(cv)
    S.append((A("abuela rosa"), s2))

    def s3(cv, lt, d, T):  # en un rincón, otra máquina vieja juntaba polvo
        cam = cam_move(lt, d, (1040, 1400, 2.0), (1090, 1420, 2.5)); stage(cv, cam, "casa_abuela")
        rincon(cv, T)
        particles(cv, T, 40, 6, (240, 236, 220), (900, 1150, 420, 450), 12, (2, 5), 0.7)
        done(cv)
    S.append((A("en un rincón"), s3))

    def s4(cv, lt, d, T):  # «esa ya no cose, pero tiene un buen motor»
        cam = cam_move(lt, d, (860, 1460, 1.5), (900, 1450, 1.65)); stage(cv, cam, "casa_abuela")
        rincon(cv, T); mesa_costura(cv, T, 0.0)
        ch(cv, ROSA, dict(POINT, mood="kind", look=(0.8, 0)) if lt > 0.4 else dict(STAND, mood="kind"), 600, FY, S=600, face=1, T=T, seed=50, persp_on=False)
        turn = lt > A("pero tiene") - A("esa ya")
        ch(cv, CAMILA, dict(STAND, look=(0.9, 0.1), mood="surprised") if turn else dict(SAD_STAND, look=(0.8, -0.3)), 820, FY, S=600, face=1 if turn else -1, T=T, seed=21, persp_on=False)
        if turn: sparkles(cv, T, [(1010, 1340), (1220, 1360), (1110, 1300)], 20)
        done(cv)
    S.append((A("esa ya"), s4))

    def s5(cv, lt, d, T):  # Camila abrió los ojos
        cam = cam_move(lt, d, (840, 1430, 2.9), (850, 1420, 3.4)); stage(cv, cam, "casa_abuela")
        mesa_costura(cv, T, 0.0)
        info = ch(cv, CAMILA, dict(STAND, look=(0.9, 0.0), mood="surprised", head=-4), 820, FY, S=600, face=1, T=T, seed=21, persp_on=False, ex=dict(blush=True, blink=0))
        hc = info["head"]
        sparkles(cv, T, [(hc[0] + 120, hc[1] - 90), (hc[0] - 110, hc[1] - 70), (hc[0] + 150, hc[1] + 40), (hc[0] - 130, hc[1] + 60)], 22)
        done(cv)
    S.append((A("camila abrió"), s5))

    def s6(cv, lt, d, T):  # juntas desarman la máquina: «punto por punto»
        cam = cam_move(lt, d, (1100, 1440, 2.3), (1110, 1420, 2.6)); stage(cv, cam, "casa_abuela")
        t0 = A("juntas"); tm = A("las cosas buenas") - t0
        rincon(cv, T, dust=max(0, 1 - lt / max(0.5, tm)))
        up = ease((lt - tm) / 1.0)
        if up > 0: motor_item(cv, 1115, 1470 - 150 * up, 1.0, glow=up, T=T)
        w = lt * 7
        for sx, sc_, base in ((-1, 1.0, (1000, 1420)), (1, 0.75, (1230, 1440))):       # mano de la abuela y mano de Camila
            hx, hy = base[0] + 8 * math.cos(w + sx), base[1] + 8 * math.sin(w + sx)
            if up > 0: hx, hy = lerp(hx, 1115 + sx * 80, up), lerp(hy, 1480 - 150 * up, up)
            cv.drawLine(hx + sx * 300, hy + 240, hx, hy, stroke(BLACK, 15 * sc_)); cv.drawCircle(hx, hy, 20 * sc_, fill(BLACK))
            if up < 0.2:
                cv.drawLine(hx, hy, hx - sx * 60, hy + 26, stroke((170, 174, 184), 7)); cv.drawLine(hx + sx * 30, hy - 12, hx, hy, stroke((255, 200, 61) if sx > 0 else (200, 60, 60), 17))
        particles(cv, T, 24, 6, (240, 236, 220), (950, 1200, 340, 380), 40, (2, 5), 0.6 * (1 - up))
        done(cv)
    S.append((A("juntas"), s6))

    def s7(cv, lt, d, T):  # Camila conecta el motor con paciencia, cable por cable
        cam = cam_move(lt, d, (700, 1680, 1.6), (720, 1640, 1.8)); stage(cv, cam, "patio_tarde")
        robot(cv, RX, GY, 600, T=T, motor=True)
        shade(cv, 430, GY); ch(cv, ROSA, dict(STAND, af=(70, 30), mood="kind", look=(0.8, 0.4)), 430, GY, T=T, seed=50)
        w = math.sin(T * 5)
        info = ch(cv, CAMILA, dict(KNEEL, af=(80 + 6 * w, 20 + 8 * w), ab=(70, 30), look=(0.9, 0.1), mood="focused"), 600, GY + 30, T=T, seed=21)
        for j, col in enumerate(((220, 60, 60), (60, 140, 220))):
            p = skia.Path(); p.moveTo(info["hand_f"][0], info["hand_f"][1]); p.quadTo(RX - 120, GY - 260 - j * 40, RX - 20, GY - 320 + j * 20)
            cv.drawPath(p, stroke(col, 5))
        done(cv)
    S.append((A("camila conectó"), s7))

    def s8(cv, lt, d, T):  # las tapas se encienden en azul y el robot levanta un brazo
        cam = cam_move(lt, d, (760, 1520, 1.9), (760, 1480, 2.2)); stage(cv, cam, "patio_tarde")
        on = ease(lt / 0.5)
        cv.save(); cv.translate(RX, GY - 470)
        for k in range(12):
            cv.save(); cv.rotate(k * 30 + T * 20); cv.drawPath(path([(0, 0), (-40, -700), (40, -700)]), fill((140, 210, 255), 0.07 * on)); cv.restore()
        cv.restore()
        robot(cv, RX, GY, 600, eyes=on, arm=ease((lt - (A("y el robot") - A("las tapas"))) / 1.0), heart=on, motor=True, T=T)
        done(cv)
    S.append((A("las tapas"), s8))

    def s9(cv, lt, d, T):  # ¡Camila gritó de felicidad!
        cam = cam_move(lt, d, (680, 1600, 1.4), (680, 1580, 1.5)); stage(cv, cam, "patio_tarde")
        robot(cv, RX, GY, 600, eyes=1, arm=1, wave=1, heart=1, motor=True, T=T)
        cl = (math.sin(T * 14) + 1) / 2
        shade(cv, 330, GY); ch(cv, ROSA, mix(CLAP_OPEN, CLAP_SHUT, cl), 330, GY, T=T, seed=50)
        hop = abs(math.sin(T * 8)) * 0.1
        shade(cv, 540, GY); ch(cv, CAMILA, dict(CHEER, air=hop), 540, GY, T=T, seed=21, ex=dict(blush=True))
        sparkles(cv, T, [(420, 1300), (620, 1240), (900, 1220), (980, 1500)], 24)
        done(cv)
    S.append((A("camila gritó"), s9))

    def s10(cv, lt, d, T):  # la abuela, seria: ¿y de dónde sacarás las pilas?
        cam = cam_move(lt, d, (560, 1560, 1.6), (500, 1480, 2.0)); stage(cv, cam, "patio_tarde")
        tq = A("y de dónde") - A("pero la abuela")
        robot(cv, RX, GY, 600, eyes=max(0.25, 1 - lt / 3), arm=max(0, 1 - lt / 2), heart=0.4, motor=True, T=T)
        shade(cv, 600, GY); ch(cv, CAMILA, dict(STAND, look=(-0.8, -0.3), mood="worried" if lt > tq else "surprised", head=-4), 600, GY, face=-1, T=T, seed=21)
        shade(cv, 360, GY)
        info = ch(cv, ROSA, dict(STAND, af=(100, 60), mood="focused", look=(0.8, 0.0)), 360, GY, T=T, seed=50,
                  ex=dict(hand_item=lambda c, h: battery(c, h[0] + 6, h[1] - 44, 1.2, dead=True)))
        if lt > tq:
            a = clamp((lt - tq) / 0.3); hx, hy = info["hand_f"]
            text_center(cv, "?", hx + 90, hy - 150 - 10 * math.sin(T * 4), 150, (255, 200, 61), (17, 17, 17), 0.08, a=a)
        done(cv)
    S.append((A("pero la abuela"), s10))
    texts = [("MÁQUINA VIEJA", A("otra máquina"), A("esa ya") - 0.1), ("PUNTO POR PUNTO", A("punto por punto"), A("camila conectó") - 0.1),
             ("¿Y LAS PILAS?", A("y de dónde"), 54.6)]
    return S, texts


# ============================================================ EPISODIO 9 — La noche de la lluvia
def gotera(cv, T, x=RX - 40, y0=985, y1=GY - 560):
    for k in range(6):
        ph = (T * 2.2 + k / 6) % 1
        cv.drawOval(XYWH(x - 5 + (k % 2) * 60, lerp(y0, y1, ph * ph), 10, 22), fill((170, 210, 255), 0.9))
    cv.drawLine(x, y0, x, y0 + 60, stroke((170, 210, 255), 4, 0.6))


def manta(cv, info, S_=1.0):
    n, h = info["neck"], info["hip"]; u = info["u"]
    cv.drawPath(path([(n[0] - 0.11 * u, n[1] - 0.01 * u), (n[0] + 0.11 * u, n[1] - 0.01 * u), (h[0] + 0.15 * u, h[1] + 0.06 * u), (h[0] - 0.15 * u, h[1] + 0.06 * u)]),
                lin((0, n[1]), (0, h[1]), [(190, 70, 60), (150, 50, 46)]))
    for k in range(4):
        yy = lerp(n[1], h[1], (k + 0.5) / 4); cv.drawLine(n[0] - 0.12 * u, yy, n[0] + 0.12 * u, yy, stroke((240, 200, 120), 3, 0.7))


def paraguas(cv, h):
    cv.drawLine(h[0], h[1], h[0] + 20, h[1] - 230, stroke((60, 60, 66), 6))
    top = (h[0] + 20, h[1] - 230)
    dome = skia.Path(); dome.addArc(XYWH(top[0] - 130, top[1] - 70, 260, 150), 180, 180); dome.close()
    cv.drawPath(dome, fill((200, 60, 70)))
    cv.drawPath(path([(top[0] + 50, top[1] + 5), (top[0] + 130, top[1] + 5), (top[0] + 150, top[1] - 60)]), fill((170, 40, 54)))     # varilla doblada
    for k in range(4): cv.drawLine(top[0], top[1] - 66, top[0] - 120 + k * 80, top[1] + 4, stroke((120, 30, 40), 3))


def vela(cv, h, T):
    fl = 1 + 0.12 * math.sin(T * 17)
    cv.drawCircle(h[0], h[1] - 70, 340 * fl, rad((h[0], h[1] - 70), 340 * fl, [(255, 200, 110, 0.5), (255, 200, 110, 0.0)]))
    rrect(cv, h[0] - 12, h[1] - 50, 24, 56, 4, fill((250, 244, 226)))
    cv.drawOval(XYWH(h[0] - 9 * fl, h[1] - 86, 18 * fl, 36), fill((255, 190, 60))); cv.drawOval(XYWH(h[0] - 4, h[1] - 72, 8, 18), fill((255, 250, 220)))


def ep09():
    S = []
    TH1 = [0.5, 2.3]

    def night(cv, cam, T, lt, flashes, rain_a=0.55):
        stage(cv, cam, "patio_noche")
        f = flash(lt, flashes)
        if f > 0.5: bolt(cv, 380, int(lt * 3), f)
        return f

    def s1(cv, lt, d, T):  # la lluvia no avisó
        cam = cam_move(lt, d, (675, 1500, 1.15), (700, 1560, 1.4))
        f = night(cv, cam, T, lt, TH1)
        robot(cv, RX, GY, 600, T=T, motor=True, wet=clamp(lt / 2))
        gotera(cv, T); rain(cv, T)
        cv.drawRect(XYWH(0, 0, BW, BH), fill((230, 240, 255), 0.55 * f)); done(cv)
    S.append((0.0, s1))

    def s2(cv, lt, d, T):  # dormía tranquila, pero un trueno la despertó
        tt = A("pero un trueno") - A("camila dormiría") + 0.3
        cam = cam_move(lt, d, (560, 1400, 1.6), (520, 1420, 1.85) if lt < tt else (520, 1420, 1.85)); stage(cv, cam, "pieza_noche")
        if lt < tt:
            cv.save(); cv.translate(640, 1478); cv.rotate(-90)
            Mo.draw_char(cv, CAMILA_PIJAMA, dict(STAND, blink=1, mood="neutral"), 0, 0, 520, 1, T)
            cv.restore()
            rrect(cv, 390, 1436, 400, 150, 40, lin((0, 1436), (0, 1586), [(110, 130, 200), (80, 100, 170)]))
            for k in range(3):
                ph = (T * 0.5 + k / 3) % 1
                text_center(cv, "z", 300 + ph * 80, 1330 - ph * 150, 40 + 30 * ph, (220, 230, 255), None, a=1 - ph, shadow_=False)
        else:
            u = ease((lt - tt) / 0.25)
            Mo.draw_char(cv, CAMILA_PIJAMA, dict(STAND, seat=0.02, lb=(88, 0), lf=(84, 0), lean=lerp(-70, 4, u), ab=(40, 60), af=(120, 40), mood="surprised", look=(0.9, -0.3)),
                         430, 1500, 520, 1, T)
            rrect(cv, 470, 1440, 330, 140, 40, lin((0, 1440), (0, 1580), [(110, 130, 200), (80, 100, 170)]))
            for k in range(3): star(cv, 520 + k * 60, 1150 - k * 40, 30 * max(0, 1 - (lt - tt) * 1.5), 1.0, (255, 240, 170))
        f = flash(lt, [tt])
        cv.drawRect(XYWH(760, 760, 420, 420), fill((230, 240, 255), 0.6 * f))
        cv.drawRect(XYWH(0, 0, BW, BH), fill((230, 240, 255), 0.45 * f)); done(cv)
    S.append((A("camila dormiría"), s2))

    def s3(cv, lt, d, T):  # corre al patio con un paraguas roto: el agua entra por el techo
        cam = cam_move(lt, d, (900, 1560, 1.35), (760, 1600, 1.5))
        f = night(cv, cam, T, lt, [1.6])
        puerta_abierta(cv, 1.0, T)
        robot(cv, RX, GY, 600, T=T, motor=True, wet=1)
        gotera(cv, T)
        x, ph, mv = walker(lt, 0, 1180, 990, d * 0.6, 2.3)
        shade(cv, x, GY)
        p = dict(run(ph), af=(150, 20)) if mv else dict(STAND, af=(150, 20), ab=(60, 60), mood="surprised", look=(-0.9, -0.2), lean=-6)
        ch(cv, CAMILA_PIJAMA, p, x, GY, face=-1, T=T, seed=21, ex=dict(hand_item=paraguas))
        rain(cv, T); cv.drawRect(XYWH(0, 0, BW, BH), fill((230, 240, 255), 0.5 * f)); done(cv)
    S.append((A("corrió"), s3))

    def cables(cv, T):
        for j, col in enumerate(((220, 60, 60), (60, 140, 220), (240, 200, 60))):
            p = skia.Path(); p.moveTo(RX - 30 + j * 30, GY - 300)
            sw = math.sin(T * 2 + j) * 14
            p.cubicTo(RX - 120 + j * 60 + sw, GY - 180, RX - 160 + j * 90 - sw, GY - 60, RX - 190 + j * 130 + sw, GY + 6)
            cv.drawPath(p, stroke(col, 6))

    def s4(cv, lt, d, T):  # el robot empapado, los cables flotando
        cam = cam_move(lt, d, (760, 1640, 1.9), (760, 1700, 2.25))
        f = night(cv, cam, T, lt, [0.9])
        robot(cv, RX, GY, 600, T=T, motor=True, wet=1); cables(cv, T); gotera(cv, T)
        rain(cv, T); cv.drawRect(XYWH(0, 0, BW, BH), fill((230, 240, 255), 0.5 * f)); done(cv)
    S.append((A("el robot estaba"), s4))

    def s5(cv, lt, d, T):  # intenta secarlo con trapos; faltan las pilas y la feria es mañana
        cam = cam_move(lt, d, (700, 1660, 1.65), (680, 1640, 1.85))
        night(cv, cam, T, lt, [])
        robot(cv, RX, GY, 600, T=T, motor=True, wet=1); cables(cv, T)
        w = math.sin(T * 11)
        info = ch(cv, CAMILA_PIJAMA, dict(KNEEL, af=(96 + 14 * w, 10), ab=(80 - 14 * w, 20), look=(0.9, 0.0), mood="worried", tears=1), 570, GY + 30, T=T, seed=21)
        for hnd in (info["hand_f"], info["hand_b"]): rrect(cv, hnd[0] - 6, hnd[1] - 24, 50, 46, 10, fill((240, 236, 220)))
        rain(cv, T, a=0.45); done(cv)
    S.append((A("intentó"), s5))

    def s6(cv, lt, d, T):  # de rodillas, llora en silencio
        cam = cam_move(lt, d, (680, 1660, 1.75), (680, 1600, 1.3))
        night(cv, cam, T, lt, [])
        robot(cv, RX, GY, 600, T=T, motor=True, wet=1); cables(cv, T)
        ch(cv, CAMILA_PIJAMA, breathe(dict(KNEEL, lean=34, head=30, af=(40, 20), ab=(30, 20), look=(0.3, 1.0), mood="sad", tears=1), T), 540, GY + 30, T=T, seed=21)
        rain(cv, T, a=0.4); done(cv)
    S.append((A("camila se quedó"), s6))

    def s7(cv, lt, d, T):  # la abuela le pone una manta: «lo importante es no soltar la aguja»
        cam = cam_move(lt, d, (600, 1620, 1.5), (580, 1560, 1.85))
        night(cv, cam, T, lt, [])
        robot(cv, RX + 60, GY, 600, T=T, motor=True, wet=0.6)
        x, ph, mv = walker(lt, 0, 1100, 760, 1.3, 1.3)
        put = lt > 1.5
        look_up = lt > 2.2
        info = ch(cv, CAMILA_PIJAMA, dict(KNEEL, lean=34 if not look_up else 8, head=30 if not look_up else -10, af=(40, 20), ab=(30, 20), look=(0.9, -0.5) if look_up else (0.3, 1.0),
                                          mood="sad", tears=0 if lt > 4 else 1), 540, GY + 30, T=T, seed=21)
        if put: manta(cv, info)
        shade(cv, x, GY)
        p = walk(ph, amp=0.7, base=dict(STAND, af=(70, 60), mood="kind")) if mv else dict(STAND, lean=10, af=(70, 60), ab=(80, 30) if lt < 2.0 else (30, 30), mood="kind", look=(-0.8, 0.5))
        ch(cv, ROSA, p, x, GY, face=-1, T=T, seed=50, ex=dict(hand_item=lambda c, h: vela(c, h, T)))
        rain(cv, T, a=0.3); done(cv)
    S.append((A("la abuela le puso"), s7))

    def s8(cv, lt, d, T):  # respira y vuelve a tomar el destornillador; amanece
        cam = cam_move(lt, d, (700, 1620, 1.55), (720, 1580, 1.7)); cv.save(); cam.apply(cv)
        u = ease((lt - d * 0.35) / (d * 0.6))
        draw_bg(cv, "patio_noche")
        pa = skia.Paint(); pa.setAlphaf(u); cv.drawImage(E.bg("patio_amanecer"), 0, 0, skia.SamplingOptions(), pa)
        robot(cv, RX, GY, 600, T=T, motor=True, wet=max(0, 0.6 - u))
        w = math.sin(T * 9)
        info = ch(cv, CAMILA_PIJAMA, dict(STAND, af=(92 + 8 * w, 10 * w), ab=(40, 40), look=(0.9, 0.0), mood="determined"), 570, GY, T=T, seed=21, ex=dict(hand_item=screwdriver()))
        manta(cv, info)
        if u < 0.9: rain(cv, T, a=0.3 * (1 - u))
        done(cv)
    S.append((A("camila respiró"), s8))

    def s9(cv, lt, d, T):  # amanece: todo el barrio llega con pilas en las manos
        tb = A("era todo") - A("cuando amaneció")
        cam = cam_move(lt, d, (760, 1620, 1.4), (600, 1600, 1.2)); stage(cv, cam, "patio_amanecer")
        robot(cv, RX + 140, GY, 600, T=T, motor=True)
        happy = lt > tb + 0.4
        shade(cv, 1080, GY); ch(cv, ROSA, dict(CLAP_OPEN if happy else STAND, mood="happy" if happy else "surprised", look=(-0.9, 0)), 1080, GY, face=-1, T=T, seed=50)
        info = ch(cv, CAMILA_PIJAMA, dict(CHEER, air=0.06 * abs(math.sin(T * 8))) if happy else dict(STAND, mood="surprised", look=(-0.9, 0), af=(60, 40)), 760, GY, face=-1, T=T, seed=21,
                  ex=dict(blush=happy))
        for k in range(7):
            x1 = 80 + k * 86; yk = GY + (k % 3) * 40 - 30
            x, ph, mv = walker(lt, tb - 0.9 + k * 0.12, -260 - k * 30, x1, 1.6, 1.5)
            if lt < tb - 0.9: continue
            sp = Mo.NEIGHBORS[k % len(Mo.NEIGHBORS)]
            p = walk(ph, base=dict(STAND, af=(150, 10), mood="happy")) if mv else dict(STAND, af=(150 + 8 * math.sin(T * 6 + k), 10), mood="happy", look=(0.8, 0))
            shade(cv, x, yk)
            ch(cv, sp, p, x, yk, face=1, T=T, seed=100 + k, ex=dict(hand_item=lambda c, h, k=k: battery(c, h[0], h[1] - 44, 1.0, rot=10 * math.sin(T * 5 + k))))
        if happy: sparkles(cv, T, [(200, 1250), (420, 1200), (620, 1260), (300, 1380)], 24)
        done(cv)
    S.append((A("cuando amaneció"), s9))
    texts = [("TORMENTA", 0.3, A("camila dormiría") - 0.1), ("«NO SUELTES LA AGUJA»", A("lo importante"), A("camila respiró") - 0.1),
             ("TODO EL BARRIO", A("era todo"), 54.6)]
    return S, texts


# ============================================================ EPISODIO 10 — El robot que saludó
BATA = [dict(k, shirt=(250, 250, 250), shirt2=(226, 230, 236)) for k in Mo.KIDS]


def mesa_simple(cv, x=1130, top=1760, w=300):
    rrect(cv, x - w / 2, top, w, 22, 5, fill((176, 132, 84)))
    for px in (x - w / 2 + 14, x + w / 2 - 30): cv.drawRect(XYWH(px, top + 20, 16, GY - top - 20), fill((130, 96, 60)))


def jurado(cv, T, lt, writing=True, mood="focused", xs=(120, 260, 400), y=GY - 20):
    for k, x in enumerate(xs):
        sp = (JUEZ, JUEZA, Mo.COACH)[k] if k < 2 else dict(JUEZ, hair_col=(150, 110, 60), shirt=(70, 110, 90), shirt2=(54, 90, 70), glasses=None)
        w = math.sin(T * 16 + k) if writing else 0
        p = dict(STAND, ab=(40, 80), af=(50 + 4 * w, 70 + 8 * w), head=12 if writing else -4, look=(0.7, 0.8) if writing else (0.9, -0.1), mood=mood)

        def clip(c, h, k=k):
            rrect(c, h[0] - 34, h[1] - 10, 68, 86, 6, fill((120, 84, 54))); rrect(c, h[0] - 28, h[1] - 2, 56, 72, 3, fill((250, 250, 244)))
            for j in range(4): c.drawLine(h[0] - 20, h[1] + 10 + j * 14, h[0] + 16, h[1] + 10 + j * 14, stroke((120, 120, 130), 3))
        shade(cv, x, y); ch(cv, sp, p, x, y, face=1, T=T, seed=60 + k, ex=dict(back_hand_item=clip))


def ep10():
    S = []

    def s1(cv, lt, d, T):  # el robot levanta la mano y el jurado deja de escribir
        cam = cam_move(lt, d, (520, 1600, 1.4), (560, 1560, 1.55)); stage(cv, cam, "feria_ciencias")
        up = ease((lt - 0.3) / 0.7)
        jurado(cv, T, lt, writing=lt < 1.0, mood="focused" if lt < 1.0 else "surprised")
        robot(cv, 760, GY, 600, eyes=1, arm=up, wave=up, heart=1, motor=True, T=T, face=-1)
        if lt > 1.0:
            for k, x in enumerate((120, 260, 400)): text_center(cv, "!", x + 20, 1270 - 10 * math.sin(T * 6 + k), 90, (255, 200, 61), (17, 17, 17), 0.09, a=clamp((lt - 1.0 - k * 0.1) / 0.2))
        done(cv)
    S.append((0.0, s1))

    def s2(cv, lt, d, T):  # la feria llena de proyectos relucientes
        cam = cam_move(lt, d, (430, 1380, 1.55), (920, 1380, 1.55)); stage(cv, cam, "feria_ciencias")
        for k, x in enumerate((170, 510, 850, 1190)):
            j = math.sin(T * 3 + k)
            p = dict(STAND, af=(120 + 20 * j, 10), mood="happy") if k % 2 == 0 else dict(HIPS, head=-4)
            shade(cv, x - 90, 1680); ch(cv, BATA[k], p, x - 90, 1680, face=1, T=T, seed=70 + k)
        sparkles(cv, T, [(170, 1240), (510, 1260), (850, 1220), (1190, 1250), (330, 1300), (700, 1330), (1020, 1300)], 22)
        done(cv)
    S.append((A("la feria de ciencias"), s2))

    def s3(cv, lt, d, T):  # en una esquina, Camila coloca su robot junto a una mesa sencilla
        cam = cam_move(lt, d, (860, 1620, 1.3), (880, 1600, 1.45)); stage(cv, cam, "feria_ciencias")
        for k, (x, sp) in enumerate(((330, ROSA), (190, Mo.NEIGHBORS[0]), (470, Mo.NEIGHBORS[3]))):
            ch(cv, sp, dict(STAND, ab=(40, 80), af=(45, 85), mood="worried" if k == 0 else "kind", look=(0.9, 0)), x, 1700, face=1, T=T, seed=50 + k)
        mesa_simple(cv)
        xr = lerp(700, 800, ease(lt / (d * 0.6)))
        robot(cv, xr, GY, 600, T=T, motor=True, step=(lt * 1.2) if lt < d * 0.6 else None)
        j = math.sin(T * 9)
        p = dict(STAND, af=(80, 10), ab=(70, 20), lean=8, look=(0.9, 0.2), mood="worried") if lt < d * 0.6 else dict(STAND, ab=(40, 90), af=(45, 95), head=6 * j, look=(0.6 * j, 0), mood="worried")
        shade(cv, xr - 190, GY); ch(cv, CAMILA, p, xr - 190, GY, T=T, seed=21)
        done(cv)
    S.append((A("en una esquina"), s3))

    def s4(cv, lt, d, T):  # respira y aprieta el botón
        tb = A("apretó") - A("respiró") + 0.25
        cv.drawRect(skia.Rect.MakeWH(W, H), lin((0, 0), (0, H), [(210, 224, 240), (150, 170, 200)]))
        cv.drawCircle(W / 2, 1000, 700, rad((W / 2, 1000), 700, [(255, 255, 255, 0.5), (255, 255, 255, 0.0)]))
        rrect(cv, 240, 760, 600, 560, 50, lin((0, 760), (0, 1320), [(196, 202, 212), (140, 146, 158)])); rrect(cv, 270, 790, 540, 500, 36, stroke((110, 116, 128), 8))
        for k in range(4): cv.drawCircle(300 + (k % 2) * 480, 820 + (k // 2) * 440, 12, fill((90, 96, 108)))
        press = ease((lt - tb) / 0.15) if lt >= tb else 0
        cv.drawCircle(540, 1060, 170, fill((90, 30, 30))); cv.drawCircle(540, 1040 + 20 * press, 150, rad((500, 990 + 20 * press), 220, [(255, 110, 100), (214, 40, 40), (150, 20, 24)]))
        text_center(cv, "ON", 540, 1040 + 20 * press, 90, (255, 240, 230), None, shadow_=False)
        u = ease(lt / max(0.3, tb))
        fx_, fy_ = lerp(860, 600, u), lerp(1700, 1140 + 20 * press, u)
        cv.drawLine(fx_ + 420, fy_ + 520, fx_, fy_, stroke(BLACK, 46)); cv.drawCircle(fx_, fy_, 60, fill(BLACK))
        if lt >= tb:
            for k in range(3):
                rr = 170 + ((lt - tb) * 500 + k * 110) % 420
                cv.drawCircle(540, 1060, rr, stroke((110, 200, 255), 10, max(0, 1 - (rr - 170) / 420)))
    S.append((A("respiró"), s4))

    def s5(cv, lt, d, T):  # se enciende, da tres pasos, toma la pelota y la deja en la mesa
        t0 = A("las tapas"); ta = A("el robot dio") - t0; tk = A("tomó") - t0; tl = A("y la dejó") - t0
        cam = cam_move(lt, d, (760, 1620, 1.35), (860, 1620, 1.5)); stage(cv, cam, "feria_ciencias")
        jurado(cv, T, lt, writing=lt < ta, mood="focused" if lt < ta else "surprised", xs=(60, 175, 290), y=GY - 40)
        mesa_simple(cv)
        rrect(cv, 870, 1680, 70, GY - 1680, 6, fill((70, 130, 220)))      # pedestal de la pelota
        shade(cv, 400, GY + 50); ch(cv, CAMILA, dict(STAND, ab=(40, 90), af=(45, 95), mood="worried" if lt < tl else "happy", look=(0.9, 0)), 400, GY + 50, T=T, seed=21)
        walk1 = clamp((lt - ta) / max(0.3, tk - ta - 0.3)); walk2 = clamp((lt - tk - 0.9) / 0.6)
        xr = lerp(500, 640, walk1) + 120 * walk2
        stepping = (0 < walk1 < 1) or (0 < walk2 < 1)
        if lt < tk: arm = 0.3 * ease((lt - tk + 0.3) / 0.3)
        else: arm = lerp(0.3, 0.5, ease((lt - tk - 0.3) / 0.5))
        r = robot(cv, xr, GY, 600, eyes=ease(lt / 0.4), arm=arm, heart=1, motor=True, T=T, step=(walk1 * 2 + walk2) if stepping else None)
        hand = r["hand"]
        tr = max(tl + 0.3, tk + 1.6)        # suelta la pelota cuando ya está sobre la mesa
        if lt < tk + 0.2: b = (905, 1654)
        elif lt < tr: b = (hand[0] + 6, hand[1] + 16)
        else:
            u = clamp((lt - tr) / 0.35); b = (hand[0] + 6, lerp(hand[1] + 16, 1734, u * u))
            if u >= 1: b = (hand[0] + 6, 1734 - abs(math.sin((lt - tr - 0.35) * 9)) * 30 * math.exp(-(lt - tr - 0.35) * 3))
        cv.drawCircle(b[0], b[1], 26, rad((b[0] - 8, b[1] - 8), 36, [(255, 150, 140), (220, 60, 60), (150, 30, 34)]))
        done(cv)
    S.append((A("las tapas"), s5))

    def s6(cv, lt, d, T):  # luego levanta la mano y saluda
        cam = cam_move(lt, d, (560, 1580, 1.45), (600, 1540, 1.65)); stage(cv, cam, "feria_ciencias")
        jurado(cv, T, lt, writing=False, mood="surprised", xs=(120, 260, 400))
        mesa_simple(cv)
        cv.drawCircle(1066, 1734, 26, rad((1058, 1726), 36, [(255, 150, 140), (220, 60, 60), (150, 30, 34)]))
        up = ease(lt / 0.6)
        robot(cv, 760, GY, 600, eyes=1, arm=up, wave=up, heart=1, motor=True, T=T, face=-1)
        sparkles(cv, T, [(600, 1280), (900, 1300), (760, 1180)], 22)
        done(cv)
    S.append((A("luego levantó"), s6))

    def s7(cv, lt, d, T):  # un juez pregunta: ¿de qué está hecho?
        cam = cam_move(lt, d, (520, 1500, 1.7), (540, 1480, 1.9)); stage(cv, cam, "feria_ciencias")
        tq = A("de qué") - A("un juez")
        robot(cv, 900, GY, 600, eyes=1, heart=1, motor=True, T=T, face=-1)
        j = math.sin(T * 8)
        shade(cv, 330, GY); info = ch(cv, JUEZ, dict(STAND, lean=8, af=(70 + 8 * j, 60), ab=(30, 60), look=(0.9, 0.2), mood="kind"), 330, GY, face=1, T=T, seed=60)
        shade(cv, 620, GY); ch(cv, CAMILA, dict(STAND, look=(-0.9, -0.4), mood="neutral", ab=(40, 90), af=(45, 95)), 620, GY, face=-1, T=T, seed=21)
        if lt > tq: text_center(cv, "?", info["head"][0] + 150, info["head"][1] - 130 - 10 * math.sin(T * 4), 150, (255, 200, 61), (17, 17, 17), 0.08, a=clamp((lt - tq) / 0.25))
        done(cv)
    S.append((A("un juez"), s7))

    def s8(cv, lt, d, T):  # «de chatarra, de pilas del barrio y del motor de la máquina de mi abuela»
        t0 = A("camila sonrió")
        cam = cam_move(lt, d, (700, 1520, 1.6), (720, 1480, 1.8)); stage(cv, cam, "feria_ciencias")
        robot(cv, 880, GY, 600, eyes=1, heart=1, motor=True, T=T, face=-1, arm_b=0.2)
        shade(cv, 600, GY); ch(cv, CAMILA, dict(STAND, af=(95, 10), ab=(-30, 110), head=-6, look=(-0.6, -0.3), mood="happy"), 600, GY, face=1, T=T, seed=21, ex=dict(blush=True))
        icons = ((A("de chatarra") - t0, 520), (A("de pilas") - t0, 720), (A("y del motor") - t0, 920))
        for k, (tt, ix) in enumerate(icons):
            if lt < tt: continue
            s_ = 0.6 + 0.4 * ease_out((lt - tt) / 0.25); iy = 1130 - 10 * math.sin(T * 3 + k)
            cv.drawCircle(ix, iy, 96 * s_, fill((255, 255, 255), 0.95)); cv.drawCircle(ix, iy, 96 * s_, stroke((255, 200, 61), 10))
            if k == 0: rrect(cv, ix - 34 * s_, iy - 50 * s_, 68 * s_, 100 * s_, 10, lin((ix - 34, 0), (ix + 34, 0), [(170, 176, 188), (220, 226, 236), (140, 146, 158)])); cv.drawRect(XYWH(ix - 34 * s_, iy - 30 * s_, 68 * s_, 24 * s_), fill((204, 64, 52)))
            elif k == 1: battery(cv, ix, iy, 1.25 * s_, rot=12)
            else: motor_item(cv, ix - 12, iy, 0.9 * s_, T=T)
        done(cv)
    S.append((A("camila sonrió"), s8))

    def s9(cv, lt, d, T):  # anuncian el Premio a la Creatividad
        cam = cam_move(lt, d, (675, 1450, 1.2), (675, 1150, 1.45)); stage(cv, cam, "escenario")
        sh_ = ((lt * 0.9) % 1.6) / 1.6
        cv.save(); cv.clipRect(XYWH(150, 420, 1050, 250)); cv.drawPath(path([(100 + sh_ * 1200, 420), (180 + sh_ * 1200, 420), (120 + sh_ * 1200, 670), (40 + sh_ * 1200, 670)]), fill((255, 255, 255), 0.35)); cv.restore()
        sw = math.sin(T * 1.5) * 200
        cv.drawPath(path([(330, 0), (390, 0), (675 + sw + 200, 1900), (675 + sw - 200, 1900)]), fill((255, 244, 200), 0.1))
        j = math.sin(T * 7)
        info = ch(cv, JUEZA, dict(STAND, af=(150, 10), ab=(30, 150), mood="happy", head=-4), 675, 1900, S=680, face=1, T=T, seed=61, persp_on=False,
                  ex=dict(hand_item=lambda c, h: trophy(c, h[0], h[1] - 6, 1.0)))
        sparkles(cv, T, [(info["hand_f"][0] + 50, info["hand_f"][1] - 110), (info["hand_f"][0] - 60, info["hand_f"][1] - 60)], 24)
        done(cv)
    S.append((A("al final"), s9))

    def s10(cv, lt, d, T):  # sube al escenario, mira a la abuela y levanta el trofeo
        t0 = A("camila subió"); t1 = A("miró a la abuela") - t0; t2 = A("y levantó") - t0
        if t1 <= lt < t2:   # la abuela y los vecinos entre el público
            cam = cam_move(lt - t1, t2 - t1, (620, 1560, 1.7), (640, 1540, 1.9)); stage(cv, cam, "feria_ciencias")
            cv.drawRect(XYWH(0, 0, BW, BH), fill((30, 20, 60), 0.35))
            cl = (math.sin(T * 14) + 1) / 2
            for k, x in enumerate((260, 420, 860, 1020)):
                ch(cv, Mo.NEIGHBORS[k], mix(CLAP_OPEN, CLAP_SHUT, (math.sin(T * 13 + k) + 1) / 2), x, GY - 60 + (k % 2) * 30, face=1 if x < 640 else -1, T=T, seed=100 + k)
            shade(cv, 640, GY); ch(cv, ROSA, dict(mix(CLAP_OPEN, CLAP_SHUT, cl), tears=1, mood="happy", head=-6, look=(0.2, -0.6)), 640, GY, face=1, T=T, seed=50)
            done(cv); return
        cam = cam_move(lt, d, (640, 1520, 1.3), (675, 1600, 1.5)); stage(cv, cam, "escenario")
        shade(cv, 930, 1880, persp_on=False)
        ch(cv, JUEZA, mix(CLAP_OPEN, CLAP_SHUT, (math.sin(T * 12) + 1) / 2) if lt > 1.6 else dict(STAND, af=(120, 20), mood="happy"), 1000, 1900, S=680, face=-1, T=T, seed=61, persp_on=False,
           ex=dict(hand_item=(lambda c, h: trophy(c, h[0], h[1] - 6, 1.0)) if lt <= 1.6 else None))
        if lt >= t2: robot(cv, 360, 1900, 600, eyes=1, arm=1, wave=1, heart=1, motor=True, T=T, face=-1)
        x, ph, mv = walker(lt, 0, 180, 700, 1.5, 1.6)
        if lt < t1:
            p = walk(ph, base=dict(STAND, mood="happy")) if mv else dict(HOLD, mood="happy", look=(0.2, -0.3))
            info = ch(cv, CAMILA, p, x, 1900, S=680, face=1, T=T, seed=21, persp_on=False, ex=dict(blush=True))
            if lt > 1.6: trophy(cv, info["hand_f"][0] + 10, info["hand_f"][1], 1.0)
        else:
            up = ease((lt - t2) / 0.5); hop = 0.05 * abs(math.sin(T * 7)) * up
            info = ch(cv, CAMILA, dict(mix(HOLD, ARMS_UP, up), air=hop, mood="happy", head=-8, look=(0.2, -0.6)), 700, 1900, S=680, face=1, T=T, seed=21, persp_on=False, ex=dict(blush=True))
            hx, hy = (info["hand_f"][0] + info["hand_b"][0]) / 2, min(info["hand_f"][1], info["hand_b"][1])
            cv.drawCircle(hx, hy - 60, 260, rad((hx, hy - 60), 260, [(255, 230, 140, 0.5 * up), (255, 230, 140, 0.0)]))
            trophy(cv, hx, hy + 4, 1.25)
            confetti(cv, T, t0 + t2)
        done(cv)
    S.append((A("camila subió"), s10))

    def s11(cv, lt, d, T):  # avance: una cocina, mucha harina y un concurso
        cv.drawRect(skia.Rect.MakeWH(W, H), lin((0, 0), (0, H), [(40, 26, 20), (12, 8, 8)]))
        cv.drawCircle(W / 2, 760, 420, rad((W / 2, 760), 420, [(255, 190, 90, 0.4), (255, 190, 90, 0)]))
        for k in range(5):   # ollas y sartenes colgando
            px = 140 + k * 200; sw = math.sin(T * 1.5 + k) * 6
            cv.drawLine(px, 0, px + sw, 300 + (k % 2) * 60, stroke((90, 80, 76), 5))
            if k % 2: cv.drawCircle(px + sw, 380 + (k % 2) * 60, 70, fill((70, 62, 60))); cv.drawRect(XYWH(px + sw - 8, 440, 16, 110), fill((70, 62, 60)))
            else: rrect(cv, px + sw - 70, 300, 140, 100, 20, fill((84, 74, 70)))
        cv.drawRect(XYWH(0, 1500, W, 60), fill((70, 50, 40))); cv.drawRect(XYWH(0, 1560, W, 400), fill((40, 28, 24)))
        u = ease(lt / 1.5)
        cv.saveLayer(None, None)
        joaquin = dict(hair="short", hair_col=(60, 40, 24), shirt=(250, 250, 250), shirt2=(226, 226, 226), pants=(40, 50, 90), apron=(70, 120, 200), shoe=(60, 60, 60), h=1.12)
        info = Mo.draw_char(cv, joaquin, dict(STAND, af=(100, 40), mood="determined", look=(0.6, 0)), W / 2, 1500, 760, 1, T)
        hc, hr = info["head"], info["hr"]
        rrect(cv, hc[0] - hr * 0.8, hc[1] - hr * 1.5, hr * 1.6, hr * 0.7, 8, fill((250, 250, 250)))
        for k in range(3): cv.drawCircle(hc[0] - hr * 0.6 + k * hr * 0.6, hc[1] - hr * 1.6, hr * 0.55, fill((250, 250, 250)))
        p = skia.Paint(Color=C((14, 10, 12), 1 - 0.75 * u)); p.setBlendMode(skia.BlendMode.kSrcATop); cv.drawPaint(p)
        cv.restore()
        rnd = random.Random(6)
        for k in range(70):   # harina en el aire
            x = rnd.uniform(0, W) + math.sin(T * 0.8 + k) * 30; y = (rnd.uniform(0, 1500) + T * rnd.uniform(20, 70)) % 1500
            cv.drawCircle(x, y, rnd.uniform(2, 6), fill((255, 250, 240), 0.5 * u))
    S.append((A("la próxima"), s11))
    # «PREMIO A LA CREATIVIDAD» va en la pancarta del escenario (plano s9)
    texts = [("«DE CHATARRA»", A("de chatarra"), A("al final") - 0.1), ("EL BARRIO GANÓ", A("y levantó") + 0.3, A("la próxima") - 0.1)]
    return S, texts
