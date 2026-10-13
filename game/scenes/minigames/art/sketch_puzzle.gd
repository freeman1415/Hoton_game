extends Control
## Мини-игра Мани «Собери эскиз»: ветер перепутал кусочки «схемы праздника»,
## игрок меняет их местами, пока картинка не сложится. 90 секунд — печать.
## Собранная картинка и есть улика: ракета за сценой обведена кружком.
## Управление: стрелки — кусочек, Enter — взять, Enter на другом — поменять.

const MASCOT := "manya"
const TIME_LIMIT := 90.0
const GRID := 3
const TILE := 60
const GAP := 2
## Сколько кусочков минимум стоят не на месте после перемешивания.
const MIN_SHUFFLED := 6

const CURSOR_COLOR := Color(1.0, 0.85, 0.3)
const PICKED_COLOR := Color(1.0, 0.45, 0.2)

const PAPER := Color(0.96, 0.92, 0.82)
const INK := Color(0.3, 0.25, 0.2)

enum State { PLAYING, RESULT }

var state := State.PLAYING
## board[клетка] = номер кусочка; собрано, когда board[i] == i.
var board: Array[int] = []
var cursor := 0
var picked := -1
var moves := 0
var time_left := TIME_LIMIT
var won := false

var picture: ImageTexture
var manya_label: Label
var grid_view: Control
var timer_bar: ProgressBar
var info_label: Label


func _ready() -> void:
	picture = ImageTexture.create_from_image(draw_picture())
	build_ui()
	shuffle_board()
	update_info()


func _process(delta: float) -> void:
	if state != State.PLAYING:
		return
	time_left -= delta
	timer_bar.value = time_left
	if time_left <= 0.0:
		finish(false)


func _unhandled_input(event: InputEvent) -> void:
	# echo — автоповтор зажатой клавиши, не считаем
	if event is InputEventKey and event.echo:
		return
	match state:
		State.PLAYING:
			if event.is_action_pressed("up"):
				move_cursor(0, -1)
			elif event.is_action_pressed("down"):
				move_cursor(0, 1)
			elif event.is_action_pressed("left"):
				move_cursor(-1, 0)
			elif event.is_action_pressed("right"):
				move_cursor(1, 0)
			elif event.is_action_pressed("enter"):
				press()
		State.RESULT:
			if event.is_action_pressed("enter"):
				if won:
					GameState.return_to_hub()
				else:
					get_tree().reload_current_scene()
			elif event.is_action_pressed("ui_cancel") and not won:
				GameState.return_to_hub()


func shuffle_board() -> void:
	board.clear()
	for i in GRID * GRID:
		board.append(i)
	while misplaced() < MIN_SHUFFLED:
		board.shuffle()


func misplaced() -> int:
	var count := 0
	for i in board.size():
		if board[i] != i:
			count += 1
	return count


func move_cursor(dx: int, dy: int) -> void:
	var x := (cursor % GRID + dx + GRID) % GRID
	var y := (cursor / GRID + dy + GRID) % GRID
	cursor = y * GRID + x
	grid_view.queue_redraw()


func press() -> void:
	if picked == -1:
		picked = cursor
	elif picked == cursor:
		picked = -1
	else:
		var tile := board[picked]
		board[picked] = board[cursor]
		board[cursor] = tile
		picked = -1
		moves += 1
		if misplaced() == 0:
			finish(true)
			return
	update_info()
	grid_view.queue_redraw()


func update_info() -> void:
	if picked == -1:
		manya_label.text = "Маня: Ой, ветер всё перепутал! Собери мою схему, солнышко!"
	else:
		manya_label.text = "Маня: Куда положим этот кусочек?"
	info_label.text = "Ходов: %d    Стрелки — кусочек   Enter — взять / поменять" % moves


func finish(is_win: bool) -> void:
	state = State.RESULT
	won = is_win
	picked = -1
	timer_bar.hide()
	grid_view.queue_redraw()
	if won:
		GameState.add_stamp(MASCOT)
		manya_label.text = "Маня: Ой, получилось! Вот она, моя схема праздника. Держи печать!\nУлика: %s" % \
			GameState.CLUES[MASCOT].title
		info_label.text = "Ходов: %d    Enter — вернуться на фестиваль" % moves
	else:
		manya_label.text = "Маня: Ой, время вышло! Ничего, давай ещё разок."
		info_label.text = "Enter — ещё раз    Esc — вернуться на фестиваль"


