"""Tomas de los episodios 1 y 2 de Brote (semana de Pedrito). Uso: python3 tomas.py <salida_dir> [toma ...]"""
import math, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
import bpy
from mathutils import Vector
import mundo3d as M
from mundo3d import (box, cyl, sphere, torus, plane, tube, smooth_tube, mat, mat_noise, stickman, camera, sun, area,
                     point, world_sky, world_color, world_point)

OUT = sys.argv[1]
ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")

# ---------------------------------------------------------------- personajes fijos (tabla del plan)
PEDRITO = dict(hair="curly", shirt=(0.55, 0.035, 0.03), shirt_rough=0.95, pants=(0.05, 0.06, 0.12),
               shoe=(0.13, 0.17, 0.26), sole=(0.62, 0.6, 0.55), tape=True)
LUCHO = dict(shirt=(0.16, 0.22, 0.3), pants=(0.16, 0.22, 0.3), shoe=(0.1, 0.07, 0.05), sole=(0.08, 0.06, 0.05),
             moustache=(0.55, 0.55, 0.55), hair="short", hair_color=(0.45, 0.45, 0.45))
MAMA = dict(hair="bun", hair_color=(0.08, 0.04, 0.02), shirt=(0.15, 0.35, 0.45), pants=(0.15, 0.35, 0.45),
            shoe=(0.2, 0.15, 0.12))
COACH = dict(cap=(0.05, 0.12, 0.35), shirt=(0.05, 0.12, 0.35), pants=(0.05, 0.12, 0.35), shoe=(0.9, 0.9, 0.9), whistle=True)
KIDS = [dict(shiny=True, hair="short", hair_color=(0.1, 0.06, 0.03), shirt=(0.1, 0.45, 0.85), pants=(0.9, 0.9, 0.92), shoe=(0.98, 0.98, 1.0), sole=(1, 1, 1)),
        dict(shiny=True, hair="pony", hair_color=(0.35, 0.18, 0.05), shirt=(0.95, 0.75, 0.1), pants=(0.1, 0.1, 0.12), shoe=(0.1, 0.9, 0.4), sole=(1, 1, 1)),
        dict(shiny=True, hair="short", hair_color=(0.02, 0.02, 0.02), shirt=(0.2, 0.7, 0.35), pants=(0.15, 0.15, 0.4), shoe=(1.0, 0.35, 0.1), sole=(1, 1, 1)),
        dict(shiny=True, hair="short", hair_color=(0.55, 0.35, 0.12), shirt=(0.55, 0.25, 0.75), pants=(0.12, 0.12, 0.12), shoe=(0.98, 0.98, 1.0), sole=(1, 1, 1)),
        dict(shiny=True, hair="pony", hair_color=(0.05, 0.03, 0.02), shirt=(0.95, 0.4, 0.55), pants=(0.1, 0.12, 0.3), shoe=(0.3, 0.6, 1.0), sole=(1, 1, 1))]


# ---------------------------------------------------------------- entornos
def hoop(x, y, rusty=True, facing=0, glass=False):
    poste = mat_noise("poste", (0.18, 0.08, 0.03), (0.35, 0.35, 0.36), 3, 0.6, 0.2, metal=0.6) if rusty else mat("poste_n", (0.08, 0.08, 0.1), 0.4, 0.5)
    cyl((x, y + 0.9, 1.6), 0.06, 3.2, poste)
    tube([(x, y + 0.9, 3.15), (x, y + 0.45, 3.15)], 0.05, poste)
    if glass:
        gm = bpy.data.materials.new("vidrio"); gm.use_nodes = True
        b = gm.node_tree.nodes["Principled BSDF"]; b.inputs["Transmission Weight"].default_value = 1.0
        b.inputs["Roughness"].default_value = 0.05
        box((x, y + 0.4, 3.25), (1.8, 0.03, 1.05), gm, bevel=0.01)
        frame = mat("marco", (0.1, 0.1, 0.1), 0.4)
        box((x, y + 0.38, 3.0), (0.6, 0.035, 0.45), mat("rojo_cuadro", (0.8, 0.1, 0.05), 0.5))
    else:
        tablero = mat_noise("tablero", (0.62, 0.6, 0.55), (0.82, 0.8, 0.75), 4, 0.8, 0.3)
        box((x, y + 0.4, 3.25), (1.8, 0.05, 1.05), tablero, bevel=0.01)
        box((x, y + 0.37, 3.08), (0.6, 0.02, 0.45), mat("marco_aro", (0.55, 0.1, 0.05), 0.7))
        box((x, y + 0.36, 3.08), (0.52, 0.021, 0.37), tablero)
    aro = mat_noise("oxido", (0.25, 0.07, 0.02), (0.55, 0.22, 0.06), 20, 0.7, 0.3, metal=0.5) if rusty else mat("aro", (0.9, 0.3, 0.02), 0.3, 0.6)
    torus((x, y + 0.08, 3.05), 0.23, 0.012, aro)
    # red
    red = mat("red", (0.85, 0.85, 0.82), 0.8)
    for k in range(10):
        a = 2 * math.pi * k / 10
        tube([(x + 0.23 * math.cos(a), y + 0.08 + 0.23 * math.sin(a), 3.05),
              (x + 0.15 * math.cos(a + 0.4), y + 0.08 + 0.15 * math.sin(a + 0.4), 2.65)], 0.004, red)


