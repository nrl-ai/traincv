import os
import pathlib
from datetime import datetime

from .exceptions import ProjectCreationError
from .tasks import TaskChoices


class Project:
    """TrainMe Project"""

    PROJECT_CONFIG_FILENAME = "TrainMe.project"

    def __init__(
        self,
        name: str,
        task: TaskChoices = TaskChoices.OBJECT_DETECTION,
        author: str = None,
        license: str = None,
        description: str = None,
        created_date: datetime = None,
        last_modified_date: datetime = None,
        path: str = None,
    ):
        self.name = name
        self.task = task
        self.author = author
        self.license = license
        self.description = description

        if created_date is None:
            created_date = datetime.now()
        if last_modified_date is None:
            last_modified_date = datetime.now()

        self.created_date = created_date
        self.last_modified_date = last_modified_date

        if path is None:
            raise ProjectCreationError("A project folder `path` is required")
        self.path = path
        self.init_project_folder()

    @property
    def project_config_path(self):
        """Get project configuration file path"""
        return os.path.join(self.path, Project.PROJECT_CONFIG_FILENAME)

    def init_project_folder(self):
        """Initialize project folder"""
        if os.path.exists(self.project_config_path):
            raise ProjectCreationError(
                "A project exists in selected path. Please choose another path"
            )

        # Create project folder
        pathlib.Path(self.path).mkdir(exist_ok=True, parents=True)

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
            f.write(str(data))
