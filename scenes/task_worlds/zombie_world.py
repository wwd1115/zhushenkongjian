import time
import random
from utils.display import clear_screen, print_header, print_info, print_warning, print_error, print_success, show_menu, get_input
from classes.enemy import create_zombie
from utils.combat_calc import CombatSystem

class ZombieWorld:
    def __init__(self, game, seed=None):
        self.game = game
        self.player = game.player
        self.days_survived = 0
        
        # 机制：种子与随机化
        if seed is None:
            self.seed = int(time.time() * 1000) % 1000000
        else:
            self.seed = seed
        random.seed(self.seed)
        
        # 任务目标生成
        self.objective_type = random.choice([
            "survival", # 存活7天
            "cure",     # 寻找解药
            "boss"      # 击杀变异源头
        ])
        
        self.scientist_rescued = False
        self.cure_found = False
        self.boss_killed = False
        
        # 特有机制
        self.infection_level = 0 # 0-100, 过高变异死亡


    def enter(self):
        clear_screen()
        print_header("T病毒爆发 - 废土之旅")
        print_info(f"世界种子 (Seed): {self.seed}")
        print_info("背景：城市沦为废墟，到处都是游荡的丧尸。必须完成目标才能离开！")
        
        if self.objective_type == "survival":
            print_warning("【主线任务】：存活 10 天")
            target_days = 10
        elif self.objective_type == "cure":
            print_warning("【主线任务】：在医院深处找到废土解药资料")
            target_days = 999
        else:
            print_warning("【主线任务】：击杀游荡在超市附近的变异源头(Boss)")
            target_days = 999
            
        time.sleep(2)
        
        while self.player.is_alive():
            # 检查特有机制死亡
            if self.infection_level >= 100:
                print_error("你体内的病毒彻底爆发了...你变成了丧尸！")
                self.player.hp = 0
                break
                
            # 检查任务是否完成
            if self.objective_type == "survival" and self.days_survived >= target_days:
                print_success("存活任务完成，主神降下光柱将你接回！")
                break
            elif self.objective_type == "cure" and self.cure_found:
                print_success("解药已找到，主神降下光柱将你接回！")
                break
            elif self.objective_type == "boss" and self.boss_killed:
                print_success("变异源头已被消灭，主神降下光柱将你接回！")
                break
                
            self.explore_day()
            
            if not self.player.is_alive():
                break
                
        if self.player.is_alive():
            clear_screen()
            print_success("恭喜完成任务，安全回归！(奖励积分: 2000)")
            self.player.points += 2000
            self.player.stats["points_spent"] += 0 # trigger achievements etc later
            get_input("按回车键继续...")
            
    def explore_day(self):
        clear_screen()
        print_header(f"第 {self.days_survived + 1} 天 | 感染度: {self.infection_level}%")
        options = {
            "1": "探索废弃超市 (物资丰富，丧尸密集)",
            "2": "探索医院 (可能有解药资料，变异丧尸出没)",
            "3": "寻找营地休息 (恢复少许HP/MP，低概率遭遇战)"
            #移除了逃跑选项
        }
        
        choice = show_menu("选择你要前往的地点", options)
        
        if choice == "1":
            self.explore_supermarket()
        elif choice == "2":
            self.explore_hospital()
        elif choice == "3":
            self.rest()
            
        if self.player.is_alive():
            self.days_survived += 1
            # 每天自然增加感染度 2-5点 (体质越高增加越少)
            inf_gain = max(0, random.randint(2, 5) - (self.player.con // 20))
            if inf_gain > 0:
                self.infection_level += inf_gain
                print_warning(f"由于空气中的微粒，你的感染度上升了 {inf_gain}%。")
                time.sleep(1)

    def explore_supermarket(self):
        print_info("你进入了废弃超市...")
        time.sleep(1)
        
        if self.objective_type == "boss" and not self.boss_killed and random.random() < 0.3:
            print_error("超市深处传来咆哮！你遭遇了变异源头 Boss！")
            time.sleep(1)
            enemies = [create_zombie("mutant"), create_zombie("mutant")]
            enemies[0]["name"] = "巨型处刑者 (Boss)"
            enemies[0]["hp"] = 300
            enemies[0]["max_hp"] = 300
            enemies[0]["attack"] += 20
            
            cs = CombatSystem(self.player, enemies)
            won = cs.start_combat()
            if won:
                self.boss_killed = True
                print_success("你击杀了变异源头！！感染度下降 30%。")
                self.infection_level = max(0, self.infection_level - 30)
                time.sleep(2)
            else:
                self.infection_level += 20 # 被打死或重伤极大增加感染度
            return

        if random.random() < 0.7:
            # 遭遇战
            num_zombies = random.randint(1, 4)
            enemies = [create_zombie(random.choice(["normal", "fast"])) for _ in range(num_zombies)]
            cs = CombatSystem(self.player, enemies)
            won = cs.start_combat()
            if won:
                print_success("你在超市里找到了一批抗生素和物资包！(积分+150, 感染度-5%)")
                self.player.points += 150
                self.infection_level = max(0, self.infection_level - 5)
                time.sleep(1.5)
            else:
                 self.infection_level += 10 # 战败增高感染
        else:
            print_success("运气不错，躲过了丧尸，找到了纯净水和食物！生命恢复30点，感染度-2%。")
            self.player.heal(30)
            self.infection_level = max(0, self.infection_level - 2)
            time.sleep(1.5)

    def explore_hospital(self):
        print_info("你小心翼翼地进入医院...")
        time.sleep(1)
        if self.objective_type == "cure" and not self.cure_found and random.random() < 0.4:
            print_warning("遭遇变异体守卫！")
            time.sleep(1)
            enemies = [create_zombie("mutant")]
            cs = CombatSystem(self.player, enemies)
            won = cs.start_combat()
            if won:
                self.cure_found = True
                print_success("你找到了解药资料以及一大批医用血清！感染度清零！(获得积分: 1000)")
                self.infection_level = 0
                self.player.points += 1000
                time.sleep(2)
            else:
                 self.infection_level += 15
        else:
            num_zombies = random.randint(2, 5)
            print_warning("你惊动了医院的丧尸群！")
            time.sleep(1)
            enemies = [create_zombie(random.choice(["normal", "fast", "mutant"])) for _ in range(num_zombies)]
            cs = CombatSystem(self.player, enemies)
            won = cs.start_combat()
            if won:
                print_success("搜刮了几个药箱。生命恢复 20点。")
                self.player.heal(20)
                time.sleep(1)
            else:
                 self.infection_level += 10

    def rest(self):
        print_info("你找到了一个相对安全的地下室休息...")
        time.sleep(1)
        if random.random() < 0.2:
            print_error("你在睡梦中被丧尸犬袭击！")
            time.sleep(1)
            enemies = [create_zombie("dog")]
            cs = CombatSystem(self.player, enemies)
            cs.start_combat()
        else:
            self.player.heal(50)
            self.player.restore_mp(30)
            print_success("一夜无事，你恢复了50点生命和30点精神。")
            time.sleep(1.5)
