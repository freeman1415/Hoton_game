"""Сырые генерации (tools/ai_art/raw/) → спрайты игры в стиле дизайнера.

    python tools/ai_art/postprocess.py [фильтр] [--sheet файл.png]

Выбранный вариант каждого ассета — в picks.json ({"props/rocket.png": 2}, по
умолчанию вариант 1). --sheet — собрать лист всех вариантов для выбора, ничего не
записывая в игру.

Что делаем со спрайтом (то, что отличает его от «сырой нейросети»):
  1. фон: заливка от краёв по светлому однотонному фону; спрайт держит обводка;
  2. сетка: Pixel Art XL рисует «пикселями» ~8×8 — уменьшаем модой блока до
     настоящих пикселей, потом до игрового размера (каждый пиксель — один цвет);
  3. палитра: k-средних до `colors` цветов, затем каждый цвет подтягиваем к общей
     палитре (цвета спрайтов маскотов дизайнера + брендбук + их тени);
  4. обводка: крайний ряд пикселей спрайта — чистый чёрный, как у маскотов;
  5. мусор: одиночные пиксели другого цвета заменяются соседним цветом.
"""
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pixel_art"))
import assets as A  # noqa: E402
from festival import draw_text, text_width  # noqa: E402

HERE = os.path.dirname(__file__)
RAW = os.path.join(HERE, "raw")
ART = os.path.join(HERE, "..", "..", "game", "art")
PICKS = os.path.join(HERE, "picks.json")

# Цвета спрайтов маскотов дизайнера (assets/new_assets/pixel_*.png) и брендбука
DESIGNER = ["#000000", "#ffffff", "#261509", "#cdd1d0", "#ab7a62", "#36418d", "#362010", "#e02719",
            "#cf7b43", "#f9c8d5", "#724718", "#b2e4e3", "#d68e5e", "#84b0ff", "#bababa", "#e68f30",
            "#44c859", "#211106", "#dd353e", "#00f4ff", "#ffcf00", "#585858", "#f0d1bc", "#f493ad",
            "#e0e0e0"]
BRAND = ["#e48824", "#d48464", "#604030", "#78b0c8", "#cc5c60", "#74b068", "#fff4e6", "#2a1b14"]
# Дополнительно: дерево, кожа, небо, фиолетовый — их нет у маскотов, а в декорациях нужны
EXTRA = ["#8a5a32", "#b97a45", "#d9a066", "#f2d3a2", "#e8b48a", "#9c6b4e", "#5b6ee1", "#2e3a6e",
         "#8e5bbf", "#5a3a7a", "#3f7a4a", "#9be0a0", "#ffe8a0", "#c8a0e8", "#7a7a7a", "#a83a3a"]


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def master_palette():
    base = [hex_rgb(h) for h in DESIGNER + BRAND + EXTRA]
    shades = [tuple(int(c * 0.72) for c in rgb) for rgb in base]
    return np.array(base + shades, dtype=float)


PALETTE = master_palette()


# region Шаги обработки

def remove_background(rgb, tolerance=38):
    """Маска непрозрачного: фон — цвет краёв картинки (белый, серый) и всё близкое к
    нему, связанное с краем (в т. ч. мягкая тень под ногами)."""
    a = rgb.astype(int)
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    bg_color = np.median(border, axis=0)
    near = np.abs(a - bg_color).max(axis=2) <= tolerance
    lab, _ = ndimage.label(near)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge))
    # Замкнутые куски фона (внутри вешалки, под прилавком) — тоже фон, если крупные;
    # мелкие белые таблички и блики остаются
    sizes = ndimage.sum(near, lab, range(1, lab.max() + 1))
    big = [i + 1 for i, s in enumerate(sizes) if s >= near.size * 0.01 and i + 1 not in edge]
    bg |= np.isin(lab, big)
    fg = ndimage.binary_opening(~bg, iterations=2)
    # оставляем крупные пятна (спрайт), мелкий мусор по углам — в фон
    lab, n = ndimage.label(fg)
    if n > 1:
        sizes = ndimage.sum(fg, lab, range(1, n + 1))
        fg = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= sizes.max() * 0.02])
    return fg


