import os

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QTableView


class TableViewWidget(QTableView):
    new_data_items = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.parent = parent

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
                link = os.path.normpath(link)
                links.append(link)

            self.new_data_items.emit(links)
        else:
            event.ignore()
