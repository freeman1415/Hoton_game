"""Мини-игра Кати «Собери образ»: манекен и 12 вещей слоями, 64×64 (в игре ×2).

Все слои — на одном холсте с манекеном, накладываются друг на друга:
манекен → костюм → аксессуар → голова. Темы: retro / circus / space / detective
(«детектив» — ловушка, его в заказах нет). Стиль как у спрайтов дизайнера:
чёрная обводка 1 px, плоская заливка, цвета брендбука.
"""
from palette import *
from characters import BLACK, B_BLUE, B_BROWN, B_GREEN, B_ORANGE, B_RED, B_SALMON, outline

WOOD_M = (226, 196, 150, 255)       # светлое дерево манекена
WOOD_M_D = (190, 156, 110, 255)
YELLOW_B = (246, 206, 72, 255)
PINK_B = (232, 110, 170, 255)
TEAL = (70, 170, 170, 255)
TRENCH = (196, 168, 120, 255)
TRENCH_D = (160, 132, 90, 255)


def blank():
    return canvas(64, 64)


# ------------------------------------------------------------------ манекен

def mannequin():
    im, d = blank()
    d.rectangle([30, 52, 33, 60], fill=WOOD_M_D, outline=BLACK)          # стойка
    d.ellipse([20, 58, 43, 63], fill=B_BROWN, outline=BLACK)             # подставка
    d.rounded_rectangle([14, 37, 20, 49], radius=2, fill=WOOD_M, outline=BLACK)
    d.rounded_rectangle([43, 37, 49, 49], radius=2, fill=WOOD_M, outline=BLACK)
    d.ellipse([13, 46, 20, 52], fill=WOOD_M, outline=BLACK)
    d.ellipse([43, 46, 50, 52], fill=WOOD_M, outline=BLACK)
    d.polygon([(21, 35), (42, 35), (45, 53), (18, 53)], fill=WOOD_M, outline=BLACK)
    d.line([(31, 37), (31, 51)], fill=WOOD_M_D)
    d.ellipse([17, 6, 46, 35], fill=WOOD_M, outline=BLACK)
    # нарисованное «лицо» манекена: точки-глаза и улыбка, как у куклы
    d.ellipse([24, 19, 28, 24], fill=BLACK)
    d.ellipse([35, 19, 39, 24], fill=BLACK)
    d.point([(25, 20), (36, 20)], fill=WHITE)
    d.line([(29, 29), (31, 30), (32, 30), (34, 29)], fill=BLACK)
    d.point([(21, 27), (22, 27), (41, 27), (42, 27)], fill=BLUSH)
    return outline(im)


# ------------------------------------------------------------------ голова

def head_retro():
    """Кудрявый парик дискотеки 80-х."""
    im, d = blank()
    for cx, cy, r in ((20, 14, 6), (27, 8, 6), (36, 8, 6), (43, 14, 6), (16, 22, 5), (47, 22, 5),
                      (31, 5, 5), (24, 4, 4), (39, 4, 4)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=B_ORANGE, outline=BLACK)
    for cx, cy in ((22, 10), (33, 6), (42, 11), (18, 20)):
        d.arc([cx - 3, cy - 3, cx + 3, cy + 3], 200, 340, fill=(250, 190, 110, 255))
    d.rectangle([20, 12, 43, 15], fill=PINK_B, outline=BLACK)            # повязка
    return outline(im)


def head_circus():
    """Клоунский колпак с помпоном."""
    im, d = blank()
    d.polygon([(22, 15), (32, -1), (41, 15)], fill=B_RED, outline=BLACK)
    d.line([(27, 9), (36, 9)], fill=YELLOW_B, width=2)
    d.point([(32, 4), (29, 12), (35, 12)], fill=YELLOW_B)
    d.ellipse([28, -2, 36, 5], fill=YELLOW_B, outline=BLACK)
    d.rounded_rectangle([19, 13, 44, 18], radius=2, fill=YELLOW_B, outline=BLACK)
    return outline(im)


def head_space():
    """Картонный шлем, как на общем арте «Космоса»."""
    im, d = blank()
    d.polygon(polygon_points(31.5, 20.5, 17, 8, rot=pi / 8), fill=CARD, outline=BLACK)
    d.ellipse([21, 11, 42, 32], fill=(0, 0, 0, 0), outline=BLACK)
    # вырез под лицо: стираем середину, чтобы было видно «лицо» манекена
    px = im.load()
    for y in range(12, 32):
        for x in range(22, 42):
            if (x - 31.5) ** 2 / 100 + (y - 21.5) ** 2 / 100 < 1:
                px[x, y] = (0, 0, 0, 0)
    d.ellipse([21, 11, 42, 32], outline=CARD_D)
    d.line([(24, 5), (21, 0)], fill=BLACK)
    d.line([(39, 5), (42, 0)], fill=BLACK)
    d.ellipse([19, -1, 23, 3], fill=B_RED, outline=BLACK)
    d.ellipse([40, -1, 44, 3], fill=B_RED, outline=BLACK)
    d.rectangle([12, 18, 15, 24], fill=CARD_D, outline=BLACK)            # «наушники»
    d.rectangle([48, 18, 51, 24], fill=CARD_D, outline=BLACK)
    return outline(im)


def head_detective():
    """Охотничья шапка детектива — ловушка."""
    im, d = blank()
    color = (150, 104, 66, 255)
    d.chord([16, 3, 47, 24], 180, 360, fill=color, outline=BLACK)
    for x in range(20, 45, 5):
        d.line([(x, 6), (x, 13)], fill=(118, 78, 50, 255))
    d.line([(18, 10), (45, 10)], fill=(118, 78, 50, 255))
    d.rectangle([14, 13, 18, 22], fill=color, outline=BLACK)
    d.rectangle([45, 13, 49, 22], fill=color, outline=BLACK)
    d.polygon([(26, 13), (37, 13), (34, 17), (29, 17)], fill=color, outline=BLACK)  # козырёк
    return outline(im)


