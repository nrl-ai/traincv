"""
traincv is a task-based training toolkit
This module defines supported tasks
"""
from enum import Enum


class TaskChoices(Enum):
    IMAGE_CLASSIFICATION = "image_classification"
    OBJECT_DETECTION = "object_detection"
    OBJECT_SEGMENTATION = "object_segmentation"
    INSTANCE_SEGMENTATION = "instance_segmentation"
