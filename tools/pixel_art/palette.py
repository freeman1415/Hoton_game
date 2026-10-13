"""Общая палитра и хелперы для пиксель-арта Хотона.

Рисуем примитивами PIL без сглаживания, контур — 1 px тёмно-коричневый
(как карандашные линии на артах организаторов). Цвета сняты с
assets/all_mascots.jpg и картинок маскотов с hotonfest.ru.
"""
from math import cos, sin, pi

from PIL import Image, ImageDraw

OUT = (51, 34, 28, 255)
WHITE = (250, 248, 244, 255)
WHITE_SH = (212, 210, 222, 255)
CARD = (201, 154, 91, 255)
CARD_D = (150, 108, 60, 255)
CARD_L = (230, 196, 140, 255)
PINK = (240, 162, 156, 255)
PINK_D = (200, 110, 110, 255)
BLUSH = (246, 186, 186, 255)
EYE = (35, 25, 22, 255)
SHOE = (72, 46, 34, 255)
PANTS = (86, 58, 44, 255)
SKY = (120, 170, 230, 255)

# Акцент сайта hotonfest.ru (--ht-accent) и тёмный (--ht-ink)
ACCENT = (242, 159, 79, 255)
INK = (30, 41, 59, 255)


def canvas(w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def polygon_points(cx, cy, r, sides, rot=0.0, sx=1.0, sy=1.0):
    return [(round(cx + cos(rot + i * 2 * pi / sides) * r * sx),
             round(cy + sin(rot + i * 2 * pi / sides) * r * sy)) for i in range(sides)]


def outline_pass(im, color=OUT):
    """Внешний контур: прозрачный пиксель рядом с непрозрачным (не контуром) — контур."""
    w, h = im.size
    src = im.load()
    marks = []
    for y in range(h):
        for x in range(w):
            if src[x, y][3] != 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    p = src[nx, ny]
                    if p[3] != 0 and p != color:
                        marks.append((x, y))
                        break
    for x, y in marks:
        src[x, y] = color
    return im


def mirror_x(points, w):
    return [(w - 1 - x, y) for x, y in points]
