extends CanvasLayer
## Детективный блокнот: печати, улики, сколько осталось до финала.
## Открывается и закрывается по Tab (Esc тоже закрывает). Пока открыт — игра на паузе.

const STAMP_ON := Color(0.95, 0.75, 0.2)
const STAMP_OFF := Color(0.4, 0.4, 0.4)
const HINT_COLOR := Color(0.6, 0.6, 0.6)

var panel: PanelContainer
var stamps_row: HBoxContainer
var clues_label: RichTextLabel
var footer_label: Label


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	layer = 50
	build_ui()
	panel.hide()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.echo:
		return
	if panel.visible:
		if event.is_action_pressed("notebook") or event.is_action_pressed("ui_cancel"):
			close()
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("notebook") and not GameState.in_dialogue:
		open()
		get_viewport().set_input_as_handled()


func open() -> void:
	refresh()
	panel.show()
	get_tree().paused = true


func close() -> void:
	panel.hide()
	get_tree().paused = false


func is_open() -> bool:
	return panel.visible


func refresh() -> void:
	for child in stamps_row.get_children():
		child.queue_free()
	for mascot in GameState.MASCOTS:
		var label := Label.new()
		var has := GameState.has_stamp(mascot)
		label.text = ("● " if has else "○ ") + GameState.MASCOT_INFO[mascot].name
		label.modulate = STAMP_ON if has else STAMP_OFF
		stamps_row.add_child(label)

	var text := ""
	for mascot in GameState.MASCOTS:
		var info: Dictionary = GameState.MASCOT_INFO[mascot]
		if GameState.has_clue(mascot):
			var clue: Dictionary = GameState.CLUES[mascot]
			text += "[b]%s[/b] (%s)\n%s\n" % [clue.title, info.name, clue.text]
		else:
			text += "[color=#%s]??? — помоги: %s, %s[/color]\n" % [
				HINT_COLOR.to_html(false), info.name, info.zone]
	clues_label.text = text.strip_edges()

	var left := GameState.STAMPS_FOR_FINALE - GameState.stamp_count()
	var footer := ""
	if left > 0:
		footer = "До разгадки: ещё %d %s." % [left, plural_stamps(left)]
	else:
		footer = "Печатей хватает! Иди к главной сцене."
	footer += "    Секретные разговоры: %d / %d    Tab — закрыть" % [
		GameState.secret_dialogues.size(), GameState.SECRET_DIALOGUES_TOTAL]
	footer_label.text = footer


func plural_stamps(n: int) -> String:
	if n % 10 == 1 and n % 100 != 11:
		return "печать"
	if n % 10 in [2, 3, 4] and not n % 100 in [12, 13, 14]:
		return "печати"
	return "печатей"


func build_ui() -> void:
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)

	panel = PanelContainer.new()
	panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	panel.offset_left = 24
	panel.offset_top = 16
	panel.offset_right = -24
	panel.offset_bottom = -16
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0, 0, 0, 0.95)
	style.border_color = Color(1, 1, 1)
	style.set_border_width_all(2)
	style.set_content_margin_all(12)
	panel.add_theme_stylebox_override("panel", style)
	root.add_child(panel)

	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 8)
	panel.add_child(box)

	var title := Label.new()
	title.text = "Детективный блокнот"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 16)
	box.add_child(title)

	stamps_row = HBoxContainer.new()
	stamps_row.alignment = BoxContainer.ALIGNMENT_CENTER
	stamps_row.add_theme_constant_override("separation", 16)
	box.add_child(stamps_row)

	clues_label = RichTextLabel.new()
	clues_label.bbcode_enabled = true
	clues_label.size_flags_vertical = Control.SIZE_EXPAND_FILL
	clues_label.add_theme_font_size_override("normal_font_size", 12)
	clues_label.add_theme_font_size_override("bold_font_size", 13)
	box.add_child(clues_label)

	footer_label = Label.new()
	footer_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	footer_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	footer_label.add_theme_font_size_override("font_size", 11)
	box.add_child(footer_label)
