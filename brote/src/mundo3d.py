"""Mundo 3D de Brote (Blender/Cycles en modo script).
Personajes stickman 3D: cabeza blanca redonda, ojos de punto, cejas expresivas, ropa de colores lisos,
brazos y piernas de palito negro. Entornos 3D realistas con luz natural y profundidad de campo."""
import math, random
import bpy
from mathutils import Vector, Euler, Matrix

RES = (1215, 2160)          # 9:16 con margen para movimientos de cámara suaves


# ------------------------------------------------------------------ escena y render
def reset(samples=28):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _mats.clear()
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.03
    sc.cycles.use_denoising = True
    try: sc.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception: pass
    sc.cycles.max_bounces = 5; sc.cycles.diffuse_bounces = 3; sc.cycles.glossy_bounces = 2
    sc.cycles.transmission_bounces = 2; sc.cycles.transparent_max_bounces = 8
    sc.render.resolution_x, sc.render.resolution_y = RES
    sc.render.film_transparent = False
    try:
        sc.view_settings.view_transform = "AgX"
        sc.view_settings.look = "AgX - Punchy"
    except Exception:
        try: sc.view_settings.look = "Medium High Contrast"
        except Exception: pass
    sc.render.image_settings.file_format = "PNG"
    return sc


def world_sky(sun_elev=6, sun_rot=200, strength=1.0, turbidity=None):
    w = bpy.data.worlds.new("cielo"); bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree; bg = nt.nodes["Background"]
    sky = nt.nodes.new("ShaderNodeTexSky")
    for t in ("MULTIPLE_SCATTERING", "NISHITA", "HOSEK_WILKIE"):
        try: sky.sky_type = t; break
        except Exception: continue
    try:
        sky.sun_elevation = math.radians(sun_elev); sky.sun_rotation = math.radians(sun_rot)
        sky.sun_disc = False; sky.air_density = 1.0; sky.dust_density = 2.5
    except Exception: pass
    nt.links.new(sky.outputs[0], bg.inputs[0])
    bg.inputs[1].default_value = strength
    return w


