import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget


class ExportTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.name = "Export"

        current_dir = os.path.dirname(__file__)
        uic.loadUi(os.path.join(current_dir, "export.ui"), self)

    def on_open(self):
        pass

    def on_close(self):
        return True
