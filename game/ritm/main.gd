extends Node2D

# Тут твоя карта нот: время (в секундах) и полоска
var chart = [

	{"time": 1.0, "lane": 0},
	{"time": 1.5, "lane": 1},
	{"time": 2.0, "lane": 2},
	{"time": 2.5, "lane": 3},
	{"time": 3.0, "lane": 0},
]
var note_scene = preload("res://ritm/note.tscn")

const MASCOT = "lenya"
const MAX_HP = 10
const HIT_WINDOW = 0.15
const MISS_Y = 350
const LANE_ACTIONS = ["lane_0", "lane_1", "lane_2", "lane_3"]

var hp = MAX_HP
var notes_left = 0       # сколько нот ещё не сыграно и не пропущено
var mistakes = 0
var finished = false     # игра закончилась — ждём выбора игрока
var won = false

var result_label: Label
## Своё время песни: трека пока нет (опенинг JoJo убран из репозитория,
## см. docs/ASSETS.md), а ноты должны падать и без музыки.
var clock = 0.0

func _ready():
	# Запускаем музыку, если трек назначен в $AudioStreamPlayer
	if $AudioStreamPlayer.stream:
		$AudioStreamPlayer.play()
	# Спавним все ноты из карты
	update_hp_bar()
	for n in chart:
		var note = note_scene.instantiate()
		note.hit_time = n.time
		note.lane = n.lane
		note.song = self     # нота спрашивает время песни через song_position()
		$Lanes.add_child(note)
	notes_left = chart.size()
	create_lane_hints()
	create_result_label()

## Текущая секунда песни: по треку, если он играет, иначе по своему таймеру.
func song_position():
	if $AudioStreamPlayer.playing:
		return $AudioStreamPlayer.get_playback_position()
	return clock

func _process(delta):
	if finished:
		return
	clock += delta
	for note in $Lanes.get_children():
		if note.position.y > MISS_Y and not note.is_queued_for_deletion():
			note.queue_free()
			print("Пропустил")
			mistakes += 1
			note_done()
			apply_hp(-1)

func _unhandled_input(event):
	if finished:
		handle_result_input(event)
		return
	# echo — автоповтор зажатой клавиши, его не считаем (BUG-002)
	if event is InputEventKey and event.echo:
		return
	for lane in LANE_ACTIONS.size():
		if event.is_action_pressed(LANE_ACTIONS[lane]):
			check_hit(lane)
			return

func check_hit(lane):
	var now = song_position()
	var best_note = null
	var best_diff = 999.0

	for note in $Lanes.get_children():
		if note.lane == lane and not note.is_queued_for_deletion():
			var diff = abs(note.hit_time - now)
			if diff < best_diff:
				best_diff = diff
				best_note = note

	# Если попал в окно 0.15 секунды — засчитываем
	if best_note and best_diff < HIT_WINDOW:
		best_note.queue_free()
		print("Хорошо", best_diff)
		note_done()
		apply_hp(1)
	else:
		print("Мимо")
		mistakes += 1
		apply_hp(-1)

func note_done():
	notes_left -= 1

func apply_hp(amount):
	hp = clamp(hp + amount, 0, MAX_HP)
	update_hp_bar()
	if hp < 1:
		finish(false)
	elif notes_left <= 0:
		finish(true)

func update_hp_bar():
	$HpBar.size.x = 20 * hp

func finish(is_win):
	if finished:
		return
	finished = true
	won = is_win
	$AudioStreamPlayer.stop()
	for note in $Lanes.get_children():
		note.queue_free()
	if won:
		GameState.add_stamp(MASCOT)
		var text = "Отлично! Леня ставит печать в блокнот.\nУлика: %s" % GameState.CLUES[MASCOT].title
		if mistakes == 0:
			text += "\nИдеальный ритм!"
		result_label.text = text + "\n\nEnter — вернуться на фестиваль"
	else:
		result_label.text = "Сбился с ритма…\n\nEnter — ещё раз    Esc — вернуться на фестиваль"
	result_label.show()

func handle_result_input(event):
	if event is InputEventKey and event.echo:
		return
	if event.is_action_pressed("enter"):
		if won:
			GameState.return_to_hub()
		else:
			get_tree().reload_current_scene()
	elif event.is_action_pressed("ui_cancel") and not won:
		GameState.return_to_hub()

# Подписи клавиш под дорожками: обучения нет, игрок должен понять сразу
func create_lane_hints():
	var keys = ["D", "F", "J", "K"]
	for lane in keys.size():
		var label = Label.new()
		label.text = keys[lane]
		label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		label.position = Vector2(220 + lane * 50, 310)
		label.size = Vector2(30, 20)
		label.add_theme_font_size_override("font_size", 14)
		add_child(label)

func create_result_label():
	var layer = CanvasLayer.new()
	add_child(layer)
	result_label = Label.new()
	result_label.set_anchors_preset(Control.PRESET_FULL_RECT)
	result_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	result_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	result_label.add_theme_font_size_override("font_size", 16)
	result_label.hide()
	layer.add_child(result_label)
