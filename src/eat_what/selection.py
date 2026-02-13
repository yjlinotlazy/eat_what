from __future__ import annotations

"""Shared interactive selection utilities for CLI flows."""

from .text_format import color_code, display_width, ljust_display

COLOR_GREEN = "\x1b[32m"
COLOR_RESET = "\x1b[0m"


def select_from(
    items: dict[str, str],
    title: str,
    *,
    finish_on_trailing_space: bool = True,
) -> list[str]:
    """Display numbered options and return selected english keys."""
    names = sorted(items)
    if not names:
        return []

    print(title)
    per_line = 3
    formatted = [
        f"{color_code(str(idx), COLOR_GREEN, COLOR_RESET)}. {items[name]} ({name})"
        for idx, name in enumerate(names, start=1)
    ]
    col_width = max(display_width(text) for text in formatted)
    for start in range(0, len(formatted), per_line):
        row = formatted[start : start + per_line]
        padded = [ljust_display(text, col_width) for text in row]
        print("   ".join(padded))

    chosen: list[str] = []
    chosen_set: set[str] = set()
    while True:
        raw = input("Select numbers (comma-separated, blank to finish): ")
        if not raw.strip():
            break
        finished = finish_on_trailing_space and raw.endswith(" ")
        parts = [part.strip() for part in raw.strip().split(",") if part.strip()]
        for part in parts:
            if not part.isdigit():
                print(f"Invalid number: {part}")
                continue
            idx = int(part)
            if idx < 1 or idx > len(names):
                print(f"Out of range: {idx}")
                continue
            name = names[idx - 1]
            if name in chosen_set:
                continue
            chosen.append(name)
            chosen_set.add(name)
        if finished:
            break
    return chosen
