from enum import Enum


class TrainingState(Enum):
    WAITING = "Phase: Configuration"
    INITIALIZING = "Phase: Intialization"
    TRAINING = "Phase: Training"
