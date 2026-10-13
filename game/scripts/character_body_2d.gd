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

@onready var actionable_finder: Area2D = $Direction/ActionableFinder
@onready var direction_node: Node2D = $Direction
@onready var sprite: Sprite2D = $Sprite2D

var input_vector: Vector2 = Vector2.ZERO
var _step_time := 0.0

func _ready():
	sprite.scale = Vector2.ONE
	sprite.texture = TEXTURES.down
	sprite.offset = SPRITE_OFFSET
	# Вернулись из мини-игры — встаём туда же, откуда ушли
	if GameState.hub_return_position != null:
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

func _unhandled_input(_event: InputEvent) -> void:
	if GameState.in_dialogue:
		return
	if Input.is_action_just_pressed("enter"):
		var actionables = actionable_finder.get_overlapping_areas()
		if actionables.size() > 0:
			actionables[0].action()
			return
