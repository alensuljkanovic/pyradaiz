import sys
from PyQt5 import QtWidgets
from model.pyradaiz import PyradaizGui

__author__ = 'Alen Suljkanovic'

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    view = PyradaizGui()
    view.show()

    app.setStyle('cleanlooks')

    sys.exit(app.exec_())
