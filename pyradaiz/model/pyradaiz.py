import sys
from PyQt4 import QtGui, QtCore
from pyradaiz.model.actions import StartAction, StopAction, QuitAction, \
    ResetAction
from pyradaiz.model.consts import SHORT_BREAK, POMODORO_DURATION, UP_ARROW_ICON, \
    DOWN_ARROW_ICON, GO_ON, TAKE_A_BREAK, LONG_BREAK, LOGO_IMAGE, START_ICON, \
    STOP_ICON
from pyradaiz import icons


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


class PyradaizThread(QtCore.QThread):
    """
    Thread that modifies the counter and gives notifications about breaks.
    """
    def __init__(self, minutes, seconds, *args, **kwargs):
        super(PyradaizThread, self).__init__(*args, **kwargs)
        self.minutes = minutes
        self.seconds = seconds
        self.pomodoro_cnt = 0
        # Shows if it's time to nofity about the break or not.
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
                    self.minutes = SHORT_BREAK if self.pomodoro_cnt % 3 != 0 \
                        else LONG_BREAK
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

        self.minutes = POMODORO_DURATION
        self.seconds = 0
        self.tasks = []
        self.running = False

        init_time = time_str(self.minutes, self.seconds)
        self.lcd.setDigitCount(len(init_time))
        self.lcd.display(init_time)

        main_layout.addWidget(self.lcd)
 
        btn_layout = QtGui.QHBoxLayout()
        self.btn_start = QtGui.QPushButton("Start", self)
        # self.btn_start.clicked.connect(self.start_action)

        btn_layout.addWidget(self.btn_start)
        self.btn_stop = QtGui.QPushButton("Stop", self)
        # self.btn_stop.clicked.connect(self.end_action)
        btn_layout.addWidget(self.btn_stop)

        self.btn_reset = QtGui.QPushButton("Reset", self)
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

        self.timer_thread = PyradaizThread(None, None)
        self.connect(self.timer_thread,
                     QtCore.SIGNAL("update_display(QString)"),
                     self.update)
        self.connect(self.timer_thread, QtCore.SIGNAL("take_a_break(QString)"),
                     self.show_message)
        self.connect(self.timer_thread, QtCore.SIGNAL("go_on(QString)"),
                     self.show_message)

        self.create_actions()
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
        self.context_menu.addAction(QuitAction(self.context_menu))

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
