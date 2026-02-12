from __future__ import annotations

"""Core planning logic for weekly menu selection."""

from dataclasses import dataclass
from typing import Iterable
import random

from .storage import Recipe


@dataclass(frozen=True)
class PlanResult:
    """Planning output with selected recipes and summary stats."""
    recipes: tuple[Recipe, ...]
    total_time: int
    ingredient_overlap: int


class WeeklyPlanner:
    """Planner that selects recipes with time and overlap constraints."""
    def __init__(
        self,
        recipes: Iterable[Recipe],
        *,
        days: int = 7,
        seed: int | None = None,
    ) -> None:
        self._recipes = list(recipes)
        self._days = days
        self._random = random.Random(seed)

    def plan(
        self,
        *,
        max_total_time_per_dish: int | None = None,
        max_weekly_time: int | None = None,
        max_overlap: int = 6,
        max_attempts: int = 200,
    ) -> PlanResult:
        """Build a weekly plan and append 3 extra veg dishes if possible."""
        if not self._recipes:
            raise ValueError("No recipes available to plan.")

        recipes = self._filter_by_time(self._recipes, max_total_time_per_dish)
        if not recipes:
            raise ValueError("No recipes fit the time constraints.")

        meat_target = self._days

        meat_recipes = [r for r in recipes if r.has_meat]
        veg_recipes = [r for r in recipes if not r.has_meat]

        if not meat_recipes:
            return None

        best_meat: list[Recipe] | None = None
        best_total_time: int = 0
        best_overlap: int = 0

        # Build a plan for meat
        for _ in range(max_attempts):
            meat_selection = self._sample_dishes(meat_recipes, meat_target)
            if not meat_selection:
                continue

            total_time = sum(r.total_time for r in meat_selection)
            if max_weekly_time is not None and total_time > max_weekly_time:
                continue

            overlap = self._ingredient_overlap(meat_selection)


            if overlap <= max_overlap:
                best_meat = meat_selection
                best_total_time = total_time
                best_overlap = overlap
                break
            if best_meat is None or total_time < best_total_time:
                best_meat = meat_selection
                best_total_time = total_time
                best_overlap = overlap

        if best_meat is None:
            raise ValueError("Unable to build a weekly plan with given constraints.")

        # Best effort to add 3 veg dishes
        veg_selection = self._sample_dishes(veg_recipes, 3, with_replacement=True)

        result = PlanResult(
            recipes=tuple(best_meat + veg_selection),
            total_time=best_total_time,
            ingredient_overlap=best_overlap,
        )
        return result

    def _filter_by_time(
        self, recipes: list[Recipe], max_total_time_per_dish: int | None
    ) -> list[Recipe]:
        """Filter recipes by per-dish total time."""
        if max_total_time_per_dish is None:
            return list(recipes)
        return [r for r in recipes if r.total_time <= max_total_time_per_dish]

    def _sample_dishes(
        self,
        recipes: list[Recipe],
        num_dishes: int,
        with_replacement=False
    ) -> list[Recipe] | None:
        """Sample dishes with or without replacement."""
        if not with_replacement:
            selection: list[Recipe] = self._random.sample(recipes, num_dishes)
        else:
            selection: list[Recipe] = self._random.choices(recipes, k=num_dishes)
        self._random.shuffle(selection)
        return selection

    @staticmethod
    def _ingredient_overlap(recipes: Iterable[Recipe]) -> int:
        """Count repeated ingredients across recipes."""
        counts: dict[str, int] = {}
        for recipe in recipes:
            for ingredient in recipe.ingredients:
                counts[ingredient] = counts.get(ingredient, 0) + 1

        return sum(count - 1 for count in counts.values() if count > 1)
