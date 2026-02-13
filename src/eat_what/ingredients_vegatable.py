from dataclasses import dataclass

"""Vegetable ingredient metadata (EN name, CN name)."""


@dataclass(frozen=True)
class VegatableIngredient:
    """Vegetable ingredient with Chinese name."""
    cn: str


INGREDIENT_VEGATABLE = {
    "broccoli": VegatableIngredient("西兰花"),
    "cabbage": VegatableIngredient("包菜"),
    "carrot": VegatableIngredient("胡萝卜"),
    "cauliflower": VegatableIngredient("菜花"),
    "celery": VegatableIngredient("芹菜"),
    "corn": VegatableIngredient("玉米"),
    "cucumber": VegatableIngredient("黄瓜"),
    "eggplant": VegatableIngredient("茄子"),
    "garlic": VegatableIngredient("大蒜"),
    "ginger": VegatableIngredient("姜"),
    "green beans": VegatableIngredient("四季豆"),
    "kale": VegatableIngredient("羽衣甘蓝"),
    "lettuce": VegatableIngredient("生菜"),
    "mushroom": VegatableIngredient("蘑菇"),
    "onion": VegatableIngredient("洋葱"),
    "potato": VegatableIngredient("土豆"),
    "spinach": VegatableIngredient("菠菜"),
    "sweet potato": VegatableIngredient("红薯"),
    "tofu": VegatableIngredient("豆腐"),
    "tomato": VegatableIngredient("番茄"),
    "vermicelli": VegatableIngredient("粉条"),
    "winter melon": VegatableIngredient("冬瓜"),
    "zucchini": VegatableIngredient("西葫芦"),
    "Sigua": VegatableIngredient("丝瓜"),
    "brussel sprouts": VegatableIngredient("小包菜"),
    "scallion": VegatableIngredient("大葱"),
    "napa cabbage": VegatableIngredient("白菜"),
    "pepper": VegatableIngredient("辣椒"),
    "green pepper": VegatableIngredient("青椒"),
}
