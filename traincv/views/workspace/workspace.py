from PyQt5 import QtCore
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget

from traincv.views.workspace.experiment_wizard import ExperimentWizard
from traincv.views.workspace.sidebar.sidebar import SideBar


class WorkspaceWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.sidebar = SideBar(self)
        self.sidebar.setMaximumWidth(320)
        self.sidebar.setMinimumWidth(250)

        self.wizard = ExperimentWizard(self)

        self.empty_wizard_label = QLabel(
            "Please select or create an experiment"
        )
        self.empty_wizard_label.setStyleSheet(
            "QLabel {background-color: #EFEFEF; color: #888888;}"
        )
        self.empty_wizard_label.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.empty_wizard_label.setAlignment(QtCore.Qt.AlignCenter)

        self.layout.addWidget(self.sidebar)
        self.layout.addWidget(self.empty_wizard_label)
