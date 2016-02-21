import os
import sys
from xml.etree.ElementTree import ElementTree, Element, SubElement
from PyQt4 import QtGui, QtCore
from xdg.Menu import ELEMENT_NODE
from model.actions import StartAction, StopAction, QuitAction, \
    ResetAction, SettingsAction
from model.consts import SHORT_BREAK, POMODORO_DURATION, UP_ARROW_ICON, \
    DOWN_ARROW_ICON, GO_ON, TAKE_A_BREAK, LONG_BREAK, LOGO_IMAGE, START_ICON, \
    STOP_ICON, RESET_ICON
from model.utils import get_root_path


def time_str(minutes, seconds):
    """
    Creates string from minutes and seconds in following format: mm:ss.
    :param minutes: current minute
    :param seconds: current second
    :return:
        string
    """
    disp_mins = "0%s" % minutes if minutes < 10  else minutes
    disp_secs = "0%s" % seconds if seconds < 10 else seconds

    time = "{0}:{1}".format(disp_mins, disp_secs)
    return time


class Task(object):
    """
    Class that describes one PyModoro task.
    """

    def __init__(self, name, description):
        """Initialize task object"""
        self.name = name
        self.description = description
        self.counter = 0
        self.finished = False


class PyradaizSettings(object):
    """
    Settings object. Contains information about pomodoro duration, short break
    duration and long break duration.
    """
    def __init__(self, parent):
        super(PyradaizSettings, self).__init__()
        self.parent = parent
        self.file_path = None
        # Default settings...
        self._pomodoro_duration = POMODORO_DURATION
        self.short_break = SHORT_BREAK
        self.long_break = LONG_BREAK

    def save(self):
        """
        Saves settings into the file.
        """
        file_path = os.path.join(get_root_path(), "config.xml")
        root = Element("config")
        tree = ElementTree(root)

        pomodoro_duration = SubElement(root, "pomodoro_duration")
        pomodoro_duration.text = "%s" % self.pomodoro_duration

        short_break = SubElement(root, "short_break")
        short_break.text = "%s" % self.short_break

        long_break = SubElement(root, "long_break")
        long_break.text = "%s" % self.long_break

        tree.write(file_path)

    def load(self):
        """
        Loads settings from .xml file.
        """
        file_path = os.path.join(get_root_path(), "config.xml")
        try:
            with open(file_path) as f:
                tree = ElementTree()
                tree.parse(f)
                root = tree.getroot()

                self.pomodoro_duration = int(root.find("pomodoro_duration").text)
                self.short_break = int(root.find("short_break").text)
                self.long_break = int(root.find("long_break").text)

        except FileNotFoundError:
            pass

    @property
    def pomodoro_duration(self):
        return self._pomodoro_duration

    @pomodoro_duration.setter
    def pomodoro_duration(self, duration):
        self._pomodoro_duration = duration
        self.parent.minutes = duration


class PyradaizThread(QtCore.QThread):
    """
    Thread that modifies the counter and gives notifications about breaks.
    """
    def __init__(self, parent):
        super(PyradaizThread, self).__init__()
        self.parent = parent
        self.minutes = self.parent.minutes
        self.seconds = self.parent.seconds

        settings = self.parent.settings
        self.short_break = settings.short_break
        self.long_break = settings.long_break
        self.pomodoro_cnt = 0
        # Shows if it's time to notify about the break or not.
        self._break = False

    def run(self):
        """
        Runs counter.
        """
        # Loop until one pomodoro session + following break are over.
        while self.minutes >= 0 and self.seconds >= 0:
            self.seconds -= 1
            if self.seconds < 0:
                self.seconds = 59
                self.minutes -= 1

            if self.minutes == 0 and self.seconds == 0:
                if not self._break:
                    self.pomodoro_cnt += 1
                    # Take a long break after third pomodoro session...
                    if self.pomodoro_cnt % 3 != 0:
                        self.minutes = self.short_break
                    else:
                        self.minutes = self.long_break

                    self.emit(QtCore.SIGNAL("take_a_break(QString)"),
                              "%s" % self.minutes)
                else:
                    self.minutes = POMODORO_DURATION
                    self.emit(QtCore.SIGNAL("go_on(QString)"), "go_on")

                self._break = not self._break

            self.emit(QtCore.SIGNAL("update_display(QString)"), self.time)
            # This ensures that the display is updated every second.
            self.sleep(1)

    @property
    def time(self):
        """
        Returns current time in minutes and seconds, as a tuple.
        :return tuple
        """
        return time_str(self.minutes, self.seconds)


