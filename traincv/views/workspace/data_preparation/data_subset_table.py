import os

import pandas as pd
from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import QFileDialog, QHeaderView, QWidget

from traincv.models.tablemodel import TableModel
from traincv.trainer.data.data_subset_preparator import DataSubsetPreparator
from traincv.views.common.toaster import QToaster


class DataSubsetTable(QWidget):
    DATA_FOLDER_TITLE = "Drop data folder here"
    DEFAULT_SPLIT_RATIO = 0.2

    def __init__(
        self,
        title,
        parent,
        show_split_from_train=True,
        train_data_preparator: DataSubsetPreparator = None,
    ):
        super().__init__()
        self.parent = parent
        self.train_data_preparator = train_data_preparator

        if show_split_from_train:
            if not train_data_preparator:
                raise Exception("Please specify a train_data_preparator")

        current_dir = os.path.dirname(__file__)
        uic.loadUi(os.path.join(current_dir, "data_subset_table.ui"), self)

        self.subset_title.setText(title)

        self.split_from_train = False
        self.split_ratio_slider.hide()
        self.split_ratio_spin.hide()
        if not show_split_from_train:
            self.split_from_train_checkbox.hide()

        data = pd.DataFrame({DataSubsetTable.DATA_FOLDER_TITLE: []})
        self.model = TableModel(data)
        self.data_sources_table.setModel(self.model)
        header = self.data_sources_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        self.data_sources_table.new_data_items.connect(
            self.verify_and_add_items
        )

        self.split_ratio_spin.setValue(DataSubsetTable.DEFAULT_SPLIT_RATIO)
        split_ratio_slider_value = int(
            DataSubsetTable.DEFAULT_SPLIT_RATIO
            * self.split_ratio_slider.maximum()
        )
        self.split_ratio_slider.setValue(split_ratio_slider_value)

        self.delete_folder_button.clicked.connect(self.delete_selected_rows)
        self.add_folder_button.clicked.connect(self.add_image_folder)
        self.split_from_train_checkbox.stateChanged.connect(
            self.split_from_train_changed
        )
        self.split_ratio_slider.valueChanged.connect(
            self.on_new_split_value_slider
        )
        self.split_ratio_spin.valueChanged.connect(
            self.on_new_split_value_spin
        )

        self.data_preparator = DataSubsetPreparator()

    def slider_disconnect(self):
        self.split_ratio_slider.valueChanged.disconnect()

    def slider_reconnect(self):
        self.split_ratio_slider.valueChanged.connect(
            self.on_new_split_value_slider
        )
        self.sender().valueChanged.emit(self.sender().value())

    def add_image_folder(self):
        path = str(QFileDialog.getExistingDirectory(self, "Add Image Folder"))
        if path:
            path = os.path.normpath(path)
            self.verify_and_add_items([path])

    def set_data(self, data):
        data_sources = []
        for i in range(len(data)):
            data_sources.append(data[i][DataSubsetTable.DATA_FOLDER_TITLE])
        pd_frame = pd.DataFrame(
            {DataSubsetTable.DATA_FOLDER_TITLE: data_sources}
        )
        self.model = TableModel(pd_frame)
        self.data_sources_table.setModel(self.model)

    def verify_and_add_items(self, links):
        for link in links:
            ret, message = self.data_preparator.is_valid_data_folder(link)
            if ret:
                self.model.addRow({DataSubsetTable.DATA_FOLDER_TITLE: link})
                data = message
                self.data_preparator.add_data_folder(data)
            else:
                corner = QtCore.Qt.Corner(QtCore.Qt.BottomRightCorner)
                QToaster.show_message(
                    self,
                    f"{message}: {link}",
                    corner=corner,
                    timeout=3000,
                    closable=True,
                )

        self.data_sources_table.clearSelection()
        self.data_sources_table.dataChanged(
            self.model.index(0, 0),
            self.model.index(
                self.model.rowCount(None), self.model.columnCount(None)
            ),
        )

        self.update_statistics()

    def update_statistics(self):
        """Update data statistics"""
        data_size = 0
        if self.split_from_train:
            data_size = self.train_data_preparator.split_size()
        else:
            data_size = self.data_preparator.size()

        self.data_statistic.setText(f"{data_size} labeled images")

    def delete_selected_rows(self):
        selected = self.data_sources_table.selectedIndexes()
        if len(selected) == 0:
            return
        rows = [i.row() for i in selected]
        self.data_preparator.remove_data_by_indices(rows)
        self.data_sources_table.clearSelection()
        self.data_sources_table.dataChanged(
            self.model.index(0, 0),
            self.model.index(
                self.model.rowCount(None), self.model.columnCount(None)
            ),
        )

        self.data_statistic.setText(
            f"{self.data_preparator.size()} labeled images"
        )

    @QtCore.pyqtSlot()
    def split_from_train_changed(self):
        self.split_from_train = self.split_from_train_checkbox.isChecked()
        if self.split_from_train:
            data = pd.DataFrame({DataSubsetTable.DATA_FOLDER_TITLE: []})
            self.set_data(data)
            self.data_sources_table.setEnabled(False)
            self.add_folder_button.setEnabled(False)
            self.delete_folder_button.setEnabled(False)
            self.data_preparator.clear()
            self.split_ratio_slider.show()
            self.split_ratio_spin.show()
        else:
            self.data_sources_table.setEnabled(True)
            self.add_folder_button.setEnabled(True)
            self.delete_folder_button.setEnabled(True)
            self.split_ratio_slider.hide()
            self.split_ratio_spin.hide()

    @QtCore.pyqtSlot()
    def on_new_split_value_slider(self):
        """Handle split value change from slider"""
        split_ratio = (
            self.sender().value()
            / self.sender().maximum()
            * self.split_ratio_spin.maximum()
        )
        self.split_ratio_spin.setValue(split_ratio)
        self.train_data_preparator.set_split_ratio(split_ratio)

    @QtCore.pyqtSlot()
    def on_new_split_value_spin(self):
        """Handle split value change from spin"""
        split_ratio_slider_value = int(
            self.sender().value() * self.split_ratio_slider.maximum()
        )
        self.slider_disconnect()
        self.split_ratio_slider.setValue(split_ratio_slider_value)
        self.slider_reconnect()
        self.train_data_preparator.set_split_ratio(self.sender().value())
        self.update_statistics()
