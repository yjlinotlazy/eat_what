from __future__ import annotations

"""CLI for listing recipes that match selected ingredients."""

import argparse
from pathlib import Path

from .ingredients_meat import INGREDIENT_MEAT
from .ingredients_vegatable import INGREDIENT_VEGATABLE
from .storage import load_recipes
from .text_format import color_code, display_width, ljust_display

COLOR_GREEN = "\x1b[32m"
COLOR_RESET = "\x1b[0m"


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the recipe picker CLI."""
    parser = argparse.ArgumentParser(
        description="Select ingredients and list matching recipes."
    )
    parser.add_argument(
        "--recipes",
        default="data/recipes.csv",
        help="Path to recipes CSV.",
    )
    return parser


def _select_from(items: dict[str, str], title: str) -> list[str]:
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
        raw = input("Select numbers (comma-separated, blank to finish): ").strip()
        if not raw:
            break
        parts = [part.strip() for part in raw.split(",") if part.strip()]
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
    return chosen


def main() -> int:
    """Entry point for selecting ingredients and listing recipes."""
    parser = build_parser()
    args = parser.parse_args()

    meat_cn = {name: item.cn for name, item in INGREDIENT_MEAT.items()}
    veg_cn = {name: item.cn for name, item in INGREDIENT_VEGATABLE.items()}

    selected: list[str] = []
    selected.extend(_select_from(meat_cn, "Select meat ingredients:"))
    selected.extend(_select_from(veg_cn, "Select veg ingredients:"))

    if not selected:
        print("No ingredients selected.")
        return 1

    selected_set = set(selected)
    recipes = load_recipes(Path(args.recipes))
    matches = [
        recipe
        for recipe in recipes
        if all(ing in selected_set for ing in recipe.ingredients)
    ]

    print("\nMatching Recipes")
    print("-")
    if not matches:
        print("No recipes match the selected ingredients.")
        return 0

    for recipe in matches:
        print(f"{recipe.name} | {recipe.total_time} min")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
