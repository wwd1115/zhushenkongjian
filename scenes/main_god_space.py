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
                "4": "装备锻造与附魔台",
                "5": "轮回小队酒馆 (招募队友)",
                "6": "进入休息区",
                "7": "查看属性与背包",
                "8": "查看个人成就",
                "9": "查看排行榜",
                "S": "保存游戏",
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
                self.forge_hall()
            elif choice == "5":
                self.tavern()
            elif choice == "6":
                self.rest_area()
            elif choice == "7":
                self.view_inventory_ui()
            elif choice == "8":
                self.view_achievements()
            elif choice == "9":
                self.view_leaderboard()
            elif choice == "S" or choice == "s":
                self.game.save_game()
            elif choice == "0":
                self.game.player = None
                break

    def forge_hall(self):
        while True:
            clear_screen()
            print_header("🔥 装备锻造台 🔥")
            print_info("在这里你可以提炼装备（提升基础属性）或进行宝石镶嵌（附加特殊属性）。")
            print_info(f"当前积分: {self.player.points}")

            options = {
                "1": "装备强化 (提升基础攻击/防御)",
                "2": "宝石镶嵌 (附加力量/敏捷/体质等)",
                "0": "离开锻造台"
            }
            choice = show_menu("选择锻造服务", options)

            if choice == "0": break
            elif choice == "1": self._forge_enhance()
            elif choice == "2": self._forge_socketing()

    def _get_equippable(self):
        equippable = []
        if self.player.equipment["weapon"]: equippable.append(("weapon", self.player.equipment["weapon"]))
        if self.player.equipment["armor"]: equippable.append(("armor", self.player.equipment["armor"]))
        if self.player.equipment["accessory"]: equippable.append(("accessory", self.player.equipment["accessory"]))
        return equippable

    def _forge_enhance(self):
        while True:
            clear_screen()
            print_header("装备强化")
            equippable = self._get_equippable()

            if not equippable:
                print_error("你身上没有任何穿戴中的装备可以强化！")
                time.sleep(1.5)
                break

            options = {}
            for idx, (slot, item) in enumerate(equippable):
                lvl = item.get("enhance_level", 0)
                cost = (lvl + 1) * 300 + item.get("level_req", 1) * 50
                options[str(idx+1)] = f"[{slot.upper()}] {item['name']} (当前: +{lvl}) - 锻造费用: {cost} 积分"

            options["0"] = "返回"
            choice = show_menu("请选择要强化的装备", options)

            if choice == "0": break
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(equippable):
                    slot, item = equippable[choice_idx]
                    lvl = item.get("enhance_level", 0)
                    cost = (lvl + 1) * 300 + item.get("level_req", 1) * 50

                    if self.player.points >= cost:
                        self.player.points -= cost
                        self.player.stats["points_spent"] += cost

                        item["enhance_level"] = lvl + 1

                        # Remove old +X from name if exists
                        import re
                        clean_name = re.sub(r' \[\+\d+\]', '', item["name"])
                        item["name"] = f"{clean_name} [+{lvl+1}]"

                        # Enhance base stats by 15% per level
                        if "attack" in item: item["attack"] = int(item["attack"] * 1.15)
                        if "defense" in item: item["defense"] = int(item["defense"] * 1.15)
                        for attr in ["str", "agi", "int", "con", "per", "cha"]:
                            if attr in item: item[attr] = int(item[attr] * 1.10) + 1

                        self.player.update_stats()
                        print_success(f"🔨 叮！锻造成功！你的装备进化为了: {item['name']}")
                    else:
                        print_error("积分不足以进行这次锻造！")
                    time.sleep(1.5)
            except ValueError:
                pass

    def _forge_socketing(self):
        while True:
            clear_screen()
            print_header("宝石镶嵌")
            print_info("选择一件装备并镶嵌背包中的宝石。每件装备最多镶嵌3颗宝石。")
            equippable = self._get_equippable()

            if not equippable:
                print_error("你身上没有任何穿戴中的装备！")
                time.sleep(1.5)
                break

            options = {}
            for idx, (slot, item) in enumerate(equippable):
                gems = item.get("gems", [])
                options[str(idx+1)] = f"[{slot.upper()}] {item['name']} (孔位: {len(gems)}/3)"
            options["0"] = "返回"

            choice = show_menu("请选择要镶嵌的装备", options)
            if choice == "0": break

            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(equippable):
                    slot, item = equippable[choice_idx]
                    if len(item.get("gems", [])) >= 3:
                        print_error("该装备的孔位已满，无法再镶嵌宝石！")
                        time.sleep(1.5)
                        continue

                    # Find gems in inventory
                    gems_in_inv = [i for i in self.player.inventory if "宝石" in i.get("name", "")]
                    if not gems_in_inv:
                        print_error("你的背包里没有任何宝石！请先去兑换大厅购买。")
                        time.sleep(1.5)
                        continue

                    gem_options = {}
                    for g_idx, gem in enumerate(gems_in_inv):
                        gem_options[str(g_idx+1)] = f"{gem['name']} - {gem.get('desc', '')}"
                    gem_options["0"] = "取消"

                    gem_choice = show_menu("选择要镶嵌的宝石", gem_options)
                    if gem_choice == "0": continue

                    gem_choice_idx = int(gem_choice) - 1
                    if 0 <= gem_choice_idx < len(gems_in_inv):
                        gem_to_socket = gems_in_inv[gem_choice_idx]
                        self.player.inventory.remove(gem_to_socket)
                        if "gems" not in item:
                            item["gems"] = []
                        item["gems"].append(gem_to_socket)
                        print_success(f"成功将 {gem_to_socket['name']} 镶嵌到 {item['name']} 上！")
                        self.player.update_stats()
                        time.sleep(1.5)
            except ValueError:
                pass

    def tavern(self):
        import random
        from classes.teammate import Teammate

        while True:
            clear_screen()
            print_header("🍻 轮回小队酒馆 🍻")
            print_info("这里聚集着来自不同位面的轮回者。你可以花费积分招募他们作为队友，或管理现有小队。")
            print_info(f"当前积分: {self.player.points} | 当前队伍规模: {len(self.player.teammates)}/4")

            # Generate 3 random mercenaries
            mercs = []
            cost_base = self.player.level * 800

            names = ["剑客·亚索", "盾卫·亚瑟", "刺客·荆轲", "机械师·源氏", "法师·甘道夫", "狂战·奥拉夫", "游侠·温蒂"]
            for _ in range(3):
                m_name = random.choice(names)
                names.remove(m_name)

                # Scale stats around player level
                m_hp = int(100 + self.player.level * random.uniform(15, 25))
                m_atk = int(20 + self.player.level * random.uniform(3, 6))
                m_def = int(10 + self.player.level * random.uniform(2, 5))
                m_agi = int(15 + self.player.level * random.uniform(1, 3))

                m_cost = int(cost_base * random.uniform(0.8, 1.2))
                mercs.append({
                    "name": m_name, "hp": m_hp, "attack": m_atk, "defense": m_def, "agi": m_agi, "cost": m_cost
                })

            options = {}
            for idx, m in enumerate(mercs):
                desc = f"HP:{m['hp']} ATK:{m['attack']} DEF:{m['defense']} AGI:{m['agi']}"
                options[str(idx+1)] = f"招募【{m['name']}】 ({desc}) - 签约费: {m['cost']} 积分"

            options["M"] = "管理当前小队 (特训 / 解雇)"
            options["0"] = "离开酒馆"
            choice = show_menu("今日可招募佣兵", options)

            if choice == "0": break
            elif choice.upper() == "M":
                self.manage_teammates()
                continue

            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(mercs):
                    if len(self.player.teammates) >= 4:
                        print_error("你的队伍已满(最多4人)，无法招募更多队友！请先解雇现有队友。")
                        time.sleep(2)
                        continue

                    m = mercs[choice_idx]
                    if self.player.points >= m["cost"]:
                        self.player.points -= m["cost"]
                        self.player.stats["points_spent"] += m["cost"]

                        new_mate = Teammate(m["name"], m["hp"], m["attack"], m["defense"], m["agi"])
                        self.player.teammates.append(new_mate)

                        print_success(f"🍻 招募成功！{m['name']} 加入了你的轮回小队！")
                    else:
                        print_error("积分不足以支付签约费！")
                    time.sleep(1.5)
            except ValueError:
                pass

    def manage_teammates(self):
        while True:
            clear_screen()
            print_header("🛡️ 队伍管理与特训中心 🛡️")
            print_info(f"当前积分: {self.player.points}")
            if not self.player.teammates:
                print_error("你目前没有招募任何队友。")
                time.sleep(1.5)
                break

            options = {}
            for idx, tm in enumerate(self.player.teammates):
                cost = tm.max_hp + tm.attack * 5 + tm.defense * 10
                desc = f"HP:{tm.hp}/{tm.max_hp} ATK:{tm.attack} DEF:{tm.defense} AGI:{tm.agi}"
                options[str(idx+1)] = f"特训【{tm.name}】(+15%属性) - 消耗: {cost}积分\n      {desc}"

            options["D"] = "解雇队友 (腾出空位)"
            options["0"] = "返回上一页"

            choice = show_menu("请选择你要操作的队员", options)
            if choice == "0": break
            elif choice.upper() == "D":
                self.dismiss_teammate()
                continue

            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(self.player.teammates):
                    tm = self.player.teammates[choice_idx]
                    cost = tm.max_hp + tm.attack * 5 + tm.defense * 10
                    if self.player.points >= cost:
                        self.player.points -= cost
                        self.player.stats["points_spent"] += cost

                        tm.max_hp = int(tm.max_hp * 1.15)
                        tm.hp = tm.max_hp
                        tm.attack = int(tm.attack * 1.15) + 1
                        tm.defense = int(tm.defense * 1.15) + 1
                        tm.agi = int(tm.agi * 1.15) + 1

                        print_success(f"💪 特训完成！{tm.name} 的属性得到了全面提升！")
                    else:
                        print_error("积分不足以进行这次特训！")
                    time.sleep(1.5)
            except ValueError:
                pass

    def dismiss_teammate(self):
        while True:
            clear_screen()
            print_header("👋 解雇队友")
            options = {}
            for idx, tm in enumerate(self.player.teammates):
                options[str(idx+1)] = f"解雇【{tm.name}】"
            options["0"] = "取消"

            choice = show_menu("请选择要遣散的队友 (此操作不可逆)", options)
            if choice == "0": break
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(self.player.teammates):
                    tm = self.player.teammates[choice_idx]
                    confirm = get_input(f"确定要解雇 {tm.name} 吗？(y/N): ")
                    if confirm.lower() == 'y':
                        self.player.teammates.pop(choice_idx)
                        print_warning(f"{tm.name} 离开了队伍。")
                        time.sleep(1.5)
                        break
            except ValueError:
                pass

    def task_hall(self):
        clear_screen()
        import random
        from data.world_templates import TEMPLATES
        from scenes.world_engine import ProceduralWorld
        
        power_score = getattr(self.player, 'power_score', 0)
                       
        if power_score < 150: difficulty = "新手"
        elif power_score < 300: difficulty = "进阶"
        else: difficulty = "精英"
            
        print_header(f"轮回之门 - 当前评价等级: {difficulty} (综合评分: {power_score})")
        print_info("主神为你揭开了无数个未知的时空锚点...")
        
        options = {}
        world_map = {}
        for idx in range(3):
            template = random.choice(TEMPLATES)
            seed = random.randint(10000, 99999)
            prefix = random.Random(seed).choice(template.name_prefixes)
            # Make the multiplier slightly more punishing for early game balance
            mult = max(1.0, (self.player.level * 0.9))
            options[str(idx + 1)] = f"【未知探测】: {prefix} 的世界 (基础难度倍率: {mult:.1f}x)"
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
            # 增加基础强化消耗，从100提升至150，并增加指数倍率，使得后期强化更加昂贵，增加平衡性挑战
            base = 150
            if current_val <= 10: return base
            return int(base + math.pow(current_val - 10, 1.6) * 20)

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

        nodes, unlocked = self._generate_enhancement_nodes()

        GUI_INSTANCE.gui_start_enhancement_hub(nodes, unlocked, sync_stats())
        GUI_INSTANCE.gui_update_status(f"强化大厅 | 极品积分: {self.player.points}")

        while True:
            response = GUI_INSTANCE.gui_get_input({"0": "返回空间"}, is_hub=True)
            if response == "0": break

            if isinstance(response, dict) and response.get("action") == "node_click":
                self._handle_enhancement_click(response, nodes, unlocked, sync_stats, get_stat_cost, get_batch_cost)

        GUI_INSTANCE.gui_end_enhancement_hub()

    def _generate_enhancement_nodes(self):
        nodes = []
        unlocked = []
        
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
                    "id": lvl_id, "name": f"{lvl['level']}", "type": "bloodline",
                    "data": {"bl_id": b_id, "level": lvl["level"], "cost": lvl["cost"], "lvl_idx": i, "bl_data": b_data},
                    "x": cx, "y": cy, "parents": [prev_id]
                })
                if getattr(self.player, 'bloodline', None) and self.player.bloodline.get("name") == b_data["name"]:
                    my_lvl = self.player.bloodline.get("level")
                    my_idx = next((j for j, l in enumerate(b_data["levels"]) if l["level"] == my_lvl), -1)
                    if i <= my_idx: unlocked.append(lvl_id)
                prev_id = lvl_id
            b_idx += 1

        # 解析修真功法
        nodes.append({"id": "cult_root", "name": "修真与功法", "type": "category", "x": 0, "y": 0})
        unlocked.append("cult_root")

        c_idx = 0
        for c_id, c_data in self.shop_data.get("cultivation", {}).items():
            base_node_id = f"cult_{c_id}_base"
            cx = (c_idx * 200) - 150
            cy = -50
            nodes.append({"id": base_node_id, "name": c_data["name"], "type": "cultivation_base", "x": cx, "y": cy, "parents": ["cult_root"]})
            unlocked.append(base_node_id)

            prev_id = base_node_id
            for i, lvl in enumerate(c_data["levels"]):
                lvl_id = f"cult_{c_id}_{i}"
                nodes.append({
                    "id": lvl_id, "name": f"{lvl['level']}", "type": "cultivation",
                    "data": {"cult_id": c_id, "level": lvl["level"], "cost": lvl["cost"], "lvl_idx": i, "cult_data": c_data},
                    "x": cx, "y": cy, "parents": [prev_id]
                })
                if getattr(self.player, 'cultivation', None) and self.player.cultivation.get("name") == c_data["name"]:
                    my_lvl = self.player.cultivation.get("level")
                    my_idx = next((j for j, l in enumerate(c_data["levels"]) if l["level"] == my_lvl), -1)
                    if i <= my_idx: unlocked.append(lvl_id)
                prev_id = lvl_id
            c_idx += 1

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
                "id": n_id, "name": f"{s['name']}", "type": "skill",
                "data": {"skill": s, "cost": cost}, "x": nx, "y": ny, "parents": ["skill_root"]
            })
            if any(ps.get("key") == s["key"] for ps in self.player.skills):
                unlocked.append(n_id)
                
        return nodes, unlocked

    def _handle_enhancement_click(self, response, nodes, unlocked, sync_stats, get_stat_cost, get_batch_cost):
        from utils.display import GUI_INSTANCE
        node_id = response.get("node_id")

        if node_id.startswith("stat_"):
            self._handle_stat_enhancement(node_id, sync_stats, get_stat_cost, get_batch_cost, unlocked)
            return

        node = next((n for n in nodes if n["id"] == node_id), None)
        if not node or node["type"] in ["category", "bloodline_base", "cultivation_base"]: return
        if node_id in unlocked:
            GUI_INSTANCE.gui_update_status("已达成该项目。")
            return
        if not response.get("can_purchase"):
            GUI_INSTANCE.gui_update_status("前置条件未解锁。")
            return

        cost = node["data"].get("cost", 0)

        # STRICT VALIDATION: Double check points immediately before transaction
        if self.player.points < cost:
            GUI_INSTANCE.gui_update_status(f"积分不足 (需{cost})")
            return
            
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
                return
                
            self.player.points -= cost
            self.player.stats["points_spent"] += cost
            new_bl = {"id": bl_id, "name": bl_data["name"], "level": node["data"]["level"]}
            lvl_data = bl_data["levels"][lvl_idx]
            for sk, sv in lvl_data.get("stats", {}).items():
                self.player.stats[sk] = self.player.stats.get(sk, 0) + sv
            
            self.player.bloodline = new_bl
            self.player.update_stats()
            unlocked.append(node_id)
            GUI_INSTANCE.gui_update_enhancement_hub(unlocked, sync_stats())
            GUI_INSTANCE.gui_update_status(f"血统共鸣成功：{bl_data['name']} 进化至 {node['data']['level']}！")

        elif node["type"] == "cultivation":
            c_id = node["data"]["cult_id"]
            lvl_idx = node["data"]["lvl_idx"]
            c_data = node["data"]["cult_data"]
            my_c = getattr(self.player, 'cultivation', None)

            if my_c and my_c.get("id") != c_id:
                GUI_INSTANCE.gui_update_status("功法冲突！您已修炼的功法排斥此次进阶。")
                return

            self.player.points -= cost
            self.player.stats["points_spent"] += cost
            new_c = {"id": c_id, "name": c_data["name"], "level": node["data"]["level"]}
            lvl_data = c_data["levels"][lvl_idx]
            for sk, sv in lvl_data.get("stats", {}).items():
                self.player.stats[sk] = self.player.stats.get(sk, 0) + sv

            self.player.cultivation = new_c
            self.player.update_stats()
            unlocked.append(node_id)
            GUI_INSTANCE.gui_update_enhancement_hub(unlocked, sync_stats())
            GUI_INSTANCE.gui_update_status(f"功法突破成功：{c_data['name']} 修炼至 {node['data']['level']}！")

    def _handle_stat_enhancement(self, node_id, sync_stats, get_stat_cost, get_batch_cost, unlocked):
        from utils.display import GUI_INSTANCE
        stat_key = node_id.replace("stat_", "")
        curr_val = getattr(self.player, stat_key)
        unit_price = get_stat_cost(stat_key, curr_val)

        dialog_text = f"强化 {stat_key.upper()} (当前:{curr_val})\n每次进化消耗: {unit_price} 积分\n输入要强化的点数:"
        amount_str = GUI_INSTANCE.gui_get_text_input(dialog_text)
        try:
            amount = int(amount_str)
            if amount <= 0: return
        except: return

        total_cost = get_batch_cost(stat_key, curr_val, amount)

        # STRICT VALIDATION for stat enhancements
        if self.player.points < total_cost:
            affordable = 0; temp_cost = 0
            for i in range(1, amount + 1):
                next_c = get_stat_cost(stat_key, curr_val + i - 1)
                if temp_cost + next_c <= self.player.points:
                    temp_cost += next_c; affordable = i
                else: break
            if affordable == 0:
                GUI_INSTANCE.gui_update_status("奖励点不足以进行哪怕一次本源强化！")
                return
            amount, total_cost = affordable, temp_cost

        # Final check to absolutely prevent negative points
        if self.player.points < total_cost or total_cost < 0:
            GUI_INSTANCE.gui_update_status("交易异常！")
            return

        self.player.points -= total_cost
        self.player.stats["points_spent"] += total_cost
        setattr(self.player, stat_key, curr_val + amount)
        self.player.update_stats()
        GUI_INSTANCE.gui_update_enhancement_hub(unlocked, sync_stats())
        GUI_INSTANCE.gui_update_status(f"成功强化 {stat_key.upper()} (+{amount})！")

    def shop(self):
        while True:
            clear_screen()
            print_header("主神空间 - 兑换大厅")
            print_info(f"当前积分: {self.player.points}")
            options = {
                "1": "武器库",
                "2": "防具库",
                "3": "道具与消耗品",
                "4": "召唤兽与灵宠",
                "5": "🎲 随机装备盲盒 (抽取极品词条!)",
                "6": "💎 宝石材料库 (锻造台镶嵌使用)",
                "0": "返回"
            }
            choice = show_menu("商品分类", options)
            
            if choice == "0": break
            elif choice == "1": self.buy_items("weapons")
            elif choice == "2": self.buy_items("armors")
            elif choice == "3": self.buy_items("consumables")
            elif choice == "4": self.buy_pets()
            elif choice == "5": self.buy_gacha()
            elif choice == "6": self.buy_items("gems")

    def buy_pets(self):
        while True:
            clear_screen()
            pets = self.shop_data.get("pets", [])
            print_header("主神空间 - 宠物契约大厅")
            print_info(f"当前积分: {self.player.points}")
            print_warning("同一时间只能出战一只宠物，但您可以拥有多只。")

            options = {}
            for idx, pet in enumerate(pets):
                options[str(idx+1)] = f"{pet['name']} - {pet.get('cost', 9999)}积分 ({pet.get('desc', '')})"

            options["C"] = "管理当前拥有的宠物"
            options["0"] = "返回"

            choice = show_menu("请选择要缔结契约的宠物", options)
            if choice == "0": break
            elif choice == "C":
                self.manage_pets()
                continue

            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(pets):
                    pet_data = pets[choice_idx].copy()
                    base_price = pet_data.get('cost', 999999)
                    discount = getattr(self.player, 'shop_discount', 0)
                    price = int(base_price * (1 - discount))

                    if any(p.get("id") == pet_data.get("id") for p in getattr(self.player, 'pets', [])):
                        print_error("你已经拥有该灵宠了！")
                        time.sleep(1.5)
                        continue

                    if self.player.points >= price:
                        self.player.points -= price
                        self.player.stats["points_spent"] += price
                        if not hasattr(self.player, 'pets'):
                            self.player.pets = []
                        self.player.pets.append(pet_data)
                        if getattr(self.player, 'active_pet', None) is None:
                            self.player.active_pet = pet_data
                            print_success(f"契约成功！获得了 {pet_data['name']}，并自动设置为出战状态！")
                        else:
                            print_success(f"契约成功！获得了 {pet_data['name']}！")
                        self.player.update_stats()
                    else:
                        print_error("积分不足！")
                    time.sleep(1.5)
            except ValueError:
                pass

    def manage_pets(self):
        while True:
            clear_screen()
            print_header("灵宠管理与升星")
            my_pets = getattr(self.player, 'pets', [])
            active = getattr(self.player, 'active_pet', None)

            if not my_pets:
                print_error("你当前没有任何灵宠！")
                time.sleep(1.5)
                break

            options = {}
            for idx, p in enumerate(my_pets):
                status = "[出战中] " if active and active.get("id") == p.get("id") else ""
                options[str(idx+1)] = f"{status}{p['name']} (HP: {p.get('hp')} | ATK: {p.get('attack')})"

            options["0"] = "返回"
            choice = show_menu("选择你要出战的灵宠", options)

            if choice == "0": break
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(my_pets):
                    self.player.active_pet = my_pets[idx]
                    print_success(f"已将 {my_pets[idx]['name']} 设置为出战灵宠！")
                    time.sleep(1)
            except ValueError:
                pass

    def buy_gacha(self):
        while True:
            clear_screen()
            print_header("主神空间 - 盲盒抽奖大厅")
            print_info("花费积分，主神将为你随机抽取当前等级的装备（包含上万种词条组合）！")
            print_info(f"当前积分: {self.player.points}")
            
            discount = getattr(self.player, 'shop_discount', 0)

            cost_normal = int((400 + self.player.level * 80) * (1 - discount))
            cost_premium = int((1200 + self.player.level * 150) * (1 - discount))
            
            options = {
                "1": f"普通盲盒 (保底精良，小概率稀有或史诗) - {cost_normal}积分",
                "2": f"高级盲盒 (保底稀有，极大概率史诗，小概率传说) - {cost_premium}积分",
                "0": "返回"
            }
            
            choice = show_menu("抽取你的命运", options)
            if choice == "0": break

            from utils.equipment_gen import generate_equipment
            import random
            
            if choice == "1":
                self._process_gacha(cost_normal, ["精良", "稀有", "史诗"], [92, 75, 0]) # Slight nerf to drop rates
            elif choice == "2":
                self._process_gacha(cost_premium, ["稀有", "史诗", "传说"], [97, 65, 0]) # Slight nerf to drop rates

    def _process_gacha(self, cost, qualities, thresholds):
        import random
        from utils.equipment_gen import generate_equipment

        if self.player.points >= cost:
            self.player.points -= cost
            self.player.stats["points_spent"] += cost
            
            r = random.randint(1, 100)
            q = qualities[0]
            if r > thresholds[0]: q = qualities[2]
            elif r > thresholds[1]: q = qualities[1]
            elif r < 15 and qualities[0] == "精良": q = "白板" # slightly higher chance for white from normal
            
            eq = generate_equipment(self.player.level, specific_quality=q)
            self.player.inventory.append(eq)
            print_success(f"抽取成功！获得了: {eq['name']}")
            print_info(f"属性: {eq['desc']}")
            time.sleep(2.5)
        else:
            print_error("积分不足！")
            time.sleep(1)

    def buy_items(self, category):
        while True:
            clear_screen()
            items = self.shop_data.get(category, [])
            cat_cn = {"weapons": "武器", "armors": "防具", "consumables": "道具/消耗品", "gems": "镶嵌宝石"}.get(category, category)
            print_header(f"购买 - {cat_cn}")
            print_info(f"当前积分: {self.player.points}")
            
            options = {}
            for idx, item in enumerate(items):
                options[str(idx+1)] = f"{item['name']} - {item.get('cost', 9999)}积分 ({item.get('desc', '')})"
            options["0"] = "返回"
            
            choice = show_menu("请选择要购买的物品", options)
            if choice == "0": break
                
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(items):
                    item = items[choice_idx].copy()
                    base_price = item.get('cost', 999999)
                    discount = getattr(self.player, 'shop_discount', 0)
                    price = int(base_price * (1 - discount))

                    if self.player.points >= price:
                        self.player.points -= price
                        self.player.stats["points_spent"] += price
                        if category == "weapons":
                            self.player.equipment["weapon"] = item
                            print_success(f"花费 {price} 积分购买并装备了 {item['name']}!")
                        elif category == "armors":
                            self.player.equipment["armor"] = item
                            print_success(f"花费 {price} 积分购买并装备了 {item['name']}!")
                        else:
                            self.player.inventory.append(item)
                            print_success(f"花费 {price} 积分购买了 {item['name']} 并放入背包。")
                        self.player.update_stats()
                        self.player.check_achievements()
                    else:
                        print_error(f"积分不足！(折后需要 {price} 积分)")
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
            for pet in getattr(self.player, 'pets', []):
                pet["hp"] = min(pet.get("max_hp", pet.get("hp", 100)), pet.get("hp", 100) + pet.get("max_hp", pet.get("hp", 100)) // 2)
            print_success("休息完毕，你、队友和灵宠的生命和精神力恢复50%。")
        elif choice == "2":
            if self.player.points >= 100:
                self.player.points -= 100
                self.player.hp = self.player.max_hp
                self.player.mp = self.player.max_mp
                self.player.purge_all_statuses()
                for teammate in self.player.teammates:
                    teammate.hp = teammate.max_hp
                for pet in getattr(self.player, 'pets', []):
                    pet["hp"] = pet.get("max_hp", pet.get("hp", 100))
                print_success("高级恢复完毕，你、队友和灵宠的状态全满，所有异常清除！")
            else:
                print_error("积分不足！")
        time.sleep(1.5)

    def view_inventory_ui(self):
        from utils.display import GUI_INSTANCE
        if not GUI_INSTANCE:
            print_error("视觉背包与属性面板只能在 GUI 模式下运行！")
            time.sleep(1.5)
            return

        GUI_INSTANCE.gui_start_visual_inventory(self._get_player_data_for_ui())
        GUI_INSTANCE.gui_update_status("背包管理器 | 查看属性详情与物品")
        
        while True:
            response = GUI_INSTANCE.gui_get_input({"0": "返回空间"}, is_hub=False)
            if response == "0": break
            elif isinstance(response, dict) and "action" in response:
                self._handle_inventory_action(response["action"])
                GUI_INSTANCE.gui_update_visual_inventory(self._get_player_data_for_ui())

        GUI_INSTANCE.gui_end_visual_inventory()

    def _get_player_data_for_ui(self):
        p = self.player
        eq = p.equipment
        return {
            "name": p.name, "level": p.level,
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
            "active_pet": getattr(p, 'active_pet', None),
            "inventory": p.inventory
        }

    def _handle_inventory_action(self, action):
        from utils.display import GUI_INSTANCE

        if action == "rest_pet":
            self.player.active_pet = None
            GUI_INSTANCE.gui_update_status("灵宠已收回休息。")
            return

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
                        if old_item: self.player.inventory.append(old_item)
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
                # Apply 50% depreciation rate to prevent infinite buy/sell point exploits
                base_val = item.get('value', 50)
                val = max(1, base_val // 2)
                self.player.points += val
                self.player.inventory.remove(item)
                GUI_INSTANCE.gui_update_status(f"已出售(折旧): {item['name']}, 获得 {val} 积分")

        elif parts[0] == "use":
            idx = int(parts[1])
            if 0 <= idx < len(self.player.inventory):
                item = self.player.inventory[idx]
                if item.get("type", "") == "consumable":
                    # Legacy support for old hardcoded numbers
                    if "heal" in item: self.player.heal(item.get("heal", 0))
                    if "restore_mp" in item: self.player.restore_mp(item.get("restore_mp", 0))
                    if "mp_restore" in item: self.player.restore_mp(item.get("mp_restore", 0))

                    effect = item.get("effect", "")

                    # Handle specific string effects based on the updated shop data
                    if effect == "heal_15": self.player.heal(int(self.player.max_hp * 0.15))
                    elif effect == "heal_35": self.player.heal(int(self.player.max_hp * 0.35))
                    elif effect == "heal_80": self.player.heal(int(self.player.max_hp * 0.80))
                    elif effect == "heal_100": self.player.hp = self.player.max_hp
                    elif effect == "stats_up_1":
                        self.player.str += 1; self.player.agi += 1; self.player.int += 1
                        self.player.con += 1; self.player.per += 1; self.player.cha += 1
                    elif effect == "stats_up_5":
                        self.player.str += 5; self.player.agi += 5; self.player.int += 5
                        self.player.con += 5; self.player.per += 5; self.player.cha += 5
                    elif effect == "stats_up_30":
                        self.player.str += 30; self.player.agi += 30; self.player.int += 30
                        self.player.con += 30; self.player.per += 30; self.player.cha += 30

                    self.player.update_stats()
                    self.player.inventory.remove(item)
                    GUI_INSTANCE.gui_update_status(f"使用了: {item['name']}")

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
