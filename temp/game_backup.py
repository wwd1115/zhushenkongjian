import sys
import time
from utils.display import clear_screen, print_header, print_info, print_error, print_success, show_menu, get_input
from classes.player import Player
from classes.teammate import Teammate
from save.save_system import save_game_data, load_game_data
from scenes.main_god_space import MainGodSpace
from save.leaderboard import LeaderboardSystem

class Game:
    def __init__(self):
        self.player = None
        self.is_running = True
        self.god_space = MainGodSpace(self)
        self.leaderboard = LeaderboardSystem()

    def start(self):
        clear_screen()
        print_header("主神空间 - 无限轮回")
        print_info("欢迎来到主神空间...")
        time.sleep(1)

        while self.is_running:
            if not self.player:
                self.main_menu()
            else:
                self.god_space_menu()
                if self.player and not self.player.is_alive():
                    self.handle_player_death()

    def main_menu(self):
        clear_screen()
        options = {
            "1": "开始新游戏",
            "2": "读取存档",
            "3": "退出游戏"
        }
        choice = show_menu("主菜单", options)

        if choice == "1":
            self.create_character()
        elif choice == "2":
            self.load_game()
        elif choice == "3":
            self.exit_game()

    def create_character(self):
        clear_screen()
        print_header("轮回殿 - 灵魂重铸")
        from save.meta_save import MetaSaveSystem
        from utils.display import get_text_input

        meta = MetaSaveSystem()
        bonus_stats = 0
        bonus_points = 0

        if meta.marks > 0:
            while True:
                clear_screen()
                print_header(f"轮回殿 (当前拥有轮回印记: {meta.marks})")
                options = {
                    "1": "兑换 [综合强化] (+5点全属性) - 消耗 50 印记",
                    "2": "兑换 [资金支援] (+1000初始积分) - 消耗 30 印记",
                    "0": "跳过兑换，直接开始"
                }
                c = show_menu("你可以消耗上一世的积累换取开局优势", options)
                if c == "0":
                    break
                elif c == "1":
                    if meta.spend_marks(50):
                        bonus_stats += 5
                        print_success("兑换成功！开局全属性+5。")
                    else:
                        print_error("轮回印记不足！")
                elif c == "2":
                    if meta.spend_marks(30):
                        bonus_points += 1000
                        print_success("兑换成功！开局积分+1000。")
                    else:
                        print_error("轮回印记不足！")
                time.sleep(1.5)

        clear_screen()
        print_header("躯体塑造")
        name = get_text_input("请输入新轮回者的名字: ")
        if not name or name == "ENTER":
            name = "轮回者一号"
        self.player = Player(name)

        # Apply bonuses
        if bonus_stats > 0:
            self.player.str += bonus_stats
            self.player.agi += bonus_stats
            self.player.int += bonus_stats
            self.player.con += bonus_stats
            self.player.per += bonus_stats
            self.player.cha += bonus_stats
        if bonus_points > 0:
            self.player.points += bonus_points

        self.player.update_stats()
        self.player.hp = self.player.max_hp
        self.player.mp = self.player.max_mp

        # ====== Novice Grand Gift Box ======
        self.player.points += 3000
        print_success("【新手大礼包】主顾厚爱！你获得了 3000 点初始极品积分！")

        # Give a random Rare/Epic weapon
        from utils.equipment_gen import generate_equipment
        import random
        q = "稀有" if random.random() < 0.8 else "史诗"
        starter_weapon = generate_equipment(self.player.level, specific_quality=q)
        starter_weapon["name"] = f"新手赐福·{starter_weapon['name']}"
        self.player.inventory.append(starter_weapon)
        print_success(f"【新手大礼包】你获得了开局护身武器: {starter_weapon['name']}！")

        # Give a starter skill
        try:
            import json
            import os
            skill_path = os.path.join(os.path.dirname(__file__), 'data', 'skills.json')
            with open(skill_path, 'r', encoding='utf-8') as f:
                all_skills = json.load(f).get("skills", [])
            if all_skills:
                skill = random.choice(all_skills)
                self.player.skills.append(skill)
                print_success(f"【新手大礼包】醍醐灌顶！你提前领悟了强力技能: {skill['name']}！")
        except Exception as e:
            pass # fallback if not found

        print_success(f"躯体塑造完成！欢迎你，{self.player.name}。准备好迎接无限的世界吧！")
        time.sleep(3.0)

    def load_game(self):
        clear_screen()
        data = load_game_data()
        if not data:
            print_error("没有找到存档文件！")
            time.sleep(1.5)
            return

        self.player = Player(data.get("name", "轮回者"))
        self.player.level = data.get("level", 1)
        self.player.points = data.get("points", 1000)
        self.player.morality = data.get("morality", 0)
        self.player.str = data.get("str", 10)
        self.player.agi = data.get("agi", 10)
        self.player.int = data.get("int", 10)
        self.player.con = data.get("con", 10)
        self.player.per = data.get("per", 10)
        self.player.cha = data.get("cha", 10)
        self.player.free_stats = data.get("free_stats", 0)

        self.player.update_stats()

        self.player.hp = data.get("hp", self.player.max_hp)
        self.player.mp = data.get("mp", self.player.max_mp)
        self.player.inventory = data.get("inventory", [])
        self.player.equipment = data.get("equipment", {
            "weapon": None, "armor": None, "accessory": None
        })
        self.player.skills = data.get("skills", [])
        self.player.stats = data.get("stats", {"kills": 0, "deaths": 0, "points_spent": 0})
        self.player.achievements = data.get("achievements", [])

        teammates_data = data.get("teammates", [])
        self.player.teammates = [Teammate.from_dict(t) for t in teammates_data]

        print_success("读取存档成功！")
        time.sleep(1.5)

    def save_game(self):
        if not self.player:
            return
        if save_game_data(self.player):
            print_success("保存游戏成功！")
            # Update leaderboard
            score = self.player.stats.get("kills", 0) * 50 + self.player.stats.get("points_spent", 0) + self.player.points
            details = f"Lv.{self.player.level} | 成就:{len(self.player.achievements)}"
            self.leaderboard.update_record(self.player.name, score, details)
        else:
            print_error("保存游戏失败！")
        time.sleep(1.5)

    def exit_game(self):
        clear_screen()
        print_info("正在退出主神空间...")
        sys.exit(0)

    def god_space_menu(self):
        self.god_space.enter()

    def handle_player_death(self):
        from utils.display import clear_screen, print_header, print_error, print_info, get_input
        from save.meta_save import MetaSaveSystem
        from save.save_system import delete_save_data

        clear_screen()
        print_header("💀 意 识 消 散 💀")
        print_error(f"{self.player.name}，你在任务世界中倒下了...")
        print_info("按照主神空间的规则，失败者将被彻底抹杀，肉身与存在都将化为飞灰。")
        time.sleep(2)

        # 计算轮回印记
        marks_gained = self.player.stats.get("kills", 0) * 2 + self.player.level * 10
        print_success(f"虽然肉身消逝，但你在本次轮回中的挣扎化作了 {marks_gained} 点【轮回印记】！")

        # 记录到排行榜
        score = self.player.stats.get("kills", 0) * 50 + self.player.stats.get("points_spent", 0) + self.player.points
        details = f"Lv.{self.player.level} | 陨落"
        self.leaderboard.update_record(self.player.name, score, details)

        # 增加轮回印记
        meta = MetaSaveSystem()
        meta.add_marks(marks_gained)

        # 删档重启
        delete_save_data()
        self.player = None

        get_input("按回车键重新开始命运的轮回...")
