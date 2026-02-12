from __future__ import annotations

"""CLI for generating a weekly meal plan and shopping list."""

import argparse
from collections import Counter
from pathlib import Path

from .ingredients_meat import INGREDIENT_MEAT
from .ingredients_vegatable import INGREDIENT_VEGATABLE
from .planner import WeeklyPlanner
from .storage import load_recipes


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the planner CLI."""
    parser = argparse.ArgumentParser(description="Generate a weekly meal plan.")
    parser.add_argument(
        "--recipes",
        default="data/recipes.csv",
        help="Path to recipes CSV.",
    )
    parser.add_argument(
        "--max-time",
        type=int,
        default=None,
        help="Max total minutes per dish.",
    )
    parser.add_argument(
        "--max-weekly-time",
        type=int,
        default=400,
        help="Max total minutes for the week.",
    )
    parser.add_argument(
        "--max-overlap",
        type=int,
        default=6,
        help="Max repeated ingredient count allowed before fallback.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility.",
    )
    return parser


def print_plan(result) -> None:
    """Print the planned menu and shopping list in CN/EN."""
    print("\n这周将就吃：")
    print("-")
    for idx, recipe in enumerate(result.recipes, start=1):
        print(
            f"{idx}. {recipe.name} | {recipe.total_time} min | "
            f"{'meat' if recipe.has_meat else 'veg'}"
        )

    print("-")
    print(f"你在做饭上浪费的时间: {result.total_time} min")
    print(f"重复吃了几个荤菜: {result.ingredient_overlap}")

    ingredients = Counter()
    for recipe in result.recipes:
        ingredients.update(recipe.ingredients)

    print("\n跑腿清单")
    print("-")
    ingredient_cn = {
        **{name: item.cn for name, item in INGREDIENT_MEAT.items()},
        **{name: item.cn for name, item in INGREDIENT_VEGATABLE.items()},
    }
    for ingredient, count in ingredients.most_common():
        cn_name = ingredient_cn.get(ingredient)
        display_name = f"{cn_name} ({ingredient})" if cn_name else ingredient
        print(f"{display_name} x{count}")


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
    )

    print_plan(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
