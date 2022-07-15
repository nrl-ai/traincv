from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets


class EscapableQListWidget(QtWidgets.QListWidget):

    # QT Overload
    def keyPressEvent(self, event):
        super(EscapableQListWidget, self).keyPressEvent(event)
        if event.key() == Qt.Key_Escape:
            self.clearSelection()
