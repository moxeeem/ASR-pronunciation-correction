import functools
from enum import StrEnum


class FmtCodes(StrEnum):
    # color codes
    Red         = "\033[91m"
    Green       = "\033[92m"
    Blue        = "\033[94m"
    Yellow      = "\033[93m"
    Magenta     = "\033[95m"
    Cyan        = "\033[96m"
    # other formatting codes:
    Bold        = "\033[1m"
    Underline   = "\033[4m"
    # code to reset formatting:
    Reset       = "\033[0m"


def _reset(text: str) -> str:
    return f"{text}{FmtCodes.Reset}"


def _colorize(color: str, text: str) -> str:
    match color.lower():
        case "red":
            return _reset(f"{FmtCodes.Red}{text}")
        case "green":
            return _reset(f"{FmtCodes.Green}{text}")
        case "blue":
            return _reset(f"{FmtCodes.Blue}{text}")
        case "yellow":
            return _reset(f"{FmtCodes.Yellow}{text}")
        case "magenta":
            return _reset(f"{FmtCodes.Magenta}{text}")
        case "cyan":
            return _reset(f"{FmtCodes.Cyan}{text}")
        case color_name:
            raise ValueError(f"Unsupported color name: '{color_name}'")


red     = functools.partial(_colorize, "red")
green   = functools.partial(_colorize, "green")
blue    = functools.partial(_colorize, "blue")
magenta = functools.partial(_colorize, "magenta")
yellow  = functools.partial(_colorize, "yellow")
cyan    = functools.partial(_colorize, "cyan")


def underline(text: str) -> str:
    return f"{FmtCodes.Underline}{text}{FmtCodes.Reset}"


def bold(text: str) -> str:
    return f"{FmtCodes.Bold}{text}{FmtCodes.Reset}"
