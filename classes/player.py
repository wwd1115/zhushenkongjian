import random

class Player:
    def __init__(self, name="轮回者"):
        self.name = name
        self.level = 1
        self.exp = 0
        self.points = 1000  # 初始积分
        self.morality = 0   # 道德值
        
        # 基础属性
        self.str = 10  # 力量
        self.agi = 10  # 敏捷
        self.int = 10  # 智力
        self.con = 10  # 体质
        self.per = 10  # 感知
        self.cha = 10  # 魅力
        
        # 自由属性点
        self.free_stats = 0
        
        # 数据统计与成就
        self.stats = {
            "kills": 0,
            "deaths": 0,
            "points_spent": 0
        }
        self.achievements = []
        
        # 当前状态
        self.status = []
        self.status_effects = []
        
        # 战斗属性（会通过update_stats更新）
        self.max_hp = 0
        self.hp = 0
        self.max_mp = 0
        self.mp = 0
        
        self.skills = []
        self.inventory = []
        self.teammates = []
        self.pets = []           # 拥有的宠物列表
        self.active_pet = None   # 当前出战的宠物
        
        self.bloodline = None    # 血统插槽
        self.cultivation = None  # 功法插槽
        self.equipment = {
            "weapon": None,
            "armor": None,
            "accessory": None
        }
        
        self.update_stats()
        self.hp = self.max_hp
        self.mp = self.max_mp

    def _get_base_bonus(self, stat_name):
        val = 0
        if getattr(self, 'bloodline', None) and isinstance(self.bloodline, dict) and "stats" in self.bloodline:
            val += self.bloodline["stats"].get(stat_name, 0)
        if getattr(self, 'cultivation', None) and isinstance(self.cultivation, dict) and "stats" in self.cultivation:
            val += self.cultivation["stats"].get(stat_name, 0)
        return val

    @property
    def total_str(self):
        val = self.str + self._get_base_bonus("str")
        for eq in self.equipment.values():
            if eq: val += eq.get("str", 0)
        return val

    @property
    def total_agi(self):
        val = self.agi + self._get_base_bonus("agi")
        for eq in self.equipment.values():
            if eq: val += eq.get("agi", 0)
        return val

    @property
    def total_int(self):
        val = self.int + self._get_base_bonus("int")
        for eq in self.equipment.values():
            if eq: val += eq.get("int", 0)
        return val

    @property
    def total_con(self):
        val = self.con + self._get_base_bonus("con")
        for eq in self.equipment.values():
            if eq: val += eq.get("con", 0)
        return val

    @property
    def total_per(self):
        val = self.per + self._get_base_bonus("per")
        for eq in self.equipment.values():
            if eq: val += eq.get("per", 0)
        return val

    @property
    def total_cha(self):
        val = self.cha + self._get_base_bonus("cha")
        for eq in self.equipment.values():
            if eq: val += eq.get("cha", 0)
        return val

    def update_stats(self):
        """更新衍生属性"""
        # 防止超高等级引发整数溢出或负数防御
        self.con = max(1, self.con)
        self.int = max(1, self.int)

        # 生命值 = 体质×10 + 等级×5
        self.max_hp = max(1, self.total_con * 10 + self.level * 5)
        # 精神力 = 智力×8 + 等级×3
        self.max_mp = max(1, self.total_int * 8 + self.level * 3)
        
        # 防止当前HP/MP超过上限
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        if self.mp > self.max_mp:
            self.mp = self.max_mp

        # 确保血量不会为负数但又是活着的bug状态
        self.hp = max(0, self.hp)
        self.mp = max(0, self.mp)

    def next_level_exp(self):
        return 100 * (self.level ** 2)

    def gain_exp(self, amount):
        from utils.display import print_success, print_info
        import time
        self.exp += amount
        print_info(f"获得经验值: +{amount} (当前进度: {self.exp}/{self.next_level_exp()})")
        
        while self.exp >= self.next_level_exp():
            self.exp -= self.next_level_exp()
            self.level += 1
            self.free_stats += 5
            self.update_stats()
            # 升级恢复全状态
            self.hp = self.max_hp
            self.mp = self.max_mp
            print_success(f"🌟 升级啦！当前等级: Lv.{self.level}")
            print_success("获得了 5 点自由属性点，可以在强化大厅使用！状态已全部恢复。")
            time.sleep(1)

    @property
    def carry_weight(self):
        # 负重 = 力量×5
        return self.total_str * 5
        
    @property
    def crit_rate(self):
        # 暴击率 = 敏捷×0.5%
        return self.total_agi * 0.005
        
    @property
    def dodge_rate(self):
        # 闪避率 = 敏捷×0.3%
        base = self.total_agi * 0.003
        if any(s.get("effect") == "dodge_up" for s in self.skills):
            base += 0.1
        return base
        
    @property
    def defense(self):
        # 防御力 = 体质×2 + 装备加成
        equip_def = 0
        if self.equipment["armor"]:
            equip_def = self.equipment["armor"].get("defense", 0)
        return self.total_con * 2 + equip_def

    @property
    def attack(self):
        # 攻击力跟力量相关，加上武器
        equip_atk = 0
        if self.equipment["weapon"]:
            equip_atk = self.equipment["weapon"].get("attack", 0)
        return self.total_str * 2 + equip_atk

    def take_damage(self, amount):
        actual_damage = max(1, amount - self.defense)
        self.hp -= actual_damage
        if self.hp < 0:
            self.hp = 0
        return actual_damage

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def restore_mp(self, amount):
        self.mp += amount
        if self.mp > self.max_mp:
            self.mp = self.max_mp

    def is_alive(self):
        return self.hp > 0

    def add_status(self, effect_name, duration, power):
        # Prevent duplicate status stacking, just refresh duration
        for s in self.status:
            if s["name"] == effect_name:
                s["duration"] = max(s["duration"], duration)
                s["power"] = max(s["power"], power)
                return
        self.status.append({"name": effect_name, "duration": duration, "power": power})

    def process_status(self):
        active_status = []
        for s in self.status:
            s["duration"] -= 1
            if s["duration"] > 0:
                active_status.append(s)
        self.status = active_status
        
    def check_achievements(self):
        from classes.achievement import AchievementSystem
        ach_sys = AchievementSystem(self)
        ach_sys.check_achievements()

    def show_status(self):
        """返回状态字符串"""
        from utils.display import draw_progress_bar, Fore
        hp_bar = draw_progress_bar(self.hp, self.max_hp, color=Fore.GREEN)
        mp_bar = draw_progress_bar(self.mp, self.max_mp, color=Fore.BLUE)
        
        bl_name = self.bloodline["name"] + f" ({self.bloodline.get('level', '')})" if getattr(self, 'bloodline', None) else "无"
        cu_name = self.cultivation["name"] + f" ({self.cultivation.get('level', '')})" if getattr(self, 'cultivation', None) else "无"
        pet_name = self.active_pet["name"] if getattr(self, 'active_pet', None) else "无"
        
        status_lines = [
            f"--- 轮回者: {self.name} | Lv.{self.level} | 积分: {self.points} | 道德: {self.morality} ---",
            f"[血统体系]: {bl_name}   |   [修真功法]: {cu_name}   |   [出战宠物]: {pet_name}",
            f"生命值: {hp_bar}  精神力: {mp_bar}",
            f"力量(STR): {self.str}(+{self.total_str-self.str})  敏捷(AGI): {self.agi}(+{self.total_agi-self.agi})  智力(INT): {self.int}(+{self.total_int-self.int})",
            f"体质(CON): {self.con}(+{self.total_con-self.con})  感知(PER): {self.per}(+{self.total_per-self.per})  魅力(CHA): {self.cha}(+{self.total_cha-self.cha})",
            f"攻击力: {self.attack}  防御力: {self.defense}",
            f"暴击率: {self.crit_rate*100:.1f}%  闪避率: {self.dodge_rate*100:.1f}%",
        ]
        return "\n".join(status_lines)
