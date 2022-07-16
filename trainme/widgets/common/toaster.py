import sys

from PyQt5 import QtCore, QtGui, QtWidgets


class QToaster(QtWidgets.QFrame):
    closed = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(QToaster, self).__init__(*args, **kwargs)
        QtWidgets.QHBoxLayout(self)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum
        )

        self.setStyleSheet(
            """
            QToaster {
                border: 1px solid black;
                border-radius: 0px;
                color: rgb(30, 30, 30);
                background-color: rgb(255, 255, 255);
            }
        """
        )
        # alternatively:
        self.setAutoFillBackground(True)
        self.setFrameShape(self.Box)

        self.timer = QtCore.QTimer(singleShot=True, timeout=self.hide)

        if self.parent():
            self.opacity_effect = QtWidgets.QGraphicsOpacityEffect(opacity=0)
            self.setGraphicsEffect(self.opacity_effect)
            self.opacity_ani = QtCore.QPropertyAnimation(
                self.opacity_effect, b"opacity"
            )
            # we have a parent, install an eventFilter so that when it's resized
            # the notification will be correctly moved to the right corner
            self.parent().installEventFilter(self)
        else:
            # there's no parent, use the window opacity property, assuming that
            # the window manager supports it; if it doesn't, this won'd do
            # anything (besides making the hiding a bit longer by half a
            # second)
            self.opacity_ani = QtCore.QPropertyAnimation(
                self, b"windowOpacity"
            )
        self.opacity_ani.setStartValue(0.0)
        self.opacity_ani.setEndValue(1.0)
        self.opacity_ani.setDuration(100)
        self.opacity_ani.finished.connect(self.check_closed)

        self.corner = QtCore.Qt.TopLeftCorner
        self.margin = 10

    def check_closed(self):
        # if we have been fading out, we're closing the notification
        if self.opacity_ani.direction() == self.opacity_ani.Backward:
            self.close()

    def restore(self):
        # this is a "helper function", that can be called from mouseEnterEvent
        # and when the parent widget is resized. We will not close the
        # notification if the mouse is in or the parent is resized
        self.timer.stop()
        # also, stop the animation if it's fading out...
        self.opacity_ani.stop()
        # ...and restore the opacity
        if self.parent():
            self.opacity_effect.setOpacity(1)
        else:
            self.setWindowOpacity(1)

    def hide(self):
        # start hiding
        self.opacity_ani.setDirection(self.opacity_ani.Backward)
        self.opacity_ani.setDuration(500)
        self.opacity_ani.start()

    def eventFilter(self, source, event):
        if source == self.parent() and event.type() == QtCore.QEvent.Resize:
            self.opacity_ani.stop()
            parent_rect = self.parent().rect()
            geo = self.geometry()
            if self.corner == QtCore.Qt.TopLeftCorner:
                geo.moveTopLeft(
                    parent_rect.topLeft()
                    + QtCore.QPoint(self.margin, self.margin)
                )
            elif self.corner == QtCore.Qt.TopRightCorner:
                geo.moveTopRight(
                    parent_rect.topRight()
                    + QtCore.QPoint(-self.margin, self.margin)
                )
            elif self.corner == QtCore.Qt.BottomRightCorner:
                geo.moveBottomRight(
                    parent_rect.bottomRight()
                    + QtCore.QPoint(-self.margin, -self.margin)
                )
            else:
                geo.moveBottomLeft(
                    parent_rect.bottomLeft()
                    + QtCore.QPoint(self.margin, -self.margin)
                )
            self.setGeometry(geo)
            self.restore()
            self.timer.start()
        return super(QToaster, self).event_filter(source, event)

    def enterEvent(self, _):
        self.restore()

    def leaveEvent(self, _):
        self.timer.start()

    def closeEvent(self, _):
        # we don't need the notification anymore, delete it!
        self.deleteLater()

    def resizeEvent(self, event):
        super(QToaster, self).resizeEvent(event)
        # if you don't set a stylesheet, you don't need any of the following!
        if not self.parent():
            # there's no parent, so we need to update the mask
            path = QtGui.QPainterPath()
            path.addRoundedRect(
                QtCore.QRectF(self.rect()).translated(-0.5, -0.5), 4, 4
            )
            self.setMask(
                QtGui.QRegion(
                    path.toFillPolygon(QtGui.QTransform()).toPolygon()
                )
            )
        else:
            self.clearMask()

    @staticmethod
    def show_message(
        parent,
        message,
        icon=QtWidgets.QStyle.SP_MessageBoxInformation,
        corner=QtCore.Qt.TopLeftCorner,
        margin=10,
        closable=True,
        timeout=5000,
        desktop=False,
        parent_window=True,
    ):

        if parent and parent_window:
            parent = parent.window()

        self.close_button = None

        if not parent or desktop:
            self = QToaster(None)
            self.setWindowFlags(
                self.windowFlags()
                | QtCore.Qt.FramelessWindowHint
                | QtCore.Qt.BypassWindowManagerHint
            )
            # This is a dirty hack!
            # parentless objects are garbage collected, so the widget will be
            # deleted as soon as the function that calls it returns, but if an
            # object is referenced to *any* other object it will not, at least
            # for PyQt (I didn't test it to a deeper level)
            self.__self = self

            current_screen = QtWidgets.QApplication.primaryScreen()
            if parent and parent.window().geometry().size().isValid():
                # the notification is to be shown on the desktop, but there is a
                # parent that is (theoretically) visible and mapped, we'll try to
                # use its geometry as a reference to guess which desktop shows
                # most of its area; if the parent is not a top level window, use
                # that as a reference
                reference = parent.window().geometry()
            else:
                # the parent has not been mapped yet, let's use the cursor as a
                # reference for the screen
                reference = QtCore.QRect(
                    QtGui.QCursor.pos() - QtCore.QPoint(1, 1),
                    QtCore.QSize(3, 3),
                )
            max_area = 0
            for screen in QtWidgets.QApplication.screens():
                intersected = screen.geometry().intersected(reference)
                area = intersected.width() * intersected.height()
                if area > max_area:
                    max_area = area
                    current_screen = screen
            parent_rect = current_screen.availableGeometry()
        else:
            self = QToaster(parent)
            parent_rect = parent.rect()

        self.timer.setInterval(timeout)

        self.label = QtWidgets.QLabel(message)
        self.label.setStyleSheet("color: rgb(33, 33, 33);")
        font = QtGui.QFont()
        font.setFamily("IRANYekanWeb")
        font.setPointSize(10)
        font.setWeight(100)
        self.label.setFont(font)
        self.layout().addWidget(self.label)

        if closable:
            self.close_button = QtWidgets.QToolButton()
            self.layout().addWidget(self.close_button)
            close_icon = self.style().standardIcon(
                QtWidgets.QStyle.SP_TitleBarCloseButton
            )
            self.close_button.setIcon(close_icon)
            self.close_button.setAutoRaise(True)
            self.close_button.clicked.connect(self.close)

        self.timer.start()

        # raise the widget and adjust its size to the minimum
        self.raise_()
        self.adjustSize()

        self.corner = corner
        self.margin = margin

        geo = self.geometry()
        # now the widget should have the correct size hints, let's move it to the
        # right place
        if corner == QtCore.Qt.TopLeftCorner:
            geo.moveTopLeft(
                parent_rect.topLeft() + QtCore.QPoint(margin, margin)
            )
        elif corner == QtCore.Qt.TopRightCorner:
            geo.moveTopRight(
                parent_rect.topRight() + QtCore.QPoint(-margin, margin)
            )
        elif corner == QtCore.Qt.BottomRightCorner:
            geo.moveBottomRight(
                parent_rect.bottomRight() + QtCore.QPoint(-margin, -margin)
            )
        else:
            geo.moveBottomLeft(
                parent_rect.bottomLeft() + QtCore.QPoint(margin, -margin)
            )

        self.setGeometry(geo)
        self.show()
        self.opacity_ani.start()


