from PyQt5.QtWidgets import QHBoxLayout, QWidget

from trainme.widgets.workspace.experiment_wizard import ExperimentWizard
from trainme.widgets.workspace.sidebar.sidebar import SideBar


class WorkspaceWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        sidebar = SideBar(self)
        sidebar.setMaximumWidth(320)
        sidebar.setMinimumWidth(250)

        wizard = ExperimentWizard(self)

        self.layout.addWidget(sidebar)
        self.layout.addWidget(wizard)
