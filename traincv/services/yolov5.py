import logging
import os
import pathlib

import cv2
import numpy as np
import yaml
from PyQt5 import QtCore

from traincv.views.labeling.labelme.shape import Shape
from traincv.views.labeling.labelme.utils.opencv import qt_img_to_cv_img

INPUT_WIDTH = 640
INPUT_HEIGHT = 640
SCORE_THRESHOLD = 0.5
NMS_THRESHOLD = 0.45
CONFIDENCE_THRESHOLD = 0.45


class YOLOv5Predictor:
    def __init__(self, config_path) -> None:
        if not os.path.isfile(config_path):
            raise Exception(f"Config file not found: {config_path}")

        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.check_missing_config(
            config_names=[
                "model_path",
                "input_width",
                "input_height",
                "score_threshold",
                "nms_threshold",
                "confidence_threshold",
                "classes",
            ],
            config=self.config,
        )

        config_folder = pathlib.Path(config_path).parent.absolute()
        model_path = self.config["model_path"]
        model_abs_path = os.path.join(config_folder, model_path)
        if not os.path.isfile(model_abs_path):
            raise Exception(f"Model not found: {model_abs_path}")

        self.net = cv2.dnn.readNet(model_abs_path)
        self.classes = self.config["classes"]

    def check_missing_config(self, config_names, config):
        for name in config_names:
            if name not in config:
                raise Exception(f"Missing config: {name}")

    def predict(self, image):
        detections = self.pre_process(image, self.net)
        results = self.post_process(image, detections)
        return results

    def pre_process(self, input_image, net):
        # Create a 4D blob from a frame.
        blob = cv2.dnn.blobFromImage(
            input_image,
            1 / 255,
            (self.config["input_width"], self.config["input_height"]),
            [0, 0, 0],
            1,
            crop=False,
        )

        # Sets the input to the network.
        net.setInput(blob)

        # Runs the forward pass to get output of the output layers.
        output_layers = net.getUnconnectedOutLayersNames()
        outputs = net.forward(output_layers)

        return outputs

    def post_process(self, input_image, outputs):
        # Lists to hold respective values while unwrapping.
        class_ids = []
        confidences = []
        boxes = []

        # Rows.
        rows = outputs[0].shape[1]

        image_height, image_width = input_image.shape[:2]

        # Resizing factor.
        x_factor = image_width / self.config["input_width"]
        y_factor = image_height / self.config["input_height"]

        # Iterate through 25200 detections.
        for r in range(rows):
            row = outputs[0][0][r]
            confidence = row[4]

            # Discard bad detections and continue.
            if confidence >= self.config["confidence_threshold"]:
                classes_scores = row[5:]

                # Get the index of max class score.
                class_id = np.argmax(classes_scores)

                #  Continue if the class score is above threshold.
                if classes_scores[class_id] > self.config["score_threshold"]:
                    confidences.append(confidence)
                    class_ids.append(class_id)

                    cx, cy, w, h = row[0], row[1], row[2], row[3]

                    left = int((cx - w / 2) * x_factor)
                    top = int((cy - h / 2) * y_factor)
                    width = int(w * x_factor)
                    height = int(h * y_factor)

                    box = np.array([left, top, width, height])
                    boxes.append(box)

        # Perform non maximum suppression to eliminate redundant overlapping boxes with
        # lower confidences.
        indices = cv2.dnn.NMSBoxes(
            boxes,
            confidences,
            self.config["confidence_threshold"],
            self.config["nms_threshold"],
        )

        output_boxes = []
        for i in indices:
            box = boxes[i]
            left = box[0]
            top = box[1]
            width = box[2]
            height = box[3]
            label = self.classes[class_ids[i]]
            score = confidences[i]

            output_box = {
                "x1": left,
                "y1": top,
                "x2": left + width,
                "y2": top + height,
                "label": label,
                "score": score,
            }

            output_boxes.append(output_box)

        return output_boxes

    def predict_shapes(self, image):
        if image is None:
            return []

        try:
            image = qt_img_to_cv_img(image)
        except Exception as e:
            logging.warning("Could not inference model")
            logging.warning(e)
            return []

        boxes = self.predict(image)
        shapes = []

        for box in boxes:
            shape = Shape(label=box["label"], shape_type="rectangle", flags={})
            shape.add_point(QtCore.QPointF(box["x1"], box["y1"]))
            shape.add_point(QtCore.QPointF(box["x2"], box["y2"]))
            shapes.append(shape)

        return shapes
