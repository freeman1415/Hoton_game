extends Control
## Мини-игра Кати «Собери образ»: Катя называет тему, игрок собирает костюм
## из трёх деталей. Три образа за минуту — печать.
## Управление: ↑↓ — деталь, ←→ — вариант, Enter — показать Кате.

const MASCOT := "katya"
const TIME_LIMIT := 60.0
const FEEDBACK_TIME := 1.5

const SELECTED_COLOR := Color(1.0, 0.85, 0.3)
const NORMAL_COLOR := Color(1, 1, 1)

## Темы прошлых фестивалей. Детали «детектива» — ловушка, его в заказах нет.
const THEMES := {
	"retro": {"name": "Ретро", "order": "Хочу ретро! Как на дискотеке восьмидесятых!"},
	"circus": {"name": "Цирк", "order": "Хочу цирк! Чтобы все улыбались!"},
	"space": {"name": "Космос", "order": "Хочу космос! Как на нашем общем фото!"},
}

const SLOTS := [
	{"name": "Голова", "items": [
		{"name": "Кудрявый парик", "theme": "retro", "color": Color(0.85, 0.45, 0.2)},
		{"name": "Клоунский колпак", "theme": "circus", "color": Color(0.9, 0.25, 0.3)},
		{"name": "Картонный шлем", "theme": "space", "color": Color(0.75, 0.75, 0.8)},
		{"name": "Шляпа детектива", "theme": "detective", "color": Color(0.45, 0.35, 0.25)},
	]},
	{"name": "Костюм", "items": [
		{"name": "Яркая куртка", "theme": "retro", "color": Color(0.95, 0.35, 0.75)},
		{"name": "Костюм в горошек", "theme": "circus", "color": Color(0.95, 0.85, 0.2)},
		{"name": "Скафандр из картона", "theme": "space", "color": Color(0.85, 0.85, 0.85)},
		{"name": "Плащ детектива", "theme": "detective", "color": Color(0.6, 0.5, 0.35)},
	]},
	{"name": "Аксессуар", "items": [
		{"name": "Кассетный плеер", "theme": "retro", "color": Color(0.3, 0.3, 0.35)},
		{"name": "Красный нос", "theme": "circus", "color": Color(1.0, 0.1, 0.1)},
		{"name": "Ракета-рюкзак", "theme": "space", "color": Color(0.3, 0.55, 0.95)},
		{"name": "Лупа", "theme": "detective", "color": Color(0.55, 0.8, 0.9)},
	]},
]

enum State { PLAYING, FEEDBACK, RESULT }

var state := State.PLAYING
var orders: Array = []        # темы по порядку
var order_index := 0
var choice := [0, 0, 0]       # выбранный вариант в каждом слоте
var selected_slot := 0
var time_left := TIME_LIMIT
var feedback_left := 0.0
var mistakes := 0
var won := false

var katya_label: Label
var slot_labels: Array[Label] = []
var timer_bar: ProgressBar
var info_label: Label
var mannequin: Control


func _ready() -> void:
	build_ui()
	orders = THEMES.keys()
	orders.shuffle()
	start_order()


func _process(delta: float) -> void:
	if state == State.RESULT:
		return
	time_left -= delta
	timer_bar.value = time_left
	if time_left <= 0.0:
		finish(false)
		return
	if state == State.FEEDBACK:
		feedback_left -= delta
		if feedback_left <= 0.0:
			next_order()


func _unhandled_input(event: InputEvent) -> void:
	# echo — автоповтор зажатой клавиши, не считаем
	if event is InputEventKey and event.echo:
		return
	match state:
		State.PLAYING:
			if event.is_action_pressed("up"):
				select_slot((selected_slot + SLOTS.size() - 1) % SLOTS.size())
			elif event.is_action_pressed("down"):
				select_slot((selected_slot + 1) % SLOTS.size())
			elif event.is_action_pressed("left"):
				change_item(-1)
			elif event.is_action_pressed("right"):
				change_item(1)
			elif event.is_action_pressed("enter"):
				submit()
		State.RESULT:
			if event.is_action_pressed("enter"):
				if won:
					GameState.return_to_hub()
				else:
					get_tree().reload_current_scene()
			elif event.is_action_pressed("ui_cancel") and not won:
				GameState.return_to_hub()


