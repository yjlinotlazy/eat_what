from __future__ import annotations

"""Core planning logic for weekly menu selection.
Overall logic:
- Filter recipes by optional per-dish time limit.
- Build a meat-heavy weekly plan of length `days` (default 7), trying to
  minimize ingredient overlap and stay under a weekly time cap.
- If any fish recipes exist, force at least one fish dish in the meat plan.
- Append configurable non-spicy veg dishes (with replacement) as a best-effort add-on.
- Append configurable spicy dishes from spicy recipes only as best effort.
"""

from dataclasses import dataclass
import logging
from typing import Iterable
import random

from .ingredients_meat import INGREDIENT_MEAT, MeatKind
from .storage import Recipe

logger = logging.getLogger(__name__)


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
        veg_dishes: int = 3,
        spicy_dishes: int = 0,
        max_attempts: int = 200,
    ) -> PlanResult:
        """Build a weekly plan and append extra veg dishes if possible."""

        # Recipe collection and validation
        if not self._recipes:
            raise ValueError("No recipes available to plan.")
        if veg_dishes < 0:
            raise ValueError("veg_dishes must be non-negative.")
        if spicy_dishes < 0:
            raise ValueError("spicy_dishes must be non-negative.")

        recipes = self._filter_by_time(self._recipes, max_total_time_per_dish)
        if not recipes:
            raise ValueError("No recipes fit the time constraints.")

        meat_target = self._days

        non_spicy_recipes = [r for r in recipes if not r.spicy]
        spicy_recipes = [r for r in recipes if r.spicy]

        meat_recipes = [r for r in non_spicy_recipes if r.has_meat]
        fish_names = {
            name for name, item in INGREDIENT_MEAT.items() if item.kind == MeatKind.FISH
        }
        fish_recipes = [
            r for r in meat_recipes if any(ing in fish_names for ing in r.ingredients)
        ]
        veg_recipes = [r for r in non_spicy_recipes if not r.has_meat]

        if not meat_recipes:
            return None

        # Build a plan for meat
        best_meat: list[Recipe] | None = None
        best_total_time: int = 0
        best_overlap: int = 0

        for _ in range(max_attempts):
            if fish_recipes:
                fish_pick = self._sample_dishes(fish_recipes, 1)
                if not fish_pick:
                    continue
                remaining_meat = [r for r in meat_recipes if r not in fish_pick]
                if meat_target > 1 and len(remaining_meat) < meat_target - 1:
                    continue
                meat_selection = list(fish_pick)
                if meat_target > 1:
                    rest = self._sample_dishes(remaining_meat, meat_target - 1)
                    if not rest:
                        continue
                    meat_selection.extend(rest)
                self._random.shuffle(meat_selection)
            else:
                meat_selection = self._sample_dishes(meat_recipes, meat_target)
            if not meat_selection:
                continue

            total_time = sum(r.total_time for r in meat_selection)
            if max_weekly_time is not None and total_time > max_weekly_time:
                continue

            overlap = self._ingredient_meat_overlap(meat_selection)


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

        # Best effort to add configured non-spicy veg dishes
        veg_selection = (
            self._sample_dishes(veg_recipes, veg_dishes, with_replacement=True)
            if veg_dishes > 0 and veg_recipes
            else []
        )
        spicy_selection = (
            self._sample_dishes(spicy_recipes, spicy_dishes, with_replacement=True)
            if spicy_dishes > 0 and spicy_recipes
            else []
        )
        if spicy_dishes > 0 and not spicy_recipes:
            logger.warning(
                "No spicy recipes available; requested %s spicy dishes, returning best effort.",
                spicy_dishes,
            )

        result = PlanResult(
            recipes=tuple(best_meat + veg_selection + spicy_selection),
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
    def _ingredient_meat_overlap(recipes: Iterable[Recipe]) -> int:
        """Count repeated meat types across recipes."""
        counts: dict[str, int] = {}
        for recipe in recipes:
            for ingredient in recipe.ingredients:
                try:
                    meat_type = INGREDIENT_MEAT.get(ingredient).kind
                    counts[meat_type] = counts.get(meat_type, 0) + 1
                except AttributeError:
                    continue
        return sum(count - 1 for count in counts.values() if count > 1)
