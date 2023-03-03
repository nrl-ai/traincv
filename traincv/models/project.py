from PyQt5.QtCore import QObject, pyqtSignal

from traincv.trainer.core.project import Project


class ProjectModel(QObject):
    project_updated = pyqtSignal(Project)

    def __init__(self):
        super().__init__()
        self.project = None

    def create_project(self, project_folder):
        """Create a new project"""
        self.project = Project.create(project_folder=project_folder)
        self.project_updated.emit(self.project)

    def open_project(self, project_folder):
        """Open a project"""
        self.project = Project.open(project_folder)
        self.project_updated.emit(self.project)

    def save_project(self):
        """Save project to disk"""
        self.project.save()