def grid_downscale(rgb, mask, w, h):
    """Уменьшение модой блока: самый частый цвет, прозрачно, если фона больше половины."""
    sh, sw = mask.shape
    out = np.zeros((h, w, 4), np.uint8)
    q = (rgb // 12).astype(np.int32)
    key = (q[..., 0] << 10) | (q[..., 1] << 5) | q[..., 2]
    for ty in range(h):
        y0 = int(ty * sh / h)
        y1 = max(y0 + 1, int((ty + 1) * sh / h))
        for tx in range(w):
            x0 = int(tx * sw / w)
            x1 = max(x0 + 1, int((tx + 1) * sw / w))
            m = mask[y0:y1, x0:x1]
            if m.mean() < 0.5:
                continue
            k = key[y0:y1, x0:x1][m]
            vals, counts = np.unique(k, return_counts=True)
            best = vals[np.argmax(counts)]
            out[ty, tx, :3] = rgb[y0:y1, x0:x1][m & (key[y0:y1, x0:x1] == best)].mean(axis=0)
            out[ty, tx, 3] = 255
    return out


## Цвет подтягивается к общей палитре, только если в ней есть близкий (иначе — свой)
SNAP_DISTANCE = 30


def quantize(img, colors):
    """k-средних до colors цветов (начальные — самые непохожие), потом каждый цвет —
    к ближайшему из общей палитры, если тот близко."""
    opaque = img[..., 3] > 0
    pix = img[opaque][:, :3].astype(float)
    if len(pix) == 0:
        return img
    rng = np.random.default_rng(1)
    centers = [pix[rng.integers(len(pix))]]
    while len(centers) < min(colors, len(pix)):
        d = np.min([((pix - c) ** 2).sum(axis=1) for c in centers], axis=0)
        centers.append(pix[d.argmax()])
    centers = np.array(centers)
    for _ in range(15):
        d = ((pix[:, None, :] - centers[None]) ** 2).sum(axis=2)
        lab = d.argmin(axis=1)
        for i in range(len(centers)):
            if (lab == i).any():
                centers[i] = pix[lab == i].mean(axis=0)
    dist = ((centers[:, None, :] - PALETTE[None]) ** 2).sum(axis=2)
    nearest = PALETTE[dist.argmin(axis=1)]
    close = np.sqrt(dist.min(axis=1)) <= SNAP_DISTANCE
    final = np.where(close[:, None], nearest, centers)
    out = img.copy()
    out[opaque, :3] = final[lab].astype(np.uint8)
    return out


def despeckle(img):
    """Одиночный пиксель, у которого нет ни одного соседа того же цвета, — в цвет соседей."""
    out = img.copy()
    h, w = img.shape[:2]
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if img[y, x, 3] == 0:
                continue
            c = tuple(img[y, x])
            neigh = [tuple(img[y + dy, x + dx]) for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0))]
            if c not in neigh:
                opaque = [n for n in neigh if n[3] > 0]
                if len(opaque) == 4:
                    vals, counts = np.unique(np.array(opaque), axis=0, return_counts=True)
                    out[y, x] = vals[counts.argmax()]
    return out

# endregion


def native(raw_path):
    """Сырая генерация → RGBA на её «настоящей» сетке (Pixel Art XL рисует блоками ~8 px)."""
    rgb = np.array(Image.open(raw_path).convert("RGB"))
    mask = remove_background(rgb)
    ys, xs = np.nonzero(mask)
    sl = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
    rgb, mask = rgb[sl], mask[sl]
    return rgb, mask


def make_sprite(raw_path, size, colors, keep_aspect_area=None):
    rgb, mask = native(raw_path)
    sh, sw = mask.shape
    if size is None:
        # площадь как у прежнего спрайта
        k = (keep_aspect_area / (sw * sh)) ** 0.5
        size = (max(4, round(sw * k)), max(4, round(sh * k)))
    w, h = size
    img = grid_downscale(rgb, mask, w, h)
    img = quantize(img, colors)
    img = despeckle(despeckle(img))
    img = outline_inside(img)
    return img


