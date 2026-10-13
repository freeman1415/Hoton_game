extends Node
## Состояние текущего забега: печати, улики, секретные диалоги, таймер.
## Autoload `GameState`. Сбрасывается через reset_run().

signal stamp_added(mascot: String)
signal run_reset

const HUB_SCENE := "res://scenes/world.tscn"
const FINALE_SCENE := "res://scenes/finale/finale.tscn"
const STAMPS_FOR_FINALE := 3
const RESTART_HOLD_TIME := 1.0
const MISTAKE_PENALTY := 15.0

## Маскоты в порядке отображения в блокноте.
const MASCOTS := ["manya", "lenya", "katya", "moyto", "sulus"]

const MASCOT_INFO := {
	"manya": {"name": "Маня", "zone": "Арт-маркет"},
	"lenya": {"name": "Леня", "zone": "Музыкальная сцена"},
	"katya": {"name": "Катя", "zone": "Косплей-дефиле"},
	"moyto": {"name": "Мойто", "zone": "Конкурсы"},
	"sulus": {"name": "Сулус", "zone": "Лекторий"},
}

## Сколько всего секретных диалогов (см. docs/GAME.md).
const SECRET_DIALOGUES_TOTAL := 5

## Улики: на какой вопрос финала отвечают (where / who / why). См. docs/GAME.md.
const CLUES := {
	"manya": {"title": "Эскиз «схема праздника»", "answers": ["where"],
		"text": "Карта фестиваля. Ракета за сценой обведена кружком, подпись «для С.»"},
	"lenya": {"title": "Партитура с шифром", "answers": ["where"],
		"text": "Ноты складываются в буквы: Р-А-К-Е-Т-А."},
	"katya": {"title": "Фото с репетиции дефиле", "answers": ["where", "who"],
		"text": "На заднем плане кто-то в картонном шлеме, с рогами и в фартуке, несёт сундучок за сцену."},
	"moyto": {"title": "Записка-загадка", "answers": ["who"],
		"text": "«Что главное для детектива?» Почерк крупный, с кляксой."},
	"sulus": {"title": "Страница лекции", "answers": ["who", "why"],
		"text": "«Как придумать хорошую загадку: 1) спрячь предмет на виду; 2) оставь подсказки у друзей…» Тот же почерк с кляксой."},
}

## Мини-игры по маскотам. Кого нет в списке — у того мини-игра ещё не готова.
const MINIGAMES := {
	"lenya": "res://ritm/main.tscn",
	"katya": "res://scenes/minigames/cosplay/cosplay.tscn",
	"moyto": "res://scenes/minigames/quiz/quiz.tscn",
}

var stamps: Array[String] = []
## Собранные улики. Обычно приходят вместе с печатью; страницу лекции Сулус
## может отдать в финале сам, если его зона не готова (см. docs/GAME.md).
var clues: Array[String] = []
## С кем игрок уже поговорил в этом забеге.
var met: Array[String] = []
var secret_dialogues: Array[String] = []
var mistakes := 0
var run_time := 0.0
var run_active := false

## Где стоял игрок в хабе перед уходом в мини-игру.
var hub_return_position = null

## Идёт диалог — игрок не ходит.
var in_dialogue := false
## Мини-игра, которую попросили запустить из диалога; стартует, когда диалог закроется.
var pending_minigame := ""

var _restart_held := 0.0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	DialogueManager.dialogue_started.connect(_on_dialogue_started)
	DialogueManager.dialogue_ended.connect(_on_dialogue_ended)
	reset_run()


func _process(delta: float) -> void:
	if run_active:
		run_time += delta

	if Input.is_action_pressed("restart"):
		_restart_held += delta
		if _restart_held >= RESTART_HOLD_TIME:
			_restart_held = 0.0
			restart()
	else:
		_restart_held = 0.0


func reset_run() -> void:
	stamps.clear()
	clues.clear()
	met.clear()
	secret_dialogues.clear()
	in_dialogue = false
	pending_minigame = ""
	mistakes = 0
	run_time = 0.0
	run_active = true
	hub_return_position = null
	run_reset.emit()


## Полный рестарт забега с возвратом в хаб.
func restart() -> void:
	reset_run()
	get_tree().paused = false
	get_tree().change_scene_to_file(HUB_SCENE)


func add_stamp(mascot: String) -> void:
	if mascot in stamps:
		return
	stamps.append(mascot)
	give_clue(mascot)
	stamp_added.emit(mascot)


func has_stamp(mascot: String) -> bool:
	return mascot in stamps


func stamp_count() -> int:
	return stamps.size()


func can_open_finale() -> bool:
	return stamps.size() >= STAMPS_FOR_FINALE


func give_clue(mascot: String) -> void:
	if not mascot in clues:
		clues.append(mascot)


func has_clue(mascot: String) -> bool:
	return mascot in clues


## Сколько собранных улик отвечает на вопрос: "where", "who" или "why".
func clues_answering(question: String) -> int:
	var count := 0
	for mascot in clues:
		if question in CLUES[mascot].answers:
			count += 1
	return count


func mark_met(mascot: String) -> void:
	if not mascot in met:
		met.append(mascot)


func has_met(mascot: String) -> bool:
	return mascot in met


func has_secret(id: String) -> bool:
	return id in secret_dialogues


func add_secret_dialogue(id: String) -> void:
	if not id in secret_dialogues:
		secret_dialogues.append(id)


## Сколько секретных диалогов нужно для «Идеального детектива».
## Без зоны Сулуса страницу лекции до финала не получить, а значит
## и секрет Мойто про почерк недоступен.
func secrets_required() -> int:
	return SECRET_DIALOGUES_TOTAL if has_minigame("sulus") else SECRET_DIALOGUES_TOTAL - 1


## Забег окончен (концовка) — таймер больше не идёт.
func finish_run() -> void:
	run_active = false


func add_mistake() -> void:
	mistakes += 1


## Время для лидерборда: реальное + штраф за ошибки в финале.
func score_time() -> float:
	return run_time + mistakes * MISTAKE_PENALTY


func has_minigame(mascot: String) -> bool:
	return MINIGAMES.has(mascot)


## Вызывается из диалога: `do GameState.request_minigame("lenya")`.
func request_minigame(mascot: String) -> void:
	pending_minigame = mascot


## Вызывается из диалога главной сцены: `do GameState.request_finale()`.
func request_finale() -> void:
	pending_minigame = "finale"


func start_minigame(mascot: String) -> void:
	var player := get_tree().current_scene.get_node_or_null("Player") as Node2D
	var player_position: Vector2 = player.global_position if player else Vector2.ZERO
	var scene_path: String = FINALE_SCENE if mascot == "finale" else MINIGAMES[mascot]
	go_to_minigame(scene_path, player_position)


func _on_dialogue_started(_resource: DialogueResource) -> void:
	in_dialogue = true


func _on_dialogue_ended(_resource: DialogueResource) -> void:
	in_dialogue = false
	if pending_minigame != "":
		var mascot := pending_minigame
		pending_minigame = ""
		start_minigame.call_deferred(mascot)


func go_to_minigame(scene_path: String, player_position: Vector2) -> void:
	hub_return_position = player_position
	get_tree().change_scene_to_file(scene_path)


func return_to_hub() -> void:
	get_tree().change_scene_to_file(HUB_SCENE)
