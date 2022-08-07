import os

import pyqtgraph as pg
from PyQt5 import uic
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QWidget

from ....services.system_monitor import SystemMonitor
from .training_state import TrainingState


class TrainingTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.name = "Training"
        self.current_state = TrainingState.WAITING

        current_dir = os.path.dirname(__file__)
        uic.loadUi(os.path.join(current_dir, "training.ui"), self)

        # System monitor
        self.system_monitor = SystemMonitor(
            self.system_monitor_edit, seconds_between_refresh=2
        )
        self.train_button.clicked.connect(self.start_training)

    def draw_losses(self, losses):
        self.loss_graph.clear()
        plt = self.loss_graph.getPlotItem()
        plt.showGrid(x=True, y=True)
        plt.addLegend()
        plt.plot(
            losses["train_loss"],
            pen=pg.mkPen({"color": "orange", "width": 2}),
            symbol=None,
            name="train_loss",
        )
        plt.plot(
            losses["val_loss"],
            pen=pg.mkPen({"color": "blue", "width": 2}),
            symbol=None,
            name="val_loss",
        )

    def on_open(self):
        pass

    def start_training(self):
        self.log_edit.setPlainText("")
        self.current_state = TrainingState.INITIALIZING
        self.training_state.setText(self.current_state.value)
        train_config = {}
        train_config["model_name"] = self.model_name_combobox.currentText()
        train_config["num_epochs"] = self.num_epochs_spin.value()
        train_config["batch_size"] = self.batch_size_spin.value()
        train_config["learning_rate"] = self.learning_rate_spin.value()
        # TODO (vietanhdev): Start training here

    def on_close(self):
        return True
