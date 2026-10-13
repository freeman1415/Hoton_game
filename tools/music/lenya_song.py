"""«Новая мелодия» Лени для ритм-игры: синтез трека и карты нот из одной партитуры.

    python tools/music/lenya_song.py

Пишет:
  game/scenes/minigames/rhythm/lenya_song.wav  — трек (моно, 22 050 Гц, 16 бит)
  game/scenes/minigames/rhythm/lenya_chart.gd  — карта нот (константы для игры)
  game/scenes/minigames/rhythm/sfx_hit.wav, sfx_miss.wav — звуки попадания и промаха

Сюжет (docs/GAME.md): в мелодии зашифровано слово. Каждая фраза кончается
ключевой нотой: до = Р, ре = А, ми = К, фа = Е, соль = Т → «РАКЕТА».
Музыка своя, сторонних семплов нет. Нужен numpy.
"""
import os
import wave

import numpy as np

SR = 22050
BPM = 120.0
BEAT = 60.0 / BPM
BAR = 4
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "game", "scenes", "minigames", "rhythm")

C3, D3, E3, F3, G3, A3, B3 = 48, 50, 52, 53, 55, 57, 59
C4, D4, E4, F4, G4, A4, B4 = 60, 62, 64, 65, 67, 69, 71
C5, D5, E5, F5, G5 = 72, 74, 76, 77, 79

# Шифр: ключевая нота фразы → буква
CIPHER = {C4: ("до", "Р"), D5: ("ре", "А"), E4: ("ми", "К"), F4: ("фа", "Е"), G4: ("соль", "Т")}

INTRO_BARS = 2
# Фразы по 2 такта: аккорды (по такту) и мелодия (доля, нота, длительность в долях).
# Последняя нота фразы — ключевая (длинная, 2 доли).
PHRASES = [
    ([C3, G3], [(0, E4, 1), (1, G4, 1), (2, C5, 1), (3, G4, 1), (4, A4, 1), (5, G4, 1), (6, C4, 2)]),
    ([A3, G3], [(0, A4, 1), (1, C5, 1), (2, B4, 1), (3, A4, 1), (4, G4, .5), (4.5, A4, .5), (5, B4, 1),
                (6, D5, 2)]),
    ([F3, C3], [(0, F4, .5), (.5, A4, .5), (1, C5, 1), (2, A4, .5), (2.5, F4, .5), (3, A4, 1),
                (4, G4, .5), (4.5, E4, .5), (5, C4, .5), (5.5, D4, .5), (6, E4, 2)]),
    ([D3, G3], [(0, D5, .5), (.5, C5, .5), (1, A4, .5), (1.5, F4, .5), (2, A4, 1), (3, D5, 1),
                (4, B4, .5), (4.5, G4, .5), (5, B4, .5), (5.5, D5, .5), (6, F4, 2)]),
    ([C3, A3], [(0, C5, .5), (.5, E5, .5), (1, G4, .5), (1.5, C5, .5), (2, E5, .5), (2.5, D5, .5),
                (3, C5, 1), (4, A4, .5), (4.5, C5, .5), (5, E5, .5), (5.5, D5, .5), (6, G4, 2)]),
    ([F3, G3], [(0, F4, .5), (.5, A4, .5), (1, C5, .5), (1.5, F5, .5), (2, E5, .5), (2.5, C5, .5),
                (3, A4, .5), (3.5, C5, .5), (4, B4, .5), (4.5, D5, .5), (5, G4, .5), (5.5, B4, .5),
                (6, D5, 2)]),
]
# Кода: финальный аккорд двумя руками
OUTRO_CHORDS = [C3, C3]
OUTRO_NOTES = [(0, C5, 2), (0, C4, 2)]


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def env(n, attack=0.005, release=0.04, sustain=0.6, decay=0.08):
    t = np.arange(n) / SR
    e = np.ones(n)
    a = max(1, int(attack * SR))
    e[:a] = np.linspace(0, 1, a)
    d = np.clip((t - attack) / decay, 0, 1)
    e = np.where(t > attack, 1 - (1 - sustain) * d, e)
    r = min(n, int(release * SR))
    e[n - r:] *= np.linspace(1, 0, r)
    return e


def pulse(freq, dur, duty=0.25, vib=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    phase = (freq * t + vib * np.sin(2 * np.pi * 5.5 * t) / 5.5) % 1.0
    return np.where(phase < duty, 1.0, -1.0) * env(n)


def triangle(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return (2 * np.abs(2 * ((freq * t) % 1) - 1) - 1) * env(n, sustain=0.8)


def bell(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * freq * t) + 0.4 * np.sin(2 * np.pi * freq * 2.01 * t)) * np.exp(-t * 3.5)


def kick():
    n = int(0.14 * SR)
    t = np.arange(n) / SR
    f = 50 + 90 * np.exp(-t * 35)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22)


def noise(dur, decay, seed):
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    x = rng.uniform(-1, 1, n)
    return x * np.exp(-t * decay)


def add(track, start, sig, gain):
    i = int(start * SR)
    j = min(len(track), i + len(sig))
    track[i:j] += sig[:j - i] * gain


def lane_for(pitch, prev):
    """Дорожка по высоте: ниже — левее. Соседние разные ноты не падают в одну дорожку."""
    lane = 0 if pitch <= F4 else 1 if pitch <= A4 else 2 if pitch <= C5 else 3
    if prev is not None:
        prev_lane, prev_pitch = prev
        if lane == prev_lane and pitch != prev_pitch:
            step = 1 if pitch > prev_pitch else -1
            lane = prev_lane + step
            if not 0 <= lane <= 3:
                lane = prev_lane - step
    return lane


