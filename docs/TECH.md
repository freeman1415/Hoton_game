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
  dialogue/main.dialogue — пока заглушка
  helpers/actionable.tscn — зона «нажми Enter → диалог»
  scenes/world.tscn    — хаб (игрок, тестовый NPC, вход в ритм-игру)
  scenes/test.tscn     — тестовая, удалить
  scripts/character_body_2d.gd — движение игрока
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

## Соглашения по именам

- Файлы и папки — английский `snake_case`: `rhythm_game.tscn`, `player.gd`.
- Узлы в сценах — `PascalCase`: `Player`, `HpBar`.
- Переменные и функции — `snake_case` (`hp`, `apply_damage()`), константы — `UPPER_SNAKE`.
- Никакой кириллицы и пробелов в именах файлов.
- **Регистр в `res://`-путях должен совпадать с именем файла буква в букву.** Windows прощает, экспорт и Linux — нет (см. BUG-001).

Известный техдолг по именам (переименовывать через редактор, не через проводник):
- папка `ritm/` → `scenes/minigames/rhythm/`;
- узел `RYTHM` → `RhythmEntrance`;
- `@export var dialogue_resourse` в `helpers/actionable.tscn` → `dialogue_resource` (после переименования переназначить ресурс в инспекторе у всех NPC);
- `scripts/character_body_2d.gd` → `scripts/player.gd`;
- функция `Health()` и переменная `Hp` в `ritm/main.gd` → `apply_hp()` / `hp`.

## Управление (Input Map)

| Действие | Клавиши | Статус |
|---|---|---|
| `left` / `right` / `up` / `down` | стрелки, WASD | есть |
| `enter` (взаимодействие) | Enter | есть; добавить Space, E, Numpad Enter |
| `notebook` (блокнот) | Tab | **нет**, добавить |
| `restart` | R (удерживать 1 с) | **нет**, добавить |
| ритм-игра, дорожки 0–3 | D, F, J, K | захардкожено в `ritm/main.gd`, вынести в Input Map |

Клавиши в Input Map назначать через **physical keycode** — на фестивальных ПК будет русская раскладка.

## Сохранения

- Лидерборд и достижения — `user://` (`ConfigFile`), бэкенда нет.
- Windows: `%APPDATA%\Godot\app_userdata\game-peakit\`.

## Экспорт

1. Editor → Manage Export Templates → скачать шаблоны 4.7.
2. Project → Export → пресеты Windows Desktop и Linux.
3. Выход — в `build/` (в git не попадает).
4. **Проверять экспортированную сборку, а не только запуск из редактора** (регистр путей, отсутствующие ресурсы).

## Открытые вопросы

- Название проекта в `project.godot` — `game-peakit`. Переименовать в `Hoton Game`? (Меняет путь `user://`.)
- Рендерер: Forward+ / D3D12 может не запуститься на слабом фестивальном ПК без нормальной видеокарты. Для 2D-игры безопаснее **Compatibility**. Решить до первого экспорта.
- `[physics] 3d/physics_engine="Jolt Physics"` для 2D-игры не нужен — можно убрать.
