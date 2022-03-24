from enum import Enum, auto


class ErrorType(Enum):
    ORIG_PKG_NOT_FOUND = auto()
    ORIG_SETUP_CFG_NOT_FOUND = auto()
    SETUP_CFG_UNREADABLE = auto()
    PKG_NAME_UNREADABLE = auto()
    CS_ENTRY_PTS_NOT_FOUND = auto()
    DESTINATION_PATH_EXISTS = auto()
    REDIRECT_REQUIRES_NEW_PATH = auto()


e_msgs = {
    ErrorType.ORIG_PKG_NOT_FOUND: 'Original package path not found.'
}



