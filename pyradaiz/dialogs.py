from model.consts import SETTINGS_LABEL_WIDTH, LINE_EDIT_WIDTH, \
    ALWAYS_ON_TOP_YES, ALWAYS_ON_TOP_NO
from PyQt5 import QtWidgets

__author__ = 'Alen Suljkanovic'


class SettingsDialog(QtWidgets.QDialog):
    """
    Dialog for changing the timer settings.
    """
    def __init__(self, parent):
        """
        Initialize dialog
        """
        super(SettingsDialog, self).__init__(parent)
        self.parent = parent
        settings = self.parent.settings
        self.pomodoro_duration = settings.pomodoro_duration
        self.short_break = settings.short_break
        self.long_break = settings.long_break

        self.init_ui()

    def init_ui(self):
        """
        Initializes the UI.
        """
        self.setWindowTitle("Settings")
        main_layout = QtWidgets.QVBoxLayout()

        # POMODORO DURATION

        pomodoro_layout = QtWidgets.QHBoxLayout()
        self.pomodoro_edit = QtWidgets.QLineEdit()
        self.pomodoro_edit.setText(str(self.pomodoro_duration))
        self.pomodoro_edit.setFixedWidth(LINE_EDIT_WIDTH)
        pomodoro_label = QtWidgets.QLabel("Pomodoro duration:")
        pomodoro_label.setFixedWidth(SETTINGS_LABEL_WIDTH)
        pomodoro_layout.addWidget(pomodoro_label)
        pomodoro_layout.addWidget(self.pomodoro_edit)
        pomodoro_layout.addWidget(QtWidgets.QLabel("minutes"))
        pomodoro_layout.addStretch()
        main_layout.addLayout(pomodoro_layout)

        # SHORT BREAK

        short_break_layout = QtWidgets.QHBoxLayout()
        self.short_break_edit = QtWidgets.QLineEdit()
        self.short_break_edit.setText(str(self.short_break))
        self.short_break_edit.setFixedWidth(LINE_EDIT_WIDTH)
        short_break_label = QtWidgets.QLabel("Short break duration:")
        short_break_label.setFixedWidth(SETTINGS_LABEL_WIDTH)

        short_break_layout.addWidget(short_break_label)
        short_break_layout.addWidget(self.short_break_edit)
        short_break_layout.addWidget(QtWidgets.QLabel("minutes"))
        short_break_layout.addStretch()
        main_layout.addLayout(short_break_layout)

        # LONG BREAK

        long_break_layout = QtWidgets.QHBoxLayout()
        self.long_break_edit = QtWidgets.QLineEdit()
        self.long_break_edit.setText(str(self.long_break))
        self.long_break_edit.setFixedWidth(LINE_EDIT_WIDTH)
        long_break_label = QtWidgets.QLabel("Long break duration:")
        long_break_label.setFixedWidth(SETTINGS_LABEL_WIDTH)

        long_break_layout.addWidget(long_break_label)
        long_break_layout.addWidget(self.long_break_edit)
        long_break_layout.addWidget(QtWidgets.QLabel("minutes"))
        long_break_layout.addStretch()

        main_layout.addLayout(long_break_layout)

        # ALWAYS ON TOP
        always_on_top_layout = QtWidgets.QHBoxLayout()
        always_on_top_label = QtWidgets.QLabel("Always on top:")
        always_on_top_label.setFixedWidth(SETTINGS_LABEL_WIDTH)
        always_on_top_layout.addWidget(always_on_top_label)
        self.always_on_top_cb = QtWidgets.QCheckBox()
        always_on_top_layout.addWidget(self.always_on_top_cb)
        always_on_top_layout.addStretch()

        if self.parent.settings.always_on_top == ALWAYS_ON_TOP_YES:
            self.always_on_top_cb.setChecked(True)
        else:
            self.always_on_top_cb.setChecked(False)

        main_layout.addLayout(always_on_top_layout)

        buttons_layout = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton("OK")
        ok_btn.clicked.connect(self.apply_changes)
        cancel_btn = QtWidgets.QPushButton("Cancel")
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
            QtWidgets.QMessageBox().critical(self, "Error", err_msg,
                                         QtWidgets.QMessageBox.Ok)
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
                    QtWidgets.QMessageBox().critical(self, "Error", err_msg,
                                                 QtWidgets.QMessageBox.Ok)
                    return False, value
            else:
                err_msg = "%s must be set"
                QtWidgets.QMessageBox().critical(self, "Error", err_msg,
                                                 QtWidgets.QMessageBox.Ok)
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

        if self.always_on_top_cb.isChecked():
            settings.always_on_top = ALWAYS_ON_TOP_YES
        else:
            settings.always_on_top = ALWAYS_ON_TOP_NO

        # Save changes...
        settings.save()

        # Update timer
        from model.pyradaiz import time_str
        time = time_str(self.parent.minutes, 0)
        self.parent.update(time)
        self.close()