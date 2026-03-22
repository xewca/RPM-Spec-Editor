from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class SpecSection:
    name: str
    start_line: int
    lines: List[str] = field(default_factory=list)


@dataclass
class SpecFile:
    headers: Dict[str, str] = field(default_factory=dict)
    sections: Dict[str, SpecSection] = field(default_factory=dict)
    section_order: List[str] = field(default_factory=list)