"""Serie interactiva «20 días» de Brote — Día 1: El aviso. Usa los ayudantes de episodios.py."""
import math, random, sys
import skia
from motor import *
import motor as Mo
import escenarios as E
import escenarios_c as EC
import escenarios_d as ED
from escenarios import Cam, cam_move, draw_bg, BW, BH, particles, paper

H_ = sys.modules["__main__"]
XYWH = skia.Rect.MakeXYWH
AMA = (255, 200, 61)
GREEN, RED = (90, 220, 120), (255, 90, 80)


def A(s, n=0): return H_.at(s, n)
def stage(cv, cam, name): cv.save(); cam.apply(cv); draw_bg(cv, name)
def done(cv): cv.restore()
def ch(*a, **k): return H_.ch(*a, **k)
def shade(*a, **k): return H_.shade(*a, **k)
def walker(*a, **k): return H_.walker(*a, **k)


# ============================================================ iconos
def heart(cv, x, y, r, col, a=1.0, outline=False):
    p = skia.Path()
    p.addCircle(x - r * 0.5, y - r * 0.25, r * 0.55); p.addCircle(x + r * 0.5, y - r * 0.25, r * 0.55)
    p.addPath(path([(x - r * 1.02, y - r * 0.05), (x + r * 1.02, y - r * 0.05), (x, y + r * 1.0)]))
    if outline: cv.drawPath(p, fill((255, 255, 255), 0.18 * a))
    else: cv.drawPath(p, fill(col, a))


def bolt(cv, x, y, r, col, a=1.0, dim=False):
    pts = [(x + r * 0.25, y - r), (x - r * 0.6, y + r * 0.15), (x - r * 0.05, y + r * 0.15), (x - r * 0.3, y + r), (x + r * 0.6, y - r * 0.2), (x + r * 0.05, y - r * 0.2)]
    cv.drawPath(path(pts), fill((255, 255, 255), 0.18 * a) if dim else fill(col, a))


def coin(cv, x, y, r, a=1.0):
    cv.drawCircle(x, y, r, rad((x - r * 0.3, y - r * 0.3), r * 1.4, [(255, 236, 140, a), (236, 170, 40, a), (190, 120, 20, a)], [0, 0.6, 1]))
    cv.drawCircle(x, y, r * 0.78, stroke((170, 110, 20), max(1.5, r * 0.08), a))
    f = skia.Font(typeface("Inter-Black"), r * 1.2); w = f.measureText("$")
    cv.drawString("$", x - w / 2, y + r * 0.42, f, fill((150, 90, 10), a))


def money(n): return "$" + f"{int(n):,}".replace(",", ".")


# ============================================================ HUD del juego (siempre arriba a la izquierda)
STATE = dict(day=1, cash=0.0, goal=1500000, trust=3, energy=5)


