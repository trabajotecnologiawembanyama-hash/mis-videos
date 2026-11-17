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
 "ep03": [
  ("El hombre de la escoba sabía algo que Pedrito no.", None, "gancho"),
  ("Se llamaba Don Lucho y cuidaba la cancha desde hacía treinta años.", None, "calido"),
  ("«¿Se ríen de ti porque se rompió la zapatilla?», preguntó.", "¿Se ríen de ti porque se rompió la zapatilla?, preguntó.", "calido"),
  ("«No, porque no sé jugar», dijo Pedrito.", "No, porque no sé jugar, dijo Pedrito.", "triste"),
  ("«Mentira. Te vi lanzar semanas. Tienes buena muñeca. Lo que te falta es base».", "¡Mentira! Te vi lanzar semanas. ¡Tienes buena muñeca! Lo que te falta es base.", "decidido"),
  ("Don Lucho abrió un armario viejo y sacó un par de zapatillas gastadas, dos números más grandes.", None, "calido"),
  ("«Son de cuando yo jugaba. Llévalas con calcetines gruesos».", "Son de cuando yo jugaba. ¡Llévalas con calcetines gruesos!", "alegre"),
  ("Desde esa mañana, antes de ir al colegio, entrenaron juntos: pasos, pases, defensa y mil lanzamientos.", "¡Desde esa mañana, antes de ir al colegio, entrenaron juntos! Pasos, pases, defensa, y mil lanzamientos.", "emocion"),
  ("Una semana después, Pedrito ya no era el mismo.", None, "decidido"),
  ("Y entonces llegó la noticia: el equipo tenía un último cupo.", "Y entonces llegó la noticia... ¡el equipo tenía un último cupo!", "emocion"),
 ],
 "ep04": [
  ("Pedrito estaba a un paso de rendirse.", "Pedrito estaba a un paso... de rendirse.", "impacto"),
  ("Faltaban dos días para el partido y el colegio pidió una cuota para inscribirse al equipo.", None, "serio"),
  ("Pedrito preguntó cuánto era y el número lo dejó mudo.", None, "impacto"),
  ("En su casa no había ese dinero.", None, "triste"),
  ("Tomás, el mejor jugador del curso, lo vio y se burló.", None, "frio"),
  ("«Un equipo no es para quien no puede pagarlo».", "Un equipo no es para quien no puede pagarlo.", "frio"),
  ("Pedrito caminó a la cancha, dejó su pelota sobre la banca y se fue.", None, "triste"),
  ("Esa noche no durmió.", None, "triste"),
  ("En la mañana, la pelota estaba en la puerta de su casa, con una nota que decía:", None, "calido"),
  ("«Los sueños no se cobran en la entrada.", "Los sueños no se cobran en la entrada.", "calido"),
  ("Ven al partido del barrio.", "¡Ven al partido del barrio!", "alegre"),
  ("El entrenador va a estar mirando».", "¡El entrenador va a estar mirando!", "emocion"),
  ("Pedrito la apretó contra el pecho.", None, "decidido"),
 ],
 "ep05": [
  ("Quedaban cinco segundos y todos miraban a Pedrito.", "¡Quedaban cinco segundos! Y todos miraban a Pedrito.", "gancho"),
  ("El partido del barrio estaba empatado.", "¡El partido del barrio estaba empatado!", "emocion"),
  ("La cancha gris estaba llena de vecinos, y en la primera fila, el entrenador del colegio con los brazos cruzados.", None, "nervioso"),
  ("Tomás se ofreció para tirar, pero estaba marcado.", None, "nervioso"),
  ("El balón llegó a las manos de Pedrito.", "¡El balón llegó a las manos de Pedrito!", "emocion"),
  ("Escuchó la voz de Don Lucho: «Base firme, muñeca suave».", "Escuchó la voz de Don Lucho... Base firme, muñeca suave.", "calido"),
  ("Pedrito dobló las rodillas, saltó con las zapatillas grandes y soltó el tiro.", None, "decidido"),
  ("La pelota dio una vuelta lenta en el aire.", "La pelota dio una vuelta lenta... en el aire.", "misterio"),
  ("Sonaron las campanas del aro.", None, "impacto"),
  ("¡Canasta!", None, "emocion"),
  ("El barrio entero gritó.", "¡El barrio entero gritó!", "emocion"),
  ("El entrenador sonrió y le estrechó la mano: «El cupo es tuyo, y la cuota corre por el colegio».", "El entrenador sonrió y le estrechó la mano. ¡El cupo es tuyo, y la cuota corre por el colegio!", "alegre"),
  ("Pedrito miró a Don Lucho y los dos lloraron de alegría.", None, "calido"),
  ("La próxima semana, una niña con anteojos y un taller de chatarra…", "La próxima semana... una niña con anteojos, y un taller de chatarra...", "misterio"),
 ],
 "ep06": [
  ("La basura de unos puede ser el tesoro de otros.", "¡La basura de unos puede ser el tesoro de otros!", "gancho"),
  ("Camila, de trece años, vivió toda su vida entre cables, tornillos y radios rotos.", None, "calido"),
  ("Cada domingo recorría la feria buscando piezas que nadie quería.", None, "alegre"),
  ("Su sueño era enorme: construir un robot y llevarlo a la feria de ciencias de la región.", "¡Su sueño era enorme: construir un robot y llevarlo a la feria de ciencias de la región!", "emocion"),
  ("Pero un robot cuesta caro, y su familia apenas llegaba a fin de mes.", None, "serio"),
  ("Con una caja de cartón llena de chatarra, empezó a armar un cuerpo metálico en el patio.", None, "decidido"),
  ("Latas, tuercas, un colador viejo como cabeza.", "¡Latas, tuercas, un colador viejo como cabeza!", "alegre"),
  ("Cuando terminó de pegar el último tornillo, el robot quedó inmóvil.", None, "impacto"),
  ("Le faltaba algo.", None, "misterio"),
  ("Camila lo miró y susurró: «Necesitas un corazón».", "Camila lo miró y susurró: Necesitas un corazón.", "misterio"),
 ],
 "ep07": [
  ("El robot se encendió por cinco segundos.", "¡El robot se encendió por cinco segundos!", "gancho"),
  ("Camila había encontrado un motor pequeño en un puesto de la feria, y lo conectó con una pila vieja.", None, "calido"),
  ("Las tapas de botella brillaron, el brazo se levantó y de pronto, un chispazo.", "¡Las tapas de botella brillaron, el brazo se levantó y de pronto, un chispazo!", "emocion"),
  ("El motor echó humo y todo quedó en silencio.", None, "impacto"),
  ("Sus compañeros, que miraban desde la reja, se rieron.", None, "frio"),
  ("«Tu robot es pura basura, Camila».", "Tu robot es pura basura, Camila.", "frio"),
  ("Ella no contestó.", None, "triste"),
  ("Dejó el destornillador en el suelo, se sentó junto al robot y escondió la cara entre las rodillas.", None, "triste"),
  ("La feria cerraba inscripciones en cuatro días.", None, "serio"),
  ("Ya no había pila, ni motor, ni esperanza.", None, "triste"),
  ("Entonces, desde la casa, se escuchó un sonido: tac, tac, tac.", None, "misterio"),
  ("«Mijita, ven», dijo una voz.", "Mijita, ven, dijo una voz.", "calido"),
 ],
 "ep08": [
  ("El corazón del robot estaba escondido en la casa de la abuela.", "¡El corazón del robot estaba escondido en la casa de la abuela!", "gancho"),
  ("Abuela Rosa, costurera de toda la vida, cosió sentada frente a una máquina nueva.", None, "calido"),
  ("En un rincón, otra máquina vieja juntaba polvo.", None, "misterio"),
  ("«Esa ya no cose, pero tiene un buen motor», dijo ella.", "Esa ya no cose, pero tiene un buen motor, dijo ella.", "calido"),
  ("Camila abrió los ojos.", "¡Camila abrió los ojos!", "emocion"),
  ("Juntas desarmaron la máquina y la abuela le enseñó su secreto:", None, "calido"),
  ("«Las cosas buenas se hacen despacio, punto por punto».", "Las cosas buenas se hacen despacio, punto por punto.", "serio"),
  ("Camila conectó el motor con paciencia, cable por cable.", None, "decidido"),
  ("Las tapas de botella se encendieron y el robot levantó un brazo.", "¡Las tapas de botella se encendieron y el robot levantó un brazo!", "emocion"),
  ("Camila gritó de felicidad.", "¡Camila gritó de felicidad!", "alegre"),
  ("Pero la abuela la miró seria:", None, "serio"),
  ("«Ahora necesitas energía para dos días.", "Ahora necesitas energía para dos días.", "serio"),
  ("¿Y de dónde sacarás las pilas?»", "¿Y de dónde sacarás las pilas?", "misterio"),
 ],
 "ep09": [
  ("La lluvia no avisó que iba a llegar.", None, "impacto"),
  ("Camila dormiría tranquila esa noche, pero un trueno la despertó.", None, "nervioso"),
  ("Corrió al patio y vio el agua entrando por el techo del taller.", "¡Corrió al patio y vio el agua entrando por el techo del taller!", "emocion"),
  ("El robot estaba empapado, con los cables flotando.", None, "triste"),
  ("Intentó secarlo con trapos hasta que le dolieron las manos.", None, "nervioso"),
  ("Aún faltaban las pilas, y la feria era al día siguiente.", None, "serio"),
  ("Camila se quedó de rodillas y lloró en silencio.", None, "triste"),
  ("La abuela le puso una manta sobre los hombros.", None, "calido"),
  ("«He hecho vestidos con retazos que parecían inservibles, mija.", "He hecho vestidos con retazos que parecían inservibles, mija.", "calido"),
  ("Lo importante es no soltar la aguja».", "¡Lo importante es no soltar la aguja!", "decidido"),
  ("Camila respiró y volvió a tomar el destornillador.", None, "decidido"),
  ("Cuando amaneció, alguien tocó la puerta.", None, "misterio"),
  ("Era todo el barrio, con pilas en las manos.", "¡Era todo el barrio, con pilas en las manos!", "emocion"),
 ],
 "ep10": [
  ("Cuando el robot levantó la mano, el jurado dejó de escribir.", "¡Cuando el robot levantó la mano, el jurado dejó de escribir!", "gancho"),
  ("La feria de ciencias estaba llena de proyectos relucientes.", None, "alegre"),
  ("En una esquina, Camila colocó su robot de latas junto a una mesa sencilla.", None, "nervioso"),
  ("Respiró y apretó el botón.", None, "impacto"),
  ("Las tapas se encendieron, el robot dio tres pasos, tomó una pelota pequeña y la dejó en la mesa.", "¡Las tapas se encendieron, el robot dio tres pasos, tomó una pelota pequeña y la dejó en la mesa!", "emocion"),
  ("Luego levantó la mano y saludó.", "¡Luego levantó la mano y saludó!", "alegre"),
  ("Un juez le preguntó: «¿De qué está hecho?».", "Un juez le preguntó: ¿De qué está hecho?", "calido"),
  ("Camila sonrió: «De chatarra, de pilas del barrio y del motor de la máquina de mi abuela».", "Camila sonrió: ¡De chatarra, de pilas del barrio y del motor de la máquina de mi abuela!", "decidido"),
  ("Al final del día, anunciaron el Premio a la Creatividad.", "¡Al final del día, anunciaron el Premio a la Creatividad!", "emocion"),
  ("Camila subió al escenario, miró a la abuela entre el público y levantó el trofeo con las dos manos.", None, "alegre"),
  ("La próxima semana, una cocina, mucha harina y un concurso…", "La próxima semana, una cocina, mucha harina y un concurso...", "misterio"),
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
    if os.environ.get("NATURAL"):
        af = f"aresample=48000:resampler=soxr,volume={gain_db * 0.6:.2f}dB"      # sin cambio de tono artificial
    else:
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
if os.environ.get("NATURAL"):
    # cadena de locutor natural: cuerpo suave, sin realces agresivos, compresión ligera y una sala pequeña muy sutil
    af = ("highpass=f=60,equalizer=f=160:t=q:w=1:g=1.0,equalizer=f=2800:t=q:w=1.5:g=1.0,"
          "acompressor=threshold=-24dB:ratio=1.8:attack=15:release=250,aecho=0.85:0.4:18|31:0.07|0.05,loudnorm=I=-16:TP=-1.5")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/voz_raw.wav", "-af", af, "-ar", "48000", "-ac", "1", f"{OUT}/voz.wav"], check=True)
for f in ("tmp_in.wav", "tmp_out.wav"):
    if os.path.exists(f"{OUT}/{f}"): os.remove(f"{OUT}/{f}")
json.dump({"duration": round(t, 3), "voice": f"kokoro {VOICE} es-419", "words": words,
           "sentences": [g[0] for g in GUION[EP]]}, open(f"{OUT}/palabras.json", "w"), ensure_ascii=False, indent=1)
print(f"duración {t:.2f}s, {len(words)} palabras")
