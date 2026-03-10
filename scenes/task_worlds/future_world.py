import time
import random
from utils.display import clear_screen, print_header, print_info, print_warning, print_error, print_success, show_menu, get_input
from classes.enemy import create_zombie
from utils.combat_calc import CombatSystem
import classes.enemy as enemy_gen
from classes.teammate import Teammate

class FutureWorld:
    def __init__(self, game, seed=None):
        self.game = game
        self.player = game.player
        self.rebel_rep = 0    # 叛军声望
        self.gov_rep = 0      # 政府军声望
        self.mission_completed = False
        
        # 种子系统
        if seed is None:
            self.seed = int(time.time() * 1000) % 1000000
        else:
            self.seed = seed
        random.seed(self.seed)
        
        # 特有机制: 环境危害等级
        self.hazard_level = 0


    def enter(self):
        clear_screen()
        print_header("未来战场 - 星际殖民地的叛乱")
        print_info(f"世界种子 (Seed): {self.seed}")
        print_info("背景：这里是拉格朗日殖民地，政府军正与叛乱势力进行残忍的火并。到处都是高科技武器。一旦卷入，无法回头。")
        print_info("任务目标：选择死忠一个阵营并帮助他们取得决战的胜利！")
        time.sleep(2)
        
        while self.player.is_alive() and not self.mission_completed:
            self.explore_step()
            
        if self.player.is_alive():
            clear_screen()
            print_success("你完成了未来战场的战役，准备回归！")
            get_input("按回车键继续回归主神空间...")
            
    def explore_step(self):
        clear_screen()
        print_header("战火纷飞的街道")
        print_info(f"生命: {self.player.hp}/{self.player.max_hp}  精神力: {self.player.mp}/{self.player.max_mp} | 环境危害(炮火频次): {self.hazard_level}%")
        print_info(f"当前声望 - 政府军: {self.gov_rep} | 叛军: {self.rebel_rep}")
        if self.player.teammates:
            for t in [x for x in self.player.teammates if x.is_alive()]:
                print_info(f"队友 {t.name} (HP: {t.hp}/{t.max_hp}) 紧随其后。")

        # 每回合基于危害等级可能受伤
        if self.hazard_level > 0 and random.randint(1, 100) < self.hazard_level:
            dmg = random.randint(30, 80)
            print_error(f"⚡ 警告！流弹击中了你，造成了 {dmg} 点环境伤害！")
            self.player.take_damage(dmg)
            time.sleep(1.5)
            if not self.player.is_alive():
                return
                
        options = {
            "1": "支援被困的政府军小队",
            "2": "协助叛军破坏能源网",
            "3": "潜入黑市 (可购买特殊临时道具)"
            # 移除了逃跑选项
        }
        
        # 终极战役触发
        if self.gov_rep >= 3 or self.rebel_rep >= 3:
            options["5"] = "⭐ 参加阵营决战 (最终任务) ⭐"
            
        choice = show_menu("接下来的行动", options)
        
        if choice == "1":
            self.assist_gov()
            self.hazard_level += random.randint(5, 15)
        elif choice == "2":
            self.assist_rebel()
            self.hazard_level += random.randint(5, 15)
        elif choice == "3":
            self.black_market()
        elif choice == "5" and (self.gov_rep >= 3 or self.rebel_rep >= 3):
            self.final_battle()

    def assist_gov(self):
        print_info("你前往了交火点，协助政府军平叛。")
        time.sleep(1)
        # 生成叛军敌人
        enemies = [enemy_gen.Enemy("叛军突击兵", 120, 40, 15, drop_points=100) for _ in range(2)]
        cs = CombatSystem(self.player, enemies)
        if cs.start_combat():
            print_success("你成功解救了政府军小队！(政府军声望+1)")
            self.gov_rep += 1
            time.sleep(1.5)

    def assist_rebel(self):
        print_info("你潜伏在暗处，试图破坏政府军的能源设施。")
        time.sleep(1)
        enemies = [enemy_gen.Enemy("政府安保机器人", 200, 30, 8, defense=15, drop_points=150)]
        cs = CombatSystem(self.player, enemies)
        if cs.start_combat():
            print_success("你成功瘫痪了能源设施！(叛军声望+1)")
            self.rebel_rep += 1
            time.sleep(1.5)

    def black_market(self):
        clear_screen()
        print_header("黑市商人")
        print_info(f"你有 {self.player.points} 积分可以使用。")
        opt = show_menu("你要买点什么？", {
            "1": "雇佣赏金猎人 (花费500积分)",
            "2": "注射纳米修复剂 (花费200积分)",
            "3": "购买微型偏导护盾 (花费300积分, 散去环境危害)",
            "0": "离开"
        })
        if opt == "1":
            if self.player.points >= 500:
                self.player.points -= 500
                new_t = Teammate("赏金猎人", hp=150, attack=45, defense=10, agi=20)
                self.player.teammates.append(new_t)
                print_success("赏金猎人加入了你的队伍！本场任务他会一直跟着你！")
            else:
                print_error("积分不足！")
            time.sleep(1.5)
        elif opt == "2":
            if self.player.points >= 200:
                self.player.points -= 200
                self.player.hp = self.player.max_hp
                print_success("生命值全满。")
            else:
                print_error("积分不足！")
            time.sleep(1.5)
        elif opt == "3":
            if self.player.points >= 300:
                self.player.points -= 300
                self.hazard_level = 0
                print_success("开启护盾，周围的流弹不再对你产生威胁！危害等级归零。")
            else:
                print_error("积分不足！")
            time.sleep(1.5)

    def final_battle(self):
        clear_screen()
        print_header("总攻战役")
        
        if self.gov_rep >= 3:
            print_warning("你协助政府军对叛军基地发起了总攻！")
            enemies = [
                enemy_gen.Enemy("叛军精锐", 180, 50, 15, drop_points=200),
                enemy_gen.Enemy("叛军精锐", 180, 50, 15, drop_points=200),
                enemy_gen.Enemy("叛军首领 (Boss)", 600, 80, 25, defense=20, drop_points=1500)
            ]
        else:
            print_warning("你跟随叛军杀入了政府军行政大楼！")
            enemies = [
                enemy_gen.Enemy("战争重机甲", 400, 60, 10, defense=30, drop_points=300),
                enemy_gen.Enemy("行政长官 (Boss)", 800, 100, 15, defense=15, drop_points=1500)
            ]
            
        time.sleep(2)
        cs = CombatSystem(self.player, enemies)
        if cs.start_combat():
            print_success("战役胜利！主线完美达成。(获得积分: 3000)")
            self.player.points += 3000
            time.sleep(2)
            self.mission_completed = True