def hud(cv, T, flash_cash=0.0, pulse_trust=0.0, a=1.0):
    st = STATE
    x0, y0, w, h = 34, 64, 470, 286
    cv.drawRRect(skia.RRect.MakeRectXY(XYWH(x0, y0 + 6, w, h), 28, 28), fill((0, 0, 0), 0.35 * a, blur=10))
    cv.drawRRect(skia.RRect.MakeRectXY(XYWH(x0, y0, w, h), 28, 28), fill((14, 14, 20), 0.72 * a))
    cv.drawRRect(skia.RRect.MakeRectXY(XYWH(x0, y0, w, h), 28, 28), stroke(AMA, 3, 0.75 * a))
    f = skia.Font(typeface("Inter-Black"), 44)
    cv.drawString(f"DÍA {st['day']}", x0 + 26, y0 + 58, f, fill(AMA, a))
    dw = f.measureText(f"DÍA {st['day']}")
    cv.drawString("de 20", x0 + 36 + dw, y0 + 58, skia.Font(typeface("Inter-Bold"), 32), fill((255, 255, 255), 0.85 * a))
    # dinero
    coin(cv, x0 + 46, y0 + 104, 20, a)
    cc = tuple(int(lerp(c1, c2, flash_cash)) for c1, c2 in zip((255, 255, 255), RED))
    fm = skia.Font(typeface("Inter-Black"), 38); ms = money(st["cash"])
    cv.drawString(ms, x0 + 80, y0 + 118, fm, fill(cc, a))
    cv.drawString("/ " + money(st["goal"]), x0 + 90 + fm.measureText(ms), y0 + 116, skia.Font(typeface("Inter-Bold"), 26), fill((200, 200, 210), 0.9 * a))
    bx, by, bw = x0 + 26, y0 + 136, w - 52
    cv.drawRRect(skia.RRect.MakeRectXY(XYWH(bx, by, bw, 14), 7, 7), fill((255, 255, 255), 0.15 * a))
    pr = clamp(st["cash"] / st["goal"])
    if pr > 0: cv.drawRRect(skia.RRect.MakeRectXY(XYWH(bx, by, bw * pr, 14), 7, 7), fill(GREEN, a))
    # confianza y energía
    s_ = 1 + 0.25 * pulse_trust * abs(math.sin(T * 9))
    for k in range(5):
        heart(cv, x0 + 46 + k * 48, y0 + 190, 16 * (s_ if k < st["trust"] else 1), (255, 70, 90), a, outline=k >= st["trust"])
        bolt(cv, x0 + 46 + k * 48, y0 + 240, 18, AMA, a, dim=k >= st["energy"])
    cv.drawString("CONFIANZA", x0 + 290, y0 + 198, skia.Font(typeface("Inter-Bold"), 20), fill((220, 220, 230), 0.8 * a))
    cv.drawString("ENERGÍA", x0 + 290, y0 + 248, skia.Font(typeface("Inter-Bold"), 20), fill((220, 220, 230), 0.8 * a))
    # mini mapa de ruta: 20 puntos
    my = y0 + h - 18
    cv.drawLine(x0 + 30, my, x0 + w - 30, my, stroke((255, 255, 255), 2, 0.25 * a))
    for k in range(20):
        px = x0 + 30 + k * (w - 60) / 19
        if k < st["day"]:
            if k == st["day"] - 1: cv.drawCircle(px, my, 13, fill(AMA, (0.25 + 0.2 * math.sin(T * 5)) * a))
            cv.drawCircle(px, my, 6.5, fill(AMA, a))
        else:
            cv.drawCircle(px, my, 4.5, fill((255, 255, 255), 0.35 * a))
    cv.drawCircle(x0 + w - 30, my, 9, stroke((255, 255, 255), 2.5, 0.5 * a))


# ============================================================ utilería
def aviso(cv, x, y, s=1.0, rot=-3, a=1.0):
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s, s)
    cv.drawRect(XYWH(-150 + 8, -200 + 12, 300, 400), fill((0, 0, 0), 0.3 * a, blur=10))
    cv.drawRect(XYWH(-150, -200, 300, 400), fill((252, 250, 240), a))
    cv.drawRect(XYWH(-150, -200, 300, 82), fill((196, 30, 36), a))
    text_center(cv, "AVISO", 0, -160, 58, (255, 255, 255), None, a=a, shadow_=False)
    text_center(cv, "$1.500.000", 0, -70, 56, (30, 30, 34), None, a=a, shadow_=False)
    text_center(cv, "EN 20 DÍAS", 0, 0, 46, (196, 30, 36), None, a=a, shadow_=False)
    text_center(cv, "O SE CIERRA", 0, 70, 46, (30, 30, 34), None, a=a, shadow_=False)
    cv.drawLine(-110, 128, 110, 128, stroke((60, 60, 70), 2, a))
    text_center(cv, "Sr. Barros", 50, 160, 30, (60, 60, 90), None, font="Inter-SemiBoldItalic", a=a, shadow_=False)
    for (tx, ty) in ((-150, -200), (150, -200)):
        cv.drawCircle(tx + (12 if tx < 0 else -12), ty + 12, 9, fill((200, 40, 40), a))
    cv.restore()


def carpeta(cv, h):
    cv.save(); cv.translate(h[0], h[1]); cv.rotate(12)
    rrect(cv, -16, -10, 90, 118, 6, fill((40, 60, 110))); cv.drawRect(XYWH(-8, -2, 74, 102), fill((250, 250, 244)))
    cv.restore()


