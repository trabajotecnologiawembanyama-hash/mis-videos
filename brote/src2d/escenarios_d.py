"""Escenarios de la serie interactiva «20 días» (Mateo y la panadería La Espiga)."""
import math, random
import skia
from motor import (C, fill, stroke, lin, rad, rrect, path, typeface, text_center, clamp, lerp)
import escenarios as E
from escenarios import BW, BH, sky, buildings, tree, wires, concrete

XYWH = skia.Rect.MakeXYWH


def marraqueta(cv, x, y, s=1.0, rot=0.0, tone=1.0):
    """Pan chileno: cuatro lóbulos dorados con la hendidura al medio."""
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s, s)
    base = tuple(min(255, int(v * tone)) for v in (214, 146, 66))
    dark = tuple(min(255, int(v * tone)) for v in (160, 96, 36))
    for dx in (-20, 20):
        cv.drawOval(XYWH(dx - 24, -18, 48, 36), rad((dx - 6, -10), 40, [(244, 196, 120), base, dark], [0, 0.55, 1]))
    cv.drawLine(0, -16, 0, 16, stroke((120, 70, 26), 3, 0.7))
    cv.drawLine(-36, -2, 36, -2, stroke((120, 70, 26), 2, 0.35))
    cv.drawOval(XYWH(-30, -14, 22, 8), fill((255, 240, 210), 0.35))
    cv.restore()


