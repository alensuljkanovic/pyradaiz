"""
This module contains all actions used by pyradaiz.
"""
from dialogs import SettingsDialog

from model.consts import START_ICON, PAUSE_ICON, RESET_ICON, SETTINGS_ICON, \
    ABOUT_ICON, TASKS_ICON, QUIT_ICON

__author__ = 'Alen Suljkanovic'

from PyQt4 import QtGui


class PyradaizAction(QtGui.QAction):
    """
    Base class for all actions used in pyradaiz.
    """
    def __init__(self, parent):
        super(PyradaizAction, self).__init__(parent)

    def do(self):
        """
        Executes the action
        """
        raise Exception("Action's do method is not implemented!")


class StartAction(PyradaizAction):

    def __init__(self, parent):
        super(StartAction, self).__init__(parent)
        self.parent = parent
        self.setIcon(QtGui.QIcon(START_ICON))
        self.setText("&Start")
        self.setShortcut('Ctrl+S')
        self.setStatusTip('Start/Continue pomodoro')

        self.triggered.connect(self.do)

    def do(self):
        """
        Executes the action.
        """
        if self.parent.running:
            return

        self.parent.running = True
        self.parent.timer_thread.minutes = self.parent.minutes
        self.parent.timer_thread.seconds = 0
        self.parent.timer_thread.start()


class StopAction(PyradaizAction):
    def __init__(self,parent):
        super(StopAction, self).__init__(parent)
        self.parent = parent
        self.setIcon(QtGui.QIcon(PAUSE_ICON))
        self.setText("&Stop")
        self.setShortcut('Ctrl+X')
        self.setStatusTip('Stop pomodoro')

        self.triggered.connect(self.do)

    def do(self):
        """
        Executes the action.
        """
        self.parent.minutes = self.parent.timer_thread.minutes
        self.parent.seconds = self.parent.timer_thread.seconds
        self.parent.timer_thread.terminate()
        self.parent.running = False


class ResetAction(PyradaizAction):

    def __init__(self, parent):
        super(ResetAction, self).__init__(parent)
        self.parent = parent
        self.setText("&Reset")
        self.setIcon(QtGui.QIcon(RESET_ICON))
        self.setShortcut('Ctrl+R')
        self.setStatusTip('Reset pomodoro timer')
        self.triggered.connect(self.do)

    def do(self):
        """
        Executes the action.
        """
        self.parent.minutes = self.parent.settings.pomodoro_duration
        self.parent.seconds = 0
        self.parent.pomodoro_cnt = 0
        self.parent.timer_thread.terminate()
        self.parent.running = False

        from pyradaiz.model.pyradaiz import time_str
        self.parent.lcd.display(time_str(self.parent.minutes,
                                         self.parent.seconds))


class QuitAction(PyradaizAction):

    def __init__(self, parent):
        super(QuitAction, self).__init__(parent)
        self.parent = parent
        self.setIcon(QtGui.QIcon(QUIT_ICON))
        self.setText("&Quit")
        self.setShortcut('Ctrl+Q')
        self.setStatusTip('Exit application')
        self.parent.timer_thread.terminate()
        self.triggered.connect(QtGui.qApp.quit)


class SettingsAction(PyradaizAction):

    def __init__(self, parent):
        super(SettingsAction, self).__init__(parent)
        self.parent = parent
        self.setIcon(QtGui.QIcon(SETTINGS_ICON))
        self.setText("&Settings")
        self.triggered.connect(self.do)

    def do(self):
        """
        Executes the action.
        """
        dialog = SettingsDialog(self.parent)
        dialog.exec_()


class AboutAction(PyradaizAction):

    def __init__(self, parent):
        super(AboutAction, self).__init__(parent)
        self.parent = parent
        self.setIcon(QtGui.QIcon(ABOUT_ICON))
        self.setText("&About")
        self.triggered.connect(self.do)

    def do(self):
        """
        Executes the action.
        """
        pass


class TasksAction(PyradaizAction):

    def __init__(self, parent):
        super(TasksAction, self).__init__(parent)
        self.parent = parent
        self.setIcon(QtGui.QIcon(TASKS_ICON))
        self.setText("&Tasks")
        self.triggered.connect(self.do)

    def do(self):
        """
        Executes the action.
        """
        pass