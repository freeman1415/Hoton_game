"""Маскоты и игрок, вид спереди. Маскоты 32×48 (Сулус выше — 32×54), игрок 24×40.

Референсы: assets/all_mascots.jpg, assets/mascot_*_mono.png, картинки с hotonfest.ru.
Все в «космических» костюмах из картона, как на общем арте организаторов.
"""
from palette import *

YELLOW_SC = (246, 206, 72, 255)

W = 32


def legs(d, top, bottom, skin, sock=WHITE, shoe=SHOE, gap=1):
    """Две ноги и ботинки. top..bottom — ноги, ботинки под ними."""
    lx0, rx0 = 16 - gap - 4, 16 + gap
    for x0 in (lx0, rx0):
        d.rectangle([x0, top, x0 + 3, bottom], fill=skin, outline=OUT)
        if sock:
            d.rectangle([x0, bottom - 2, x0 + 3, bottom], fill=sock, outline=OUT)
    d.ellipse([lx0 - 2, bottom, lx0 + 3, bottom + 4], fill=shoe, outline=OUT)
    d.ellipse([rx0, bottom, rx0 + 5, bottom + 4], fill=shoe, outline=OUT)


def arms(d, y0, y1, sleeve, hand=WHITE, x_in=10):
    x_out = W - 1 - x_in
    d.rectangle([x_in - 3, y0, x_in, y1], fill=sleeve, outline=OUT)
    d.rectangle([x_out, y0, x_out + 3, y1], fill=sleeve, outline=OUT)
    d.ellipse([x_in - 4, y1 - 1, x_in - 1, y1 + 2], fill=hand, outline=OUT)
    d.ellipse([x_out + 1, y1 - 1, x_out + 4, y1 + 2], fill=hand, outline=OUT)


def eyes(d, y, left=12, right=18, h=3, highlight=True):
    for x in (left, right):
        d.rectangle([x, y, x + 1, y + h - 1], fill=EYE)
        if highlight:
            d.point((x + 1, y), fill=WHITE)


def manya():
    """Маня, коровка: восьмигранный картонный шлем с антеннами, оранжевая
    рубашка, коричневый фартук художника, колокольчик."""
    im, d = canvas(W, 48)
    # хвост с кисточкой
    d.line([(20, 36), (24, 38), (26, 35)], fill=OUT)
    d.rectangle([25, 33, 27, 34], fill=PANTS)
    legs(d, 35, 41, WHITE, sock=WHITE)
    for x in (12, 18):  # пятна на коленях
        d.rectangle([x, 36, x + 1, 37], fill=(150, 95, 70, 255))
    arms(d, 27, 32, ACCENT)
    d.rounded_rectangle([10, 25, 21, 36], radius=2, fill=ACCENT, outline=OUT)
    d.rectangle([12, 28, 19, 36], fill=(122, 74, 42, 255))
    d.line([(13, 32), (18, 32)], fill=(96, 58, 34, 255))
    d.rectangle([15, 25, 16, 27], fill=(242, 194, 48, 255), outline=OUT)
    # антенны
    for x0, x1 in ((11, 9), (20, 22)):
        d.line([(x0, 5), (x1, 1)], fill=CARD_D)
        d.ellipse([x1 - 1, 0, x1 + 1, 2], fill=CARD, outline=OUT)
    # уши-клапаны шлема
    ear = [(1, 12), (8, 10), (9, 16), (2, 15)]
    d.polygon(ear, fill=CARD, outline=OUT)
    d.polygon(mirror_x(ear, W), fill=CARD, outline=OUT)
    d.polygon(polygon_points(15.5, 14, 11.5, 8, rot=pi / 8), fill=CARD, outline=OUT)
    d.ellipse([9, 7, 22, 21], fill=WHITE, outline=CARD_D)
    d.ellipse([13, 7, 18, 10], fill=(150, 95, 70, 255))  # рыжий чубчик
    eyes(d, 12, 12, 18)
    d.ellipse([11, 15, 20, 20], fill=PINK, outline=OUT)
    d.point([(13, 17), (18, 17)], fill=PINK_D)
    d.point([(10, 14), (21, 14)], fill=BLUSH)
    return outline_pass(im)