def world_color(c, s=1.0):
    w = bpy.data.worlds.new("fondo"); bpy.context.scene.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (*c, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = s


def sun(elev, azim, energy=4.0, color=(1.0, 0.75, 0.5), angle=1.0):
    d = bpy.data.lights.new("sol", "SUN"); d.energy = energy; d.color = color; d.angle = math.radians(angle)
    o = bpy.data.objects.new("sol", d); bpy.context.collection.objects.link(o)
    o.rotation_euler = Euler((math.radians(90 - elev), 0, math.radians(azim)), "XYZ")
    return o


def area(loc, rot, size, energy, color=(1, 1, 1), shape="RECTANGLE", size_y=None):
    d = bpy.data.lights.new("area", "AREA"); d.energy = energy; d.color = color; d.size = size
    if size_y: d.shape = shape; d.size_y = size_y
    o = bpy.data.objects.new("area", d); bpy.context.collection.objects.link(o)
    o.location = loc; o.rotation_euler = Euler([math.radians(a) for a in rot])
    return o


def point(loc, energy, color=(1, 0.8, 0.6), radius=0.1):
    d = bpy.data.lights.new("p", "POINT"); d.energy = energy; d.color = color; d.shadow_soft_size = radius
    o = bpy.data.objects.new("p", d); bpy.context.collection.objects.link(o); o.location = loc
    return o


def camera(loc, target, lens=35, fstop=2.8, focus=None, roll=0):
    d = bpy.data.cameras.new("cam"); d.lens = lens; d.sensor_width = 36
    o = bpy.data.objects.new("cam", d); bpy.context.collection.objects.link(o)
    o.location = loc
    direction = Vector(target) - Vector(loc)
    o.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    o.rotation_euler.rotate_axis("Z", math.radians(roll))
    d.dof.use_dof = fstop is not None
    if fstop:
        d.dof.aperture_fstop = fstop
        d.dof.focus_distance = focus if focus else direction.length
    bpy.context.scene.camera = o
    return o


def render(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


# ------------------------------------------------------------------ materiales
_mats = {}


def mat(name, color, rough=0.6, metal=0.0, spec=0.5, emit=None, emit_s=0.0, coat=0.0):
    key = (name, tuple(color), rough, metal, emit, emit_s)
    if key in _mats and _mats[key].name in bpy.data.materials: return _mats[key]
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if coat:
        try: b.inputs["Coat Weight"].default_value = coat
        except Exception: pass
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = emit_s
    _mats[key] = m
    return m


def mat_noise(name, c1, c2, scale=8.0, rough=0.8, bump=0.3, detail=8.0, metal=0.0):
    """Material con variación procedural (concreto, óxido, madera gastada...)."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = detail
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*c1, 1); ramp.color_ramp.elements[1].color = (*c2, 1)
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if bump > 0:
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
        nz2 = nt.nodes.new("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = scale * 12
        nt.links.new(tc.outputs["Object"], nz2.inputs["Vector"])
        nt.links.new(nz2.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def mat_wood(name="madera", c1=(0.55, 0.32, 0.15), c2=(0.78, 0.52, 0.28), scale=2.0, rough=0.25, planks=True):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale, scale * 0.12, scale)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 3.0
    wv.inputs["Distortion"].default_value = 6.0; wv.inputs["Detail"].default_value = 4
    nt.links.new(mp.outputs["Vector"], wv.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*c1, 1); ramp.color_ramp.elements[1].color = (*c2, 1)
    nt.links.new(wv.outputs["Fac"], ramp.inputs["Fac"])
    if planks:
        br = nt.nodes.new("ShaderNodeTexBrick")
        br.inputs["Scale"].default_value = 1.0; br.inputs["Mortar Size"].default_value = 0.004
        br.inputs["Brick Width"].default_value = 1.6; br.inputs["Row Height"].default_value = 0.14
        br.inputs["Color1"].default_value = (1, 1, 1, 1); br.inputs["Color2"].default_value = (0.82, 0.8, 0.78, 1)
        br.inputs["Mortar"].default_value = (0.35, 0.3, 0.25, 1)
        nt.links.new(tc.outputs["Object"], br.inputs["Vector"])
        mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        nt.links.new(ramp.outputs["Color"], mix.inputs["A"]); nt.links.new(br.outputs["Color"], mix.inputs["B"])
        nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    else:
        nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    try: b.inputs["Coat Weight"].default_value = 0.3
    except Exception: pass
    return m


def mat_brick(name="ladrillo"):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    br = nt.nodes.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = 4.0
    br.inputs["Color1"].default_value = (0.42, 0.15, 0.09, 1); br.inputs["Color2"].default_value = (0.55, 0.22, 0.12, 1)
    br.inputs["Mortar"].default_value = (0.6, 0.58, 0.55, 1); br.inputs["Mortar Size"].default_value = 0.015
    nt.links.new(tc.outputs["Object"], br.inputs["Vector"])
    nt.links.new(br.outputs["Color"], b.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.4
    nt.links.new(br.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = 0.9
    return m


def mat_image(name, path, rough=0.7, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = bpy.data.images.load(path)
    nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    if emit:
        nt.links.new(tx.outputs["Color"], b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = emit
    return m


def mat_fence(name="reja"):
    """Malla de alambre (chain-link) con transparencia procedural."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; out = nt.nodes["Material Output"]; b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.45, 0.45, 0.47, 1); b.inputs["Metallic"].default_value = 0.9
    b.inputs["Roughness"].default_value = 0.45
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Rotation"].default_value = (0, 0, math.radians(45))
    mp.inputs["Scale"].default_value = (16, 16, 16)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(mp.outputs["Vector"], sep.inputs[0])
    def wire(axis):
        fr = nt.nodes.new("ShaderNodeMath"); fr.operation = "PINGPONG"; fr.inputs[1].default_value = 0.5
        nt.links.new(sep.outputs[axis], fr.inputs[0])
        lt = nt.nodes.new("ShaderNodeMath"); lt.operation = "LESS_THAN"; lt.inputs[1].default_value = 0.035
        nt.links.new(fr.outputs[0], lt.inputs[0]); return lt
    a, c = wire(0), wire(1)
    mx = nt.nodes.new("ShaderNodeMath"); mx.operation = "MAXIMUM"
    nt.links.new(a.outputs[0], mx.inputs[0]); nt.links.new(c.outputs[0], mx.inputs[1])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(mx.outputs[0], mix.inputs[0]); nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(b.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def mat_ball(name="balon"):
    """Balón naranja con costuras negras."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sep.inputs[0])
    def band(expr_node):
        ab = nt.nodes.new("ShaderNodeMath"); ab.operation = "ABSOLUTE"; nt.links.new(expr_node, ab.inputs[0])
        lt = nt.nodes.new("ShaderNodeMath"); lt.operation = "LESS_THAN"; lt.inputs[1].default_value = 0.006
        nt.links.new(ab.outputs[0], lt.inputs[0]); return lt.outputs[0]
    bx = band(sep.outputs[0]); bz = band(sep.outputs[2])
    # costura curva: |y| - 0.6*(x²...) aproximada con seno
    sn = nt.nodes.new("ShaderNodeMath"); sn.operation = "SINE"
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = 14.0
    nt.links.new(sep.outputs[2], mul.inputs[0]); nt.links.new(mul.outputs[0], sn.inputs[0])
    sc = nt.nodes.new("ShaderNodeMath"); sc.operation = "MULTIPLY"; sc.inputs[1].default_value = 0.05
    nt.links.new(sn.outputs[0], sc.inputs[0])
    sub = nt.nodes.new("ShaderNodeMath"); sub.operation = "SUBTRACT"
    nt.links.new(sep.outputs[1], sub.inputs[0]); nt.links.new(sc.outputs[0], sub.inputs[1])
    by = band(sub.outputs[0])
    m1 = nt.nodes.new("ShaderNodeMath"); m1.operation = "MAXIMUM"; nt.links.new(bx, m1.inputs[0]); nt.links.new(bz, m1.inputs[1])
    m2 = nt.nodes.new("ShaderNodeMath"); m2.operation = "MAXIMUM"; nt.links.new(m1.outputs[0], m2.inputs[0]); nt.links.new(by, m2.inputs[1])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (0.75, 0.24, 0.05, 1); mix.inputs["B"].default_value = (0.02, 0.02, 0.02, 1)
    nt.links.new(m2.outputs[0], mix.inputs["Factor"])
    nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.65
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.15
    vz = nt.nodes.new("ShaderNodeTexVoronoi"); vz.inputs["Scale"].default_value = 300
    nt.links.new(tc.outputs["Object"], vz.inputs["Vector"]); nt.links.new(vz.outputs["Distance"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


# ------------------------------------------------------------------ primitivas
def _link(o):
    if o.name not in bpy.context.collection.objects: bpy.context.collection.objects.link(o)
    return o


def box(loc, size, material, bevel=0.0, rot=(0, 0, 0), name="caja"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=[math.radians(r) for r in rot])
    o = bpy.context.object; o.name = name; o.scale = size
    if bevel:
        bpy.ops.object.transform_apply(scale=True)
        md = o.modifiers.new("bv", "BEVEL"); md.width = bevel; md.segments = 3
    o.data.materials.append(material)
    return o


def cyl(loc, r, depth, material, rot=(0, 0, 0), verts=32, name="cil", smooth=True):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=[math.radians(a) for a in rot], vertices=verts)
    o = bpy.context.object; o.name = name; o.data.materials.append(material)
    if smooth: bpy.ops.object.shade_smooth()
    return o


def sphere(loc, r, material, scale=(1, 1, 1), name="esf", seg=32):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=seg // 2)
    o = bpy.context.object; o.name = name; o.scale = scale
    o.data.materials.append(material); bpy.ops.object.shade_smooth()
    return o


def torus(loc, R, r, material, rot=(0, 0, 0), name="toro"):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc, rotation=[math.radians(a) for a in rot])
    o = bpy.context.object; o.name = name; o.data.materials.append(material); bpy.ops.object.shade_smooth()
    return o


def plane(loc, size, material, rot=(0, 0, 0), name="plano"):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=[math.radians(a) for a in rot])
    o = bpy.context.object; o.name = name; o.scale = (size[0], size[1], 1)
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(material)
    return o


def tube(points, r, material, name="tubo"):
    """Tubo suave por una lista de puntos (extremidades de palito)."""
    cd = bpy.data.curves.new(name, "CURVE"); cd.dimensions = "3D"
    cd.bevel_depth = r; cd.bevel_resolution = 4; cd.use_fill_caps = True
    sp = cd.splines.new("POLY"); sp.points.add(len(points) - 1)
    for p, q in zip(sp.points, points): p.co = (*q, 1)
    o = bpy.data.objects.new(name, cd); _link(o)
    o.data.materials.append(material)
    return o


def smooth_tube(points, r, material, name="tubo"):
    cd = bpy.data.curves.new(name, "CURVE"); cd.dimensions = "3D"
    cd.bevel_depth = r; cd.bevel_resolution = 4; cd.use_fill_caps = True
    sp = cd.splines.new("BEZIER"); sp.bezier_points.add(len(points) - 1)
    for p, q in zip(sp.bezier_points, points):
        p.co = q; p.handle_left_type = p.handle_right_type = "AUTO"
    o = bpy.data.objects.new(name, cd); _link(o); o.data.materials.append(material)
    return o


def text3d(body, loc, size, material, rot=(90, 0, 0), extrude=0.0, align="CENTER", font_path=None):
    cd = bpy.data.curves.new("txt", "FONT"); cd.body = body; cd.size = size; cd.extrude = extrude
    cd.align_x = align
    if font_path: cd.font = bpy.data.fonts.load(font_path)
    o = bpy.data.objects.new("txt", cd); _link(o); o.location = loc
    o.rotation_euler = Euler([math.radians(a) for a in rot]); o.data.materials.append(material)
    return o


def parent_all(objs, root):
    for o in objs:
        o.parent = root


# ------------------------------------------------------------------ personajes stickman 3D
WHITE_HEAD = None


def head_mat():
    m = bpy.data.materials.new("cabeza"); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.93, 0.92, 0.9, 1); b.inputs["Roughness"].default_value = 0.42
    try:
        b.inputs["Subsurface Weight"].default_value = 0.15
        b.inputs["Subsurface Radius"].default_value = (0.3, 0.25, 0.2)
        b.inputs["Coat Weight"].default_value = 0.15
    except Exception: pass
    return m


BLACK = None


def stickman(loc=(0, 0, 0), facing=0.0, height=1.25, outfit=None, pose=None, face=None, name="pj"):
    """Crea un personaje. facing: grados (0 = mira hacia -Y, a cámara frontal).
    pose: dict con hip (alto de cadera, 0..1 relativo), lean (grados hacia delante),
    la/ra: (codo, mano) relativos al hombro; ll/rl: (rodilla, pie) relativos a la cadera; head: (yaw, pitch, roll)."""
    o = outfit or {}; p = pose or {}; f = face or {}
    s = height / 1.25
    root = bpy.data.objects.new(name, None); _link(root)
    objs = []
    blk = mat("palito", (0.004, 0.004, 0.004), 0.35)
    shirt = mat(name + "_ropa", o.get("shirt", (0.6, 0.05, 0.04)), o.get("shirt_rough", 0.85))
    pants = mat(name + "_pant", o.get("pants", (0.05, 0.07, 0.15)), 0.85)
    hip_z = 0.50 * p.get("hip", 1.0)
    lean = math.radians(p.get("lean", 0))
    hipc = Vector((0, 0, hip_z))
    up = Vector((0, -math.sin(lean), math.cos(lean)))       # inclinación hacia delante (-Y)
    torso_h = 0.33
    neck = hipc + up * torso_h
    # torso (polera) y pantalón/short
    t = box(tuple(hipc + up * (torso_h * 0.5 + 0.04)), (0.27, 0.17, torso_h * 0.86), shirt, bevel=0.06, rot=(-math.degrees(lean), 0, 0), name=name + "_torso")
    objs.append(t)
    if o.get("apron"):
        ap = mat(name + "_delantal", o["apron"], 0.8)
        objs.append(box(tuple(hipc + up * (torso_h * 0.42) + Vector((0, -0.088, 0))), (0.22, 0.02, torso_h * 0.75), ap, bevel=0.01, rot=(-math.degrees(lean), 0, 0)))
    sh = box(tuple(hipc + Vector((0, 0, -0.02))), (0.25, 0.16, 0.13), pants, bevel=0.04, name=name + "_short")
    objs.append(sh)
    if o.get("long_pants"):
        pass
    # cabeza
    hr = 0.19
    hc = neck + up * 0.03 + Vector((0, 0, hr + 0.02))
    objs.append(tube([tuple(neck), tuple(neck + Vector((0, 0, 0.06)))], 0.02, blk))
    head = sphere(tuple(hc), hr, head_mat(), name=name + "_cabeza", seg=48)
    objs.append(head)
    yaw, pitch, roll = [math.radians(v) for v in p.get("head", (0, 0, 0))]
    Rh = Euler((-pitch, roll, yaw), "XYZ").to_matrix()
    def on_head(vec):     # vec en coordenadas de la cabeza (-Y = cara)
        return hc + Rh @ Vector(vec)
    # ojos de punto (con brillo)
    eye = mat("ojo", (0.005, 0.005, 0.005), 0.08)
    shine = mat("brillo", (1, 1, 1), 0.2, emit=(1, 1, 1), emit_s=2.0)
    ey = f.get("eye_y", 0.0)
    eyes_big = f.get("eyes", 1.0)
    for sx in (-1, 1):
        ex = sx * 0.062
        pos = on_head((ex, -hr * 0.96, 0.015 + ey))
        e = sphere(tuple(pos), 0.022 * eyes_big, eye, scale=(1, 0.55, 1.15), seg=16)
        e.rotation_euler = Euler((-pitch, roll, yaw)); objs.append(e)
        if f.get("teary"):
            tr = sphere(tuple(on_head((ex + 0.008, -hr * 1.0, 0.024 + ey))), 0.008, shine, seg=12); objs.append(tr)
            wet = mat("lagrima", (0.6, 0.8, 1.0), 0.02, emit=(0.6, 0.8, 1), emit_s=0.6)
            objs.append(sphere(tuple(on_head((ex, -hr * 0.98, -0.012 + ey))), 0.011, wet, scale=(1.3, 0.5, 0.6), seg=12))
        else:
            objs.append(sphere(tuple(on_head((ex + 0.007, -hr * 1.0, 0.026 + ey))), 0.006, shine, seg=10))
    # cejas expresivas: (ángulo interior, altura)
    mood = f.get("mood", "neutral")
    brow = {"neutral": (0, 0.0), "sad": (-22, 0.006), "determined": (20, -0.01), "surprised": (-4, 0.028),
            "happy": (-8, 0.012), "worried": (-28, 0.012), "focused": (14, -0.006), "kind": (-14, 0.008)}[mood]
    for sx in (-1, 1):
        ang = math.radians(brow[0]) * sx
        c = Vector((sx * 0.064, -hr * 0.93, 0.075 + brow[1] + ey))
        d = Vector((math.cos(ang) * 0.032, 0, math.sin(-ang) * 0.032 * -1))
        a0 = on_head(tuple(c - d)); a1 = on_head(tuple(c + d))
        objs.append(tube([tuple(a0), tuple(a1)], 0.0085, blk))
    # pelo y accesorios
    hair = o.get("hair")
    if hair == "curly":
        hm = mat("pelo_negro", (0.004, 0.0035, 0.003), 0.6)
        rnd = random.Random(3)
        for k in range(46):
            th = rnd.uniform(0, 2 * math.pi); ph = rnd.uniform(0, math.radians(72))
            v = Vector((math.sin(ph) * math.cos(th), math.sin(ph) * math.sin(th), math.cos(ph)))
            if v.y < -0.55 and v.z < 0.75: continue      # despeja la cara
            objs.append(sphere(tuple(on_head(tuple(v * hr * 1.0))), rnd.uniform(0.038, 0.05), hm, seg=12))
    elif hair == "bun":
        hm = mat("pelo_cafe", o.get("hair_color", (0.12, 0.06, 0.03)), 0.6)
        objs.append(sphere(tuple(on_head((0, 0.02, 0.03))), hr * 1.04, hm, scale=(1, 1, 0.82)))
        objs.append(sphere(tuple(on_head((0, 0.12, 0.17))), 0.075, hm))
    elif hair == "short":
        hm = mat("pelo_" + name, o.get("hair_color", (0.05, 0.03, 0.02)), 0.6)
        objs.append(sphere(tuple(on_head((0, 0.03, 0.05))), hr * 1.03, hm, scale=(1, 1, 0.78)))
    elif hair == "pony":
        hm = mat("pelo_" + name, o.get("hair_color", (0.2, 0.09, 0.03)), 0.6)
        objs.append(sphere(tuple(on_head((0, 0.03, 0.05))), hr * 1.03, hm, scale=(1, 1, 0.78)))
        objs.append(smooth_tube([tuple(on_head((0, 0.17, 0.08))), tuple(on_head((0, 0.25, -0.05))), tuple(on_head((0, 0.24, -0.18)))], 0.035, hm))
    if o.get("cap"):
        cm = mat(name + "_gorra", o["cap"], 0.7)
        objs.append(sphere(tuple(on_head((0, 0.0, 0.06))), hr * 1.05, cm, scale=(1, 1, 0.7)))
        objs.append(box(tuple(on_head((0, -hr * 1.05, 0.08))), (0.2, 0.14, 0.015), cm, bevel=0.005, rot=(-math.degrees(pitch), 0, math.degrees(yaw))))
    if o.get("moustache"):
        mm = mat("bigote", o["moustache"], 0.8)
        for sx in (-1, 1):
            objs.append(sphere(tuple(on_head((sx * 0.035, -hr * 0.97, -0.045))), 0.035, mm, scale=(1.2, 0.5, 0.55), seg=16))
    if o.get("whistle"):
        sil = mat("silbato", (0.8, 0.8, 0.82), 0.2, metal=1.0)
        w0 = on_head((0, -0.05, -hr * 0.9)); objs.append(sphere(tuple(neck + Vector((0, -0.11, -0.1))), 0.022, sil, seg=16))
    # extremidades de palito
    r = 0.017
    shw = 0.15
    side = Vector((1, 0, 0))
    for sx, key in ((-1, "la"), (1, "ra")):
        shp = neck + side * sx * shw + Vector((0, 0, -0.03))
        el, ha = p.get(key, ((sx * 0.06, 0.0, -0.2), (sx * 0.08, -0.02, -0.4)))
        e = shp + Vector(el); h = shp + Vector(ha)
        objs.append(tube([tuple(shp), tuple(e), tuple(h)], r, blk))
        objs.append(sphere(tuple(h), 0.035, blk, seg=16))
        objs.append(sphere(tuple(shp), 0.03, shirt, seg=16))
        if key == "ra": hand_r = h
        else: hand_l = h
    sole_detached = o.get("sole_detached")
    for sx, key in ((-1, "ll"), (1, "rl")):
        hp = hipc + side * sx * 0.075 + Vector((0, 0, -0.04))
        kn, ft = p.get(key, ((sx * 0.01, 0.0, -0.23), (sx * 0.02, 0.0, -0.46)))
        k = hp + Vector(kn); fpos = hp + Vector(ft)
        if key == "rl": foot_r = fpos
        else: foot_l = fpos
        objs.append(tube([tuple(hp), tuple(k), tuple(fpos)], r * 1.1, blk))
        # zapatilla
        shoe = o.get("shoe", (0.85, 0.85, 0.85))
        fy = p.get("foot_dir", 0.0)
        sm = mat(name + "_zapa", shoe, 0.18 if o.get("shiny") else 0.6, coat=0.8 if o.get("shiny") else 0.0)
        so = mat("suela", o.get("sole", (0.9, 0.9, 0.88)), 0.8)
        ang = math.radians(p.get(key + "_toe", 0))
        sz = box(tuple(fpos + Vector((0, -0.045, 0.02))), (0.09, 0.17, 0.065), sm, bevel=0.028, rot=(math.degrees(ang), 0, 0))
        objs.append(sz)
        if not (sole_detached and key == sole_detached):
            objs.append(box(tuple(fpos + Vector((0, -0.045, -0.02))), (0.095, 0.18, 0.022), so, bevel=0.008, rot=(math.degrees(ang), 0, 0)))
        if o.get("tape"):
            tp = mat("cinta", (0.6, 0.61, 0.63), 0.28, metal=0.55)
            for ty in (-0.1, -0.02):
                objs.append(box(tuple(fpos + Vector((0, ty, 0.012))), (0.104, 0.035, 0.08), tp, bevel=0.022, rot=(math.degrees(ang), 0, 0)))
        if o.get("shiny_shoes"):
            pass
    for ob in objs:
        if ob.parent is None: ob.parent = root
    root.location = loc
    root.rotation_euler = (0, 0, math.radians(facing))
    root.scale = (s, s, s)
    return root, dict(hand_r=hand_r, hand_l=hand_l, head=hc, neck=neck, hip=hipc, foot_r=foot_r, foot_l=foot_l)


def world_point(root, local):
    bpy.context.view_layer.update()
    return root.matrix_world @ Vector(local)


# ------------------------------------------------------------------ poses
def P(**kw): return kw


STAND = P()
HOLD_BALL = P(la=((-0.02, -0.12, -0.12), (0.08, -0.25, -0.18)), ra=((0.02, -0.12, -0.12), (-0.08, -0.25, -0.18)))
LOOK_DOWN = dict(HOLD_BALL, head=(0, -24, 0))
SHOOT = P(la=((-0.04, -0.1, 0.18), (0.03, -0.12, 0.38)), ra=((0.08, -0.08, 0.2), (0.06, -0.12, 0.42)), head=(0, 14, 0),
          ll=((-0.01, -0.02, -0.23), (-0.02, 0.0, -0.46)), rl=((0.01, -0.02, -0.23), (0.02, 0.0, -0.46)))
RUN = P(lean=14, la=((-0.04, 0.12, -0.14), (-0.04, 0.04, -0.3)), ra=((0.04, -0.14, -0.1), (0.05, -0.27, -0.02)),
        ll=((-0.01, -0.18, -0.15), (-0.02, -0.12, -0.4)), rl=((0.01, 0.12, -0.2), (0.02, 0.24, -0.34)), head=(0, 5, 0))
JUMP = P(hip=1.0, lean=6, la=((-0.04, -0.1, 0.16), (-0.02, -0.12, 0.36)), ra=((0.08, -0.06, 0.18), (0.06, -0.1, 0.4)),
         ll=((-0.01, -0.18, -0.12), (-0.02, -0.02, -0.34)), rl=((0.01, 0.05, -0.22), (0.02, 0.12, -0.42)), head=(0, 12, 0))
FALL = P(hip=0.55, lean=-40, la=((-0.18, 0.05, 0.05), (-0.3, -0.05, 0.12)), ra=((0.2, 0.04, 0.0), (0.32, -0.08, 0.05)),
         ll=((-0.02, -0.22, 0.02), (-0.03, -0.42, -0.06)), rl=((0.04, -0.2, -0.05), (0.06, -0.38, -0.2)), head=(0, -10, 8))
SIT_SAD = P(hip=0.38, lean=18, la=((-0.04, -0.16, -0.06), (0.04, -0.28, 0.02)), ra=((0.04, -0.16, -0.06), (-0.04, -0.28, 0.02)),
            ll=((-0.02, -0.22, 0.1), (-0.03, -0.28, -0.15)), rl=((0.02, -0.22, 0.1), (0.03, -0.28, -0.15)), head=(0, -22, 0))
HOLD_SOLE = P(la=((-0.04, -0.1, -0.14), (0.02, -0.24, -0.1)), ra=((0.06, 0.0, -0.2), (0.08, 0.02, -0.4)), head=(0, -18, 0))
WALK_DRIBBLE = P(la=((-0.04, 0.06, -0.2), (-0.06, 0.02, -0.38)), ra=((0.06, -0.08, -0.16), (0.1, -0.18, -0.3)),
                 ll=((-0.01, -0.08, -0.22), (-0.02, -0.12, -0.44)), rl=((0.01, 0.06, -0.22), (0.02, 0.12, -0.44)), head=(0, 4, 0))
WARMUP = P(la=((-0.2, 0.0, 0.05), (-0.36, 0.0, 0.1)), ra=((0.2, 0.0, 0.05), (0.36, 0.0, 0.1)))
LAUGH = P(lean=-8, la=((-0.1, -0.06, -0.12), (-0.02, -0.08, -0.05)), ra=((0.1, -0.06, -0.12), (0.02, -0.08, -0.05)), head=(0, 18, 0))
POINT_AWAY = P(ra=((0.2, -0.05, 0.02), (0.4, -0.06, 0.08)), la=((-0.08, 0.04, -0.18), (-0.06, 0.02, -0.38)), head=(25, 0, 0))
ARMS_CROSSED = P(la=((-0.06, -0.12, -0.14), (0.12, -0.14, -0.08)), ra=((0.06, -0.12, -0.12), (-0.12, -0.15, -0.06)))
WHISTLE = P(ra=((0.05, -0.12, -0.04), (-0.03, -0.12, 0.1)), la=((-0.06, 0.0, -0.2), (-0.08, 0.0, -0.4)))
WINDOW = P(la=((-0.04, -0.12, -0.08), (0.03, -0.2, 0.0)), ra=((0.04, -0.12, -0.08), (-0.03, -0.2, 0.0)), head=(0, 6, 0))
SIT_CHAIR = P(hip=0.92, ll=((-0.01, -0.24, 0.0), (-0.02, -0.24, -0.24)), rl=((0.01, -0.24, 0.0), (0.02, -0.24, -0.24)),
              la=((-0.04, -0.14, -0.1), (0.0, -0.3, -0.06)), ra=((0.04, -0.14, -0.1), (0.02, -0.3, -0.06)), head=(0, -20, 0))
BROOM_BACK = P(ra=((0.06, -0.1, -0.12), (0.02, -0.16, 0.02)), la=((-0.06, -0.08, -0.16), (-0.02, -0.16, -0.22)), head=(0, -4, 0))