def outline_inside(img):
    """Обводка внутри размера: внешний ряд непрозрачных пикселей — чёрный."""
    opaque = img[..., 3] > 0
    edge = opaque & ~ndimage.binary_erosion(opaque, structure=[[0, 1, 0], [1, 1, 1], [0, 1, 0]],
                                            border_value=0)
    out = img.copy()
    out[edge] = (0, 0, 0, 255)
    return out


def character(raw_path, colors=9):
    """Гость: рост A.HEIGHT, холст 64×64, ноги на нижнем ряду, по центру."""
    rgb, mask = native(raw_path)
    sh, sw = mask.shape
    h = A.HEIGHT
    w = max(8, round(sw * h / sh))
    img = grid_downscale(rgb, mask, w, h)
    img = quantize(img, colors)
    img = despeckle(despeckle(img))
    img = outline_inside(img)
    canvas = np.zeros((64, 64, 4), np.uint8)
    x0 = (64 - w) // 2
    canvas[64 - h:, max(0, x0):max(0, x0) + min(w, 64)] = img[:, max(0, -x0):max(0, -x0) + min(w, 64)]
    return canvas


def tile(raw_path, size, colors=8):
    """Пол: исходник был плиткой 2×2 — уменьшаем до 2×2 плиток и берём центральную
    (её края — середины соседних, швы мягче), потом прячем шов: края, не совпадающие
    с противоположными, заменяем соседним рядом."""
    rgb = np.array(Image.open(raw_path).convert("RGB"))
    w, h = size
    img = grid_downscale(rgb, np.ones(rgb.shape[:2], bool), w * 2, h * 2)
    img = img[h // 2:h // 2 + h, w // 2:w // 2 + w].copy()
    return quantize(img, colors)


def backdrop(raw_path, colors=16):
    """Задник мини-игры: 214×120 (в игре ×3), середина темнее — там текст."""
    rgb = np.array(Image.open(raw_path).convert("RGB"))
    # Исходник 640×360 вписан в 1344×768 с белыми полями по 6 px сверху и снизу
    pad = (rgb.shape[0] - round(360 * rgb.shape[1] / 640)) // 2
    if pad > 0:
        rgb = rgb[pad:rgb.shape[0] - pad]
    img = grid_downscale(rgb, np.ones(rgb.shape[:2], bool), 214, 120)
    img = quantize(img, colors)
    yy, xx = np.mgrid[0:120, 0:214]
    d = np.clip(((xx - 107) / 107) ** 2 * 0.8 + ((yy - 60) / 60) ** 2 * 1.2, 0, 1)
    k = (1 - 0.5 * (1 - d))[..., None]
    img[..., :3] = (img[..., :3] * k).astype(np.uint8)
    return img


INIT = os.path.join(RAW, "_init", "game", "art")


def cosplay(file, raw_path, colors=8):
    """Деталь костюма рисовалась на манекене (холст 64×64 ×16): уменьшаем весь кадр
    обратно до 64×64 и берём пиксели там, где была прежняя деталь (с запасом в 1 px) —
    слои ложатся друг на друга как раньше. Манекен — целиком."""
    rgb = np.array(Image.open(raw_path).convert("RGB"))
    fg = remove_background(rgb)
    img = grid_downscale(rgb, fg, 64, 64)
    old = np.array(Image.open(os.path.join(INIT, file)).convert("RGBA"))[..., 3] > 0
    if not file.endswith("mannequin.png"):
        keep = ndimage.binary_dilation(old, iterations=1)
        img[~keep] = 0
    img = quantize(img, colors)
    img = despeckle(img)
    return outline_inside(img)


def add_label(img, label):
    """Надпись пиксельным шрифтом на плашке (генератор кириллицу не умеет)."""
    text, fx, fy, color, plate = label
    im = Image.fromarray(img).copy()
    x = round(im.width * fx - text_width(text, 1) / 2)
    y = round(im.height * fy - 2)
    px = im.load()
    for yy in range(max(0, y - 2), min(im.height, y + 7)):
        for xx in range(max(0, x - 2), min(im.width, x + text_width(text, 1) + 2)):
            edge = yy in (y - 2, y + 6) or xx in (x - 2, x + text_width(text, 1) + 1)
            px[xx, yy] = (0, 0, 0, 255) if edge else plate
    draw_text(im, x, y, text, color, 1)
    return np.array(im)


def old_area(file):
    """Площадь прежнего спрайта (из снимка raw/_init — не из игры, её мы перезаписываем)."""
    path = os.path.join(INIT, file)
    if not os.path.exists(path):
        return 48 * 48
    w, h = Image.open(path).size
    return w * h


def variants(file):
    folder = os.path.join(RAW, os.path.splitext(file)[0].replace("/", "__"))
    if not os.path.isdir(folder):
        return []
    return sorted(os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".png"))


