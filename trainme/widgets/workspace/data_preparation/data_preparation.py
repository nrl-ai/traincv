import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget

from .data_subset_table import DataSubsetTable


class DataPreparationTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.name = "Data"

        current_dir = os.path.dirname(__file__)
        uic.loadUi(os.path.join(current_dir, "data_preparation.ui"), self)

        self.training_set_table = DataSubsetTable(
            "Training", self, show_split_from_train=False
        )
        train_data_preparator = self.training_set_table.data_preparator
        self.validation_set_table = DataSubsetTable(
            "Validation", self, train_data_preparator=train_data_preparator
        )
        self.validation_set_table.split_ratio_spin.valueChanged.connect(
            self.training_set_table.update_statistics
        )
        self.test_set_table = DataSubsetTable(
            "Test", self, show_split_from_train=False
        )

        self.data_source_layout.addWidget(self.training_set_table)
        self.data_source_layout.addWidget(self.validation_set_table)
        self.data_source_layout.addWidget(self.test_set_table)

    def get_name(self):
        return self.name

    def on_close(self):
        return True

    def on_open(self):
        pass
