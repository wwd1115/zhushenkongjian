from utils.display import clear_screen, show_menu, print_header, print_error, print_info, print_success, print_warning, get_input
import time
import json
import os
import math

class MainGodSpace:
    def __init__(self, game):
        self.game = game
        self.items_data = {}
        self.skills_data = {}
        self.shop_data = {}
        self.load_data()

    def load_data(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        try:
            with open(os.path.join(base_dir, "data", "items.json"), "r", encoding="utf-8") as f:
                self.items_data = json.load(f)
            with open(os.path.join(base_dir, "data", "skills.json"), "r", encoding="utf-8") as f:
                self.skills_data = json.load(f)
            with open(os.path.join(base_dir, "data", "shop.json"), "r", encoding="utf-8") as f:
                self.shop_data = json.load(f)
        except Exception as e:
            print_error(f"加载数据失败: {e}")

    @property
    def player(self):
        return self.game.player

    def enter(self):
        while True:
            if not self.player or not self.player.is_alive():
                break
            clear_screen()
            print_info(self.player.show_status())
            print("-" * 50)
            options = {
                "1": "进入任务大厅",
                "2": "强化大厅 (属性与血统图谱)",
                "3": "进入兑换商城 (装备道具)",
                "4": "进入休息区",
                "5": "查看属性与背包",
                "6": "查看个人成就",
                "7": "查看排行榜",
                "8": "保存游戏",
                "0": "返回主菜单(退出当前角色)"
            }
            choice = show_menu("主神空间", options)
            
            if choice == "1":
                self.task_hall()
            elif choice == "2":
                self.enhance_hall()
            elif choice == "3":
                self.shop()
            elif choice == "4":
                self.rest_area()
            elif choice == "5":
                self.view_inventory_ui()
            elif choice == "6":
                self.view_achievements()
            elif choice == "7":
                self.view_leaderboard()
            elif choice == "8":
                self.game.save_game()
            elif choice == "0":
                self.game.player = None
                break

    def task_hall(self):
        clear_screen()
        import random
        from data.world_templates import TEMPLATES
        from scenes.world_engine import ProceduralWorld
        
        # 动态计算玩家总评分
        power_score = (self.player.str + self.player.agi + self.player.int + 
                       self.player.con + self.player.per)
                       
        if power_score < 70:
            difficulty = "新手"
        elif power_score < 120:
            difficulty = "进阶"
        else:
            difficulty = "精英"
            
        print_header(f"轮回之门 - 当前评价等级: {difficulty} (评分: {power_score})")
        print_info("主神为你揭开了无数个未知的时空锚点...")
        
        options = {}
        world_map = {}
        for idx in range(3):
            template = random.choice(TEMPLATES)
            seed = random.randint(10000, 99999)
            
            # Predict name for display
            prefix = random.Random(seed).choice(template.name_prefixes)
            options[str(idx + 1)] = f"【未知探测】: {prefix} 的世界 (基础倍率: {(self.player.level * 0.8):.1f}x)"
            world_map[str(idx + 1)] = (template, seed)
            
        options["0"] = "返回主神空间"
        
        choice = show_menu("请选择穿越的裂隙（门后一切皆随机）", options)
        
        if choice in world_map:
            template, seed = world_map[choice]
            world = ProceduralWorld(self.game, template, self.player.level, seed=seed)
            world.enter()

    def enhance_hall(self):
        from utils.display import GUI_INSTANCE
        if not GUI_INSTANCE:
            print_error("视觉强化大厅只能在 GUI 模式下运行！")
            time.sleep(1.5)
            return

        def get_stat_cost(stat_key, current_val):
            # 递增阶梯物价公式: 基础100 + (当前值-10)^1.5 * 15
            base = 100
            if current_val <= 10: return base
            return int(base + math.pow(current_val - 10, 1.5) * 15)

        def get_batch_cost(stat_key, current_val, amount):
            total = 0
            temp_val = current_val
            for _ in range(amount):
                total += get_stat_cost(stat_key, temp_val)
                temp_val += 1
            return total

        def sync_stats():
            return {
                "str": self.player.str, "agi": self.player.agi, "int": self.player.int,
                "con": self.player.con, "per": self.player.per, "cha": self.player.cha,
                "points": self.player.points
            }

        # Prepare Node Data (星图中不再有属性星球，属性移到了侧边栏)
        nodes = []
        unlocked = []
        
        # 1. Bloodlines Root (血统变异节点)
        nodes.append({"id": "bl_root", "name": "核心血统树", "type": "category", "x": 0, "y": -140})
        unlocked.append("bl_root")
        
        b_idx = 0
        for b_id, b_data in self.shop_data.get("bloodlines", {}).items():
            base_node_id = f"bl_{b_id}_base"
            cx = (b_idx * 200) - 150
            cy = -220
            nodes.append({"id": base_node_id, "name": b_data["name"], "type": "bloodline_base", "x": cx, "y": cy, "parents": ["bl_root"]})
            unlocked.append(base_node_id)
            
            prev_id = base_node_id
            for i, lvl in enumerate(b_data["levels"]):
                lvl_id = f"bl_{b_id}_{i}"
                nodes.append({
                    "id": lvl_id, "name": f"{lvl['level']} ({lvl['cost']})", "type": "bloodline",
                    "data": {"bl_id": b_id, "level": lvl["level"], "cost": lvl["cost"], "lvl_idx": i, "bl_data": b_data},
                    "x": cx, "y": cy - 60 * (i + 1), "parents": [prev_id]
                })
                # Check unlock
                if getattr(self.player, 'bloodline', None) and self.player.bloodline.get("name") == b_data["name"]:
                    my_lvl = self.player.bloodline.get("level")
                    my_idx = next((j for j, l in enumerate(b_data["levels"]) if l["level"] == my_lvl), -1)
                    if i <= my_idx: unlocked.append(lvl_id)
                prev_id = lvl_id
            b_idx += 1

        # 2. Skills Root (技能图谱)
        nodes.append({"id": "skill_root", "name": "因果技能网", "type": "category", "x": 0, "y": 140})
        unlocked.append("skill_root")
        
        skills = []
        for key, val in self.skills_data.get("active", {}).items():
            s = val.copy(); s["key"] = key; skills.append(s)
        for key, val in self.skills_data.get("passive", {}).items():
            s = val.copy(); s["key"] = key; skills.append(s)
            
        for i, s in enumerate(skills):
            cost = s.get("price", 500)
            n_id = f"skill_{s['key']}"
            r = 160
            ang = (i / max(1, len(skills))) * 3.1415 * 2
            nx = int(math.cos(ang) * r)
            ny = 140 + int(math.sin(ang) * r)
            nodes.append({
                "id": n_id, "name": f"{s['name']}\\n({cost})", "type": "skill",
                "data": {"skill": s, "cost": cost}, "x": nx, "y": ny, "parents": ["skill_root"]
            })
            if any(ps.get("key") == s["key"] for ps in self.player.skills):
                unlocked.append(n_id)
                
        # Draw Hub
        GUI_INSTANCE.gui_start_enhancement_hub(nodes, unlocked, sync_stats())
        GUI_INSTANCE.gui_update_status(f"强化大厅 | 极品积分: {self.player.points}")
        
        while True:
            response = GUI_INSTANCE.gui_get_input({"0": "返回空间"}, is_hub=True)
            if response == "0": break
            
            if isinstance(response, dict) and response.get("action") == "node_click":
                node_id = response.get("node_id")

                # Handling Stat Clicks (via Sidebar + Button)
                if node_id.startswith("stat_"):
                    stat_key = node_id.replace("stat_", "")
                    curr_val = getattr(self.player, stat_key)
                    unit_price = get_stat_cost(stat_key, curr_val)
                    
                    dialog_text = f"强化 {stat_key.upper()} (当前:{curr_val})\n每次进化消耗: {unit_price} 积分\n输入要强化的点数:"
                    amount_str = GUI_INSTANCE.gui_get_text_input(dialog_text)
                    try:
                        amount = int(amount_str)
                        if amount <= 0: continue
                    except: continue
                    
                    total_cost = get_batch_cost(stat_key, curr_val, amount)
                    if self.player.points < total_cost:
                        affordable = 0; temp_cost = 0
                        for i in range(1, amount + 1):
                            next_c = get_stat_cost(stat_key, curr_val + i - 1)
                            if temp_cost + next_c <= self.player.points:
                                temp_cost += next_c; affordable = i
                            else: break
                        if affordable == 0:
                            GUI_INSTANCE.gui_update_status("奖励点不足以进行哪怕一次本源强化！")
                            continue
                        amount, total_cost = affordable, temp_cost
                    
                    self.player.points -= total_cost
                    self.player.stats["points_spent"] += total_cost
                    setattr(self.player, stat_key, curr_val + amount)
                    self.player.update_stats()
                    GUI_INSTANCE.gui_update_enhancement_hub(unlocked, sync_stats())
                    GUI_INSTANCE.gui_update_status(f"成功强化 {stat_key.upper()} (+{amount})！")
                    continue

                # Planet Nodes
                node = next((n for n in nodes if n["id"] == node_id), None)
                if not node or node["type"] in ["category", "bloodline_base"]: continue
                if node_id in unlocked:
                    GUI_INSTANCE.gui_update_status("已达成该项目。")
                    continue
                if not response.get("can_purchase"):
                    GUI_INSTANCE.gui_update_status("前置条件未解锁。")
                    continue
                
                cost = node["data"].get("cost", 0)
                if self.player.points < cost:
                    GUI_INSTANCE.gui_update_status(f"积分不足 (需{cost})")
                    continue
                    
                if node["type"] == "skill":
                    self.player.points -= cost
                    self.player.stats["points_spent"] += cost
                    self.player.skills.append(node["data"]["skill"])
                    unlocked.append(node_id)
                    GUI_INSTANCE.gui_update_enhancement_hub(unlocked, sync_stats())
                    GUI_INSTANCE.gui_update_status(f"进化成功：获得 {node['name']}!")
                    
                elif node["type"] == "bloodline":
                    bl_id = node["data"]["bl_id"]
                    lvl_idx = node["data"]["lvl_idx"]
                    bl_data = node["data"]["bl_data"]
                    my_bl = getattr(self.player, 'bloodline', None)
                    
                    if my_bl and my_bl.get("id") != bl_id:
                        GUI_INSTANCE.gui_update_status("体系冲突！您已拥有的血统排斥此次进化。")
                        continue
                        
                    self.player.points -= cost
                    self.player.stats["points_spent"] += cost
                    new_bl = {"id": bl_id, "name": bl_data["name"], "level": node["data"]["level"]}
                    # Apply permanent stat boost from bloodline level
                    lvl_data = bl_data["levels"][lvl_idx]
                    for sk, sv in lvl_data.get("stats", {}).items():
                        self.player.stats[sk] = self.player.stats.get(sk, 0) + sv
                    
                    self.player.bloodline = new_bl
                    self.player.update_stats()
                    unlocked.append(node_id)
                    GUI_INSTANCE.gui_update_enhancement_hub(unlocked, sync_stats())
                    GUI_INSTANCE.gui_update_status(f"血统共鸣成功：{bl_data['name']} 进化至 {node['data']['level']}！")

        GUI_INSTANCE.gui_end_enhancement_hub()

    def learn_skills(self):
        while True:
            clear_screen()
            print_header("技能学习")
            print_info(f"当前积分: {self.player.points}")
            
            options = {}
            idx = 1
            skill_list = []
            
            for key, val in self.skills_data.get("active", {}).items():
                s = val.copy()
                s["key"] = key
                s["type"] = "active"
                skill_list.append(s)
                
            for key, val in self.skills_data.get("passive", {}).items():
                s = val.copy()
                s["key"] = key
                s["type"] = "passive"
                skill_list.append(s)
                
            for s in skill_list:
                options[str(idx)] = f"[{'主动' if s['type']=='active' else '被动'}] {s['name']} - {s.get('price', 0)}积分 ({s.get('desc', '')})"
                idx += 1
                
            options["0"] = "返回"
            
            choice = show_menu("选择要学习的技能", options)
            if choice == "0":
                break
                
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(skill_list):
                    selected_skill = skill_list[choice_idx]
                    
                    has_skill = any(s.get("key") == selected_skill["key"] for s in self.player.skills)
                    if has_skill:
                        print_error("你已经学习过这个技能了！")
                        time.sleep(1.5)
                        continue
                        
                    price = selected_skill.get('price', 99999)
                    if self.player.points >= price:
                        self.player.points -= price
                        self.player.stats["points_spent"] += price
                        self.player.skills.append(selected_skill)
                        self.player.check_achievements()
                        print_success(f"成功学习技能: {selected_skill['name']} !")
                    else:
                        print_error("积分不足！")
                    time.sleep(1.5)
            except ValueError:
                pass

    def enhance_equipment(self):
        while True:
            clear_screen()
            print_header("强化装备")
            print_info(f"当前积分: {self.player.points}")
            wpn = self.player.equipment["weapon"]
            arm = self.player.equipment["armor"]
            
            options = {}
            if wpn:
                lvl = wpn.get("enhance_level", 0)
                cost = 500 * (lvl + 1)
                options["1"] = f"强化武器 ({wpn['name']} +{lvl}) - 需要 {cost} 积分"
            if arm:
                lvl = arm.get("enhance_level", 0)
                cost = 400 * (lvl + 1)
                options["2"] = f"强化防具 ({arm['name']} +{lvl}) - 需要 {cost} 积分"
            
            options["0"] = "返回"
            if not wpn and not arm:
                print_error("你没有任何可以强化的装备！")
                time.sleep(1.5)
                return
                
            choice = show_menu("请选择要强化的装备", options)
            if choice == "0":
                break
                
            if choice == "1" and wpn:
                lvl = wpn.get("enhance_level", 0)
                cost = 500 * (lvl + 1)
                if self.player.points >= cost:
                    self.player.points -= cost
                    self.player.stats["points_spent"] += cost
                    wpn["enhance_level"] = lvl + 1
                    wpn["attack"] = int(wpn["attack"] * 1.2) + 5
                    self.player.update_stats()
                    self.player.check_achievements()
                    print_success(f"强化成功！{wpn['name']} 提升到了 +{lvl+1}！当前攻击加成: {wpn['attack']}")
                else:
                    print_error("积分不足！")
                time.sleep(1.5)
            elif choice == "2" and arm:
                lvl = arm.get("enhance_level", 0)
                cost = 400 * (lvl + 1)
                if self.player.points >= cost:
                    self.player.points -= cost
                    self.player.stats["points_spent"] += cost
                    arm["enhance_level"] = lvl + 1
                    arm["defense"] = int(arm["defense"] * 1.2) + 2
                    self.player.update_stats()
                    self.player.check_achievements()
                    print_success(f"强化成功！{arm['name']} 提升到了 +{lvl+1}！当前防御加成: {arm['defense']}")
                else:
                    print_error("积分不足！")
                time.sleep(1.5)

    def shop(self):
        while True:
            clear_screen()
            print_header("主神空间 - 兑换大厅")
            print_info(f"当前积分: {self.player.points}")
            options = {
                "1": "武器库",
                "2": "防具库",
                "3": "道具与消耗品",
                "4": "🎲 随机装备盲盒 (抽取极品词条!)",
                "0": "返回"
            }
            choice = show_menu("商品分类", options)
            
            if choice == "0":
                break
            elif choice == "1":
                self.buy_items("weapons")
            elif choice == "2":
                self.buy_items("armors")
            elif choice == "3":
                self.buy_items("consumables")
            elif choice == "4":
                self.buy_gacha()

    def buy_gacha(self):
        while True:
            clear_screen()
            print_header("主神空间 - 盲盒抽奖大厅")
            print_info("花费积分，主神将为你随机抽取当前等级的装备（包含上万种词条组合）！")
            print_info(f"当前积分: {self.player.points}")
            
            cost_normal = 300 + self.player.level * 50
            cost_premium = 800 + self.player.level * 100
            
            options = {
                "1": f"普通盲盒 (保底精良，小概率稀有或史诗) - {cost_normal}积分",
                "2": f"高级盲盒 (保底稀有，极大概率史诗，小概率传说) - {cost_premium}积分",
                "0": "返回"
            }
            
            choice = show_menu("抽取你的命运", options)
            if choice == "0":
                break
                
            from utils.equipment_gen import generate_equipment
            import random
            
            if choice == "1":
                if self.player.points >= cost_normal:
                    self.player.points -= cost_normal
                    self.player.stats["points_spent"] += cost_normal
                    
                    r = random.randint(1, 100)
                    q = "精良"
                    if r > 90: q = "史诗"
                    elif r > 70: q = "稀有"
                    elif r < 10: q = "白板"
                    
                    eq = generate_equipment(self.player.level, specific_quality=q)
                    self.player.inventory.append(eq)
                    print_success(f"抽取成功！获得了: {eq['name']}")
                    print_info(f"属性: {eq['desc']}")
                    time.sleep(2.5)
                else:
                    print_error("积分不足！")
                    time.sleep(1)
                    
            elif choice == "2":
                if self.player.points >= cost_premium:
                    self.player.points -= cost_premium
                    self.player.stats["points_spent"] += cost_premium
                    
                    r = random.randint(1, 100)
                    q = "稀有"
                    if r > 95: q = "传说"
                    elif r > 60: q = "史诗"
                    
                    eq = generate_equipment(self.player.level, specific_quality=q)
                    self.player.inventory.append(eq)
                    print_success(f"🎉 高级抽取成功！获得了极品装备: {eq['name']}")
                    print_info(f"属性: {eq['desc']}")
                    time.sleep(2.5)
                else:
                    print_error("积分不足！")
                    time.sleep(1)

    def buy_bloodline(self):
        while True:
            clear_screen()
            print_header("血统强化中心")
            print_info(f"当前积分: {self.player.points}")
            
            bloodlines = self.shop_data.get("bloodlines", {})
            options = {}
            idx = 1
            b_list = list(bloodlines.values())
            for b in b_list:
                options[str(idx)] = f"{b['name']} ({b['desc']})"
                idx += 1
            options["0"] = "返回"
            
            choice = show_menu("请选择要查看的血统", options)
            if choice == "0": break
            
            try:
                c_idx = int(choice) - 1
                if 0 <= c_idx < len(b_list):
                    self.view_bloodline_levels(b_list[c_idx])
            except ValueError:
                pass

    def view_bloodline_levels(self, bg_data):
        while True:
            clear_screen()
            print_header(f"血统 - {bg_data['name']}")
            print_info(bg_data['desc'])
            
            current_level_idx = -1
            if getattr(self.player, 'bloodline', None) and self.player.bloodline.get("name") == bg_data["name"]:
                for i, lvl in enumerate(bg_data["levels"]):
                    if lvl["level"] == self.player.bloodline.get("level"):
                        current_level_idx = i
                        break
            elif getattr(self.player, 'bloodline', None):
                print_error(f"你当前已经拥有了【{self.player.bloodline['name']}】血统，无法兼并在其他体系中！")
                time.sleep(2)
                return
            
            options = {}
            for i, lvl in enumerate(bg_data["levels"]):
                status = "未解锁"
                if i < current_level_idx + 1:
                    status = "已拥有"
                elif i == current_level_idx + 1:
                    status = "可购买"
                else:
                    status = "需前置"
                    
                options[str(i+1)] = f"[{status}] {lvl['level']} - {lvl['cost']}积分"
                
            options["0"] = "返回"
            choice = show_menu("选择层级", options)
            if choice == "0": break
            
            try:
                c_idx = int(choice) - 1
                if 0 <= c_idx < len(bg_data["levels"]):
                    if c_idx <= current_level_idx:
                        print_error("你已经拥有该级别或更高级别了！")
                        time.sleep(1)
                    elif c_idx > current_level_idx + 1:
                        print_error("需要先购买前置级别的血统！")
                        time.sleep(1)
                    else:
                        lvl_data = bg_data["levels"][c_idx]
                        if self.player.points >= lvl_data["cost"]:
                            self.player.points -= lvl_data["cost"]
                            self.player.stats["points_spent"] += lvl_data["cost"]
                            new_bl = bg_data.copy()
                            del new_bl["levels"]
                            new_bl["level"] = lvl_data["level"]
                            new_bl["stats"] = lvl_data["stats"]
                            new_bl["effects"] = lvl_data["effects"]
                            
                            self.player.bloodline = new_bl
                            self.player.update_stats()
                            print_success(f"成功强化【{bg_data['name']}】至 {lvl_data['level']} ！")
                            time.sleep(1.5)
                        else:
                            print_error("积分不足！")
                            time.sleep(1)
            except ValueError:
                pass

    def buy_cultivation(self):
        while True:
            clear_screen()
            print_header("修真与功法楼")
            print_info(f"当前积分: {self.player.points}")
            
            cultivations = self.shop_data.get("cultivation", {})
            options = {}
            idx = 1
            c_list = list(cultivations.values())
            for c in c_list:
                options[str(idx)] = f"{c['name']} ({c['desc']})"
                idx += 1
            options["0"] = "返回"
            
            choice = show_menu("请选择要结印的主修功法", options)
            if choice == "0": break
            
            try:
                c_idx = int(choice) - 1
                if 0 <= c_idx < len(c_list):
                    self.view_cultivation_levels(c_list[c_idx])
            except ValueError:
                pass

    def view_cultivation_levels(self, cg_data):
        while True:
            clear_screen()
            print_header(f"功法 - {cg_data['name']}")
            print_info(cg_data['desc'])
            
            current_level_idx = -1
            if getattr(self.player, 'cultivation', None) and self.player.cultivation.get("name") == cg_data["name"]:
                for i, lvl in enumerate(cg_data["levels"]):
                    if lvl["level"] == self.player.cultivation.get("level"):
                        current_level_idx = i
                        break
            elif getattr(self.player, 'cultivation', None):
                print_error(f"你当前已经主修了【{self.player.cultivation['name']}】，废功重修将导致走火入魔！(暂不支持)")
                time.sleep(2)
                return
            
            options = {}
            for i, lvl in enumerate(cg_data["levels"]):
                status = "未解锁"
                if i < current_level_idx + 1: status = "已拥有"
                elif i == current_level_idx + 1: status = "可购买"
                else: status = "需前置"
                options[str(i+1)] = f"[{status}] {lvl['level']} - {lvl['cost']}积分"
                
            options["0"] = "返回"
            choice = show_menu("选择突破境界", options)
            if choice == "0": break
            
            try:
                c_idx = int(choice) - 1
                if 0 <= c_idx < len(cg_data["levels"]):
                    if c_idx <= current_level_idx:
                        print_warning("此境界你已经突破了。")
                        time.sleep(1)
                    elif c_idx > current_level_idx + 1:
                        print_error("修真讲究循序渐进，不可跨界突破！")
                        time.sleep(1)
                    else:
                        lvl_data = cg_data["levels"][c_idx]
                        if self.player.points >= lvl_data["cost"]:
                            self.player.points -= lvl_data["cost"]
                            self.player.stats["points_spent"] += lvl_data["cost"]
                            new_cu = cg_data.copy()
                            del new_cu["levels"]
                            new_cu["level"] = lvl_data["level"]
                            new_cu["stats"] = lvl_data["stats"]
                            new_cu["effects"] = lvl_data.get("effects", [])
                            
                            self.player.cultivation = new_cu
                            self.player.update_stats()
                            print_success(f"成功突破【{cg_data['name']}】至 {lvl_data['level']} ！体会浩瀚神威。")
                            time.sleep(1.5)
                        else:
                            print_error("积分不足！")
                            time.sleep(1)
            except ValueError:
                pass

    def buy_items(self, category):
        while True:
            clear_screen()
            items = self.shop_data.get(category, [])
            cat_cn = {"weapons": "武器", "armors": "防具", "consumables": "道具/消耗品"}.get(category, category)
            print_header(f"购买 - {cat_cn}")
            print_info(f"当前积分: {self.player.points}")
            
            options = {}
            for idx, item in enumerate(items):
                options[str(idx+1)] = f"{item['name']} - {item.get('cost', 9999)}积分 ({item.get('desc', '')})"
            options["0"] = "返回"
            
            choice = show_menu("请选择要购买的物品", options)
            if choice == "0":
                break
                
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(items):
                    item = items[choice_idx].copy()
                    price = item.get('cost', 999999)
                    if self.player.points >= price:
                        self.player.points -= price
                        self.player.stats["points_spent"] += price
                        if category == "weapons":
                            self.player.equipment["weapon"] = item
                            print_success(f"购买并装备了 {item['name']}!")
                        elif category == "armors":
                            self.player.equipment["armor"] = item
                            print_success(f"购买并装备了 {item['name']}!")
                        else:
                            self.player.inventory.append(item)
                            print_success(f"购买了 {item['name']} 并放入背包。")
                        self.player.update_stats()
                        self.player.check_achievements()
                    else:
                        print_error("积分不足！")
                    time.sleep(1.5)
            except ValueError:
                pass


    def rest_area(self):
        clear_screen()
        print_header("休息区")
        options = {
            "1": "免费休息 (恢复50%生命值 and 精神力)",
            "2": "高级恢复 (消耗100积分，完全恢复)",
            "0": "返回"
        }
        choice = show_menu("休息选项", options)
        if choice == "1":
            self.player.heal(self.player.max_hp // 2)
            self.player.restore_mp(self.player.max_mp // 2)
            print_success("休息完毕，生命和精神力恢复50%。")
        elif choice == "2":
            if self.player.points >= 100:
                self.player.points -= 100
                self.player.hp = self.player.max_hp
                self.player.mp = self.player.max_mp
                self.player.status_effects.clear()
                print_success("高级恢复完毕，状态全满！")
            else:
                print_error("积分不足！")
        time.sleep(1.5)

    def view_inventory_ui(self):
        from utils.display import GUI_INSTANCE
        if not GUI_INSTANCE:
            print_error("视觉背包与属性面板只能在 GUI 模式下运行！")
            time.sleep(1.5)
            return

        def get_player_data():
            p = self.player
            eq = p.equipment
            
            return {
                "name": p.name,
                "level": p.level,
                "hp": p.hp, "max_hp": p.max_hp,
                "mp": p.mp, "max_mp": p.max_mp,
                "str": p.str, "agi": p.agi, "int": p.int,
                "con": p.con, "per": p.per, "cha": p.cha,
                "points": p.points, "free_stats": p.free_stats,
                "equipment": {
                    "weapon": eq.get("weapon"),
                    "armor": eq.get("armor"),
                    "accessory": eq.get("accessory")
                },
                "inventory": p.inventory
            }

        GUI_INSTANCE.gui_start_visual_inventory(get_player_data())
        GUI_INSTANCE.gui_update_status("背包管理器 | 查看属性详情与物品")
        
        while True:
            response = GUI_INSTANCE.gui_get_input({"0": "返回空间"}, is_hub=False)
            if response == "0":
                break
            elif isinstance(response, dict) and "action" in response:
                action = response["action"]
                parts = action.split("_", 1)
                
                if parts[0] == "equip":
                    idx = int(parts[1])
                    if 0 <= idx < len(self.player.inventory):
                        item = self.player.inventory[idx]
                        slot = item.get("type", "")
                        if slot in ["weapon", "armor", "accessory"]:
                            if self.player.level < item.get("level_req", 1):
                                GUI_INSTANCE.gui_update_status(f"等级不足！需要Lv.{item.get('level_req', 1)}")
                            else:
                                old_item = self.player.equipment.get(slot)
                                if old_item:
                                    self.player.inventory.append(old_item)
                                self.player.equipment[slot] = item
                                self.player.inventory.remove(item)
                                self.player.update_stats()
                                GUI_INSTANCE.gui_update_status(f"已装备: {item['name']}")
                
                elif parts[0] == "unequip":
                    slot = parts[1]
                    if slot in self.player.equipment and self.player.equipment[slot]:
                        item = self.player.equipment[slot]
                        self.player.inventory.append(item)
                        self.player.equipment[slot] = None
                        self.player.update_stats()
                        GUI_INSTANCE.gui_update_status(f"已卸下: {item['name']}")
                
                elif parts[0] == "drop":
                    idx = int(parts[1])
                    if 0 <= idx < len(self.player.inventory):
                        item = self.player.inventory[idx]
                        val = item.get('value', 50)
                        self.player.points += val
                        self.player.inventory.remove(item)
                        GUI_INSTANCE.gui_update_status(f"已出售: {item['name']}, 获得 {val} 积分")
                        
                elif parts[0] == "use":
                    idx = int(parts[1])
                    if 0 <= idx < len(self.player.inventory):
                        item = self.player.inventory[idx]
                        if item.get("type", "") == "consumable":
                            # Apply effects
                            healed = 0
                            restored = 0
                            if "heal" in item:
                                healed = item["heal"]
                                self.player.heal(healed)
                            if "restore_mp" in item:
                                restored = item["restore_mp"]
                                self.player.restore_mp(restored)
                            self.player.inventory.remove(item)
                            GUI_INSTANCE.gui_update_status(f"使用了: {item['name']} (恢复了生命 {healed}, 精神 {restored})")

                # Update UI
                GUI_INSTANCE.gui_update_visual_inventory(get_player_data())

        GUI_INSTANCE.gui_end_visual_inventory()

    def view_achievements(self):
        clear_screen()
        print_header("个人成就")
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        try:
            with open(os.path.join(base_dir, "data", "achievements.json"), "r", encoding="utf-8") as f:
                all_achs = json.load(f)
        except Exception:
            all_achs = {}
            
        if not self.player.achievements:
            print_info("你还没有解锁任何成就。")
        else:
            for ach_key in self.player.achievements:
                if ach_key in all_achs:
                    ach = all_achs[ach_key]
                    print_success(f"🏆 【{ach['name']}】 - {ach['desc']}")
                else:
                    print_success(f"🏆 【未知成就】 - {ach_key}")
                    
        print("-" * 50)
        print_info(f"统计数据: 击杀 {self.player.stats['kills']} | 死亡 {self.player.stats['deaths']} | 消费积分 {self.player.stats['points_spent']}")
        
        get_input("按回车键返回...")
        
    def view_leaderboard(self):
        clear_screen()
        print_header("轮回者排行榜")
        from save.leaderboard import LeaderboardSystem
        lb = LeaderboardSystem()
        top_records = lb.get_top(10)
        
        if not top_records:
            print_warning("暂无排行数据。")
        else:
            for idx, r in enumerate(top_records):
                print_info(f"第 {idx + 1} 名: 【{r['name']}】 - 综合评分: {r['score']} - {r['details']}")
                
        print("-" * 50)
        get_input("按回车键返回...")