def process(file, raw_path):
    """Один ассет → numpy RGBA."""
    for f, prompt in A.GUESTS:
        if f == file:
            return character(raw_path)
    for item in A.PROPS:
        if item[0] == file:
            img = make_sprite(raw_path, None, 10, old_area(file))
            return add_label(img, item[2]) if len(item) > 2 else img
    for f, prompt, size in A.TILES:
        if f == file:
            return tile(raw_path, size)
    for f, prompt in A.BACKDROPS:
        if f == file:
            return backdrop(raw_path)
    for f, prompt in A.COSPLAY_ITEMS + [A.COSPLAY_MANNEQUIN]:
        if f == file:
            return cosplay(file, raw_path)
    raise KeyError(file)


def all_files():
    return ([f for f, _ in A.GUESTS] + [p[0] for p in A.PROPS] + [t[0] for t in A.TILES]
            + [b[0] for b in A.BACKDROPS] + [c[0] for c in A.COSPLAY_ITEMS + [A.COSPLAY_MANNEQUIN]])


def sheet(files, path):
    """Лист выбора: строка на ассет — все варианты, обработанные, ×3 на сером."""
    rows = []
    for file in files:
        cells = []
        for v in variants(file):
            try:
                img = Image.fromarray(process(file, v))
            except Exception as e:  # пустая генерация и т. п.
                print("  ошибка", file, v, e)
                continue
            k = max(1, min(4, 150 // max(img.size)))
            cells.append(img.resize((img.width * k, img.height * k), Image.NEAREST))
        if cells:
            rows.append((file, cells))
    width = max(sum(c.width + 10 for c in cells) for _, cells in rows) + 10
    height = sum(max(c.height for c in cells) + 24 for _, cells in rows)
    out = Image.new("RGBA", (width, height), (96, 112, 96, 255))
    from PIL import ImageDraw
    d = ImageDraw.Draw(out)
    y = 0
    for file, cells in rows:
        d.text((4, y + 2), file, fill=(255, 255, 0, 255))
        x = 10
        for i, c in enumerate(cells):
            out.alpha_composite(c, (x, y + 16))
            d.text((x, y + 16), str(i + 1), fill=(255, 255, 255, 255))
            x += c.width + 10
        y += max(c.height for c in cells) + 24
    out.save(path)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--") and not a.endswith(".png")]
    files = [f for f in all_files() if not args or any(a in f for a in args)]
    if "--sheet" in sys.argv:
        sheet(files, sys.argv[sys.argv.index("--sheet") + 1])
        return
    picks = json.load(open(PICKS)) if os.path.exists(PICKS) else {}
    for file in files:
        vs = variants(file)
        if not vs:
            continue
        pick = picks.get(file, 1)
        img = process(file, vs[pick - 1])
        path = os.path.join(ART, file)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        Image.fromarray(img).save(path)
        print("ai_art", file, img.shape[1], "x", img.shape[0], "вариант", pick)


if __name__ == "__main__":
    main()