def billetes(cv, h, n=4, T=0.0):
    for k in range(n):
        cv.save(); cv.translate(h[0], h[1] - 6); cv.rotate(-30 + k * 16 + 3 * math.sin(T * 4 + k))
        rrect(cv, 0, -16, 92, 34, 4, fill((96, 170, 120))); rrect(cv, 6, -10, 80, 22, 3, stroke((40, 110, 70), 3))
        cv.drawCircle(46, 1, 8, fill((40, 110, 70)))
        cv.restore()


def telefono(cv, h):
    cv.save(); cv.translate(h[0], h[1] - 10); cv.rotate(-8)
    rrect(cv, -22, -76, 50, 92, 9, fill((24, 24, 30))); cv.drawRect(XYWH(-16, -68, 38, 72), fill((120, 200, 255)))
    cv.drawCircle(14, -60, 5, fill((255, 60, 60)))
    cv.restore()


def receta(cv, h, T):
    cv.save(); cv.translate(h[0] + 20, h[1] - 60); cv.rotate(-6 + 2 * math.sin(T * 2))
    cv.drawRect(XYWH(-70, -90, 150, 180), fill((0, 0, 0), 0.25, blur=6))
    cv.drawRect(XYWH(-74, -96, 150, 180), fill((246, 232, 196)))
    text_center(cv, "RECETA", 0, -64, 24, (150, 40, 36), None, font="Inter-Black", shadow_=False)
    text_center(cv, "de la abuela", 0, -36, 18, (120, 80, 50), None, font="Inter-SemiBoldItalic", shadow_=False)
    for k in range(5): cv.drawLine(-54, -6 + k * 18, 50 - (k % 2) * 20, -6 + k * 18, stroke((120, 90, 60), 3, 0.7))
    cv.restore()


def masa(cv, x, y, T, k=1.0):
    sq = 1 + 0.08 * math.sin(T * 6) * k
    cv.drawOval(XYWH(x - 90 * sq, y - 44 / sq, 180 * sq, 60 / sq), rad((x - 20, y - 30), 120, [(255, 246, 226), (238, 222, 190), (210, 190, 156)]))


def polilla(cv, x, y, T):
    f = abs(math.sin(T * 30))
    for sx in (-1, 1):
        cv.drawOval(XYWH(x + sx * (4 + 16 * f) - 12, y - 10, 24, 18 * (0.5 + 0.5 * f)), fill((150, 140, 120)))
    cv.drawOval(XYWH(x - 5, y - 10, 10, 22), fill((90, 80, 70)))


def vineta(cv, rect, bgname, center, z, draw, T):
    """Mini escena dentro de una tarjeta: un trozo del escenario + personajes."""
    x, y, w, h = rect
    cv.save()
    cv.clipRRect(skia.RRect.MakeRectXY(XYWH(x, y, w, h), 22, 22), skia.ClipOp.kIntersect, True)
    cv.translate(x + w / 2, y + h / 2); cv.scale(z, z); cv.translate(-center[0], -center[1])
    cv.drawImage(E.bg(bgname), 0, 0)
    draw(cv, T)
    cv.restore()


def effect_chip(cv, x, y, kind, txt, good):
    col = GREEN if good else RED
    tw = skia.Font(typeface("Inter-Black"), 36).measureText(txt)
    cv.drawRRect(skia.RRect.MakeRectXY(XYWH(x, y - 30, tw + 78, 56), 28, 28), fill((14, 14, 20), 0.85))
    cv.drawRRect(skia.RRect.MakeRectXY(XYWH(x, y - 30, tw + 78, 56), 28, 28), stroke(col, 3))
    if kind == "$": coin(cv, x + 30, y - 2, 17)
    elif kind == "h": heart(cv, x + 30, y - 4, 15, (255, 70, 90))
    else: bolt(cv, x + 30, y - 2, 18, AMA)
    cv.drawString(txt, x + 58, y + 12, skia.Font(typeface("Inter-Black"), 36), fill(col))
    return tw + 92


