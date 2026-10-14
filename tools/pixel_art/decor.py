"""Оформление: задники мини-игр и Детективный блокнот.

    python tools/pixel_art/decor.py

Пишет:
  game/art/minigames/backdrop_<маскот>.png — 640×360, во всю сцену мини-игры
      (manya — арт-маркет, moyto — цирковой шатёр, sulus — лекторий, katya — подиум).
      Середина кадра тёмная и спокойная: там текст и сама игра.
  game/art/notebook/notebook.png   — разворот блокнота 592×328
  game/art/notebook/stamp_<маскот>.png, stamp_empty.png — печати 40×40

Черновик (см. docs/ASSETS.md): после ручной перерисовки убрать файл из MAIN.
"""
import os
import random

from PIL import Image, ImageDraw

from palette import OUT

ART = os.path.join(os.path.dirname(__file__), "..", "..", "game", "art")
W, H = 640, 360

# Брендбук (game/scripts/brand.gd)
ORANGE = (228, 136, 36, 255)
SALMON = (212, 132, 100, 255)
BROWN = (96, 64, 48, 255)
BLUE = (120, 176, 200, 255)
RED = (204, 92, 96, 255)
GREEN = (116, 176, 104, 255)
CREAM = (255, 244, 230, 255)

MASCOT_COLORS = {"manya": SALMON, "lenya": BLUE, "katya": GREEN, "moyto": RED, "sulus": ORANGE}


def shade(c, k):
    """k < 1 — темнее, k > 1 — светлее."""
    if k <= 1:
        return tuple(int(v * k) for v in c[:3]) + (c[3],)
    return tuple(int(v + (255 - v) * (k - 1)) for v in c[:3]) + (c[3],)


def save(im, *parts):
    path = os.path.join(ART, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path)
    print("decor", "/".join(parts))


def vignette(im, strength=0.55):
    """Края светлее, середина темнее: на середине — текст мини-игры."""
    px = im.load()
    for y in range(H):
        for x in range(W):
            dx = (x - W / 2) / (W / 2)
            dy = (y - H / 2) / (H / 2)
            d = min(1.0, (dx * dx * 0.8 + dy * dy * 1.2))
            k = 1 - strength * (1 - d)
            # шахматный дизеринг на границе, чтобы не было полос
            if (x + y) % 2 and 0.3 < d < 0.7:
                k += 0.03
            r, g, b, a = px[x, y]
            px[x, y] = (int(r * k), int(g * k), int(b * k), a)


