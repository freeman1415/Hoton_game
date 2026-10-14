"""Что генерировать: описание каждого спрайта для tools/ai_art/generate.py.

Поля ассета:
  file    — путь в game/art/
  kind    — character / prop / tile / backdrop / cosplay (шаблон промпта и обработка)
  size    — итоговый размер (w, h). Для персонажей — холст 64×64, рост HEIGHT.
            Для декораций None — площадь как у прежнего спрайта, пропорции — новые.
  prompt  — что нарисовать (по-английски: модель понимает английский)
  colors  — сколько цветов оставить (стиль дизайнера — 6–10 на спрайт)
  label   — надпись пиксельным шрифтом: (текст, x, y в долях, цвет, плашка под текстом)
            (модели портят кириллицу — на вывесках просим пустую табличку)

Маскоты (спрайты дизайнера) и игрок — не генерируются.
"""

# Общий стиль — как у спрайтов маскотов дизайнера (assets/new_assets/pixel_*.png):
# чиби, анфас, толстая чёрная обводка, плоская заливка, почти без теней.
STYLE = ("pixel art, 16-bit game sprite, thick black outline, flat colors, minimal shading, "
         "cute, simple shapes, warm cozy palette")
NEGATIVE = ("3d render, realistic, photo, blurry, gradient, soft shading, noise, dithering, text, letters, "
            "watermark, signature, frame, border, multiple views, cropped, shadow on ground")

CHARACTER = ("{style}, chibi character, full body, standing straight, facing the viewer, front view, "
             "looking at the camera, symmetrical, big head, small body, short legs, arms down, "
             "{prompt}, plain white background, centered, single character")
PROP = ("{style}, game asset, single object, {prompt}, front view, plain white background, "
        "centered, isolated")
COSPLAY = ("{style}, game asset, single clothing item, {prompt}, front view, flat lay, "
           "plain white background, centered, isolated, no person")
TILE = ("pixel art, seamless top-down floor texture, {prompt}, flat colors, simple, "
        "evenly lit, no objects, fills the whole image")
BACKDROP = ("pixel art, 16-bit game background, {prompt}, empty center, no characters, flat colors, "
            "simple shapes, warm cozy palette, wide shot")

HEIGHT = 62  # рост гостя в холсте 64×64 (как маскоты: ноги на нижнем ряду)

GUESTS = [
    ("characters/guest_0.png", "young woman, red knitted beanie with white pompom, long brown hair, "
     "light blue winter coat, orange scarf, brown boots"),
    ("characters/guest_1.png", "young man, dark grey knitted beanie with white pompom, dark skin, "
     "orange winter coat, light blue scarf, dark boots"),
    ("characters/guest_2.png", "young woman cosplayer, cat ears headband, long blond hair, "
     "green winter coat, red scarf, brown boots"),
    ("characters/guest_3.png", "young man, white knitted beanie with pompom, brown hair, "
     "salmon pink winter coat, green scarf, dark boots"),
    ("characters/guest_4.png", "young man cosplayer, black cat ears, messy black hair, "
     "purple winter coat, pink scarf, dark boots"),
    ("characters/guest_5.png", "young woman, light blue knitted beanie with pompom, auburn hair, "
     "red winter coat, white scarf, brown boots"),
]

INK = (74, 40, 22, 255)
CREAM = (255, 244, 230, 255)

