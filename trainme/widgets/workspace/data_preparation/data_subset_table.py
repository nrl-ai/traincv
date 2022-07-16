import os

import pandas as pd
from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import QFileDialog, QHeaderView, QWidget

from trainme.widgets.common.tablemodel import TableModel
from trainme.widgets.common.toaster import QToaster


class DataSubsetTable(QWidget):

    DATA_FOLDER_TITLE = "Drop data folder here"

    def __init__(self, title, parent, split_from_train=True):
        super().__init__()
        self.parent = parent

        current_dir = os.path.dirname(__file__)
        uic.loadUi(os.path.join(current_dir, "data_subset_table.ui"), self)

        self.subset_title.setText(title)

        if not split_from_train:
            self.split_from_train_checkbox.hide()
            self.split_ratio_slider.hide()
            self.split_ratio_spin.hide()

        data = pd.DataFrame({DataSubsetTable.DATA_FOLDER_TITLE: []})
        self.model = TableModel(data)

        self.data_sources_table.setModel(self.model)
        header = self.data_sources_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        self.data_sources_table.set_drop_callback(self.add_items)
        self.data_sources_table.set_data_validator(self.verify_data_folder)

        self.delete_folder_button.clicked.connect(self.delete_selected_rows)
        self.add_folder_button.clicked.connect(self.add_image_folder)

    def add_image_folder(self):
        path = str(QFileDialog.getExistingDirectory(self, "Add Image Folder"))
        if path:
            path = os.path.normpath(path)
            if os.path.isdir(path):
                self.add_items([path])
            else:
                corner = QtCore.Qt.Corner(QtCore.Qt.BottomRightCorner)
                QToaster.show_message(
                    self,
                    "Skipped not-folder items.",
                    "",
                    corner=corner,
                    timeout=3000,
                    closable=True,
                )

    def set_data(self, data):
        data_sources = []
        for i in range(len(data)):
            data_sources.append(data[i][DataSubsetTable.DATA_FOLDER_TITLE])
        pd_frame = pd.DataFrame(
            {DataSubsetTable.DATA_FOLDER_TITLE: data_sources}
        )
        self.model = TableModel(pd_frame, self.commit_pandas_data)
        self.data_sources_table.setModel(self.model)

    def add_items(self, links):
        for link in links:
            self.model.addRow({DataSubsetTable.DATA_FOLDER_TITLE: link})
        self.data_sources_table.clearSelection()
        self.data_sources_table.dataChanged(
            self.model.index(0, 0),
            self.model.index(
                self.model.rowCount(None), self.model.columnCount(None)
            ),
        )

    def delete_selected_rows(self):
        selected = self.data_sources_table.selectedIndexes()
        if len(selected) == 0:
            return
        rows = [i.row() for i in selected]
        rows = sorted(set(rows), reverse=True)
        for row in rows:
            self.model.removeRow(row)
        self.data_sources_table.clearSelection()
        self.data_sources_table.dataChanged(
            self.model.index(0, 0),
            self.model.index(
                self.model.rowCount(None), self.model.columnCount(None)
            ),
        )

    def commit_pandas_data(self, data: pd.DataFrame):
        data_dict = list(data.T.to_dict().values())
        self.parent.getState()["data_sources"] = data_dict
        self.parent.saveState()

    def verify_data_folder(self, path):
        if os.path.isdir(path):
            return True
        corner = QtCore.Qt.Corner(QtCore.Qt.BottomRightCorner)
        QToaster.show_message(
            self,
            "Skipped not-folder items.",
            "",
            corner=corner,
            timeout=3000,
            closable=True,
        )
        return False

    def on_close(self):
        return True
