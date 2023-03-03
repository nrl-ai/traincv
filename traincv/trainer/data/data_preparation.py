import json
import logging
import os
import pathlib
import random
import sys
import uuid

import cv2
from imutils import paths

logging.getLogger().setLevel(logging.DEBUG)

label_id_map = {"object": 1}


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


def scan_labelme_labels(root_path):
    """Scan a root path and return list of (image_file, label_file)"""
    dataset = []
    image_paths = list(paths.list_images(root_path))
    for image_path in image_paths:
        pre_name, _ = os.path.splitext(image_path)
        label_path = f"{pre_name}.json"
        if os.path.isfile(label_path):
            dataset.append((image_path, label_path))
    return dataset


def convert_box(size, box):
    """Convert labelme bounding box to YOLO bounding box"""
    dw = 1.0 / size[0]
    dh = 1.0 / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)


def labelme_to_yolo(img_label_sets, output_path):
    """Convert a labelme folder to a YOLO folder"""
    pathlib.Path(output_path).mkdir(exist_ok=True, parents=True)

    len_labels = len(img_label_sets)
    for i, (image_path, label_path) in enumerate(img_label_sets):
        print(f"{i} / {len_labels}")
        new_base_name = str(uuid.uuid4())
        new_image_name = f"{new_base_name}.jpg"
        output_json_name = f"{new_base_name}.json"
        output_json_path = os.path.join(output_path, output_json_name)
        output_label_path = os.path.join(output_path, f"{new_base_name}.txt")

        # Read label
        with open(label_path, "r") as f:
            data = json.load(f)

        # Read image
        img = cv2.imread(image_path)
        img_height, img_width = img.shape[:2]

        # Output label and jsons
        data["imagePath"] = new_image_name
        with open(output_json_path, "w") as f:
            json.dump(data, f)
        cv2.imwrite(os.path.join(output_path, new_image_name), img)

        with open(output_label_path, "w") as f:
            shapes = data["shapes"]
            for shape in shapes:
                if len(shape["points"]) != 2:
                    continue

                label = shape["label"]

                if label not in label_id_map:
                    logging.warning("Skip label: %s", label)
                    continue

                if shape["shape_type"] != "rectangle":
                    logging.warning(
                        "Shape type is not `rectangle`: %s",
                        shape["shape_type"],
                    )
                    continue

                label_id = label_id_map[label]
                x1 = shape["points"][0][0]
                y1 = shape["points"][0][1]
                x2 = shape["points"][1][0]
                y2 = shape["points"][1][1]

                xmin = min(x1, x2)
                xmax = max(x1, x2)
                ymin = min(y1, y2)
                ymax = max(y1, y2)
                bbox = (xmin, xmax, ymin, ymax)

                yolo_bbox = convert_box((img_width, img_height), bbox)
                f.write(
                    f"{label_id} {yolo_bbox[0]} {yolo_bbox[1]} {yolo_bbox[2]} {yolo_bbox[3]}\n"
                )


def main(args):
    if args.output_format != "YOLO":
        raise Exception("Only YOLO format is supported now")

    # List of (image_path, label_path)
    train_sets = []
    val_sets = []
    test_sets = []

    # Scan training
    if args.train_path is None:
        raise Exception("At least one `train_path` must be present")
    for path in args.train_path:
        train_sets += scan_labelme_labels(path)
    original_train_sets_size = len(train_sets)

    random.seed(42)
    random.shuffle(train_sets)

    # Scan validation
    if args.val_path is not None and args.split_val_from_train:
        raise Exception(
            "`val_path` and `split_val_from_train` cannot exist together"
        )
    if args.val_path is not None:
        for path in args.val_path:
            val_sets += scan_labelme_labels(path)
    elif args.split_val_from_train:
        if args.split_val_ratio <= 0 or args.split_val_ratio >= 1:
            raise Exception("Validation ratio must be from 0 to 1")
        val_size = int(original_train_sets_size * args.split_val_ratio)
        val_sets = train_sets[: val_size + 1]
        train_sets = train_sets[val_size + 1 :]

    # Scan test
    if args.test_path is not None and args.split_test_from_train:
        raise Exception(
            "`test_path` and `split_test_from_train` cannot exist together"
        )
    if args.test_path is not None:
        for path in args.test_path:
            test_sets += scan_labelme_labels(path)
    elif args.split_test_from_train:
        if args.split_test_ratio <= 0 or args.split_test_ratio >= 1:
            raise Exception("Test ratio must be from 0 to 1")
        test_size = int(original_train_sets_size * args.split_test_ratio)
        if test_size > len(train_sets):
            raise Exception(
                "Not enough training data to split for both validation and"
                f" test set. Training size: {original_train_sets_size},"
                f" expected: > {test_size + len(train_sets)}"
            )
        test_sets = train_sets[: test_size + 1]
        train_sets = train_sets[test_size + 1 :]

    logging.info("Converting training set")
    labelme_to_yolo(train_sets, args.output_train_path)

    if len(val_sets) == 0:
        logging.warning("Skipped empty validation set")
    else:
        logging.info("Converting validation set")
        labelme_to_yolo(val_sets, args.output_val_path)

    if len(test_sets) == 0:
        logging.warning("Skipped empty test set")
    else:
        logging.info("Converting test set")
        labelme_to_yolo(test_sets, args.output_test_path)

    logging.info("Training size: %d", len(train_sets))
    logging.info("Validation size: %d", len(val_sets))
    logging.info("Test size: %d", len(test_sets))

    return 0


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        "Collect and convert data from labelme for object detection"
    )
    parser.add_argument(
        "--train_path", action="append", help="Path to training data"
    )
    parser.add_argument(
        "--val_path", action="append", help="Path to validation data"
    )
    parser.add_argument(
        "--test_path", action="append", help="Path to test data"
    )
    parser.add_argument(
        "--split_val_from_train",
        type=str2bool,
        default=False,
        help="Split validation set from training set",
    )
    parser.add_argument(
        "--split_val_ratio",
        type=float,
        required=False,
        help="Ratio to split validation set from training",
    )
    parser.add_argument(
        "--split_test_from_train",
        type=str2bool,
        default=False,
        help="Split test set from training set",
    )
    parser.add_argument(
        "--split_test_ratio",
        type=float,
        required=False,
        help="Ratio to split test set from training",
    )
    parser.add_argument(
        "--output_train_path",
        type=str,
        required=False,
        help="Output training folder",
    )
    parser.add_argument(
        "--output_val_path",
        type=str,
        required=False,
        help="Output validation folder",
    )
    parser.add_argument(
        "--output_test_path",
        type=str,
        required=False,
        help="Output test folder",
    )
    parser.add_argument(
        "--output_format",
        type=str,
        default="YOLO",
        help="Output format for training data",
    )
    parser.add_argument(
        "--report_file",
        type=str,
        required=False,
        help="Report file of data preparation",
    )

    parsed_args = parser.parse_args()
    sys.exit(main(parsed_args))
