from scenes.world_engine import WorldTemplate

TEMPLATES = [
    WorldTemplate(
        name_prefixes=["废弃的", "血腥的", "变异的", "腐朽的", "寂静的"],
        desc_template="你来到了一个[环境]的末日废土。这里曾经是繁华的[地形1]，但现在只剩下无尽的尸骸和饥饿的变异体。",
        terrains=["废弃都会", "地下避难所", "黑暗医院", "封锁的高速公路", "军方隔离区"],
        enemy_pool=[
            {"name": "游荡丧尸", "hp": 50, "attack": 15, "agi": 5, "drop_points": 20},
            {"name": "变异猎犬", "hp": 40, "attack": 25, "agi": 20, "drop_points": 30},
            {"name": "舔食者", "hp": 120, "attack": 35, "agi": 25, "defense": 10, "drop_points": 80},
            {"name": "巨型暴君", "hp": 300, "attack": 50, "agi": 10, "defense": 20, "drop_points": 200}
        ],
        quest_pool=[
            {"type": "survive", "desc": "在这个修罗场中存活 {target} 步", "base_value": 8},
            {"type": "kill", "desc": "清理 {target} 只游荡的怪物", "base_value": 12},
            {"type": "boss", "desc": "寻找并击杀该区域的变异母体", "base_value": 10}
        ],
        event_pool=["zombie_world"],
        env_effects=["弥漫着尸臭", "下着酸雨", "死寂无声", "布满暗红血迹"]
    ),
    WorldTemplate(
        name_prefixes=["深渊的", "诅咒的", "幽暗的", "失落的", "血祭的"],
        desc_template="你坠入了一个[环境]的奇幻领域。前方是深不可测的[地形1]，传说中隐藏着神明的遗物。",
        terrains=["古老陵墓", "毒气沼泽", "哥布林营地", "龙之巢穴", "水晶洞穴"],
        enemy_pool=[
            {"name": "哥布林掠夺者", "hp": 40, "attack": 15, "agi": 25, "drop_points": 30},
            {"name": "剧毒史莱姆", "hp": 80, "attack": 15, "agi": 5, "defense":5, "drop_points": 30},
            {"name": "兽人狂战士", "hp": 150, "attack": 35, "agi": 10, "defense": 10, "drop_points": 120},
            {"name": "烈焰幼龙", "hp": 400, "attack": 70, "agi": 30, "defense": 30, "drop_points": 500}
        ],
        quest_pool=[
            {"type": "survive", "desc": "在恶劣环境中生存 {target} 步", "base_value": 10},
            {"type": "kill", "desc": "剿灭 {target} 只深渊魔物", "base_value": 10},
            {"type": "boss", "desc": "发掘并消灭远古守卫", "base_value": 12}
        ],
        event_pool=["fantasy_world"],
        env_effects=["魔力紊乱", "令人窒息", "满是诅咒气息", "幽暗无光"]
    ),
    WorldTemplate(
        name_prefixes=["赛博的", "霓虹的", "轰炸的", "机械的", "暴走的"],
        desc_template="你传送到了一个[环境]的未来殖民星。在钢铁铸成的[地形1]里，各大势力正在疯狂交火。",
        terrains=["霓虹黑市", "高空轻轨", "荒漠提炼厂", "克隆人培育中心", "AI核心机房"],
        enemy_pool=[
            {"name": "叛军士兵", "hp": 100, "attack": 30, "agi": 15, "drop_points": 40},
            {"name": "安保无人机", "hp": 60, "attack": 20, "agi": 35, "defense":10, "drop_points": 40},
            {"name": "赛博忍者", "hp": 200, "attack": 60, "agi": 45, "defense": 15, "drop_points": 150},
            {"name": "重装机甲 (Boss)", "hp": 800, "attack": 120, "agi": 15, "defense": 50, "drop_points": 800}
        ],
        quest_pool=[
            {"type": "survive", "desc": "躲避两军清剿，坚持 {target} 步", "base_value": 12},
            {"type": "kill", "desc": "破坏 {target} 台敌对武装单位", "base_value": 15},
            {"type": "boss", "desc": "突入核心指挥室，斩首长官", "base_value": 15}
        ],
        event_pool=[],
        env_effects=["霓虹闪烁但十分冰冷", "电磁干扰极其强烈", "枪声不断", "充满全息投影污染"]
    ),
    WorldTemplate(
        name_prefixes=["混沌的", "不可名状的", "疯狂的", "呓语的", "星海的"],
        desc_template="这里是[环境]的旧日支配者领域，你在[地形1]中每走一步都能听到理智崩溃的低语。",
        terrains=["拉莱耶遗迹", "血肉回廊", "深海祭坛", "迷雾小镇", "星之彩矿区"],
        enemy_pool=[
            {"name": "深潜者", "hp": 200, "attack": 50, "agi": 20, "defense": 30, "drop_points": 100},
            {"name": "星之眷族", "hp": 400, "attack": 80, "agi": 10, "defense": 50, "drop_points": 200},
            {"name": "无形之子", "hp": 300, "attack": 60, "agi": 40, "defense": 10, "drop_points": 150},
            {"name": "修格斯", "hp": 800, "attack": 120, "agi": 5, "defense": 80, "drop_points": 500}
        ],
        quest_pool=[
            {"type": "survive", "desc": "在理智耗尽前支撑 {target} 步", "base_value": 8},
            {"type": "boss", "desc": "打断亵渎仪式，消灭旧日化身", "base_value": 1}
        ],
        event_pool=[],
        env_effects=["充斥着亵渎的低语", "令人头晕目眩", "充满滑腻触手", "空间几何极其扭曲"]
    ),
    WorldTemplate(
        name_prefixes=["修真的", "仙侠的", "灵气的", "九天的", "洪荒的"],
        desc_template="你踏入了[环境]的修真界。在[地形1]中，无数修士为了得道飞升而不择手段。",
        terrains=["青云山脉", "落日灵谷", "万妖之森", "上古剑冢", "天雷秘境"],
        enemy_pool=[
            {"name": "练气期劫匪", "hp": 150, "attack": 40, "agi": 30, "drop_points": 60},
            {"name": "低阶妖兽", "hp": 250, "attack": 60, "agi": 20, "defense": 20, "drop_points": 80},
            {"name": "筑基期散修", "hp": 450, "attack": 100, "agi": 40, "defense": 30, "drop_points": 150},
            {"name": "结丹期大妖", "hp": 1200, "attack": 250, "agi": 60, "defense": 100, "drop_points": 600}
        ],
        quest_pool=[
            {"type": "kill", "desc": "斩杀 {target} 名拦路的修士/妖兽", "base_value": 10},
            {"type": "boss", "desc": "夺取秘境传承，击败守护兽", "base_value": 1}
        ],
        event_pool=[],
        env_effects=["灵气充沛", "剑气纵横", "仙云缭绕", "法则轰鸣"]
    ),
    WorldTemplate(
        name_prefixes=["武侠的", "刀剑的", "江湖的", "血雨的", "恩怨的"],
        desc_template="这是[环境]的混乱武林，[地形1]上到处是门派仇杀和刀光剑影。",
        terrains=["绝情谷", "光明顶", "华山之巅", "破败龙门客栈", "锦衣卫昭狱"],
        enemy_pool=[
            {"name": "江湖杂兵", "hp": 80, "attack": 20, "agi": 15, "drop_points": 30},
            {"name": "名门下徒", "hp": 120, "attack": 35, "agi": 20, "defense": 5, "drop_points": 50},
            {"name": "魔教香主", "hp": 250, "attack": 60, "agi": 35, "defense": 15, "drop_points": 100},
            {"name": "武林泰斗", "hp": 600, "attack": 100, "agi": 50, "defense": 40, "drop_points": 300}
        ],
        quest_pool=[
            {"type": "kill", "desc": "惩恶扬善，击杀 {target} 个恶徒", "base_value": 15},
            {"type": "boss", "desc": "击败走火入魔的魔教教主", "base_value": 1}
        ],
        event_pool=[],
        env_effects=["肃杀之气弥漫", "飘着细雨", "黄沙漫天", "满地残砖断瓦"]
    ),
    WorldTemplate(
        name_prefixes=["蒸汽的", "发条的", "黄铜的", "齿轮的", "煤烟的"],
        desc_template="你置身于[环境]的维多利亚时代。巨大的齿轮在[地形1]上轰鸣作响。",
        terrains=["工业下水道", "空中飞艇", "机械钟塔", "伦敦浓雾街区", "发条工厂"],
        enemy_pool=[
            {"name": "发条猎犬", "hp": 90, "attack": 25, "agi": 30, "defense": 15, "drop_points": 40},
            {"name": "齿轮守卫", "hp": 150, "attack": 40, "agi": 10, "defense": 30, "drop_points": 60},
            {"name": "蒸汽机甲", "hp": 400, "attack": 80, "agi": 5, "defense": 60, "drop_points": 150},
            {"name": "机械改造寡头", "hp": 900, "attack": 120, "agi": 20, "defense": 80, "drop_points": 450}
        ],
        quest_pool=[
            {"type": "kill", "desc": "摧毁 {target} 台失控的机械", "base_value": 12},
            {"type": "boss", "desc": "击垮工厂的核心暴君", "base_value": 1}
        ],
        event_pool=[],
        env_effects=["煤烟呛人", "齿轮声震耳欲聋", "蒸汽弥漫", "满是黄铜锈迹"]
    ),
    WorldTemplate(
        name_prefixes=["太空的", "异星的", "异形的", "幽闭的", "失重的"],
        desc_template="你登上了[环境]的废弃空间站。[地形1]里到处是外星生物的黏液和宇航员的残骸。",
        terrains=["休眠舱区域", "动力引擎室", "生态温室", "外星舰桥", "气闸长廊"],
        enemy_pool=[
            {"name": "抱脸虫", "hp": 30, "attack": 80, "agi": 50, "drop_points": 50},
            {"name": "工蜂异形", "hp": 150, "attack": 60, "agi": 40, "defense": 20, "drop_points": 90},
            {"name": "禁卫异形", "hp": 350, "attack": 100, "agi": 30, "defense": 50, "drop_points": 180},
            {"name": "异形女皇", "hp": 1200, "attack": 180, "agi": 20, "defense": 100, "drop_points": 800}
        ],
        quest_pool=[
            {"type": "survive", "desc": "在无尽的猎杀中存活 {target} 步", "base_value": 12},
            {"type": "boss", "desc": "消灭正在产卵的异形女皇", "base_value": 1}
        ],
        event_pool=[],
        env_effects=["重力异常", "闪烁着红色警报灯", "充满腐蚀性酸液", "死寂又压抑"]
    ),
    WorldTemplate(
        name_prefixes=["史前的", "蛮荒的", "侏罗纪的", "巨兽的", "原始的"],
        desc_template="你回到了[环境]的史前时代。[地形1]中随时可能窜出恐怖的远古统治者。",
        terrains=["原始丛林", "火山盆地", "蕨类沼泽", "巨大峡谷", "史前瀑布"],
        enemy_pool=[
            {"name": "迅猛龙", "hp": 80, "attack": 40, "agi": 45, "drop_points": 45},
            {"name": "三角龙", "hp": 300, "attack": 70, "agi": 15, "defense": 50, "drop_points": 120},
            {"name": "翼龙", "hp": 120, "attack": 50, "agi": 60, "drop_points": 80},
            {"name": "霸王龙", "hp": 1500, "attack": 200, "agi": 25, "defense": 80, "drop_points": 800}
        ],
        quest_pool=[
            {"type": "survive", "desc": "在恐龙的狩猎中生存 {target} 步", "base_value": 15},
            {"type": "boss", "desc": "猎杀处于食物链顶端的霸王龙", "base_value": 1}
        ],
        event_pool=[],
        env_effects=["气候异常炎热", "大地震颤", "充满原始野性", "植被遮天蔽日"]
    ),
    WorldTemplate(
        name_prefixes=["交界地的", "黑暗的", "传火的", "堕落的", "褪色的"],
        desc_template="欢迎来到[环境]的黑暗魂系世界。[地形1]上徘徊着失去理智的游魂和恐怖的畸变骑士。",
        terrains=["腐败盖利德", "黄金树王城", "深邃教堂", "不死镇", "古龙顶峰"],
        enemy_pool=[
            {"name": "活尸士兵", "hp": 100, "attack": 40, "agi": 15, "defense": 10, "drop_points": 50},
            {"name": "发狂的黑骑士", "hp": 350, "attack": 90, "agi": 25, "defense": 60, "drop_points": 150},
            {"name": "咒蛙", "hp": 50, "attack": 150, "agi": 40, "drop_points": 100},
            {"name": "半神", "hp": 2000, "attack": 250, "agi": 40, "defense": 150, "drop_points": 1500}
        ],
        quest_pool=[
            {"type": "survive", "desc": "在这片充满绝望的土地上坚持 {target} 步", "base_value": 10},
            {"type": "boss", "desc": "击倒手握大卢恩的半神", "base_value": 1}
        ],
        event_pool=[],
        env_effects=["天空犹如滴血般暗红", "充满绝望与死亡的气息", "遍地白骨", "黄金树的光芒黯淡"]
    )
]
