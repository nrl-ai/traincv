from asyncio.log import logger

from PyQt5.QtWidgets import QTabWidget

from traincv.views.workspace.data_preparation.data_preparation import \
    DataPreparationTab
from traincv.views.workspace.evaluation.evaluation import EvaluationTab
from traincv.views.workspace.export.export import ExportTab
from traincv.views.workspace.training.training import TrainingTab


class ExperimentWizard(QTabWidget):
    def __init__(self, parent):
        super().__init__()

        self.exp_path = None

        self.parent = parent
        self.tabs = []
        self.last_tab_index = 0
        self.currentChanged.connect(self.on_change)

        self.setStyleSheet(
            """
            QTabWidget::tab-bar {
                alignment: center;
            }
            """
        )
        self.setup_tabs()

    def setup_tabs(self):
        if len(self.tabs) != 0:
            logger.warning("Number of tabs is not 0.")

        self.data_preparation_tab = DataPreparationTab(self)
        self.tabs.append(self.data_preparation_tab)
        self.addTab(self.data_preparation_tab, self.data_preparation_tab.name)

        self.training_tab = TrainingTab(self)
        self.tabs.append(self.training_tab)
        self.addTab(self.training_tab, self.training_tab.name)

        self.evaluation_tab = EvaluationTab(self)
        self.tabs.append(self.evaluation_tab)
        self.addTab(self.evaluation_tab, self.evaluation_tab.name)

        self.export_tab = ExportTab(self)
        self.tabs.append(self.export_tab)
        self.addTab(self.export_tab, self.export_tab.name)

        self.last_tab_index = 0

    def on_change(self, i):
        if i == self.last_tab_index:
            return
        self.setCurrentWidget(self.tabs[self.last_tab_index])
        can_close = self.tabs[self.last_tab_index].on_close()
        if not can_close:
            return
        self.last_tab_index = i
        self.setCurrentWidget(self.tabs[i])
        self.tabs[i].on_open()

    def set_current_index(self, index):
        pass

    def switch_tab(self, tab_name):
        for tab in self.tabs:
            if tab.name == tab_name:
                self.setCurrentWidget(tab)
                break

    def enable_tab(self, tab_name):
        for i, tab in enumerate(self.tabs):
            if tab.name == tab_name:
                self.setTabEnabled(i, True)
                break

    def disable_tab(self, tab_name):
        for i, tab in enumerate(self.tabs):
            if tab.name == tab_name:
                self.setTabEnabled(i, False)
                break
