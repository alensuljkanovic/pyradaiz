"""
This module contains all constants used in the code.
"""
import os
from model.utils import get_root_path

__author__ = 'Alen Suljkanovic'

POMODORO_DURATION = 25  # 25 minutes
SHORT_BREAK = 5
LONG_BREAK = 15

icons_path = os.path.join(get_root_path(), "icons")
UP_ARROW_ICON = "/icons/up-arrow-icon.png"
DOWN_ARROW_ICON = "./icons/down-arrow-icon.png"
LOGO_IMAGE = os.path.join(icons_path, "pomodoro.png")
START_ICON = os.path.join(icons_path, "start.png")
STOP_ICON = os.path.join(icons_path, "stop.png")
RESET_ICON = os.path.join(icons_path, "reset.png")

TAKE_A_BREAK = "Sir, you should take a %s minute break"
GO_ON = "Go on, sir!"