class W(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        layout = QtWidgets.QVBoxLayout(self)

        toaster_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(toaster_layout)

        self.text_edit = QtWidgets.QLineEdit("Ciao!")
        toaster_layout.addWidget(self.text_edit)

        self.corner_combo = QtWidgets.QComboBox()
        toaster_layout.addWidget(self.corner_combo)
        for pos in ("TopLeft", "TopRight", "BottomRight", "BottomLeft"):
            corner = getattr(QtCore.Qt, f"{pos}Corner")
            self.corner_combo.addItem(pos, corner)

        self.window_button = QtWidgets.QPushButton("Show window toaster")
        toaster_layout.addWidget(self.window_button)
        self.window_button.clicked.connect(self.show_toaster)

        self.screen_button = QtWidgets.QPushButton("Show desktop toaster")
        toaster_layout.addWidget(self.screen_button)
        self.screen_button.clicked.connect(self.show_toaster)

        # a random widget for the window
        layout.addWidget(QtWidgets.QTableView())

    def show_toaster(self):
        if self.sender() == self.window_button:
            parent = self
            desktop = False
        else:
            parent = None
            desktop = True
        corner = QtCore.Qt.Corner(self.corner_combo.currentData())
        QToaster.show_message(
            parent,
            self.text_edit.text(),
            QtWidgets.QStyle.SP_MessageBoxCritical,
            corner=corner,
            desktop=desktop,
            timeout=5000,
            closable=True,
        )


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = W()
    w.show()
    sys.exit(app.exec())
