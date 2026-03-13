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
        self.status = []

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

    @property
    def dodge_rate(self):
        return self.agi * 0.003
        
    def add_status(self, effect_name, duration, power):
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

    def is_alive(self):
        return self.hp > 0

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

class PetActor:
    def __init__(self, pet_data, owner_level):
        self.name = pet_data["name"]
        self.base_hp = pet_data["hp"]
        self.max_hp = self.base_hp + (owner_level * 10)
        self.hp = self.max_hp
        self.attack = pet_data["attack"] + (owner_level * 5)
        self.speed = pet_data["speed"] + owner_level
        self.defense = pet_data["defense"] + (owner_level * 2)
        self.skill = pet_data.get("skill", "attack")
        self.actor_id = "pet_0"
        self.is_defending = False
        self.status = []

    def add_status(self, effect_name, duration, power):
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

    def take_damage(self, amount):
        actual_damage = max(1, amount - self.defense)
        self.hp -= actual_damage
        if self.hp < 0:
            self.hp = 0
        return actual_damage

    def is_alive(self):
        return self.hp > 0

    @property
    def crit_rate(self):
        return self.speed * 0.005
