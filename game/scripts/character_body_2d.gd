extends CharacterBody2D

const SPEED = 400
@onready var actionable_finder: Area2D = $Direction/ActionableFinder
@onready var direction_node: Node2D = $Direction

var input_vector: Vector2 = Vector2.ZERO

func get_input():
	var input_direction = Input.get_vector("left","right","up","down")
	velocity = input_direction * SPEED
	
	if input_direction != Vector2.ZERO:
		direction_node.rotation = input_direction.angle()
	
func _physics_process(delta: float) -> void:
	get_input()
	move_and_slide()

func _unhandled_input(_event: InputEvent) -> void:
	if Input.is_action_just_pressed("enter"):
		var actionables = actionable_finder.get_overlapping_areas()
		if actionables.size() > 0:
			actionables[0].action()
			return