def lenya():
    """Леня, олень: квадратная рамка-шлем, закрытые мечтательные глаза,
    тёмно-синяя толстовка, широкие коричневые штаны."""
    im, d = canvas(W, 48)
    brown = (122, 80, 56, 255)
    navy = (38, 52, 110, 255)
    legs(d, 34, 41, PANTS, sock=None, gap=2)
    d.rectangle([11, 34, 20, 38], fill=PANTS, outline=OUT)
    arms(d, 26, 32, navy, hand=brown)
    d.rounded_rectangle([10, 24, 21, 35], radius=2, fill=navy, outline=OUT)
    # белая эмблема на толстовке
    d.line([(15, 27), (15, 32)], fill=WHITE)
    d.line([(13, 29), (17, 29)], fill=WHITE)
    d.point([(14, 31), (16, 31)], fill=WHITE)
    # уши оленя торчат из рамки
    ear = [(1, 11), (7, 9), (8, 14), (3, 14)]
    d.polygon(ear, fill=brown, outline=OUT)
    d.polygon(mirror_x(ear, W), fill=brown, outline=OUT)
    # рамка
    d.rectangle([5, 2, 26, 23], fill=WHITE_SH, outline=OUT)
    d.rectangle([7, 4, 24, 21], fill=SKY, outline=CARD_D)
    # голубые «рожки» на рамке
    d.rectangle([10, 3, 11, 5], fill=(80, 140, 230, 255))
    d.rectangle([20, 3, 21, 5], fill=(80, 140, 230, 255))
    # голова
    d.ellipse([8, 6, 23, 21], fill=brown, outline=OUT)
    d.polygon([(13, 6), (16, 9), (19, 6)], fill=WHITE)  # белая чёлка
    d.ellipse([10, 14, 21, 21], fill=WHITE, outline=OUT)  # светлая морда
    d.line([(11, 12), (13, 13)], fill=EYE)
    d.line([(18, 13), (20, 12)], fill=EYE)
    d.line([(14, 18), (15, 19), (16, 18), (17, 19)], fill=OUT)
    return outline_pass(im)


def katya():
    """Катя, лошадка: серый космический шлем с ушками, тёмная коса,
    зелёная куртка с трёхцветной полосой, подмигивает."""
    im, d = canvas(W, 48)
    skin = (196, 132, 86, 255)
    hair = (78, 46, 34, 255)
    green = (64, 170, 76, 255)
    grey = (184, 184, 194, 255)
    # хвост
    d.polygon([(19, 33), (26, 36), (27, 42), (22, 39)], fill=hair, outline=OUT)
    legs(d, 36, 41, skin)
    d.rectangle([11, 33, 20, 37], fill=WHITE, outline=OUT)  # белые шорты
    arms(d, 26, 31, green)
    d.rounded_rectangle([10, 24, 21, 34], radius=2, fill=green, outline=OUT)
    # полоса: белая, оранжевая, синяя
    d.line([(10, 27), (15, 30), (21, 27)], fill=WHITE)
    d.line([(10, 28), (15, 31), (21, 28)], fill=(232, 110, 50, 255))
    d.line([(10, 29), (15, 32), (21, 29)], fill=(60, 120, 220, 255))
    # коса
    d.line([(9, 18), (8, 24), (9, 28)], fill=hair, width=2)
    # шлем с ушками
    for ear in ([(7, 6), (8, 0), (12, 4)], [(24, 6), (23, 0), (19, 4)]):
        d.polygon(ear, fill=grey, outline=OUT)
    d.ellipse([4, 2, 27, 24], fill=grey, outline=OUT)
    for p in polygon_points(15.5, 13, 10.5, 12):
        d.point(p, fill=(130, 130, 140, 255))  # заклёпки
    d.ellipse([2, 11, 5, 16], fill=grey, outline=OUT)
    d.ellipse([26, 11, 29, 16], fill=grey, outline=OUT)
    d.ellipse([8, 6, 23, 21], fill=skin, outline=OUT)
    d.pieslice([8, 5, 23, 20], 180, 360, fill=hair)  # чёлка
    d.polygon([(8, 12), (11, 10), (10, 18)], fill=hair)
    d.ellipse([12, 15, 18, 20], fill=WHITE, outline=OUT)  # светлая морда
    d.rectangle([12, 12, 13, 14], fill=EYE)
    d.point((13, 12), fill=WHITE)
    d.line([(18, 13), (20, 13)], fill=EYE)  # подмигивает
    d.point([(11, 15), (20, 15)], fill=BLUSH)
    return outline_pass(im)


