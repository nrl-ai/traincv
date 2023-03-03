import os

from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import QDialog

from traincv.models.project import ProjectModel


class ProjectDialog(QDialog):
    project_saved = QtCore.pyqtSignal()

    def __init__(self, project_model: ProjectModel, parent=None):
        super().__init__()
        self.parent = parent

        current_dir = os.path.dirname(__file__)
        uic.loadUi(os.path.join(current_dir, "project_dialog.ui"), self)

        self.setWindowTitle("Project Configuration")
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.project_model = project_model
        self.project_model.project_updated.connect(self.load_project)
        self.project_saved.connect(self.project_model.save_project)

        self.close_button.clicked.connect(self.close)
        self.save_button.clicked.connect(self.save_project)

    def load_project(self, project):
        """Load project to UI"""
        self.name_edit.setText(project.name)
        self.author_edit.setText(project.author)
        self.license_edit.setText(project.license)
        self.description_edit.setPlainText(project.description)

    def save_project(self):
        """Save project from UI"""
        project = self.project_model.project
        project.name = self.name_edit.text()
        project.author = self.author_edit.text()
        project.license = self.license_edit.text()
        project.description = self.description_edit.toPlainText()
        self.project_model.project_updated.emit(project)
        self.project_saved.emit()
        self.close()
