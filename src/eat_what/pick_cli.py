from __future__ import annotations

"""CLI for listing recipes that match selected ingredients."""

import argparse
from pathlib import Path

from .ingredients_meat import INGREDIENT_MEAT
from .ingredients_vegatable import INGREDIENT_VEGATABLE
from .selection import select_from
from .storage import default_recipes_path, load_recipes


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the recipe picker CLI."""
    parser = argparse.ArgumentParser(
        description="Select ingredients and list matching recipes."
    )
    parser.add_argument(
        "--recipes",
        default=default_recipes_path(),
        help="Path to recipes CSV.",
    )
    return parser


def main() -> int:
    """Entry point for selecting ingredients and listing recipes."""
    parser = build_parser()
    args = parser.parse_args()

    meat_cn = {name: item.cn for name, item in INGREDIENT_MEAT.items()}
    veg_cn = {name: item.cn for name, item in INGREDIENT_VEGATABLE.items()}

    selected: list[str] = []
    selected.extend(select_from(meat_cn, "Select meat ingredients:"))
    selected.extend(select_from(veg_cn, "Select veg ingredients:"))

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
