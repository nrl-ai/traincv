import os

import cv2
from imutils import paths
from PyQt5 import QtGui, uic
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget


class EvaluationTab(QWidget):

    change_pixmap = pyqtSignal(QImage)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.name = "Evaluation"

        current_dir = os.path.dirname(__file__)
        uic.loadUi(os.path.join(current_dir, "evaluation.ui"), self)

        self.test_image_button.clicked.connect(self.test_image)
        self.test_image_folder_button.clicked.connect(self.test_image_folder)
        self.change_pixmap.connect(self.set_image)
        self.next_image_button.clicked.connect(self.next_image)
        self.prev_image_button.clicked.connect(self.prev_image)

        self.threshold_slider.valueChanged.connect(self.threshold_changed)
        self.threshold_slider.sliderPressed.connect(self.slider_disconnect)
        self.threshold_slider.sliderReleased.connect(self.slider_reconnect)

        self.image_list = []
        self.current_image_id = -1

        self.threshold = 0.5
        self.threshold_slider.setValue(self.threshold * 10000)
        self.threshold_changed()

    def write_log(self, log):
        self.log_edit.append(log)
        log_content = self.log_edit.toPlainText()
        log_content = log_content.replace("\n\n", "\n")
        if len(log_content) > 5000:
            self.log_edit.setPlainText(log_content[-5000:])
        self.log_edit.moveCursor(QtGui.QTextCursor.End)

    def eval_error(self, error):
        QMessageBox.warning(self, "Error", error)

    def eval_success(self, report):
        pass

    def slider_disconnect(self):
        self.threshold_slider.valueChanged.disconnect()

    def slider_reconnect(self):
        self.threshold_slider.valueChanged.connect(self.threshold_changed)
        self.sender().valueChanged.emit(self.sender().value())

    def threshold_changed(self):
        self.threshold = self.threshold_slider.value() / 10000.0
        self.threshold_label.setText(f"{self.threshold * 100:.2f}%")
        self.infer_current_image()

    def on_open(self):
        pass

    def test_image(self):
        path = str(
            QFileDialog.getOpenFileName(
                self,
                "Open image",
                "",
                "Image files (*.png *.jpg *.jpeg *.bmp)",
            )[0]
        )
        if path:
            path = os.path.normpath(path)
            if os.path.isfile(path):
                img = cv2.imread(path)
                if img is None:
                    self.image_view.setText(
                        f"Could not read image file: {path}"
                    )
                    return
                self.image_list = [path]
                self.current_image_id = 0
                self.infer_current_image()

    def test_image_folder(self):
        path = str(QFileDialog.getExistingDirectory(self, "Open image folder"))
        if path:
            path = os.path.normpath(path)
            if os.path.isdir(path):
                self.image_list = list(paths.list_images(path))
                if len(self.image_list) == 0:
                    self.current_image_id = -1
                    self.image_view.setText("No Image")
                else:
                    self.current_image_id = 0
                    self.infer_current_image()

    def run_infer(self, image):
        return True, image

    def infer_current_image(self):
        if self.current_image_id < 0 or self.current_image_id >= len(
            self.image_list
        ):
            self.image_view.setText("No Image")
        else:
            self.image_view.setText("Running Inference...")
            frame = cv2.imread(self.image_list[self.current_image_id])
            ret, result_frame = self.run_infer(frame)
            if not ret:
                self.image_view.setText(
                    "Failed to run inference on image:"
                    f" {self.image_list[self.current_image_id]}"
                )
            rgb_image = cv2.cvtColor(result_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_qt_format = QImage(
                rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888
            )
            p = convert_to_qt_format.scaled(640, 480, Qt.KeepAspectRatio)
            self.change_pixmap.emit(p)

        # Update button status
        self.prev_image_button.setEnabled(self.current_image_id > 0)
        self.next_image_button.setEnabled(
            self.current_image_id < len(self.image_list) - 1
        )

    def next_image(self):
        if self.current_image_id < len(self.image_list) - 1:
            self.current_image_id += 1
            self.infer_current_image()

    def prev_image(self):
        if self.current_image_id > 0:
            self.current_image_id -= 1
            self.infer_current_image()

    @pyqtSlot(QImage)
    def set_image(self, image):
        self.image_view.setPixmap(QPixmap.fromImage(image))

    def on_close(self):
        return True

    def on_open(self):
        pass
