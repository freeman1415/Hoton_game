# docs/TECH.md — техническая спецификация

## Стек

- **Godot 4.7**, GDScript. Открывать проект только этой версией — более старая не откроет, более новая может молча переконвертировать сцены.
- Плагин: Dialogue Manager 4.1.0 (Nathan Hoad, MIT) — autoload `DialogueManager`, файлы диалогов `*.dialogue`.
- ПК (Windows, Linux), экспорт `.exe` / `.x86_64`.
- Рендер сейчас: Forward+ / D3D12 (`project.godot` → `[rendering]`). Решение по смене — см. «Открытые вопросы».

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
godot --headless --path game --quit-after 180 res://ritm/main.tscn   # прогнать сцену ~3 с
```

## Структура `game/`

Текущая:

```
game/
  project.godot        — главная сцена: scenes/world.tscn
  addons/dialogue_manager/
  dialogue/           — по файлу на маскота: manya, lenya, katya, moyto, sulus
  scenes/world.tscn    — хаб: 5 зон маскотов, игрок, HUD печатей
  scenes/hub/mascot_npc.tscn — маскот в хабе (зона, заглушка-кружок, разговор по Enter)
  scenes/minigames/quiz/ — викторина Мойто
  scenes/minigames/cosplay/ — «Собери образ» Кати
  scenes/test.tscn     — тестовая, удалить
  scripts/character_body_2d.gd — движение игрока, возврат на место после мини-игры
  scripts/game_state.gd — autoload `GameState`: печати, улики, таймер, рестарт по R
  scripts/hud.gd       — счётчик печатей в хабе
  ritm/                — ритм-игра (Леня): main.tscn, main.gd, note.tscn, note.gd, музыка
```

Целевая (переезжать постепенно, через редактор Godot — он обновит ссылки):

```
game/
  scenes/hub/          — хаб
  scenes/minigames/rhythm/ art/ cosplay/ quiz/ logic/
  scenes/ui/           — блокнот, меню, лидерборд
  scripts/             — общие скрипты, autoload'ы
  dialogue/            — по файлу на маскота: manya.dialogue …
  art/  audio/music/  audio/sfx/  fonts/
```

## Пиксель-арт

- `rendering/textures/canvas_textures/default_texture_filter = Nearest` — спрайты не размываются.
- `rendering/2d/snap/snap_2d_transforms_to_pixel = true` — без дрожания на субпикселях.
- Stretch mode `canvas_items`: спрайты масштабируются блочно, а текст диалогов и UI остаётся чётким (по решению — диалоги не обязаны быть пиксельными).
- Мини-игры строить на контейнерах и якорях, без абсолютных координат: базовое разрешение ещё не выбрано (см. «Открытые вопросы»).

## Соглашения по именам

- Файлы и папки — английский `snake_case`: `rhythm_game.tscn`, `player.gd`.
- Узлы в сценах — `PascalCase`: `Player`, `HpBar`.
- Переменные и функции — `snake_case` (`hp`, `apply_damage()`), константы — `UPPER_SNAKE`.
- Никакой кириллицы и пробелов в именах файлов.
- **Регистр в `res://`-путях должен совпадать с именем файла буква в букву.** Windows прощает, экспорт и Linux — нет (см. BUG-001).

Известный техдолг по именам (переименовывать через редактор, не через проводник):
- папка `ritm/` → `scenes/minigames/rhythm/`;
- `scripts/character_body_2d.gd` → `scripts/player.gd`;

## Управление (Input Map)

| Действие | Клавиши | Статус |
|---|---|---|
| `left` / `right` / `up` / `down` | стрелки, WASD | есть |
| `enter` (взаимодействие) | Enter, Space, E, Numpad Enter | есть |
| `notebook` (блокнот) | Tab | действие есть, блокнота ещё нет |
| `restart` | R (удерживать 1 с) | есть, обрабатывает `GameState` |
| `lane_0` … `lane_3` (ритм-игра) | D, F, J, K | есть |
| `ui_accept` (листать диалог) | Enter, Space, E, Numpad Enter | переопределено, чтобы совпадало с `enter` |
| `ui_cancel` (встроенное) | Esc | выход из мини-игры в хаб после поражения |

Клавиши в Input Map назначать через **physical keycode** — на фестивальных ПК будет русская раскладка.

## GameState (autoload)

`scripts/game_state.gd` хранит состояние текущего забега.

- `stamps` — пройденные зоны (`"manya"`, `"lenya"`, `"katya"`, `"moyto"`, `"sulus"`). Улика выдаётся вместе с печатью, тексты улик лежат в `CLUES`.
- `clues_answering("where" | "who" | "why")` — сколько собранных улик отвечает на вопрос финала.
- `add_stamp(mascot)`, `can_open_finale()` (≥ 3 печатей), сигнал `stamp_added`.
- `secret_dialogues`, `mistakes`, `score_time()` = время + 15 с за ошибку.
- `go_to_minigame(path, player_pos)` / `return_to_hub()` — переходы; игрок возвращается туда, откуда ушёл.
- `met`, `mark_met()` / `has_met()` — с кем уже говорили (первые реплики).
- `has_secret()` / `add_secret_dialogue()` — секретные диалоги.
- `in_dialogue` — идёт диалог, игрок стоит (по сигналам `DialogueManager`).
- `MINIGAMES` — какие мини-игры готовы. Из диалога: `do GameState.request_minigame("lenya")`, игра стартует после закрытия диалога.
- `restart()` — сброс забега и возврат в хаб, вызывается удержанием R.

**Диалоги** (`dialogue/*.dialogue`) обращаются к `GameState` по имени: `if GameState.has_stamp("lenya")`. Порядок веток в `~ start`: знакомство → секретный диалог → после печати / до печати.

**Новый маскот в хабе:** инстанс `scenes/hub/mascot_npc.tscn`, в инспекторе задать `mascot`, `display_name`, `zone_name`, `color`, `dialogue_resource`.

**Контракт мини-игры:** при победе вызвать `GameState.add_stamp("<маскот>")`, показать результат, по `enter` → `GameState.return_to_hub()`. Образец — `ritm/main.gd`.

## Сохранения

- Лидерборд и достижения — `user://` (`ConfigFile`), бэкенда нет.
- Windows: `%APPDATA%\Godot\app_userdata\game-peakit\`.

## Экспорт

1. Editor → Manage Export Templates → скачать шаблоны 4.7.
2. Project → Export → пресеты Windows Desktop и Linux.
3. Выход — в `build/` (в git не попадает).
4. **Проверять экспортированную сборку, а не только запуск из редактора** (регистр путей, отсутствующие ресурсы).

## Открытые вопросы

- **Базовое разрешение для пиксель-арта.** Сейчас стоит Godot-умолчание 1152×648, а оно не делится нацело при масштабировании до 1920×1080. Предложение: 640×360 (×3 = 1080p, ×2 = 720p) + `window/stretch/scale_mode = integer`. Затронет координаты и размеры шрифтов в хабе и ритм-игре. Решить до того, как рисовать спрайты: от этого зависит их размер в пикселях.

- Название проекта в `project.godot` — `game-peakit`. Переименовать в `Hoton Game`? (Меняет путь `user://`.)
- Рендерер: Forward+ / D3D12 может не запуститься на слабом фестивальном ПК без нормальной видеокарты. Для 2D-игры безопаснее **Compatibility**. Решить до первого экспорта.
- `[physics] 3d/physics_engine="Jolt Physics"` для 2D-игры не нужен — можно убрать.
