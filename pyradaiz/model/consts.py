"""
This module contains all constants used in the code.
"""
import os
from model.utils import get_root_path

__author__ = 'Alen Suljkanovic'

POMODORO_DURATION = 25  # 25 minutes
SHORT_BREAK = 5
LONG_BREAK = 15

# Credit  Dave Gandy for the icon pack (fontawesome.io)
icons_path = os.path.join(get_root_path(), "icons")
LOGO_IMAGE = os.path.join(icons_path, "pomodoro.png")
START_ICON = os.path.join(icons_path, "play-button.svg")
PAUSE_ICON = os.path.join(icons_path, "pause-symbol.svg")
RESET_ICON = os.path.join(icons_path, "refresh-arrow.svg")
SETTINGS_ICON = os.path.join(icons_path, "settings.svg")
ABOUT_ICON = os.path.join(icons_path, "information-symbol.svg")
TASKS_ICON = os.path.join(icons_path, "tasks-list.svg")
QUIT_ICON = os.path.join(icons_path, "power-button-off.svg")

TAKE_A_BREAK = "Sir, you should take a %s minute break"
GO_ON = "Go on, sir!"

SETTINGS_LABEL_WIDTH = 140
LINE_EDIT_WIDTH = 40
ALWAYS_ON_TOP_YES = "Yes"
ALWAYS_ON_TOP_NO = "No"
