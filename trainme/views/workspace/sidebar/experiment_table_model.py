from dataclasses import astuple

from PyQt5 import QtCore
from PyQt5.QtCore import QVariant


class ExperimentTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, _):
        return 0

    def columnCount(self, _):
        return 0

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        if role == QtCore.Qt.EditRole:
            return None
        if role != QtCore.Qt.DisplayRole:
            return None
        return astuple(self._data[index.row()])[index.column()]
