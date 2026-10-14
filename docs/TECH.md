# docs/TECH.md — техническая спецификация

## Стек

- **Godot 4.7**, GDScript. Открывать проект только этой версией — более старая не откроет, более новая может молча переконвертировать сцены.
- **Сторонних плагинов нет** (Dialogue Manager убран 2026-10-14). Диалоги — своя система на обычных сценах, см. «Диалоги».
- ПК (Windows, Linux), экспорт `.exe` / `.x86_64`.
- Рендер: **Compatibility** (OpenGL 3.3) — запустится и на слабом фестивальном ПК со встроенной графикой (решено 2026-10-14). 3D-физика (Jolt) выключена — игра 2D.
- Имя проекта: «Хотон: Дело о пропавшей Капсуле» (заголовок окна).

## Первый запуск

```bash
git clone <repo>
# Godot 4.7 → Import → game/project.godot
```

Git инициализирован в корне. `.gitignore`:
- `/.gitignore` — ОС-мусор, `build/`, `*.tmp`;
- `game/.gitignore` — `.godot/` (кэш импорта, пересоздаётся редактором).

## Godot MCP (для ИИ-ассистент)

Сервер `@coding-solo/godot-mcp` позволяет ИИ-ассистент запускать редактор и проект, читать вывод отладки и создавать сцены. Он подключается **у каждого локально**, потому что путь к Godot у всех свой:

```bash
mcp add godot --scope local -e "GODOT_PATH=<путь>\Godot_v4.7.2-stable_win64_console.exe" -- npx -y "@coding-solo/godot-mcp@0.1.1"
```

- Нужен Node.js 18+.
- Указывайте `_console.exe`, а не обычный `.exe`: только он пишет вывод в stdout.
- После добавления перезапустите ИИ-ассистент.

Проверка проекта без MCP:

```bash
godot --headless --path game --import                      # импорт ресурсов
godot --headless --path game --quit-after 180 res://scenes/minigames/rhythm/rhythm.tscn   # прогнать сцену ~3 с
```

## Структура `game/`

Текущая:

```
game/
  project.godot        — главная сцена: scenes/ui/title.tscn
  dialogue/           — по файлу на маскота: manya, lenya, katya, moyto, sulus
  scenes/world.tscn    — хаб: 5 зон маскотов, гости, декорации секторов, проход за кулисы, HUD печатей
  scenes/hub/mascot_npc.tscn — маскот/гость/предмет (спрайт, круг зоны по show_zone, разговор по Enter)
  scenes/hub/door.tscn — проход между локациями (хаб ↔ закулисье)
  scenes/player/player.tscn — игрок (общий для хаба и закулисья; camera_limits — края локации)
  scenes/backstage/    — закулисье: ракета, коробки «ПРИЗЫ»; в финале — маскоты и открытие Капсулы
  scenes/minigames/quiz/ — викторина Мойто
  scenes/minigames/cosplay/ — «Собери образ» Кати
  scenes/minigames/art/ — «Собери эскиз» Мани (картинка — art/minigames/manya_sketch.png)
  scenes/minigames/logic/ — «Рассади слушателей» Сулуса
  scenes/finale/       — финал: вопросы ГДЕ/КТО/ЗАЧЕМ, концовки, итоги
  scenes/ui/title.tscn — титульный экран, топ-5, Ctrl+Shift+F12 — сброс рекордов
  scenes/ui/notebook.tscn — Детективный блокнот (Tab), ставит игру на паузу
  scenes/ui/dialogue_box.tscn/.gd — окно диалога (своё): имя, текст с печатью, варианты ответа
  scripts/dialogue.gd  — autoload `Dialogue`: запуск и обрыв разговоров
  scenes/test.tscn     — тестовая, удалить
  scripts/character_body_2d.gd — движение игрока, возврат на место после мини-игры
  scripts/game_state.gd — autoload `GameState`: печати, улики, таймер, рестарт по R
  scripts/leaderboard.gd — autoload `Leaderboard`: топ-5 в user://leaderboard.cfg
  art/ui/logo_hoton.png — логотип для титульного экрана
  art/characters/ props/ tiles/ minigames/ — пиксель-арт (черновик, собирается tools/pixel_art/build.py)
  scripts/hud.gd       — счётчик печатей в хабе
  scenes/minigames/rhythm/ — ритм-игра Лени: rhythm.tscn/.gd; lenya_song.wav, lenya_chart.gd, sfx_*.wav
                         собираются tools/music/lenya_song.py (трек и карта нот из одной партитуры)
```

