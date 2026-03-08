import io
import re
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from eat_what import cli
from eat_what.storage import Recipe


class PlannerCliListModeTests(unittest.TestCase):
    def test_parser_accepts_short_and_long_list_flags(self) -> None:
        parser = cli.build_parser()

        args_short = parser.parse_args(["-l"])
        args_long = parser.parse_args(["--list"])

        self.assertTrue(args_short.list)
        self.assertTrue(args_long.list)

    def test_main_list_mode_prints_all_recipes_and_skips_planner(self) -> None:
        parser = Mock()
        parser.parse_args.return_value = SimpleNamespace(
            recipes="data/recipes.csv",
            list=True,
            seed=None,
            max_time=None,
            max_weekly_time=400,
            max_overlap=6,
            veg_dishes=3,
            spicy_dishes=0,
        )
        recipes = [
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
                ingredients=("green beans",),
                prep_time=5,
                cook_time=5,
                has_meat=False,
                spicy=False,
            ),
        ]

        with patch.object(cli, "build_parser", return_value=parser), patch.object(
            cli, "load_recipes", return_value=recipes
        ), patch.object(cli, "WeeklyPlanner") as mock_planner, patch(
            "sys.stdout", new_callable=io.StringIO
        ) as stdout:
            exit_code = cli.main()

        self.assertEqual(exit_code, 0)
        mock_planner.assert_not_called()
        output = stdout.getvalue()
        output_plain = re.sub(r"\x1b\[[0-9;]*m", "", output)
        self.assertIn("All Recipes", output)
        self.assertIn("1. dish_a", output_plain)
        self.assertIn("2. dish_b", output_plain)


if __name__ == "__main__":
    unittest.main()
