"""Игрок и гости фестиваля, 64×64 — под спрайты маскотов дизайнера (assets/new_assets/).

Стиль как у дизайнера: чёрная обводка 1 px, голова почти в половину роста,
крупные глаза с бликом, плоская заливка. Ноги — на нижнем ряду (y = 63).
Маскотов здесь больше нет: это спрайты дизайнера, их не генерируем.
"""
from palette import *

W = 64
BLACK = (0, 0, 0, 255)
EYE_W = (255, 255, 255, 255)

# Фирменные цвета брендбука (scripts/brand.gd)
B_ORANGE = (228, 136, 36, 255)
B_SALMON = (212, 132, 100, 255)
B_BROWN = (96, 64, 48, 255)
B_BLUE = (120, 176, 200, 255)
B_RED = (204, 92, 96, 255)
B_GREEN = (116, 176, 104, 255)


def outline(im):
    return outline_pass(im, BLACK)


def eyes_front(d, y, left=23, right=35):
    """Крупные глаза с бликом, как у маскотов дизайнера."""
    for x in (left, right):
        d.ellipse([x, y, x + 5, y + 7], fill=BLACK)
        d.rectangle([x + 1, y + 1, x + 2, y + 2], fill=EYE_W)


def kid(facing, coat, hat, hair, skin, scarf, ears=False, magnifier=False, pants=PANTS):
    """Ребёнок-гость 64×64. facing: down / up / side (смотрит вправо).
    hat: None, ("beanie", цвет) или ("detective", цвет)."""
    im, d = canvas(W, 64)
    # ноги и ботинки
    for x0 in (24, 34):
        d.rectangle([x0, 51, x0 + 5, 58], fill=pants, outline=BLACK)
        d.rounded_rectangle([x0 - 1, 57, x0 + 6, 63], radius=2, fill=SHOE, outline=BLACK)
    # руки за телом
    d.rounded_rectangle([14, 37, 20, 49], radius=2, fill=coat, outline=BLACK)
    d.rounded_rectangle([43, 37, 49, 49], radius=2, fill=coat, outline=BLACK)
    d.ellipse([13, 46, 20, 52], fill=skin, outline=BLACK)
    d.ellipse([43, 46, 50, 52], fill=skin, outline=BLACK)
    # куртка
    d.polygon([(21, 35), (42, 35), (45, 53), (18, 53)], fill=coat, outline=BLACK)
    if facing != "up":
        d.line([(31, 39), (31, 52)], fill=BLACK)
        for y in (42, 47):
            d.point([(29, y), (34, y)], fill=BLACK)
    # голова
    d.ellipse([17, 6, 46, 35], fill=hair if facing == "up" else skin, outline=BLACK)
    if ears:  # косплей: кошачьи ушки
        for pts in ([(18, 14), (19, 1), (28, 8)], [(45, 14), (44, 1), (35, 8)]):
            d.polygon(pts, fill=hair, outline=BLACK)
        d.polygon([(21, 10), (21, 5), (25, 8)], fill=PINK)
        d.polygon([(42, 10), (42, 5), (38, 8)], fill=PINK)
    if facing == "down":
        d.chord([17, 6, 46, 30], 180, 360, fill=hair, outline=BLACK)
        d.polygon([(19, 18), (24, 14), (21, 25)], fill=hair)
        d.polygon([(44, 18), (39, 14), (42, 25)], fill=hair)
        eyes_front(d, 19)
        d.point([(21, 29), (22, 29), (41, 29), (42, 29)], fill=BLUSH)
        d.line([(30, 30), (31, 31), (32, 31), (33, 30)], fill=BLACK)
    elif facing == "side":
        d.chord([17, 6, 46, 30], 180, 360, fill=hair, outline=BLACK)
        d.polygon([(17, 18), (27, 14), (25, 30), (18, 27)], fill=hair)
        d.ellipse([37, 19, 42, 26], fill=BLACK)
        d.rectangle([39, 20, 40, 21], fill=EYE_W)
        d.point([(43, 29), (44, 29)], fill=BLUSH)
        d.line([(41, 31), (43, 30)], fill=BLACK)
    # шапка
    if hat:
        kind, color = hat
        if kind == "beanie":
            d.chord([17, 4, 46, 24], 180, 360, fill=color, outline=BLACK)
            d.rectangle([17, 13, 46, 17], fill=color, outline=BLACK)
            d.ellipse([28, 0, 35, 6], fill=WHITE, outline=BLACK)
        else:  # охотничья шапка детектива (без нуара)
            d.chord([16, 3, 47, 24], 180, 360, fill=color, outline=BLACK)
            for x in range(20, 45, 5):
                d.line([(x, 6), (x, 13)], fill=(118, 78, 50, 255))
            d.line([(18, 10), (45, 10)], fill=(118, 78, 50, 255))
            if facing == "side":
                d.polygon([(44, 12), (54, 15), (44, 17)], fill=color, outline=BLACK)
            else:
                d.rectangle([14, 13, 18, 22], fill=color, outline=BLACK)   # клапаны
                d.rectangle([45, 13, 49, 22], fill=color, outline=BLACK)
    # шарф
    d.rounded_rectangle([20, 32, 43, 37], radius=2, fill=scarf, outline=BLACK)
    if facing != "up":
        d.rectangle([35, 36, 39, 45], fill=scarf, outline=BLACK)
    # лупа в правой руке
    if magnifier and facing != "up":
        d.line([(48, 48), (52, 43)], fill=B_BROWN, width=2)
        d.ellipse([49, 33, 59, 43], fill=(200, 236, 248, 255), outline=BLACK)
        d.ellipse([50, 34, 58, 42], outline=(150, 150, 160, 255))
        d.point([(52, 36), (53, 36)], fill=WHITE)
    return outline(im)


def player(facing):
    """Гость-детектив: охотничья шапка, оранжевое пальто, красный шарф, лупа."""
    return kid(facing, coat=B_ORANGE, hat=("detective", (150, 104, 66, 255)), hair=(70, 44, 30, 255),
               skin=(244, 206, 172, 255), scarf=B_RED, magnifier=True)


## Гости фестиваля: (куртка, шапка, волосы, кожа, шарф, кошачьи ушки)
GUESTS = [
    (B_BLUE, ("beanie", B_RED), (60, 40, 30, 255), (244, 206, 172, 255), B_ORANGE, False),
    (B_ORANGE, ("beanie", (70, 70, 80, 255)), (30, 24, 22, 255), (214, 164, 120, 255), B_BLUE, False),
    (B_GREEN, None, (232, 186, 100, 255), (248, 214, 186, 255), B_RED, True),
    (B_SALMON, ("beanie", WHITE), (96, 58, 36, 255), (226, 186, 150, 255), B_GREEN, False),
    ((80, 70, 96, 255), None, (24, 22, 28, 255), (240, 200, 166, 255), B_SALMON, True),
    (B_RED, ("beanie", B_BLUE), (122, 72, 40, 255), (198, 146, 108, 255), WHITE, False),
]


def guest(i):
    coat, hat, hair, skin, scarf, ears = GUESTS[i]
    return kid("down", coat, hat, hair, skin, scarf, ears=ears)
