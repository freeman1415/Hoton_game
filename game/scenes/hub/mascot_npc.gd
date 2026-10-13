extends Area2D
## Маскот в хабе: зона, сам маскот (пока заглушка-кружок) и разговор по Enter.
## Используется и для главной сцены (mascot = "stage").
## Игрок находит его через ActionableFinder (слой 5 «Actionables») и вызывает action().

@export var mascot := "manya"
@export var display_name := "Маня"
@export var zone_name := "Арт-маркет"
@export var color := Color.WHITE
@export var dialogue_resource: DialogueResource
@export var dialogue_start := "start"
## Начать разговор сразу при входе в хаб, если ещё не знакомы (Маня у входа).
@export var auto_start := false
## Подсказка, когда игрок рядом.
@export var prompt := "Enter — поговорить"

const BODY_RADIUS := 16.0
const ZONE_RADIUS := 80.0
const STAMP_COLOR := Color(0.95, 0.75, 0.2)

var _player_near := false


func _ready() -> void:
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	if auto_start and not GameState.has_met(mascot):
		action.call_deferred()


func action() -> void:
	DialogueManager.show_dialogue_balloon(dialogue_resource, dialogue_start)


func _process(_delta: float) -> void:
	# Подсказка «Enter» прячется на время разговора
	queue_redraw()


func _draw() -> void:
	var font := ThemeDB.fallback_font
	var zone_color := color
	zone_color.a = 0.15
	draw_circle(Vector2.ZERO, ZONE_RADIUS, zone_color)
	draw_string(font, Vector2(-ZONE_RADIUS, -ZONE_RADIUS + 14), zone_name,
		HORIZONTAL_ALIGNMENT_CENTER, ZONE_RADIUS * 2, 12)

	draw_circle(Vector2.ZERO, BODY_RADIUS, color)
	draw_string(font, Vector2(-60, BODY_RADIUS + 14), display_name,
		HORIZONTAL_ALIGNMENT_CENTER, 120, 11)

	if GameState.has_stamp(mascot):
		draw_circle(Vector2(BODY_RADIUS, -BODY_RADIUS), 6, STAMP_COLOR)

	if _player_near and not GameState.in_dialogue:
		draw_string(font, Vector2(-100, -BODY_RADIUS - 6), prompt,
			HORIZONTAL_ALIGNMENT_CENTER, 200, 10)


func _on_body_entered(body: Node2D) -> void:
	if body.name == "Player":
		_player_near = true


func _on_body_exited(body: Node2D) -> void:
	if body.name == "Player":
		_player_near = false
