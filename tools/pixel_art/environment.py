"""Декорации хаба (вид 3/4, как в Undertale) и плитка площади.

Зоны — по сюжету docs/GAME.md: главная сцена, музыкальная сцена Лени
с картонной ракетой за ней (тайник!), арт-маркет Мани, дефиле Кати,
цирковой шатёр Мойто (отсылка к «Цирку»), лекторий Сулуса.
"""
import random

from palette import *

WOOD = (150, 100, 64, 255)
WOOD_D = (112, 72, 44, 255)
WOOD_L = (186, 134, 88, 255)
RED = (200, 50, 60, 255)
RED_D = (140, 30, 44, 255)
YELLOW = (246, 206, 72, 255)
GREEN_PINE = (52, 110, 80, 255)
GREEN_PINE_D = (34, 78, 60, 255)
SNOW = (240, 244, 250, 255)
STONE = (196, 186, 170, 255)
STONE_D = (176, 165, 150, 255)
STONE_L = (210, 202, 188, 255)


def ground_tile():
    """Плитка площади 32×32, бесшовная."""
    rnd = random.Random(7)
    im, d = canvas(32, 32)
    d.rectangle([0, 0, 31, 31], fill=STONE)
    for y0 in (0, 16):
        shift = 0 if y0 == 0 else 8
        d.line([(0, y0), (31, y0)], fill=STONE_D)
        for x in range(shift, 32 + shift, 16):
            d.line([(x % 32, y0), (x % 32, y0 + 15)], fill=STONE_D)
    for _ in range(18):
        d.point((rnd.randrange(32), rnd.randrange(32)), fill=STONE_L)
    return im


def main_stage():
    """Главная сцена 96×60: помост, красный занавес, гирлянда."""
    im, d = canvas(96, 60)
    d.rectangle([2, 4, 93, 44], fill=RED_D, outline=OUT)
    for x in range(6, 92, 8):
        d.line([(x, 8), (x, 43)], fill=RED)
    d.rectangle([2, 0, 93, 6], fill=WOOD, outline=OUT)
    for i, x in enumerate(range(8, 92, 8)):  # гирлянда
        d.point((x, 9 + (i % 2)), fill=YELLOW if i % 2 else (120, 190, 255, 255))
    d.rectangle([34, 14, 61, 34], fill=INK, outline=OUT)  # проём
    d.polygon([(47, 18), (49, 23), (54, 23), (50, 26), (52, 31), (47, 28), (43, 31), (45, 26),
               (41, 23), (46, 23)], fill=YELLOW)  # звезда
    d.rectangle([0, 42, 95, 52], fill=WOOD, outline=OUT)
    d.line([(1, 45), (94, 45)], fill=WOOD_L)
    for x in range(12, 95, 16):
        d.line([(x, 46), (x, 51)], fill=WOOD_D)
    d.rectangle([40, 52, 55, 58], fill=WOOD_D, outline=OUT)  # ступеньки
    d.line([(41, 55), (54, 55)], fill=WOOD)
    return im


def music_stage():
    """Музыкальная сцена Лени 72×52: помост, колонки, микрофон, ноты."""
    im, d = canvas(72, 52)
    d.rectangle([4, 2, 67, 34], fill=(40, 52, 96, 255), outline=OUT)
    for x, y in ((14, 10), (30, 6), (50, 12)):  # ноты на заднике
        d.ellipse([x, y + 6, x + 3, y + 8], fill=WHITE)
        d.line([(x + 3, y), (x + 3, y + 7)], fill=WHITE)
        d.line([(x + 3, y), (x + 6, y + 2)], fill=WHITE)
    d.rectangle([0, 32, 71, 44], fill=WOOD, outline=OUT)
    d.line([(1, 35), (70, 35)], fill=WOOD_L)
    for x in (4, 58):  # колонки
        d.rectangle([x, 16, x + 9, 33], fill=(48, 44, 48, 255), outline=OUT)
        d.ellipse([x + 2, 19, x + 7, 24], fill=(90, 86, 92, 255), outline=OUT)
        d.ellipse([x + 2, 26, x + 7, 31], fill=(90, 86, 92, 255), outline=OUT)
    d.line([(36, 18), (36, 33)], fill=OUT)  # микрофон
    d.ellipse([34, 15, 38, 19], fill=(150, 150, 160, 255), outline=OUT)
    d.line([(32, 33), (40, 33)], fill=OUT)
    d.rectangle([28, 44, 43, 50], fill=WOOD_D, outline=OUT)
    return im