def bunting(d, y, colors, step=24):
    d.line([(0, y), (W, y + 4)], fill=OUT)
    for i, x in enumerate(range(4, W, step)):
        c = colors[i % len(colors)]
        yy = y + x * 4 // W
        d.polygon([(x, yy + 1), (x + step - 8, yy + 1), (x + (step - 8) // 2, yy + 12)], fill=c, outline=OUT)


def floor_planks(d, top, color):
    d.rectangle([0, top, W, H], fill=color)
    d.line([(0, top), (W, top)], fill=OUT)
    for y in range(top + 8, H, 8):
        d.line([(0, y), (W, y)], fill=shade(color, 0.8))
    rnd = random.Random(top)
    for y in range(top, H, 8):
        for x in range(rnd.randint(0, 60), W, 90):
            d.line([(x, y + 1), (x, y + 7)], fill=shade(color, 0.8))


# region Задники

def backdrop_manya():
    """Арт-маркет: дощатая стена, гирлянда, мольберт, банка с кистями, палитра."""
    wall = shade(SALMON, 0.42)
    im = Image.new("RGBA", (W, H), wall)
    d = ImageDraw.Draw(im)
    for x in range(0, W, 32):
        d.line([(x, 0), (x, H)], fill=shade(wall, 0.85))
    rnd = random.Random(1)
    for _ in range(40):  # брызги краски на стене
        x, y = rnd.randrange(W), rnd.randrange(40, 300)
        c = rnd.choice([ORANGE, BLUE, GREEN, RED, CREAM])
        d.point([(x, y), (x + 1, y), (x, y + 1)], fill=shade(c, 0.55))
    floor_planks(d, 322, shade(BROWN, 0.9))
    vignette(im, 0.5)
    d = ImageDraw.Draw(im)
    bunting(d, 2, [ORANGE, BLUE, GREEN, RED, SALMON])
    # банка с кистями — левый нижний угол
    d.rectangle([14, 300, 34, 330], fill=BLUE, outline=OUT)
    d.rectangle([16, 302, 18, 328], fill=shade(BLUE, 1.3))
    for i, c in enumerate([RED, ORANGE, GREEN]):
        x = 18 + i * 6
        d.line([(x, 300), (x - 4 + i * 4, 278)], fill=BROWN, width=2)
        d.rectangle([x - 6 + i * 4, 274, x - 3 + i * 4, 279], fill=c, outline=OUT)
    # палитра — правый нижний угол
    d.ellipse([570, 312, 630, 344], fill=(222, 184, 135, 255), outline=OUT)
    d.ellipse([578, 330, 588, 338], fill=wall, outline=OUT)
    for i, c in enumerate([RED, ORANGE, GREEN, BLUE, CREAM]):
        cx, cy = 592 + i * 7, 318 + (i % 2) * 6
        d.ellipse([cx, cy, cx + 5, cy + 4], fill=c)
    # рамы с картинами по краям
    for x, y, c in [(6, 60, BLUE), (6, 150, GREEN), (594, 60, ORANGE), (596, 160, RED)]:
        d.rectangle([x, y, x + 38, y + 48], fill=(222, 184, 135, 255), outline=OUT)
        d.rectangle([x + 4, y + 4, x + 34, y + 44], fill=shade(c, 0.8))
        d.polygon([(x + 4, y + 44), (x + 16, y + 26), (x + 26, y + 44)], fill=shade(c, 0.55))
        d.ellipse([x + 22, y + 9, x + 29, y + 16], fill=CREAM)
    return im


def backdrop_moyto():
    """Цирковой шатёр конкурсов: полосы, фестон, прожекторы, арена."""
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    a, b = shade(RED, 0.5), shade(RED, 0.36)
    for i, x in enumerate(range(0, W, 40)):
        d.rectangle([x, 0, x + 39, H], fill=a if i % 2 else b)
    # арена
    d.ellipse([60, 290, 580, 420], fill=(150, 110, 70, 255), outline=OUT)
    d.ellipse([80, 300, 560, 410], fill=(196, 160, 110, 255))
    vignette(im, 0.45)
    d = ImageDraw.Draw(im)
    # прожекторы — светлые клинья с дизерингом
    px = im.load()
    for sx in (40, 600):
        for y in range(30, 330):
            half = (y - 30) * 0.28
            cx = sx + (320 - sx) * (y - 30) / 600
            for x in range(int(cx - half), int(cx + half)):
                if 0 <= x < W and (x + y) % 3 == 0:
                    r, g, bl, al = px[x, y]
                    px[x, y] = (min(255, r + 40), min(255, g + 34), min(255, bl + 12), al)
        d.rectangle([sx - 8, 18, sx + 8, 32], fill=(70, 70, 80, 255), outline=OUT)
        d.ellipse([sx - 5, 28, sx + 5, 36], fill=(255, 236, 160, 255), outline=OUT)
    # фестон по верху
    d.rectangle([0, 0, W, 10], fill=shade(ORANGE, 0.8))
    for x in range(0, W, 20):
        d.pieslice([x, 0, x + 20, 20], 0, 180, fill=ORANGE, outline=OUT)
        d.ellipse([x + 8, 16, x + 12, 20], fill=(255, 216, 90, 255))
    # звёзды-лампочки по краям
    for y in range(60, 280, 36):
        for x in (10, 626):
            d.ellipse([x, y, x + 4, y + 4], fill=(255, 216, 90, 255))
    return im


def backdrop_sulus():
    """Лекторий: стена с панелями, книжные полки по краям, паркет."""
    wall = shade(ORANGE, 0.3)
    im = Image.new("RGBA", (W, H), wall)
    d = ImageDraw.Draw(im)
    # обои — мелкий ромб
    for y in range(4, 250, 12):
        for x in range((y // 12 % 2) * 8, W, 16):
            d.point([(x, y)], fill=shade(wall, 1.15))
    # панели внизу стены
    d.rectangle([0, 250, W, 322], fill=shade(BROWN, 0.85), outline=OUT)
    for x in range(8, W, 64):
        d.rectangle([x, 258, x + 52, 314], outline=shade(BROWN, 0.6))
    floor_planks(d, 322, shade(BROWN, 1.1))
    vignette(im, 0.45)
    d = ImageDraw.Draw(im)
    rnd = random.Random(5)
    for x0 in (0, 588):  # книжные шкафы
        d.rectangle([x0, 40, x0 + 52, 322], fill=shade(BROWN, 0.7), outline=OUT)
        for shelf in range(48, 310, 44):
            x = x0 + 4
            while x < x0 + 46:
                w = rnd.randint(4, 7)
                h = rnd.randint(26, 36)
                c = rnd.choice([RED, BLUE, GREEN, ORANGE, SALMON, CREAM])
                d.rectangle([x, shelf + 38 - h, x + w - 1, shelf + 38], fill=shade(c, 0.75), outline=OUT)
                x += w
            d.line([(x0 + 2, shelf + 39), (x0 + 50, shelf + 39)], fill=OUT, width=2)
    # глобус на полу справа
    d.ellipse([548, 288, 576, 316], fill=BLUE, outline=OUT)
    d.arc([548, 288, 576, 316], 200, 340, fill=GREEN, width=3)
    d.line([(562, 316), (562, 324)], fill=OUT, width=2)
    d.rectangle([554, 322, 570, 326], fill=BROWN, outline=OUT)
    return im


def backdrop_katya():
    """Подиум дефиле: кулисы по бокам, лампочки-рамка, дорожка подиума."""
    back = shade(GREEN, 0.3)
    im = Image.new("RGBA", (W, H), back)
    d = ImageDraw.Draw(im)
    # дорожка подиума в перспективе
    d.polygon([(250, 360), (390, 360), (350, 250), (290, 250)], fill=(110, 80, 120, 255), outline=OUT)
    d.line([(320, 252), (320, 360)], fill=(150, 116, 160, 255))
    vignette(im, 0.45)
    d = ImageDraw.Draw(im)
    rnd = random.Random(3)
    for _ in range(50):  # блёстки
        x, y = rnd.randrange(60, 580), rnd.randrange(30, 240)
        d.point([(x, y)], fill=shade(CREAM, 0.6))
    # кулисы
    for x0, x1, step in ((0, 56, 1), (584, 640, -1)):
        d.rectangle([x0, 0, x1, H], fill=shade(RED, 0.6))
        for x in range(x0 + 4, x1, 8):
            d.line([(x, 0), (x, H)], fill=shade(RED, 0.42), width=2)
        d.line([(x1 if step == 1 else x0, 0), (x1 if step == 1 else x0, H)], fill=OUT)
    # рамка из лампочек сверху
    d.rectangle([56, 0, 584, 14], fill=shade(BROWN, 0.8), outline=OUT)
    for x in range(64, 580, 16):
        d.ellipse([x, 4, x + 6, 10], fill=(255, 226, 120, 255), outline=OUT)
    # диско-шар
    d.line([(320, 14), (320, 24)], fill=OUT)
    d.ellipse([310, 24, 330, 44], fill=(190, 196, 210, 255), outline=OUT)
    for y in range(28, 42, 4):
        for x in range(312 + (y % 8), 328, 4):
            d.point([(x, y)], fill=CREAM)
    return im

# endregion


# region Блокнот

NB_W, NB_H = 592, 328
PAPER = (250, 240, 214, 255)
PAPER_SH = (226, 210, 176, 255)
RULE = (196, 210, 222, 255)
MARGIN = (226, 150, 140, 255)
LEATHER = (110, 66, 40, 255)


def notebook():
    """Разворот: кожаная обложка, две страницы в линейку, пружина, закладки, скрепка."""
    im = Image.new("RGBA", (NB_W, NB_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 4, NB_W - 1, NB_H - 1], 8, fill=LEATHER, outline=OUT)
    d.rounded_rectangle([3, 7, NB_W - 4, NB_H - 4], 6, outline=shade(LEATHER, 1.25))
    # закладки сверху
    for x, c in ((60, RED), (84, BLUE), (440, GREEN)):
        d.rectangle([x, 0, x + 14, 14], fill=c, outline=OUT)
    mid = NB_W // 2
    for x0, x1 in ((10, mid - 4), (mid + 4, NB_W - 11)):
        d.rectangle([x0 + 2, 14, x1 + 2, NB_H - 10], fill=PAPER_SH)  # стопка листов
        d.rectangle([x0, 12, x1, NB_H - 12], fill=PAPER, outline=OUT)
        for y in range(52, NB_H - 16, 14):
            d.line([(x0 + 4, y), (x1 - 4, y)], fill=RULE)
    d.line([(36, 13), (36, NB_H - 13)], fill=MARGIN)
    d.line([(mid + 30, 13), (mid + 30, NB_H - 13)], fill=MARGIN)
    # пружина
    for y in range(22, NB_H - 18, 12):
        d.ellipse([mid - 8, y, mid + 8, y + 6], outline=(150, 150, 160, 255), width=2)
        d.point([(mid - 5, y + 1)], fill=CREAM)
    # скрепка на правой странице
    d.rounded_rectangle([NB_W - 40, 6, NB_W - 30, 36], 4, outline=(150, 150, 160, 255), width=2)
    d.rounded_rectangle([NB_W - 37, 12, NB_W - 33, 30], 2, outline=(150, 150, 160, 255))
    # отпечаток лапы-«клякса» в углу левой страницы
    for cx, cy, r in ((38, 300, 5), (30, 290, 2), (38, 287, 2), (46, 290, 2)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(60, 60, 90, 120))
    return im


def _stamp_ring(d, c, dashed=False):
    if dashed:
        for a in range(0, 360, 30):
            d.arc([2, 2, 37, 37], a, a + 15, fill=c, width=2)
        return
    d.ellipse([2, 2, 37, 37], outline=c, width=3)
    d.ellipse([7, 7, 32, 32], outline=c)


def stamp(mascot):
    """Печать: чернильный круг цвета маскота и значок его зоны."""
    c = shade(MASCOT_COLORS[mascot], 0.85)
    im = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    _stamp_ring(d, c)
    if mascot == "manya":  # кисть
        d.line([(13, 27), (25, 13)], fill=c, width=3)
        d.polygon([(11, 29), (14, 24), (16, 27)], fill=c)
    elif mascot == "lenya":  # нота
        d.ellipse([12, 22, 19, 28], fill=c)
        d.line([(18, 25), (18, 11)], fill=c, width=2)
        d.line([(18, 11), (25, 14)], fill=c, width=2)
    elif mascot == "katya":  # звезда подиума
        d.polygon([(20, 10), (23, 17), (30, 17), (24, 22), (27, 29), (20, 25), (13, 29), (16, 22),
                   (10, 17), (17, 17)], fill=c)
    elif mascot == "moyto":  # «?» викторины
        d.arc([14, 10, 26, 20], 180, 30, fill=c, width=3)
        d.line([(24, 18), (20, 22), (20, 25)], fill=c, width=3)
        d.rectangle([19, 27, 21, 29], fill=c)
    elif mascot == "sulus":  # раскрытая книга
        d.polygon([(10, 14), (19, 16), (19, 28), (10, 26)], outline=c, fill=None)
        d.polygon([(30, 14), (21, 16), (21, 28), (30, 26)], outline=c, fill=None)
        d.line([(12, 19), (17, 20)], fill=c)
        d.line([(23, 20), (28, 19)], fill=c)
    # «чернила легли неровно»: выбить несколько пикселей
    rnd = random.Random(mascot)
    px = im.load()
    for _ in range(26):
        x, y = rnd.randrange(40), rnd.randrange(40)
        if px[x, y][3]:
            px[x, y] = (0, 0, 0, 0)
    return im


def stamp_empty():
    im = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = (180, 160, 130, 255)
    _stamp_ring(d, c, dashed=True)
    d.arc([15, 11, 25, 19], 180, 30, fill=c, width=2)
    d.line([(23, 17), (20, 21), (20, 24)], fill=c, width=2)
    d.rectangle([19, 26, 20, 27], fill=c)
    return im

# endregion


def main():
    # Задники мини-игр с 2026-10-15 генерирует tools/ai_art/ (исходником служат
    # функции backdrop_* отсюда — через снимок raw/_init). Здесь — только блокнот.
    save(notebook(), "notebook", "notebook.png")
    for mascot in MASCOT_COLORS:
        save(stamp(mascot), "notebook", "stamp_%s.png" % mascot)
    save(stamp_empty(), "notebook", "stamp_empty.png")


if __name__ == "__main__":
    main()
