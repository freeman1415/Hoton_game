extends CanvasLayer
## Счётчик печатей в углу экрана хаба.

@onready var stamps_label: Label = $StampsLabel


func _ready() -> void:
	# Плашка под счётчиком, чтобы он не сливался с подписями зон
	var style := Brand.panel_style()
	style.bg_color = Color(Brand.BROWN_DEEP, 0.85)
	style.set_content_margin_all(6)
	stamps_label.add_theme_stylebox_override("normal", style)
	stamps_label.add_theme_color_override("font_color", Brand.CREAM)
	stamps_label.size = Vector2.ZERO
	GameState.stamp_added.connect(_on_stamp_added)
	update_text()


func _on_stamp_added(_mascot: String) -> void:
	update_text()


func update_text() -> void:
	var text := "Печати: %d / %d" % [GameState.stamp_count(), GameState.MASCOTS.size()]
	if GameState.can_open_finale():
		text += "\nМожно идти к главной сцене!"
	stamps_label.text = text + "\nTab — блокнот"
