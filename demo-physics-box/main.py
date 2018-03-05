# Demonstrate how to prevent specific bodies from colliding with each other

import harfang as hg
from random import uniform
from math import radians

BOX_SIZE = 2.5
SBOX_SIZE = BOX_SIZE * 0.1

cube_list = []

hg.LoadPlugins()

plus = hg.GetPlus()
plus.RenderInit(640, 640, 4)
hg.MountFileDriver(hg.StdFileDriver())

scn = plus.NewScene()
cam = plus.AddCamera(scn, hg.Matrix4.TranslationMatrix(hg.Vector3(0, 1, -10)))
cam.GetCamera().SetZoomFactor(0.75)
plus.AddLight(scn, hg.Matrix4.TransformationMatrix(hg.Vector3(BOX_SIZE * -0.1, BOX_SIZE * 0.25, BOX_SIZE * 0.15), hg.Vector3(radians(90), 0, 0)), hg.LightModelSpot, BOX_SIZE * 2.0, True)

plus.AddPhysicCube(scn, hg.Matrix4.TranslationMatrix(hg.Vector3(-3, 5, 0)))

# add a plane in layer 0 (default layer)
plus.AddPhysicCube(scn, hg.Matrix4.TranslationMatrix(hg.Vector3(0, BOX_SIZE, 0)), BOX_SIZE, BOX_SIZE, BOX_SIZE, 0)
plus.AddPhysicCube(scn, hg.Matrix4.TranslationMatrix(hg.Vector3(0, -BOX_SIZE, 0)), BOX_SIZE, BOX_SIZE, BOX_SIZE, 0)

plus.AddPhysicCube(scn, hg.Matrix4.TranslationMatrix(hg.Vector3(BOX_SIZE, 0, 0)), BOX_SIZE, BOX_SIZE, BOX_SIZE, 0)
plus.AddPhysicCube(scn, hg.Matrix4.TranslationMatrix(hg.Vector3(-BOX_SIZE, 0, 0)), BOX_SIZE, BOX_SIZE, BOX_SIZE, 0)

plus.AddPhysicCube(scn, hg.Matrix4.TranslationMatrix(hg.Vector3(0, 0, BOX_SIZE)), BOX_SIZE, BOX_SIZE, BOX_SIZE, 0)
plus.AddPhysicCube(scn, hg.Matrix4.TranslationMatrix(hg.Vector3(0, 0, -BOX_SIZE)), BOX_SIZE, BOX_SIZE, BOX_SIZE, 0)


# add 2 cubes in layer 1
def spawn_new_box():
	global cube_list
	new_pos = hg.Vector3(uniform(BOX_SIZE * -0.45, BOX_SIZE * 0.45), BOX_SIZE * 0.5, uniform(BOX_SIZE * -0.45, BOX_SIZE * 0.45))
	new_size = uniform(SBOX_SIZE * 0.25, SBOX_SIZE)
	new_cube, rb = plus.AddPhysicCube(scn, hg.Matrix4.TranslationMatrix(new_pos), new_size, new_size, new_size, 1.0, "assets/materials/orange.mat")
	new_light = plus.AddLight(scn, hg.Matrix4(), hg.LightModelPoint, new_size * 2.0, False, hg.Color.Orange, hg.Color.Orange) # plus.AddLight(scn)
	new_light.GetTransform().SetParent(new_cube)
	cube_list.append([new_cube, rb, new_light])

# rigid_body.SetCollisionLayer(1)
#
# node, rigid_body = plus.AddPhysicCube(scn, hg.Matrix4.TranslationMatrix(hg.Vector3(0.5, 2, 0.5)), 1, 1.5, 1)
# rigid_body.SetCollisionLayer(1)
#
# # layer 1 collides with layer 0 but not with itself
# scn.GetPhysicSystem().SetCollisionLayerPairState(0, 1, True)
# scn.GetPhysicSystem().SetCollisionLayerPairState(1, 1, True)

fps = hg.FPSController(0, 0, -BOX_SIZE * 0.45)

spawn_every = 0

while not plus.IsAppEnded():
	dt_sec = plus.UpdateClock()

	fps.UpdateAndApplyToNode(cam, dt_sec)

	spawn_every += 1
	if spawn_every > 8:
		spawn_every = 0
		spawn_new_box()

		if len(cube_list) > 64:
			cube_list[0][1].SetType(hg.RigidBodyDynamic)
			# cube_list[0][0].GetComponents("Collision").at(0).SetMass(0.0)
			# cube_list[0][1].SetIsSleeping(True)
			scn.RemoveNode(cube_list[0][2])
			cube_list.remove(cube_list[0])

	plus.UpdateScene(scn, dt_sec)
	plus.Flip()
	plus.EndFrame()

plus.RenderUninit()
