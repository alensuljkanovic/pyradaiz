"""
This module contains all actions used by pyradaiz.
"""

from pyradaiz.model.consts import START_ICON, STOP_ICON, POMODORO_DURATION

__author__ = 'Alen Suljkanovic'

from PyQt4 import QtGui


class StartAction(QtGui.QAction):

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
        self.parent.timer_thread.seconds = self.parent.seconds
        self.parent.timer_thread.start()


class StopAction(QtGui.QAction):
    def __init__(self,parent):
        super(StopAction, self).__init__(parent)
        self.parent = parent
        self.setIcon(QtGui.QIcon(STOP_ICON))
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


class ResetAction(QtGui.QAction):

    def __init__(self, parent):
        super(ResetAction, self).__init__(parent)
        self.parent = parent
        self.setText("&Reset")
        self.setShortcut('Ctrl+R')
        self.setStatusTip('Reset pomodoro timer')
        self.triggered.connect(self.do)

    def do(self):
        """
        Executes the action.
        """
        self.parent.minutes = POMODORO_DURATION
        self.parent.seconds = 0
        self.parent.pomodoro_cnt = 0
        self.parent.timer_thread.terminate()
        self.parent.running = False

        from pyradaiz.model.pyradaiz import time_str
        self.parent.lcd.display(time_str(self.parent.minutes,
                                         self.parent.seconds))


class QuitAction(QtGui.QAction):

    def __init__(self, parent, *args, **kwargs):
        super(QuitAction, self).__init__(parent)
        self.setText("&Quit")
        self.setShortcut('Ctrl+Q')
        self.setStatusTip('Exit application')
        self.triggered.connect(QtGui.qApp.quit)