Целевая (переезжать постепенно, через редактор Godot — он обновит ссылки):

```
game/
  scenes/hub/          — хаб
  scenes/minigames/rhythm/ art/ cosplay/ quiz/ logic/
  scenes/ui/           — блокнот, меню, лидерборд
  scripts/             — общие скрипты, autoload'ы
  dialogue/            — разговоры: manya.gd, lenya.gd … (обычные GDScript-функции)
  art/  audio/music/  audio/sfx/  fonts/
```

## Пиксель-арт

- `rendering/textures/canvas_textures/default_texture_filter = Nearest` — спрайты не размываются.
- `rendering/2d/snap/snap_2d_transforms_to_pixel = true` — без дрожания на субпикселях.
- Stretch mode `canvas_items`: спрайты масштабируются блочно, а текст диалогов и UI остаётся чётким (по решению — диалоги не обязаны быть пиксельными).
- **Базовое разрешение 640×360** (решено 2026-10-14), `scale_mode = integer`: на 1080p ровно ×3, на 720p ×2. Окно при запуске — 1280×720. Все координаты и размеры шрифтов — в этих 640×360. Шрифт UI: 10–16 px (Nunito по умолчанию, Montserrat для заголовков — см. «Фирменный стиль»).
- Мини-игры строить на контейнерах и якорях, а не на абсолютных координатах.

## Спрайты и хаб

- Пиксель-арт собирает `python tools/pixel_art/build.py` (нужен Pillow) в `game/art/`. Сборка **перезаписывает** PNG: перерисованный вручную спрайт сначала убрать из `build.py`.
- **Персонажи — 64×64** (как спрайты дизайнера): маскоты, игрок, гости. Игрок: `SPRITE_OFFSET = (0, -18)`.
- **Точка ног — низ спрайта.** Маскот: низ картинки на `BODY_RADIUS` (16 px) ниже центра NPC. Игрок: `SPRITE_OFFSET` в `scripts/character_body_2d.gd`. Декорации: `centered = false`, `offset = (-w/2, -h)`. При перерисовке размеры менять можно, но ноги должны оставаться на нижнем крае.
- Спрайт маскота в хабе: `mascot_npc.gd` сам грузит `art/characters/<mascot>.png`. Нет файла — рисуется только зона (так у главной сцены).
- Хаб (`world.tscn`) сортируется по Y (`y_sort_enabled`): декорации — в узле `Decor`, плитка — `Ground` (`z_index = -10`), круги зон — `z_index = -1`. Края карты — стены в `collisions` и `limit_*` у камеры.

## Фирменный стиль

По брендбуку `assets/Brandbook.pptx` (2026-10-14):

- **`scripts/brand.gd`** (`class_name Brand`) — палитра (`Brand.ORANGE`, `SALMON`, `BROWN`, `BLUE`, `RED`, `GREEN`, производные `BROWN_DEEP`, `CREAM`), цвет выделения `Brand.SELECTED`, шрифты `Brand.BODY_FONT` / `Brand.HEADER_FONT`, `Brand.panel_style()` — тёмная панель с оранжевой рамкой. Новые цвета брать отсюда, а не писать `Color(...)` руками.
- **Тема проекта `ui/theme.tres`** (`gui/theme/custom`): шрифт по умолчанию — Nunito SemiBold 12. Заголовок — `label.theme_type_variation = &"HeaderLabel"` (Montserrat Bold).
- В `draw_string()` шрифт передаётся явно: `Brand.BODY_FONT` или `Brand.HEADER_FONT` (не `ThemeDB.fallback_font` — это шрифт движка, не наш).
- Фоны мини-игр — тёмный оттенок цвета маскота: `Brand.SALMON.darkened(0.65)` у Мани и т. д.

## Соглашения по именам

- Файлы и папки — английский `snake_case`: `rhythm_game.tscn`, `player.gd`.
- Узлы в сценах — `PascalCase`: `Player`, `HpBar`.
- Переменные и функции — `snake_case` (`hp`, `apply_damage()`), константы — `UPPER_SNAKE`.
- Никакой кириллицы и пробелов в именах файлов.
- **Регистр в `res://`-путях должен совпадать с именем файла буква в букву.** Windows прощает, экспорт и Linux — нет (см. BUG-001).

