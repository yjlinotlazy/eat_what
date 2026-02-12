"""Helpers for terminal-friendly text alignment."""

from __future__ import annotations

import re
import unicodedata

ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*m")


def display_width(text: str) -> int:
    """Return the display width, accounting for ANSI codes and CJK width."""
    plain = ANSI_PATTERN.sub("", text)
    width = 0
    for ch in plain:
        if unicodedata.east_asian_width(ch) in {"W", "F"}:
            width += 2
        else:
            width += 1
    return width


def ljust_display(text: str, width: int) -> str:
    """Pad text to a display width (CJK and ANSI aware)."""
    pad = width - display_width(text)
    if pad <= 0:
        return text
    return text + (" " * pad)


def color_code(text: str, color: str, reset: str = "\x1b[0m") -> str:
    """Wrap text in ANSI color codes."""
    return f"{color}{text}{reset}"
