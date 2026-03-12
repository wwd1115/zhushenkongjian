import random

class Enemy:
    def __init__(self, name, hp, attack, speed, special_ability=None, defense=0, drop_exp=0, drop_points=0):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.speed = speed
        self.defense = defense
        self.special_ability = special_ability
        self.drop_exp = drop_exp
        self.drop_points = drop_points
        self.status = []

    def take_damage(self, amount):
        actual_damage = max(1, amount - self.defense)
        self.hp -= actual_damage
        if self.hp < 0:
            self.hp = 0
        return actual_damage

    def is_alive(self):
        return self.hp > 0

# 预设敌人工厂
def create_zombie(enemy_type="normal"):
    if enemy_type == "normal":
        return Enemy("普通丧尸", hp=80, attack=15, speed=5, drop_exp=20, drop_points=50)
    elif enemy_type == "fast":
        return Enemy("迅捷丧尸", hp=50, attack=20, speed=15, drop_exp=30, drop_points=80)
    elif enemy_type == "mutant":
        return Enemy("变异体", hp=300, attack=40, speed=8, special_ability="喷毒", defense=5, drop_exp=100, drop_points=200)
    elif enemy_type == "dog":
        return Enemy("丧尸犬", hp=100, attack=25, speed=12, drop_exp=40, drop_points=100)
    elif enemy_type == "mummy":
        return Enemy("复活的木乃伊", hp=150, attack=25, speed=3, defense=10, special_ability="毒素", drop_exp=40, drop_points=80)
    elif enemy_type == "scarab":
        return Enemy("圣甲虫群", hp=60, attack=15, speed=15, special_ability="虫群", drop_exp=20, drop_points=40)
    elif enemy_type == "robber":
        return Enemy("持枪盗墓贼", hp=100, attack=35, speed=10, drop_exp=30, drop_points=60)
    elif enemy_type == "elite_robber":
        return Enemy("盗墓团伙头目", hp=250, attack=50, speed=12, defense=15, drop_exp=100, drop_points=200)
    elif enemy_type == "pharaoh":
        return Enemy("法老王虚影 (Boss)", hp=500, attack=60, speed=20, defense=20, special_ability="诅咒", drop_exp=300, drop_points=1000)
    else:
        return Enemy("未知生物", hp=50, attack=10, speed=5, drop_exp=10, drop_points=20)

def create_fantasy_enemy(enemy_type="goblin"):
    if enemy_type == "goblin":
        return Enemy("哥布林掠夺者", hp=40, attack=15, speed=25, drop_exp=15, drop_points=30)
    elif enemy_type == "orc_warrior":
        return Enemy("兽人狂战士", hp=150, attack=35, speed=10, defense=10, drop_exp=60, drop_points=120)
    elif enemy_type == "dragon_cub":
        return Enemy("烈焰幼龙", hp=400, attack=70, speed=30, defense=30, special_ability="火焰吐息", drop_exp=200, drop_points=500)
    else:
        return Enemy("魔物", hp=50, attack=15, speed=10, drop_exp=10, drop_points=20)

def create_cyber_enemy(enemy_type="drone"):
    if enemy_type == "drone":
        return Enemy("安保无人机", hp=60, attack=20, speed=35, drop_exp=25, drop_points=40)
    elif enemy_type == "cyborg_ninja":
        return Enemy("赛博忍者", hp=200, attack=60, speed=45, defense=15, special_ability="高频刃", drop_exp=80, drop_points=150)
    elif enemy_type == "mech_boss":
        return Enemy("重装机甲 (Boss)", hp=800, attack=120, speed=15, defense=50, special_ability="等离子炮", drop_exp=400, drop_points=800)
    else:
        return Enemy("故障机器人", hp=50, attack=15, speed=10, drop_exp=10, drop_points=20)
