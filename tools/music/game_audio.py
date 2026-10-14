"""Музыка и звуки игры: синтез в стиле 8-бит, сторонних семплов нет.

    python tools/music/game_audio.py

Пишет:
  game/audio/music/<трек>.wav  — зацикленные темы (моно, 22 050 Гц, 16 бит):
      title, intro, hub, backstage, finale — локации;
      manya, lenya, katya, moyto, sulus — темы маскотов (их мини-игры и разговоры с ними)
  game/audio/sfx/<звук>.wav    — интерфейс, шаги, печать, победа, «голоса» для диалогов

Мелодия Лени для ритм-игры — отдельно, tools/music/lenya_song.py.
Партитуры записаны строками: «E4:1 G4:.5 r:.5» — нота:длительность в долях, r — пауза.
Нужен numpy.
"""
import os
import wave

import numpy as np

SR = 22050
ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "game", "audio")
NOTE_INDEX = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
rng = np.random.default_rng(22)


# region Синтез

def midi(name):
    """«C#4» → номер MIDI."""
    base = NOTE_INDEX[name[0]]
    i = 1
    while i < len(name) and name[i] in "#b":
        base += 1 if name[i] == "#" else -1
        i += 1
    return base + 12 * (int(name[i:]) + 1)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def env(n, attack=0.005, decay=0.1, sustain=0.6, release=0.05):
    t = np.arange(n) / SR
    e = np.minimum(1.0, t / max(attack, 1e-4))
    e = np.where(t > attack, 1 - (1 - sustain) * np.clip((t - attack) / decay, 0, 1), e)
    r = min(n, int(release * SR))
    if r > 0:
        e[n - r:] *= np.linspace(1, 0, r)
    return e


def osc(kind, freq, n, duty=0.25):
    phase = (freq * np.arange(n) / SR) % 1.0
    if kind == "pulse":
        return np.where(phase < duty, 1.0, -1.0)
    if kind == "tri":
        return 2 * np.abs(2 * phase - 1) - 1
    if kind == "saw":
        return 2 * phase - 1
    if kind == "sine":
        return np.sin(2 * np.pi * phase)
    raise ValueError(kind)


def noise(n):
    return rng.uniform(-1, 1, n)


def lowpass(x, k):
    """Простой однополюсный фильтр, k ∈ (0, 1]: меньше — глуше."""
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += k * (v - acc)
        y[i] = acc
    return y


def parse(score):
    """«E4:1 r:.5 G4:.5» → [(доля, midi | None, длительность)]."""
    out, beat = [], 0.0
    for token in score.split():
        name, dur = token.split(":")
        dur = float(dur)
        out.append((beat, None if name == "r" else midi(name), dur))
        beat += dur
    return out


def render_part(buf, notes, beat_sec, kind, vol, duty=0.25, gate=0.9, transpose=0, **env_kw):
    for beat, m, dur in notes:
        if m is None:
            continue
        start = int(beat * beat_sec * SR)
        n = int(dur * beat_sec * gate * SR)
        if start >= len(buf) or n <= 0:
            continue
        n = min(n, len(buf) - start)
        wave_ = osc(kind, hz(m + transpose), n, duty=duty) * env(n, **env_kw) * vol
        buf[start:start + n] += wave_


def drum(kind, n=None):
    if kind == "kick":
        n = n or int(0.12 * SR)
        t = np.arange(n) / SR
        f = 150 * np.exp(-t * 30) + 45
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22)
    if kind == "snare":
        n = n or int(0.1 * SR)
        t = np.arange(n) / SR
        return (noise(n) * 0.8 + np.sin(2 * np.pi * 190 * t) * 0.3) * np.exp(-t * 30)
    if kind == "hat":
        n = n or int(0.03 * SR)
        x = noise(n)
        x = x - lowpass(x, 0.3)  # верхние частоты
        return x * np.exp(-np.arange(n) / SR * 120)
    raise ValueError(kind)


