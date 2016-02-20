import os
import sys
from PyQt4 import QtGui
from model.pyradaiz import PyradaizGui

__author__ = 'Alen Suljkanovic'

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    view = PyradaizGui()
    view.show()

    app.setStyle('cleanlooks')

    sys.exit(app.exec_())