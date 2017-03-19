import gs
import math
import random
from constants import *

gs.LoadPlugins()

def setup_game_level(plus=None):
	scn = plus.NewScene()

	while not scn.IsReady():
		plus.UpdateScene(scn, plus.UpdateClock())

	scn.GetPhysicSystem().SetDebugVisuals(True)

	cam_matrix = gs.Matrix4.TransformationMatrix(gs.Vector3(0, 15, 3), gs.Vector3(math.radians(90), 0, 0))
	cam = plus.AddCamera(scn, cam_matrix)
	plus.AddLight(scn, gs.Matrix4.TranslationMatrix((-10, 10, 10)))
	plus.AddPhysicPlane(scn)

	return scn


def create_turret(plus=None, scn=None, pos=gs.Vector3(0, 0.75, 0), rot=gs.Vector3(), w=1, h=1.25, d=1, mass = 10):
	scn.GetPhysicSystem().SetForceRigidBodyAxisLockOnCreation(gs.LockX + gs.LockY + gs.LockZ + gs.LockRotX + gs.LockRotZ)
	root = plus.AddPhysicCube(scn, gs.Matrix4.TransformationMatrix(pos, rot), w, h, d, mass)
	# root[1].SetAngularDamping(0.995)
	cannon = plus.AddCube(scn, gs.Matrix4.TranslationMatrix((0, h * 0.2, d * 0.75)), w * 0.35, w * 0.35, d)
	cannon.GetTransform().SetParent(root[0])

	return root, cannon, mass


def rotate_turret(turret, angle, mass):
	rot = turret[0].GetTransform().GetRotation()
	dt_rot = math.radians(angle) - rot.y
	angular_vel = turret[1].GetAngularVelocity().y
	dt_rot -= angular_vel
	turret[1].SetIsSleeping(False)
	turret[1].ApplyTorque(gs.Vector3(0, dt_rot * mass, 0))


def spawn_enemy(plus, scn, pos = gs.Vector3(0, 2, 5)):
	scn.GetPhysicSystem().SetForceRigidBodyAxisLockOnCreation(0)
	root = plus.AddPhysicSphere(scn, gs.Matrix4.TranslationMatrix(pos), 0.7)

	return root


def game():
	plus = gs.GetPlus()
	plus.RenderInit(1280, 720)
	game_device = gs.GetInputSystem().GetDevice("keyboard")

	scn = setup_game_level(plus)
	turret, cannon, turret_mass = create_turret(plus, scn)
	target_angle = 0.0

	enemy_list = []
	spawn_timer = 0.0

	while not plus.KeyPress(gs.InputDevice.KeyEscape):
		dt = plus.UpdateClock()

		# Turret
		if game_device.IsDown(gs.InputDevice.KeyRight):
			target_angle += dt.to_sec() * aim_rotation_speed
		else:
			if game_device.IsDown(gs.InputDevice.KeyLeft):
				target_angle -= dt.to_sec() * aim_rotation_speed

		target_angle = max(min(target_angle, aim_angle_range['max']), aim_angle_range['min'])

		rotate_turret(turret, target_angle, turret_mass)

		# Enemies
		spawn_timer += dt.to_sec()
		if spawn_timer > enemy_spawn_interval:
			spawn_timer = 0
			spawn_pos = gs.Vector3(random.uniform(-5, 5), 2, random.uniform(4.5, 5.5))
			new_enemy = spawn_enemy(plus, scn, spawn_pos)
			enemy_list.append([new_enemy[0], new_enemy[1]])

		for enemy in enemy_list:
			# make enemy crawl toward the player
			enemy_dir = turret[0].GetTransform().GetPosition() - enemy[0].GetTransform().GetPosition()
			enemy_dir.Normalize()
			enemy[1].ApplyLinearForce(enemy_dir)

		plus.UpdateScene(scn, dt)
		plus.Text2D(5, 5, "Turret Control, angle = " + str(target_angle))
		plus.Flip()

game()
