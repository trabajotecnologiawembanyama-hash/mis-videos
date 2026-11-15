"""Narrador de Brote con Kokoro TTS (voz em_alex, fonética es-419): alegre, prendido y con tono que cambia según la emoción.
Cada frase lleva una emoción del guion -> velocidad, tono (semitonos), volumen y puntuación expresiva.
Uso: voz_kokoro.py <ep01|ep02> <salida_dir>"""
import json, os, re, subprocess, sys
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

KOK = "/tmp/claude-0/kokoro"
VOICE = "em_alex"
EP, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

# emoción -> (velocidad, semitonos, ganancia dB, pausa posterior s)
EMO = {
    "gancho":     (1.04, +1.0, 0.0, 0.50),
    "calido":     (1.06, +0.3, -0.5, 0.45),
    "alegre":     (1.10, +1.8, +1.0, 0.45),
    "emocion":    (1.14, +2.2, +1.5, 0.40),
    "serio":      (0.94, -0.8, -1.5, 0.50),
    "nervioso":   (1.00, 0.0, -0.5, 0.40),
    "decidido":   (1.02, +0.8, +0.5, 0.45),
    "impacto":    (0.95, -0.3, +0.5, 0.55),
    "triste":     (0.90, -1.5, -2.5, 0.60),
    "frio":       (0.98, -1.0, -1.0, 0.50),
    "misterio":   (0.90, -1.8, -1.5, 0.30),
}

# (texto en pantalla, texto hablado con puntuación expresiva, emoción)
GUION = {
 "ep01": [
  ("Pedrito tenía un sueño enorme y un par de zapatillas rotas.", "¡Pedrito tenía un sueño enorme! Y un par de zapatillas rotas.", "gancho"),
  ("Cada tarde, cuando el barrio se quedaba en silencio, cruzaba la cancha gris con una pelota casi sin aire.", None, "calido"),
  ("Quería ser la estrella del básquetbol.", "¡Quería ser la estrella del básquetbol!", "alegre"),
  ("Pero en su casa el dinero alcanzaba justo para el pan.", None, "serio"),
  ("Unas zapatillas nuevas costaban lo mismo que un mes de alquiler.", None, "serio"),
  ("Así que Pedrito pegaba las suyas con cinta, una y otra vez.", None, "decidido"),
  ("Esa tarde, el colegio anunció las pruebas para entrar al equipo.", "¡Esa tarde, el colegio anunció las pruebas para entrar al equipo!", "emocion"),
  ("Todos llegarían con zapatillas brillantes.", None, "nervioso"),
  ("Pedrito miró sus pies, respiró hondo y apretó la pelota.", None, "impacto"),
  ("«Si no tengo con qué, tendré que tener algo más», se dijo.", "¡Si no tengo con qué, tendré que tener algo más!, se dijo.", "decidido"),
  ("Lanzó una vez más al aro oxidado.", "¡Lanzó una vez más al aro oxidado!", "alegre"),
  ("Y no sabía que, desde la reja, alguien llevaba semanas mirándolo.", "Y no sabía que, desde la reja... alguien llevaba semanas mirándolo.", "misterio"),
 ],
 "ep02": [
  ("Pedrito corría rápido, hasta que su zapatilla decidió rendirse.", "¡Pedrito corría rápido! Hasta que su zapatilla decidió rendirse.", "gancho"),
  ("Llegó el día de las pruebas y el gimnasio estaba lleno.", "¡Llegó el día de las pruebas, y el gimnasio estaba lleno!", "emocion"),
  ("Los otros niños reían y calentaban con zapatillas que olían a nuevas.", None, "alegre"),
  ("Pedrito se paró en la fila, con la cinta bien apretada.", None, "nervioso"),
  ("El entrenador tocó el silbato.", "¡El entrenador tocó el silbato!", "decidido"),
  ("Pedrito robó un balón, esquivó a dos y saltó hacia el aro.", "¡Pedrito robó un balón, esquivó a dos, y saltó hacia el aro!", "emocion"),
  ("En ese instante, la suela se soltó y rodó por el piso.", "En ese instante... la suela se soltó, y rodó por el piso.", "impacto"),
  ("Pedrito cayó, el balón rebotó lejos y el gimnasio estalló en risas.", None, "triste"),
  ("«Puedes ir a sentarte», dijo el entrenador.", "Puedes ir a sentarte, dijo el entrenador.", "frio"),
  ("Pedrito recogió su suela, la guardó en el bolsillo y salió sin mirar a nadie.", None, "triste"),
  ("Se sentó solo en la cancha gris.", None, "triste"),
  ("Y entonces, una sombra le tapó el sol.", "Y entonces... una sombra le tapó el sol.", "misterio"),
 ],
}

