import gs
from math import radians, cos, sin
import random
from constants import *

gs.LoadPlugins()


def setup_game_level(plus=None):
	scn = plus.NewScene()

	while not scn.IsReady():
		plus.UpdateScene(scn, plus.UpdateClock())

	scn.GetPhysicSystem().SetDebugVisuals(False)

	cam_matrix = gs.Matrix4.TransformationMatrix(gs.Vector3(0, 15, 3), gs.Vector3(radians(90), 0, 0))
	cam = plus.AddCamera(scn, cam_matrix)
	plus.AddLight(scn, gs.Matrix4.TranslationMatrix((-10, 10, 10)))
	ground = plus.AddPhysicPlane(scn)

	return scn, ground


def create_turret(plus=None, scn=None, pos=gs.Vector3(0, 0.75, 0), rot=gs.Vector3(), w=1, h=1.25, d=1, mass = 10):
	scn.GetPhysicSystem().SetForceRigidBodyAxisLockOnCreation(gs.LockX + gs.LockY + gs.LockZ + gs.LockRotX + gs.LockRotZ)
	root = plus.AddPhysicCube(scn, gs.Matrix4.TransformationMatrix(pos, rot), w, h, d, mass)
	root[1].SetAngularDamping(1.0)
	cannon = plus.AddCube(scn, gs.Matrix4.TranslationMatrix((0, h * 0.2, d * 0.75)), w * 0.35, w * 0.35, d)
	cannon.GetTransform().SetParent(root[0])

	return root, cannon, mass


def rotate_turret(turret, angle, mass):
	rot = turret[0].GetTransform().GetRotation()
	dt_rot = radians(angle) - rot.y
	turret[1].SetIsSleeping(False)
	turret[1].ApplyTorque(gs.Vector3(0, dt_rot * mass * turret_rotation_speed, 0))


def spawn_enemy(plus, scn, pos = gs.Vector3(0, 2, 5)):
	scn.GetPhysicSystem().SetForceRigidBodyAxisLockOnCreation(0)
	root = plus.AddPhysicSphere(scn, gs.Matrix4.TranslationMatrix(pos), 0.7, 6, 16, enemy_mass)
	root[0].SetName('enemy')

	return root


def throw_bullet(plus, scn, pos, dir):
	scn.GetPhysicSystem().SetForceRigidBodyAxisLockOnCreation(gs.LockY)
	root = plus.AddPhysicSphere(scn, gs.Matrix4.TranslationMatrix(pos), 0.2, 3, 8)
	root[0].SetName('bullet')
	root[1].ApplyLinearImpulse(dir * bullet_velocity)

	return root


def destroy_enemy(plus, scn, enemy):
	pos = enemy.GetTransform().GetPosition()
	scn.RemoveNode(enemy)


def render_aim_cursor(plus, scn, angle):
	radius = screen_width / 8
	angle = 90 - angle
	a = gs.Vector2(cos(radians(angle)), sin(radians(angle))) * radius * 1.15
	b = gs.Vector2(cos(radians(angle - 5)), sin(radians(angle - 5))) * radius
	c = gs.Vector2(cos(radians(angle + 5)), sin(radians(angle + 5))) * radius
	plus.Triangle2D(screen_width * 0.5 + a.x, screen_height * 0.15 + a.y,
					screen_width * 0.5 + b.x, screen_height * 0.15 + b.y,
					screen_width * 0.5 + c.x, screen_height * 0.15 + c.y,
					gs.Color.Green, gs.Color.Green, gs.Color.Green)


def display_hud(plus, player_energy, cool_down, score):

	# Life bar
	plus.Quad2D(screen_width * 0.015, screen_height * 0.225,
				player_energy * screen_width * 0.15, screen_height * 0.225,
				player_energy * screen_width * 0.15, screen_height * 0.175,
				screen_width * 0.015, screen_height * 0.175,
				gs.Color.Green, gs.Color.Green, gs.Color.Green, gs.Color.Green)
	plus.Text2D(screen_width * 0.018, screen_height * 0.1825, "LIFE", font_size, gs.Color.White, "aerial.ttf")

	plus.Quad2D(screen_width * 0.015, screen_height * 0.15,
				cool_down * screen_width * 0.15, screen_height * 0.15,
				cool_down * screen_width * 0.15, screen_height * 0.1,
				screen_width * 0.015, screen_height * 0.1,
				gs.Color.Green, gs.Color.Green, gs.Color.Green, gs.Color.Green)

	plus.Text2D(screen_width * 0.018, screen_height * 0.1075, "HEAT", font_size, gs.Color.White, "aerial.ttf")

	plus.Text2D(screen_width * 0.018, screen_height * 0.035, "SCORE", font_size, gs.Color.White, "aerial.ttf")
	plus.Text2D(screen_width * 0.15, screen_height * 0.035, str(score), font_size, gs.Color.Green, "aerial.ttf")


