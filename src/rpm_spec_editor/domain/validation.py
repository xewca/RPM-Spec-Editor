from dataclasses import dataclass
from enum import Enum


class ValidationLevel(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"


@dataclass
class ValidationIssue:
    level: ValidationLevel
    message: str
    line_no: int | None = None