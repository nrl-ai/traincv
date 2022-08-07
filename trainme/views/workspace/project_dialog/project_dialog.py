import os

from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import QDialog


class ProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

        current_dir = os.path.dirname(__file__)
        uic.loadUi(os.path.join(current_dir, "project_dialog.ui"), self)

        self.setWindowTitle("Project Configuration")
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.close_button.clicked.connect(self.close)
