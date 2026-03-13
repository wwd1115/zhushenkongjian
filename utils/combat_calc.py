import random
import time
from utils.display import clear_screen, print_header, print_info, print_error, print_success, print_warning, show_menu, get_input, GUI_INSTANCE

def get_all_special_effects(player):
    effects = []
    # 装备
    for eq in player.equipment.values():
        if eq and isinstance(eq, dict) and "special_effects" in eq:
            for eff in eq["special_effects"]:
                if isinstance(eff, dict):
                    effects.append(eff)
    # 血统
    if getattr(player, 'bloodline', None) and isinstance(player.bloodline, dict) and "effects" in player.bloodline:
        for eff in player.bloodline["effects"]:
            if isinstance(eff, dict):
                effects.append(eff)
    # 功法
    if getattr(player, 'cultivation', None) and isinstance(player.cultivation, dict) and "effects" in player.cultivation:
        for eff in player.cultivation["effects"]:
            if isinstance(eff, dict):
                effects.append(eff)
    return effects

def calc_dodge_chance(attacker, target):
    atk_agi = getattr(attacker, 'agi', getattr(attacker, 'speed', 10))
    tgt_agi = getattr(target, 'agi', getattr(target, 'speed', 10))
    base_dodge = getattr(target, 'dodge_rate', 0.05)
    
    diff = tgt_agi - atk_agi
    chance = float(base_dodge) + (float(diff) * 0.01)
    return max(0.01, min(0.50, chance))

