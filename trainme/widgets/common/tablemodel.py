import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, Qt, pyqtSignal


class TableModel(QAbstractTableModel):
    table_changed = pyqtSignal(pd.DataFrame)

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self.data = data
        self.editable_cols = []

    def setEditableCols(self, cols):
        self.editable_cols = cols

    def rowCount(self, _):
        return self.data.shape[0]

    def columnCount(self, _):
        return self.data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self.data.iloc[index.row(), index.column()])
            column_count = self.columnCount(self)
            for column in range(0, column_count):
                if index.column() == column and role == Qt.TextAlignmentRole:
                    return Qt.AlignLeft | Qt.AlignVCenter
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.data.columns[col]
        return None

    def addRow(self, row: dict) -> bool:
        self.data = self.data.append(row, ignore_index=True)
        self.table_changed.emit(self.data)
        self.modelReset.emit()

    def removeRow(self, row: int) -> bool:
        self.data.drop(self.data.index[row], inplace=True)
        self.table_changed.emit(self.data)
        self.modelReset.emit()

    def removeRows(self, rows: list):
        rows = sorted(set(rows), reverse=True)
        for row in rows:
            self.removeRow(row)

    def setData(self, index, value, role=Qt.EditRole):

        if not index.isValid():
            return False

        if role != Qt.EditRole:
            return False

        row = index.row()
        if row < 0 or row >= len(self.data.values):
            return False

        column = index.column()
        if column < 0 or column >= self.data.columns.size:
            return False

        self.data.values[row][column] = value

        self.dataChanged.emit(index, index)
        self.on_changed_cb(self.data)

        return True

    def flags(self, index):
        flags = QAbstractTableModel.flags(self, index)
        if index.column() in self.editable_cols:
            flags |= Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return flags
