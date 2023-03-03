from PyQt5.QtWidgets import QGridLayout, QWidget

from traincv.views.workspace.workspace import WorkspaceWidget


class WorkspaceWrapper(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        view = WorkspaceWidget(self)

        main_layout = QGridLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        central_widget = QWidget()
        central_widget.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(central_widget)
        layout = QGridLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(view, 0, 0, 1, 1)
        self.setLayout(main_layout)