func draw_grid() -> void:
	# Собранная картинка — без щелей, с подписью у ракеты
	var gap := 0 if won else GAP
	for i in board.size():
		var tile := board[i]
		var src := Rect2((tile % GRID) * TILE, (tile / GRID) * TILE, TILE, TILE)
		var dst := Rect2((i % GRID) * (TILE + gap), (i / GRID) * (TILE + gap), TILE, TILE)
		grid_view.draw_texture_rect_region(picture, dst, src)
		if i == picked:
			grid_view.draw_rect(dst, Color(1, 1, 1, 0.3))
			grid_view.draw_rect(dst.grow(-1), PICKED_COLOR, false, 2.0)
		if i == cursor and state == State.PLAYING:
			grid_view.draw_rect(dst.grow(1), CURSOR_COLOR, false, 2.0)
	if won:
		grid_view.draw_string(ThemeDB.fallback_font, Vector2(122, 61), "для С.",
			HORIZONTAL_ALIGNMENT_LEFT, -1, 10, Color(0.8, 0.1, 0.1))


## Эскиз Мани 180×180: схема фестиваля, ракета за сценой обведена красным.
## У каждого кусочка своя заметная деталь, дорожки связывают соседние кусочки.
## Заглушка — заменить нарисованным от руки пиксель-артом.
func draw_picture() -> Image:
	var size := GRID * TILE
	var img := Image.create_empty(size, size, false, Image.FORMAT_RGBA8)
	img.fill(PAPER)

	# Дорожки: от сцены вниз к воротам и поперёк через всю карту
	img.fill_rect(Rect2i(0, 84, size, 12), Color(0.8, 0.68, 0.5))
	img.fill_rect(Rect2i(84, 50, 12, size - 50), Color(0.8, 0.68, 0.5))

	# (0,0) солнце
	fill_circle(img, Vector2i(30, 28), 13, Color(1.0, 0.8, 0.2))
	for ray in 8:
		var dir := Vector2.RIGHT.rotated(ray * TAU / 8)
		for r in range(16, 22):
			var p := Vector2i(Vector2(30, 28) + dir * r)
			img.fill_rect(Rect2i(p, Vector2i(2, 2)), Color(1.0, 0.7, 0.1))

	# (1,0) сцена: занавес и пол
	img.fill_rect(Rect2i(64, 14, 52, 36), Color(0.55, 0.12, 0.15))
	img.fill_rect(Rect2i(68, 18, 44, 24), Color(0.85, 0.3, 0.3))
	img.fill_rect(Rect2i(88, 18, 4, 24), Color(0.55, 0.12, 0.15))
	img.fill_rect(Rect2i(62, 46, 56, 6), Color(0.45, 0.3, 0.2))

	# (2,0) ракета за сценой — обведена кружком
	img.fill_rect(Rect2i(142, 18, 12, 28), Color(0.75, 0.75, 0.8))
	fill_triangle(img, Vector2i(148, 6), Vector2i(141, 18), Vector2i(155, 18), Color(0.85, 0.2, 0.2))
	fill_triangle(img, Vector2i(142, 34), Vector2i(135, 48), Vector2i(142, 48), Color(0.85, 0.2, 0.2))
	fill_triangle(img, Vector2i(154, 34), Vector2i(161, 48), Vector2i(154, 48), Color(0.85, 0.2, 0.2))
	fill_circle(img, Vector2i(148, 26), 3, Color(0.4, 0.65, 0.95))
	draw_ring(img, Vector2i(148, 28), 25, 2, Color(0.85, 0.1, 0.1))

	# (0,1) деревья
	for x in [14, 40]:
		img.fill_rect(Rect2i(x - 2, 70, 4, 12), Color(0.45, 0.3, 0.2))
		fill_circle(img, Vector2i(x, 66), 10, Color(0.3, 0.6, 0.3))
	fill_circle(img, Vector2i(27, 108), 9, Color(0.35, 0.65, 0.35))

	# (2,1) лекторий: крыша и колонны
	fill_triangle(img, Vector2i(150, 62), Vector2i(128, 78), Vector2i(172, 78), Color(0.45, 0.5, 0.6))
	img.fill_rect(Rect2i(130, 78, 40, 4), Color(0.6, 0.65, 0.75))
	for x in [133, 143, 153, 163]:
		img.fill_rect(Rect2i(x, 82, 4, 15), Color(0.6, 0.65, 0.75))
	img.fill_rect(Rect2i(130, 97, 40, 16), Color(0.6, 0.65, 0.75))
	for x in [134, 146, 158]:
		img.fill_rect(Rect2i(x, 99, 6, 14), Color(0.4, 0.45, 0.55))

	# (0,2) арт-маркет: полосатые навесы
	for i in 2:
		var x := 6 + i * 26
		for s in 5:
			var stripe := Color(0.93, 0.55, 0.65) if s % 2 == 0 else Color(1, 1, 1)
			img.fill_rect(Rect2i(x + s * 4, 130, 4, 8), stripe)
		img.fill_rect(Rect2i(x, 138, 20, 14), Color(0.7, 0.5, 0.35))
		img.fill_rect(Rect2i(x + 4, 142, 5, 5), Color(0.3, 0.55, 0.9))
		img.fill_rect(Rect2i(x + 11, 142, 5, 5), Color(0.95, 0.8, 0.2))

	# (1,2) ворота-вход с флажками
	img.fill_rect(Rect2i(70, 140, 6, 36), Color(0.5, 0.35, 0.25))
	img.fill_rect(Rect2i(104, 140, 6, 36), Color(0.5, 0.35, 0.25))
	img.fill_rect(Rect2i(70, 134, 40, 7), Color(0.5, 0.35, 0.25))
	for i in 5:
		var x := 72 + i * 8
		var flag: Color = [Color(0.9, 0.3, 0.3), Color(0.3, 0.6, 0.9), Color(0.95, 0.8, 0.2)][i % 3]
		fill_triangle(img, Vector2i(x, 141), Vector2i(x + 6, 141), Vector2i(x + 3, 148), flag)

	# (2,2) цирковой шатёр Мойто
	for s in 6:
		var stripe := Color(0.9, 0.2, 0.25) if s % 2 == 0 else Color(0.98, 0.85, 0.3)
		fill_triangle(img, Vector2i(150, 128), Vector2i(126 + s * 8, 168), Vector2i(134 + s * 8, 168), stripe)
	img.fill_rect(Rect2i(149, 120, 2, 8), INK)
	fill_triangle(img, Vector2i(151, 120), Vector2i(151, 126), Vector2i(158, 123), Color(0.3, 0.6, 0.9))

	# Рамка листа
	for i in 2:
		img.fill_rect(Rect2i(i, i, size - i * 2, 1), INK)
		img.fill_rect(Rect2i(i, size - 1 - i, size - i * 2, 1), INK)
		img.fill_rect(Rect2i(i, i, 1, size - i * 2), INK)
		img.fill_rect(Rect2i(size - 1 - i, i, 1, size - i * 2), INK)
	return img