def houses(y0, n=9, seed=4, xspan=(-14, 14)):
    rnd = random.Random(seed)
    cols = [(0.75, 0.55, 0.35), (0.55, 0.65, 0.7), (0.8, 0.75, 0.6), (0.65, 0.4, 0.35), (0.5, 0.55, 0.4), (0.85, 0.82, 0.78)]
    x = xspan[0]
    while x < xspan[1]:
        w = rnd.uniform(3, 5.5); h = rnd.uniform(3, 7)
        wall = mat_noise("muro%d" % rnd.randint(0, 99), cols[rnd.randrange(len(cols))], tuple(c * 0.8 for c in cols[rnd.randrange(len(cols))]), 2, 0.9, 0.3)
        yy = y0 + rnd.uniform(0, 3)
        box((x + w / 2, yy, h / 2), (w, 4, h), wall)
        roof = mat("techo", (0.25, 0.1, 0.07), 0.8)
        box((x + w / 2, yy, h + 0.08), (w + 0.2, 4.2, 0.16), roof)
        for wx in range(int(w // 1.4)):
            for wz in range(int(h // 1.8)):
                lit = rnd.random() < 0.35
                wm = mat("vent_on" if lit else "vent_off", (1.0, 0.7, 0.4) if lit else (0.08, 0.1, 0.12), 0.2,
                         emit=(1.0, 0.65, 0.35) if lit else None, emit_s=3.0 if lit else 0)
                box((x + 0.6 + wx * 1.4, yy - 2.01, 1.3 + wz * 1.8), (0.7, 0.04, 0.9), wm)
        x += w + rnd.uniform(0.2, 1.5)
    # árboles
    for k in range(6):
        tx = rnd.uniform(*xspan); ty = y0 - rnd.uniform(1, 3)
        trunk = mat("tronco", (0.15, 0.09, 0.05), 0.9)
        cyl((tx, ty, 1.5), 0.12, 3, trunk)
        leaf = mat_noise("hojas", (0.08, 0.2, 0.05), (0.2, 0.35, 0.08), 8, 0.85, 0.5)
        for j in range(5):
            sphere((tx + rnd.uniform(-0.8, 0.8), ty + rnd.uniform(-0.8, 0.8), 3.2 + rnd.uniform(0, 1.3)), rnd.uniform(0.8, 1.3), leaf, seg=16)
    # postes y cables de luz
    wood = mat("poste_madera", (0.2, 0.13, 0.08), 0.9)
    for px in (-9, 0, 9):
        cyl((px, y0 - 3.5, 4), 0.1, 8, wood)
    cable = mat("cable", (0.01, 0.01, 0.01), 0.5)
    for dz in (7.4, 7.0):
        smooth_tube([(-9, y0 - 3.5, dz), (-4.5, y0 - 3.5, dz - 0.5), (0, y0 - 3.5, dz), (4.5, y0 - 3.5, dz - 0.5), (9, y0 - 3.5, dz)], 0.012, cable)


def fence(y, x0=-12, x1=12, h=3.0):
    fm = M.mat_fence()
    o = plane(((x0 + x1) / 2, y, h / 2), (x1 - x0, h), fm, rot=(90, 0, 0))
    bpy.ops.object.select_all(action="DESELECT")
    pm = mat("poste_reja", (0.35, 0.35, 0.37), 0.4, 0.8)
    for px in range(int(x0), int(x1) + 1, 3):
        cyl((px, y, h / 2), 0.035, h, pm)
    tube([(x0, y, h), (x1, y, h)], 0.03, pm)
    return o


def court(sun_elev=5, sun_azim=210, sky=0.25, sun_e=2.6, warm=(1.0, 0.62, 0.32), fence_y=9, with_houses=True):
    world_sky(4, sun_azim, 0.16)                 # cielo de atardecer (luz ambiente)
    sun(max(sun_elev, 13), sun_azim, 5.5, (1.0, 0.6, 0.3), 0.8)
    conc = mat_noise("concreto", (0.27, 0.27, 0.27), (0.43, 0.42, 0.4), 5, 0.88, 0.35)
    plane((0, 0, 0), (60, 60), conc)
    cr = mat_noise("cancha", (0.33, 0.33, 0.34), (0.48, 0.47, 0.46), 9, 0.9, 0.25)
    plane((0, 1, 0.003), (15, 14), cr)
    linea = mat_noise("linea", (0.55, 0.53, 0.5), (0.85, 0.84, 0.8), 30, 0.8, 0.0)
    for (x, y, sx, sy) in ((0, -6, 15, 0.06), (0, 8, 15, 0.06), (-7.5, 1, 0.06, 14), (7.5, 1, 0.06, 14), (0, 1, 15, 0.06)):
        plane((x, y, 0.006), (sx, sy), linea)
    bpy.ops.mesh.primitive_circle_add(radius=1.8, location=(0, 1, 0.007), vertices=64)
    c = bpy.context.object
    md = c.modifiers.new("w", "SKIN") if False else None
    # arco y zona
    smooth_tube([(-2.5, 8, 0.008), (-2.5, 4.5, 0.008), (0, 3.2, 0.008), (2.5, 4.5, 0.008), (2.5, 8, 0.008)], 0.03, linea)
    hoop(0, 8.0, rusty=True)
    fence(fence_y)
    if with_houses: houses(fence_y + 4)
    # hojas secas y grietas
    rnd = random.Random(8)
    leafm = mat("hoja_seca", (0.35, 0.2, 0.06), 0.9)
    for k in range(40):
        box((rnd.uniform(-8, 8), rnd.uniform(-5, 9), 0.01), (0.06, 0.04, 0.005), leafm, rot=(0, 0, rnd.uniform(0, 180)))


def ball_at(p, r=0.12):
    return sphere(tuple(p), r, M.mat_ball(), name="balon")


def house_interior():
    world_color((0.9, 0.6, 0.35), 1.2)
    wall = mat_noise("pared", (0.62, 0.52, 0.38), (0.72, 0.62, 0.46), 3, 0.95, 0.25)
    floor = M.mat_wood("piso", (0.25, 0.14, 0.07), (0.38, 0.22, 0.11), 3.0, 0.5)
    plane((0, 0, 0), (8, 8), floor)
    box((0, 2.5, 1.5), (8, 0.1, 3), wall)            # pared del fondo con ventana
    box((-3, 0, 1.5), (0.1, 8, 3), wall)
    box((0, 0, 3.0), (8, 8, 0.1), mat("techo_int", (0.5, 0.45, 0.4), 0.9))
    # hueco de ventana: marco y luz cálida de atardecer
    win = mat("cielo_ventana", (1.0, 0.65, 0.35), 0.5, emit=(1.0, 0.62, 0.3), emit_s=5.0)
    box((0.9, 2.44, 1.6), (1.3, 0.02, 1.1), win)
    frame = mat("marco_v", (0.35, 0.22, 0.12), 0.7)
    for (x, z, sx, sz) in ((0.9, 2.15, 1.42, 0.07), (0.9, 1.05, 1.42, 0.07), (0.23, 1.6, 0.07, 1.16), (1.57, 1.6, 0.07, 1.16), (0.9, 1.6, 0.04, 1.1)):
        box((x, 2.4, z), (sx, 0.1, sz), frame)
    area((0.9, 3.2, 1.7), (100, 0, 180), 1.4, 450, (1.0, 0.6, 0.32))
    area((-1, -2.5, 2.6), (-60, 0, 20), 3, 60, (0.7, 0.8, 1.0))
    point((-1.2, 0.3, 2.6), 30, (1.0, 0.8, 0.55), 0.15)
    # mesa, sillas, pan y monedas
    tm = M.mat_wood("mesa", (0.32, 0.18, 0.08), (0.45, 0.27, 0.12), 4, 0.4, planks=False)
    box((-0.9, 0.6, 0.74), (1.3, 0.8, 0.05), tm, bevel=0.01)
    for (lx, ly) in ((-1.5, 0.25), (-0.3, 0.25), (-1.5, 0.95), (-0.3, 0.95)):
        box((lx, ly, 0.36), (0.05, 0.05, 0.72), tm)
    box((-0.9, -0.15, 0.45), (0.45, 0.4, 0.04), tm)          # silla
    for (lx, ly) in ((-1.1, -0.32), (-0.7, -0.32), (-1.1, 0.02), (-0.7, 0.02)):
        box((lx, ly, 0.22), (0.04, 0.04, 0.45), tm)
    bread = mat_noise("pan", (0.55, 0.3, 0.1), (0.8, 0.55, 0.25), 10, 0.8, 0.4)
    sphere((-0.55, 0.75, 0.81), 0.1, bread, scale=(1.4, 0.9, 0.6))
    gold = mat("moneda", (0.85, 0.6, 0.25), 0.3, 1.0); silver = mat("moneda2", (0.8, 0.8, 0.8), 0.3, 1.0)
    rnd = random.Random(2)
    for k in range(9):
        cyl((-1.0 + rnd.uniform(-0.18, 0.18), 0.5 + rnd.uniform(-0.12, 0.12), 0.772 + 0.004 * (k % 3)), 0.022, 0.004, gold if k % 3 else silver, verts=24)
    # cortina y cuadro
    cur = mat_noise("cortina", (0.6, 0.15, 0.1), (0.75, 0.25, 0.15), 6, 0.9, 0.2)
    box((0.05, 2.38, 1.55), (0.25, 0.04, 1.6), cur); box((1.75, 2.38, 1.55), (0.25, 0.04, 1.6), cur)


def school_wall(poster_path):
    world_sky(5, 230, 0.16)
    sun(14, 230, 5.0, (1.0, 0.65, 0.38), 0.8)
    conc = mat_noise("vereda", (0.35, 0.34, 0.33), (0.5, 0.49, 0.47), 6, 0.9, 0.3)
    plane((0, 0, 0), (40, 40), conc)
    box((0, 3, 2.5), (14, 0.4, 5), M.mat_brick())
    pm = M.mat_image("cartel", poster_path, 0.75)
    o = plane((0, 2.78, 1.85), (1.4, 1.98), pm, rot=(90, 0, 0))
    o.rotation_euler[1] = math.radians(1.5)
    # cinta adhesiva en las esquinas
    tp = mat("cinta_cartel", (0.85, 0.82, 0.7), 0.6)
    for (x, z) in ((-0.68, 2.82), (0.68, 2.82), (-0.68, 0.88), (0.68, 0.88)):
        box((x, 2.77, z), (0.16, 0.005, 0.05), tp, rot=(0, 30 if x > 0 else -30, 0))
    # ventanas del colegio y otro aviso
    wm = mat("vent_col", (0.2, 0.25, 0.3), 0.08, 0.2)
    for x in (-5, -3, 3, 5):
        box((x, 2.78, 3.3), (1.2, 0.04, 1.2), wm)


def gym():
    world_color((0.75, 0.82, 0.95), 0.6)
    floor = M.mat_wood("parquet", (0.55, 0.33, 0.15), (0.78, 0.52, 0.26), 2.5, 0.18)
    plane((0, 0, 0), (34, 22), floor)
    lm = mat("linea_gym", (0.9, 0.9, 0.9), 0.3)
    pnt = mat("pintura_gym", (0.12, 0.25, 0.6), 0.3)
    plane((0, 6.5, 0.003), (4.9, 5.8), pnt)
    for (x, y, sx, sy) in ((0, 3.6, 4.9, 0.05), (-2.45, 6.5, 0.05, 5.8), (2.45, 6.5, 0.05, 5.8), (0, -4, 15, 0.05), (-7.5, 3, 0.05, 18), (7.5, 3, 0.05, 18)):
        plane((x, y, 0.005), (sx, sy), lm)
    wall_lo = mat("pared_gym_baja", (0.18, 0.35, 0.62), 0.6)
    wall_hi = mat_noise("pared_gym", (0.82, 0.83, 0.85), (0.9, 0.9, 0.92), 3, 0.9, 0.15)
    for (x, y, sx, sy) in ((0, 10.5, 34, 0.2), (-11, 0, 0.2, 22), (11, 0, 0.2, 22)):
        box((x, y, 1.0), (sx, sy, 2.0), wall_lo); box((x, y, 5.0), (sx, sy, 6.0), wall_hi)
    # graderías de madera
    gm = M.mat_wood("graderia", (0.45, 0.28, 0.12), (0.6, 0.4, 0.18), 3, 0.4, planks=False)
    for k in range(5):
        box((-9.2 + k * 0.45, 0, 0.25 + k * 0.45), (0.5, 16, 0.12), gm)
        box((-9.2 + k * 0.45, 0, 0.12 + k * 0.45 / 2), (0.45, 16, 0.25 + k * 0.45), mat("grad_base", (0.25, 0.25, 0.28), 0.6))
    # ventanas altas con luz de día
    sky = mat("ventana_gym", (0.85, 0.92, 1.0), 0.2, emit=(0.85, 0.92, 1.0), emit_s=6.0)
    for x in range(-9, 10, 3):
        box((x, 10.38, 6.6), (2.2, 0.05, 1.3), sky)
    area((0, 9.5, 6.5), (-70, 0, 0), 14, 1200, (0.9, 0.95, 1.0), "RECTANGLE", 2)
    # techo con luminarias
    box((0, 0, 8.1), (34, 22, 0.2), mat("techo_gym", (0.3, 0.3, 0.32), 0.7))
    lamp = mat("luminaria", (1, 1, 1), 0.2, emit=(1.0, 0.97, 0.9), emit_s=12)
    for x in (-6, 0, 6):
        for y in (-4, 2, 8):
            box((x, y, 7.9), (1.8, 0.3, 0.06), lamp)
            area((x, y, 7.7), (0, 0, 0), 1.6, 380, (1.0, 0.96, 0.9))
    hoop(0, 9.3, rusty=False, glass=True)


def poster(path):
    from PIL import Image, ImageDraw, ImageFont
    W, H = 700, 990
    im = Image.new("RGB", (W, H), (245, 238, 220)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 150], fill=(200, 40, 30))
    fb = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Black.otf", 92)
    fm = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf", 120)
    fs = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 40)
    def ctext(y, t, f, c):
        w = d.textlength(t, font=f); d.text(((W - w) / 2, y), t, font=f, fill=c)
    ctext(25, "PRUEBAS", fb, (255, 255, 255))
    ctext(190, "DEL EQUIPO", ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Black.otf", 80), (30, 30, 30))
    ctext(300, "—", fs, (30, 30, 30))
    ctext(360, "VIERNES", fm, (200, 40, 30))
    # balón dibujado
    cx, cy, r = W // 2, 700, 150
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(230, 110, 30), outline=(30, 20, 10), width=8)
    d.line([cx - r, cy, cx + r, cy], fill=(30, 20, 10), width=8); d.line([cx, cy - r, cx, cy + r], fill=(30, 20, 10), width=8)
    d.arc([cx - r - 90, cy - r, cx + r - 210, cy + r], -60, 60, fill=(30, 20, 10), width=8)
    d.arc([cx - r + 210, cy - r, cx + r + 90, cy + r], 120, 240, fill=(30, 20, 10), width=8)
    ctext(900, "GIMNASIO · 15:00", fs, (60, 60, 60))
    im.save(path)


# ---------------------------------------------------------------- tomas
def P_(base, **kw):
    d = dict(base); d.update(kw); return d


def hands_mid(root, info, off=(0, -0.1, 0)):
    return world_point(root, tuple((info["hand_l"] + info["hand_r"]) / 2 + Vector(off)))


SHOTS = {}


def shot(name):
    def deco(fn): SHOTS[name] = fn; return fn
    return deco


# ===== EPISODIO 1
@shot("e1_01_cenital")
def _():
    court(sun_elev=6, sun_azim=235)
    r, i = stickman((0.4, 0.5, 0), 200, 1.25, PEDRITO, M.WALK_DRIBBLE, dict(mood="neutral"))
    ball_at(world_point(r, (0.18, -0.25, 0.35)))
    camera((0.8, -0.6, 5.2), (0.4, 0.7, 0), lens=30, fstop=8)


@shot("e1_02_zapatillas")
def _():
    court(sun_elev=6, sun_azim=235)
    r, i = stickman((0, 0, 0), 15, 1.25, PEDRITO, P_(M.STAND, ll=((-0.01, 0.0, -0.23), (-0.04, 0.03, -0.46)), rl=((0.02, -0.02, -0.23), (0.06, -0.06, -0.46))), dict(mood="neutral"))
    # suela despegada colgando en la punta
    so = mat("suela_rota", (0.7, 0.68, 0.64), 0.8)
    box(tuple(world_point(r, (0.12, -0.2, 0.02))), (0.09, 0.08, 0.02), so, bevel=0.006, rot=(-25, 0, 15))
    fr = world_point(r, tuple(i["foot_r"])); fl = world_point(r, tuple(i["foot_l"]))
    mid = (fr + fl) / 2
    camera(tuple(mid + Vector((0.22, -0.62, 0.12))), tuple(mid + Vector((0, -0.04, 0.04))), lens=50, fstop=2.0)


@shot("e1_03_cancha_baja")
def _():
    court(sun_elev=5, sun_azim=200)
    r, i = stickman((0.6, 2.0, 0), 165, 1.25, PEDRITO, M.WALK_DRIBBLE, dict(mood="neutral"))
    ball_at(world_point(r, (0.14, -0.22, 0.2)))
    camera((-1.2, -2.2, 0.35), (0.3, 4.5, 1.6), lens=24, fstop=4, focus=4.3)


@shot("e1_04_sueno")
def _():
    court(sun_elev=5, sun_azim=200)
    r, i = stickman((0, 3.0, 0), 160, 1.25, PEDRITO, P_(M.HOLD_BALL, head=(-10, 14, 0)), dict(mood="happy", eyes=1.15))
    ball_at(hands_mid(r, i))
    camera((-0.55, 4.5, 0.85), (0.0, 3.0, 1.05), lens=35, fstop=2.2)


@shot("e1_05_casa")
def _():
    house_interior()
    stickman((-0.9, -0.2, 0), 180, 1.45, MAMA, P_(M.SIT_CHAIR, head=(0, -28, 0),
             la=((-0.05, -0.18, -0.05), (0.03, -0.36, -0.03)), ra=((0.05, -0.18, -0.05), (-0.03, -0.36, -0.03))), dict(mood="worried"))
    for o in bpy.data.objects:
        if o.type == "EMPTY" and o.name.startswith("pj"): pass
    stickman((0.95, 1.85, 0), 180, 1.25, PEDRITO, M.WINDOW, dict(mood="sad"))
    camera((1.5, -2.3, 1.45), (-0.3, 0.8, 0.95), lens=24, fstop=4)


@shot("e1_06_monedas")
def _():
    house_interior()
    stickman((-0.9, -0.2, 0), 180, 1.45, MAMA, P_(M.SIT_CHAIR, head=(0, -30, 0),
             la=((-0.05, -0.18, -0.05), (0.03, -0.36, -0.03)), ra=((0.05, -0.18, -0.05), (-0.03, -0.36, -0.03))), dict(mood="worried"))
    camera((-0.45, 1.05, 1.1), (-0.95, 0.45, 0.8), lens=40, fstop=2.2)


@shot("e1_07_cinta")
def _():
    court(sun_elev=6, sun_azim=235)
    r, i = stickman((0, 0, 0), 20, 1.25, PEDRITO, M.SIT_SAD, dict(mood="focused"))
    fr = world_point(r, tuple(i["foot_r"]))
    tp = mat("rollo", (0.6, 0.61, 0.63), 0.3, 0.5)
    torus(tuple(fr + Vector((0.22, -0.08, 0.03))), 0.05, 0.025, tp)
    tube([tuple(fr + Vector((0.17, -0.08, 0.04))), tuple(fr + Vector((0.06, -0.08, 0.05)))], 0.012, tp)
    camera(tuple(fr + Vector((0.32, -0.5, 0.2))), tuple(fr + Vector((0.06, -0.05, 0.03))), lens=50, fstop=2.0)


@shot("e1_08_cartel")
def _():
    p = os.path.join(OUT, "cartel.png"); poster(p)
    school_wall(p)
    for k, (x, y, fc, pose) in enumerate(((-1.4, 1.6, 20, M.STAND), (1.3, 1.5, -25, M.ARMS_CROSSED), (-0.5, 2.0, 5, M.HOLD_BALL), (0.7, 0.9, -160, M.STAND))):
        r, i = stickman((x, y, 0), fc + 180 if k < 3 else fc, 1.2 + 0.05 * (k % 2), KIDS[k], pose, dict(mood="happy"))
    camera((0.2, -2.6, 1.4), (0, 2.6, 1.55), lens=30, fstop=4, focus=4.6)


@shot("e1_09_brillantes")
def _():
    p = os.path.join(OUT, "cartel.png")
    school_wall(p)
    xs = [-0.45, -0.05, 0.38]
    for k, x in enumerate(xs):
        stickman((x, 1.2 + 0.15 * k, 0), 180 + (k - 1) * 12, 1.22, KIDS[k], M.STAND, dict(mood="happy"))
    camera((0.05, 0.4, 0.14), (0.0, 1.35, 0.03), lens=32, fstop=2.0, focus=1.0)


@shot("e1_10_mira_pies")
def _():
    court(sun_elev=5, sun_azim=210)
    r, i = stickman((0, 2.5, 0), 180, 1.25, PEDRITO, P_(M.LOOK_DOWN, head=(0, -30, 0)), dict(mood="determined"))
    ball_at(hands_mid(r, i))
    camera((0.25, 4.35, 1.05), (0, 2.5, 0.85), lens=40, fstop=2.2)


@shot("e1_11_lanzamiento")
def _():
    court(sun_elev=5, sun_azim=200)
    r, i = stickman((0.2, 3.9, 0), 0, 1.25, PEDRITO, M.SHOOT, dict(mood="determined"))
    ball_at((0.1, 6.7, 3.15))
    camera((0.9, 2.2, 0.6), (0.0, 7.0, 2.8), lens=24, fstop=5.6, focus=5.0)


@shot("e1_12_reja")
def _():
    court(sun_elev=4, sun_azim=200, fence_y=-6.5, with_houses=False)
    houses(14)
    r, i = stickman((0.3, 4.0, 0), 0, 1.25, PEDRITO, M.SHOOT, dict(mood="determined"))
    ball_at((0.3, 5.6, 2.9))
    stickman((-0.45, -7.0, 0), 180, 1.7, LUCHO, M.BROOM_BACK, dict(mood="kind"))
    broom = mat("escoba", (0.45, 0.3, 0.12), 0.8)
    tube([(-0.62, -6.85, 0.05), (-0.58, -6.9, 1.45)], 0.02, broom)
    box((-0.63, -6.83, 0.08), (0.3, 0.08, 0.14), mat("cerdas", (0.6, 0.45, 0.2), 0.95))
    camera((-1.75, -10.6, 1.45), (0.0, 2.0, 1.2), lens=35, fstop=2.8, focus=3.8)


def shadow_caster(target, dist):
    """Don Lucho fuera de cuadro: solo su sombra larga (con la escoba) llega a la cancha."""
    sol = [o for o in bpy.data.objects if o.type == "LIGHT" and o.data.type == "SUN"][0]
    bpy.context.view_layer.update()
    d = sol.matrix_world.to_3x3() @ Vector((0, 0, -1)); d.z = 0; d.normalize()
    pos = (target[0] - d.x * dist, target[1] - d.y * dist)
    face = math.degrees(math.atan2(d.x, -d.y))
    r, i = stickman((pos[0], pos[1], 0), face, 1.75, LUCHO, M.STAND, dict(mood="kind"), name="sombra")
    broom = mat("escoba2", (0.45, 0.3, 0.12), 0.8)
    t = tube([(pos[0] + 0.15, pos[1] + 0.3, 0.05), (pos[0] + 0.15, pos[1] + 0.25, 1.55)], 0.025, broom)
    bpy.context.view_layer.update()
    for o in bpy.data.objects:
        if o.name.startswith("sombra") or o == t or (o.parent and o.parent.name.startswith("sombra")):
            o.visible_camera = False
            o.visible_glossy = False


# ===== EPISODIO 2
def gym_kids(line=True):
    poses = [M.WARMUP, M.STAND, M.WARMUP, M.LAUGH, M.STAND]
    for k in range(5):
        stickman((-3.5 + k * 1.1, 1.0 + (k % 2) * 0.25, 0), 180 + (k - 2) * 6 if False else 0, 1.2 + 0.04 * (k % 3), KIDS[k], poses[k], dict(mood="happy"))


@shot("e2_01_gimnasio")
def _():
    gym()
    for k in range(5):
        stickman((-3.6 + k * 1.15, 1.0, 0), 0, 1.2 + 0.04 * (k % 3), KIDS[k], [M.WARMUP, M.STAND, M.WARMUP, M.LAUGH, M.STAND][k], dict(mood="happy"))
    stickman((2.4, 1.0, 0), 0, 1.25, PEDRITO, M.STAND, dict(mood="worried"))
    camera((1.0, -5.8, 2.2), (0.0, 2.0, 1.0), lens=28, fstop=5.6, focus=7.0)


@shot("e2_02_ninos")
def _():
    gym()
    for k in range(3):
        stickman((-0.7 + k * 0.75, 1.0 + (k % 2) * 0.3, 0), (k - 1) * 18, 1.22, KIDS[k], [M.LAUGH, M.WARMUP, M.LAUGH][k], dict(mood="happy"))
    camera((0.1, -1.4, 0.55), (0.0, 1.2, 0.7), lens=32, fstop=2.8, focus=2.5)


@shot("e2_03_cinta_gym")
def _():
    gym()
    r, i = stickman((0, 0, 0), 15, 1.25, PEDRITO, M.STAND, dict(mood="focused"))
    fr = world_point(r, tuple(i["foot_r"]))
    camera(tuple(fr + Vector((0.3, -0.42, 0.1))), tuple(fr + Vector((0, -0.05, 0.03))), lens=55, fstop=1.8)


@shot("e2_04_entrenador")
def _():
    gym()
    stickman((0.0, 0.0, 0), 0, 1.55, COACH, M.WHISTLE, dict(mood="focused"))
    for k in range(3):
        stickman((-2.5 + k * 1.2, 3.5, 0), 0, 1.2, KIDS[k], M.STAND, dict(mood="neutral"))
    camera((0.4, -1.9, 1.25), (0.0, 0.0, 1.35), lens=40, fstop=2.4)


@shot("e2_05_corre")
def _():
    gym()
    r, i = stickman((0.0, 3.0, 0), 25, 1.25, PEDRITO, M.RUN, dict(mood="determined"))
    ball_at(world_point(r, (0.12, -0.3, 0.33)))
    stickman((-1.2, 4.5, 0), 160, 1.24, KIDS[0], P_(M.WARMUP, lean=10), dict(mood="surprised"))
    stickman((1.1, 4.8, 0), 200, 1.2, KIDS[2], P_(M.WARMUP, lean=8), dict(mood="surprised"))
    stickman((3.5, 7.5, 0), -30, 1.55, COACH, M.WHISTLE, dict(mood="focused"))
    camera((1.6, 0.2, 0.75), (0.0, 3.6, 0.9), lens=32, fstop=2.8, focus=3.3)


@shot("e2_06_salto")
def _():
    gym()
    r, i = stickman((0.1, 6.6, 0.55), 0, 1.25, PEDRITO, M.JUMP, dict(mood="determined"))
    ball_at(world_point(r, (0.04, -0.12, 1.32)))
    camera((1.4, 3.6, 0.5), (0.0, 7.4, 2.2), lens=26, fstop=4, focus=3.4)


@shot("e2_07_suela")
def _():
    gym()
    o = dict(PEDRITO, sole_detached="rl")
    r, i = stickman((0.0, 6.0, 0.35), 0, 1.25, o, M.JUMP, dict(mood="surprised"))
    so = mat("suela_vuela", (0.7, 0.68, 0.64), 0.8)
    fr = world_point(r, tuple(i["foot_r"]))
    s = box(tuple(fr + Vector((0.12, -0.2, -0.16))), (0.095, 0.18, 0.022), so, bevel=0.008, rot=(35, 20, 40))
    camera(tuple(fr + Vector((0.55, -1.0, -0.15))), tuple(fr + Vector((0.05, -0.1, -0.05))), lens=45, fstop=2.0)


@shot("e2_08_caida")
def _():
    gym()
    o = dict(PEDRITO, sole_detached="rl")
    r, i = stickman((0.0, 5.5, 0.0), 30, 1.25, o, M.FALL, dict(mood="surprised"))
    ball_at((1.6, 7.4, 0.12))
    camera((-1.3, 3.2, 0.45), (0.1, 5.6, 0.3), lens=32, fstop=2.8, focus=3.0)


@shot("e2_09_risas")
def _():
    gym()
    for k in range(4):
        stickman((-1.6 + k * 1.0, 4.0 + (k % 2) * 0.4, 0), (k - 1.5) * 10, 1.22, KIDS[k], M.LAUGH, dict(mood="happy"))
    o = dict(PEDRITO, sole_detached="rl")
    r, i = stickman((0.25, 0.3, 0), 15, 1.25, o, M.HOLD_SOLE, dict(mood="sad", teary=True))
    so = mat("suela_mano", (0.7, 0.68, 0.64), 0.8)
    box(tuple(world_point(r, tuple(i["hand_l"] + Vector((0, -0.02, 0.02))))), (0.095, 0.18, 0.022), so, bevel=0.008, rot=(70, 0, 15))
    camera((0.55, -1.15, 1.0), (0.2, 0.3, 1.0), lens=45, fstop=1.8, focus=1.55)


@shot("e2_10_sentarte")
def _():
    gym()
    stickman((0.0, 0.0, 0), -15, 1.55, COACH, M.POINT_AWAY, dict(mood="neutral"))
    camera((-0.6, -1.9, 1.15), (0.1, 0.0, 1.35), lens=40, fstop=2.4)


@shot("e2_11_solo")
def _():
    court(sun_elev=12, sun_azim=250, sky=0.16, sun_e=4.5)
    stickman((0.5, 0.5, 0), -10, 1.25, PEDRITO, M.SIT_SAD, dict(mood="sad"))
    shadow_caster((0.5, 0.5), 15)
    camera((-3.8, -6.5, 1.6), (0.3, 1.0, 0.7), lens=32, fstop=4, focus=8.0)


@shot("e2_12_sombra")
def _():
    court(sun_elev=12, sun_azim=250, sky=0.16, sun_e=4.5)
    stickman((0.5, 0.5, 0), -10, 1.25, PEDRITO, P_(M.SIT_SAD, head=(-30, 10, 0)), dict(mood="surprised"))
    # alguien detrás, fuera de cuadro: solo su sombra larga llega hasta Pedrito
    shadow_caster((0.5, 0.5), 4.2)
    camera((1.9, -3.2, 1.0), (0.3, 0.8, 0.45), lens=30, fstop=3.2, focus=3.8)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    names = sys.argv[2:] or list(SHOTS)
    samples = int(os.environ.get("SAMPLES", "28"))
    if os.environ.get("PREVIEW"):
        M.RES = (405, 720)
    import time
    for n in names:
        t = time.time()
        M.reset(samples)
        SHOTS[n]()
        M.render(os.path.join(OUT, n + ".png"))
        print(f"{n} {time.time() - t:.1f}s", flush=True)
