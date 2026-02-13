import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from eat_what import recipe_cli


class RecipeCliSpicyInferenceTests(unittest.TestCase):
    def test_name_with_lazi_sets_spicy_true_without_prompt(self) -> None:
        # Scenario: dish name contains "辣", so spicy should be inferred as True
        # and the explicit spicy prompt should be skipped.
        parser = Mock()
        parser.parse_args.return_value = SimpleNamespace(recipes="data/recipes.csv")

        with patch.object(recipe_cli, "build_parser", return_value=parser), patch.object(
            recipe_cli, "load_recipes", return_value=[]
        ), patch.object(
            recipe_cli, "_prompt_unique_name", return_value="辣子鸡"
        ), patch.object(
            recipe_cli, "_prompt_ingredients", return_value=["chicken thigh"]
        ), patch.object(
            recipe_cli, "_prompt_int", side_effect=[5, 10]
        ), patch.object(
            recipe_cli,
            "_prompt_bool",
            side_effect=AssertionError("_prompt_bool should not be called"),
        ), patch.object(recipe_cli, "save_recipes") as mock_save:
            exit_code = recipe_cli.main()

        # Validate saved recipe has spicy=True from name-based inference.
        self.assertEqual(exit_code, 0)
        mock_save.assert_called_once()
        saved_path, saved_recipes = mock_save.call_args.args
        self.assertEqual(saved_path, Path("data/recipes.csv"))
        self.assertEqual(saved_recipes[-1].name, "辣子鸡")
        self.assertTrue(saved_recipes[-1].spicy)
        self.assertTrue(saved_recipes[-1].has_meat)

    def test_name_without_lazi_uses_prompt_bool(self) -> None:
        # Scenario: name does not contain "辣", so CLI should fall back to
        # interactive spicy prompt and use that returned value.
        parser = Mock()
        parser.parse_args.return_value = SimpleNamespace(recipes="data/recipes.csv")

        with patch.object(recipe_cli, "build_parser", return_value=parser), patch.object(
            recipe_cli, "load_recipes", return_value=[]
        ), patch.object(
            recipe_cli, "_prompt_unique_name", return_value="清炒豆角"
        ), patch.object(
            recipe_cli, "_prompt_ingredients", return_value=["green beans"]
        ), patch.object(
            recipe_cli, "_prompt_int", side_effect=[3, 8]
        ), patch.object(
            recipe_cli, "_prompt_bool", return_value=False
        ) as mock_prompt_bool, patch.object(recipe_cli, "save_recipes") as mock_save:
            exit_code = recipe_cli.main()

        # Validate the prompt path is used and saved spicy flag matches prompt output.
        self.assertEqual(exit_code, 0)
        mock_prompt_bool.assert_called_once_with("Is this dish spicy? (y/N): ")
        saved_path, saved_recipes = mock_save.call_args.args
        self.assertEqual(saved_path, Path("data/recipes.csv"))
        self.assertEqual(saved_recipes[-1].name, "清炒豆角")
        self.assertFalse(saved_recipes[-1].spicy)
        self.assertFalse(saved_recipes[-1].has_meat)


class RecipeCliDuplicateNameTests(unittest.TestCase):
    def test_prompt_unique_name_retries_when_name_exists(self) -> None:
        # Scenario: user first enters an existing name, then enters a new one.
        # Behavior: helper should prompt again instead of exiting.
        with patch.object(
            recipe_cli,
            "_prompt_non_empty",
            side_effect=["红烧肉", "新菜名"],
        ) as mock_prompt_non_empty, patch("builtins.print") as mock_print:
            name = recipe_cli._prompt_unique_name({"红烧肉"})

        # Validate function keeps asking and eventually returns a unique name.
        self.assertEqual(name, "新菜名")
        self.assertEqual(mock_prompt_non_empty.call_count, 2)
        mock_print.assert_any_call(
            "Recipe name already exists. Please choose a different name."
        )


if __name__ == "__main__":
    unittest.main()
