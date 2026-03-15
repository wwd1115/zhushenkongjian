import json
import os
import time
from utils.display import print_success

class AchievementSystem:
    def __init__(self, player):
        self.player = player
        self.achievements_data = self.load_achievements()

    def load_achievements(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        try:
            with open(os.path.join(base_dir, "data", "achievements.json"), "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def check_achievements(self):
        new_unlocks = []
        for key, ach in self.achievements_data.items():
            if key in self.player.achievements:
                continue
                
            unlocked = False
            req = ach.get("req", {})

            # Use 'if-elif' structurally or check all conditions independently to avoid logical overwrites
            # Actually, since these are discrete achievements, checking independent requirements per achievement is better.
            if "kills" in req and self.player.stats.get("kills", 0) >= req["kills"]:
                unlocked = True
            elif "deaths" in req and self.player.stats.get("deaths", 0) >= req["deaths"]:
                unlocked = True
            elif "points_spent" in req and self.player.stats.get("points_spent", 0) >= req["points_spent"]:
                unlocked = True
            elif "morality_high" in req and self.player.morality >= req["morality_high"]:
                unlocked = True
            elif "morality_low" in req and self.player.morality <= req["morality_low"]:
                unlocked = True

            if unlocked:
                self.player.achievements.append(key)
                new_unlocks.append(ach)
                if "reward_points" in ach:
                    self.player.points += ach["reward_points"]
                
        for ach in new_unlocks:
            msg = f"🏆 解锁史诗成就: 【{ach['name']}】 - {ach['desc']} (奖励: {ach.get('reward_points', 0)} 积分) 🏆"
            print_success(msg)

            from utils.display import GUI_INSTANCE
            if GUI_INSTANCE:
                GUI_INSTANCE.gui_print("\n" + "="*40, "yellow")
                GUI_INSTANCE.gui_print(msg, "yellow")
                GUI_INSTANCE.gui_print("="*40 + "\n", "yellow")
            time.sleep(1.5)
