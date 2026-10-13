extends CharacterBody2D

const SPEED = 160
## Спрайты гостя-детектива; «side» смотрит вправо, влево — отражение.
const TEXTURES := {
	"down": preload("res://art/characters/player_down.png"),
	"up": preload("res://art/characters/player_up.png"),
	"side": preload("res://art/characters/player_side.png"),
}
## Ноги спрайта (40 px) — на нижнем краю коллизии (радиус 14).
const SPRITE_OFFSET := Vector2(0, -6)
const STEP_TIME := 0.15

## Края локации для камеры (left, top, width, height) — у хаба и закулисья свои.
@export var camera_limits := Rect2i(-365, -367, 960, 704)

@onready var actionable_finder: Area2D = $Direction/ActionableFinder
@onready var direction_node: Node2D = $Direction
@onready var sprite: Sprite2D = $Sprite2D

var input_vector: Vector2 = Vector2.ZERO
var _step_time := 0.0

func _ready():
	sprite.scale = Vector2.ONE
	sprite.texture = TEXTURES.down
	sprite.offset = SPRITE_OFFSET
	var camera: Camera2D = $Camera2D
	camera.limit_left = camera_limits.position.x
	camera.limit_top = camera_limits.position.y
	camera.limit_right = camera_limits.end.x
	camera.limit_bottom = camera_limits.end.y
	# Вернулись в хаб из мини-игры или из-за кулис — встаём туда же, откуда ушли.
	# В других локациях (закулисье) позицию задаёт сама локация.
	var in_hub: bool = get_parent().scene_file_path == GameState.HUB_SCENE
	if in_hub and GameState.hub_return_position != null:
		global_position = GameState.hub_return_position
		GameState.hub_return_position = null

func get_input():
	# Во время диалога стоим на месте
	if GameState.in_dialogue:
		velocity = Vector2.ZERO
		return
	var input_direction = Input.get_vector("left","right","up","down")
	velocity = input_direction * SPEED
	
	if input_direction != Vector2.ZERO:
		direction_node.rotation = input_direction.angle()
		face(input_direction)

func face(direction: Vector2) -> void:
	if absf(direction.x) > absf(direction.y):
		sprite.texture = TEXTURES.side
		sprite.flip_h = direction.x < 0
	else:
		sprite.texture = TEXTURES.up if direction.y < 0 else TEXTURES.down
		sprite.flip_h = false

func animate_step(delta: float) -> void:
	# Шаг — спрайт подпрыгивает на пиксель, стоим — ровно
	if velocity == Vector2.ZERO:
		_step_time = 0.0
		sprite.offset = SPRITE_OFFSET
		return
	_step_time += delta
	var up := int(_step_time / STEP_TIME) % 2 == 1
	sprite.offset = SPRITE_OFFSET + (Vector2.UP if up else Vector2.ZERO)
	
func _physics_process(delta: float) -> void:
	get_input()
	move_and_slide()
	animate_step(delta)

func _unhandled_input(event: InputEvent) -> void:
	if GameState.in_dialogue:
		return
	# Только само нажатие Enter: Input.is_action_just_pressed() срабатывал на любое
	# событие в том же кадре (движение мыши, отпускание) и открывал второй диалог (BUG-009)
	if event.is_action_pressed("enter") and not event.is_echo():
		var actionables = actionable_finder.get_overlapping_areas()
		if actionables.size() > 0:
			actionables[0].action()
			return
