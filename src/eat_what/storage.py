from __future__ import annotations

"""CSV storage helpers for recipes."""

from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Iterable

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Recipe:
    """Immutable recipe record."""
    name: str
    ingredients: tuple[str, ...]
    prep_time: int
    cook_time: int
    has_meat: bool
    spicy: bool = False

    @property
    def total_time(self) -> int:
        """Total minutes required for the recipe."""
        return self.prep_time + self.cook_time


REQUIRED_COLUMNS = {
    "name",
    "ingredients",
    "prep_time",
    "cook_time",
    "has_meat",
}
OUTPUT_COLUMNS = (
    "cook_time",
    "has_meat",
    "ingredients",
    "name",
    "prep_time",
    "spicy",
)


def _split_list(value: str) -> tuple[str, ...]:
    """Split a semicolon-separated list into a tuple."""
    items = [item.strip() for item in value.split(";") if item.strip()]
    return tuple(items)


def _parse_bool(value: object) -> bool:
    """Parse CSV boolean-like values in a predictable way."""
    if isinstance(value, bool):
        return value
    if value is None:
        return False

    text = str(value).strip().lower()
    if text in {"1", "true", "t", "yes", "y"}:
        return True
    if text in {"0", "false", "f", "no", "n", ""}:
        return False
    raise ValueError(f"Invalid boolean value: {value}")


def load_recipes(path: str | Path) -> list[Recipe]:
    """Load recipes from a CSV file, with minimal format validation"""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Recipes file not found: {path}")

    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in recipes file: {sorted(missing)}")

    recipes: list[Recipe] = []
    for idx, row in df.iterrows():
        try:
            recipes.append(
                Recipe(
                    name=str(row["name"]).strip(),
                    ingredients=_split_list(str(row["ingredients"]).strip()),
                    prep_time=int(row["prep_time"]),
                    cook_time=int(row["cook_time"]),
                    has_meat=_parse_bool(row["has_meat"]),
                    spicy=_parse_bool(row["spicy"]) if "spicy" in df.columns else False,
                )
            )
        except Exception as exc:
            logger.warning("Invalid recipe row at index %s: %s", idx, exc)
            continue

    return recipes


def save_recipes(path: str | Path, recipes: Iterable[Recipe]) -> None:
    """Write recipes to a CSV file."""
    rows = []
    for recipe in recipes:
        rows.append(
            {
                "name": recipe.name,
                "ingredients": ";".join(recipe.ingredients),
                "prep_time": recipe.prep_time,
                "cook_time": recipe.cook_time,
                "has_meat": recipe.has_meat,
                "spicy": recipe.spicy,
            }
        )

    df = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    df.to_csv(path, index=False)