class PyradaizGui(QtGui.QMainWindow):
    """
    Main window.
    """
    def __init__(self, *args, **kwargs):
        super(PyradaizGui, self).__init__(*args, **kwargs)

        self.setWindowTitle("pyradaiz")
        main_layout = QtGui.QVBoxLayout()
 
        self.lcd = QtGui.QLCDNumber(self)

        self.tasks = []
        self.running = False
        self.settings = PyradaizSettings(self)
        self.settings.load()
        self.minutes = self.settings.pomodoro_duration
        self.seconds = 0

        init_time = time_str(self.minutes, self.seconds)
        self.lcd.setDigitCount(len(init_time))
        self.lcd.display(init_time)

        main_layout.addWidget(self.lcd)
 
        btn_layout = QtGui.QHBoxLayout()
        self.btn_start = QtGui.QPushButton(QtGui.QIcon(START_ICON),
                                           "Start", self)

        btn_layout.addWidget(self.btn_start)
        self.btn_stop = QtGui.QPushButton(QtGui.QIcon(STOP_ICON),
                                          "Stop", self)
        btn_layout.addWidget(self.btn_stop)

        self.btn_reset = QtGui.QPushButton(QtGui.QIcon(RESET_ICON),
                                           "Reset", self)
        btn_layout.addWidget(self.btn_reset)
        btn_layout.addStretch()

        main_layout.addLayout(btn_layout)

        self.shown = False

        self.tasks = QtGui.QTableWidget()
        self.tasks.setAlternatingRowColors(True)
        self.tasks.setColumnCount(1)
        self.tasks.setVisible(self.shown)

        header = self.tasks.horizontalHeader()
        header.setResizeMode(0, QtGui.QHeaderView.Stretch)
        header.setVisible(False)

        main_layout.addWidget(self.tasks)

        central_widget = QtGui.QWidget()
 
        self.setCentralWidget(central_widget)
 
        central_widget.setLayout(main_layout)
        self.setGeometry(300, 300, 280, 170)

        self.tray_icon = QtGui.QSystemTrayIcon(self)
        self.logo = QtGui.QIcon()
        self.logo.addPixmap(QtGui.QPixmap(LOGO_IMAGE),
                       QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.tray_icon.setIcon(self.logo)
        self.tray_icon.show()

        self.setWindowIcon(self.logo)

        self.timer_thread = PyradaizThread(self)
        self.connect(self.timer_thread,
                     QtCore.SIGNAL("update_display(QString)"),
                     self.update)
        self.connect(self.timer_thread, QtCore.SIGNAL("take_a_break(QString)"),
                     self.show_message)
        self.connect(self.timer_thread, QtCore.SIGNAL("go_on(QString)"),
                     self.show_message)

        self.create_actions()
        self.create_menu()
        self.create_context_menu()

    def create_actions(self):
        """
        Create actions and assign them to the buttons.
        """
        self.start_action = StartAction(self)
        self.btn_start.clicked.connect(self.start_action.do)

        self.stop_action = StopAction(self)
        self.btn_stop.clicked.connect(self.stop_action.do)

        self.reset_action = ResetAction(self)
        self.btn_reset.clicked.connect(self.reset_action.do)
        self.quit_action = QuitAction(self)

        self.settings_action = SettingsAction(self)

    def create_menu(self):
        """
        Creates menu.
        """
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(self.quit_action)

        tasks_menu = self.menuBar().addMenu("&Tasks")

        settings_menu = self.menuBar().addMenu("&Settings")
        settings_menu.addAction(self.settings_action)

        about_menu = self.menuBar().addMenu("&About")

    def create_context_menu(self):
        """
        Creates context menu used for system tray icon.
        """
        self.context_menu = QtGui.QMenu()
        self.tray_icon.setContextMenu(self.context_menu)

        self.context_menu.addAction(self.start_action)
        self.context_menu.addAction(self.stop_action)
        self.context_menu.addSeparator()
        self.context_menu.addAction(self.reset_action)
        self.context_menu.addSeparator()
        self.context_menu.addAction(self.quit_action)

    def update(self, time):
        """
        Updates GUI.
        :param time: time which will be set to the counter.
        """
        self.lcd.display(time)

    def show_message(self, minutes):
        """
        Shows notifications.
        :param minutes: break length.
        """
        if minutes == "go_on":
            title = GO_ON
        else:
            title = TAKE_A_BREAK % minutes
        icon = QtGui.QSystemTrayIcon.Information
        self.tray_icon.showMessage(title, "", icon, 5000)