# ------------------------------------------------------------------ костюм

def _jacket(d, body, sleeve, collar=None):
    d.rounded_rectangle([13, 36, 20, 48], radius=2, fill=sleeve, outline=BLACK)
    d.rounded_rectangle([43, 36, 50, 48], radius=2, fill=sleeve, outline=BLACK)
    d.polygon([(20, 34), (43, 34), (46, 54), (17, 54)], fill=body, outline=BLACK)
    if collar:
        d.polygon([(22, 34), (31, 34), (27, 41)], fill=collar, outline=BLACK)
        d.polygon([(41, 34), (32, 34), (36, 41)], fill=collar, outline=BLACK)


def costume_retro():
    """Яркая куртка с большим воротником и полосами."""
    im, d = blank()
    _jacket(d, PINK_B, PINK_B, collar=B_BLUE)
    for y in (44, 48):
        d.line([(18, y), (45, y)], fill=YELLOW_B, width=2)
    d.line([(31, 41), (31, 53)], fill=BLACK)
    return outline(im)


def costume_circus():
    """Костюм в горошек с жабо."""
    im, d = blank()
    _jacket(d, YELLOW_B, YELLOW_B)
    for x, y in ((22, 42), (28, 47), (35, 42), (40, 48), (25, 51), (37, 52), (16, 41), (46, 43)):
        d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=B_RED)
    for x in range(20, 44, 4):                                           # жабо
        d.ellipse([x - 1, 32, x + 4, 38], fill=WHITE, outline=BLACK)
    return outline(im)


def costume_space():
    """Скафандр из картона: скотч, кнопки, шланг."""
    im, d = blank()
    _jacket(d, CARD, CARD_L)
    d.rectangle([24, 39, 39, 48], fill=CARD_L, outline=BLACK)            # панель
    for x, c in ((27, B_RED), (31, B_GREEN), (35, B_BLUE)):
        d.ellipse([x - 1, 42, x + 2, 45], fill=c, outline=BLACK)
    d.rectangle([17, 50, 46, 52], fill=(214, 200, 160, 255), outline=BLACK)  # скотч
    d.line([(14, 40), (19, 40)], fill=(214, 200, 160, 255))
    d.line([(44, 40), (49, 40)], fill=(214, 200, 160, 255))
    return outline(im)


def costume_detective():
    """Бежевый плащ детектива — ловушка."""
    im, d = blank()
    _jacket(d, TRENCH, TRENCH, collar=TRENCH_D)
    d.rectangle([18, 45, 45, 47], fill=TRENCH_D, outline=BLACK)          # пояс
    d.rectangle([29, 44, 33, 48], fill=YELLOW_B, outline=BLACK)          # пряжка
    for y in (39, 51):
        d.point([(27, y), (36, y)], fill=BLACK)
    return outline(im)


# ------------------------------------------------------------------ аксессуар

def accessory_retro():
    """Кассетный плеер с наушниками."""
    im, d = blank()
    d.rounded_rectangle([46, 42, 57, 51], radius=1, fill=(70, 70, 82, 255), outline=BLACK)
    d.rectangle([48, 44, 55, 48], fill=(150, 150, 160, 255), outline=BLACK)
    d.ellipse([49, 45, 51, 47], fill=BLACK)
    d.ellipse([52, 45, 54, 47], fill=BLACK)
    d.line([(51, 42), (47, 31), (45, 25)], fill=BLACK)                   # провод
    d.ellipse([12, 20, 18, 28], fill=B_ORANGE, outline=BLACK)            # наушники
    d.ellipse([45, 20, 51, 28], fill=B_ORANGE, outline=BLACK)
    return outline(im)


def accessory_circus():
    """Красный нос клоуна."""
    im, d = blank()
    d.ellipse([28, 23, 35, 30], fill=(230, 40, 50, 255), outline=BLACK)
    d.point((30, 25), fill=WHITE)
    return outline(im)


def accessory_space():
    """Ракета-рюкзак: видна из-за плеча, с пламенем."""
    im, d = blank()
    d.rounded_rectangle([50, 30, 58, 52], radius=3, fill=B_BLUE, outline=BLACK)
    d.polygon([(50, 31), (54, 24), (58, 31)], fill=B_RED, outline=BLACK)
    d.ellipse([52, 36, 56, 40], fill=WHITE, outline=BLACK)
    d.polygon([(51, 53), (54, 61), (57, 53)], fill=B_ORANGE, outline=BLACK)
    d.polygon([(53, 53), (54, 57), (55, 53)], fill=YELLOW_B)
    d.line([(43, 35), (50, 34)], fill=BLACK, width=2)                    # лямка
    return outline(im)


def accessory_detective():
    """Лупа — ловушка."""
    im, d = blank()
    d.line([(48, 49), (53, 43)], fill=B_BROWN, width=3)
    d.ellipse([50, 31, 61, 42], fill=(200, 236, 248, 255), outline=BLACK)
    d.ellipse([51, 32, 60, 41], outline=(150, 150, 160, 255))
    d.point([(53, 34), (54, 34)], fill=WHITE)
    return outline(im)


COSPLAY = {
    "mannequin": mannequin,
    "head_retro": head_retro, "head_circus": head_circus, "head_space": head_space,
    "head_detective": head_detective,
    "costume_retro": costume_retro, "costume_circus": costume_circus, "costume_space": costume_space,
    "costume_detective": costume_detective,
    "accessory_retro": accessory_retro, "accessory_circus": accessory_circus,
    "accessory_space": accessory_space, "accessory_detective": accessory_detective,
}