def hallulla(cv, x, y, s=1.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawOval(XYWH(-34, -14, 68, 28), rad((-8, -8), 46, [(250, 220, 160), (222, 172, 96), (176, 120, 56)], [0, 0.6, 1]))
    for k in range(5): cv.drawCircle(-20 + k * 10, -2 + (k % 2) * 4, 1.6, fill((150, 100, 50), 0.6))
    cv.restore()


def awning(cv, x0, x1, y, depth, c1, c2, n=9):
    w = (x1 - x0) / n
    for k in range(n):
        cv.drawPath(path([(x0 + k * w, y), (x0 + (k + 1) * w, y), (x0 + (k + 1) * w + 10, y + depth), (x0 + k * w + 10, y + depth)]), fill(c1 if k % 2 == 0 else c2))
    for k in range(n):
        cv.drawArc(XYWH(x0 + k * w + 10, y + depth - w * 0.32, w, w * 0.64), 0, 180, True, fill(c1 if k % 2 == 0 else c2))
    cv.drawRect(XYWH(x0, y + depth, x1 - x0 + 10, 14), fill((0, 0, 0), 0.18, blur=6))


def casita(cv, x, w, base, h, col, roof=(150, 70, 50), rnd=None, reja=True):
    shade = tuple(int(v * 0.8) for v in col)
    cv.drawRect(XYWH(x, base - h, w, h), lin((x, 0), (x + w, 0), [col, shade]))
    cv.drawPath(path([(x - 16, base - h + 6), (x + w + 16, base - h + 6), (x + w + 6, base - h - 40), (x - 6, base - h - 40)]), fill(roof))
    rrect(cv, x + w * 0.18, base - h + 70, w * 0.32, 120, 6, fill((90, 70, 52)))
    cv.drawRect(XYWH(x + w * 0.18 + 8, base - h + 78, w * 0.32 - 16, 104), lin((0, base - h + 78), (0, base - h + 182), [(170, 200, 220), (110, 140, 170)]))
    rrect(cv, x + w * 0.62, base - h + 110, w * 0.24, base - (base - h + 110), 4, fill((120, 84, 56)))
    if reja:
        for k in range(int(w // 26)):
            cv.drawRect(XYWH(x + 6 + k * 26, base - 120, 6, 120), fill((40, 40, 46)))
        cv.drawRect(XYWH(x, base - 124, w, 8), fill((40, 40, 46)))


# ------------------------------------------------------------------ calle con la fachada de La Espiga
def _espiga_calle(cv, rnd):
    sky(cv, (120, 170, 230), (214, 226, 240), (255, 222, 176), 1150, sun=(250, 820, 70), sun_col=(255, 236, 196))
    buildings(cv, 1150, rnd, (176, 168, 196), (255, 236, 200), h_min=140, h_max=330, win_p=0.12, alpha=0.65)
    # cordillera a lo lejos
    cv.drawPath(path([(0, 1080), (160, 930), (300, 1010), (480, 880), (640, 990), (820, 900), (1000, 1000), (1180, 910), (1350, 990), (1350, 1150), (0, 1150)]), fill((190, 196, 220), 0.8))
    cv.drawPath(path([(430, 905), (480, 880), (530, 905), (500, 915)]), fill((250, 250, 255)))
    cv.drawPath(path([(1130, 935), (1180, 910), (1230, 935), (1195, 945)]), fill((250, 250, 255)))
    # casas vecinas
    casita(cv, -40, 300, 1600, 430, (120, 180, 200), rnd=rnd)
    casita(cv, 1090, 300, 1600, 470, (236, 190, 110), roof=(130, 60, 44), rnd=rnd)
    # fachada de la panadería
    fx0, fx1, top, base = 250, 1100, 960, 1600
    cv.drawRect(XYWH(fx0, top, fx1 - fx0, base - top), lin((fx0, 0), (fx1, 0), [(246, 226, 190), (226, 204, 166)]))
    for k in range(60):
        cv.drawCircle(rnd.uniform(fx0, fx1), rnd.uniform(top, base), rnd.uniform(1, 3), fill((120, 90, 60), 0.06))
    cv.drawRect(XYWH(fx0 - 14, top - 24, fx1 - fx0 + 28, 34), fill((150, 94, 56)))
    # letrero
    rrect(cv, 380, 990, 590, 140, 16, lin((0, 990), (0, 1130), [(150, 40, 36), (118, 28, 26)]))
    rrect(cv, 392, 1002, 566, 116, 12, stroke((255, 210, 120), 4))
    text_center(cv, "LA ESPIGA", 675, 1046, 82, (255, 236, 190), None, font="Inter-Black", shadow_=False)
    text_center(cv, "PANADERÍA · DESDE 1985", 675, 1100, 30, (255, 210, 140), None, font="Inter-Bold", shadow_=False)
    for sx in (350, 1000):     # espigas de trigo pintadas
        for k in range(6):
            cv.drawOval(XYWH(sx - 10 + (k % 2) * 14, 1020 + k * 14, 14, 22), fill((236, 180, 70)))
        cv.drawLine(sx + 4, 1020, sx + 4, 1120, stroke((200, 150, 60), 4))
    awning(cv, 300, 1050, 1140, 70, (176, 40, 40), (250, 244, 232), n=11)
    # vitrina con pan
    vx, vy, vw, vh = 300, 1250, 420, 300
    rrect(cv, vx - 12, vy - 12, vw + 24, vh + 24, 8, fill((110, 70, 44)))
    cv.drawRect(XYWH(vx, vy, vw, vh), lin((0, vy), (0, vy + vh), [(255, 226, 170), (240, 190, 120)]))
    for r_, yy in enumerate((vy + 110, vy + 220)):
        cv.drawRect(XYWH(vx + 10, yy, vw - 20, 10), fill((150, 100, 60)))
        for k in range(6):
            (marraqueta if (k + r_) % 2 == 0 else hallulla)(cv, vx + 50 + k * 64, yy - 22, 0.62)
    cv.drawPath(path([(vx + 30, vy), (vx + 140, vy), (vx + 40, vy + vh), (vx - 70 + 30, vy + vh)]), fill((255, 255, 255), 0.22))
    text_center(cv, "PAN CALIENTE", vx + vw / 2, vy + 40, 38, (150, 40, 36), None, font="Inter-Black", shadow_=False)
    # puerta de vidrio
    dx0, dy0, dw, dh = 780, 1230, 240, 370
    rrect(cv, dx0 - 12, dy0 - 12, dw + 24, dh + 12, 8, fill((96, 58, 36)))
    cv.drawRect(XYWH(dx0, dy0, dw, dh), lin((0, dy0), (0, dy0 + dh), [(196, 160, 110), (150, 112, 72)]))
    cv.drawRect(XYWH(dx0 + 20, dy0 + 20, dw - 40, 190), lin((0, dy0), (0, dy0 + 210), [(255, 230, 180), (226, 180, 120)]))
    cv.drawPath(path([(dx0 + 40, dy0 + 20), (dx0 + 90, dy0 + 20), (dx0 + 50, dy0 + 210), (dx0 + 20, dy0 + 210)]), fill((255, 255, 255), 0.25))
    cv.drawCircle(dx0 + dw - 30, dy0 + 260, 10, fill((230, 190, 80)))
    rrect(cv, dx0 + 50, dy0 + 240, 140, 56, 6, fill((40, 120, 60)))
    text_center(cv, "ABIERTO", dx0 + dw / 2, dy0 + 268, 30, (255, 255, 255), None, font="Inter-Black", shadow_=False)
    cv.drawRect(XYWH(fx0 - 20, base, fx1 - fx0 + 40, 30), fill((150, 140, 130)))
    # macetero y bicicleta de reparto
    rrect(cv, 1030, 1480, 70, 110, 10, fill((176, 90, 60)))
    for k in range(7): cv.drawCircle(1065 + rnd.uniform(-46, 46), 1460 + rnd.uniform(-50, 20), 28, fill((70, 150, 80)))
    # vereda y calle
    cv.drawRect(XYWH(0, 1600, BW, 260), lin((0, 1600), (0, 1860), [(196, 186, 172), (168, 158, 146)]))
    for x in range(-40, BW, 150): cv.drawLine(x, 1600, x - 30, 1860, stroke((140, 130, 120), 3, 0.5))
    cv.drawRect(XYWH(0, 1860, BW, 34), fill((206, 200, 190)))
    cv.drawRect(XYWH(0, 1894, BW, BH - 1894), lin((0, 1894), (0, BH), [(110, 110, 116), (80, 80, 86)]))
    for x in range(40, BW, 260): cv.drawRect(XYWH(x, 2160, 140, 16), fill((240, 230, 200), 0.85))
    for k in range(500):
        cv.drawCircle(rnd.uniform(0, BW), rnd.uniform(1900, BH), rnd.uniform(1, 3), fill((255, 255, 255) if k % 2 else (0, 0, 0), 0.06))
    for px in (40, 1310):
        cv.drawRect(XYWH(px - 9, 780, 18, 830), fill((90, 64, 44))); cv.drawRect(XYWH(px - 50, 800, 100, 10), fill((90, 64, 44)))
    for dy in (0, 26):
        pth = skia.Path(); pth.moveTo(40, 805 + dy); pth.quadTo(675, 900 + dy, 1310, 805 + dy); cv.drawPath(pth, stroke((30, 30, 30), 2.5, cap=False))
    tree(cv, 120, 1620, 1.25, rnd, (80, 150, 76))


# ------------------------------------------------------------------ interior de La Espiga
def _espiga_interior(cv, rnd):
    cv.drawRect(skia.Rect.MakeWH(BW, 1300), lin((0, 0), (0, 1300), [(240, 214, 170), (226, 196, 150)]))
    for k in range(400): cv.drawCircle(rnd.uniform(0, BW), rnd.uniform(0, 1300), rnd.uniform(1, 3), fill((120, 80, 40), 0.04))
    # azulejos blancos abajo
    cv.drawRect(XYWH(0, 1300, BW, 500), fill((244, 242, 236)))
    for y in range(1300, 1800, 60):
        cv.drawLine(0, y, BW, y, stroke((206, 200, 190), 2))
        for x in range((0 if (y // 60) % 2 else 30), BW, 60): cv.drawLine(x, y, x, y + 60, stroke((206, 200, 190), 2))
    cv.drawRect(XYWH(0, 1290, BW, 16), fill((150, 40, 36)))
    # horno de barro con fuego (derecha)
    ox, oy = 1040, 1150
    cv.drawRect(XYWH(ox - 230, oy - 60, 460, 700), lin((ox - 230, 0), (ox + 230, 0), [(176, 96, 66), (150, 78, 52)]))
    for r_ in range(14):
        for c_ in range(5):
            bx = ox - 230 + c_ * 96 + (48 if r_ % 2 else 0); by = oy - 60 + r_ * 50
            cv.drawRect(XYWH(bx, by, 92, 46), stroke((120, 60, 40), 3, 0.6))
    arch = skia.Path(); arch.addArc(XYWH(ox - 140, oy + 120, 280, 260), 180, 180); arch.lineTo(ox + 140, oy + 330); arch.lineTo(ox - 140, oy + 330); arch.close()
    cv.drawPath(arch, fill((40, 20, 14)))
    cv.drawPath(arch, rad((ox, oy + 330), 220, [(255, 200, 90, 0.95), (240, 110, 40, 0.7), (60, 20, 10, 0.0)], [0, 0.45, 1]))
    cv.drawRect(XYWH(ox - 170, oy + 330, 340, 30), fill((90, 60, 40)))
    cv.drawCircle(ox, oy + 300, 420, rad((ox, oy + 300), 420, [(255, 170, 80, 0.32), (255, 170, 80, 0.0)]))
    # repisas con pan (izquierda)
    for r_, yy in enumerate((560, 760, 960)):
        cv.drawRect(XYWH(40, yy, 620, 22), lin((0, yy), (0, yy + 22), [(170, 116, 70), (126, 82, 46)]))
        for k in range(3):
            bx = 70 + k * 200
            cv.drawPath(path([(bx, yy), (bx + 170, yy), (bx + 150, yy - 60), (bx + 20, yy - 60)]), fill((196, 150, 96)))
            for j in range(4): cv.drawLine(bx + 24 + j * 38, yy - 58, bx + 18 + j * 40, yy, stroke((150, 110, 66), 3, 0.6))
            for j in range(3):
                (marraqueta if (j + r_ + k) % 2 == 0 else hallulla)(cv, bx + 40 + j * 46, yy - 66 - (j % 2) * 10, 0.6)
    # foto antigua 1985
    cv.save(); cv.translate(760, 600); cv.rotate(-3)
    rrect(cv, -110, -90, 220, 180, 6, fill((90, 60, 40)))
    cv.drawRect(XYWH(-96, -76, 192, 132), lin((0, -76), (0, 56), [(214, 190, 150), (180, 150, 110)]))
    cv.drawRect(XYWH(-60, -30, 120, 70), fill((140, 100, 70), 0.6)); cv.drawRect(XYWH(-60, -40, 120, 14), fill((120, 50, 40), 0.6))
    cv.drawCircle(-20, 20, 10, fill((90, 70, 50), 0.7)); cv.drawCircle(20, 20, 9, fill((90, 70, 50), 0.7))
    text_center(cv, "1985", 0, 72, 22, (240, 220, 180), None, font="Inter-Bold", shadow_=False)
    cv.restore()
    # lámpara colgante
    cv.drawLine(480, 0, 480, 300, stroke((60, 50, 44), 4))
    cv.drawPath(path([(410, 360), (550, 360), (510, 300), (450, 300)]), fill((60, 74, 60)))
    cv.drawCircle(480, 372, 20, fill((255, 246, 210)))
    cv.drawCircle(480, 420, 520, rad((480, 420), 520, [(255, 236, 180, 0.3), (255, 236, 180, 0.0)]))
    # sacos de harina
    for k, (sx, sy) in enumerate(((600, 1600), (720, 1620), (660, 1510))):
        rrect(cv, sx - 70, sy - 110, 140, 150, 40, lin((0, sy - 110), (0, sy + 40), [(246, 240, 226), (214, 206, 190)]))
        text_center(cv, "HARINA", sx, sy - 40, 24, (150, 40, 36), None, font="Inter-Black", shadow_=False)
    # piso
    cv.drawRect(XYWH(0, 1800, BW, BH - 1800), lin((0, 1800), (0, BH), [(176, 120, 72), (130, 86, 48)]))
    for x in range(-60, BW + 60, 120):
        cv.drawLine(x, 1800, x - 120, BH, stroke((110, 72, 40), 3, 0.5))
    for y in (1900, 2040, 2210): cv.drawLine(0, y, BW, y, stroke((110, 72, 40), 3, 0.5))
    cv.drawRect(XYWH(0, 1800, BW, 200), lin((0, 1800), (0, 2000), [(0, 0, 0, 0.25), (0, 0, 0, 0.0)]))


def mostrador(cv, x0=60, x1=760, top=1600):
    """Mostrador de madera con vitrina (se dibuja delante del personaje)."""
    cv.drawRect(XYWH(x0, top, x1 - x0, 220), lin((0, top), (0, top + 220), [(156, 102, 60), (112, 70, 40)]))
    for k in range(int((x1 - x0) // 140)): cv.drawRect(XYWH(x0 + 20 + k * 140, top + 30, 110, 160), stroke((90, 56, 30), 4, 0.6))
    rrect(cv, x0 - 20, top - 26, x1 - x0 + 40, 30, 6, lin((0, top - 26), (0, top + 4), [(196, 140, 90), (150, 100, 60)]))


def caja_registradora(cv, x, y, open_=0.0, T=0.0, s=1.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    d = 90 * open_
    rrect(cv, -110, -10 + d * 0.15, 220, 54, 6, fill((60, 46, 40)))           # cajón
    if open_ > 0.05:
        cv.drawRect(XYWH(-96, -4 + d * 0.15, 192, 40), fill((30, 24, 22)))
        for k in range(4): cv.drawRect(XYWH(-90 + k * 46, -2 + d * 0.15, 40, 34), stroke((90, 80, 76), 3))
    rrect(cv, -120, -150, 240, 150, 14, lin((0, -150), (0, 0), [(196, 160, 90), (150, 116, 60)]))
    rrect(cv, -100, -200, 200, 60, 10, fill((40, 40, 46)))
    for k in range(9): rrect(cv, -96 + (k % 3) * 34, -126 + (k // 3) * 34, 28, 26, 5, fill((240, 236, 226)))
    cv.drawRect(XYWH(10, -130, 90, 100), fill((220, 196, 140)))
    cv.restore()


# ------------------------------------------------------------------ puerta del colegio (para la tarjeta 1A)
def _colegio_puerta(cv, rnd):
    sky(cv, (120, 176, 236), (200, 224, 244), (250, 236, 210), 1100, sun=(1100, 600, 60))
    cv.drawRect(XYWH(0, 980, BW, 680), fill((176, 86, 60)))
    for row, y in enumerate(range(980, 1660, 40)):
        off = 0 if row % 2 else 55
        for x in range(-off, BW, 110):
            c = rnd.uniform(0.86, 1.08)
            rrect(cv, x + 3, y + 3, 104, 34, 3, fill(tuple(min(255, int(v * c)) for v in (186, 92, 64))))
    rrect(cv, 400, 860, 550, 120, 10, fill((40, 90, 160)))
    text_center(cv, "COLEGIO", 675, 920, 80, (255, 255, 255), None, font="Inter-Black", shadow_=False)
    for x in range(430, 930, 36): cv.drawRect(XYWH(x, 1080, 10, 580), fill((40, 44, 52)))
    cv.drawRect(XYWH(420, 1080, 520, 14), fill((40, 44, 52))); cv.drawRect(XYWH(420, 1360, 520, 10), fill((40, 44, 52)))
    concrete(cv, 1660, BH, (196, 190, 180), (150, 146, 138), rnd)


E.BUILD.update({"espiga_calle": _espiga_calle, "espiga_interior": _espiga_interior, "colegio_puerta": _colegio_puerta})
