"""Портреты для окна диалога (как в Undertale): голова и плечи из спрайтов 64×64.

    python tools/pixel_art/portraits.py

Берёт game/art/characters/<кто>.png (маскоты — спрайты дизайнера команды, гости —
черновик из build.py) и вырезает кадр CROP. Пишет game/art/portraits/<кто>.png,
в игре показывается ×2. Перерисовал спрайт — перезапусти скрипт.
Захочется отдельный портрет с эмоциями — нарисовать его 48×40 руками
и убрать имя из WHO.
"""
import os

from PIL import Image

ART = os.path.join(os.path.dirname(__file__), "..", "..", "game", "art")
WHO = ["manya", "lenya", "katya", "moyto", "sulus"] + ["guest_%d" % i for i in range(6)]
# (left, top, right, bottom) в спрайте 64×64: голова и плечи
CROP = (8, 0, 56, 40)


def main():
    out = os.path.join(ART, "portraits")
    os.makedirs(out, exist_ok=True)
    for who in WHO:
        sprite = Image.open(os.path.join(ART, "characters", who + ".png")).convert("RGBA")
        sprite.crop(CROP).save(os.path.join(out, who + ".png"))
        print("portrait", who)


if __name__ == "__main__":
    main()