Известный техдолг по именам (переименовывать через редактор, не через проводник):
- `scripts/character_body_2d.gd` → `scripts/player.gd`;

## Управление (Input Map)

| Действие | Клавиши | Статус |
|---|---|---|
| `left` / `right` / `up` / `down` | стрелки, WASD | есть |
| `enter` (взаимодействие) | Enter, Space, E, Numpad Enter | есть |
| `notebook` (блокнот) | Tab | есть; Esc тоже закрывает; во время диалога не открывается |
| `restart` | R (удерживать 1 с) | есть, обрабатывает `GameState` |
| `lane_0` … `lane_3` (ритм-игра) | D, F, J, K | есть |
| `ui_accept` | Enter, Space, E, Numpad Enter | как `enter` (кнопки интерфейса); диалоги листаются по `enter` |
| `ui_cancel` (встроенное) | Esc | выход из мини-игры в хаб после поражения |

Клавиши в Input Map назначать через **physical keycode** — на фестивальных ПК будет русская раскладка.

## GameState (autoload)

`scripts/game_state.gd` хранит состояние текущего забега.

- `stamps` — пройденные зоны (`"manya"`, `"lenya"`, `"katya"`, `"moyto"`, `"sulus"`).
- `clues` — собранные улики; `add_stamp()` выдаёт улику автоматически, `give_clue()` — улику без печати (страница Сулуса в финале). Тексты — в `CLUES`, `has_clue()` проверяет именно `clues`.
- `clues_answering("where" | "who" | "why")` — сколько собранных улик отвечает на вопрос финала.
- `add_stamp(mascot)`, `can_open_finale()` (≥ 3 печатей), сигнал `stamp_added`.
- `secret_dialogues`, `mistakes`, `score_time()` = время + 15 с за ошибку.
- `go_to_minigame(path, player_pos)` / `return_to_hub()` — переходы; игрок возвращается туда, откуда ушёл.
- `met`, `mark_met()` / `has_met()` — с кем уже говорили (первые реплики).
- `has_secret()` / `add_secret_dialogue()` — секретные диалоги.
- `in_dialogue` — идёт диалог, игрок стоит (по сигналам `Dialogue.started` / `ended`).
- `MINIGAMES` — какие мини-игры готовы. Из диалога: `GameState.request_minigame("lenya")`, игра стартует после закрытия диалога.
- `request_finale()` — из диалога главной сцены, открывает `FINALE_SCENE`.
- `finale_ending` / `finale_why` — концовка, разгаданная на главной сцене. Пока `finale_ending` не пуст, за кулисами ждут маскоты и ракета открывается; `request_finale_summary()` (из `dialogue/backstage.gd`) после диалога возвращает в финал, тот сразу показывает итоги.
- `go_to_backstage()` — проход за кулисы из хаба; назад — `return_to_hub()`, игрок встаёт у занавеса.
- `finish_run()` — останавливает таймер (концовка); `secrets_required()` — сколько секретов нужно для «Идеального детектива».
- `go_to_title()` — сброс забега и титульный экран (по бездействию и после итогов финала). На титульном экране таймер забега стоит.
- Бездействие: `_input()` обнуляет счётчик при любой клавише/кнопке/заметном движении мыши; 50 с — предупреждение, 60 с — `go_to_title()`.
- `restart()` — сброс забега и возврат в хаб, вызывается удержанием R.

## Диалоги

Своя система, без плагинов (раньше был Dialogue Manager). Три части:

1. **Окно** — обычная сцена `scenes/ui/dialogue_box.tscn` (`class_name DialogueBox`): панель внизу, имя, текст, варианты. Две функции:
   - `await d.say("Маня", "Текст")` — реплика печатается (50 символов/с), ждёт Enter. Имя `""` — слова рассказчика.
   - `await d.ask("Маня", "Вопрос?", ["Да", "Потом"])` — после печати показывает варианты (↑↓ + Enter), возвращает номер.
   - Enter во время печати показывает реплику целиком, второй Enter листает. Пока окно открыто, ввод больше никому не идёт.
2. **Autoload `Dialogue`** (`scripts/dialogue.gd`): `Dialogue.start(скрипт, "функция")` создаёт объект скрипта диалога и вызывает функцию, передавая окно. Сигналы `started` / `ended` (по ним `GameState.in_dialogue`). Второй разговор поверх первого не открывается. `Dialogue.cancel()` обрывает разговор (вызывается в `GameState.reset_run()` — рестарт, автосброс).
3. **Разговоры** — `dialogue/<кто>.gd`, обычные функции: условия — `if GameState.has_stamp(...)`, действия — вызовы `GameState`, ветки — `return`. Порядок веток в `start`: знакомство → секретный разговор → после печати / до печати. Пример:

