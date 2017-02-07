import os
from xml.etree.ElementTree import ElementTree, Element, SubElement
from PyQt5 import QtWidgets, QtCore, QtGui
from model.actions import StartAction, StopAction, QuitAction, \
    ResetAction, SettingsAction, TasksAction, AboutAction, ChangeUI
from model.consts import SHORT_BREAK, POMODORO_DURATION,\
    GO_ON, TAKE_A_BREAK, LONG_BREAK, LOGO_IMAGE, ALWAYS_ON_TOP_NO, \
    ALWAYS_ON_TOP_YES, TOOLBAR_ICON_MAX_SIZE, TOOLBAR_ICON_MIN_SIZE
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
        self._always_on_top = ALWAYS_ON_TOP_NO

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

        always_on_top = SubElement(root, "always_on_top")
        always_on_top.text = self.always_on_top

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
                self.always_on_top = root.find("always_on_top").text
        except FileNotFoundError:
            pass

    @property
    def pomodoro_duration(self):
        return self._pomodoro_duration

    @pomodoro_duration.setter
    def pomodoro_duration(self, duration):
        self._pomodoro_duration = duration
        self.parent.minutes = duration

    @property
    def always_on_top(self):
        return self._always_on_top

    @always_on_top.setter
    def always_on_top(self, value):
        self._always_on_top = value

        if value == ALWAYS_ON_TOP_YES:
            self.parent.setWindowFlags(self.parent.windowFlags()
                                       | QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.parent.setWindowFlags(self.parent.windowFlags()
                                       & ~QtCore.Qt.WindowStaysOnTopHint)
        # Show must be called after the window flags are changed.
        self.parent.show()


class PyradaizThread(QtCore.QThread):
    """
    Thread that modifies the counter and gives notifications about breaks.
    """
    # update_display = QtCore.pyqtSignal(['QString'])
    def __init__(self, parent, update_signal, take_a_break_signal,
                 go_on_signal):
        super(PyradaizThread, self).__init__()
        self.parent = parent
        self.update_signal = update_signal
        self.take_a_break_signal = take_a_break_signal
        self.go_on_signal = go_on_signal
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
            print("Running thread...")
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

                    # self.emit(QtCore.SIGNAL("take_a_break(QString)"),
                    #           "%s" % self.minutes)
                    self.take_a_break_signal.emit(self.minutes)
                else:
                    self.minutes = POMODORO_DURATION
                    # self.emit(QtCore.SIGNAL("go_on(QString)"), "go_on")
                    self.go_on_signal.emit(self.minutes)

                self._break = not self._break

            print("Update display...")
            print(self.time)
            self.update_signal.emit(self.time)
            # self.emit(QtCore.SIGNAL("update_display(QString)"), self.time)
            # This ensures that the display is updated every second.
            self.sleep(1)

    @property
    def time(self):
        """
        Returns current time in minutes and seconds, as a tuple.
        :return tuple
        """
        return time_str(self.minutes, self.seconds)


class PyradaizGui(QtWidgets.QMainWindow):
    """
    Main window.
    """

    # Signal definitions...
    update_display = QtCore.pyqtSignal(['QString'])
    take_a_break = QtCore.pyqtSignal(['QString'])
    go_on = QtCore.pyqtSignal(['QString'])

    def __init__(self, *args, **kwargs):
        super(PyradaizGui, self).__init__(*args, **kwargs)
        main_layout = QtWidgets.QVBoxLayout()
        self.slim_view = False

        self.setWindowTitle("Pyradaiz")
 
        self.lcd = QtWidgets.QLCDNumber(self)

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

        self.shown = False

        self.tasks = QtWidgets.QTableWidget()
        self.tasks.setAlternatingRowColors(True)
        self.tasks.setColumnCount(1)
        self.tasks.setVisible(self.shown)

        header = self.tasks.horizontalHeader()
        # header.setResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setVisible(False)

        main_layout.addWidget(self.tasks)

        central_widget = QtWidgets.QWidget()
 
        self.setCentralWidget(central_widget)
 
        central_widget.setLayout(main_layout)
        self.setGeometry(300, 300, 280, 130)

        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.logo = QtGui.QIcon()
        self.logo.addPixmap(QtGui.QPixmap(LOGO_IMAGE),
                       QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.tray_icon.setIcon(self.logo)
        self.tray_icon.show()

        self.setWindowIcon(self.logo)

        self.timer_thread = PyradaizThread(self, self.update_display,
                                           self.take_a_break, self.go_on)
        self.update_display.connect(self.update)
        self.take_a_break.connect(self.show_message)
        self.go_on.connect(self.show_message)

        self.create_actions()
        self.create_toolbar()
        self.create_context_menu()

    def create_actions(self):
        """
        Create actions and assign them to the buttons.
        """
        self.start_action = StartAction(self)
        self.stop_action = StopAction(self)
        self.reset_action = ResetAction(self)
        self.quit_action = QuitAction(self)
        self.tasks_action = TasksAction(self)
        self.settings_action = SettingsAction(self)
        self.about_action = AboutAction(self)
        self.change_ui_action = ChangeUI(self)

    def create_toolbar(self):
        """
        Creates menu.
        """
        self.toolbar = self.addToolBar("Toolbar")
        self.toolbar.setIconSize(TOOLBAR_ICON_MAX_SIZE)
        self.toolbar.addAction(self.start_action)
        self.toolbar.addAction(self.stop_action)
        self.toolbar.addAction(self.reset_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.tasks_action)
        self.toolbar.addAction(self.settings_action)
        self.toolbar.addAction(self.about_action)
        self.toolbar.addAction(self.quit_action)
        self.toolbar.addAction(self.change_ui_action)

    def create_context_menu(self):
        """
        Creates context menu used for system tray icon.
        """
        self.context_menu = QtWidgets.QMenu()
        self.tray_icon.setContextMenu(self.context_menu)

        self.context_menu.addAction(self.start_action)
        self.context_menu.addAction(self.stop_action)
        self.context_menu.addSeparator()
        self.context_menu.addAction(self.reset_action)
        self.context_menu.addSeparator()
        self.context_menu.addAction(self.settings_action)
        self.context_menu.addAction(self.about_action)
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
        icon = QtWidgets.QSystemTrayIcon.Information
        self.tray_icon.showMessage(title, "", icon, 5000)

    def toggle_ui(self):
        """
        Toggle UI between slim and regular view.
        """
        if not self.slim_view:
            self.toolbar.setIconSize(TOOLBAR_ICON_MIN_SIZE)
            self.addToolBar(QtCore.Qt.RightToolBarArea, self.toolbar)
            self.resize(175, 75)
            self.slim_view = True
        else:
            self.toolbar.setIconSize(TOOLBAR_ICON_MAX_SIZE)
            self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolbar)
            self.resize(280, 130)
            self.slim_view = False
