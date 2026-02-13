from __future__ import annotations

"""CLI for generating a weekly meal plan and shopping list."""

import argparse
from collections import Counter
from pathlib import Path

from .ingredients_meat import INGREDIENT_MEAT
from .ingredients_vegatable import INGREDIENT_VEGATABLE
from .planner import WeeklyPlanner
from .storage import default_recipes_path, load_recipes
from .text_format import color_code, display_width, ljust_display

COLOR_ORANGE = "\x1b[38;5;208m"
COLOR_GREEN = "\x1b[32m"
COLOR_BLUE = "\x1b[34m"
COLOR_PURPLE = "\x1b[35m"
COLOR_RED = "\x1b[31m"
COLOR_RESET = "\x1b[0m"


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the planner CLI."""
    parser = argparse.ArgumentParser(description="Generate a weekly meal plan.")
    parser.add_argument(
        "--recipes",
        default=default_recipes_path(),
        help="Path to recipes CSV.",
    )
    parser.add_argument(
        "--max-time",
        "-t",
        type=int,
        default=None,
        help="Max total minutes per dish.",
    )
    parser.add_argument(
        "--max-weekly-time",
        "-m",
        type=int,
        default=400,
        help="Max total minutes for the week.",
    )
    parser.add_argument(
        "--max-overlap",
        "-o",
        type=int,
        default=6,
        help="Max repeated ingredient count allowed before fallback.",
    )
    parser.add_argument(
        "--veg-dishes",
        "-v",
        type=int,
        default=3,
        help="Number of veg dishes to append to results.",
    )
    parser.add_argument(
        "--spicy-dishes",
        "-s",
        type=int,
        default=0,
        help="Number of spicy dishes to append to results.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility.",
    )
    return parser


def print_plan(result) -> None:
    """Pretty print the planned menu and shopping list in CN/EN.
     - CN support so that multi-column display is aligned properly
       with Chinese characters
     - Color code
       - vegatable are COLOR_GREEN
       - dishes taking more than 1 hr are colored COLOR_RED
    """
    print("\n这周将就吃：")
    print("-")
    dish_items = []
    fish_names = {
        name for name, item in INGREDIENT_MEAT.items() if item.kind.value == "fish"
    }

    # Print recipe for the week
    for idx, recipe in enumerate(result.recipes, start=1):
        is_fish = any(ing in fish_names for ing in recipe.ingredients)
        if recipe.spicy:
            name = color_code(recipe.name, COLOR_PURPLE, COLOR_RESET)
        elif is_fish:
            name = color_code(recipe.name, COLOR_BLUE, COLOR_RESET)
        elif not recipe.has_meat:
            name = color_code(recipe.name, COLOR_GREEN, COLOR_RESET)
        else:
            name = recipe.name
        time_label = f"{recipe.total_time} min"
        if recipe.total_time > 60:
            time_label = color_code(time_label, COLOR_RED, COLOR_RESET)
        dish_items.append(
            f"{color_code(f'{idx}.', COLOR_ORANGE, COLOR_RESET)} "
            f"{name} | {time_label} | "
            f"{'meat' if recipe.has_meat else 'veg'}"
        )
    if dish_items:
        per_line = 2
        col_width = max(display_width(item) for item in dish_items)
        for start in range(0, len(dish_items), per_line):
            row = dish_items[start : start + per_line]
            padded = [ljust_display(item, col_width) for item in row]
            print("   ".join(padded))

    print("-")
    print(f"你在做饭上浪费的时间: {result.total_time} min")
    print(f"肉类重复次数: {result.ingredient_overlap}")

    # Extract ingredients from all recipe and display the total as
    # the shopping list
    ingredients = Counter()
    for recipe in result.recipes:
        ingredients.update(recipe.ingredients)

    print("\n跑腿清单")
    print("-")
    ingredient_cn = {
        **{name: item.cn for name, item in INGREDIENT_MEAT.items()},
        **{name: item.cn for name, item in INGREDIENT_VEGATABLE.items()},
    }
    veg_names = set(INGREDIENT_VEGATABLE)
    fish_names = {
        name for name, item in INGREDIENT_MEAT.items() if item.kind.value == "fish"
    }
    display_items: list[str] = []
    for ingredient, count in ingredients.most_common():
        cn_name = ingredient_cn.get(ingredient)
        display_name = f"{cn_name} ({ingredient})" if cn_name else ingredient
        if ingredient in fish_names:
            display_name = color_code(display_name, COLOR_BLUE, COLOR_RESET)
        elif ingredient in veg_names:
            display_name = color_code(display_name, COLOR_GREEN, COLOR_RESET)
        display_items.append(f"{display_name} x{count}")

    if display_items:
        per_line = 3
        col_width = max(display_width(item) for item in display_items)
        for start in range(0, len(display_items), per_line):
            row = display_items[start : start + per_line]
            padded = [ljust_display(item, col_width) for item in row]
            print("   ".join(padded))


def main() -> int:
    """Entry point for the meal planner CLI."""
    parser = build_parser()
    args = parser.parse_args()

    recipes_path = Path(args.recipes)
    recipes = load_recipes(recipes_path)
    planner = WeeklyPlanner(recipes, seed=args.seed)

    result = planner.plan(
        max_total_time_per_dish=args.max_time,
        max_weekly_time=args.max_weekly_time,
        max_overlap=args.max_overlap,
        veg_dishes=args.veg_dishes,
        spicy_dishes=args.spicy_dishes,
    )

    print_plan(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
