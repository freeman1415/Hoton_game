extends Control
## Заставка после «Начать» на титульном экране: завязка «Дела о пропавшей Капсуле».
## Кадры — рисунки дизайнера команды (art/cutscene/, 150×75, в игре ×3).
## Enter — дальше (во время печати — показать реплику целиком), Esc — пропустить.
## Потом — хаб, где Маня встречает гостя (dialogue/manya.gd).

const STAGE := preload("res://art/cutscene/intro_stage.png")
const RELICS := preload("res://art/cutscene/intro_relics.png")
const BACKGROUND := Color("#1b0c00")
const CHARS_PER_SECOND := 40.0
## Кадр 150×75 ×3 = 450×225
const FRAME_SCALE := 3.0
const FRAME_SIZE := Vector2(450, 225)
## Приближение к одной реликвии
const ZOOM := 2.0
const PAN_TIME := 0.8
const FADE_TIME := 0.4

## Слайды: картинка (null — чёрный экран), куда смотреть (точка на кадре 150×75,
## Vector2.ZERO — весь кадр) и текст.
var slides := [
	[STAGE, Vector2.ZERO, "Каждый год в Якутске проходит фестиваль «Хотон»."],
	[STAGE, Vector2.ZERO, "Гостей встречают маскоты: Маня, Леня, Катя, Мойто и Сулус."],
	[RELICS, Vector2.ZERO, "От каждого фестиваля остаётся реликвия."],
	[RELICS, Vector2(47, 40), "С «Ретро» — виниловая пластинка."],
	[RELICS, Vector2(75, 38), "С «Цирка» — красный клоунский нос."],
	[RELICS, Vector2(103, 40), "С «Космоса» — картонный шлем."],
	[RELICS, Vector2.ZERO, "Все реликвии хранятся в Капсуле Хотона. Её открывают в начале каждого фестиваля."],
	[null, Vector2.ZERO, "Но сегодня, за два часа до открытия фестиваля «Детектив», Капсула пропала…"],
	[null, Vector2.ZERO, "На подставке нашли только записку:\n«Настоящий детектив найдёт меня до открытия»."],
]

var _index := -1
var _typing := false
var _shown := 0.0
var _blip_chars := 0
var _frame: Control
var _picture: TextureRect
var _text: Label
var _hint: Label
var _tween: Tween


func _ready() -> void:
	_build_ui()
	_next()


func _process(delta: float) -> void:
	if not _typing:
		return
	_shown += CHARS_PER_SECOND * delta
	var count := int(_shown)
	if count > _blip_chars:
		_blip_chars = count
		var ch := _text.text.substr(count - 1, 1)
		if count % 2 == 0 and ch.strip_edges() != "":
			Sfx.voice("narrator")
	_text.visible_characters = count
	if count >= _text.text.length():
		_finish_typing()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.echo:
		return
	var is_cancel := event.is_action_pressed("ui_cancel")
	if not is_cancel and not event.is_action_pressed("enter"):
		return
	# До смены сцены: после change_scene_to_file() сцены уже нет в дереве
	# и get_viewport() вернёт null
	get_viewport().set_input_as_handled()
	if is_cancel:
		_done()
	elif _typing:
		_finish_typing()
	else:
		_next()


func _finish_typing() -> void:
	_typing = false
	_text.visible_characters = -1
	_hint.text = "Enter — дальше    Esc — пропустить"


func _next() -> void:
	_index += 1
	if _index >= slides.size():
		_done()
		return
	var slide: Array = slides[_index]
	var previous: Texture2D = _picture.texture
	var texture: Texture2D = slide[0]
	if _tween:
		_tween.kill()
	if texture != previous:
		# Новый кадр — через затемнение
		_tween = create_tween()
		_tween.tween_property(_frame, "modulate:a", 0.0, FADE_TIME if previous else 0.0)
		_tween.tween_callback(func() -> void:
			_picture.texture = texture
			_apply_focus(slide[1], false))
		if texture:
			_tween.tween_property(_frame, "modulate:a", 1.0, FADE_TIME)
	else:
		# Прошлое затемнение могли оборвать на полпути
		_frame.modulate.a = 1.0 if texture else 0.0
		_apply_focus(slide[1], true)
	_text.text = slide[2]
	_text.visible_characters = 0
	_shown = 0.0
	_blip_chars = 0
	_typing = true
	_hint.text = "Esc — пропустить"


## Показать весь кадр или приблизить точку focus (в пикселях кадра 150×75).
func _apply_focus(focus: Vector2, animate: bool) -> void:
	var zoom := 1.0 if focus == Vector2.ZERO else ZOOM
	var center := FRAME_SIZE / FRAME_SCALE / 2.0 if focus == Vector2.ZERO else focus
	var scale_to := Vector2.ONE * FRAME_SCALE * zoom
	var position_to := FRAME_SIZE / 2.0 - center * scale_to.x
	# Не выезжать за края кадра
	position_to = position_to.clamp(FRAME_SIZE - Vector2(150, 75) * scale_to.x, Vector2.ZERO)
	if not animate:
		_picture.scale = scale_to
		_picture.position = position_to
		return
	var pan := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	pan.tween_property(_picture, "scale", scale_to, PAN_TIME)
	pan.tween_property(_picture, "position", position_to, PAN_TIME)


func _done() -> void:
	set_process_unhandled_input(false)
	GameState.restart()


func _build_ui() -> void:
	var background := ColorRect.new()
	background.color = BACKGROUND
	background.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(background)

	_frame = Control.new()
	_frame.clip_contents = true
	_frame.set_anchors_preset(Control.PRESET_CENTER_TOP)
	_frame.offset_left = -FRAME_SIZE.x / 2.0
	_frame.offset_right = FRAME_SIZE.x / 2.0
	_frame.offset_top = 20
	_frame.offset_bottom = 20 + FRAME_SIZE.y
	_frame.modulate.a = 0.0
	add_child(_frame)

	_picture = TextureRect.new()
	_picture.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_frame.add_child(_picture)

	var panel := PanelContainer.new()
	panel.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	panel.offset_left = 40
	panel.offset_right = -40
	panel.offset_top = -100
	panel.offset_bottom = -12
	panel.add_theme_stylebox_override("panel", Brand.panel_style())
	add_child(panel)

	var box := VBoxContainer.new()
	panel.add_child(box)

	_text = Label.new()
	_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_text.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_text.add_theme_font_size_override("font_size", 14)
	_text.add_theme_color_override("font_color", Brand.CREAM)
	box.add_child(_text)

	_hint = Label.new()
	_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_hint.add_theme_font_size_override("font_size", 10)
	_hint.add_theme_color_override("font_color", Brand.MUTED)
	box.add_child(_hint)
