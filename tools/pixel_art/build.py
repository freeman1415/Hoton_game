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
from characters import GUESTS, guest
from environment import PROPS, ground_tile, art_stall, circus_tent, lecture, \
    main_stage, music_stage, rocket, runway
from festival import FESTIVAL_PROPS, backstage_floor, balloons, gate_hoton, planet, tea_stall
from cosplay import COSPLAY

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
    # Маскоты — спрайты дизайнера (assets/new_assets/pixel_*.png), скопированы в game/art/characters/.
    # Гости, декорации, пол и «Собери образ» с 2026-10-15 генерирует tools/ai_art/ — здесь их
    # больше не рисуем, иначе сборка затрёт генерацию. Игрок с 2026-10-15 — спрайты дизайнера
    # (assets/new_assets/mc*.png). Остался эскиз Мани.
    save(manya_sketch(), "minigames", "manya_sketch.png")


if __name__ == "__main__":
    main()