PROPS = [
    ("props/main_stage.png", "festival main stage, wooden platform with steps, red curtains, "
     "big yellow star on the curtain, string lights, speakers"),
    ("props/music_stage.png", "small outdoor music stage, dark blue backdrop with white music notes, "
     "microphone stand, speakers, metal truss with lights"),
    ("props/rocket.png", "cardboard rocket costume prop, tall, round porthole window, small door, "
     "red nose cone and red fins, taped cardboard"),
    ("props/art_stall.png", "art market stall, pink and white striped awning, small paintings "
     "on display, easel with a painting"),
    ("props/circus_tent.png", "circus tent, red and yellow stripes, small red flag on top, open entrance"),
    ("props/lecture.png", "school chalkboard on legs with chalk drawings of a magnifying glass "
     "and question mark, small wooden lectern"),
    ("props/runway.png", "clothes rack with three costumes on hangers, tall mirror with light bulbs"),
    ("props/gate_hoton.png", "festival entrance arch, two wooden posts with flags, big blank orange "
     "banner on top, colorful bunting", ("ХОТОН", 0.5, 0.2, INK, (240, 160, 60, 255))),
    ("props/tea_stall.png", "tea stall, teal and white striped awning with a blank sign, samovar, "
     "teapot and cups on the counter, bunting", ("ЧАЙ", 0.5, 0.2, INK, CREAM)),
    ("props/bunting.png", "two wooden poles with colorful triangle flag garlands between them"),
    ("props/lamp.png", "old street lamp, black iron post, glowing yellow lantern"),
    ("props/bench.png", "wooden park bench, front view"),
    ("props/balloons.png", "bunch of three balloons, red blue and yellow, strings tied together"),
    ("props/guest_rope.png", "three brass stanchion posts with red velvet rope"),
    ("props/backstage_door.png", "doorway with red theater curtains, dark inside, wooden frame"),
    ("props/planet.png", "blue cardboard planet with yellow ring on a wooden stick, decoration"),
    ("props/star_sign.png", "yellow cardboard star on a wooden stick, decoration"),
    ("props/astronaut_board.png", "photo board standee with a cartoon astronaut on a dark blue starry "
     "background, blank sign at the top", ("КОСМОС", 0.5, 0.12, CREAM, (40, 50, 110, 255))),
    ("props/circus_pedestal.png", "circus pedestal drum, red and yellow triangles, striped ball on top"),
    ("props/circus_sign.png", "red marquee sign with light bulbs around a blank panel, on a wooden "
     "post", ("ЦИРК", 0.5, 0.22, CREAM, (190, 50, 50, 255))),
    ("props/jukebox.png", "retro jukebox, red and cream, glowing, rounded top"),
    ("props/vinyl_standee.png", "giant black vinyl record with orange label on a wooden stand"),
    ("props/disco_ball.png", "disco mirror ball on a black stand"),
    ("props/stage_back.png", "backstage wall, wooden panels with crossed braces, black cloth, "
     "red curtain at the edge, sandbags, road case, wide"),
    ("props/crates_prizes.png", "stack of cardboard boxes with red stars, blank red sign on top, "
     "gift box", ("ПРИЗЫ", 0.45, 0.15, CREAM, (200, 60, 60, 255))),
    ("props/spotlight.png", "stage spotlight on a black tripod, glowing lamp"),
    ("props/cable_coil.png", "coiled black cable on the floor"),
]

TILES = [
    ("tiles/ground.png", "beige paving stones, rounded rectangle bricks, light grey mortar", (64, 64)),
    ("tiles/backstage_floor.png", "dark brown wooden floor planks, vertical boards, nails", (64, 64)),
]

# Задники мини-игр: 214×120, в игре ×3 (640×360). Середина спокойная — там текст.
BACKDROPS = [
    ("minigames/backdrop_manya.png", "cozy art market interior, wooden walls with paintings, "
     "easels at the sides, paint pots on the floor, garland at the top"),
    ("minigames/backdrop_moyto.png", "inside a circus tent, red and dark red stripes, spotlights "
     "at the top corners, sand arena floor"),
    ("minigames/backdrop_sulus.png", "lecture hall, bookshelves at the sides, green chalkboard "
     "on the back wall, wooden floor, warm light"),
    ("minigames/backdrop_katya.png", "fashion runway stage, red velvet curtains at the sides, "
     "row of light bulbs at the top, disco ball, purple runway in perspective"),
]

# «Собери образ»: детали отдельно, их раскладывает по манекену postprocess.place_cosplay
COSPLAY_ITEMS = [
    ("cosplay/head_retro.png", "big curly orange afro wig with pink headband bow"),
    ("cosplay/head_circus.png", "red and yellow striped cone party hat with yellow pompom"),
    ("cosplay/head_space.png", "white cardboard space helmet with antennas, round open visor"),
    ("cosplay/head_detective.png", "brown checkered deerstalker detective hat"),
    ("cosplay/costume_retro.png", "pink and blue 80s windbreaker jacket with yellow stripes"),
    ("cosplay/costume_circus.png", "yellow clown jumpsuit with red polka dots and white ruffled collar"),
    ("cosplay/costume_space.png", "white cardboard spacesuit with control panel on the chest"),
    ("cosplay/costume_detective.png", "beige trench coat with belt"),
    ("cosplay/accessory_retro.png", "blue cassette player with orange headphones"),
    ("cosplay/accessory_circus.png", "round red clown nose"),
    ("cosplay/accessory_space.png", "small toy rocket backpack, red and white"),
    ("cosplay/accessory_detective.png", "magnifying glass with wooden handle"),
]
COSPLAY_MANNEQUIN = ("cosplay/mannequin.png", "wooden art mannequin doll on a round stand, "
                     "smiling face, arms down")
