from __future__ import annotations

import argparse
import re
from pathlib import Path

from .ingredients_meat import INGREDIENT_MEAT
from .storage import Recipe, load_recipes, save_recipes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Add a recipe to the recipes CSV.")
    parser.add_argument(
        "--recipes",
        default="data/recipes.csv",
        help="Path to recipes CSV.",
    )
    return parser


def _prompt_non_empty(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Please enter a non-empty value.")


def _parse_ingredients(raw: str) -> list[str]:
    parts = [item.strip() for item in re.split(r"[;,]", raw) if item.strip()]
    return parts


def _prompt_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("Please enter a number.")
            continue
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a whole number.")
            continue
        if value < 0:
            print("Please enter a non-negative number.")
            continue
        return value


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    name = _prompt_non_empty("Recipe name: ")
    ingredients_raw = _prompt_non_empty("Ingredients (comma or ';' separated): ")
    ingredients = _parse_ingredients(ingredients_raw)
    if not ingredients:
        print("No ingredients provided. Aborting.")
        return 1
    prep_time = _prompt_int("Prep time (minutes): ")
    cook_time = _prompt_int("Cook time (minutes): ")

    has_meat = any(ingredient in INGREDIENT_MEAT for ingredient in ingredients)
    recipe = Recipe(
        name=name,
        ingredients=tuple(ingredients),
        prep_time=prep_time,
        cook_time=cook_time,
        has_meat=has_meat,
    )

    recipes_path = Path(args.recipes)
    recipes = load_recipes(recipes_path)
    recipes.append(recipe)
    save_recipes(recipes_path, recipes)

    print(f"Added recipe: {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
