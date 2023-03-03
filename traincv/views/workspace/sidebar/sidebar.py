import logging
import os

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QFileDialog, QWidget

from traincv.storage import project_model
from traincv.trainer.core.project import Project

from ..project_dialog.project_dialog import ProjectDialog
from .experiment_table_model import ExperimentTableModel


class SideBar(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        current_dir = os.path.dirname(__file__)
        uic.loadUi(os.path.join(current_dir, "sidebar.ui"), self)

        project_model.project_updated.connect(self.load_project)

        self.project_dialog = ProjectDialog(project_model)
        self.experiment_table_model = ExperimentTableModel([])
        self.experiment_table.setModel(self.experiment_table_model)
        self.experiment_table.update()

        self.open_project_button.clicked.connect(self.browse_and_open_project)
        self.new_project_button.clicked.connect(self.browse_and_create_project)
        self.edit_project_button.clicked.connect(self.project_dialog.show)

    @pyqtSlot(Project)
    def load_project(self, project: Project):
        self.project_name_label.setText(project.name)
        html = f"""
        <b>Task:</b> {project.task.value}<br>
        <b>Author:</b> {project.author}<br>
        <b>License:</b> {project.license}<br>
        <b>Description:</b> {project.description}<br>
        <b>Project path:</b> {project.project_folder}<br>
        """
        self.project_description_edit.setHtml(html)

    def browse_and_create_project(self):
        self.project_dialog.show()
        folder = str(
            QFileDialog.getExistingDirectory(
                self, "Select folder to save new project"
            )
        )
        if folder:
            folder = os.path.normpath(folder)
            project_model.create_project(folder)

    def browse_and_open_project(self):
        folder = str(
            QFileDialog.getExistingDirectory(self, "Select project to open")
        )
        if folder:
            folder = os.path.normpath(folder)
            try:
                project_model.open_project(folder)
            except Exception as e:
                logging.error(e)