def render_drums(buf, pattern, beat_sec, bars, beats_per_bar, vol):
    """pattern: {"kick": [доли в такте], ...}"""
    for bar in range(bars):
        for kind, beats in pattern.items():
            for b in beats:
                start = int((bar * beats_per_bar + b) * beat_sec * SR)
                hit = drum(kind) * vol * (0.5 if kind == "hat" else 1.0)
                end = min(len(buf), start + len(hit))
                buf[start:end] += hit[:end - start]


def chord_parts(chords, beats_per_bar, style):
    """Аккорды по тактам → бас и аккомпанемент (арпеджио или «ум-па»)."""
    bass, comp = [], []
    for bar, chord in enumerate(chords):
        minor = chord.endswith("m")
        root = midi(chord.rstrip("m") + "3")
        if root < midi("F3"):
            root += 12  # аккомпанемент — в середине, от фа до ми
        third = root + (3 if minor else 4)
        fifth = root + 7
        b0 = bar * beats_per_bar
        if style == "arp":
            bass.append((b0, root - 12, beats_per_bar))
            seq = [root, third, fifth, root + 12, fifth, third] * 3
            for i in range(beats_per_bar * 2):
                comp.append((b0 + i * 0.5, seq[i], 0.5))
        elif style == "oompah":
            for i in range(beats_per_bar):
                if i % 2 == 0:
                    bass.append((b0 + i, (root if i % 4 == 0 else fifth - 12) - 12, 1))
                else:
                    for m in (third, fifth):
                        comp.append((b0 + i, m, 1))
        elif style == "waltz":
            bass.append((b0, root - 12, 1))
            for i in (1, 2):
                for m in (third, fifth):
                    comp.append((b0 + i, m, 1))
        elif style == "octave":
            for i in range(beats_per_bar * 2):
                bass.append((b0 + i * 0.5, root - (24 if i % 2 == 0 else 12), 0.5))
            for m in (root, third, fifth):
                comp.append((b0 + 1, m + 12, 0.5))
                comp.append((b0 + 3, m + 12, 0.5))
        elif style == "walk":
            steps = [root, third, fifth, third]
            for i in range(beats_per_bar):
                bass.append((b0 + i, steps[i % 4] - 12, 0.5))
        elif style == "pad":
            bass.append((b0, root - 12, beats_per_bar))
            for m in (root, third, fifth):
                comp.append((b0, m, beats_per_bar))
        elif style == "drive":
            for i in range(beats_per_bar * 2):
                bass.append((b0 + i * 0.5, root - 12, 0.5))
            for m in (third, fifth):
                comp.append((b0, m, 1.5))
                comp.append((b0 + 2.5, m, 1.5))
    return bass, comp


def master(buf, peak=0.7):
    buf = np.tanh(buf * 1.2)
    buf *= peak / max(1e-6, np.max(np.abs(buf)))
    return buf


