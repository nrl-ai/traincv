import os
import typing

from PyQt5 import uic
from PyQt5.QtWidgets import (QApplication, QFileDialog, QMainWindow,
                             QMessageBox, QWidget)

from ..project_dialog.project_dialog import ProjectDialog


class SideBar(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        current_dir = os.path.dirname(__file__)
        uic.loadUi(os.path.join(current_dir, "sidebar.ui"), self)

        self.open_project_button.clicked.connect(self.browse_and_open_project)
        self.new_project_button.clicked.connect(self.browse_and_create_project)

        self.project_dialog = ProjectDialog()

    def browse_and_create_project(self):
        self.project_dialog.show()
        return
        folder = str(
            QFileDialog.getExistingDirectory(
                self, "Select folder to save new project"
            )
        )
        if folder:
            folder = os.path.normpath(folder)

    def browse_and_open_project(self):
        self.project_dialog.show()
        return
        folder = str(
            QFileDialog.getExistingDirectory(self, "Select project to open")
        )
        if folder:
            folder = os.path.normpath(folder)
            if not os.path.isfile(os.path.join(folder, "trainme.xml")):
                QMessageBox.warning(
                    self, "Error", f"Invalid project folder: {folder}"
                )
                return
