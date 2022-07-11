from enum import Enum
from sre_constants import SUCCESS


class TaskStatus(Enum):
    SUCCEED = "SUCCEED"
    FAILED = "FAILED"
