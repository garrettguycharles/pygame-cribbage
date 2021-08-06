import cx_Freeze
import os

game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "images")
anim_folder = os.path.join(game_folder, "anim")

executables = [cx_Freeze.Executable("cribbage.py")]

cx_Freeze.setup(
    name="Cribbage",
    options={"build_exe": {"packages":["pygame", "os"],
                           "include_files":[os.path.join(img_folder, ""),
                                            os.path.join(anim_folder, "")
                                            os.path.join(game_folder, "cardsprite.py"),
                                            os.path.join(game_folder, "globals.py"),
                                            os.path.join(game_folder, "model.py"),
                                            os.path.join(game_folder, "nineslice.py"),
                                            os.path.join(game_folder, "pegboard.py"),
                                            os.path.join(game_folder, "playingcard.py"),
                                            os.path.join(game_folder, "utils.py"),
                                            os.path.join(game_folder, "visual_fx.py"),
                                            os.path.join(game_folder, "ui.py")]}},
    executables = executables

    )