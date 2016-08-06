import gs
from math import pi

board_width = 30
board_length = 20

gsplus = gs.GetPlus()
gsplus.RenderInit(640, 400, "../pkg.core")

scn = gsplus.NewScene()

gsplus.AddPhysicCube(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(0, 0.5, 0)))

cam = gsplus.AddCamera(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(0, 40, 0)))
cam.GetTransform().SetRotation(gs.Vector3(pi / 2, 0, 0))
gsplus.AddLight(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(board_width, board_length, board_length)))
gsplus.AddPlane(scn, gs.Matrix4.Identity, board_width, board_length)

while not gsplus.KeyPress(gs.InputDevice.KeyEscape):
    dt_sec = gsplus.UpdateClock()

    gsplus.UpdateScene(scn, dt_sec)
    gsplus.Text2D(5, 5, "Move around with QSZD, left mouse button to look around")
    gsplus.Flip()