from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class Recipe:
    name: str
    ingredients: tuple[str, ...]
    prep_time: int
    cook_time: int
    has_meat: bool

    @property
    def total_time(self) -> int:
        return self.prep_time + self.cook_time


REQUIRED_COLUMNS = {
    "name",
    "ingredients",
    "prep_time",
    "cook_time",
    "has_meat",
}


def _split_list(value: str) -> tuple[str, ...]:
    items = [item.strip() for item in value.split(";") if item.strip()]
    return tuple(items)


def load_recipes(path: str | Path) -> list[Recipe]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Recipes file not found: {path}")

    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in recipes file: {sorted(missing)}")

    recipes: list[Recipe] = []
    for _, row in df.iterrows():
        recipes.append(
            Recipe(
                name=str(row["name"]).strip(),
                ingredients=_split_list(str(row["ingredients"]).strip()),
                prep_time=int(row["prep_time"]),
                cook_time=int(row["cook_time"]),
                has_meat=bool(row["has_meat"]),
            )
        )

    return recipes


def save_recipes(path: str | Path, recipes: Iterable[Recipe]) -> None:
    rows = []
    for recipe in recipes:
        rows.append(
            {
                "name": recipe.name,
                "ingredients": ";".join(recipe.ingredients),
                "prep_time": recipe.prep_time,
                "cook_time": recipe.cook_time,
                "has_meat": recipe.has_meat,
            }
        )

    df = pd.DataFrame(rows, columns=sorted(REQUIRED_COLUMNS))
    df.to_csv(path, index=False)
