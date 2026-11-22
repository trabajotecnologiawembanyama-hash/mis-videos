"""Sintetizadores de música y efectos de Brote (compartidos por el motor 2D)."""
import os
import numpy as np
DUR = float(os.environ.get("BROTE_DUR", "55"))
SR = 48000
NA = int(DUR * SR)
rng = np.random.default_rng(11)


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


