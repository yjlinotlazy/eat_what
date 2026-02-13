import unittest
from pathlib import Path

from eat_what.storage import default_recipes_path


class StorageDefaultsTests(unittest.TestCase):
    def test_default_recipes_path_points_to_existing_csv(self) -> None:
        path = default_recipes_path()
        self.assertEqual(path.name, "recipes.csv")
        self.assertTrue(path.exists())
        self.assertEqual(path.suffix, ".csv")
        self.assertIn("data", Path(path).parts)


if __name__ == "__main__":
    unittest.main()
