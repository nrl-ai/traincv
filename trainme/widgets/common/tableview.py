import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableView


class TableViewWidget(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.parent = parent
        self.drop_callback = None
        self.data_validator = None

    def set_drop_callback(self, cb):
        self.drop_callback = cb

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()

            links = []
            for url in event.mimeData().urls():
                link = str(url.toLocalFile())
                if self.data_validator is not None:
                    if not self.data_validator(link):
                        continue
                link = os.path.normpath(link)
                links.append(link)

            if self.drop_callback is not None:
                self.drop_callback(links)
        else:
            event.ignore()

    def set_data_validator(self, func):
        self.data_validator = func
