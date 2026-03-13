import random

class Equipment:
    def __init__(self):
        self.id = random.randint(100000, 999999)
        self.name = ""
        self.type = ""          # "weapon", "armor", "accessory"
        self.subtype = ""       # e.g., "sword", "helmet", "ring"
        self.quality = ""       # "白板", "精良", "稀有", "史诗", "传说"
        self.level_req = 1
        self.attributes = {}    # {"str": 5, "agi": 3}
        self.special_effects = [] # [{"name": "火焰附加", "value": 10}]
        self.enhance_level = 0
        self.value = 0
        self.desc = ""

def generate_equipment(player_level, difficulty=1.0, specific_quality=None):
    eq = Equipment()
    
    # 1. 选择类型和子类型
    eq.type = random.choice(["weapon", "armor", "accessory"])
    if eq.type == "weapon":
        eq.subtype = random.choice(["sword", "axe", "bow", "staff", "dagger"])
    elif eq.type == "armor":
        eq.subtype = random.choice(["helmet", "chest", "legs", "boots"])
    else:
        eq.subtype = random.choice(["ring", "necklace", "charm"])
        
    # 2. 决定品质
    quality_keys = ["白板", "精良", "稀有", "史诗", "传说"]
    quality_weights = [50, 30, 15, 4, 1]
    if specific_quality and specific_quality in quality_keys:
        eq.quality = specific_quality
    else:
        eq.quality = random.choices(quality_keys, weights=quality_weights)[0]

    # 3. 品质配置
    quality_config = {
        "白板": {"attr_range": (1,1), "effect_range": (0,0), "attr_factor": (0.5,1.0), "base_multi": 1.0},
        "精良": {"attr_range": (1,2), "effect_range": (0,1), "attr_factor": (0.8,1.5), "base_multi": 1.5},
        "稀有": {"attr_range": (2,3), "effect_range": (1,2), "attr_factor": (1.2,2.0), "base_multi": 2.0},
        "史诗": {"attr_range": (3,4), "effect_range": (2,3), "attr_factor": (1.5,2.5), "base_multi": 2.5},
        "传说": {"attr_range": (4,5), "effect_range": (3,4), "attr_factor": (2.0,3.5), "base_multi": 3.0},
    }
    cfg = quality_config[eq.quality]
    
    # 4. 设置等级要求
    eq.level_req = max(1, player_level + random.randint(-2, 3))
    
    # 基础面板值 (Weapon Attack or Armor Defense)
    base_val = int(eq.level_req * cfg["base_multi"] * random.uniform(0.8, 1.2))
    base_val = max(1, base_val)
    if eq.type == "weapon":
        eq.attributes["attack"] = base_val * 2
    elif eq.type == "armor":
        eq.attributes["defense"] = int(base_val * 1.5)

    # 5. 生成附加基础属性
    attr_list = ["str", "agi", "int", "con", "per", "cha"]
    num_attrs = random.randint(int(cfg["attr_range"][0]), int(cfg["attr_range"][1]))
    chosen_attrs = random.sample(attr_list, min(num_attrs, len(attr_list)))
    for attr in chosen_attrs:
        min_val = int(eq.level_req * float(cfg["attr_factor"][0]))
        max_val = int(eq.level_req * float(cfg["attr_factor"][1]))
        eq.attributes[attr] = max(1, random.randint(min_val, max_val))
        
    # 6. 生成特殊效果 (Added new effects like 暴伤增加, 真实伤害)
    effect_pool = [
        {"name": "火焰附加", "min": 5, "max": 25, "suffix": "of Fire"},
        {"name": "寒冰附加", "min": 5, "max": 25, "suffix": "of Frost"},
        {"name": "雷电穿透", "min": 10, "max": 30, "suffix": "of Lightning"},
        {"name": "剧毒蔓延", "min": 2, "max": 15, "suffix": "of Poison"},
        {"name": "神圣打击", "min": 20, "max": 50, "suffix": "of Holy"},
        {"name": "暗影侵蚀", "min": 15, "max": 40, "suffix": "of Shadow"},
        {"name": "生命吸取", "min": 2, "max": 10, "suffix": "of Leech"},
        {"name": "法力护盾", "min": 5, "max": 20, "suffix": "of Mana"},
        {"name": "经验加成", "min": 5, "max": 30, "suffix": "of Wisdom"},
        {"name": "暴击率提升", "min": 1, "max": 10, "suffix": "of Strikes"},
        {"name": "暴伤增加", "min": 10, "max": 50, "suffix": "of Brutality"}, # NEW
        {"name": "闪避率提升", "min": 1, "max": 10, "suffix": "of Evasion"},
        {"name": "伤害反射", "min": 5, "max": 25, "suffix": "of Thorns"},
        {"name": "真实伤害", "min": 10, "max": 40, "suffix": "of Truth"}, # NEW
        {"name": "破甲", "min": 5, "max": 20, "suffix": "of Piercing"},
        {"name": "速度爆发", "min": 2, "max": 8, "suffix": "of Haste"},
        {"name": "坚韧不拔", "min": 10, "max": 40, "suffix": "of Fortitude"},
        {"name": "全属性增强", "min": 1, "max": 5, "suffix": "of the Kings"},
        {"name": "金钱掉落", "min": 10, "max": 50, "suffix": "of Wealth"},
        {"name": "灵魂收割", "min": 5, "max": 15, "suffix": "of Souls"},
        {"name": "时间扭曲", "min": 1, "max": 3, "suffix": "of Time"},
        {"name": "狂暴打击", "min": 15, "max": 35, "suffix": "of Rage"},
        {"name": "虚空之力", "min": 20, "max": 60, "suffix": "of the Void"}
    ]
    num_effects = random.randint(int(cfg["effect_range"][0]), int(cfg["effect_range"][1]))
    chosen_effects = random.sample(effect_pool, min(num_effects, len(effect_pool)))
    for eff in chosen_effects:
        value = random.randint(int(eff["min"]), int(eff["max"]))
        eq.special_effects.append({"name": str(eff["name"]), "value": value, "suffix": eff["suffix"]})
        
    # 7. 生成装备名称
    eq.name = generate_equipment_name(eq)
    
    # 8. 价值与统一描述生成
    eq.value = int(eq.level_req * 15 * cfg["base_multi"])
    
    desc_str = f"要求Lv.{eq.level_req} | 价值:{eq.value}积 "
    if "attack" in eq.attributes: desc_str += f"| 攻击+{eq.attributes['attack']} "
    if "defense" in eq.attributes: desc_str += f"| 防御+{eq.attributes['defense']} "
    for attr in chosen_attrs:
        desc_str += f"| {attr.upper()}+{eq.attributes[attr]} "
    
    if eq.special_effects:
        eff_strs = [f"{e['name']} {e['value']}" for e in eq.special_effects]
        desc_str += f"| 特效: {','.join(eff_strs)}"
        
    eq.desc = desc_str
    
    # 转译为dict供原版系统兼容
    dict_repr = {
        "id": eq.id,
        "name": f"[{eq.quality}] {eq.name}",
        "type": eq.type,
        "subtype": eq.subtype,
        "quality": eq.quality,
        "level_req": eq.level_req,
        "enhance_level": 0,
        "value": eq.value,
        "desc": eq.desc,
        "special_effects": eq.special_effects
    }
    # 混入attributes到根层级保持兼容老代码
    for k, v in eq.attributes.items():
        dict_repr[k] = v
        
    return dict_repr