def decision(cv, lt, d, T, num, pregunta, opts, t_a, t_b, bgname="espiga_interior"):
    """Pantalla de decisión: dos tarjetas A/B con mini escena animada, efectos y cuenta regresiva."""
    cv.save(); Cam(675, 1500, 1.1).apply(cv); draw_bg(cv, bgname); cv.restore()
    cv.drawRect(XYWH(0, 0, W, H), fill((10, 10, 18), 0.62))
    intro = ease_out(lt / 0.35)
    # cabecera
    cv.save(); cv.translate(0, (1 - intro) * -60)
    cv.drawRRect(skia.RRect.MakeRectXY(XYWH(60, 378, W - 120, 120), 24, 24), fill(AMA, intro))
    text_center(cv, f"DECISIÓN {num}", W / 2, 412, 34, (40, 30, 10), None, a=intro, shadow_=False)
    f = skia.Font(typeface("Inter-Black"), 50); fit = min(1, (W - 180) / f.measureText(pregunta))
    text_center(cv, pregunta, W / 2, 462, 50 * fit, (20, 20, 24), None, a=intro, shadow_=False)
    cv.restore()
    # cuenta regresiva
    rem = clamp(1 - lt / d)
    cv.drawCircle(W - 120, 300, 46, fill((14, 14, 20), 0.85))
    cv.drawArc(XYWH(W - 160, 260, 80, 80), -90, 360 * rem, False, stroke(RED if rem < 0.3 else AMA, 9))
    text_center(cv, str(int(math.ceil(rem * d))), W - 120, 296, 38, (255, 255, 255), None, shadow_=False)
    for i, (op, ty, ts) in enumerate(((opts[0], 528, t_a), (opts[1], 918, t_b))):
        a = ease_out((lt - 0.15 - i * 0.18) / 0.35)
        if a <= 0: continue
        act = clamp((lt - ts) / 0.25) * (1 - clamp((lt - (t_b if i == 0 else d + 9)) / 0.25)) if lt >= ts else 0.0
        sc = 0.94 + 0.06 * a + 0.03 * act
        cv.save(); cv.translate(W / 2, ty + 180); cv.scale(sc, sc); cv.translate(-W / 2, -(ty + 180))
        cv.translate((1 - a) * (-W if i == 0 else W), 0)
        cv.drawRRect(skia.RRect.MakeRectXY(XYWH(56, ty + 8, W - 112, 360), 30, 30), fill((0, 0, 0), 0.4, blur=14))
        cv.drawRRect(skia.RRect.MakeRectXY(XYWH(50, ty, W - 100, 360), 30, 30), fill((250, 248, 242)))
        border = AMA if act > 0.5 else (230, 226, 216)
        cv.drawRRect(skia.RRect.MakeRectXY(XYWH(50, ty, W - 100, 360), 30, 30), stroke(border, 8 if act > 0.5 else 3))
        vineta(cv, (66, ty + 16, 420, 328), op["bg"], op["center"], op["z"], op["draw"], T)
        # clave grande
        kc = (40, 110, 220) if op["key"].endswith("A") else (220, 70, 60)
        cv.drawRRect(skia.RRect.MakeRectXY(XYWH(510, ty + 26, 150, 96), 22, 22), fill(kc))
        text_center(cv, op["key"], 585, ty + 72, 70, (255, 255, 255), None, shadow_=False)
        f2 = skia.Font(typeface("Inter-Black"), 44)
        yy = ty + 168
        for ln in op["title"]:
            fit2 = min(1, 470 / f2.measureText(ln))
            cv.drawString(ln, 510, yy, skia.Font(typeface("Inter-Black"), 44 * fit2), fill((24, 24, 30))); yy += 50
        ex = 506
        for (k_, t_, g_) in op["fx"]:
            ex += effect_chip(cv, ex, ty + 300, k_, t_, g_)
        if act > 0.5:
            sparkle_pts = [(70, ty + 20), (W - 70, ty + 20), (W - 90, ty + 350)]
            for j, (sx, sy) in enumerate(sparkle_pts):
                r = 22 * max(0, math.sin(T * 6 + j * 2))
                cv.drawLine(sx - r, sy, sx + r, sy, stroke((255, 255, 255), 5)); cv.drawLine(sx, sy - r, sx, sy + r, stroke((255, 255, 255), 5))
        cv.restore()