def build():
    total_bars = INTRO_BARS + 2 * len(PHRASES) + 2
    length = total_bars * BAR * BEAT
    track = np.zeros(int((length + 1.0) * SR))
    notes = []
    phrases = []

    chords = [C3, G3] + [c for p in PHRASES for c in p[0]] + OUTRO_CHORDS
    for bar, root in enumerate(chords):
        t0 = bar * BAR * BEAT
        third = root + (3 if root in (A3, D3) else 4)
        for beat in range(BAR):
            t = t0 + beat * BEAT
            add(track, t, triangle(midi_hz(root if beat % 2 == 0 else root + 12), BEAT * 0.9), 0.30)
            if beat in (0, 2):
                add(track, t, kick(), 0.55)
            else:
                add(track, t, noise(0.12, 28, bar * 4 + beat), 0.22)
            for half in (0, 0.5):
                add(track, t + half * BEAT, noise(0.03, 120, bar * 8 + beat * 2 + int(half * 2)), 0.06)
        for k, m in enumerate((root + 12, third + 12, root + 19)):  # мягкое арпеджио
            for rep in range(2):
                add(track, t0 + (rep * 2 + k * 0.5) * BEAT, triangle(midi_hz(m), BEAT * 0.45), 0.06)

    # отсчёт на последний такт вступления
    for beat in range(BAR):
        add(track, ((INTRO_BARS - 1) * BAR + beat) * BEAT, bell(midi_hz(C5 + (7 if beat == 3 else 0)), 0.3), 0.18)

    prev = None
    for i, (_, melody) in enumerate(PHRASES):
        start = (INTRO_BARS + 2 * i) * BAR * BEAT
        key_pitch = melody[-1][1]
        note_name, letter = CIPHER[key_pitch]
        phrases.append({"start": start, "end": start + 2 * BAR * BEAT, "letter": letter, "note": note_name})
        for k, (beat, pitch, dur) in enumerate(melody):
            t = start + beat * BEAT
            is_key = k == len(melody) - 1
            add(track, t, pulse(midi_hz(pitch), dur * BEAT * 0.95, vib=3.0 if is_key else 0.0), 0.16)
            if is_key:
                add(track, t, bell(midi_hz(pitch + 12), 1.2), 0.22)
            lane = lane_for(pitch, prev)
            prev = (lane, pitch)
            notes.append({"time": round(t, 4), "lane": lane, "key": is_key, "phrase": i})

    outro = (INTRO_BARS + 2 * len(PHRASES)) * BAR * BEAT
    for k, (beat, pitch, dur) in enumerate(OUTRO_NOTES):
        add(track, outro + beat * BEAT, pulse(midi_hz(pitch), dur * BEAT), 0.14)
        add(track, outro + beat * BEAT, bell(midi_hz(pitch + 12), 1.5), 0.16)
        notes.append({"time": round(outro + beat * BEAT, 4), "lane": 3 if k == 0 else 0, "key": False, "phrase": -1})

    track = track[:int(length * SR)]
    fade = int(0.5 * SR)
    track[-fade:] *= np.linspace(1, 0, fade)
    track *= 0.9 / np.max(np.abs(track))
    return track, notes, phrases, length


def write_wav(path, samples):
    data = (np.clip(samples, -1, 1) * 32767).astype("<i2").tobytes()
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data)
    print("wrote", os.path.normpath(path))


def write_chart(path, notes, phrases, length):
    lines = [
        "extends RefCounted",
        "## Карта нот «новой мелодии» Лени. Сгенерировано tools/music/lenya_song.py — не править руками,",
        "## менять партитуру там и пересобрать (трек и ноты должны совпадать).",
        "",
        "const BPM := %.1f" % BPM,
        "const SONG_LENGTH := %.3f" % length,
        "",
        "## time — секунда трека, lane — дорожка 0..3 (D F J K), key — ключевая нота фразы,",
        "## phrase — номер фразы (-1 — финальный аккорд).",
        "const NOTES := [",
    ]
    for n in notes:
        lines.append('\t{"time": %.4f, "lane": %d, "key": %s, "phrase": %d},' % (
            n["time"], n["lane"], "true" if n["key"] else "false", n["phrase"]))
    lines += ["]", "", "## Фразы шифра: ключевая нота → буква слова «РАКЕТА».", "const PHRASES := ["]
    for p in phrases:
        lines.append('\t{"start": %.3f, "end": %.3f, "letter": "%s", "note": "%s"},' % (
            p["start"], p["end"], p["letter"], p["note"]))
    lines.append("]")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", os.path.normpath(path))


def sfx():
    hit = bell(midi_hz(C5 + 12), 0.12) * 0.5
    click = noise(0.02, 200, 1) * 0.2
    hit[:len(click)] += click
    miss = triangle(midi_hz(C3 - 5), 0.15) * np.exp(-np.arange(int(0.15 * SR)) / SR * 15)
    return hit, miss


def main():
    os.makedirs(OUT, exist_ok=True)
    track, notes, phrases, length = build()
    write_wav(os.path.join(OUT, "lenya_song.wav"), track)
    write_chart(os.path.join(OUT, "lenya_chart.gd"), notes, phrases, length)
    hit, miss = sfx()
    write_wav(os.path.join(OUT, "sfx_hit.wav"), hit / np.max(np.abs(hit)) * 0.6)
    write_wav(os.path.join(OUT, "sfx_miss.wav"), miss / np.max(np.abs(miss)) * 0.5)
    print("notes: %d, length: %.1f s" % (len(notes), length))


if __name__ == "__main__":
    main()
