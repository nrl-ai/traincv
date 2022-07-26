"""This module contains table model for using with table widget
"""

import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, Qt, pyqtSignal


class TableModel(QAbstractTableModel):
    """Table model with Pandas data frame"""

    table_changed = pyqtSignal(pd.DataFrame)

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self.data = data
        self.editable_cols = []

    def setEditableCols(self, cols):
        """Set which colmumn can be edit"""
        self.editable_cols = cols

    def rowCount(self, _):
        """Return number of data rows"""
        return self.data.shape[0]

    def columnCount(self, _):
        """Return number of data columns"""
        return self.data.shape[1]

    def get_data(self, index, role=Qt.DisplayRole):
        """Get data by index and role"""
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self.data.iloc[index.row(), index.column()])
            column_count = self.columnCount(self)
            for column in range(0, column_count):
                if index.column() == column and role == Qt.TextAlignmentRole:
                    return Qt.AlignLeft | Qt.AlignVCenter
        return None

    def headerData(self, col, orientation, role):
        """Get header data"""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.data.columns[col]
        return None

    def addRow(self, row: dict) -> bool:
        """Add a new row to the table"""
        self.data = self.data.append(row, ignore_index=True)
        self.table_changed.emit(self.data)
        self.modelReset.emit()

    def removeRow(self, row: int) -> bool:
        """Remove a row from table"""
        self.data.drop(self.data.index[row], inplace=True)
        self.table_changed.emit(self.data)
        self.modelReset.emit()

    def removeRows(self, rows: list):
        """Remove a list of rows from table"""
        rows = sorted(set(rows), reverse=True)
        for row in rows:
            self.removeRow(row)

    def setData(self, index, value, role=Qt.EditRole):
        """Set data for a table cell"""

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
        """Get flags of a cell"""
        flags = QAbstractTableModel.flags(self, index)
        if index.column() in self.editable_cols:
            flags |= Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return flags
