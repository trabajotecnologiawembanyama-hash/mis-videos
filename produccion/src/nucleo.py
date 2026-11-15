"""El personaje: la IA ('el Núcleo'). Mismo diseño en todas las escenas; solo cambian escala, temperatura y energía."""
import math
import numpy as np

_cache = {}

COLD = np.array([0.30, 0.78, 1.00], np.float32)
WARM = np.array([1.00, 0.62, 0.28], np.float32)
WHITE_HOT = np.array([1.00, 0.92, 0.80], np.float32)


def _grid(S):
    if S not in _cache:
        y, x = np.mgrid[0:S, 0:S].astype(np.float32)
        x = (x - S / 2 + 0.5) / S; y = (y - S / 2 + 0.5) / S
        r = np.sqrt(x * x + y * y)
        th = np.arctan2(y, x)
        rng = np.random.default_rng(3)
        # textura radial del iris (fibras)
        k = np.arange(1, 90)
        ph = rng.uniform(0, 2 * np.pi, k.size); amp = rng.uniform(0.2, 1.0, k.size) / np.sqrt(k)
        thl = np.linspace(-np.pi, np.pi, 2048, dtype=np.float32)
        fib = (amp[:, None] * np.sin(k[:, None] * thl[None, :] * 1.0 + ph[:, None])).sum(0)
        fib = (fib - fib.min()) / (fib.max() - fib.min())
        idx = ((th + np.pi) / (2 * np.pi) * 2047).astype(np.int32)
        fibers = fib[idx].astype(np.float32)
        _cache[S] = (r, th, fibers)
    return _cache[S]


def g(r, r0, w):
    return np.exp(-((r - r0) / w) ** 2)


def ai_core(S, t, warm=0.0, energy=1.0, pupil=1.0):
    """Devuelve luz aditiva (S,S,3). warm 0 = azul frío, 1 = cálido. energy escala brillo/rotación."""
    r, th, fibers = _grid(S)
    col = COLD * (1 - warm) + WARM * warm
    px = 1.0 / S
    def w(v): return max(v, 1.4 * px)
    L = np.zeros((S, S), np.float32)          # canal "color"
    Hh = np.zeros((S, S), np.float32)         # canal "blanco cálido" (núcleo)

    # anillo exterior punteado
    dash = (np.sin(th * 72 + t * 0.35) > -0.2).astype(np.float32)
    L += 0.55 * g(r, 0.465, w(0.0022)) * dash
    # anillo principal con 3 arcos que giran
    arcs = np.clip(np.sin(th * 3 + t * 0.6) * 4 - 1.6, 0, 1)
    L += 0.95 * g(r, 0.405, w(0.006)) * (0.25 + 0.75 * arcs)
    # marcas de escala (120)
    tick = (np.mod((th + t * 0.08) * 120 / (2 * np.pi), 1.0) < 0.18).astype(np.float32)
    big = (np.mod((th + t * 0.08) * 12 / (2 * np.pi), 1.0) < 0.018).astype(np.float32)
    L += 0.5 * tick * ((r > 0.335) & (r < 0.352)) + 0.9 * big * ((r > 0.325) & (r < 0.362))
    # anillo interior segmentado, gira al revés
    seg = (np.mod((th - t * 0.9) * 8 / (2 * np.pi), 1.0) < 0.78).astype(np.float32)
    L += 0.8 * g(r, 0.262, w(0.009)) * seg
    L += 0.35 * g(r, 0.29, w(0.0016))
    # iris: fibras radiales que respiran
    breath = 1 + 0.06 * math.sin(t * 2.1)
    iris = np.clip((0.2 * breath - r) / 0.2, 0, 1)
    L += 1.1 * iris ** 0.7 * (0.35 + 0.9 * fibers) * (r > 0.055 * pupil)
    L += 0.5 * g(r, 0.2 * breath, w(0.006))
    # pupila: anillo blanco caliente + vacío
    Hh += 1.6 * g(r, 0.06 * pupil, w(0.0045))
    Hh += 0.9 * np.exp(-r / 0.022)
    # halo
    L += 0.20 * np.exp(-np.maximum(r - 0.2, 0) / 0.09) * (r > 0.2)
    L += 0.06 * np.exp(-r / 0.3)
    # rejilla hexagonal muy tenue
    hexg = (np.abs(np.sin(th * 30)) * np.abs(np.sin(r * 180))) > 0.97
    L += 0.06 * hexg * (r < 0.45)

    out = L[..., None] * col[None, None, :] * energy + Hh[..., None] * WHITE_HOT[None, None, :] * energy
    fade = np.clip((0.5 - r) / 0.03, 0, 1)[..., None]
    return out * fade


def paste_add(dst, src, cx, cy, gain=1.0):
    """Suma aditiva de src centrado en (cx,cy) sobre dst, con recorte."""
    h, w = src.shape[:2]
    x0 = int(round(cx - w / 2)); y0 = int(round(cy - h / 2))
    X0, Y0 = max(0, x0), max(0, y0)
    X1, Y1 = min(dst.shape[1], x0 + w), min(dst.shape[0], y0 + h)
    if X1 <= X0 or Y1 <= Y0: return dst
    dst[Y0:Y1, X0:X1] += src[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] * gain
    return dst
