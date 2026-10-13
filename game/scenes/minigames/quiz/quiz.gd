extends Control
## Викторина Мойто: 5 случайных вопросов, 3 варианта, 10 секунд на ответ.
## 3 верных ответа — печать. Управление: ↑↓ + Enter или цифры 1–3.

const MASCOT := "moyto"
const QUESTIONS_PER_ROUND := 5
const CORRECT_TO_WIN := 3
const TIME_PER_QUESTION := 10.0
const FEEDBACK_TIME := 1.2

const SELECTED_COLOR := Color(1.0, 0.85, 0.3)
const NORMAL_COLOR := Color(1, 1, 1)

## Первый ответ в списке — верный, на экране варианты перемешиваются.
const QUESTIONS := [
	{"q": "Чем детектив рассматривает мелкие улики?", "a": ["Лупой", "Зонтиком", "Барабаном"]},
	{"q": "Куда детектив записывает улики?", "a": ["В блокнот", "В торт", "В ведро"]},
	{"q": "Какой фестиваль Хотона был про ракеты и звёзды?", "a": ["«Космос»", "«Цирк»", "«Ретро»"]},
	{"q": "Кто на цирковой арене носит красный нос?", "a": ["Клоун", "Космонавт", "Дирижёр"]},
	{"q": "Что крутили на проигрывателе в ретро-времена?", "a": ["Пластинку", "Флешку", "Блин"]},
	{"q": "Кто из маскотов Хотона — собачка?", "a": ["Мойто", "Маня", "Сулус"]},
	{"q": "Кто из маскотов Хотона — коровка?", "a": ["Маня", "Катя", "Леня"]},
	{"q": "Кто ведёт музыкальную программу фестиваля?", "a": ["Леня", "Мойто", "Катя"]},
	{"q": "Что остаётся на снегу, если по нему пройти?", "a": ["Следы", "Ноты", "Печати"]},
	{"q": "Что главное для детектива?", "a": ["Наблюдательность", "Громкий голос", "Длинный хвост"]},
]

enum State { QUESTION, FEEDBACK, RESULT }

var state := State.QUESTION
var round_questions := []
var index := 0
var correct_count := 0
var options: Array = []      # варианты текущего вопроса в порядке на экране
var correct_option := 0
var selected := 0
var time_left := TIME_PER_QUESTION
var feedback_left := 0.0
var won := false

var title_label: Label
var question_label: Label
var option_labels: Array[Label] = []
var timer_bar: ProgressBar
var info_label: Label


func _ready() -> void:
	build_ui()
	var pool := QUESTIONS.duplicate()
	pool.shuffle()
	round_questions = pool.slice(0, QUESTIONS_PER_ROUND)
	show_question()


func _process(delta: float) -> void:
	match state:
		State.QUESTION:
			time_left -= delta
			timer_bar.value = time_left
			if time_left <= 0.0:
				answer(-1)
		State.FEEDBACK:
			feedback_left -= delta
			if feedback_left <= 0.0:
				next_question()


func _unhandled_input(event: InputEvent) -> void:
	# echo — автоповтор зажатой клавиши, не считаем
	if event is InputEventKey and event.echo:
		return
	match state:
		State.QUESTION:
			if event.is_action_pressed("up"):
				select((selected + options.size() - 1) % options.size())
			elif event.is_action_pressed("down"):
				select((selected + 1) % options.size())
			elif event.is_action_pressed("enter"):
				answer(selected)
			elif event is InputEventKey and event.pressed:
				var digit: int = event.physical_keycode - KEY_1
				if digit >= 0 and digit < options.size():
					answer(digit)
		State.RESULT:
			if event.is_action_pressed("enter"):
				if won:
					GameState.return_to_hub()
				else:
					get_tree().reload_current_scene()
			elif event.is_action_pressed("ui_cancel") and not won:
				GameState.return_to_hub()


func show_question() -> void:
	state = State.QUESTION
	var question: Dictionary = round_questions[index]
	options = question.a.duplicate()
	options.shuffle()
	correct_option = options.find(question.a[0])
	title_label.text = "Мойто: Внимание, вопрос! %d из %d" % [index + 1, QUESTIONS_PER_ROUND]
	question_label.text = question.q
	for i in option_labels.size():
		option_labels[i].text = "%d. %s" % [i + 1, options[i]]
	time_left = TIME_PER_QUESTION
	timer_bar.value = time_left
	timer_bar.show()
	info_label.text = "Верных ответов: %d" % correct_count
	select(0)


func select(i: int) -> void:
	selected = i
	for j in option_labels.size():
		option_labels[j].modulate = SELECTED_COLOR if j == selected else NORMAL_COLOR
		option_labels[j].text = ("> " if j == selected else "   ") + "%d. %s" % [j + 1, options[j]]


## i = -1 — время вышло.
func answer(i: int) -> void:
	if state != State.QUESTION:
		return
	state = State.FEEDBACK
	feedback_left = FEEDBACK_TIME
	timer_bar.hide()
	if i == correct_option:
		correct_count += 1
		question_label.text = "Верно! Мойто радостно виляет хвостом."
	elif i == -1:
		question_label.text = "Время вышло! Правильно: %s" % options[correct_option]
	else:
		question_label.text = "Не-а! Правильно: %s" % options[correct_option]
	info_label.text = "Верных ответов: %d" % correct_count


func next_question() -> void:
	index += 1
	if index >= round_questions.size():
		finish()
	else:
		show_question()


func finish() -> void:
	state = State.RESULT
	won = correct_count >= CORRECT_TO_WIN
	for label in option_labels:
		label.text = ""
	if won:
		GameState.add_stamp(MASCOT)
		title_label.text = "Мойто: Победа! Держи печать!"
		question_label.text = "Верных ответов: %d из %d\nУлика: %s" % [
			correct_count, QUESTIONS_PER_ROUND, GameState.CLUES[MASCOT].title]
		info_label.text = "Enter — вернуться на фестиваль"
	else:
		title_label.text = "Мойто: Эх, почти!"
		question_label.text = "Верных ответов: %d из %d. Нужно хотя бы %d." % [
			correct_count, QUESTIONS_PER_ROUND, CORRECT_TO_WIN]
		info_label.text = "Enter — ещё раз    Esc — вернуться на фестиваль"


func build_ui() -> void:
	var background := ColorRect.new()
	background.color = Color(0.35, 0.12, 0.18)
	background.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(background)

	var box := VBoxContainer.new()
	box.set_anchors_preset(Control.PRESET_FULL_RECT)
	box.alignment = BoxContainer.ALIGNMENT_CENTER
	box.add_theme_constant_override("separation", 10)
	add_child(box)

	title_label = make_label(box, 16)
	question_label = make_label(box, 14)
	for i in 3:
		var label := make_label(box, 13)
		option_labels.append(label)

	timer_bar = ProgressBar.new()
	timer_bar.max_value = TIME_PER_QUESTION
	timer_bar.show_percentage = false
	timer_bar.custom_minimum_size = Vector2(200, 6)
	timer_bar.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	box.add_child(timer_bar)

	info_label = make_label(box, 11)


func make_label(parent: Node, font_size: int) -> Label:
	var label := Label.new()
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_font_size_override("font_size", font_size)
	parent.add_child(label)
	return label
