import json

from PyQt5 import QtCore, QtGui, QtWidgets


class ScrollAreaPreview(QtWidgets.QScrollArea):
    def __init__(self, *args, **kwargs):
        super(ScrollAreaPreview, self).__init__(*args, **kwargs)

        self.setWidgetResizable(True)

        content = QtWidgets.QWidget(self)
        self.setWidget(content)

        layout = QtWidgets.QVBoxLayout(content)

        self.label = QtWidgets.QLabel(content)
        self.label.setWordWrap(True)

        layout.addWidget(self.label)

    def set_text(self, text):
        self.label.setText(text)

    def set_pixmap(self, pixmap):
        self.label.setPixmap(pixmap)

    def clear(self):
        self.label.clear()


class FileDialogPreview(QtWidgets.QFileDialog):
    def __init__(self, *args, **kwargs):
        super(FileDialogPreview, self).__init__(*args, **kwargs)
        self.setOption(self.DontUseNativeDialog, True)

        self.labelPreview = ScrollAreaPreview(self)
        self.labelPreview.setFixedSize(300, 300)
        self.labelPreview.setHidden(True)

        box = QtWidgets.QVBoxLayout()
        box.addWidget(self.labelPreview)
        box.addStretch()

        self.setFixedSize(self.width() + 300, self.height())
        self.layout().addLayout(box, 1, 3, 1, 1)
        self.currentChanged.connect(self.on_change)

    def on_change(self, path):
        if path.lower().endswith(".json"):
            with open(path, "r") as f:
                data = json.load(f)
                self.labelPreview.set_text(
                    json.dumps(data, indent=4, sort_keys=False)
                )
            self.labelPreview.label.setAlignment(
                QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop
            )
            self.labelPreview.setHidden(False)
        else:
            pixmap = QtGui.QPixmap(path)
            if pixmap.isNull():
                self.labelPreview.clear()
                self.labelPreview.setHidden(True)
            else:
                self.labelPreview.set_pixmap(
                    pixmap.scaled(
                        self.labelPreview.width() - 30,
                        self.labelPreview.height() - 30,
                        QtCore.Qt.KeepAspectRatio,
                        QtCore.Qt.SmoothTransformation,
                    )
                )
                self.labelPreview.label.setAlignment(QtCore.Qt.AlignCenter)
                self.labelPreview.setHidden(False)