```gdscript
func start(d: DialogueBox) -> void:
	if GameState.has_stamp("manya"):
		await d.say("Маня", "Ой, солнышко, как продвигается расследование?")
		return
	if await d.ask("Маня", "Поможешь собрать?", ["Помогу!", "Потом"]) == 0:
		GameState.request_minigame("manya")
```

**Новый маскот в хабе:** инстанс `scenes/hub/mascot_npc.tscn`, в инспекторе задать `mascot`, `display_name`, `zone_name`, `color`, `dialogue_script` (файл из `dialogue/`) и `dialogue_start` (функция в нём).

**Гость или предмет:** тот же `mascot_npc.tscn` с `show_zone = false`, пустыми `display_name`/`zone_name` и своим `dialogue_start` (функция в `dialogue/guests.gd` или `dialogue/backstage.gd`). Спрайт берётся из `art/characters/<mascot>.png`, если он есть (гости — `guest_0…5`); у предметов спрайта нет, их рисует декорация рядом.

**Контракт мини-игры:** при победе вызвать `GameState.add_stamp("<маскот>")`, показать результат, по `enter` → `GameState.return_to_hub()`. Образец — `scenes/minigames/cosplay/cosplay.gd`.

**Ритм-игра и музыка.** Мелодию и ноты меняют в `tools/music/lenya_song.py` (`PHRASES`), потом `python tools/music/lenya_song.py` — перепишет `lenya_song.wav` и `lenya_chart.gd`. Руками `lenya_chart.gd` не править: ноты разъедутся с музыкой. Время песни берётся из позиции звука с поправкой на задержку вывода (`AudioServer.get_time_since_last_mix()`/`get_output_latency()`), без звуковой карты — по своему таймеру.

## Leaderboard (autoload)

`scripts/leaderboard.gd`: `entries` (топ-5, `{name, stamps, time, ending}`), `qualifies()`, `add()` → место или -1, `clear()`, `is_name_allowed()`, `format_lines()`. Сортировка: печати по убыванию, затем время (с штрафами) по возрастанию.

## Сохранения

- Лидерборд и достижения — `user://` (`ConfigFile`), бэкенда нет.
- Папка `user://` задана латиницей (`config/custom_user_dir_name="hoton_game"`), чтобы в пути не было кириллицы из имени проекта.
- Windows: `%APPDATA%\hoton_game\` (лидерборд — `leaderboard.cfg`).
- Linux: `~/.local/share/hoton_game/`.

## Экспорт

Пресеты — `game/export_presets.cfg` (в git): **Windows Desktop** и **Linux**, x86_64, `.pck` встроен в исполняемый файл, рядом — консольная обёртка для логов.

1. Шаблоны экспорта 4.7.2: Editor → Manage Export Templates → Download (1,3 ГБ). Ставятся в `%APPDATA%\Godot\export_templates\4.7.2.stable\`.
2. Сборка из командной строки (из папки `game/`):

```bash
godot --headless --path . --export-release "Windows Desktop" ../build/windows/HotonGame.exe
godot --headless --path . --export-release "Linux" ../build/linux/HotonGame.x86_64
```

3. Выход — в `build/` (в git не попадает): `HotonGame.exe` (для показа) и `HotonGame.console.exe` (то же, но с выводом в консоль). Для Linux — `HotonGame.x86_64` и `HotonGame.sh`.
4. **Проверять собранную игру, а не запуск из редактора** — дымовым тестом:

```bash
HotonGame.console.exe -- --smoke-test
```

Он по очереди открывает все сцены и печатает `SMOKE ok <сцена>` или `SMOKE FAIL <сцена>`, в конце `SMOKE TEST DONE`. Любой `SCRIPT ERROR` / `ERROR` до этой строки — проблема (утечки при выходе — нет). **Прогнать на фестивальном ПК** до открытия. Новую сцену — добавлять в `scripts/smoke_test.gd`.


## Открытые вопросы

- Иконка `.exe` — сейчас стандартная Godot. Своя иконка требует `rcedit` (Editor Settings → Export → Windows) и `application/modify_resources=true` в пресете.
