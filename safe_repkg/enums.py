from enum import Enum, auto


class ReqSource(Enum):
    TEXT = auto()
    CONDA_YML = auto()
    PROJ_TOML = auto()
    SETUP_CFG = auto()
    NONE = auto()
