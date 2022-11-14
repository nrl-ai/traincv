"""
Data preparation for data subsets (train/test/val)
This modules contains utilities for copying, spliting and preparing data subsets.
"""

import json
import os
import pathlib


class DataSubsetPreparator:
    """Data preparator for a subset (train/val/test)"""

    def __init__(self):
        self.data = []
        self.split_ratio = 0.0

    def set_split_ratio(self, split_ratio):
        """Set split ratio when we need to split one dataset into multiple subsets"""
        self.split_ratio = split_ratio

    def is_valid_data_folder(self, path):
        """Check if the data folder is valid

        Return False, error_message when data folder is not valid
        Return True, {"path": path, "image_label_list": image_label_list} otherwise
        """
        if not os.path.isdir(path):
            return False, "Not a folder"

        for data in self.data:
            if data["path"] == path:
                return False, "Folder is already in the list"

        label_paths = []
        for folder, _, files in os.walk(path):
            for file in files:
                if file.endswith(".json"):
                    label_paths.append(os.path.join(folder, file))
        if len(label_paths) == 0:
            return False, "Folder contains no label file"

        image_label_list = []
        for label_path in label_paths:
            data_root = pathlib.Path(label_path).parent.absolute()

            with open(label_path, "r") as f:
                data = json.load(f)

            if "imagePath" in data:
                image_path = os.path.join(data_root, data["imagePath"])
                image_label_list.append((image_path, label_path))

        if len(image_label_list) == 0:
            return False, "No valid data in folder"

        return True, {"path": path, "image_label_list": image_label_list}

    def add_data_folder(self, new_data):
        """Add data folder"""
        for data in self.data:
            if data["path"] == new_data["path"]:
                return
        self.data.append(new_data)

    def remove_data_by_indices(self, indices):
        """Remove data by indices"""
        indices = sorted(set(indices), reverse=True)
        for idx in indices:
            if idx >= 0 and idx < len(self.data):
                del self.data[idx]

    def total_size(self):
        """Total data size"""
        return sum(len(data["image_label_list"]) for data in self.data)

    def split_size(self):
        """Size of split set"""
        return int(self.split_ratio * self.total_size())

    def size(self):
        """Return the size of dataset"""
        total_size = self.total_size()
        return total_size - int(self.split_ratio * total_size)

    def clear(self):
        """Clear all data"""
        self.data = []
        self.split_ratio = 0.0