def rocket():
    """Картонная ракета с фестиваля «Космос», 30×66. В ней спрятана Капсула."""
    im, d = canvas(30, 66)
    d.polygon([(7, 46), (1, 60), (8, 60)], fill=RED, outline=OUT)
    d.polygon([(22, 46), (28, 60), (21, 60)], fill=RED, outline=OUT)
    d.rectangle([7, 18, 22, 60], fill=CARD, outline=OUT)
    d.polygon([(7, 18), (14, 2), (15, 2), (22, 18)], fill=RED, outline=OUT)
    d.line([(9, 20), (9, 58)], fill=CARD_L)
    d.line([(20, 20), (20, 58)], fill=CARD_D)
    d.ellipse([10, 24, 19, 33], fill=SKY, outline=OUT)
    d.point((12, 26), fill=WHITE)
    d.rectangle([7, 40, 22, 43], fill=(214, 200, 160, 255), outline=OUT)  # скотч
    d.line([(11, 50), (18, 50)], fill=CARD_D)  # шов-«дверца»
    d.line([(11, 50), (11, 58)], fill=CARD_D)
    d.line([(18, 50), (18, 58)], fill=CARD_D)
    d.rectangle([10, 60, 19, 64], fill=(110, 110, 120, 255), outline=OUT)
    return im


def art_stall():
    """Палатка арт-маркета Мани 60×48: полосатый навес, картины, мольберт."""
    im, d = canvas(60, 48)
    d.line([(4, 10), (4, 44)], fill=WOOD_D, width=2)
    d.line([(44, 10), (44, 44)], fill=WOOD_D, width=2)
    d.rectangle([2, 26, 46, 44], fill=WOOD, outline=OUT)
    d.line([(3, 29), (45, 29)], fill=WOOD_L)
    for i, x in enumerate(range(0, 48, 6)):  # навес
        d.polygon([(x, 4), (x + 6, 4), (x + 6, 13), (x + 3, 15), (x, 13)],
                  fill=(236, 140, 160, 255) if i % 2 == 0 else WHITE, outline=OUT)
    d.rectangle([0, 0, 48, 4], fill=(236, 140, 160, 255), outline=OUT)
    for x, c in ((8, (90, 150, 230, 255)), (20, YELLOW), (32, (120, 190, 110, 255))):
        d.rectangle([x, 17, x + 8, 25], fill=WHITE, outline=OUT)
        d.rectangle([x + 2, 19, x + 6, 23], fill=c)
    # мольберт
    d.line([(52, 24), (48, 46)], fill=WOOD_D)
    d.line([(52, 24), (57, 46)], fill=WOOD_D)
    d.rectangle([47, 22, 58, 34], fill=WHITE, outline=OUT)
    d.ellipse([49, 25, 56, 31], fill=ACCENT)
    return im


def circus_tent():
    """Шатёр конкурсов Мойто 68×60: красно-жёлтые полосы, флажок."""
    im, d = canvas(68, 60)
    d.line([(34, 1), (34, 10)], fill=OUT)
    d.polygon([(35, 1), (42, 4), (35, 7)], fill=(80, 140, 230, 255), outline=OUT)
    stripes = 8
    for i in range(stripes):
        x0 = 4 + i * 60 // stripes
        x1 = 4 + (i + 1) * 60 // stripes
        d.polygon([(34, 10), (x0, 40), (x1, 40)], fill=RED if i % 2 == 0 else YELLOW)
    d.polygon([(34, 10), (4, 40), (64, 40)], outline=OUT)
    d.rectangle([8, 40, 60, 56], fill=YELLOW, outline=OUT)
    for x in range(8, 60, 8):
        d.rectangle([x, 41, x + 3, 55], fill=RED)
    d.polygon([(28, 56), (34, 42), (40, 56)], fill=INK, outline=OUT)  # вход
    for x in range(6, 64, 6):  # фестоны
        d.ellipse([x - 3, 38, x + 3, 44], fill=RED, outline=OUT)
    return im