def moyto():
    """Мойто, собачка: голова в картонной коробке с клапанами,
    красная футболка с белыми ромбами, шорты, хвост-завиток."""
    im, d = canvas(W, 48)
    fur = (196, 206, 232, 255)
    red = (224, 72, 44, 255)
    d.line([(20, 35), (25, 34), (26, 31), (24, 30)], fill=WHITE, width=2)  # хвост
    legs(d, 36, 41, WHITE)
    d.rectangle([11, 33, 20, 37], fill=(58, 42, 42, 255), outline=OUT)
    arms(d, 25, 30, red, hand=WHITE, x_in=9)
    d.rectangle([9, 24, 22, 34], fill=red, outline=OUT)
    for x, y in ((15, 26), (13, 28), (17, 28), (15, 30)):
        d.rectangle([x, y, x + 1, y + 1], fill=WHITE)
    # коробка
    d.polygon([(4, 3), (2, 0), (8, 1), (9, 3)], fill=CARD_L, outline=OUT)
    d.polygon([(27, 3), (29, 0), (23, 1), (22, 3)], fill=CARD_L, outline=OUT)
    d.rectangle([3, 3, 28, 23], fill=CARD, outline=OUT)
    d.line([(4, 4), (27, 4)], fill=CARD_L)
    d.ellipse([7, 6, 24, 23], fill=fur, outline=CARD_D)
    d.ellipse([11, 14, 20, 21], fill=WHITE)
    eyes(d, 11, 11, 18, h=4)
    d.rectangle([15, 15, 16, 15], fill=EYE)  # нос
    d.rectangle([15, 18, 16, 20], fill=PINK, outline=OUT)  # язык
    d.line([(13, 17), (14, 18), (15, 17), (16, 17), (17, 18), (18, 17)], fill=OUT)
    return outline_pass(im)


def sulus():
    """Сулус, бык: круглый картонный шлем с рожками, голубой свитер
    с узором, серый фартук, широкие тёмные штаны. Выше остальных."""
    im, d = canvas(W, 54)
    sweater = (206, 230, 242, 255)
    apron = (160, 158, 156, 255)
    d.line([(21, 40), (25, 44), (24, 48)], fill=OUT)  # хвост
    legs(d, 40, 47, PANTS, sock=None, gap=2)
    d.rectangle([10, 38, 21, 44], fill=PANTS, outline=OUT)
    arms(d, 27, 35, sweater, hand=WHITE, x_in=10)
    d.rounded_rectangle([10, 25, 21, 40], radius=2, fill=sweater, outline=OUT)
    for x in range(11, 21, 3):  # голубой узор-ромбики
        d.point([(x + 1, 27), (x, 28), (x + 2, 28), (x + 1, 29)], fill=(110, 180, 220, 255))
    d.rectangle([12, 31, 19, 43], fill=apron, outline=OUT)
    # рожки и уши шлема
    horn = [(5, 8), (0, 4), (1, 10), (6, 12)]
    d.polygon(horn, fill=CARD, outline=OUT)
    d.polygon(mirror_x(horn, W), fill=CARD, outline=OUT)
    d.ellipse([4, 2, 27, 25], fill=CARD, outline=OUT)
    d.ellipse([8, 6, 23, 21], fill=WHITE, outline=CARD_D)
    d.point([(15, 8), (15, 9), (16, 9), (16, 8)], fill=(150, 150, 160, 255))  # отметина
    d.line([(11, 13), (13, 13)], fill=EYE)  # невозмутимый взгляд
    d.line([(18, 13), (20, 13)], fill=EYE)
    d.rectangle([12, 14, 13, 14], fill=EYE)
    d.rectangle([18, 14, 19, 14], fill=EYE)
    d.ellipse([11, 16, 20, 20], fill=PINK, outline=OUT)
    d.point([(13, 18), (18, 18)], fill=PINK_D)
    return outline_pass(im)


