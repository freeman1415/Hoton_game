"""Пересчитать offset декораций после замены спрайтов (размеры поменялись).

    python tools/pixel_art/fix_offsets.py          — показать, что изменится
    python tools/pixel_art/fix_offsets.py --write  — записать в сцены

Декорация в хабе и закулисье — Sprite2D с centered = false и offset = (-w/2, -h):
ноги (низ картинки) стоят на position. Скрипт находит такие узлы в SCENES и
ставит offset по текущему размеру PNG. Узлы с положительным offset (сдвинуты
руками не по формуле) не трогает и печатает — их проверить в редакторе.
"""
import os
import re
import sys

from PIL import Image

GAME = os.path.join(os.path.dirname(__file__), "..", "..", "game")
SCENES = ["scenes/world.tscn", "scenes/backstage/backstage.tscn"]
TEXTURE_RE = r'\[ext_resource type="Texture2D"[^\]]*path="res://([^"]+)" id="([^"]+)"\]'


def formula(w, h):
    return (-(w // 2), -h)


def main(write):
    for scene in SCENES:
        path = os.path.join(GAME, scene)
        text = open(path, encoding="utf-8").read()
        textures = {rid: p for p, rid in re.findall(TEXTURE_RE, text)}
        blocks = re.split(r"(?m)^(?=\[node )", text)
        changed = 0
        for i, block in enumerate(blocks):
            tex = re.search(r'^texture = ExtResource\("([^"]+)"\)', block, re.M)
            off = re.search(r"^offset = Vector2\((-?[\d.]+), (-?[\d.]+)\)", block, re.M)
            if not tex or not off or "centered = false" not in block or tex.group(1) not in textures:
                continue
            png = textures[tex.group(1)]
            w, h = Image.open(os.path.join(GAME, png)).size
            new = formula(w, h)
            old = (float(off.group(1)), float(off.group(2)))
            name = re.search(r'name="([^"]+)"', block).group(1)
            if new == old:
                continue
            if old[0] > 0 or old[1] > 0:
                print("  SKIP %s %s: offset %s" % (scene, name, old))
                continue
            print("  %s %s (%s): %s -> %s" % (scene, name, png, old, new))
            blocks[i] = block[:off.start()] + "offset = Vector2(%d, %d)" % new + block[off.end():]
            changed += 1
        if write and changed:
            open(path, "w", encoding="utf-8", newline="\n").write("".join(blocks))
        print("%s: %d changes%s" % (scene, changed, "" if write else " (dry run, use --write)"))


if __name__ == "__main__":
    main("--write" in sys.argv)