k = Kokoro(f"{KOK}/kokoro-v1.0.onnx", f"{KOK}/voices-v1.0.bin")
SR = 24000
SPEED_K = float(os.environ.get("SPEED_K", "0.96"))
GAP_K = float(os.environ.get("GAP_K", "1.8"))


def syllables(w):
    w = re.sub(r"[^a-záéíóúüñ]", "", w.lower())
    return max(1, len(re.findall(r"[aeiouáéíóúü]+", w)))


def process(x, semis, gain_db, tmp):
    sf.write(tmp + "_in.wav", x, SR)
    ratio = 2 ** (semis / 12)
    af = (f"aresample=48000,rubberband=pitch={ratio:.4f}:formant=preserved:pitchq=quality,"
          f"volume={gain_db}dB")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp + "_in.wav", "-af", af, "-ac", "1", tmp + "_out.wav"], check=True)
    y, _ = sf.read(tmp + "_out.wav")
    return y.astype(np.float32)


audio = [np.zeros(int(0.3 * 48000), np.float32)]
t = 0.3
words = []
for si, (disp, spoken, emo) in enumerate(GUION[EP]):
    spd, semis, gain, gap = EMO[emo]
    spd *= SPEED_K; gap *= GAP_K
    if si == len(GUION[EP]) - 2: gap += 0.5          # silencio antes del gancho final
    x, sr = k.create(spoken or disp, voice=VOICE, speed=spd, lang="es-419")
    y = process(x, semis, gain, f"{OUT}/tmp")
    # recorte de silencios de borde
    env = np.sqrt(np.convolve(y ** 2, np.ones(960) / 960, "same"))
    on = np.where(env > 0.01)[0]
    y = y[max(0, on[0] - 480): on[-1] + 2400]
    env = env[max(0, on[0] - 480): on[-1] + 2400]
    # pausas internas (comas / puntos suspensivos)
    active = env > 0.012
    gaps, i = [], 0
    while i < len(active):
        if not active[i]:
            j = i
            while j < len(active) and not active[j]: j += 1
            if (j - i) / 48000 > 0.09 and i > 0 and j < len(active): gaps.append((i, j))
            i = j
        else: i += 1
    a0 = np.argmax(active); a1 = len(active) - np.argmax(active[::-1])
    phrases = [p for p in re.split(r"(?<=[,;:])\s+", disp)]
    if len(gaps) >= len(phrases) - 1 and len(phrases) > 1:
        gs = sorted(sorted(gaps, key=lambda g: g[1] - g[0], reverse=True)[:len(phrases) - 1])
        segs, s0 = [], a0
        for g in gs: segs.append((s0, g[0])); s0 = g[1]
        segs.append((s0, a1))
    else:
        phrases, segs = [disp], [(a0, a1)]
    for ph, (s0, s1) in zip(phrases, segs):
        ws = ph.split()
        wt = np.array([syllables(w) + 0.35 for w in ws], float)
        c = np.concatenate([[0], np.cumsum(wt)]) / wt.sum()
        for n, w in enumerate(ws):
            words.append({"w": w, "t0": round(t + (s0 + c[n] * (s1 - s0)) / 48000, 3),
                          "t1": round(t + (s0 + c[n + 1] * (s1 - s0)) / 48000, 3), "s": si, "emo": emo})
    audio.append(y); t += len(y) / 48000
    audio.append(np.zeros(int(gap * 48000), np.float32)); t += gap
    print(f"{si:2d} {emo:9s} {t - gap - len(y) / 48000:6.2f}-{t - gap:6.2f}  {disp}")

x = np.concatenate(audio)
sf.write(f"{OUT}/voz_raw.wav", x, 48000)
# cadena final: voz cercana y brillante, compresión suave, sin reverb pesada
af = ("highpass=f=70,equalizer=f=200:t=q:w=1:g=1.5,equalizer=f=3500:t=q:w=1.2:g=2.5,equalizer=f=9000:t=q:w=1:g=1.5,"
      "acompressor=threshold=-20dB:ratio=2.5:attack=6:release=120,loudnorm=I=-16:TP=-1.5")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/voz_raw.wav", "-af", af, "-ar", "48000", "-ac", "1", f"{OUT}/voz.wav"], check=True)
for f in ("tmp_in.wav", "tmp_out.wav"):
    if os.path.exists(f"{OUT}/{f}"): os.remove(f"{OUT}/{f}")
json.dump({"duration": round(t, 3), "voice": f"kokoro {VOICE} es-419", "words": words,
           "sentences": [g[0] for g in GUION[EP]]}, open(f"{OUT}/palabras.json", "w"), ensure_ascii=False, indent=1)
print(f"duración {t:.2f}s, {len(words)} palabras")
