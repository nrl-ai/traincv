from PyQt5.QtWidgets import (QVBoxLayout, QWidget)

from .labelme.labelme.labelme_widget import LabelmeWidget


class LabelingWrapper(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        view = LabelmeWidget(self)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(view)
        self.setLayout(main_layout)