def write_wav(path, data, loop=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pcm = (np.clip(data, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    if loop:
        _append_smpl_loop(path, len(pcm))


def _append_smpl_loop(path, frames):
    """Чанк smpl с петлёй на весь файл: Godot при импорте («Detect From WAV»)
    сам включит зацикливание."""
    import struct
    chunk = struct.pack("<9I", 0, 0, int(1e9 / SR), 60, 0, 0, 0, 1, 0)
    chunk += struct.pack("<6I", 0, 0, 0, frames - 1, 0, 0)
    with open(path, "r+b") as f:
        f.seek(0, 2)
        f.write(b"smpl" + struct.pack("<I", len(chunk)) + chunk)
        size = f.tell() - 8
        f.seek(4)
        f.write(struct.pack("<I", size))

# endregion


# region Музыка

def song(name, bpm, beats_per_bar, chords, style, lead, lead_kind="pulse", lead_duty=0.25,
         counter=None, drums=None, comp_kind="pulse", comp_vol=0.12, lead_vol=0.3, bass_vol=0.35,
         repeat_up=False):
    """Трек из аккордов (по такту), мелодии и барабанов. repeat_up — второй проход
    мелодии на октаву выше и с другим тембром, чтобы петля не надоедала."""
    beat_sec = 60.0 / bpm
    bars = len(chords)
    loops = 2
    total_beats = bars * beats_per_bar * loops
    buf = np.zeros(int(total_beats * beat_sec * SR))
    bass, comp = chord_parts(chords * loops, beats_per_bar, style)
    render_part(buf, bass, beat_sec, "tri", bass_vol, gate=0.95, sustain=0.9, decay=0.2)
    render_part(buf, comp, beat_sec, comp_kind, comp_vol, duty=0.125, gate=0.8, sustain=0.3, decay=0.15)
    notes = parse(lead)
    span = bars * beats_per_bar
    second = [(b + span, m, d) for b, m, d in notes]
    render_part(buf, notes, beat_sec, lead_kind, lead_vol, duty=lead_duty, decay=0.15, sustain=0.55)
    if repeat_up:
        render_part(buf, second, beat_sec, lead_kind, lead_vol * 0.8, duty=0.5 if lead_duty != 0.5 else 0.25,
                    transpose=12, decay=0.15, sustain=0.5)
    else:
        render_part(buf, second, beat_sec, lead_kind, lead_vol, duty=lead_duty, decay=0.15, sustain=0.55)
    if counter:
        cn = [(b + span, m, d) for b, m, d in parse(counter)]
        render_part(buf, cn, beat_sec, "tri", lead_vol * 0.8, decay=0.2, sustain=0.6)
    if drums:
        render_drums(buf, drums, beat_sec, bars * loops, beats_per_bar, 0.35)
    write_wav(os.path.join(ROOT, "music", name + ".wav"), master(buf, 0.6), loop=True)
    print("music", name, "%.1f с" % (len(buf) / SR))


def music():
    # Титульный экран: тёплая праздничная тема (до мажор)
    song("title", 100, 4, ["C", "G", "Am", "F", "C", "G", "F", "C"], "arp",
         "E5:1 D5:.5 C5:.5 G4:2 B4:1 C5:.5 D5:.5 G4:2 C5:1 E5:1 A5:1.5 G5:.5 F5:1 E5:.5 D5:.5 C5:2 "
         "E5:1 D5:.5 C5:.5 G4:1.5 G4:.5 B4:1 D5:1 G5:2 A5:1 G5:.5 F5:.5 E5:1 D5:1 C5:4",
         counter="C4:4 B3:4 A3:4 A3:4 C4:4 D4:4 C4:4 E4:4",
         drums={"kick": [0, 2], "hat": [0.5, 1.5, 2.5, 3.5]}, repeat_up=True)

    # Завязка: таинственно, без барабанов (ля минор)
    song("intro", 76, 4, ["Am", "F", "Dm", "E", "Am", "F", "Dm", "E"], "arp",
         "r:2 E5:1 C5:1 D5:2 A4:2 F4:2 A4:1 D5:1 B4:3 G#4:1 "
         "r:2 E5:1 A5:1 G5:2 F5:2 F5:1 E5:1 D5:1 C5:1 B4:4",
         lead_kind="tri", comp_vol=0.08, lead_vol=0.35)

    # Хаб: бодрая прогулка по фестивалю (фа мажор)
    song("hub", 116, 4, ["F", "C", "Dm", "Bb", "F", "C", "Bb", "C"], "oompah",
         "A4:.5 C5:.5 F5:1 E5:.5 D5:.5 C5:1 G4:.5 A4:.5 Bb4:.5 C5:.5 G4:2 "
         "A4:.5 F4:.5 A4:.5 D5:.5 C5:1 A4:1 Bb4:1 D5:1 F5:2 "
         "A5:.5 G5:.5 F5:1 C5:1 A4:1 G4:.5 A4:.5 Bb4:.5 C5:.5 E5:2 "
         "D5:1 Bb4:.5 D5:.5 F5:1 D5:1 C5:.5 D5:.5 E5:.5 G5:.5 F5:2",
         drums={"kick": [0, 2], "snare": [1, 3], "hat": [0.5, 1.5, 2.5, 3.5]}, repeat_up=True)

    # Закулисье: детектив крадётся (ре минор, шагающий бас)
    song("backstage", 92, 4, ["Dm", "Dm", "Bb", "A", "Dm", "Gm", "Bb", "A"], "walk",
         "r:1 D5:.5 r:.5 F5:.5 r:.5 E5:1 r:2 D5:.5 C#5:.5 D5:1 "
         "r:1 F5:.5 r:.5 Bb5:.5 r:.5 A5:1 r:1 G5:.5 F5:.5 E5:2 "
         "r:1 D5:.5 r:.5 F5:.5 r:.5 A5:1 r:1 G5:.5 F5:.5 G5:1 "
         "r:1 F5:.5 E5:.5 D5:.5 r:.5 C#5:1 E5:1 A4:4",
         lead_duty=0.125, comp_vol=0.0, lead_vol=0.25, bass_vol=0.45,
         drums={"hat": [0, 1, 2, 3], "snare": [3.5]})

    # Финал: разгадка, напряжение и азарт (ля минор, гонящий бас)
    song("finale", 128, 4, ["Am", "F", "C", "G", "Am", "F", "G", "E"], "drive",
         "A4:.5 C5:.5 E5:1 A5:1 G5:.5 E5:.5 F5:1 E5:.5 D5:.5 C5:2 "
         "E5:.5 G5:.5 C6:1 B5:.5 A5:.5 G5:1.5 D5:.5 G5:1 "
         "A5:.5 G5:.5 E5:1 C5:1 E5:1 F5:.5 E5:.5 D5:.5 C5:.5 D5:2 "
         "E5:1 D5:.5 C5:.5 B4:1 D5:1 E5:1 G#5:1 B5:4",
         drums={"kick": [0, 1, 2, 3], "snare": [1, 3], "hat": [0.5, 1.5, 2.5, 3.5]}, repeat_up=True)

    # Маня: ласковый вальс арт-маркета (соль мажор, 3/4)
    song("manya", 138, 3, ["G", "D", "Em", "C", "G", "C", "D", "G"], "waltz",
         "B4:2 D5:1 G5:2 F#5:1 E5:2 D5:1 C5:3 B4:2 C5:1 D5:2 G5:1 "
         "F#5:1.5 E5:.5 D5:1 G5:3",
         lead_kind="pulse", lead_duty=0.5, comp_kind="tri", comp_vol=0.12, repeat_up=True)

    # Леня: мечтательно, мотив его «Новой мелодии» (до мажор)
    song("lenya", 84, 4, ["C", "Am", "F", "G", "C", "Am", "F", "G"], "arp",
         "E5:1 G5:1 C6:1 G5:1 A5:1 G5:1 C5:2 A5:1 C6:1 B5:1 A5:1 G5:1.5 A5:.5 B5:1 D6:1 "
         "F5:1 A5:1 C6:2 A5:1 F5:1 E5:2 D5:1 E5:1 G5:2 F5:1 D5:1 G5:2",
         lead_kind="tri", comp_vol=0.1, lead_vol=0.38,
         drums={"hat": [1, 3]})

    # Катя: ретро-диско с подиума (ми минор, «бочка» на каждую долю)
    song("katya", 120, 4, ["Em", "Em", "C", "D", "Em", "Em", "Am", "B"], "octave",
         "E5:.5 r:.5 E5:.5 G5:.5 r:.5 A5:.5 B5:1 r:2 D6:.5 B5:.5 A5:1 "
         "G5:.5 r:.5 G5:.5 E5:.5 r:.5 G5:.5 A5:1 F#5:.5 G5:.5 F#5:.5 D5:.5 E5:2 "
         "E5:.5 r:.5 E5:.5 G5:.5 r:.5 A5:.5 B5:1 r:2 E6:.5 D6:.5 B5:1 "
         "C6:.5 B5:.5 A5:.5 G5:.5 F#5:1 A5:1 B5:2 D#5:2",
         lead_duty=0.25, comp_vol=0.1,
         drums={"kick": [0, 1, 2, 3], "snare": [1, 3], "hat": [0.5, 1.5, 2.5, 3.5]})

    # Мойто: цирковой галоп конкурсов (до мажор, быстро)
    song("moyto", 168, 4, ["C", "C", "G", "G", "G", "G", "C", "C"], "oompah",
         "E5:.5 F5:.5 G5:1 G5:.5 A5:.5 G5:1 E5:.5 F5:.5 G5:1 C6:1 G5:1 "
         "F5:.5 E5:.5 D5:1 D5:.5 E5:.5 F5:1 G5:.5 F5:.5 E5:.5 D5:.5 B4:2 "
         "D5:.5 E5:.5 F5:1 F5:.5 G5:.5 F5:1 D5:.5 E5:.5 F5:1 B5:1 G5:1 "
         "E5:.5 D5:.5 C5:1 E5:1 G5:1 C6:1 G5:1 C5:2",
         lead_duty=0.5, comp_vol=0.14,
         drums={"kick": [0, 2], "snare": [1, 3]}, repeat_up=True)

    # Сулус: важный профессор (си-бемоль мажор, неторопливо, «фагот» внизу)
    song("sulus", 96, 4, ["Bb", "Eb", "Bb", "F", "Gm", "Eb", "F", "Bb"], "walk",
         "D4:1 F4:1 Bb4:1.5 A4:.5 G4:1 F4:1 Eb4:2 C4:1 Eb4:1 G4:1.5 F4:.5 D4:1 C4:1 A3:2 "
         "Bb3:1 D4:1 G4:1.5 F4:.5 Eb4:1 G4:1 C5:2 A4:1 G4:.5 F4:.5 G4:1 A4:1 Bb4:4",
         lead_kind="pulse", lead_duty=0.5, lead_vol=0.28, bass_vol=0.4, comp_vol=0.0,
         counter="r:12 Bb4:2 C5:2 D5:4 Eb5:4 D5:2 C5:2 Bb4:4",
         drums={"kick": [0, 2], "hat": [1, 3]})

# endregion


# region Звуки

def tone_seq(seq, kind="pulse", duty=0.5, vol=0.5, gap=0.0, **env_kw):
    """Последовательность нот: [(частота или имя, секунды)]."""
    parts = []
    for f, dur in seq:
        n = int(dur * SR)
        freq = hz(midi(f)) if isinstance(f, str) else f
        parts.append(osc(kind, freq, n, duty=duty) * env(n, **env_kw) * vol)
        if gap:
            parts.append(np.zeros(int(gap * SR)))
    return np.concatenate(parts)


def sweep(f0, f1, dur, kind="pulse", duty=0.5, vol=0.5):
    n = int(dur * SR)
    f = np.geomspace(f0, f1, n)
    phase = np.cumsum(f) / SR % 1.0
    if kind == "pulse":
        x = np.where(phase < duty, 1.0, -1.0)
    elif kind == "tri":
        x = 2 * np.abs(2 * phase - 1) - 1
    else:
        x = np.sin(2 * np.pi * phase)
    return x * env(n, decay=dur, sustain=0.2, release=0.02) * vol


def swish(dur, k0, k1, vol=0.4):
    """Шорох: шум с плавающим фильтром (страница, занавес)."""
    n = int(dur * SR)
    x = noise(n)
    k = np.linspace(k0, k1, n)
    y = np.empty(n)
    acc = 0.0
    for i in range(n):
        acc += k[i] * (x[i] - acc)
        y[i] = acc
    shape = np.sin(np.linspace(0, np.pi, n)) ** 1.5
    return y * shape * vol / max(1e-6, np.max(np.abs(y)))


def voice(kind, freq, duty=0.5, dur=0.05, slide=0.0, vol=0.35):
    """«Голос» персонажа: короткий писк на каждую пару букв, как в Undertale."""
    n = int(dur * SR)
    f = freq * (1 + slide * np.linspace(0, 1, n))
    phase = np.cumsum(f) / SR % 1.0
    if kind == "pulse":
        x = np.where(phase < duty, 1.0, -1.0)
    elif kind == "tri":
        x = 2 * np.abs(2 * phase - 1) - 1
    else:
        x = 2 * phase - 1
    return x * env(n, attack=0.002, decay=dur, sustain=0.3, release=0.01) * vol


def sfx(name, data):
    data = np.concatenate([data, np.zeros(int(0.01 * SR))])
    write_wav(os.path.join(ROOT, "sfx", name + ".wav"), data)


def sounds():
    sfx("ui_move", tone_seq([(880, 0.035)], duty=0.25, vol=0.25, release=0.01))
    sfx("ui_select", tone_seq([("E5", 0.05), ("B5", 0.08)], duty=0.25, vol=0.3, release=0.02))
    sfx("ui_open", tone_seq([("C5", 0.04), ("E5", 0.04), ("G5", 0.06)], duty=0.25, vol=0.25))
    sfx("ui_close", tone_seq([("G5", 0.04), ("E5", 0.04), ("C5", 0.06)], duty=0.25, vol=0.25))

    # Шаги: глухой стук (площадь) — два варианта по очереди
    for i, k in enumerate((0.08, 0.11)):
        n = int(0.05 * SR)
        x = lowpass(noise(n), k) * np.exp(-np.arange(n) / SR * 70)
        sfx("step_%d" % i, x * 0.9 / np.max(np.abs(x)))

    sfx("page", swish(0.22, 0.05, 0.5, 0.35))
    sfx("door", swish(0.45, 0.02, 0.2, 0.45))
    sfx("correct", tone_seq([("C6", 0.07), ("G6", 0.14)], duty=0.5, vol=0.3))
    sfx("wrong", tone_seq([("D3", 0.1), ("C#3", 0.2)], kind="saw", vol=0.35, sustain=0.8))
    sfx("swap", sweep(400, 900, 0.07, vol=0.25))
    stamp = np.concatenate([drum("kick") * 0.9,
                            tone_seq([("C5", 0.06), ("E5", 0.06), ("G5", 0.06), ("C6", 0.25)],
                                     duty=0.25, vol=0.3)])
    sfx("stamp", stamp)
    sfx("win", tone_seq([("C5", 0.1), ("E5", 0.1), ("G5", 0.1), ("C6", 0.2), ("G5", 0.1), ("C6", 0.5)],
                        duty=0.25, vol=0.35, sustain=0.7))
    sfx("lose", tone_seq([("G4", 0.18), ("F#4", 0.18), ("F4", 0.18), ("E4", 0.5)],
                         kind="tri", vol=0.45, sustain=0.8))
    sfx("tick", tone_seq([(1400, 0.02)], duty=0.5, vol=0.2, release=0.005))

    # Голоса: тембр и высота — характер (docs/GAME.md → «Характеры маскотов»)
    sfx("voice_manya", voice("pulse", 620, duty=0.25))          # хлопотливая, тёплая
    sfx("voice_lenya", voice("tri", 330, dur=0.07, vol=0.45))   # спокойный, мягкий
    sfx("voice_katya", voice("pulse", 900, duty=0.125, dur=0.04))  # звонкая, быстрая
    sfx("voice_moyto", voice("pulse", 560, duty=0.5, slide=-0.35))  # «гав» вниз
    sfx("voice_sulus", voice("saw", 170, dur=0.07, vol=0.3))    # низкий, важный
    sfx("voice_guest", voice("pulse", 460, duty=0.25, dur=0.045, vol=0.28))
    sfx("voice_narrator", voice("tri", 240, dur=0.035, vol=0.4))
    print("sfx ok")

# endregion


if __name__ == "__main__":
    music()
    sounds()
