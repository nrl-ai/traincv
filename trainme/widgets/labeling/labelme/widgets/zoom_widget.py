from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets


class ZoomWidget(QtWidgets.QSpinBox):
    def __init__(self, value=100):
        super(ZoomWidget, self).__init__()
        self.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.setRange(1, 1000)
        self.setSuffix(" %")
        self.setValue(value)
        self.setToolTip("Zoom Level")
        self.setStatusTip(self.toolTip())
        self.setAlignment(QtCore.Qt.AlignCenter)

    # QT Overload
    def minimumSizeHint(self):
        height = super(ZoomWidget, self).minimumSizeHint().height()
        font_metric = QtGui.QFontMetrics(self.font())
        width = font_metric.horizontalAdvance(str(self.maximum()))
        return QtCore.QSize(width, height)