def generate_equipment_name(eq):
    # 前缀库
    prefix_map = {
        "白板": ["破旧的", "普通的", "褪色的", "生锈的", "劣质的", "残破的", "粗糙的", "黯淡的", "裂开的", "沉重的"],
        "精良": ["精良的", "锋利的", "坚固的", "轻盈的", "打磨过的", "平衡的", "结实的", "耀眼的", "优良的", "无双的"],
        "稀有": ["稀有的", "发光的", "附魔的", "神秘的", "卓越的", "魔法的", "符文的", "幻影的", "灵动的", "水晶的"],
        "史诗": ["古老的", "不朽的", "龙纹的", "失落的", "泰坦的", "星辰的", "虚空的", "圣洁的", "堕落的", "英雄的"],
        "传说": ["神圣的", "深渊的", "混沌的", "创世的", "灭世的", "命运的", "神话的", "奇迹的", "永恒的", "无尽的"]
    }
    
    # 核心词库
    core_map = {
        "sword": "长剑", "axe": "战斧", "bow": "长弓", "staff": "法杖", "dagger": "短刃",
        "helmet": "头盔", "chest": "胸甲", "legs": "裙甲", "boots": "战靴",
        "ring": "指环", "necklace": "项链", "charm": "护符"
    }
    
    # 后缀库 (映射特效名到英文/中文词汇)
    suffix_map = {
        "火焰附加": "之火 (of Fire)",
        "寒冰附加": "之冰 (of Frost)",
        "生命吸取": "之血 (of Leech)",
        "经验加成": "之智 (of Wisdom)"
    }
    
    prefix = random.choice(prefix_map.get(eq.quality, ["未知的"]))
    core = core_map.get(eq.subtype, "物品")
    
    suffixes = []
    for eff in eq.special_effects:
        if "suffix" in eff:
            suffixes.append(eff["suffix"])
            
    if suffixes:
        suffix_str = " & ".join(suffixes)
        return f"{prefix}{core} {suffix_str}"
    else:
        return f"{prefix}{core}"
