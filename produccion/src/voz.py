"""Genera la narración (Piper TTS, voz masculina, fonética es-419) y los tiempos palabra a palabra."""
import json, os, subprocess, sys, wave, re
import numpy as np

TTS = sys.argv[1]           # carpeta con es-carlfm-x-low.onnx + latam.json
OUT = sys.argv[2]           # carpeta de salida
os.makedirs(OUT, exist_ok=True)
SR = 48000
DUR = 40.0

# (texto, inicio en s, length_scale)
LINES = [
 ("En 24 horas, la humanidad dejará de existir.", "En veinticuatro horas, la humanidad dejará de existir.", 0.30, 1.16),
 ("Y dejamos a una inteligencia artificial la última misión de nuestra historia.", None, 4.20, 1.12),
 ("Le pedimos que encontrara lo más importante que habíamos creado.", None, 9.25, 1.20),
 ("Analizó nuestras guerras, nuestros errores, nuestros logros y nuestros sueños.", None, 14.10, 0.98),
 ("Pero encontró algo que ningún algoritmo podía medir.", None, 19.80, 1.25),
 ("No éramos especiales por ser perfectos.", None, 24.50, 1.12),
 ("Éramos especiales porque, incluso sabiendo que todo podía terminar, seguíamos amándonos.", None, 27.00, 0.90),
 ("Y ese fue el último mensaje que envió al universo.", None, 31.95, 1.22),
 ("Si mañana todo terminara…", "Si mañana todo terminara...", 36.20, 1.18),
 ("¿qué dejarías de nosotros?", None, 38.00, 1.14),
]

def synth(text, ls, path):
    tmp = path + ".txt"
    open(tmp, "w").write(text + "\n")
    subprocess.run([sys.executable, "-m", "piper", "-m", f"{TTS}/es-carlfm-x-low.onnx", "-c", f"{TTS}/latam.json",
                    "--length-scale", str(ls), "--noise-scale", "0.6", "--noise-w-scale", "0.7",
                    "-i", tmp, "-f", path], check=True, capture_output=True)
    # 48 kHz, voz ligeramente más grave (−1 semitono) sin cambiar duración, EQ de narrador
    proc = path.replace(".wav", "_p.wav")
    af = ("aresample=48000,asetrate=48000*0.944,aresample=48000,atempo=1.0593,"
          "highpass=f=70,equalizer=f=140:t=q:w=1:g=4,equalizer=f=3200:t=q:w=1.2:g=2.5,"
          "equalizer=f=7000:t=q:w=1:g=-3,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,"
          "aresample=48000")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-af", af, "-ac", "1", proc], check=True)
    w = wave.open(proc); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return x

def active_span(x, thr=0.02, win=480):
    env = np.sqrt(np.convolve(x**2, np.ones(win)/win, "same"))
    idx = np.where(env > thr)[0]
    return idx[0], idx[-1], env

def word_times(display, x, t0):
    a, b, env = active_span(x)
    words = display.split()
    # pausas internas (>110 ms) para las comas
    on = env > 0.02
    gaps = []
    i = a
    while i < b:
        if not on[i]:
            j = i
            while j < b and not on[j]: j += 1
            if (j - i) / SR > 0.11: gaps.append((i, j))
            i = j
        else: i += 1
    phrases = re.split(r"(?<=,)\s+", display)
    segs = []
    if len(gaps) >= len(phrases) - 1 and len(phrases) > 1:
        gaps = sorted(sorted(gaps, key=lambda g: g[1]-g[0], reverse=True)[:len(phrases)-1])
        s = a
        for g in gaps: segs.append((s, g[0])); s = g[1]
        segs.append((s, b))
    else:
        phrases = [display]; segs = [(a, b)]
    out = []
    for ph, (s, e) in zip(phrases, segs):
        ws = ph.split()
        wl = np.array([len(re.sub(r"[^\wáéíóúñü0-9]", "", w, flags=re.I)) + 1.2 for w in ws])
        cum = np.concatenate([[0], np.cumsum(wl)]) / wl.sum()
        for k, w in enumerate(ws):
            out.append({"w": w, "t0": round(t0 + (s + cum[k]*(e-s))/SR, 3), "t1": round(t0 + (s + cum[k+1]*(e-s))/SR, 3)})
    return out

track = np.zeros(int(DUR*SR), np.float32)
subs = []
for n, (disp, spoken, start, ls) in enumerate(LINES):
    x = synth(spoken or disp, ls, f"{OUT}/linea_{n:02d}.wav")
    a, b, _ = active_span(x)
    x = x[max(0, a-int(0.03*SR)):]          # recorta silencio inicial
    i0 = int(start*SR)
    seg = x[:len(track)-i0]
    track[i0:i0+len(seg)] += seg
    wt = word_times(disp, x, start)
    end = start + (b - a)/SR
    subs.append({"line": n, "text": disp, "start": start, "end": round(end, 3), "words": wt})
    print(f"{n}: {start:6.2f} -> {end:6.2f}  {disp}")

track = track / (np.abs(track).max() + 1e-9) * 0.89
np.save(f"{OUT}/voz.npy", track)
w = wave.open(f"{OUT}/voz.wav", "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((track*32767).astype(np.int16).tobytes()); w.close()
json.dump(subs, open(f"{OUT}/subs.json", "w"), ensure_ascii=False, indent=1)