func fill_circle(img: Image, center: Vector2i, radius: int, color: Color) -> void:
	for y in range(-radius, radius + 1):
		for x in range(-radius, radius + 1):
			if x * x + y * y <= radius * radius:
				set_pixel_safe(img, center + Vector2i(x, y), color)


func draw_ring(img: Image, center: Vector2i, radius: int, width: int, color: Color) -> void:
	var inner := (radius - width) * (radius - width)
	for y in range(-radius, radius + 1):
		for x in range(-radius, radius + 1):
			var d := x * x + y * y
			if d <= radius * radius and d > inner:
				set_pixel_safe(img, center + Vector2i(x, y), color)


func fill_triangle(img: Image, a: Vector2i, b: Vector2i, c: Vector2i, color: Color) -> void:
	var points := PackedVector2Array([a, b, c])
	var top := mini(a.y, mini(b.y, c.y))
	var bottom := maxi(a.y, maxi(b.y, c.y))
	var left := mini(a.x, mini(b.x, c.x))
	var right := maxi(a.x, maxi(b.x, c.x))
	for y in range(top, bottom + 1):
		for x in range(left, right + 1):
			if Geometry2D.is_point_in_polygon(Vector2(x, y) + Vector2(0.5, 0.5), points):
				set_pixel_safe(img, Vector2i(x, y), color)


func set_pixel_safe(img: Image, p: Vector2i, color: Color) -> void:
	if p.x >= 0 and p.y >= 0 and p.x < img.get_width() and p.y < img.get_height():
		img.set_pixelv(p, color)


func build_ui() -> void:
	var background := ColorRect.new()
	background.color = Color(0.3, 0.18, 0.22)
	background.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(background)

	var box := VBoxContainer.new()
	box.set_anchors_preset(Control.PRESET_FULL_RECT)
	box.alignment = BoxContainer.ALIGNMENT_CENTER
	box.add_theme_constant_override("separation", 8)
	add_child(box)

	manya_label = make_label(box, 13)

	var row := HBoxContainer.new()
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", 24)
	box.add_child(row)

	grid_view = Control.new()
	grid_view.custom_minimum_size = Vector2.ONE * (GRID * TILE + (GRID - 1) * GAP)
	grid_view.draw.connect(draw_grid)
	row.add_child(grid_view)

	# Образец в уменьшенном виде — чтобы собрать за минуту без мучений
	var sample_box := VBoxContainer.new()
	sample_box.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_child(sample_box)
	make_label(sample_box, 10).text = "Как было:"
	var sample := TextureRect.new()
	sample.texture = picture
	sample.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	sample.custom_minimum_size = Vector2.ONE * GRID * TILE / 2
	sample.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	sample_box.add_child(sample)

	timer_bar = ProgressBar.new()
	timer_bar.max_value = TIME_LIMIT
	timer_bar.value = TIME_LIMIT
	timer_bar.show_percentage = false
	timer_bar.custom_minimum_size = Vector2(200, 6)
	timer_bar.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	box.add_child(timer_bar)

	info_label = make_label(box, 10)


func make_label(parent: Node, font_size: int) -> Label:
	var label := Label.new()
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.custom_minimum_size.x = 200
	label.add_theme_font_size_override("font_size", font_size)
	parent.add_child(label)
	return label
