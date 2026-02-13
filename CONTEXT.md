# Repository Context: `eat-what`

## Purpose

`eat-what` is a Python CLI project for meal planning from a recipe CSV.
It supports:

- generating a weekly meat-focused plan with optional veg/spicy add-ons,
- printing a shopping list aggregated from selected recipes,
- interactively adding recipes and new ingredients,
- finding recipes that can be cooked from selected ingredients.

Primary language in user output is Chinese, while code/docstrings are mostly English.

## Tech Stack

- Python `>=3.9`
- Packaging: `setuptools` via `pyproject.toml`
- Dependency: `pandas>=2.0`
- Source layout: `src/` package style

## Entrypoints

Installed CLI commands (`pyproject.toml`):

- `eat-what` -> `eat_what.cli:main`
- `eat-what-recipe` -> `eat_what.recipe_cli:main`
- `eat-what-pick` -> `eat_what.pick_cli:main`

Typical local install:

```bash
pip install -e .
```

## Data Model and Files

Default dataset: `data/recipes.csv`

Required CSV columns:

- `name`
- `ingredients` (semicolon-separated, e.g. `pork belly;ginger`)
- `prep_time`
- `cook_time`
- `has_meat`

Optional CSV column:

- `spicy` (defaults to `False` when absent)

Core model:

- `Recipe` dataclass in `src/eat_what/storage.py`
  - fields: `name`, `ingredients`, `prep_time`, `cook_time`, `has_meat`, `spicy`
  - computed property: `total_time = prep_time + cook_time`

## Code Map

- `src/eat_what/cli.py`
  - planner CLI, output formatting, shopping-list aggregation.
- `src/eat_what/planner.py`
  - planning algorithm and constraints.
- `src/eat_what/storage.py`
  - CSV load/save, boolean parsing, tolerant row-level validation.
- `src/eat_what/recipe_cli.py`
  - interactive recipe creation, optional ingredient dictionary updates.
- `src/eat_what/pick_cli.py`
  - ingredient-driven recipe lookup.
- `src/eat_what/selection.py`
  - shared numbered-selection prompt helper.
- `src/eat_what/ingredients_meat.py`
  - meat ingredient dictionary + kind enum (includes fish type).
- `src/eat_what/ingredients_vegatable.py`
  - veg ingredient dictionary.
- `src/eat_what/text_format.py`
  - ANSI color and display-width alignment helpers.

## Planning Behavior (`WeeklyPlanner.plan`)

High-level flow:

1. Validate input recipe set and argument ranges.
2. Optionally filter by per-dish max time.
3. Build a 7-day meat plan (`days=7` default).
4. If fish recipes exist, force at least one fish dish in meat plan.
5. Retry random sampling (`max_attempts=200`) to satisfy weekly-time and overlap goals.
6. Append veg and spicy dishes as best-effort add-ons (with replacement).

Reported metrics in result:

- `total_time`: total for meat-plan portion only.
- `ingredient_overlap`: repeated meat-kind count via `INGREDIENT_MEAT` type grouping.

## Important Implementation Notes

- `ingredients_vegatable.py` and related symbols intentionally use the misspelling
  `vegatable`; keep naming consistent unless doing a coordinated refactor.
- `WeeklyPlanner.plan` currently has one inconsistent path:
  when no meat recipes exist, it returns `None` even though the declared return type is
  `PlanResult`; callers generally expect a valid plan object.
- CLI output uses ANSI colors and width-aware alignment to support mixed
  Chinese/English display.
- CSV loading is tolerant: invalid rows are skipped with warnings instead of failing fast.

## Quick Run Commands

```bash
eat-what --recipes data/recipes.csv
eat-what-recipe --recipes data/recipes.csv
eat-what-pick --recipes data/recipes.csv
```

## Suggested Guardrails for Future Changes

- Preserve CSV compatibility unless intentionally migrating schema.
- Keep `pyproject.toml` script entrypoints in sync with module refactors.
- Add tests before changing planner randomness/constraints to avoid behavioral regressions.
