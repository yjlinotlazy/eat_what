from dataclasses import dataclass
from enum import Enum


class VegatableKind(Enum):
    LEAFY = "leafy"
    ROOT = "root"
    CRUCIFEROUS = "cruciferous"
    ALLIUM = "allium"
    NIGHTSHADE = "nightshade"
    LEGUME = "legume"
    SQUASH = "squash"
    OTHER = "other"


@dataclass(frozen=True)
class VegatableIngredient:
    kind: VegatableKind
    cn: str


INGREDIENT_VEGATABLE = {
    "broccoli": VegatableIngredient(VegatableKind.CRUCIFEROUS, "西兰花"),
    "cabbage": VegatableIngredient(VegatableKind.CRUCIFEROUS, "包菜"),
    "carrot": VegatableIngredient(VegatableKind.ROOT, "胡萝卜"),
    "cauliflower": VegatableIngredient(VegatableKind.CRUCIFEROUS, "菜花"),
    "celery": VegatableIngredient(VegatableKind.OTHER, "芹菜"),
    "corn": VegatableIngredient(VegatableKind.OTHER, "玉米"),
    "cucumber": VegatableIngredient(VegatableKind.OTHER, "黄瓜"),
    "eggplant": VegatableIngredient(VegatableKind.NIGHTSHADE, "茄子"),
    "garlic": VegatableIngredient(VegatableKind.ALLIUM, "大蒜"),
    "ginger": VegatableIngredient(VegatableKind.OTHER, "姜"),
    "green beans": VegatableIngredient(VegatableKind.LEGUME, "四季豆"),
    "kale": VegatableIngredient(VegatableKind.LEAFY, "羽衣甘蓝"),
    "lettuce": VegatableIngredient(VegatableKind.LEAFY, "生菜"),
    "mushroom": VegatableIngredient(VegatableKind.OTHER, "蘑菇"),
    "onion": VegatableIngredient(VegatableKind.ALLIUM, "洋葱"),
    "potato": VegatableIngredient(VegatableKind.NIGHTSHADE, "土豆"),
    "spinach": VegatableIngredient(VegatableKind.LEAFY, "菠菜"),
    "sweet potato": VegatableIngredient(VegatableKind.ROOT, "红薯"),
    "tofu": VegatableIngredient(VegatableKind.OTHER, "豆腐"),
    "tomato": VegatableIngredient(VegatableKind.NIGHTSHADE, "番茄"),
    "vermicelli": VegatableIngredient(VegatableKind.OTHER, "粉条"),
    "winter melon": VegatableIngredient(VegatableKind.SQUASH, "冬瓜"),
    "zucchini": VegatableIngredient(VegatableKind.SQUASH, "西葫芦"),
}
