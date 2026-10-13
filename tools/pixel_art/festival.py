"""Фестивальные декорации хаба и закулисье.

Хаб — площадь фестиваля, не лес: палатки, гирлянды, гости и три сектора
прошлых фестивалей — «Космос» (у музыкальной сцены, там и ракета-тайник),
«Цирк» (у шатра Мойто), «Ретро» (у дефиле Кати).
"""
from palette import *
from environment import WOOD, WOOD_D, WOOD_L, RED, RED_D, YELLOW

# Пиксельный шрифт 3–5×5 — только буквы, которые нужны на вывесках
GLYPHS = {
    "Х": ["X.X", "X.X", ".X.", "X.X", "X.X"],
    "О": [".X.", "X.X", "X.X", "X.X", ".X."],
    "Т": ["XXX", ".X.", ".X.", ".X.", ".X."],
    "Н": ["X.X", "X.X", "XXX", "X.X", "X.X"],
    "П": ["XXX", "X.X", "X.X", "X.X", "X.X"],
    "Р": ["XX.", "X.X", "XX.", "X..", "X.."],
    "И": ["X..X", "X.XX", "XX.X", "X..X", "X..X"],
    "З": ["XX.", "..X", ".X.", "..X", "XX."],
    "Ы": ["X...X", "X...X", "XX..X", "X.X.X", "XX..X"],
    "Ч": ["X.X", "X.X", ".XX", "..X", "..X"],
    "А": [".X.", "X.X", "XXX", "X.X", "X.X"],
    "Й": [".X..", "X..X", "X.XX", "XX.X", "X..X"],
    "К": ["X.X", "X.X", "XX.", "X.X", "X.X"],
    "С": [".XX", "X..", "X..", "X..", ".XX"],
    "М": ["X...X", "XX.XX", "X.X.X", "X...X", "X...X"],
    "Ц": ["X.X.", "X.X.", "X.X.", "XXXX", "...X"],
    "Е": ["XXX", "X..", "XX.", "X..", "XXX"],
    " ": ["..", "..", "..", "..", ".."],
}


def text_width(text, scale=1):
    return sum((len(GLYPHS[c][0]) + 1) * scale for c in text) - scale


def draw_text(im, x, y, text, color, scale=1):
    px = im.load()
    for c in text:
        glyph = GLYPHS[c]
        for gy, row in enumerate(glyph):
            for gx, cell in enumerate(row):
                if cell == "X":
                    for sy in range(scale):
                        for sx in range(scale):
                            px[x + gx * scale + sx, y + gy * scale + sy] = color
        x += (len(glyph[0]) + 1) * scale


