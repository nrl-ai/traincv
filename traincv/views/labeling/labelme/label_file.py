import base64
import contextlib
import io
import json
import os.path as osp

import PIL.Image

from . import __version__, utils
from .logger import logger

PIL.Image.MAX_IMAGE_PIXELS = None


@contextlib.contextmanager
def io_open(name, mode):
    assert mode in ["r", "w"]
    encoding = "utf-8"
    yield io.open(name, mode, encoding=encoding)


class LabelFileError(Exception):
    pass


class LabelFile:

    suffix = ".json"

    def __init__(self, filename=None):
        self.shapes = []
        self.image_path = None
        self.image_data = None
        if filename is not None:
            self.load(filename)
        self.filename = filename

    @staticmethod
    def load_image_file(filename):
        try:
            image_pil = PIL.Image.open(filename)
        except IOError:
            logger.error("Failed opening image file: %s", filename)
            return None

        # apply orientation to image according to exif
        image_pil = utils.apply_exif_orientation(image_pil)

        with io.BytesIO() as f:
            ext = osp.splitext(filename)[1].lower()
            if ext in [".jpg", ".jpeg"]:
                image_pil = image_pil.convert("RGB")
                img_format = "JPEG"
            else:
                img_format = "PNG"
            image_pil.save(f, format=img_format)
            f.seek(0)
            return f.read()

    def load(self, filename):
        keys = [
            "version",
            "imageData",
            "imagePath",
            "shapes",  # polygonal annotations
            "flags",  # image level flags
            "imageHeight",
            "imageWidth",
        ]
        shape_keys = [
            "label",
            "text",
            "points",
            "group_id",
            "shape_type",
            "flags",
        ]
        try:
            with io_open(filename, "r") as f:
                data = json.load(f)
            version = data.get("version")
            if version is None:
                logger.warning(
                    "Loading JSON file (%s) of unknown version", filename
                )
            elif (
                version.split(".")[0] != __version__.split(".", maxsplit=1)[0]
            ):
                logger.warning(
                    "This JSON file (%s) may be incompatible with "
                    "current labelme. version in file: %s, "
                    "current version: %s",
                    filename,
                    version,
                    __version__,
                )

            if data["imageData"] is not None:
                image_data = base64.b64decode(data["imageData"])
            else:
                # relative path from label file to relative path from cwd
                image_path = osp.join(osp.dirname(filename), data["imagePath"])
                image_data = self.load_image_file(image_path)
            flags = data.get("flags") or {}
            image_path = data["imagePath"]
            self._check_image_height_and_width(
                base64.b64encode(image_data).decode("utf-8"),
                data.get("imageHeight"),
                data.get("imageWidth"),
            )
            shapes = [
                dict(
                    label=s["label"],
                    text=s.get("text", ""),
                    points=s["points"],
                    shape_type=s.get("shape_type", "polygon"),
                    flags=s.get("flags", {}),
                    group_id=s.get("group_id"),
                    other_data={
                        k: v for k, v in s.items() if k not in shape_keys
                    },
                )
                for s in data["shapes"]
            ]
        except Exception as e:
            raise LabelFileError(e) from e

        other_data = {}
        for key, value in data.items():
            if key not in keys:
                other_data[key] = value

        # Add new fields if not available
        other_data["text"] = other_data.get("text", "")

        # Only replace data after everything is loaded.
        self.flags = flags
        self.shapes = shapes
        self.image_path = image_path
        self.image_data = image_data
        self.filename = filename
        self.other_data = other_data

    @staticmethod
    def _check_image_height_and_width(image_data, image_height, image_width):
        img_arr = utils.img_b64_to_arr(image_data)
        if image_height is not None and img_arr.shape[0] != image_height:
            logger.error(
                "image_height does not match with image_data or image_path, "
                "so getting image_height from actual image."
            )
            image_height = img_arr.shape[0]
        if image_width is not None and img_arr.shape[1] != image_width:
            logger.error(
                "image_width does not match with image_data or image_path, "
                "so getting image_width from actual image."
            )
            image_width = img_arr.shape[1]
        return image_height, image_width

    def save(
        self,
        filename=None,
        shapes=None,
        image_path=None,
        image_height=None,
        image_width=None,
        image_data=None,
        other_data=None,
        flags=None,
    ):
        if image_data is not None:
            image_data = base64.b64encode(image_data).decode("utf-8")
            image_height, image_width = self._check_image_height_and_width(
                image_data, image_height, image_width
            )
        if other_data is None:
            other_data = {}
        if flags is None:
            flags = {}
        data = dict(
            version=__version__,
            flags=flags,
            shapes=shapes,
            imagePath=image_path,
            imageData=image_data,
            imageHeight=image_height,
            imageWidth=image_width,
        )
        for key, value in other_data.items():
            assert key not in data
            data[key] = value
        try:
            with io_open(filename, "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.filename = filename
        except Exception as e:
            raise LabelFileError(e) from e

    @staticmethod
    def is_label_file(filename):
        return osp.splitext(filename)[1].lower() == LabelFile.suffix
