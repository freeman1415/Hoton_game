"""Генерация спрайтов через локальный ComfyUI (http://127.0.0.1:8188).

Режим img2img: за основу берётся прежний спрайт игры (raw/_init/game/art/, снимок из
git) — увеличенный, на белом фоне. Пропорции, поза, анфас, цвета и размеры остаются
нашими (как у маскотов дизайнера), нейросеть только перерисовывает детали
(DENOISE: 0 — без изменений, 1 — с нуля). Без исходника — генерация с нуля.

    python tools/ai_art/generate.py [фильтр] [--seeds N] [--denoise 0.6] [--force]

Для каждого ассета из assets.py делает N вариантов (разные seed) и кладёт сырые
картинки в tools/ai_art/raw/<имя>/<seed>.png (в git не попадают). Дальше —
postprocess.py: выбор варианта, пиксельная сетка, палитра, обводка.
фильтр — подстрока имени файла («guest», «props/», «cosplay»).

Модели (в ComfyUI/models): SDXL base 1.0, VAE fp16-fix, LoRA Pixel Art XL.
Лицензии — docs/ASSETS.md → «Генерация (ComfyUI)».
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

import assets as A

SERVER = "http://127.0.0.1:8188"
RAW = os.path.join(os.path.dirname(__file__), "raw")
CHECKPOINT = "sd_xl_base_1.0.safetensors"
VAE = "sdxl_vae_fp16_fix.safetensors"
PIXEL_LORA = ("pixel-art-xl.safetensors", 1.2)
STEPS = 28
CFG = 6.5
## Насколько перерисовывать исходный спрайт
DENOISE = 0.72
INIT = os.path.join(RAW, "_init", "game", "art")


def canvas_for(file, default=(1024, 1024)):
    """Размер генерации (~1 Мп, кратно 64) по пропорциям прежнего спрайта."""
    from PIL import Image
    path = os.path.join(INIT, file)
    if not os.path.exists(path):
        return default
    w, h = Image.open(path).size
    aspect = max(0.5, min(2.4, w / h))
    width = int(round((1048576 * aspect) ** 0.5 / 64)) * 64
    height = int(round(1048576 / width / 64)) * 64
    return width, height


def jobs():
    """[(имя, промпт, ширина, высота, режим исходника)].
    Режимы: sprite — спрайт по центру, ноги внизу; full — кадр целиком;
    tile — плитка 2×2; cosplay — деталь на манекене (холст 64×64 целиком)."""
    out = []
    for file, prompt in A.GUESTS:
        out.append((file, A.CHARACTER.format(style=A.STYLE, prompt=prompt), 832, 1216, "sprite"))
    for item in A.PROPS:
        file, prompt = item[0], item[1]
        out.append((file, A.PROP.format(style=A.STYLE, prompt=prompt), *canvas_for(file), "sprite"))
    for file, prompt, _ in A.TILES:
        out.append((file, A.TILE.format(prompt=prompt), 1024, 1024, "tile"))
    for file, prompt in A.BACKDROPS:
        out.append((file, A.BACKDROP.format(prompt=prompt), 1344, 768, "full"))
    for file, prompt in A.COSPLAY_ITEMS + [A.COSPLAY_MANNEQUIN]:
        template = A.PROP if "mannequin" in file else A.COSPLAY
        out.append((file, template.format(style=A.STYLE, prompt=prompt), 1024, 1024, "cosplay"))
    return out


def init_image(file, width, height, mode):
    """Прежний спрайт → PNG width×height на белом фоне (исходник для img2img)."""
    from PIL import Image
    import io
    path = os.path.join(INIT, file)
    if not os.path.exists(path):
        return None
    src = Image.open(path).convert("RGBA")
    canvas = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    if mode == "sprite":
        sprite = src.crop(src.getbbox())
        k = max(1, min(int(width * 0.8 // sprite.width), int(height * 0.85 // sprite.height)))
        sprite = sprite.resize((sprite.width * k, sprite.height * k), Image.NEAREST)
        canvas.alpha_composite(sprite, ((width - sprite.width) // 2, height - sprite.height - height // 20))
    elif mode == "tile":
        tiled = Image.new("RGBA", (src.width * 2, src.height * 2))
        for i in range(2):
            for j in range(2):
                tiled.paste(src, (i * src.width, j * src.height))
        canvas = tiled.resize((width, height), Image.NEAREST)
    elif mode == "full":
        k = min(width / src.width, height / src.height)
        big = src.resize((round(src.width * k), round(src.height * k)), Image.NEAREST)
        canvas.alpha_composite(big, ((width - big.width) // 2, (height - big.height) // 2))
    elif mode == "cosplay":
        # деталь на манекене: модель видит, где голова и тело; холст 64×64 → ×16
        base = Image.open(os.path.join(INIT, "cosplay", "mannequin.png")).convert("RGBA")
        if not file.endswith("mannequin.png"):
            base.alpha_composite(src)
        canvas.alpha_composite(base.resize((width, height), Image.NEAREST))
    buf = io.BytesIO()
    canvas.convert("RGB").save(buf, "PNG")
    return buf.getvalue()


def upload(png, name):
    """Картинку — в input/ ComfyUI (multipart/form-data)."""
    boundary = "----hoton%d" % int(time.time() * 1000)
    crlf = "\r\n"
    head = crlf.join(["--" + boundary,
                      'Content-Disposition: form-data; name="image"; filename="%s"' % name,
                      "Content-Type: image/png", "", ""])
    tail = crlf.join(["", "--" + boundary, 'Content-Disposition: form-data; name="overwrite"', "",
                      "true", "--" + boundary + "--", ""])
    body = head.encode() + png + tail.encode()
    req = urllib.request.Request(SERVER + "/upload/image", data=body,
                                 headers={"Content-Type": "multipart/form-data; boundary=" + boundary})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["name"]


def workflow(prompt, width, height, seed, init_name=None, denoise=DENOISE):
    """Граф ComfyUI в формате API. init_name — исходник в input/ (img2img)."""
    graph = {
        "ckpt": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CHECKPOINT}},
        "vae": {"class_type": "VAELoader", "inputs": {"vae_name": VAE}},
        "lora": {"class_type": "LoraLoader", "inputs": {
            "model": ["ckpt", 0], "clip": ["ckpt", 1], "lora_name": PIXEL_LORA[0],
            "strength_model": PIXEL_LORA[1], "strength_clip": 1.0}},
        "pos": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["lora", 1], "text": prompt}},
        "neg": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["lora", 1], "text": A.NEGATIVE}},
        "latent": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height,
                                                                 "batch_size": 1}},
        "sample": {"class_type": "KSampler", "inputs": {
            "model": ["lora", 0], "positive": ["pos", 0], "negative": ["neg", 0],
            "latent_image": ["latent", 0], "seed": seed, "steps": STEPS, "cfg": CFG,
            "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0}},
        "decode": {"class_type": "VAEDecode", "inputs": {"samples": ["sample", 0], "vae": ["vae", 0]}},
        "save": {"class_type": "SaveImage", "inputs": {"images": ["decode", 0],
                                                        "filename_prefix": "hoton"}},
    }
    if init_name:
        graph["init"] = {"class_type": "LoadImage", "inputs": {"image": init_name}}
        graph["encode"] = {"class_type": "VAEEncode", "inputs": {"pixels": ["init", 0], "vae": ["vae", 0]}}
        graph["sample"]["inputs"]["latent_image"] = ["encode", 0]
        graph["sample"]["inputs"]["denoise"] = denoise
        del graph["latent"]
    return graph


def call(path, data=None):
    req = urllib.request.Request(SERVER + path, data=json.dumps(data).encode() if data else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def run(prompt, width, height, seed, init_name=None, denoise=DENOISE):
    graph = workflow(prompt, width, height, seed, init_name, denoise)
    pid = json.loads(call("/prompt", {"prompt": graph}))["prompt_id"]
    while True:
        time.sleep(1.0)
        hist = json.loads(call("/history/" + pid))
        if pid in hist:
            status = hist[pid].get("status", {})
            if status.get("status_str") == "error":
                raise RuntimeError(json.dumps(status)[:500])
            images = hist[pid]["outputs"]["save"]["images"]
            q = urllib.parse.urlencode({"filename": images[0]["filename"],
                                        "subfolder": images[0]["subfolder"], "type": "output"})
            return call("/view?" + q)


def main():
    argv = sys.argv[1:]
    seeds = 3
    if "--seeds" in argv:
        i = argv.index("--seeds")
        seeds = int(argv[i + 1])
        del argv[i:i + 2]
    denoise = DENOISE
    if "--denoise" in argv:
        i = argv.index("--denoise")
        denoise = float(argv[i + 1])
        del argv[i:i + 2]
    args = [a for a in argv if not a.startswith("--")]
    force = "--force" in sys.argv
    todo = [j for j in jobs() if not args or any(a in j[0] for a in args)]
    print("заданий:", len(todo), "× вариантов:", seeds)
    for file, prompt, w, h, mode in todo:
        folder = os.path.join(RAW, os.path.splitext(file)[0].replace("/", "__"))
        os.makedirs(folder, exist_ok=True)
        png = init_image(file, w, h, mode)
        init_name = upload(png, file.replace("/", "__")) if png else None
        for seed in range(1, seeds + 1):
            out = os.path.join(folder, "%d.png" % seed)
            if os.path.exists(out) and not force:
                continue
            t = time.time()
            result = run(prompt, w, h, seed * 1000 + 7, init_name, denoise)
            open(out, "wb").write(result)
            print("%s seed %d — %.0f с" % (file, seed, time.time() - t), flush=True)


if __name__ == "__main__":
    main()
