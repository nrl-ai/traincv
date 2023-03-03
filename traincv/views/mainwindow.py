"""This module defines the main application window"""

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QMainWindow, QStatusBar,
                             QVBoxLayout, QWidget)

from .maintabs import MainTabsWidget


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self, app):
        super().__init__()
        self.app = app

        self.setContentsMargins(0, 0, 0, 0)
        self.setWindowTitle("traincv")

        header_widget = QWidget(self)
        header_layout = QHBoxLayout(header_widget)
        program_title = QLabel("traincv - AI toolkit")
        program_title.setStyleSheet(
            "QLabel {background-color: #333; color: #fff; font: bold;}"
        )
        program_title.setFont(QFont("Arial", 16))
        header_layout.addWidget(program_title)
        header_widget.setStyleSheet("background-color: #333;")

        self.maintabs_widget = MainTabsWidget(self)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(header_widget)
        main_layout.addWidget(self.maintabs_widget)
        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        status_bar = QStatusBar()
        status_bar.showMessage(
            "traincv - No-code labeling and training toolkit"
        )
        self.setStatusBar(status_bar)
