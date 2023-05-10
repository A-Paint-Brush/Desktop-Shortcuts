from contextlib import suppress
from typing import *
import platform
import tkinter
import math
with suppress(ImportError):
    from ctypes import windll


def resize_image(original_size: Tuple[int, int], new_size: Tuple[int, int]) -> Tuple[Union[int, float],
                                                                                     Union[int, float]]:
    hw_ratio = original_size[1] / original_size[0]
    if new_size[0] * hw_ratio <= new_size[1]:
        scaled_size = (new_size[0], math.floor(new_size[0] * hw_ratio))
    else:
        scaled_size = (math.floor(new_size[1] / hw_ratio), new_size[1])
    return scaled_size


def word_wrap_text(string: str, width: int, font: tkinter.font.Font, br: str = "-") -> List[str]:
    lines, break_locations = [[]], []
    for index, char in enumerate(string):
        if char == " ":
            break_locations.append(len(lines[-1]))
            lines[-1].append(char)
            continue
        elif char == "\n":
            break_locations.clear()
            lines.append([])
            continue
        if font.measure("".join(lines[-1] + [char, br])) <= width:
            lines[-1].append(char)
        else:
            if break_locations:
                last_word = lines[-1][break_locations[-1] + 1:]
                lines[-1] = lines[-1][:break_locations[-1]]
                break_locations.clear()
                lines.append(last_word)
                lines[-1].append(char)
            else:
                if lines and lines[-1]:
                    if lines[-1][-1].isascii():  # Chinese characters do not need a dash on line-breaking.
                        lines[-1].append(br)
                lines.append([char])
    return ["".join(line) for line in lines]


def configure_dpi() -> None:
    """If current OS is Windows, attempts to configure the Python process to be DPI aware."""
    if platform.system() == "Windows":
        if not post_win8_config_dpi():
            pre_win8_config_dpi()


def post_win8_config_dpi() -> bool:
    try:
        windll.shcore.SetProcessDpiAwareness(2)
    except (OSError, AttributeError):
        return False
    else:
        return True


def pre_win8_config_dpi() -> bool:
    try:
        windll.shcore.SetProcessDPIAware()
    except (OSError, AttributeError):
        return False
    else:
        return True
