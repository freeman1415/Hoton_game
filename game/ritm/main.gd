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
var Hp = 10
func _ready():
	# Запускаем музыку
	$AudioStreamPlayer.play()
	# Спавним все ноты из карты
	$HpBar.size.x=120*Hp
	for n in chart:
		var note = note_scene.instantiate()
		note.hit_time = n.time
		note.lane = n.lane
		note.song = $AudioStreamPlayer     # <-- вот тут передаём музыку
		$Lanes.add_child(note)

func _process(delta):
	for note in $Lanes.get_children():
		if note.position.y > 700:
			note.queue_free()
			print("Пропустил")
			Health(-1)
func _input(event):
	# Проверяем нажатия клавиш
	if event is InputEventKey and event.pressed:
		var lane = -1
		if event.keycode == KEY_D: lane = 0
		if event.keycode == KEY_F: lane = 1
		if event.keycode == KEY_J: lane = 2
		if event.keycode == KEY_K: lane = 3
		if lane >= 0:
			check_hit(lane)

func check_hit(lane):
	var now = $AudioStreamPlayer.get_playback_position()
	var best_note = null
	var best_diff = 999.0
	
	for note in $Lanes.get_children():
		if note.lane == lane:
			var diff = abs(note.hit_time - now)
			if diff < best_diff:
				best_diff = diff
				best_note = note

	
	# Если попал в окно 0.15 секунды — засчитываем
	if best_note and best_diff < 0.15:
		best_note.queue_free()
		print("Хорошо",best_diff)
		Health(1)
	else:
		print("Мимо")
		Health(-1)

func Health(dmg):
	Hp = Hp+dmg
	$HpBar.size.x=120*Hp
	if Hp < 1:
		print("You lose")
		get_tree().change_scene_to_file("res://ritm/main.tscn")
	
	
