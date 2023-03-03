import json
import os
import pathlib
from datetime import datetime

from .exceptions import ProjectValidationError
from .tasks import TaskChoices


class Project:
    """traincv Project"""

    PROJECT_CONFIG_FILENAME = "traincv.project"

    def __init__(self):
        self.name = "Untitled"
        self.task = None
        self.author = None
        self.license = None
        self.description = None
        self.created_date = datetime.now()
        self.last_modified_date = datetime.now()
        self.project_folder = None

    @property
    def project_config_path(self):
        """Get project configuration file path"""
        return os.path.join(
            self.project_folder, Project.PROJECT_CONFIG_FILENAME
        )

    @staticmethod
    def open(project_folder):
        project_config_path = os.path.join(
            project_folder, Project.PROJECT_CONFIG_FILENAME
        )
        if not os.path.isfile(project_config_path):
            raise ProjectValidationError(
                "Wrong project configuration file path"
            )
        if (
            os.path.basename(project_config_path)
            != Project.PROJECT_CONFIG_FILENAME
        ):
            raise ProjectValidationError("Invalid project configuration file")

        project = Project()
        with open(project_config_path, "r") as f:
            data = json.load(f)
            project.project_folder = os.path.dirname(project_config_path)
            project.name = data["name"]
            project.task = TaskChoices(data["task"])
            project.author = data["author"]
            project.license = data["license"]
            project.description = data["description"]
            project.created_date = datetime.fromisoformat(data["created_date"])
            project.last_modified_date = datetime.fromisoformat(
                data["last_modified_date"]
            )
        return project

    @staticmethod
    def create(
        name: str = None,
        task: TaskChoices = TaskChoices.OBJECT_DETECTION,
        author: str = None,
        project_license: str = None,
        description: str = None,
        project_folder: str = None,
    ):
        """Create a new project"""
        if project_folder is None:
            raise ProjectValidationError("Project folder must be specified")
        project = Project()
        project.name = name
        project.task = task
        project.author = author
        project.license = project_license
        project.description = description
        project.project_folder = project_folder
        project.save()
        return project

    def save(self):
        """Initialize project folder"""
        # Create project folder
        pathlib.Path(self.project_folder).mkdir(exist_ok=True, parents=True)
        # Save project configs
        self.save_project_configs()

    def save_project_configs(self):
        """Save project configuration file"""
        self.last_modified_date = datetime.now()
        data = {
            "name": self.name,
            "task": self.task.value,
            "author": self.author,
            "license": self.license,
            "description": self.description,
            "created_date": self.created_date.isoformat(),
            "last_modified_date": self.last_modified_date.isoformat(),
        }
        with open(self.project_config_path, "w") as f:
            json.dump(data, f, indent=4)
