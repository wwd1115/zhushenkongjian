import json
import os

SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "save")
SAVE_FILE = os.path.join(SAVE_DIR, "save_data.json")

def ensure_save_dir():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

def save_game_data(player):
    ensure_save_dir()
    data = {
        "name": player.name,
        "level": player.level,
        "points": player.points,
        "morality": player.morality,
        "str": player.str,
        "agi": player.agi,
        "int": player.int,
        "con": player.con,
        "per": player.per,
        "cha": player.cha,
        "free_stats": player.free_stats,
        "hp": player.hp,
        "mp": player.mp,
        "inventory": player.inventory,
        "equipment": player.equipment,
        "skills": player.skills,
        "stats": player.stats,
        "achievements": player.achievements,
        "teammates": [t.to_dict() for t in player.teammates],
        "pets": getattr(player, "pets", []),
        "active_pet": getattr(player, "active_pet", None),
        "status": getattr(player, "status", [])
    }
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return True

def load_game_data():
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception:
        return None

def delete_save_data():
    if os.path.exists(SAVE_FILE):
        try:
            os.remove(SAVE_FILE)
            return True
        except:
            return False
    return True

