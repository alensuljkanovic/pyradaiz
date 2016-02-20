
import sys
from PyQt4 import QtGui
from pyradaiz.model.pyradaiz import PyModoroGui

__author__ = 'Alen Suljkanovic'

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    view = PyModoroGui()
    view.show()

    app.setStyle('cleanlooks')

    sys.exit(app.exec_())