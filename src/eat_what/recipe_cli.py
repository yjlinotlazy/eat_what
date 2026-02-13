from __future__ import annotations

"""Interactive CLI for adding recipes to the CSV store."""

import argparse
from pathlib import Path

from .ingredients_meat import INGREDIENT_MEAT, MeatIngredient, MeatKind
from .ingredients_vegatable import INGREDIENT_VEGATABLE, VegatableIngredient
from .storage import Recipe, load_recipes, save_recipes


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the recipe CLI."""
    parser = argparse.ArgumentParser(description="Add a recipe to the recipes CSV.")
    parser.add_argument(
        "--recipes",
        default="data/recipes.csv",
        help="Path to recipes CSV.",
    )
    return parser


def _prompt_non_empty(prompt: str) -> str:
    """Prompt until a non-empty string is entered."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Please enter a non-empty value.")


def _prompt_int(prompt: str) -> int:
    """Prompt until a non-negative integer is entered."""
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


def _prompt_bool(prompt: str) -> bool:
    """Prompt until a yes/no value is entered."""
    while True:
        raw = input(prompt).strip().lower()
        if raw in {"y", "yes", "true", "1"}:
            return True
        if raw in {"n", "no", "false", "0", ""}:
            return False
        print("Please enter y/n.")


def _insert_into_dict(path: Path, dict_name: str, entry_line: str) -> None:
    """Insert a new entry into a module-level dict in-place."""
    text = path.read_text(encoding="utf-8")
    marker = f"{dict_name} = {{"
    start = text.find(marker)
    if start == -1:
        raise ValueError(f"Unable to find {dict_name} in {path}.")
    end = text.find("\n}", start)
    if end == -1:
        raise ValueError(f"Unable to find end of {dict_name} in {path}.")

    updated = text[:end] + entry_line + text[end:]
    path.write_text(updated, encoding="utf-8")


def _prompt_choice(prompt: str, options: list[str]) -> str:
    """Prompt for a choice from a fixed set."""
    while True:
        raw = input(prompt).strip().upper()
        if raw in options:
            return raw
        print(f"Please enter one of: {', '.join(options)}")


def _add_meat_ingredient() -> None:
    """Interactively add a meat ingredient to the source list."""
    name = _prompt_non_empty("New meat ingredient (english): ")
    if name in INGREDIENT_MEAT:
        print("Ingredient already exists.")
        return
    cn = _prompt_non_empty("Chinese name: ")
    kind_options = [k.name for k in MeatKind]
    kind_raw = _prompt_choice(
        f"Meat kind {kind_options}: ",
        kind_options,
    )
    kind = MeatKind[kind_raw]

    entry_line = f'    "{name}": MeatIngredient(MeatKind.{kind.name}, "{cn}"),\n'
    _insert_into_dict(
        Path(__file__).with_name("ingredients_meat.py"),
        "INGREDIENT_MEAT",
        entry_line,
    )
    INGREDIENT_MEAT[name] = MeatIngredient(kind, cn)
    print(f"Added meat ingredient: {cn} ({name})")


def _add_veg_ingredient() -> None:
    """Interactively add a veg ingredient to the source list."""
    name = _prompt_non_empty("New veg ingredient (english): ")
    if name in INGREDIENT_VEGATABLE:
        print("Ingredient already exists.")
        return
    cn = _prompt_non_empty("Chinese name: ")
    entry_line = f'\n    "{name}": VegatableIngredient("{cn}"),\n'
    _insert_into_dict(
        Path(__file__).with_name("ingredients_vegatable.py"),
        "INGREDIENT_VEGATABLE",
        entry_line,
    )
    INGREDIENT_VEGATABLE[name] = VegatableIngredient(cn)
    print(f"Added veg ingredient: {cn} ({name})")


def _prompt_ingredients() -> list[str]:
    """Prompt to select ingredients from meat and veg lists."""
    def select_from(items: dict[str, str], title: str) -> list[str]:
        names = sorted(items)
        if not names:
            return []

        print(title)
        per_line = 3
        green = "\x1b[32m"
        reset = "\x1b[0m"
        formatted = [
            f"{green}{idx}.{reset} {items[name]} ({name})"
            for idx, name in enumerate(names, start=1)
        ]
        col_width = max(len(text) for text in formatted)
        for start in range(0, len(formatted), per_line):
            row = formatted[start : start + per_line]
            padded = [text.ljust(col_width) for text in row]
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

    while True:
        action = input(
            "Add new ingredient? (m=meat, v=veg, enter to continue): "
        ).strip().lower()
        if not action:
            break
        if action == "m":
            _add_meat_ingredient()
        elif action == "v":
            _add_veg_ingredient()
        else:
            print("Invalid choice. Use 'm', 'v', or Enter.")

    meat_cn = {name: item.cn for name, item in INGREDIENT_MEAT.items()}
    veg_cn = {name: item.cn for name, item in INGREDIENT_VEGATABLE.items()}

    selected = []
    selected.extend(select_from(meat_cn, "Select meat ingredients:"))
    selected.extend(select_from(veg_cn, "Select veg ingredients:"))

    return selected


def main() -> int:
    """Entry point for adding a recipe via prompts."""
    parser = build_parser()
    args = parser.parse_args()

    name = _prompt_non_empty("Recipe name: ")
    ingredients = _prompt_ingredients()
    if not ingredients:
        print("No ingredients provided. Aborting.")
        return 1
    prep_time = _prompt_int("Prep time (minutes): ")
    cook_time = _prompt_int("Cook time (minutes): ")
    spicy = _prompt_bool("Is this dish spicy? (y/N): ")

    has_meat = any(ingredient in INGREDIENT_MEAT for ingredient in ingredients)
    recipe = Recipe(
        name=name,
        ingredients=tuple(ingredients),
        prep_time=prep_time,
        cook_time=cook_time,
        has_meat=has_meat,
        spicy=spicy,
    )

    recipes_path = Path(args.recipes)
    recipes = load_recipes(recipes_path)
    recipes.append(recipe)
    save_recipes(recipes_path, recipes)

    print(f"Added recipe: {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