def lecture():
    """Лекторий Сулуса 64×50: доска с формулой-загадкой и кафедра."""
    im, d = canvas(64, 50)
    d.line([(10, 30), (8, 48)], fill=WOOD_D, width=2)
    d.line([(44, 30), (46, 48)], fill=WOOD_D, width=2)
    d.rectangle([2, 2, 52, 32], fill=WOOD, outline=OUT)
    d.rectangle([5, 5, 49, 29], fill=(46, 82, 66, 255), outline=OUT)
    chalk = (226, 236, 226, 255)
    d.ellipse([9, 9, 17, 17], outline=chalk)  # лупа мелом
    d.line([(16, 16), (20, 20)], fill=chalk)
    d.line([(24, 11), (30, 11)], fill=chalk)
    d.line([(24, 15), (44, 15)], fill=chalk)
    d.line([(24, 19), (38, 19)], fill=chalk)
    d.line([(38, 8), (41, 8), (42, 9), (42, 10), (40, 12), (40, 13)], fill=chalk)  # «?»
    d.point((40, 15), fill=chalk)
    d.line([(8, 24), (40, 24)], fill=chalk)
    # кафедра
    d.polygon([(46, 30), (62, 30), (60, 48), (48, 48)], fill=WOOD_L, outline=OUT)
    d.rectangle([44, 27, 63, 31], fill=WOOD, outline=OUT)
    d.rectangle([52, 36, 56, 40], fill=CARD_L, outline=OUT)
    return im


def runway():
    """Дефиле Кати 64×48: вешалка с костюмами «Ретро», «Цирк», «Космос», зеркало."""
    im, d = canvas(64, 48)
    d.line([(4, 8), (4, 46)], fill=(150, 150, 160, 255), width=2)
    d.line([(40, 8), (40, 46)], fill=(150, 150, 160, 255), width=2)
    d.line([(3, 8), (41, 8)], fill=(110, 110, 120, 255), width=2)
    for x, c, pattern in ((8, (236, 90, 190, 255), None),       # ретро: яркая куртка
                          (19, YELLOW, RED),                     # цирк: в горошек
                          (30, (220, 220, 226, 255), None)):     # космос: скафандр
        d.line([(x + 4, 9), (x + 4, 12)], fill=OUT)
        d.polygon([(x, 13), (x + 8, 13), (x + 9, 30), (x - 1, 30)], fill=c, outline=OUT)
        if pattern:
            d.point([(x + 2, 17), (x + 6, 20), (x + 3, 24), (x + 6, 27)], fill=pattern)
    d.ellipse([28, 15, 32, 19], fill=SKY, outline=OUT)
    d.ellipse([4, 44, 40, 47], fill=(150, 150, 160, 255))
    # зеркало
    d.ellipse([46, 4, 62, 40], fill=WOOD, outline=OUT)
    d.ellipse([48, 6, 60, 38], fill=(186, 220, 236, 255), outline=OUT)
    d.line([(51, 12), (55, 8)], fill=WHITE)
    d.rectangle([50, 40, 58, 46], fill=WOOD_D, outline=OUT)
    return im


def gate():
    """Вход на фестиваль 80×60: арка с флажками в цветах маскотов."""
    im, d = canvas(80, 60)
    d.rectangle([4, 10, 11, 58], fill=WOOD, outline=OUT)
    d.rectangle([68, 10, 75, 58], fill=WOOD, outline=OUT)
    d.rectangle([0, 2, 79, 14], fill=ACCENT, outline=OUT)
    d.line([(1, 5), (78, 5)], fill=(250, 196, 140, 255))
    colors = [(236, 140, 160, 255), (80, 110, 200, 255), (64, 170, 76, 255), (224, 72, 44, 255),
              (206, 230, 242, 255)]
    for i, x in enumerate(range(14, 66, 6)):
        d.polygon([(x, 15), (x + 5, 15), (x + 2, 21)], fill=colors[i % len(colors)], outline=OUT)
    return im


def pine():
    """Ёлка со снегом 26×44 — ноябрь в Якутске."""
    im, d = canvas(26, 44)
    d.rectangle([11, 36, 14, 43], fill=WOOD_D, outline=OUT)
    for top, half, bottom in ((0, 6, 14), (7, 9, 24), (15, 12, 37)):
        d.polygon([(12, top), (12 - half, bottom), (13 + half, bottom), (13, top)],
                  fill=GREEN_PINE, outline=OUT)
        d.line([(12 - half + 2, bottom - 1), (13 + half - 2, bottom - 1)], fill=GREEN_PINE_D)
        d.line([(12 - half // 2, bottom - 3), (12, bottom - 5)], fill=SNOW)
    d.point([(12, 1), (13, 1)], fill=SNOW)
    return outline_pass(im)


PROPS = {
    "main_stage": main_stage, "music_stage": music_stage, "rocket": rocket,
    "art_stall": art_stall, "circus_tent": circus_tent, "lecture": lecture,
    "runway": runway, "gate": gate, "pine": pine,
}