# ============================================================ DÍA 1 — El aviso
def ep11():
    H_.SUB_COLOR = AMA; H_.KEY_Y = 470; H_.FADE_IN = False
    S = []
    T_CERO = A("cero pesos"); T_TI = A("y te tiene") if True else 0

    def overlay(cv, T):
        flash = clamp(1 - abs(T - T_CERO - 0.4) / 0.9)
        hud(cv, T, flash_cash=flash, pulse_trust=clamp(1 - abs(T - A("a ti") - 0.3) / 0.8))
    H_.OVERLAY = overlay

    # 1. gancho: el aviso golpea la puerta; Mateo lo lee y mira a cámara
    def s1(cv, lt, d, T):
        t2 = A("y tú")
        if lt < t2 - 0.2:
            cam = cam_move(lt, t2, (880, 1420, 2.05), (840, 1460, 1.95))
        else:
            cam = cam_move(lt - t2, d - t2, (820, 1470, 1.85), (780, 1440, 2.05))
        cam.cx += math.sin(T * 60) * 16 * max(0, 1 - lt / 0.45); cam.cy += math.cos(T * 47) * 12 * max(0, 1 - lt / 0.45)
        stage(cv, cam, "espiga_calle")
        slap = ease_out(lt / 0.16)
        aviso(cv, 900, lerp(1300, 1340, slap), lerp(0.8, 0.62, slap), rot=lerp(-12, -3, slap))
        if lt < 0.45:   # la mano del señor Barros
            hx = lerp(1010, 990, slap)
            cv.drawLine(hx + 220, 1560, hx + 30, 1380, stroke((84, 88, 100), 34)); cv.drawCircle(hx + 30, 1380, 22, fill(BLACK))
        if lt > 0.25:
            look = lt >= t2 - 0.2
            p = dict(STAND, af=(95, 0), ab=(10, 0), head=-6, mood="happy", look=(0.0, 0.0)) if look else dict(STAND, head=-8, look=(0.9, -0.5), mood="surprised", lean=-6)
            x = lerp(1150, 700, ease_out((lt - 0.25) / 0.6))
            ch(cv, MATEO, p, x, 1790, S=560, face=1 if not look else -1, T=T, seed=111, persp_on=False, ex=dict(blush=look))
        done(cv)
    S.append((0.0, s1))

    # 2. el señor Barros se va con su carpeta; Mateo llega corriendo
    def s2(cv, lt, d, T):
        cam = cam_move(lt, d, (675, 1460, 1.15), (700, 1480, 1.25)); stage(cv, cam, "espiga_calle")
        aviso(cv, 900, 1340, 0.62)
        x, ph, mv = walker(lt, 0, 640, 120, d, 1.2)
        shade(cv, x, 1840); ch(cv, BARROS, H_.walk(ph, base=dict(STAND, ab=(30, 80), mood="neutral")), x, 1840, S=520, face=-1, T=T, seed=112, ex=dict(back_hand_item=carpeta))
        xm, phm, mvm = walker(lt, 0.4, 1450, 980, d * 0.55, 2.2)
        shade(cv, xm, 1860); ch(cv, MATEO, H_.run(phm) if mvm else dict(STAND, look=(-0.6, -0.4), mood="worried"), xm, 1860, S=520, face=-1, T=T, seed=111)
        done(cv)
    S.append((A("esta mañana"), s2))

    # 3. el aviso en primer plano: la cifra y el plazo
    def s3(cv, lt, d, T):
        tc = A("o la") - A("un millón")
        sh = 14 * max(0, 1 - (lt - tc) / 0.4) if lt > tc else 0
        cam = cam_move(lt, d, (900, 1330, 3.0), (900, 1350, 3.4))
        cam.cx += math.sin(T * 60) * sh; stage(cv, cam, "espiga_calle")
        aviso(cv, 900, 1340, 0.62)
        if lt > tc:
            a = clamp((lt - tc) / 0.2)
            cv.save(); cv.translate(900, 1350); cv.rotate(-12); cv.scale(1 + 0.4 * (1 - a), 1 + 0.4 * (1 - a))
            cv.drawRRect(skia.RRect.MakeRectXY(XYWH(-150, -40, 300, 80), 10, 10), stroke((210, 30, 36), 10, a))
            text_center(cv, "CIERRE", 0, -4, 54, (210, 30, 36), None, a=a, shadow_=False)
            cv.restore()
        done(cv)
    S.append((A("un millón"), s3))

    # 4. la abuela Rosa amasa; cuarenta años horneando
    def s4(cv, lt, d, T):
        cam = cam_move(lt, d, (480, 1420, 2.0), (520, 1400, 2.25)); stage(cv, cam, "espiga_interior")
        w = math.sin(T * 6)
        look = lt > d * 0.55
        p = dict(STAND, lean=14, af=(70 + 12 * w, 30), ab=(60 - 12 * w, 40), head=10, look=(0.6, 0.8), mood="kind") if not look else dict(STAND, af=(40, 60), ab=(30, 60), head=-6, look=(0.9, -0.6), mood="sad")
        shade(cv, 420, 1830, persp_on=False)
        ch(cv, ABUELA, p, 420, 1830, S=600, face=1, T=T, seed=113, persp_on=False)
        ED.mostrador(cv, 60, 760, 1700)
        masa(cv, 560, 1676, T, 0 if look else 1)
        particles(cv, T, 40, 11, (255, 252, 244), (300, 1200, 600, 500), 25, (2, 5), 0.7)
        done(cv)
    S.append((A("la abuela rosa"), s4))

    # 5. abre la caja: cero pesos (y sale una polilla)
    def s5(cv, lt, d, T):
        t0 = A("cero pesos") - A("mateo abrió")
        cam = cam_move(lt, d, (420, 1400, 2.4), (420, 1420, 2.75)); stage(cv, cam, "espiga_interior")
        ED.mostrador(cv, 60, 760, 1640)
        op = ease_out((lt - 0.35) / 0.25)
        info = ch(cv, MATEO, dict(STAND, lean=22, af=(60, 50), head=24 if lt < t0 else -4, look=(0.3, 1.0) if lt < t0 else (0.0, 0.0), mood="surprised" if lt > t0 else "worried"),
                  560, 1600, S=520, face=-1, T=T, seed=111, persp_on=False)
        ED.caja_registradora(cv, 380, 1612, op, T, 1.0)
        if lt > t0:
            u = lt - t0
            polilla(cv, 380 + 140 * u + 20 * math.sin(u * 9), 1640 - 260 * u, T)
            a = clamp(u / 0.15)
            cv.save(); cv.translate(330, 1270); cv.scale(0.8 + 0.2 * ease_out(u / 0.25), 0.8 + 0.2 * ease_out(u / 0.25))
            text_center(cv, "$0", 0, 0, 170, RED, (20, 10, 10), 0.06, a=a)
            cv.restore()
        done(cv)
    S.append((A("mateo abrió"), s5))

    # 6. el horno, la receta... y tú
    def s6(cv, lt, d, T):
        tt = A("y te tiene") - A("pero tiene")
        if lt < tt: cam = cam_move(lt, tt, (900, 1500, 1.5), (840, 1480, 1.7))
        else: cam = cam_move(lt - tt, d - tt, (760, 1440, 1.9), (740, 1400, 2.4))
        stage(cv, cam, "espiga_interior")
        if lt < tt:
            p = dict(STAND, af=(110, 40), ab=(20, 40), head=-6, look=(0.7, -0.2), mood="determined")
            ex = dict(hand_item=lambda c, h: receta(c, h, T))
            face = 1
        else:
            p = dict(STAND, af=(92, 0), ab=(15, 10), head=-4, look=(0.0, 0.0), mood="happy"); ex = dict(blush=True); face = -1
        shade(cv, 760, 1860, persp_on=False)
        ch(cv, MATEO, p, 760, 1860, S=600, face=face, T=T, seed=111, persp_on=False, ex=ex)
        particles(cv, T, 30, 4, (255, 220, 150), (500, 1100, 700, 700), 30, (2, 5), 0.8)
        done(cv)
    S.append((A("pero tiene"), s6))

    # --- viñetas de las tarjetas
    def v_colegio(cv, T):
        for k in range(3):
            j = abs(math.sin(T * 4 + k)) * 6
            ch(cv, Mo.KIDS[k], dict(STAND, af=(70, 40), mood="happy"), 830 + k * 110, 1950 - j, S=560, face=-1, T=T, seed=120 + k, persp_on=False)
        ch(cv, MATEO, dict(HOLD, mood="happy", look=(0.9, 0)), 640, 1960, S=560, face=1, T=T, seed=111, persp_on=False,
           ex=dict(hand_item=lambda c, h: [ED.marraqueta(c, h[0] + 30, h[1] - 20, 0.7), ED.marraqueta(c, h[0] + 60, h[1] - 34, 0.7)]))

    def v_feria(cv, T):
        ch(cv, Mo.NEIGHBORS[1], dict(STAND, af=(80, 30), mood="happy", look=(-0.9, 0)), 860, 1720, S=560, face=-1, T=T, seed=130, persp_on=False)
        ch(cv, MATEO, dict(STAND, af=(90, 10), mood="happy", look=(0.9, 0)), 560, 1720, S=560, face=1, T=T, seed=111, persp_on=False)
        for k in range(4): ED.marraqueta(cv, 560 + k * 60, 1575, 0.6)
        for j in range(3): heart(cv, 800 + j * 40, 1300 - ((T * 60 + j * 40) % 120), 12, (255, 80, 100), 0.8)

    def v_prestamo(cv, T):
        ch(cv, TIO_LUCHO, dict(STAND, af=(90, 20), mood="smug", look=(-0.9, 0)), 760, 1840, S=560, face=-1, T=T, seed=140, persp_on=False,
           ex=dict(hand_item=lambda c, h: billetes(c, h, 4, T)))
        ch(cv, MATEO, dict(STAND, af=(70, 40), mood="worried", look=(0.9, 0)), 520, 1840, S=560, face=1, T=T, seed=111, persp_on=False)

    def v_video(cv, T):
        ch(cv, VALE, dict(STAND, af=(95, 60), mood="happy", look=(0.9, 0)), 450, 1880, S=600, face=1, T=T, seed=150, persp_on=False,
           ex=dict(hand_item=telefono))
        masa(cv, 720, 1660, T); ED.mostrador(cv, 560, 1000, 1700)
        for k in range(3): ED.marraqueta(cv, 640 + k * 70, 1660, 0.6)
        cv.drawCircle(560, 1500, 14, fill((255, 60, 60), 0.6 + 0.4 * math.sin(T * 8)))

    # 7. decisión 1
    D1 = [dict(key="1A", title=["PUERTA DEL", "COLEGIO"], fx=[("$", "+30.000", True), ("e", "−1", False)],
               bg="colegio_puerta", center=(760, 1760), z=0.85, draw=v_colegio),
          dict(key="1B", title=["FERIA", "LIBRE"], fx=[("$", "+10.000", True), ("h", "+1", True)],
               bg="feria", center=(700, 1560), z=0.8, draw=v_feria)]

    def s7(cv, lt, d, T):
        t0 = A("primera decisión")
        decision(cv, lt, d, T, 1, "¿DÓNDE VENDE HOY?", D1, A("1a") - t0, A("1b") - t0, "espiga_interior")
    S.append((A("primera decisión"), s7))

    # 8. el tío Lucho: «te presto, pero no se lo cuentes a tu abuela»
    def s8(cv, lt, d, T):
        tp = A("te presto") - A("segunda decisión")
        cam = cam_move(lt, d, (600, 1460, 1.35), (560, 1440, 1.75) if lt > tp else (600, 1460, 1.5)); stage(cv, cam, "espiga_calle")
        cv.save(); cv.clipRect(XYWH(300, 1250, 420, 300))
        H_.silhouette_begin(cv); ch(cv, ABUELA, dict(STAND, mood="kind"), 420, 1640, S=420, face=1, T=T, seed=113, persp_on=False); H_.silhouette_end(cv, (90, 60, 40), 0.55)
        cv.restore()
        x, ph, mv = walker(lt, 0.2, 80, 420, 1.6, 1.3)
        whisper = lt > tp
        p = dict(STAND, lean=10, af=(30, 150), ab=(80, 30), head=10, look=(0.9, 0.2), mood="smug") if whisper else (H_.walk(ph, base=dict(STAND, af=(110, 20))) if mv else dict(STAND, af=(110, 20), mood="happy"))
        shade(cv, x, 1840); ch(cv, TIO_LUCHO, p, x, 1840, S=520, face=1, T=T, seed=140, ex=None if whisper else dict(hand_item=lambda c, h: billetes(c, h, 4, T)))
        if whisper: billetes(cv, (x + 120, 1610), 4, T)
        shade(cv, 680, 1850); ch(cv, MATEO, dict(STAND, look=(-0.9, 0.1), mood="worried" if whisper else "surprised", ab=(10, 40), af=(20, 60)), 680, 1850, S=520, face=-1, T=T, seed=111)
        if whisper:
            for k in range(3):
                a = 0.5 + 0.5 * math.sin(T * 5 - k)
                cv.drawArc(XYWH(x + 120 + k * 20, 1380 - k * 20, 40 + k * 40, 40 + k * 40), -40, 80, False, stroke((255, 255, 255), 5, a))
        done(cv)
    S.append((A("segunda decisión"), s8))

    D2 = [dict(key="2A", title=["PRÉSTAMO DEL", "TÍO LUCHO"], fx=[("$", "+100.000", True), ("h", "−1", False)],
               bg="espiga_calle", center=(640, 1620), z=0.8, draw=v_prestamo),
          dict(key="2B", title=["VIDEO CON", "VALE"], fx=[("$", "+0", True), ("h", "+1", True)],
               bg="espiga_interior", center=(620, 1640), z=0.75, draw=v_video)]

    def s9(cv, lt, d, T):
        t0 = A("2a")
        decision(cv, lt, d, T, 2, "¿QUIÉN AYUDA?", D2, 0.05, A("2b") - t0, "espiga_calle")
    S.append((A("2a"), s9))

    # 10. llamada a votar en los comentarios
    def s10(cv, lt, d, T):
        cam = cam_move(lt, d, (760, 1500, 1.35), (760, 1520, 1.45)); stage(cv, cam, "espiga_calle")
        ED_a = 1
        aviso(cv, 900, 1340, 0.62)
        wv = math.sin(T * 8)
        shade(cv, 620, 1850); ch(cv, ABUELA, dict(STAND, af=(150 + 15 * wv, 10), mood="happy"), 620, 1850, S=520, face=1, T=T, seed=113)
        shade(cv, 820, 1860); ch(cv, MATEO, dict(STAND, af=(160 - 15 * wv, 0), mood="happy", look=(0, 0)), 820, 1860, S=520, face=-1, T=T, seed=111)
        done(cv)
        cv.drawRect(XYWH(0, 0, W, H), fill((10, 10, 18), 0.55 * ease_out(lt / 0.3)))
        a = ease_out((lt - 0.1) / 0.35)
        cv.save(); cv.translate(W / 2, 760); cv.scale(0.85 + 0.15 * a, 0.85 + 0.15 * a)
        text_center(cv, "¿QUÉ HACE MATEO?", 0, -150, 76, AMA, (17, 17, 17), 0.08, a=a)
        text_center(cv, "COMENTA TU VOTO", 0, -60, 54, (255, 255, 255), (17, 17, 17), 0.08, a=a)
        for i, (k1, k2) in enumerate((("1A", "1B"), ("2A", "2B"))):
            y = 40 + i * 140
            for j, k in enumerate((k1, k2)):
                pulse = 1 + 0.06 * max(0, math.sin(T * 6 + i * 1.5 + j * 0.8))
                x = -150 + j * 300
                kc = (40, 110, 220) if k.endswith("A") else (220, 70, 60)
                cv.save(); cv.translate(x, y); cv.scale(pulse, pulse)
                cv.drawRRect(skia.RRect.MakeRectXY(XYWH(-120, -55, 240, 110), 26, 26), fill(kc, a))
                text_center(cv, k, 0, -4, 80, (255, 255, 255), None, a=a, shadow_=False)
                cv.restore()
            text_center(cv, "o", 0, y - 4, 44, (255, 255, 255), None, a=a)
        text_center(cv, "Si nadie vota, gana la A", 0, 350, 38, (230, 230, 240), (17, 17, 17), 0.06, a=a)
        text_center(cv, "MAÑANA: EL RESULTADO", 0, 420, 44, AMA, (17, 17, 17), 0.08, a=a)
        cv.restore()
        # flecha hacia los comentarios
        bob = 18 * math.sin(T * 7)
        cv.save(); cv.translate(930, 1250 + bob); cv.rotate(20)
        cv.drawPath(path([(-22, -90), (22, -90), (22, 0), (56, 0), (0, 70), (-56, 0), (-22, 0)]), fill(AMA, a))
        cv.restore()
    S.append((A("comenta"), s10))
    texts = [("TÚ DECIDES", A("y tú"), A("esta mañana") - 0.1)]
    return S, texts
