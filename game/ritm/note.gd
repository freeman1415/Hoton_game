extends ColorRect

var speed = 400.0        # скорость падения
var lane = 0             # какая полоска (0,1,2,3)
var hit_time = 0.0       # когда нота должна быть нажата
var song = null          # ссылка на музыкальный плеер

func _process(_delta):
	# Получаем текущую секунду песни
	var now = song.get_playback_position()
	# Считаем, сколько осталось до момента нажатия
	var left = hit_time - now
	# Ставим ноту по горизонтали (lane) и вертикали (по времени)
	position.x = 400 + lane * 100
	position.y = 600 - left * speed
	
	# Если нота улетела вниз — удаляем
	
		