def player(facing):
    """Гость-детектив: шапка-охотничья (без нуара), бежевое пальто,
    красный шарф (ноябрь в Якутске), лупа в руке. facing: down / up / side."""
    im, d = canvas(24, 40)
    coat = (214, 182, 130, 255)
    coat_d = (170, 138, 92, 255)
    hat = (140, 96, 60, 255)
    scarf = (210, 50, 60, 255)
    skin = (240, 200, 164, 255)
    hair = (70, 44, 30, 255)
    # ноги
    for x0 in (8, 13):
        d.rectangle([x0, 30, x0 + 2, 35], fill=PANTS, outline=OUT)
        d.ellipse([x0 - 1, 34, x0 + 3, 38], fill=SHOE, outline=OUT)
    # пальто
    d.polygon([(6, 30), (8, 18), (15, 18), (17, 30)], fill=coat, outline=OUT)
    if facing == "down":
        d.line([(11, 21), (11, 29)], fill=coat_d)
        d.point([(10, 23), (10, 26)], fill=OUT)
    # руки
    d.rectangle([4, 19, 6, 26], fill=coat, outline=OUT)
    d.rectangle([17, 19, 19, 26], fill=coat, outline=OUT)
    d.ellipse([4, 25, 7, 28], fill=skin, outline=OUT)
    d.ellipse([16, 25, 19, 28], fill=skin, outline=OUT)
    if facing != "up":  # лупа в правой руке
        d.line([(19, 26), (21, 23)], fill=SHOE, width=1)
        d.ellipse([19, 18, 23, 22], fill=(190, 230, 245, 255), outline=OUT)
    # голова
    d.ellipse([5, 5, 18, 18], fill=skin if facing != "up" else hair, outline=OUT)
    if facing == "down":
        d.pieslice([5, 5, 18, 18], 180, 360, fill=hair)
        d.rectangle([8, 11, 9, 13], fill=EYE)
        d.rectangle([14, 11, 15, 13], fill=EYE)
        d.point([(9, 11), (15, 11)], fill=WHITE)
        d.point([(7, 14), (16, 14)], fill=BLUSH)
        d.line([(11, 15), (12, 15)], fill=OUT)
    elif facing == "side":
        d.pieslice([5, 5, 18, 18], 180, 360, fill=hair)
        d.polygon([(5, 9), (9, 9), (8, 15), (5, 14)], fill=hair)
        d.rectangle([14, 11, 15, 13], fill=EYE)
        d.point((15, 11), fill=WHITE)
        d.point((16, 14), fill=BLUSH)
    # шапка
    d.ellipse([4, 2, 19, 11], fill=hat, outline=OUT)
    d.line([(6, 7), (17, 7)], fill=(110, 72, 44, 255))
    d.point([(8, 4), (12, 3), (16, 5), (10, 6), (14, 6)], fill=(170, 124, 84, 255))
    if facing == "side":
        d.polygon([(17, 8), (22, 9), (17, 10)], fill=hat, outline=OUT)  # козырёк
    else:
        d.rectangle([3, 8, 5, 12], fill=hat, outline=OUT)  # клапаны
        d.rectangle([18, 8, 20, 12], fill=hat, outline=OUT)
    # шарф
    d.rectangle([7, 17, 16, 19], fill=scarf, outline=OUT)
    if facing != "up":
        d.rectangle([13, 19, 15, 23], fill=scarf, outline=OUT)
    return outline_pass(im)


