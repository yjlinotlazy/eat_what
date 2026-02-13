from dataclasses import dataclass
from enum import Enum

"""Meat ingredient metadata (EN name, CN name, and kind)."""


class MeatKind(Enum):
    """High-level meat category."""
    PORK = "pork"
    BEEF = "beef"
    CHICKEN = "chicken"
    LAMB = "lamb"
    DUCK = "duck"
    FISH = "fish"


@dataclass(frozen=True)
class MeatIngredient:
    """Meat ingredient with kind and Chinese name."""
    kind: MeatKind
    cn: str


INGREDIENT_MEAT = {
    "bacon": MeatIngredient(MeatKind.PORK, "培根"),
    "beef brisket": MeatIngredient(MeatKind.BEEF, "牛腩"),
    "beef steak": MeatIngredient(MeatKind.BEEF, "牛排"),
    "chicken breast": MeatIngredient(MeatKind.CHICKEN, "鸡胸肉"),
    "chicken drumstick": MeatIngredient(MeatKind.CHICKEN, "鸡腿"),
    "chicken thigh": MeatIngredient(MeatKind.CHICKEN, "鸡腿肉"),
    "chicken wings": MeatIngredient(MeatKind.CHICKEN, "鸡翅"),
    "duck breast": MeatIngredient(MeatKind.DUCK, "鸭胸"),
    "ground beef": MeatIngredient(MeatKind.BEEF, "牛肉末"),
    "lamb chops": MeatIngredient(MeatKind.LAMB, "羊排"),
    "pork belly": MeatIngredient(MeatKind.PORK, "五花肉"),
    "pork ribs": MeatIngredient(MeatKind.PORK, "排骨"),
    "pork shoulder": MeatIngredient(MeatKind.PORK, "猪肩肉"),
    "salmon": MeatIngredient(MeatKind.FISH, "三文鱼"),    "beef piece": MeatIngredient(MeatKind.BEEF, "火锅牛肉片"),
    "mussel": MeatIngredient(MeatKind.FISH, "青口"),

}