func start_order() -> void:
	state = State.PLAYING
	var order_theme: Dictionary = THEMES[orders[order_index]]
	katya_label.text = "Катя: %s" % order_theme.order
	info_label.text = "Образ %d из %d    ↑↓ — деталь   ←→ — вариант   Enter — показать Кате" % [
		order_index + 1, orders.size()]
	# Каждый образ начинаем с перемешанного манекена
	for i in SLOTS.size():
		choice[i] = randi() % SLOTS[i].items.size()
	select_slot(0)


func select_slot(i: int) -> void:
	selected_slot = i
	update_slots()


func change_item(step: int) -> void:
	var count: int = SLOTS[selected_slot].items.size()
	choice[selected_slot] = (choice[selected_slot] + step + count) % count
	update_slots()


func current_item(slot: int) -> Dictionary:
	return SLOTS[slot].items[choice[slot]]


func update_slots() -> void:
	for i in SLOTS.size():
		var arrow := "> " if i == selected_slot else "   "
		slot_labels[i].text = "%s%s:  < %s >" % [arrow, SLOTS[i].name, current_item(i).name]
		slot_labels[i].modulate = SELECTED_COLOR if i == selected_slot else NORMAL_COLOR
	mannequin.queue_redraw()


func submit() -> void:
	var theme_id: String = orders[order_index]
	var wrong_slot := -1
	for i in SLOTS.size():
		if current_item(i).theme != theme_id:
			wrong_slot = i
			break
	if wrong_slot == -1:
		state = State.FEEDBACK
		feedback_left = FEEDBACK_TIME
		katya_label.text = "Катя: Да! Это настоящий «%s»! *подмигивает*" % THEMES[theme_id].name
	else:
		mistakes += 1
		var item := current_item(wrong_slot)
		if item.theme == "detective":
			katya_label.text = "Катя: %s? Это же для нового фестиваля! Мне нужен «%s»." % [
				item.name, THEMES[theme_id].name]
		else:
			katya_label.text = "Катя: Почти! Только %s сюда не подходит." % SLOTS[wrong_slot].name.to_lower()
		select_slot(wrong_slot)


func next_order() -> void:
	order_index += 1
	if order_index >= orders.size():
		finish(true)
	else:
		start_order()


func finish(is_win: bool) -> void:
	state = State.RESULT
	won = is_win
	timer_bar.hide()
	if won:
		GameState.add_stamp(MASCOT)
		var text := "Катя: Шикарное дефиле! Держи печать!\nУлика: %s" % GameState.CLUES[MASCOT].title
		if mistakes == 0:
			text += "\nМастер косплея: все образы с первого раза!"
		katya_label.text = text
		info_label.text = "Enter — вернуться на фестиваль"
	else:
		katya_label.text = "Катя: Время вышло! Дефиле начинается без нас…"
		info_label.text = "Enter — ещё раз    Esc — вернуться на фестиваль"


## Манекен-заглушка: голова, костюм и аксессуар цветами выбранных деталей.
## Заменить пиксельными спрайтами.
func draw_mannequin() -> void:
	var center := mannequin.size / 2
	var unit := mannequin.size.y / 10
	mannequin.draw_rect(Rect2(center + Vector2(-1.5, -4) * unit, Vector2(3, 2.5) * unit), current_item(0).color)
	mannequin.draw_rect(Rect2(center + Vector2(-2, -1.3) * unit, Vector2(4, 4.5) * unit), current_item(1).color)
	mannequin.draw_circle(center + Vector2(2.8, 0.5) * unit, unit, current_item(2).color)


func build_ui() -> void:
	var background := ColorRect.new()
	background.color = Color(0.22, 0.12, 0.3)
	background.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(background)

	var box := VBoxContainer.new()
	box.set_anchors_preset(Control.PRESET_FULL_RECT)
	box.alignment = BoxContainer.ALIGNMENT_CENTER
	box.add_theme_constant_override("separation", 8)
	add_child(box)

	katya_label = make_label(box, 13)

	var row := HBoxContainer.new()
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", 20)
	box.add_child(row)

	mannequin = Control.new()
	mannequin.custom_minimum_size = Vector2(100, 120)
	mannequin.draw.connect(draw_mannequin)
	row.add_child(mannequin)

	var slots_box := VBoxContainer.new()
	slots_box.alignment = BoxContainer.ALIGNMENT_CENTER
	slots_box.add_theme_constant_override("separation", 10)
	row.add_child(slots_box)
	for i in SLOTS.size():
		var label := make_label(slots_box, 12)
		label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
		slot_labels.append(label)

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