def rvect(r):
	return gs.Vector3(random.uniform(-r, r), random.uniform(-r, r), random.uniform(-r, r))


def create_explosion(plus, scn, pos, debris_amount=32, debris_radius=0.5):
	scn.GetPhysicSystem().SetForceRigidBodyAxisLockOnCreation(0)
	new_debris_list = []
	for i in range(debris_amount):
		debris_size = random.uniform(0.1, 0.25)
		debris = plus.AddPhysicCube(scn, gs.Matrix4().TransformationMatrix(pos + rvect(debris_radius), rvect(radians(45))),
									debris_size, debris_size, debris_size, 0.05)
		debris[1].ApplyLinearImpulse(rvect(0.25))
		new_debris_list.append(debris[0])

	return new_debris_list


def game():
	plus = gs.GetPlus()
	plus.RenderInit(screen_width, screen_height)
	game_device = gs.GetInputSystem().GetDevice("keyboard")
	gs.MountFileDriver(gs.StdFileDriver())

	scn, ground = setup_game_level(plus)
	turret, cannon, turret_mass = create_turret(plus, scn)
	target_angle = 0.0

	enemy_list = []
	debris_list = []
	spawn_timer = 0.0
	turret_cool_down = 0.0
	enemy_spawn_interval = 5  # every n second
	player_life = max_player_life
	score = 0

	while not plus.KeyPress(gs.InputDevice.KeyEscape):
		dt = plus.UpdateClock()

		# Turret
		if game_device.IsDown(gs.InputDevice.KeyRight):
			target_angle += dt.to_sec() * aim_rotation_speed
		else:
			if game_device.IsDown(gs.InputDevice.KeyLeft):
				target_angle -= dt.to_sec() * aim_rotation_speed

		if turret_cool_down < 0.0 and game_device.WasPressed(gs.InputDevice.KeySpace):
			throw_bullet(plus, scn, cannon.GetTransform().GetWorld().GetTranslation(), cannon.GetTransform().GetWorld().GetRow(2))
			turret_cool_down = turret_cool_down_duration

		turret_cool_down -= dt.to_sec()

		target_angle = max(min(target_angle, aim_angle_range['max']), aim_angle_range['min'])

		rotate_turret(turret, target_angle, turret_mass)

		# Enemies
		spawn_timer += dt.to_sec()
		if spawn_timer > enemy_spawn_interval:
			spawn_timer = 0
			spawn_pos = gs.Vector3(random.uniform(-10, 10), 2.5, random.uniform(5.5, 6.5))
			spawn_pos.Normalize()
			spawn_pos = spawn_pos * 10.0
			spawn_pos.y = 5.0
			new_enemy = spawn_enemy(plus, scn, spawn_pos)
			enemy_list.append([new_enemy[0], new_enemy[1]])

		for enemy in enemy_list:
			# make enemy crawl toward the player
			enemy_dir = turret[0].GetTransform().GetPosition() - enemy[0].GetTransform().GetPosition()
			enemy_dir.Normalize()
			enemy[1].SetIsSleeping(False)
			enemy[1].ApplyLinearForce(enemy_dir * 0.25 * enemy_mass)

			if gs.Vector3.Dist(turret[0].GetTransform().GetPosition(), enemy[0].GetTransform().GetPosition()) < 1.5:
				destroy_enemy(plus, scn, enemy[0])
				debris_list.extend(create_explosion(plus, scn, enemy[0].GetTransform().GetPosition()))
				enemy_list.remove(enemy)
				player_life -= 1
			else:
				col_pairs = scn.GetPhysicSystem().GetCollisionPairs(enemy[0])
				if len(col_pairs) > 0:
					for col_pair in col_pairs:
						if col_pair.GetNodeB().GetName() == 'bullet':
							pos = col_pair.GetNodeB().GetTransform().GetPosition()
							debris_list.extend(create_explosion(plus, scn, pos, 8, 0.25))

							pos = enemy[0].GetTransform().GetPosition()
							destroy_enemy(plus, scn, enemy[0])
							enemy_list.remove(enemy)
							scn.RemoveNode(col_pair.GetNodeB())
							debris_list.extend(create_explosion(plus, scn, pos))

							score += 10

		# Game difficulty
		enemy_spawn_interval = max(1.0, enemy_spawn_interval - dt.to_sec() * 0.025)

		# Cleanup debris
		if len(debris_list) > max_debris:
			tmp_debris = debris_list[0]
			debris_list.remove(debris_list[0])
			scn.RemoveNode(tmp_debris)

		plus.UpdateScene(scn, dt)

		render_aim_cursor(plus, scn, target_angle)
		display_hud(plus, player_life / max_player_life, max(0, turret_cool_down) / turret_cool_down_duration, score)
		plus.Flip()

game()
