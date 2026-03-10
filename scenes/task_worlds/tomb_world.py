import time
import random
from utils.display import clear_screen, print_header, print_info, print_warning, print_error, print_success, show_menu, get_input
from classes.enemy import create_zombie
from utils.combat_calc import CombatSystem
import classes.enemy as enemy_gen
from classes.teammate import Teammate

class TombWorld:
    def __init__(self, game, seed=None):
        self.game = game
        self.player = game.player
        self.progress = 0  # 探索进度 0~100
        
        # 种子系统
        if seed is None:
            self.seed = int(time.time() * 1000) % 1000000
        else:
            self.seed = seed
        random.seed(self.seed)
        
        self.has_staff = False
        self.met_archaeologist = False
        
        # 特有机制: 毒气诅咒 (随进度按比例增加，扣减最大生命值上限的比例)
        self.curse_level = 0


    def enter(self):
        clear_screen()
        print_header("古墓迷踪 - 神秘的埃及")
        print_info(f"世界种子 (Seed): {self.seed}")
        print_info("背景：探索金字塔深处，寻找被历史遗忘的法老权杖。无法中途退出！")
        print_info("主线任务：探索度达到100%并击倒守卫者！")
        print_warning("提示：这里布满古老机关，且文物常常带着恶毒的诅咒(最高诅咒100%，会每回合削减生命上限)。")
        time.sleep(2)
        
        while self.player.is_alive() and self.progress < 100:
            self.explore_step()
            
        if self.player.is_alive():
            clear_screen()
            print_success("你已成功完成了古墓的探索！根据你的表现开始结算...")
            if self.has_staff:
                print_success("获取法老权杖！主线完美达成。(积分+2000)")
                self.player.points += 2000
            else:
                print_warning("虽然或者回来了，但是并没找到法老权杖。(积分+500)")
                self.player.points += 500
            get_input("按回车键继续回归主神空间...")
            
    def explore_step(self):
        clear_screen()
        print_header(f"探索进度: {self.progress}% | 诅咒程度: {self.curse_level}%")
        
        # 诅咒判定 (临时最大HP减少)
        curse_penalty = int(self.player.max_hp * (self.curse_level / 100.0))
        effective_max_hp = max(1, self.player.max_hp - curse_penalty)
        if self.player.hp > effective_max_hp:
            self.player.hp = effective_max_hp
            
        print_info(f"生命: {self.player.hp}/{effective_max_hp}  精神力: {self.player.mp}/{self.player.max_mp}")
        if self.player.teammates:
            for t in [x for x in self.player.teammates if x.is_alive()]:
                print_info(f"队友 {t.name} (HP: {t.hp}/{t.max_hp}) 紧随其后。")

        options = {
            "1": "谨慎前进 (进度+5%，大概率发现陷阱)",
            "2": "快速搜寻 (进度+15%，极易遭遇战和诅咒增加)",
            "3": f"研读墙壁上的象形文字 (需要智力智力>= {random.randint(10, 20)})"
        }
        
        choice = show_menu("接下来的行动", options)
        
        if choice == "1":
            self.progress += 5
            self.handle_event(risk_level="low")
        elif choice == "2":
            self.progress += 15
            self.handle_event(risk_level="high")
        elif choice == "3":
            # 动态智力检定
            req_int = random.randint(12, 22)
            if self.player.int >= req_int:
                print_success(f"凭借你的高智力({self.player.int} >= {req_int})，你成功解开了墙壁的暗门的秘密！")
                print_info("你发现了一条捷径。进度+20%，并且精神力恢复了30点，驱散了部分诅咒！")
                self.progress += 20
                self.player.restore_mp(30)
                self.curse_level = max(0, self.curse_level - 10)
                time.sleep(2)
            else:
                print_error(f"这些文字对你来说像天书 (需智力 {req_int})，你看得头皮发麻。扣除10点精神力，诅咒加剧！")
                self.player.mp = max(0, self.player.mp - 10)
                self.curse_level += 5
                time.sleep(1.5)

        if self.progress >= 90 and not self.has_staff and self.progress < 100:
            self.boss_fight()

    def handle_event(self, risk_level):
        print_info("你在黑暗的古墓中摸索着...")
        time.sleep(1)
        r = random.random()
        encounter_chance = 0.3 if risk_level == "low" else 0.7
        trap_chance = 0.2 if risk_level == "low" else 0.5
        
        # 考古队剧情
        if not self.met_archaeologist and r < 0.15:
            self.met_archaeologist = True
            print_success("你遇到了一个被困的考古队员！")
            opt = show_menu("是否带上他？", {"1": "带上他 (加入队伍)", "2": "冷酷拒绝"})
            if opt == "1":
                new_teammate = Teammate("考古队员", hp=80, attack=10, defense=5, agi=12)
                self.player.teammates.append(new_teammate)
                print_success("考古队员加入了你的队伍，他对古墓的了解可能会有帮助。")
                time.sleep(1.5)
            return

        # 陷阱事件
        if random.random() < trap_chance:
            print_warning("⚡ 你触发了机关陷阱！(毒箭/诅咒迷雾) ⚡")
            time.sleep(1)
            # 敏捷判定闪避
            if self.player.agi + random.randint(1, 10) > 20: # 敏捷+D10 判定
                print_success("你的身手异常敏捷，一个翻滚躲开了所有机关！")
            else:
                dmg = random.randint(20, 50)
                if risk_level == "high": 
                    dmg *= 2
                    self.curse_level += 15
                    print_error("你吸入了大量诅咒迷雾，诅咒程度暴增！")
                else:
                    self.curse_level += 5
                print_error(f"你未能完全躲开，被机关弄伤，扣减了 {dmg} 点生命值！")
                self.player.take_damage(dmg)
            time.sleep(1.5)
            if not self.player.is_alive(): return
        
        # 遭遇战 (木乃伊/圣甲虫/盗墓贼)
        if random.random() < encounter_chance:
            enemy_pool = ["mummy", "mummy", "scarab", "robber"]
            num_enemies = random.randint(1, 3) if risk_level == "high" else random.randint(1, 2)
            enemies = [enemy_gen.create_zombie(random.choice(enemy_pool)) for _ in range(num_enemies)]
            
            cs = CombatSystem(self.player, enemies)
            cs.start_combat()
            if self.player.is_alive():
                print_info("你搜刮了下怪物/尸体，找到了一些积分。")
                time.sleep(1.5)

    def boss_fight(self):
        clear_screen()
        print_header("墓室的核心")
        print_warning("你终于来到了法老的停尸间。祭台的中央悬浮着那柄散发着不详金光的权杖。")
        print_error("就在你伸手去拿的瞬间，法老的石棺爆裂了！")
        time.sleep(2)
        
        boss = enemy_gen.create_zombie("pharaoh")
        # 盗墓团伙也会来插一脚
        elite = enemy_gen.create_zombie("elite_robber")
        enemies = [boss, elite]
        
        cs = CombatSystem(self.player, enemies)
        won = cs.start_combat()
        
        if won:
            self.has_staff = True
            print_success("你击败了法老王虚影以及妄图渔翁得利的盗墓贼，将法老权杖收入囊中！")
            time.sleep(2)
            self.progress = 100
