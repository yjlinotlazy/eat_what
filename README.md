# 吃啥 (`eat-what`)

基于菜谱 CSV 生成每周菜单、输出采购清单，并提供交互式菜谱管理工具。

## 功能

- `eat-what`：生成每周菜单（默认 7 个荤主菜）并追加若干素菜结果。
- `eat-what-recipe`：新增菜谱（支持从已有食材中选择，也支持新增食材）。
- `eat-what-pick`：先选择食材，再列出所有这些食材能做的菜谱。

## 安装

```bash
pip install -e .
```

## 数据文件

默认菜谱文件：`data/recipes.csv`。用户可提供自己的菜谱文件，但必须符合同一个格式。

当前列：
- `cook_time`
- `has_meat`
- `ingredients`（分号分隔，如 `pork belly;ginger`）
- `name`
- `prep_time`
- `spicy`（默认 `False`）

说明：
- 读取的时候如果出错，会显示哪一行错了并跳过，不会中断程序。

## CLI 用法

### 1) 生成菜单：`eat-what`

基本款

```bash
eat-what
```

提供自己的菜单

```bash
eat-what --recipes ~/my_recipes.csv
```

完整自定义：

```bash
eat-what \
  --recipes data/recipes.csv \
  --max-time 60 \
  --max-weekly-time 400 \
  --max-overlap 6 \
  --veg-dishes 3 \
  --seed 42
```

参数说明：
- `--max-time, -t`：单道菜最多允许几分钟（`prep_time + cook_time`）。
- `--max-weekly-time, -m`：一周做菜总耗时（不包括素菜）。
- `--max-overlap, -o`：最多允许几样食材重复。
- `--veg-dishes, -v`：额外的素菜数量，默认 `3`。
- `--seed, -s`：随机种子，基本不会用。

#### 实现方法：

- 主菜单默认按 `days=7` 随机选择 7 道含肉菜，从肉类菜谱里选。随机选出来的如果超过每周时限，就重来一轮。
- 如果存在鱼类菜谱，会保证结果里至少 1 道鱼类。
- 再从素菜谱里选 `-v` 指定数量的素菜（可重复）。

### 2) 新增菜谱：`eat-what-recipe`

```bash
eat-what-recipe --recipes data/recipes.csv
```

### 3) 食材推导菜谱：`eat-what-pick`

```bash
eat-what-pick --recipes data/recipes.csv
```

## 代码结构

- `src/eat_what/cli.py`：主菜单 CLI。
- `src/eat_what/recipe_cli.py`：新增菜谱 CLI。
- `src/eat_what/pick_cli.py`：食材反查菜谱 CLI。
- `src/eat_what/planner.py`：菜单生成逻辑。
- `src/eat_what/storage.py`：CSV 读写与校验。
- `src/eat_what/text_format.py`：终端对齐与颜色封装。
