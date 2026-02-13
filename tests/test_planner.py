import unittest

from eat_what.planner import find_remaining_meat
from eat_what.storage import Recipe


class FindRemainingMeatTests(unittest.TestCase):
    def test_excludes_recipes_with_same_meat_kind(self) -> None:
        # Selected recipe uses pork kind (via "pork belly").
        selected = [
            Recipe(
                name="dish_selected",
                ingredients=("pork belly", "scallion"),
                prep_time=5,
                cook_time=10,
                has_meat=True,
                spicy=False,
            )
        ]
        all_recipes = [
            Recipe(
                name="dish_same_kind",
                ingredients=("meatball",),
                prep_time=5,
                cook_time=5,
                has_meat=True,
                spicy=False,
            ),
            Recipe(
                name="dish_other_kind",
                ingredients=("beef brisket",),
                prep_time=5,
                cook_time=5,
                has_meat=True,
                spicy=False,
            ),
            Recipe(
                name="dish_no_meat_kind",
                ingredients=("scallion",),
                prep_time=5,
                cook_time=5,
                has_meat=False,
                spicy=False,
            ),
        ]

        # Candidate set includes:
        # - another pork dish ("meatball") -> should be excluded
        # - a beef dish -> should remain
        # - a dish without known meat ingredient -> should remain
        remaining = find_remaining_meat(all_recipes, selected)

        # Only recipes with non-overlapping meat kinds are returned.
        self.assertEqual(
            [recipe.name for recipe in remaining],
            ["dish_other_kind", "dish_no_meat_kind"],
        )

    def test_returns_all_when_no_selected_recipes(self) -> None:
        # With no selected recipes, there are no blocked meat kinds.
        all_recipes = [
            Recipe(
                name="dish_a",
                ingredients=("pork belly",),
                prep_time=5,
                cook_time=10,
                has_meat=True,
                spicy=False,
            ),
            Recipe(
                name="dish_b",
                ingredients=("beef brisket",),
                prep_time=5,
                cook_time=10,
                has_meat=True,
                spicy=False,
            ),
        ]

        remaining = find_remaining_meat(all_recipes, [])

        # Function should return all candidates unchanged.
        self.assertEqual([recipe.name for recipe in remaining], ["dish_a", "dish_b"])


if __name__ == "__main__":
    unittest.main()
