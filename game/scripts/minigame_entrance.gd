extends Area2D
## Вход в мини-игру: игрок подходит и жмёт Enter.

@export_file("*.tscn") var next_scene: String = "res://ritm/main.tscn"


func action() -> void:
	var player := get_tree().current_scene.get_node_or_null("Player") as Node2D
	var return_position: Vector2 = player.global_position if player else Vector2.ZERO
	GameState.go_to_minigame(next_scene, return_position)
