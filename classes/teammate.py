import random

class Teammate:
    def __init__(self, name, hp, attack, defense, agi):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.agi = agi  # 影响闪避等
        self.skills = []
        self.is_defending = False

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

    def is_alive(self):
        return self.hp > 0
        
    @property
    def dodge_rate(self):
        return self.agi * 0.003
        
    @property
    def crit_rate(self):
        return self.agi * 0.005

    def to_dict(self):
        return {
            "name": self.name,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "attack": self.attack,
            "defense": self.defense,
            "agi": self.agi
        }

    @classmethod
    def from_dict(cls, data):
        tm = cls(data["name"], data["max_hp"], data["attack"], data["defense"], data["agi"])
        tm.hp = data["hp"]
        return tm
