import os
import sys

import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.append(".")

from traincv.resources.resources import *
from traincv.views.mainwindow import MainWindow


def main():
    # Enable scaling for high dpi screens
    QtWidgets.QApplication.setAttribute(
        QtCore.Qt.AA_EnableHighDpiScaling, True
    )  # enable highdpi scaling
    QtWidgets.QApplication.setAttribute(
        QtCore.Qt.AA_UseHighDpiPixmaps, True
    )  # use highdpi icons

    # Setup pyqtgraph default bg/fg colors
    pg.setConfigOption("background", "w")
    pg.setConfigOption("foreground", "k")

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    app.processEvents()

    main_win = MainWindow(app)

    main_win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