## Гости фестиваля: (куртка, шапка, волосы, кожа, шарф, кошачьи ушки-косплей)
GUESTS = [
    ((90, 120, 200, 255), (230, 80, 90, 255), (60, 40, 30, 255), (240, 200, 164, 255), YELLOW_SC, False),
    ((230, 120, 60, 255), (60, 60, 70, 255), (30, 24, 22, 255), (214, 164, 120, 255), (90, 160, 220, 255), False),
    ((120, 170, 90, 255), None, (220, 180, 90, 255), (246, 210, 180, 255), (200, 60, 70, 255), True),
    ((150, 90, 160, 255), (250, 250, 250, 255), (90, 56, 36, 255), (226, 186, 150, 255), (250, 200, 80, 255), False),
    ((70, 70, 90, 255), None, (20, 20, 26, 255), (236, 196, 160, 255), (230, 90, 140, 255), True),
    ((200, 60, 70, 255), (90, 160, 220, 255), (120, 70, 40, 255), (200, 150, 110, 255), WHITE, False),
]


def guest(i):
    """Гость фестиваля 24×40: зимняя куртка, шапка с помпоном или косплей-ушки."""
    coat, hat, hair, skin, scarf, ears = GUESTS[i]
    im, d = canvas(24, 40)
    for x0 in (8, 13):
        d.rectangle([x0, 30, x0 + 2, 35], fill=PANTS, outline=OUT)
        d.ellipse([x0 - 1, 34, x0 + 3, 38], fill=SHOE, outline=OUT)
    d.polygon([(6, 30), (8, 18), (15, 18), (17, 30)], fill=coat, outline=OUT)
    d.line([(11, 21), (11, 29)], fill=OUT)
    d.rectangle([4, 19, 6, 26], fill=coat, outline=OUT)
    d.rectangle([17, 19, 19, 26], fill=coat, outline=OUT)
    d.ellipse([4, 25, 7, 28], fill=skin, outline=OUT)
    d.ellipse([16, 25, 19, 28], fill=skin, outline=OUT)
    d.ellipse([5, 5, 18, 18], fill=skin, outline=OUT)
    d.pieslice([5, 5, 18, 18], 180, 360, fill=hair)
    d.rectangle([8, 11, 9, 13], fill=EYE)
    d.rectangle([14, 11, 15, 13], fill=EYE)
    d.point([(7, 14), (16, 14)], fill=BLUSH)
    d.line([(11, 15), (12, 15)], fill=OUT)
    if ears:  # косплей: кошачьи ушки
        d.polygon([(6, 7), (7, 1), (10, 5)], fill=hair, outline=OUT)
        d.polygon([(17, 7), (16, 1), (13, 5)], fill=hair, outline=OUT)
        d.point([(8, 4), (15, 4)], fill=PINK)
    if hat:
        d.pieslice([4, 3, 19, 14], 180, 360, fill=hat, outline=OUT)
        d.rectangle([4, 7, 19, 9], fill=hat, outline=OUT)
        d.ellipse([9, 0, 14, 4], fill=WHITE, outline=OUT)
    d.rectangle([7, 17, 16, 19], fill=scarf, outline=OUT)
    return outline_pass(im)


MASCOTS = {"manya": manya, "lenya": lenya, "katya": katya, "moyto": moyto, "sulus": sulus}
