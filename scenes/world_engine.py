import random
import time
from utils.display import clear_screen, print_header, print_info, print_warning, print_error, print_success, show_menu, get_input
from utils.combat_calc import CombatSystem
import classes.enemy as enemy_gen

class WorldTemplate:
    def __init__(self, name_prefixes, desc_template, terrains, enemy_pool, quest_pool, event_pool, env_effects):
        self.name_prefixes = name_prefixes
        self.desc_template = desc_template
        self.terrains = terrains
        self.enemy_pool = enemy_pool
        self.quest_pool = quest_pool
        self.event_pool = event_pool
        self.env_effects = env_effects

class ProceduralWorld:
    def __init__(self, game, template, player_level, seed=None):
        self.game = game
        self.player = game.player
        self.template = template
        self.player_level = player_level
        
        # 种子设定
        if seed is None:
            self.seed = int(time.time() * 1000) % 1000000
        else:
            self.seed = seed
        self.rng = random.Random(self.seed)
        
        # 动态难度计算
        if player_level <= 1:
            self.base_difficulty = 0.6  # 严格限制新手关卡难度
        else:
            self.base_difficulty = max(0.5, (player_level * 0.8) + self.rng.uniform(0.5, 1.5))
        
        # 世界属性提取
        prefix = self.rng.choice(self.template.name_prefixes)
        suffix = self.rng.choice(["世界", "领域", "废墟", "秘境", "空间"])
        self.name = f"{prefix} {suffix}"
        
        # 随机抽取 2 个地形作为主要区域
        self.active_terrains = self.rng.sample(self.template.terrains, min(2, len(self.template.terrains)))
        
        # 随机任务目标
        quest_proto = self.rng.choice(self.template.quest_pool)
        self.quest = {
            "type": quest_proto["type"],
            "desc": quest_proto["desc"], # ex: "消灭所有敌人", "生存{days}天"
            "target_value": int(quest_proto["base_value"] * self.base_difficulty),
            "current_value": 0
        }
        
        # 格式化描述
        self.description = self.template.desc_template.replace("[地形1]", self.active_terrains[0]).replace("[环境]", self.rng.choice(self.template.env_effects))
        
        self.mission_completed = False
        self.total_enemies_killed_here = 0
        self.total_exploration_steps = 0

    def get_scaled_enemies(self, count=1, is_boss=False):
        enemies = []
        import classes.enemy as enemy_gen
        pool = self.template.enemy_pool
        
        for _ in range(count):
            if is_boss:
                base_e = pool[-1]
            else:
                # Level 1-2 only see the first 2 enemies in the pool
                cap = min(len(pool) - 1, max(2, (self.player_level // 3) + 2))
                base_e = self.rng.choice(pool[:cap])
                
            name = f"首领·{base_e['name']}" if is_boss else base_e["name"]
            
            # 乘以动态难度系数
            boss_mult = 2.0 if is_boss else 1.0
            if self.player_level <= 1 and is_boss:
                boss_mult = 1.2 # 新手期的 Boss 不能有2倍属性膨胀

            mult = self.base_difficulty * boss_mult

            hp = int(base_e["hp"] * mult)
            # 新手血量强制保护机制：防止出现700血怪物
            if self.player_level <= 1 and hp > 150:
                hp = 150

            atk = int(base_e["attack"] * mult)
            agi = int(base_e["agi"] * mult)
            df = int(base_e.get("defense", 0) * mult)
            drop = int(base_e.get("drop_points", 50) * mult)
            
            enemies.append(enemy_gen.Enemy(name, hp, atk, agi, defense=df, drop_points=drop))
        return enemies

    def enter(self):
        import utils.display as disp
        if not disp.GUI_INSTANCE:
            disp.print_error("视觉世界引擎只能在 GUI 模式下运行！")
            time.sleep(1.5)
            self.mission_completed = True
            return
            
        disp.clear_screen()
        print_header(f"🌀 {self.name} (Seed: {self.seed}) 难度系数: {self.base_difficulty:.1f}")
        print_info(self.description)
        
        q_desc = self.quest["desc"].replace("{target}", str(self.quest["target_value"]))
        print_warning(f"【主线任务】: {q_desc}")
        time.sleep(2)
        
        # Generate 2D Map
        self.generate_map()
        disp.GUI_INSTANCE.gui_start_map_exploration(self.map_data, self.player_x, self.player_y)
        disp.GUI_INSTANCE.gui_update_status(f"探索 {self.name} | 任务: {q_desc}")
        
        while self.player.is_alive() and not self.mission_completed:
            response = disp.GUI_INSTANCE.gui_get_input({"0": "尝试撤离 (需回到起点)"}, is_map=True)
            if response == "0":
                if self.map_data[self.player_y][self.player_x].get("type") == "start":
                    confirm = get_input("确认要强行撤离吗？放弃任务将无法获得结算奖励。(Y/n): ")
                    if confirm.lower() == 'y' or confirm == '':
                        break
                else:
                    disp.GUI_INSTANCE.gui_update_status("必须回到起点 (绿格) 才能撤离！")
            elif isinstance(response, dict) and response.get("action") == "move":
                cx = response.get("x")
                cy = response.get("y")
                self.handle_movement(cx, cy)
                
        disp.GUI_INSTANCE.gui_end_map_exploration()
            
        if self.player.is_alive():
            clear_screen()
            print_success(f"任务完成！回归主神空间！")
            
            # 结算经验
            exp_reward = int(self.base_difficulty * 100) + (self.total_enemies_killed_here * 50) + (self.total_exploration_steps * 20)
            if self.quest["type"] == "boss":
                exp_reward += 500
                
            self.player.gain_exp(exp_reward)
            get_input("按回车键继续回归...")
            
    def generate_map(self):
        # 10x10 map size
        self.rows = 10
        self.cols = 10
        self.map_data = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        
        # Room types: start, empty, enemy, event, treasure, boss
        
        # Random Walk Gen
        curr_x = self.rng.randint(2, 7)
        curr_y = self.rng.randint(2, 7)
        self.player_x = curr_x
        self.player_y = curr_y
        
        self.map_data[curr_y][curr_x] = {"type": "start", "visited": True, "cleared": True}
        
        num_rooms = self.rng.randint(20, 30)
        max_dist = 0
        boss_pos = (curr_x, curr_y)
        
        for _ in range(num_rooms):
            dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            self.rng.shuffle(dirs)
            for dx, dy in dirs:
                nx = curr_x + dx
                ny = curr_y + dy
                if 0 <= nx < self.cols and 0 <= ny < self.rows:
                    if self.map_data[ny][nx] is None:
                        # Determine type
                        r = self.rng.random()
                        r_type = "empty"
                        if r < 0.4: r_type = "enemy"
                        elif r < 0.6: r_type = "event"
                        elif r < 0.7: r_type = "treasure"
                        
                        self.map_data[ny][nx] = {"type": r_type, "visited": False, "cleared": False}
                        curr_x, curr_y = nx, ny
                        
                        dist = abs(nx - self.player_x) + abs(ny - self.player_y)
                        if dist > max_dist:
                            max_dist = dist
                            boss_pos = (nx, ny)
                        break
                    else:
                        curr_x, curr_y = nx, ny
                        
        # Place Boss at furthest point
        bx, by = boss_pos
        if (bx, by) != (self.player_x, self.player_y):
            self.map_data[by][bx] = {"type": "boss", "visited": False, "cleared": False}

    def handle_movement(self, cx, cy):
        from utils.display import GUI_INSTANCE
        room = self.map_data[cy][cx]
        if not room: return
        
        # Move player visually first
        self.player_x = cx
        self.player_y = cy
        room["visited"] = True
        GUI_INSTANCE.gui_update_map_pos(cx, cy, self.map_data)
        
        self.total_exploration_steps += 1
        q_type = self.quest["type"]
        if q_type == "survive":
            self.quest["current_value"] += 1
            
        # Process Room
        if not room.get("cleared", False):
            if room["type"] == "enemy":
                # Ensure we return to map view before combat starts if we were in text view
                GUI_INSTANCE.gui_update_map_pos(self.player_x, self.player_y, self.map_data)
                GUI_INSTANCE.gui_update_status("遭遇敌人！")
                time.sleep(1)
                max_count = min(3, max(1, (self.player_level // 3) + 1))
                enemies = self.get_scaled_enemies(count=self.rng.randint(1, max_count))
                cs = CombatSystem(self.player, enemies)
                if cs.start_combat():
                    room["cleared"] = True
                    self.total_enemies_killed_here += len(enemies)
                    if q_type == "kill":
                        self.quest["current_value"] += len(enemies)
                    
                    from utils.equipment_gen import generate_equipment
                    for _ in enemies:
                        if self.rng.randint(1, 100) <= 25:
                            eq = generate_equipment(self.player_level)
                            print_success(f"战斗掉落: 获得了 {eq['name']}")
                            self.player.inventory.append(eq)
                            time.sleep(1)
            elif room["type"] == "treasure":
                pts = self.rng.randint(50, 200)
                GUI_INSTANCE.gui_update_status(f"发现宝箱！积分+{pts}")
                self.player.points += pts
                room["cleared"] = True
                from utils.equipment_gen import generate_equipment
                eq = generate_equipment(self.player_level + 1)
                GUI_INSTANCE.gui_print(f"💰 发现宝箱！\n积分 +{pts}\n从宝箱中开出了装备: 【{eq['name']}】!", "yellow")
                self.player.inventory.append(eq)
                # Force user to acknowledge the find in GUI
                GUI_INSTANCE.gui_get_input({"0": "收起战利品"}, is_event=True)
                
            elif room["type"] == "event":
                GUI_INSTANCE.gui_update_status("触发未知奇遇事件！")
                event_type = self.rng.choice(["shrine", "altar", "chest", "trap", "merchant", "nothing"])
                
                if event_type == "chest":
                    GUI_INSTANCE.gui_print("🎁 你发现了一个隐藏的奇遇宝箱！散发着诱人的光芒。", "cyan")
                    res = GUI_INSTANCE.gui_get_input({"1": "开启", "2": "无视并离开"}, is_event=True)
                    if res == "1":
                        if self.rng.random() < 0.2:
                            dmg = self.player.max_hp // 4
                            GUI_INSTANCE.gui_print(f"这是一个宝箱怪！你被咬了一口，损失 {dmg} HP！", "red")
                            self.player.take_damage(dmg)
                        else:
                            from utils.equipment_gen import generate_equipment
                            eq = generate_equipment(self.player_level + 3) # High tier loot
                            GUI_INSTANCE.gui_print(f"🎉 奇遇爆出极品装备：【{eq['name']}】！已放入背包。", "green")
                            self.player.inventory.append(eq)
                        room["cleared"] = True
                        GUI_INSTANCE.gui_get_input({"0": "继续"}, is_event=True)
                    else:
                        GUI_INSTANCE.gui_print("你小心翼翼地离开了。", "white")
                        room["cleared"] = True
                        
                elif event_type == "shrine":
                    GUI_INSTANCE.gui_print("👼 你发现了一座古老的神龛。", "cyan")
                    res = GUI_INSTANCE.gui_get_input({"1": "虔诚祈祷", "2": "暴力破坏获取能量", "3": "离开"}, is_event=True)
                    if res == "1":
                        heal = self.player.max_hp // 2
                        self.player.heal(heal)
                        GUI_INSTANCE.gui_print(f"🕊️ 圣光拂过，你的伤势恢复了，生命 +{heal}！", "green")
                    elif res == "2":
                        if self.rng.random() < 0.5:
                            pts = self.rng.randint(300, 800)
                            GUI_INSTANCE.gui_print(f"😈 神龛中涌出狂暴的能量，你吸收了它！积分+{pts}", "yellow")
                            self.player.points += pts
                        else:
                            dmg = self.player.max_hp // 3
                            GUI_INSTANCE.gui_print(f"💀 神明震怒！雷罚降临，你损失了 {dmg} 点生命值！", "red")
                            self.player.take_damage(dmg)
                    else:
                        GUI_INSTANCE.gui_print("你默默走开了。", "white")
                    room["cleared"] = True
                    GUI_INSTANCE.gui_get_input({"0": "继续"}, is_event=True)
                    
                elif event_type == "altar":
                    dmg = self.player.max_hp // 5
                    GUI_INSTANCE.gui_print(f"🩸 眼前是一个鲜血祭坛，祭祀需要大量生命力。", "magenta")
                    res = GUI_INSTANCE.gui_get_input({"1": f"割腕献祭 (扣除{dmg}HP换取积分)", "2": "拒绝邪恶, 直接离开"}, is_event=True)
                    if res == "1":
                        self.player.take_damage(dmg)
                        if self.player.is_alive():
                            pts = self.rng.randint(200, 500)
                            self.player.points += pts
                            GUI_INSTANCE.gui_print(f"🩸 献祭成功！你的血液化为 {pts} 积分！", "yellow")
                        else:
                            GUI_INSTANCE.gui_print("🩸 你的生命力不足以支撑献祭，你死在了祭坛上！", "red")
                    else:
                        GUI_INSTANCE.gui_print("你厌恶地离开了祭坛。", "white")
                    room["cleared"] = True
                    if self.player.is_alive():
                        GUI_INSTANCE.gui_get_input({"0": "继续"}, is_event=True)
                elif event_type == "trap":
                    dmg = self.player.max_hp // 8
                    self.player.take_damage(dmg)
                    GUI_INSTANCE.gui_print(f"⚠️ 糟糕，你误入了古代陷阱！受到了 {dmg} 点真实穿透伤害！", "red")
                    room["cleared"] = True
                    if self.player.is_alive():
                        GUI_INSTANCE.gui_get_input({"0": "继续"}, is_event=True)
                elif event_type == "merchant":
                    pts = self.rng.randint(100, 300)
                    GUI_INSTANCE.gui_print(f"🎒 你遇到了一个身穿黑袍的流浪商人。他递给你一个沉甸甸的钱袋（包含 {pts} 积分）后匆匆离去。", "yellow")
                    self.player.points += pts
                    GUI_INSTANCE.gui_get_input({"0": "继续"}, is_event=True)
                else:
                    GUI_INSTANCE.gui_print("💨 这是一片空地，什么也没有发生，只有风吹过的声音。", "white")
                    GUI_INSTANCE.gui_get_input({"0": "继续"}, is_event=True)
                    
                room["cleared"] = True
            elif room["type"] == "boss":
                GUI_INSTANCE.gui_update_map_pos(self.player_x, self.player_y, self.map_data)
                GUI_INSTANCE.gui_update_status("🚨 遭遇关底 Boss！")
                time.sleep(1.5)
                boss = self.get_scaled_enemies(count=1, is_boss=True)
                cs = CombatSystem(self.player, boss)
                if cs.start_combat():
                    room["cleared"] = True
                    self.total_enemies_killed_here += 1
                    if q_type == "boss":
                        self.quest["current_value"] = 1 # Boss defeated
                     
                    from utils.equipment_gen import generate_equipment
                    q = "传说" if self.rng.randint(1, 100) <= 20 else "史诗"
                    eq = generate_equipment(self.player_level, specific_quality=q)
                    print_success(f"💎 Boss轰然倒下...掉落了极品装备: {eq['name']} 💎")
                    self.player.inventory.append(eq)
                    time.sleep(2)
        else:
            GUI_INSTANCE.gui_update_status("探索安全区域。")
            
        # Re-render map to reflect cleared status if they survived
        if self.player.is_alive():
            GUI_INSTANCE.gui_update_map_pos(self.player_x, self.player_y, self.map_data) # Update natively without redraw
            
        # Check completion
        if q_type in ["survive", "kill", "explore"] and self.quest["current_value"] >= self.quest["target_value"]:
            self.mission_completed = True
        elif q_type == "boss" and self.quest["current_value"] >= 1:
            self.mission_completed = True