def draw_text_centered(im, cx, y, text, color, scale=1):
    draw_text(im, cx - text_width(text, scale) // 2, y, text, color, scale)


# ---------------------------------------------------------------- общие

def gate_hoton():
    """Вход 80×60 с вывеской «ХОТОН» и флажками в цветах маскотов."""
    im, d = canvas(80, 60)
    d.rectangle([4, 10, 11, 58], fill=WOOD, outline=OUT)
    d.rectangle([68, 10, 75, 58], fill=WOOD, outline=OUT)
    d.rectangle([0, 0, 79, 15], fill=ACCENT, outline=OUT)
    draw_text_centered(im, 40, 3, "ХОТОН", WHITE, scale=2)
    colors = [(236, 140, 160, 255), (80, 110, 200, 255), (64, 170, 76, 255), (224, 72, 44, 255),
              (206, 230, 242, 255)]
    for i, x in enumerate(range(14, 66, 6)):
        d.polygon([(x, 16), (x + 5, 16), (x + 2, 22)], fill=colors[i % len(colors)], outline=OUT)
    return im


def bunting():
    """Два столбика с гирляндой флажков и лампочек, 72×46."""
    im, d = canvas(72, 46)
    for x in (2, 67):
        d.rectangle([x, 4, x + 2, 45], fill=(120, 120, 130, 255), outline=OUT)
        d.ellipse([x - 1, 0, x + 3, 4], fill=YELLOW, outline=OUT)
    pts = [(4 + i, 8 + round(10 * (1 - ((i - 32) / 32) ** 2))) for i in range(64)]
    d.line(pts, fill=OUT)
    colors = [RED, YELLOW, (80, 140, 230, 255), (64, 170, 76, 255), ACCENT]
    for i, (x, y) in enumerate(pts[4:60:7]):
        d.polygon([(x - 2, y), (x + 3, y), (x, y + 5)], fill=colors[i % len(colors)], outline=OUT)
    return im


def tea_stall():
    """Чайная 60×50: бирюзовый навес, самовар, чашки — гостей греют."""
    im, d = canvas(60, 50)
    teal = (60, 160, 160, 255)
    d.line([(4, 12), (4, 46)], fill=WOOD_D, width=2)
    d.line([(54, 12), (54, 46)], fill=WOOD_D, width=2)
    d.rectangle([1, 28, 58, 46], fill=WOOD, outline=OUT)
    d.line([(2, 31), (57, 31)], fill=WOOD_L)
    for i, x in enumerate(range(0, 60, 6)):
        d.polygon([(x, 6), (x + 6, 6), (x + 6, 14), (x + 3, 16), (x, 14)],
                  fill=teal if i % 2 == 0 else WHITE, outline=OUT)
    d.rectangle([0, 0, 59, 6], fill=teal, outline=OUT)
    draw_text_centered(im, 30, 1, "ЧАЙ", WHITE)
    # самовар
    d.ellipse([10, 16, 22, 28], fill=(214, 170, 70, 255), outline=OUT)
    d.rectangle([14, 13, 18, 16], fill=(214, 170, 70, 255), outline=OUT)
    d.point((23, 22), fill=OUT)
    for x in (30, 38, 46):  # чашки
        d.rectangle([x, 23, x + 4, 27], fill=WHITE, outline=OUT)
        d.point((x + 2, 20), fill=(200, 200, 210, 255))
    return im


def bench():
    """Скамейка 40×20."""
    im, d = canvas(40, 20)
    d.rectangle([0, 2, 39, 8], fill=WOOD, outline=OUT)
    d.line([(1, 5), (38, 5)], fill=WOOD_D)
    d.rectangle([0, 10, 39, 14], fill=WOOD_L, outline=OUT)
    for x in (3, 34):
        d.rectangle([x, 14, x + 2, 19], fill=(80, 80, 90, 255), outline=OUT)
    return im


def balloons():
    """Связка шариков 26×48."""
    im, d = canvas(26, 48)
    for (x, y), c in (((2, 4), RED), ((13, 0), (80, 140, 230, 255)), ((8, 12), YELLOW)):
        d.line([(x + 5, y + 13), (13, 46)], fill=OUT)
        d.ellipse([x, y, x + 10, y + 12], fill=c, outline=OUT)
        d.point((x + 3, y + 3), fill=WHITE)
    return im


def guest_rope():
    """Ограждение для очереди 56×22: столбики с красной лентой."""
    im, d = canvas(56, 22)
    d.line([(4, 6), (28, 10), (51, 6)], fill=RED, width=2)
    for x in (2, 26, 49):
        d.rectangle([x, 3, x + 4, 19], fill=(214, 170, 70, 255), outline=OUT)
        d.ellipse([x - 1, 17, x + 5, 21], fill=(150, 120, 60, 255), outline=OUT)
    return im


def lamp():
    """Фонарь 12×52."""
    im, d = canvas(12, 52)
    d.rectangle([4, 10, 7, 50], fill=(70, 74, 86, 255), outline=OUT)
    d.rectangle([1, 1, 10, 10], fill=(255, 230, 150, 255), outline=OUT)
    d.line([(5, 2), (5, 9)], fill=WHITE)
    d.rectangle([2, 48, 9, 51], fill=(70, 74, 86, 255), outline=OUT)
    return im


# ---------------------------------------------------------------- «Космос»

def planet():
    """Картонная планета с кольцом на палке 40×56."""
    im, d = canvas(40, 56)
    d.rectangle([18, 26, 21, 55], fill=WOOD_D, outline=OUT)
    d.ellipse([10, 4, 30, 24], fill=(236, 160, 80, 255), outline=OUT)
    d.arc([10, 4, 30, 24], 200, 290, fill=(250, 200, 130, 255))
    d.line([(14, 12), (26, 12)], fill=(210, 130, 60, 255))
    d.ellipse([0, 11, 39, 19], outline=OUT)
    d.ellipse([1, 12, 38, 18], outline=CARD_L)
    return im


def star_sign():
    """Картонная звезда на палке 24×44."""
    im, d = canvas(24, 44)
    d.rectangle([10, 18, 13, 43], fill=WOOD_D, outline=OUT)
    d.polygon(_star(11.5, 11, 11, 5), fill=YELLOW, outline=OUT)
    return im


def _star(cx, cy, r_out, r_in):
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = -pi / 2 + i * pi / 5
        pts.append((round(cx + cos(a) * r), round(cy + sin(a) * r)))
    return pts


def astronaut_board():
    """Фотостенд «Космонавт» с дыркой для лица, 44×60 — фотозона «Космоса»."""
    im, d = canvas(44, 60)
    d.rectangle([2, 0, 41, 54], fill=(40, 52, 96, 255), outline=OUT)
    for p in ((6, 6), (35, 10), (9, 40), (33, 44), (22, 3)):
        d.point(p, fill=WHITE)
    d.ellipse([9, 6, 34, 30], fill=(220, 220, 228, 255), outline=OUT)  # шлем
    d.ellipse([15, 11, 28, 25], fill=(18, 14, 12, 255))                 # дырка для лица
    d.rounded_rectangle([10, 28, 33, 43], radius=3, fill=(220, 220, 228, 255), outline=OUT)
    d.rectangle([17, 32, 26, 37], fill=(80, 140, 230, 255), outline=OUT)
    d.rectangle([6, 54, 10, 59], fill=WOOD_D, outline=OUT)
    d.rectangle([33, 54, 37, 59], fill=WOOD_D, outline=OUT)
    draw_text_centered(im, 22, 47, "КОСМОС", WHITE)
    return im


# ---------------------------------------------------------------- «Цирк»

def circus_pedestal():
    """Цирковая тумба с мячом 32×40."""
    im, d = canvas(32, 40)
    d.ellipse([6, 0, 25, 17], fill=(80, 140, 230, 255), outline=OUT)
    d.arc([6, 0, 25, 17], 180, 260, fill=WHITE)
    d.pieslice([6, 0, 25, 17], 300, 360, fill=RED)
    d.rectangle([4, 20, 27, 37], fill=RED, outline=OUT)
    d.ellipse([3, 15, 28, 23], fill=YELLOW, outline=OUT)
    for x in range(7, 26, 6):
        d.polygon([(x, 24), (x + 3, 30), (x, 36)], fill=YELLOW)
    d.ellipse([3, 34, 28, 39], fill=RED_D, outline=OUT)
    return im


def circus_sign():
    """Вывеска «ЦИРК» на столбике 48×46."""
    im, d = canvas(48, 46)
    d.rectangle([22, 18, 25, 45], fill=WOOD_D, outline=OUT)
    d.rounded_rectangle([1, 1, 46, 19], radius=3, fill=RED, outline=OUT)
    for x in range(4, 45, 4):
        d.point([(x, 3), (x, 17)], fill=YELLOW)
    draw_text_centered(im, 24, 7, "ЦИРК", WHITE)
    return im


# ---------------------------------------------------------------- «Ретро»

def jukebox():
    """Музыкальный автомат 32×48."""
    im, d = canvas(32, 48)
    d.rounded_rectangle([2, 2, 29, 47], radius=10, fill=(170, 40, 70, 255), outline=OUT)
    d.rounded_rectangle([6, 6, 25, 26], radius=8, fill=(255, 220, 140, 255), outline=OUT)
    for i, c in enumerate((RED, YELLOW, (80, 200, 120, 255), (80, 140, 230, 255))):
        d.line([(8, 12 + i * 3), (23, 12 + i * 3)], fill=c)
    d.rectangle([8, 30, 23, 36], fill=(40, 30, 40, 255), outline=OUT)
    d.rectangle([8, 39, 23, 44], fill=(214, 170, 70, 255), outline=OUT)
    return im


def vinyl_standee():
    """Огромная пластинка-стенд «Ретро» 44×54."""
    im, d = canvas(44, 54)
    d.rectangle([20, 40, 23, 53], fill=WOOD_D, outline=OUT)
    d.ellipse([1, 1, 42, 42], fill=(28, 26, 30, 255), outline=OUT)
    for r in (17, 13):
        d.ellipse([21 - r, 21 - r, 22 + r, 22 + r], outline=(60, 58, 66, 255))
    d.ellipse([14, 14, 29, 29], fill=ACCENT, outline=OUT)
    d.ellipse([20, 20, 23, 23], fill=(28, 26, 30, 255))
    d.arc([5, 5, 38, 38], 200, 240, fill=(120, 118, 130, 255))
    return im


def disco_ball():
    """Диско-шар на стойке 26×56."""
    im, d = canvas(26, 56)
    d.rectangle([11, 22, 14, 52], fill=(150, 150, 160, 255), outline=OUT)
    d.ellipse([5, 50, 20, 55], fill=(110, 110, 120, 255), outline=OUT)
    d.ellipse([2, 2, 23, 23], fill=(190, 196, 210, 255), outline=OUT)
    for y in range(5, 22, 4):
        d.line([(3, y), (22, y)], fill=(140, 146, 160, 255))
    for x in range(6, 22, 4):
        d.line([(x, 3), (x, 22)], fill=(140, 146, 160, 255))
    d.point([(8, 7), (9, 7), (16, 12), (8, 16)], fill=WHITE)
    return im


# ---------------------------------------------------------------- закулисье

def backstage_floor():
    """Доски пола за сценой 32×32, бесшовно."""
    im, d = canvas(32, 32)
    base = (92, 66, 52, 255)
    d.rectangle([0, 0, 31, 31], fill=base)
    for y in (0, 8, 16, 24):
        d.line([(0, y), (31, y)], fill=(70, 50, 40, 255))
        x = (y * 3) % 32
        d.line([(x, y), (x, y + 7)], fill=(70, 50, 40, 255))
        d.point(((x + 13) % 32, y + 4), fill=(110, 82, 64, 255))
    return im


def stage_back():
    """Задник музыкальной сцены изнутри 160×64: фанера, распорки, тросы."""
    im, d = canvas(160, 64)
    ply = (170, 140, 100, 255)
    d.rectangle([0, 0, 159, 63], fill=ply, outline=OUT)
    for x in range(0, 160, 40):
        d.line([(x, 0), (x, 63)], fill=(140, 112, 78, 255))
    for x0 in (10, 90):
        d.line([(x0, 63), (x0 + 30, 8)], fill=WOOD_D, width=3)
        d.line([(x0 + 60, 63), (x0 + 30, 8)], fill=WOOD_D, width=3)
    d.line([(0, 4), (159, 4)], fill=(60, 60, 70, 255), width=2)
    for x in (24, 136):  # мешки с песком
        d.rounded_rectangle([x - 6, 50, x + 6, 62], radius=3, fill=(190, 170, 130, 255), outline=OUT)
    return im


def crates_prizes():
    """Коробки Мойто «ПРИЗЫ» 48×40 — ложный след: прятал он именно их."""
    im, d = canvas(48, 40)
    for x0, y0 in ((0, 14), (22, 14), (10, 0)):
        d.rectangle([x0, y0, x0 + 24, y0 + 24], fill=CARD, outline=OUT)
        d.line([(x0 + 1, y0 + 3), (x0 + 23, y0 + 3)], fill=CARD_L)
        d.line([(x0 + 12, y0), (x0 + 12, y0 + 6)], fill=(214, 200, 160, 255), width=2)
    draw_text_centered(im, 23, 6, "ПРИЗЫ", RED)
    d.polygon(_star(11, 30, 4, 2), fill=YELLOW, outline=OUT)
    d.rectangle([30, 26, 39, 33], fill=(80, 140, 230, 255), outline=OUT)
    d.line([(34, 26), (34, 33)], fill=YELLOW)
    return im


def cable_coil():
    """Бухта кабеля 28×16."""
    im, d = canvas(28, 16)
    for r in range(3):
        d.ellipse([r * 2, r, 27 - r * 2, 15 - r], outline=(40, 40, 48, 255))
    d.line([(26, 8), (27, 3)], fill=(40, 40, 48, 255))
    return im


def spotlight():
    """Прожектор на треноге 24×44."""
    im, d = canvas(24, 44)
    d.line([(12, 18), (3, 43)], fill=(60, 60, 70, 255), width=2)
    d.line([(12, 18), (21, 43)], fill=(60, 60, 70, 255), width=2)
    d.line([(12, 18), (12, 43)], fill=(60, 60, 70, 255), width=2)
    d.rectangle([4, 4, 19, 18], fill=(50, 50, 58, 255), outline=OUT)
    d.ellipse([7, 6, 16, 15], fill=(255, 236, 170, 255), outline=OUT)
    return im


def backstage_door():
    """Проход за кулисы 34×50: раздвинутый занавес, за ним темно."""
    im, d = canvas(34, 50)
    d.rectangle([2, 2, 31, 49], fill=(20, 16, 24, 255), outline=OUT)
    d.polygon([(2, 2), (14, 2), (9, 49), (2, 49)], fill=RED_D, outline=OUT)
    d.polygon([(31, 2), (19, 2), (24, 49), (31, 49)], fill=RED_D, outline=OUT)
    for x in (5, 9, 25, 28):
        d.line([(x, 4), (x, 47)], fill=RED)
    d.rectangle([0, 0, 33, 4], fill=WOOD, outline=OUT)
    return im


FESTIVAL_PROPS = {
    "backstage_door": backstage_door,
    "gate_hoton": gate_hoton, "bunting": bunting, "tea_stall": tea_stall, "bench": bench,
    "balloons": balloons, "guest_rope": guest_rope, "lamp": lamp,
    "planet": planet, "star_sign": star_sign, "astronaut_board": astronaut_board,
    "circus_pedestal": circus_pedestal, "circus_sign": circus_sign,
    "jukebox": jukebox, "vinyl_standee": vinyl_standee, "disco_ball": disco_ball,
    "stage_back": stage_back, "crates_prizes": crates_prizes, "cable_coil": cable_coil,
    "spotlight": spotlight,
}
