"""Собирает пиксель-арт в game/art/. Запуск из корня репозитория:

    python tools/pixel_art/build.py

Нужен Pillow. Перезаписывает PNG в game/art/ — после ручной перерисовки
в редакторе (Aseprite и т. п.) соответствующий спрайт из сборки убрать,
иначе правки затрутся.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from palette import *
from characters import GUESTS, MASCOTS, guest, player
from environment import PROPS, ground_tile, art_stall, circus_tent, lecture, \
    main_stage, music_stage, rocket, runway
from festival import FESTIVAL_PROPS, backstage_floor, balloons, gate_hoton, planet, tea_stall

ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "game", "art")

PAPER = (250, 244, 226, 255)
PAPER_LINE = (214, 226, 238, 255)
PATH = (226, 206, 168, 255)
CIRCLE = (214, 30, 40, 255)


def manya_sketch():
    """Эскиз Мани «схема праздника» 240×240 (сетка пазла 3×3 по 80 px).
    Раскладка повторяет хаб: лекторий слева сверху, музыкальная сцена сверху
    по центру и ракета за ней (обведена), арт-маркет и вход слева, главная
    сцена в центре, дефиле справа, шатёр Мойто снизу."""
    im, d = canvas(240, 240)
    d.rectangle([0, 0, 239, 239], fill=PAPER)
    for v in range(10, 240, 10):  # тетрадная клетка
        d.line([(v, 0), (v, 239)], fill=PAPER_LINE)
        d.line([(0, v), (239, v)], fill=PAPER_LINE)
    d.rectangle([0, 150, 239, 161], fill=PATH)
    d.rectangle([114, 60, 125, 190], fill=PATH)

    def put(sprite, x, y):
        im.alpha_composite(sprite, (x, y))

    put(lecture(), 8, 22)
    put(rocket(), 160, 4)
    put(music_stage(), 84, 24)
    put(planet(), 198, 50)
    put(art_stall(), 10, 98)
    put(main_stage(), 72, 96)
    put(runway(), 170, 100)
    put(gate_hoton(), 0, 176)
    put(circus_tent(), 86, 172)
    put(balloons(), 162, 178)
    put(tea_stall(), 180, 188)
    # кружок вокруг ракеты
    for r in (27, 28):
        d.ellipse([175 - r, 32 - r, 175 + r, 32 + r], outline=CIRCLE)
    # рамка листа
    d.rectangle([0, 0, 239, 239], outline=OUT)
    d.rectangle([1, 1, 238, 238], outline=OUT)
    return im


def save(im, *parts):
    path = os.path.join(ROOT, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path)
    print("wrote", os.path.relpath(path, os.path.join(ROOT, "..", "..")))


def main():
    for name, draw in MASCOTS.items():
        save(draw(), "characters", name + ".png")
    for facing in ("down", "up", "side"):
        save(player(facing), "characters", "player_%s.png" % facing)
    for i in range(len(GUESTS)):
        save(guest(i), "characters", "guest_%d.png" % i)
    for name, draw in PROPS.items():
        if name in ("pine", "gate"):  # хаб — фестиваль, не лес; вход теперь gate_hoton
            continue
        save(draw(), "props", name + ".png")
    for name, draw in FESTIVAL_PROPS.items():
        save(draw(), "props", name + ".png")
    save(ground_tile(), "tiles", "ground.png")
    save(backstage_floor(), "tiles", "backstage_floor.png")
    save(manya_sketch(), "minigames", "manya_sketch.png")


if __name__ == "__main__":
    main()