class CombatSystem:
    def __init__(self, player, enemies):
        self.player = player
        self.player.actor_id = "p_0"
        self.player.is_defending = False
        self.enemies = enemies if isinstance(enemies, list) else [enemies]
        for i, e in enumerate(self.enemies):
            e.actor_id = f"e_{i}"
            e.is_defending = False
        
        # Teammates
        for i, t in enumerate(self.player.teammates):
            t.actor_id = f"p_{i+1}"
            t.is_defending = False
            
        # Pet
        self.pet_actor = None
        if getattr(self.player, 'active_pet', None):
            from classes.teammate import PetActor
            self.pet_actor = PetActor(self.player.active_pet, self.player.level)

        self.turn = 1

    def start_combat(self):
        if GUI_INSTANCE:
            p_team_data = [{"id": self.player.actor_id, "name": self.player.name, "hp": self.player.hp, "max_hp": self.player.max_hp}]
            for t in self.player.teammates:
                if t.is_alive():
                    p_team_data.append({"id": t.actor_id, "name": t.name, "hp": t.hp, "max_hp": t.max_hp})
            if self.pet_actor and self.pet_actor.is_alive():
                p_team_data.append({"id": self.pet_actor.actor_id, "name": self.pet_actor.name, "hp": self.pet_actor.hp, "max_hp": self.pet_actor.max_hp})
                    
            e_team_data = []
            for e in self.enemies:
                if e.is_alive():
                    e_team_data.append({"id": e.actor_id, "name": e.name, "hp": e.hp, "max_hp": e.max_hp})
                    
            GUI_INSTANCE.gui_start_visual_combat(p_team_data, e_team_data)

        clear_screen()
        print_header("🔥 遭遇战触发 🔥")
        enemy_names = ", ".join([e.name for e in self.enemies])
        print_warning(f"遇到了敌人: {enemy_names}!")
        time.sleep(0.5)

        while self.player.is_alive() and any(e.is_alive() for e in self.enemies):
            self.play_turn()

        clear_screen()
        if self.player.is_alive():
            print_success("🔥 战斗胜利！🔥")
            
            # 基础收益
            total_exp = 0
            if len(self.enemies) > 0 and hasattr(self.enemies[0], 'drop_exp'):
                total_exp = sum(e.drop_exp for e in self.enemies)
            else:
                total_exp = sum(e.hp // 2 for e in self.enemies)
                
            total_points = sum(getattr(e, 'drop_points', 50) for e in self.enemies)
            
            # 计算经验和掉落加成特效
            exp_multi = 1.0
            points_multi = 1.0
            all_effs = get_all_special_effects(self.player)
            for eff in all_effs:
                if eff.get("name") == "经验加成":
                    exp_multi += float(eff.get("value", 0)) / 100.0
                elif eff.get("name") == "金钱掉落":
                    points_multi += float(eff.get("value", 0)) / 100.0
                            
            final_exp = int(float(total_exp) * exp_multi)
            final_points = int(float(total_points) * points_multi)
            print_info(f"获得积分: {final_points}")
            
            self.player.gain_exp(final_exp)
            
            self.player.points += final_points
            self.player.stats["kills"] += len(self.enemies)
            self.player.check_achievements()
            
            if GUI_INSTANCE:
                GUI_INSTANCE.gui_combat_event({"type": "end_battle", "is_victory": True})
        else:
            print_error("💀 你已死亡... 💀")
            self.player.stats["deaths"] += 1
            self.player.check_achievements()
            
            if GUI_INSTANCE:
                GUI_INSTANCE.gui_combat_event({"type": "end_battle", "is_victory": False})
        
        get_input("按回车键结束战斗...")
        if GUI_INSTANCE:
            GUI_INSTANCE.gui_end_visual_combat()
        return self.player.is_alive()

    def play_turn(self):
        clear_screen()
        print_header(f"第 {self.turn} 回合")
        print_info(f"[玩家] {self.player.name} Lv.{self.player.level}")
        print_info(f"生命: {self.player.hp}/{self.player.max_hp}  精神力: {self.player.mp}/{self.player.max_mp}")
        
        alive_teammates = [t for t in self.player.teammates if t.is_alive()]
        for t in alive_teammates:
            print_info(f"[队友] {t.name} 生命: {t.hp}/{t.max_hp}")
            t.is_defending = False
            
        if self.pet_actor and self.pet_actor.is_alive():
            print_info(f"[灵宠] {self.pet_actor.name} 生命: {self.pet_actor.hp}/{self.pet_actor.max_hp}")
            self.pet_actor.is_defending = False

        print("-" * 30)
        
        alive_enemies = [e for e in self.enemies if e.is_alive()]
        for idx, e in enumerate(alive_enemies):
            print_warning(f"[{idx+1}] {e.name}  生命: {e.hp}/{e.max_hp}")
        
        print("-" * 30)
        
        actors = []
        if self.player.is_alive():
            self.player.is_defending = False
            actors.append((self.player, self.player.agi))
        for t in alive_teammates:
            actors.append((t, getattr(t, 'agi', 10)))
        if self.pet_actor and self.pet_actor.is_alive():
            actors.append((self.pet_actor, self.pet_actor.speed))

        for e in alive_enemies:
            e.is_defending = False
            actors.append((e, e.speed))
            
        actors.sort(key=lambda x: x[1], reverse=True)
        escaped = False
        
        for actor, speed in actors:
            if not actor.is_alive():
                continue
                
            if not self.player.is_alive() or not any(e.is_alive() for e in self.enemies):
                break

            # 状态异常结算
            skip_turn = False
            for s in actor.status:
                if s["name"] == "中毒":
                    dmg = s["power"]
                    actor.hp = max(0, actor.hp - dmg)
                    if GUI_INSTANCE:
                        GUI_INSTANCE.gui_combat_event({"type": "status_tick", "target": actor.actor_id, "text": f"毒-{dmg}", "color": "purple"})
                    print_warning(f"🤢 {actor.name} 受到中毒伤害 {dmg} 点！")
                elif s["name"] == "灼烧":
                    dmg = s["power"]
                    actor.hp = max(0, actor.hp - dmg)
                    if GUI_INSTANCE:
                        GUI_INSTANCE.gui_combat_event({"type": "status_tick", "target": actor.actor_id, "text": f"🔥-{dmg}", "color": "orange"})
                    print_warning(f"🔥 {actor.name} 受到灼烧伤害 {dmg} 点！")
                elif s["name"] == "冰冻":
                    skip_turn = True
                    if GUI_INSTANCE:
                        GUI_INSTANCE.gui_combat_event({"type": "status_tick", "target": actor.actor_id, "text": "冻结!", "color": "cyan"})
                    print_warning(f"❄️ {actor.name} 被冰冻了，无法行动！")

            actor.process_status()
            time.sleep(0.2)

            # Check for Revive Logic if target dies from poison/burn
            if not self.player.is_alive():
                has_revive = False
                for item in self.player.inventory:
                    if getattr(item, 'get', lambda x: None)("effect") == "revive":
                        has_revive = True
                        self.player.inventory.remove(item)
                        break
                if has_revive:
                    revive_hp = int(self.player.max_hp * 0.3)
                    self.player.hp = revive_hp
                    if GUI_INSTANCE:
                        GUI_INSTANCE.gui_combat_event({"type": "heal", "target": self.player.actor_id, "amount": revive_hp, "hp": self.player.hp})
                        GUI_INSTANCE.gui_combat_event({"type": "text", "target": self.player.actor_id, "text": "复活!", "color": "yellow"})
                    print_success("🌟 你的生命值归零！但【复活十字章】散发出耀眼的光芒，将你从死亡边缘拉了回来！")

            if not actor.is_alive() or skip_turn:
                continue

            if not self.player.is_alive() or not any(e.is_alive() for e in self.enemies):
                break
                
            if actor == self.player:
                escaped = self.handle_player_action(alive_enemies)
                if escaped:
                    break
            elif actor in self.player.teammates:
                alive_enemies_cur = [e for e in self.enemies if e.is_alive()]
                if alive_enemies_cur:
                    target = random.choice(alive_enemies_cur)
                    self.teammate_attack(actor, target)
            elif self.pet_actor and actor == self.pet_actor:
                alive_enemies_cur = [e for e in self.enemies if e.is_alive()]
                if alive_enemies_cur:
                    target = random.choice(alive_enemies_cur)
                    self.pet_attack(actor, target)
            elif actor in self.enemies:
                possible_targets = [self.player] if self.player.is_alive() else []
                possible_targets.extend([t for t in self.player.teammates if t.is_alive()])
                if self.pet_actor and self.pet_actor.is_alive():
                    possible_targets.append(self.pet_actor)
                if possible_targets:
                    target = random.choice(possible_targets)
                    self.enemy_attack(actor, target)
                    
        self.turn += 1

    def handle_player_action(self, alive_enemies) -> bool:
        options = {
            "1": "普通攻击 (造成100%伤害)",
            "2": "强力攻击 (消耗20精神力，造成150%伤害)",
            "3": "技能释放",
            "4": "防御姿态 (减少50%伤害)",
            "5": "使用道具",
            "6": "逃跑 (成功率与敏捷相关)"
        }
        
        action_taken = False
        escaped = False
        
        while not action_taken:
            choice = show_menu("【你的回合】 战斗选项", options)
            if choice == "1":
                target = self.choose_target(alive_enemies)
                if target:
                    self.player_attack(target, multiplier=1.0)
                    action_taken = True
            elif choice == "2":
                if self.player.mp >= 20:
                    target = self.choose_target(alive_enemies)
                    if target:
                        self.player.mp -= 20
                        self.player_attack(target, multiplier=1.5)
                        action_taken = True
                else:
                    print_error("精神力不足！")
                    time.sleep(1)
            elif choice == "3":
                active_skills = [s for s in self.player.skills if s.get("type") == "active"]
                if not active_skills:
                    print_error("你还没有学习任何主动技能！")
                    time.sleep(1)
                else:
                    skill_options = {str(i+1): f"{s['name']} (耗蓝:{s['mp_cost']} - {s['desc']})" for i, s in enumerate(active_skills)}
                    skill_options["0"] = "返回"
                    s_choice = show_menu("选择技能", skill_options)
                    if s_choice == "0":
                        continue
                    try:
                        s_idx = int(s_choice) - 1
                        if 0 <= s_idx < len(active_skills):
                            skill = active_skills[s_idx]
                            if self.player.mp >= skill['mp_cost']:
                                target = self.choose_target(alive_enemies) if skill.get("effect") != "heal_100" else self.player
                                if target:
                                    self.player.mp -= skill['mp_cost']
                                    self.use_skill(skill, target)
                                    action_taken = True
                            else:
                                print_error("精神力不足！")
                                time.sleep(1)
                    except ValueError:
                        pass
            elif choice == "4":
                self.player.is_defending = True
                print_info(f"{self.player.name} 采取了防御姿态！")
                time.sleep(1)
                action_taken = True
            elif choice == "5":
                if not self.player.inventory:
                    print_error("背包是空的！")
                    time.sleep(1)
                else:
                    inv_options = {str(i+1): f"{item['name']} - {item['desc']}" for i, item in enumerate(self.player.inventory)}
                    inv_options["0"] = "返回"
                    i_choice = show_menu("选择道具", inv_options)
                    if i_choice == "0":
                        continue
                    try:
                        i_idx = int(i_choice) - 1
                        if 0 <= i_idx < len(self.player.inventory):
                            item = self.player.inventory.pop(i_idx)
                            print_success(f"使用了 {item['name']}!")
                            if "heal" in item:
                                self.player.heal(item["heal"])
                            if "mp_restore" in item:
                                self.player.restore_mp(item["mp_restore"])
                            time.sleep(1)
                            action_taken = True
                    except ValueError:
                        pass
            elif choice == "6":
                escape_chance = min(0.8, self.player.agi * 0.05)
                if random.random() < escape_chance:
                    print_success("逃跑成功！")
                    for e in self.enemies: e.hp = 0 
                    escaped = True
                else:
                    print_error("逃跑失败！")
                time.sleep(1)
                action_taken = True
                
        return escaped

    def choose_target(self, alive_enemies):
        if len(alive_enemies) == 1:
            return alive_enemies[0]
            
        opt = {}
        for i, e in enumerate(alive_enemies):
            opt[str(i+1)] = f"{e.name} (HP: {e.hp}/{e.max_hp})"
        opt["0"] = "返回"
        
        while True:
            c = show_menu("选择目标", opt)
            if c == "0": return None
            try:
                idx = int(c) - 1
                if 0 <= idx < len(alive_enemies):
                    return alive_enemies[idx]
            except ValueError:
                pass

    def teammate_attack(self, teammate, target):
        if GUI_INSTANCE:
            GUI_INSTANCE.gui_combat_event({"type": "attack", "attacker": teammate.actor_id, "target": target.actor_id})
            time.sleep(0.5)
            
        if random.random() < calc_dodge_chance(teammate, target):
            if GUI_INSTANCE:
                GUI_INSTANCE.gui_combat_event({"type": "text", "target": target.actor_id, "text": "闪避!", "color": "cyan"})
            print_info(f"未命中！{target.name} 闪避了 {teammate.name} 的攻击。")
            time.sleep(0.3)
            return

        base_dmg = float(teammate.attack)
        is_crit = random.random() < float(getattr(teammate, 'crit_rate', 0.05))
        if is_crit:
            base_dmg = float(base_dmg) * 1.5
            print_warning(f"⚡ {teammate.name} 暴击！ ⚡")
            
        dmg_dealt = target.take_damage(int(base_dmg))
        
        if GUI_INSTANCE:
            GUI_INSTANCE.gui_combat_event({
                "type": "hit", "target": target.actor_id, "damage": dmg_dealt, 
                "hp": target.hp, "crit": is_crit, "color": "white"
            })
            
        print_success(f"{teammate.name} 对 {target.name} 造成了 {dmg_dealt} 点伤害！")

        # Boss Phase 2 Check
        if hasattr(target, 'max_hp') and target.max_hp >= 1000 and "首领" in getattr(target, 'name', '') and target.hp > 0 and target.hp <= target.max_hp * 0.5 and not getattr(target, 'phase2_triggered', False):
            target.phase2_triggered = True
            target.attack = int(target.attack * 1.5)
            target.speed += 10
            target.status = [] # Clear negative statuses
            if GUI_INSTANCE:
                GUI_INSTANCE.gui_combat_event({"type": "text", "target": target.actor_id, "text": "狂暴!", "color": "magenta"})
            print_error(f"⚠️ 警告：{target.name} 进入二阶段【狂暴】状态！解除了所有异常，攻击力和速度大幅提升！⚠️")

        time.sleep(0.3)

    def pet_attack(self, pet, target):
        if pet.skill == "heal":
            heal_amt = pet.attack * 2
            self.player.heal(heal_amt)
            if GUI_INSTANCE:
                GUI_INSTANCE.gui_combat_event({"type": "heal", "target": self.player.actor_id, "amount": heal_amt, "hp": self.player.hp})
            print_success(f"💖 {pet.name} 释放了治愈魔法，为你恢复了 {heal_amt} 点生命！")
            time.sleep(0.5)
            return

        if GUI_INSTANCE:
            vfx_color = "white"
            if pet.skill == "fire": vfx_color = "orange"
            elif pet.skill == "laser": vfx_color = "cyan"
            elif pet.skill == "poison": vfx_color = "purple"

            skill_event = {
                "type": "skill",
                "attacker": pet.actor_id,
                "target": target.actor_id,
                "skill_name": "攻击",
                "color": vfx_color,
                "hit_event": None
            }
            GUI_INSTANCE.gui_combat_event(skill_event)
            time.sleep(0.4)

        if random.random() < calc_dodge_chance(pet, target):
            if GUI_INSTANCE:
                GUI_INSTANCE.gui_combat_event({"type": "text", "target": target.actor_id, "text": "闪避!", "color": "cyan"})
            print_info(f"未命中！{target.name} 闪避了 {pet.name} 的攻击。")
            time.sleep(0.3)
            return

        base_dmg = float(pet.attack)
        dmg_dealt = target.take_damage(int(base_dmg))

        if pet.skill == "fire" and random.random() < 0.4:
            target.add_status("灼烧", duration=2, power=pet.attack // 2)
            print_warning(f"🔥 {pet.name} 点燃了 {target.name}！")
        elif pet.skill == "poison" and random.random() < 0.5:
            target.add_status("中毒", duration=3, power=pet.attack // 2)
            print_warning(f"🤢 {pet.name} 让 {target.name} 中毒了！")

        if GUI_INSTANCE:
            GUI_INSTANCE.gui_combat_event({
                "type": "hit", "target": target.actor_id, "damage": dmg_dealt,
                "hp": target.hp, "crit": False, "color": "white"
            })

        print_success(f"🐾 {pet.name} 攻击了 {target.name}，造成了 {dmg_dealt} 点伤害！")

        # Boss Phase 2 Check
        if hasattr(target, 'max_hp') and target.max_hp >= 1000 and "首领" in getattr(target, 'name', '') and target.hp > 0 and target.hp <= target.max_hp * 0.5 and not getattr(target, 'phase2_triggered', False):
            target.phase2_triggered = True
            target.attack = int(target.attack * 1.5)
            target.speed += 10
            target.status = [] # Clear negative statuses
            if GUI_INSTANCE:
                GUI_INSTANCE.gui_combat_event({"type": "text", "target": target.actor_id, "text": "狂暴!", "color": "magenta"})
            print_error(f"⚠️ 警告：{target.name} 进入二阶段【狂暴】状态！解除了所有异常，攻击力和速度大幅提升！⚠️")

        time.sleep(0.4)

    def use_skill(self, skill, target):
        print_info(f"{self.player.name} 释放技能：【{skill['name']}】！")
        time.sleep(0.2)
        if GUI_INSTANCE:
            vfx_color = "orange" # default fireball color
            if "冰" in skill['name'] or "霜" in skill['name']:
                vfx_color = "cyan"
            elif "剑" in skill['name'] or "斩" in skill['name']:
                vfx_color = "white"
            elif "毒" in skill['name']:
                vfx_color = "purple"
                
            skill_event = {
                "type": "skill", 
                "attacker": self.player.actor_id, 
                "target": target.actor_id,
                "skill_name": skill['name'], 
                "color": vfx_color,
                "hit_event": None
            }
            
        if skill["effect"] in ["dmg_fire", "aoe_meteor", "dmg_fire_dot"]:
            target.add_status("灼烧", duration=3, power=int(self.player.total_int * 0.5))
            print_warning(f"🔥 {target.name} 被技能点燃了！")
        elif skill["effect"] == "dmg_ice":
            if random.random() < 0.4:
                target.add_status("冰冻", duration=1, power=0)
                print_warning(f"❄️ {target.name} 被技能冻结了！")
        elif skill["effect"] == "dmg_poison_dot":
            target.add_status("中毒", duration=4, power=int(self.player.total_int * 0.8))
            print_warning(f"🤢 {target.name} 被技能施加了剧毒！")

        if skill["effect"] == "atk_up":
            if GUI_INSTANCE:
                GUI_INSTANCE.gui_combat_event(skill_event)
                time.sleep(0.4)
            self.player_attack(target, multiplier=2.0)
        elif skill["effect"] == "heal_100":
            target.heal(100)
            if GUI_INSTANCE:
                GUI_INSTANCE.gui_combat_event({"type": "heal", "target": target.actor_id, "amount": 100, "hp": target.hp})
            print_success(f"{target.name} 恢复了 100 点生命值！当前生命: {target.hp}/{target.max_hp}")
            time.sleep(0.5)
        else:
            if GUI_INSTANCE:
                skill_event["hit_event"] = {"type": "text", "text": "击中!", "color": "red"}
                GUI_INSTANCE.gui_combat_event(skill_event)
                time.sleep(0.5)
            self.player_attack(target, multiplier=1.5)

    def player_attack(self, target, multiplier=1.0):
        if GUI_INSTANCE:
            GUI_INSTANCE.gui_combat_event({"type": "attack", "attacker": self.player.actor_id, "target": target.actor_id})
            time.sleep(0.5)
            
        if random.random() < calc_dodge_chance(self.player, target):
            if GUI_INSTANCE:
                GUI_INSTANCE.gui_combat_event({"type": "text", "target": target.actor_id, "text": "闪避!", "color": "cyan"})
            print_info(f"未命中！{target.name} 闪避了你的攻击。")
            time.sleep(0.4)
            return

        base_dmg = float(self.player.attack) * float(multiplier)
        is_crit = random.random() < float(self.player.crit_rate)

        # Calculate crit damage multiplier from effects
        crit_dmg_mult = 1.5
        all_effs = get_all_special_effects(self.player)
        for eff in all_effs:
            if eff.get("name") == "暴伤增加":
                crit_dmg_mult += float(eff.get("value", 0)) / 100.0

        if is_crit:
            base_dmg = float(base_dmg) * crit_dmg_mult
            print_warning("⚡ 暴击！ ⚡")
            
        fire_dmg = 0
        frost_dmg = 0
        leech_pct = 0
        true_dmg = 0

        poison_power = 0
        for eff in all_effs:
            if eff.get("name") == "火焰附加": fire_dmg += int(eff.get("value", 0))
            elif eff.get("name") == "寒冰附加": frost_dmg += int(eff.get("value", 0))
            elif eff.get("name") == "剧毒蔓延": poison_power += int(eff.get("value", 0))
            elif eff.get("name") == "真实伤害": true_dmg += int(eff.get("value", 0))
            elif eff.get("name") == "生命吸取" or eff.get("name") == "吸血": leech_pct += int(eff.get("value", 0))
                    
        total_dmg = int(float(base_dmg) + float(fire_dmg) + float(frost_dmg))
        dmg_dealt = target.take_damage(total_dmg)
        
        # Apply Status Ailments
        if fire_dmg > 0 and random.random() < 0.3:
            target.add_status("灼烧", duration=3, power=fire_dmg)
            print_warning(f"🔥 {target.name} 被点燃了！")
        if frost_dmg > 0 and random.random() < 0.2:
            target.add_status("冰冻", duration=1, power=0)
            print_warning(f"❄️ {target.name} 被冻结了！")
        if poison_power > 0 and random.random() < 0.5:
            target.add_status("中毒", duration=4, power=poison_power)
            print_warning(f"🤢 {target.name} 中毒了！")

        # Add true damage after armor reduction
        if true_dmg > 0:
            target.hp = max(0, target.hp - true_dmg)
            dmg_dealt += true_dmg

        if GUI_INSTANCE:
            GUI_INSTANCE.gui_combat_event({
                "type": "hit", "target": target.actor_id, "damage": dmg_dealt, 
                "hp": target.hp, "crit": is_crit, "color": "white"
            })
            if fire_dmg > 0:
                GUI_INSTANCE.gui_combat_event({"type": "text", "target": target.actor_id, "text": f"🔥+{fire_dmg}", "color": "orange"})
            if frost_dmg > 0:
                GUI_INSTANCE.gui_combat_event({"type": "text", "target": target.actor_id, "text": f"❄️+{frost_dmg}", "color": "cyan"})
            if true_dmg > 0:
                GUI_INSTANCE.gui_combat_event({"type": "text", "target": target.actor_id, "text": f"⚔️+{true_dmg}", "color": "yellow"})
        
        msg = f"你对 {target.name} 造成了 {dmg_dealt} 点总伤害！"
        if fire_dmg > 0: msg += f" (🔥火焰+{fire_dmg})"
        if frost_dmg > 0: msg += f" (❄️寒冰+{frost_dmg})"
        if true_dmg > 0: msg += f" (⚔️真实+{true_dmg})"
        print_success(msg)

        # Boss Phase 2 Check
        if hasattr(target, 'max_hp') and target.max_hp >= 1000 and "首领" in getattr(target, 'name', '') and target.hp > 0 and target.hp <= target.max_hp * 0.5 and not getattr(target, 'phase2_triggered', False):
            target.phase2_triggered = True
            target.attack = int(target.attack * 1.5)
            target.speed += 10
            target.status = [] # Clear negative statuses
            if GUI_INSTANCE:
                GUI_INSTANCE.gui_combat_event({"type": "text", "target": target.actor_id, "text": "狂暴!", "color": "magenta"})
            print_error(f"⚠️ 警告：{target.name} 进入二阶段【狂暴】状态！解除了所有异常，攻击力和速度大幅提升！⚠️")
        
        if leech_pct > 0:
            heal_amt = max(1, int(dmg_dealt * (leech_pct / 100.0)))
            self.player.heal(heal_amt)
            if GUI_INSTANCE:
                GUI_INSTANCE.gui_combat_event({"type": "heal", "target": self.player.actor_id, "amount": heal_amt, "hp": self.player.hp})
            print_success(f"🦇 你的武器汲取了 {heal_amt} 点生命！")
            
        time.sleep(0.4)
        
    def enemy_attack(self, enemy, target):
        if GUI_INSTANCE:
            GUI_INSTANCE.gui_combat_event({"type": "attack", "attacker": enemy.actor_id, "target": target.actor_id})
            time.sleep(0.5)

        is_defending = getattr(target, 'is_defending', False)

        if not is_defending and random.random() < calc_dodge_chance(enemy, target):
            if GUI_INSTANCE:
                GUI_INSTANCE.gui_combat_event({"type": "text", "target": target.actor_id, "text": "闪避!", "color": "cyan"})
            print_success(f"漂亮！{target.name} 闪避了 {enemy.name} 的攻击。")
            time.sleep(0.4)
            return

        base_dmg = float(enemy.attack)
        if is_defending:
            base_dmg = float(base_dmg) * 0.5
            
        dmg_dealt = target.take_damage(int(base_dmg))
        
        # Check for damage reflection
        thorns_dmg = 0
        if target == self.player:
            all_effs = get_all_special_effects(self.player)
            for eff in all_effs:
                if eff.get("name") == "伤害反射":
                    thorns_pct = int(eff.get("value", 0))
                    thorns_dmg += max(1, int(dmg_dealt * (thorns_pct / 100.0)))

        if GUI_INSTANCE:
            GUI_INSTANCE.gui_combat_event({
                "type": "hit", "target": target.actor_id, "damage": dmg_dealt, 
                "hp": target.hp, "crit": False, "color": "red"
            })
            
        print_error(f"{enemy.name} 攻击了 {target.name}，造成了 {dmg_dealt} 点伤害！")

        if thorns_dmg > 0:
            enemy.take_damage(thorns_dmg)
            if GUI_INSTANCE:
                GUI_INSTANCE.gui_combat_event({"type": "hit", "target": enemy.actor_id, "damage": thorns_dmg, "hp": enemy.hp, "crit": False, "color": "magenta"})
            print_warning(f"🛡️ 伤害反射！{enemy.name} 受到了 {thorns_dmg} 点反弹伤害！")

        # Boss Phase 2 Check (triggered if they hurt themselves via thorns)
        if hasattr(enemy, 'max_hp') and enemy.max_hp >= 1000 and "首领" in getattr(enemy, 'name', '') and enemy.hp > 0 and enemy.hp <= enemy.max_hp * 0.5 and not getattr(enemy, 'phase2_triggered', False):
            enemy.phase2_triggered = True
            enemy.attack = int(enemy.attack * 1.5)
            enemy.speed += 10
            enemy.status = [] # Clear negative statuses
            if GUI_INSTANCE:
                GUI_INSTANCE.gui_combat_event({"type": "text", "target": enemy.actor_id, "text": "狂暴!", "color": "magenta"})
                GUI_INSTANCE.gui_combat_event({"type": "heal", "target": enemy.actor_id, "amount": 0, "hp": enemy.hp}) # Trigger particle effect
            print_error(f"⚠️ 警告：{enemy.name} 进入二阶段【狂暴】状态！解除了所有异常，攻击力和速度大幅提升！⚠️")

        # Check for Revive Logic if target dies
        if target == self.player and not self.player.is_alive():
            has_revive = False
            for item in self.player.inventory:
                if getattr(item, 'get', lambda x: None)("effect") == "revive":
                    has_revive = True
                    self.player.inventory.remove(item)
                    break
            if has_revive:
                revive_hp = int(self.player.max_hp * 0.3)
                self.player.hp = revive_hp
                if GUI_INSTANCE:
                    GUI_INSTANCE.gui_combat_event({"type": "heal", "target": self.player.actor_id, "amount": revive_hp, "hp": self.player.hp})
                    GUI_INSTANCE.gui_combat_event({"type": "text", "target": self.player.actor_id, "text": "复活!", "color": "yellow"})
                print_success("🌟 你的生命值归零！但【复活十字章】散发出耀眼的光芒，将你从死亡边缘拉了回来！")

        time.sleep(0.4)
