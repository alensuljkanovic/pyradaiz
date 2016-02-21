from model.consts import SETTINGS_LABEL_WIDTH, LINE_EDIT_WIDTH, \
    POMODORO_DURATION, SHORT_BREAK, LONG_BREAK

__author__ = 'Alen Suljkanovic'

from PyQt4 import QtGui


class SettingsDialog(QtGui.QDialog):
    """
    Dialog for changing the timer settings.
    """
    def __init__(self, parent):
        """
        Initialize dialog
        """
        super(SettingsDialog, self).__init__(parent)
        self.parent = parent
        self.pomodoro_duration = self.parent.settings.pomodoro_duration
        self.short_break = self.parent.settings.short_break
        self.long_break = self.parent.settings.long_break

        self.init_ui()

    def init_ui(self):
        """
        Initializes the UI.
        """
        self.setWindowTitle("Settings")
        main_layout = QtGui.QVBoxLayout()

        # POMODORO DURATION

        pomodoro_layout = QtGui.QHBoxLayout()
        self.pomodoro_edit = QtGui.QLineEdit()
        self.pomodoro_edit.setText(str(self.pomodoro_duration))
        self.pomodoro_edit.setFixedWidth(LINE_EDIT_WIDTH)
        pomodoro_label = QtGui.QLabel("Pomodoro duration:")
        pomodoro_label.setFixedWidth(SETTINGS_LABEL_WIDTH)
        pomodoro_layout.addWidget(pomodoro_label)
        pomodoro_layout.addWidget(self.pomodoro_edit)
        pomodoro_layout.addWidget(QtGui.QLabel("minutes"))
        pomodoro_layout.addStretch()
        main_layout.addLayout(pomodoro_layout)

        # SHORT BREAK

        short_break_layout = QtGui.QHBoxLayout()
        self.short_break_edit = QtGui.QLineEdit()
        self.short_break_edit.setText(str(self.short_break))
        self.short_break_edit.setFixedWidth(LINE_EDIT_WIDTH)
        short_break_label = QtGui.QLabel("Short break duration:")
        short_break_label.setFixedWidth(SETTINGS_LABEL_WIDTH)

        short_break_layout.addWidget(short_break_label)
        short_break_layout.addWidget(self.short_break_edit)
        short_break_layout.addWidget(QtGui.QLabel("minutes"))
        short_break_layout.addStretch()
        main_layout.addLayout(short_break_layout)

        # LONG BREAK

        long_break_layout = QtGui.QHBoxLayout()
        self.long_break_edit = QtGui.QLineEdit()
        self.long_break_edit.setText(str(self.long_break))
        self.long_break_edit.setFixedWidth(LINE_EDIT_WIDTH)
        long_break_label = QtGui.QLabel("Long break duration:")
        long_break_label.setFixedWidth(SETTINGS_LABEL_WIDTH)

        long_break_layout.addWidget(long_break_label)
        long_break_layout.addWidget(self.long_break_edit)
        long_break_layout.addWidget(QtGui.QLabel("minutes"))
        long_break_layout.addStretch()

        main_layout.addLayout(long_break_layout)

        buttons_layout = QtGui.QHBoxLayout()
        ok_btn = QtGui.QPushButton("OK")
        ok_btn.clicked.connect(self.apply_changes)
        cancel_btn = QtGui.QPushButton("Cancel")
        cancel_btn.clicked.connect(lambda x: self.close())
        buttons_layout.addStretch()
        buttons_layout.addWidget(ok_btn)
        buttons_layout.addWidget(cancel_btn)
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

    def apply_changes(self):
        """
        Applies changes after the OK button is clicked.
        """
        if self.parent.running:
            err_msg = "Timer settings cannot be changed while the timer is " \
                      "running"
            QtGui.QMessageBox().critical(self, "Error", err_msg,
                                         QtGui.QMessageBox.Ok)
            return

        def validate(from_field, field_label):
            """
            Validates the value inserted into the line edit field.
            :param from_field: line edit field
            :param field_label: field label
            :return:
            """
            value = from_field.text()
            if value:
                try:
                    int_value = int(value)
                    return True, int_value
                except ValueError as ex:
                    err_msg = "%s must be an integer number!" % \
                              field_label
                    QtGui.QMessageBox().critical(self, "Error", err_msg,
                                                 QtGui.QMessageBox.Ok)
                    return False, value
            else:
                err_msg = "%s must be set"
                QtGui.QMessageBox().critical(self, "Error", err_msg,
                                                 QtGui.QMessageBox.Ok)
                return False, value

        settings = self.parent.settings
        valid, value = validate(self.pomodoro_edit, "Pomodoro duration")
        if valid:
            settings.pomodoro_duration = value

        valid, value = validate(self.short_break_edit, "Short break")
        if valid:
            settings.short_break = value

        valid, value = validate(self.long_break_edit, "Long break")
        if valid:
            settings.parent.long_break = value

        # Save changes...
        settings.save()

        # Update timer
        from model.pyradaiz import time_str
        time = time_str(self.parent.minutes, 0)
        self.parent.update(time)
        self.close()