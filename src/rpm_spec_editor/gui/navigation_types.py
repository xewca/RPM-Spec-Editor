from enum import Enum, auto

class NavigationSource(Enum):
    EDITOR = "editor"
    TREE = "tree"
    STRUCTURE = auto()
    ERROR = auto()