import tkinter as tk
import math
import random
from typing import Optional

class Stickman:
    def __init__(self, canvas, x, y, color="white", direction=1):
        self.canvas = canvas
        self.base_x = x
        self.base_y = y
        self.x = x
        self.y = y
        self.color = color
        self.dir = direction # 1 facing right, -1 facing left
        self.scale = 2.0
        
        self.hp = 100
        self.max_hp = 100
        self.name = ""
        self.actor_id = ""
        
        self.head = None
        self.body = None
        self.arm_l = None
        self.arm_r = None
        self.leg_l = None
        self.leg_r = None
        self.weapon = None
        
        # Animations
        self.state = "idle" # idle, attack, hit, dead
        self.tick = 0
        self.state_tick = 0
        self.action_duration = 20
        
        self.hp_text = None
        self.hp_bar_bg = None
        self.hp_bar_fg = None
        self.name_text = None
        
        self.draw()
        
    def draw(self):
        s = self.scale
        
        # Create shapes if not exist
        if not self.head:
            self.head = self.canvas.create_oval(0, 0, 0, 0, outline=self.color, width=2*s)
            self.body = self.canvas.create_line(0, 0, 0, 0, fill=self.color, width=2*s)
            self.arm_l = self.canvas.create_line(0, 0, 0, 0, fill=self.color, width=2*s)
            self.arm_r = self.canvas.create_line(0, 0, 0, 0, fill=self.color, width=2*s)
            self.leg_l = self.canvas.create_line(0, 0, 0, 0, fill=self.color, width=2*s)
            self.leg_r = self.canvas.create_line(0, 0, 0, 0, fill=self.color, width=2*s)
            self.weapon = self.canvas.create_line(0, 0, 0, 0, fill="#FFD700", width=2*s)
            
            self.hp_bar_bg = self.canvas.create_rectangle(0,0,0,0, fill="#222", outline="")
            self.hp_bar_fg = self.canvas.create_rectangle(0,0,0,0, fill="#10b981", outline="")
            self.name_text = self.canvas.create_text(0,0, text=self.name, fill="white", font=("Microsoft YaHei", 12, "bold"))
            self.hp_text = self.canvas.create_text(0,0, text="", fill="white", font=("Consolas", 10, "bold"))
            
        self.update_pose()
        
    def update_pose(self):
        s = self.scale
        d = self.dir
        
        # Idle animation using sin
        breath_y = math.sin(self.tick * 0.1) * 2 * s if self.state == "idle" else 0
        
        # Calculate joints
        head_r = 10 * s
        hx, hy = self.x, self.y - 30 * s + breath_y
        
        bx1, by1 = hx, hy + head_r
        bx2, by2 = hx, hy + head_r + 25 * s
        
        # Arms
        arm_ang = math.sin(self.tick * 0.15) * 0.2 if self.state == "idle" else 0
        
        if self.state == "attack":
            # attack animation
            progress = self.state_tick / float(self.action_duration) # 0 to 1
            if progress < 0.5:
                # winding up & moving forward
                self.x = self.base_x + d * (progress * 2) * 60 * s
                arm_ang = -1.5 * (progress * 2)
            else:
                # striking & moving back
                self.x = self.base_x + d * (1 - (progress-0.5)*2) * 60 * s
                arm_ang = 2.0 * (progress - 0.5) * 2 - 1.5
                
        elif self.state == "hit":
            self.x = self.base_x - d * 5 * s + random.randint(-4, 4)
            hy += random.randint(-2, 2)
            
        elif self.state == "dodge":
            progress = self.state_tick / float(self.action_duration)
            if progress < 0.5:
                # lean back quickly
                self.x = self.base_x - d * (progress * 2) * 20 * s
                arm_ang = 0.5
            else:
                # recover
                self.x = self.base_x - d * (1 - (progress - 0.5) * 2) * 20 * s
                arm_ang = 0.2
            
        elif self.state == "dead":
            self.x = self.base_x
            hy += 35 * s # fall down
            by1 += 35 * s
            by2 += 35 * s
            arm_ang = math.pi / 2
        else:
            self.x = self.base_x

        shoulder_y = by1 + 5 * s
        
        # Left Arm (Back)
        alx, aly = hx - d*3*s, shoulder_y
        alx2, aly2 = alx + math.cos(math.pi/2 + arm_ang) * 15 * s, aly + math.sin(math.pi/2 + arm_ang) * 15 * s
        
        # Right Arm (Front)
        arx, ary = hx + d*3*s, shoulder_y
        arx2, ary2 = arx + math.cos(math.pi/2 - arm_ang*d) * 15 * s, ary + math.sin(math.pi/2 - arm_ang*d) * 15 * s
        
        # Legs
        leg_ang = math.sin(self.tick * 0.1) * 0.1 if self.state == "idle" else 0
        if self.state == "dead":
            leg_ang = math.pi/2
            
        llx, lly = bx2, by2
        llx2, lly2 = llx - d*8*s + math.cos(leg_ang)*10*s, lly + 20*s + math.sin(leg_ang)*10*s
        
        lrx, lry = bx2, by2
        lrx2, lry2 = lrx + d*8*s + math.cos(leg_ang)*10*s, lry + 20*s + math.sin(leg_ang)*10*s
        
        # Update canvas coords
        self.canvas.coords(self.head, hx - head_r, hy - head_r, hx + head_r, hy + head_r)
        self.canvas.coords(self.body, bx1, by1, bx2, by2)
        self.canvas.coords(self.arm_l, alx, aly, alx2, aly2)
        self.canvas.coords(self.arm_r, arx, ary, arx2, ary2)
        self.canvas.coords(self.leg_l, llx, lly, llx2, lly2)
        self.canvas.coords(self.leg_r, lrx, lry, lrx2, lry2)
        
        # Weapon attached to right arm
        wx1, wy1 = arx2, ary2
        # Extend weapon outwards
        wood_ang = arm_ang if d == 1 else -arm_ang
        wx2, wy2 = wx1 + d * math.cos(wood_ang)*25*s, wy1 - math.sin(wood_ang)*25*s
        if self.state == "dead":
            wx1, wy1 = self.base_x + d*20*s, self.base_y + 40*s
            wx2, wy2 = wx1 + 25*s, wy1
        self.canvas.coords(self.weapon, wx1, wy1, wx2, wy2)
        
        # UI - Moved above head instead of below
        bar_w = 40 * s
        bar_h = 4 * s
        bar_x = self.base_x - bar_w/2
        bar_y = self.base_y - 100 * s # Higher up
        
        # Color based on HP percentage
        hp_pct = max(0.0, float(self.hp) / max(1.0, float(self.max_hp)))
        bar_color = "#10b981" # Green
        if hp_pct < 0.3: bar_color = "#ef4444" # Red
        elif hp_pct < 0.6: bar_color = "#f59e0b" # Orange
            
        self.canvas.coords(self.hp_bar_bg, bar_x, bar_y, bar_x + bar_w, bar_y + bar_h)
        self.canvas.itemconfigure(self.hp_bar_fg, fill=bar_color)
        self.canvas.coords(self.hp_bar_fg, bar_x, bar_y, bar_x + bar_w * hp_pct, bar_y + bar_h)
        
        self.canvas.coords(self.name_text, self.base_x, bar_y - 12 * s)
        self.canvas.itemconfigure(self.name_text, text=self.name)
        self.canvas.coords(self.hp_text, self.base_x, bar_y + 10 * s)
        self.canvas.itemconfigure(self.hp_text, text=f"{int(self.hp)}/{int(self.max_hp)}")
        
    def set_action(self, state, duration_ticks=20):
        if self.hp <= 0 and state != "dead":
            return
        self.state = state
        self.state_tick = 0
        self.action_duration = duration_ticks

    def step(self):
        self.tick += 1
        if self.state != "idle" and self.state != "dead":
            self.state_tick += 1
            if self.state_tick >= self.action_duration:
                if self.hp <= 0:
                    self.state = "dead"
                else:
                    self.state = "idle"
        self.update_pose()

    def update_hp(self, hp, max_hp):
        self.hp = hp
        self.max_hp = max_hp
        if self.hp <= 0:
            self.set_action("dead")

    def delete(self):
        for item in [self.head, self.body, self.arm_l, self.arm_r, self.leg_l, self.leg_r, self.weapon, self.hp_bar_bg, self.hp_bar_fg, self.name_text, self.hp_text]:
            if item:
                self.canvas.delete(item)

class FloatingText:
    def __init__(self, canvas, x, y, text, color="red", size=16, is_crit=False):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.color = color
        
        font_weight = "bold"
        if is_crit:
            size += 8
            self.color = "#fbbf24" # Intense Yellow
            
        self.id = self.canvas.create_text(x, y, text=text, fill=self.color, font=("Microsoft YaHei", size, font_weight))
        self.tick = 0
        self.life = 50 if is_crit else 35
        self.vy = -3 if is_crit else -2
        
    def step(self):
        self.tick += 1
        self.y += self.vy
        self.vy *= 0.9 # decelerate
        
        self.canvas.coords(self.id, self.x, self.y)
        return self.tick >= self.life
        
    def delete(self):
        self.canvas.delete(self.id)

class Projectile:
    def __init__(self, canvas, start_x, start_y, target_x, target_y, color, speed, on_hit_callback=None):
        self.canvas = canvas
        self.x = start_x
        self.y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = speed
        self.color = color
        self.on_hit = on_hit_callback
        
        # Determine direction vector
        dx = target_x - start_x
        dy = target_y - start_y
        dist = math.hypot(dx, dy)
        if dist == 0:
            self.vx = 0
            self.vy = 0
        else:
            self.vx = (dx / dist) * speed
            self.vy = (dy / dist) * speed
            
        r = 8
        self.id = self.canvas.create_oval(self.x-r, self.y-r, self.x+r, self.y+r, fill=self.color, outline="white")
        self.active = True
        
    def step(self):
        if not self.active: return True
        self.x += self.vx
        self.y += self.vy
        self.canvas.coords(self.id, self.x-8, self.y-8, self.x+8, self.y+8)
        
        # Check collision with target
        if math.hypot(self.target_x - self.x, self.target_y - self.y) < self.speed:
            self.active = False
            if self.on_hit:
                self.on_hit(self.target_x, self.target_y)
            return True
        return False
        
    def delete(self):
        self.canvas.delete(self.id)

class ParticleSystem:
    def __init__(self, canvas, x, y, color, count=10, p_type="explosion"):
        self.canvas = canvas
        self.particles = []
        self.type = p_type
        self.tick = 0
        self.life = 20 if p_type == "explosion" else 30
        
        for _ in range(count):
            if p_type == "explosion":
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(2, 8)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
                r = random.uniform(2, 6)
            elif p_type == "heal":
                vx = random.uniform(-1, 1)
                vy = random.uniform(-4, -1)
                r = random.uniform(3, 5)
                color = "#32CD32"
                
            pid = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="")
            self.particles.append({"id": pid, "x": x, "y": y, "vx": vx, "vy": vy, "r": r})
            
    def step(self):
        self.tick += 1
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if self.type == "explosion":
                p["vy"] += 0.5 # Gravity
            self.canvas.coords(p["id"], p["x"]-p["r"], p["y"]-p["r"], p["x"]+p["r"], p["y"]+p["r"])
            
        return self.tick >= self.life
        
    def delete(self):
        for p in self.particles:
            self.canvas.delete(p["id"])

class CombatRenderer:
    def __init__(self, canvas):
        self.canvas = canvas
        self.width = 0
        self.height = 0
        
        self.player_team = []
        self.enemy_team = []
        self.floating_texts = []
        self.projectiles = []
        self.particles = []
        
        # Deferred event queues for staggering animations
        self.event_queue = []
        self.event_timer = 0
        
        self.battle_ended = False
        self.end_banner = None
        self.end_banner_text = None
        
    def get_stick_by_id(self, sid) -> 'Optional[Stickman]':
        for s in self.player_team:
            if getattr(s, 'actor_id', None) == sid: return s
        for s in self.enemy_team:
            if getattr(s, 'actor_id', None) == sid: return s
        # Fallback to names if IDs aren't provided
        for s in self.player_team:
            if s.name == sid: return s
        for s in self.enemy_team:
            if s.name == sid: return s
        return None

    def setup_teams(self, width, height, player_data_list, enemy_data_list):
        self.width = width
        self.height = height
        self.canvas.delete("all")
        
        # Ground line
        self.canvas.create_line(0, height*0.75, width, height*0.75, fill="#444444", width=4)
        
        self.player_team = []
        self.enemy_team = []
        
        cy_base = height * 0.75 - 40
        
        # Player formation (left side)
        for i, pd in enumerate(player_data_list):
            cx = width * 0.4 - (i * 70) # cascade backwards
            s = Stickman(self.canvas, cx, cy_base, color="#00BFFF", direction=1)
            s.name = pd.get("name", "Player")
            s.actor_id = pd.get("id", s.name)
            s.update_hp(pd.get("hp", 100), pd.get("max_hp", 100))
            self.player_team.append(s)
            
        # Enemy formation (right side)
        for i, ed in enumerate(enemy_data_list):
            cx = width * 0.6 + (i * 70)
            s = Stickman(self.canvas, cx, cy_base, color="#FF6347", direction=-1)
            s.name = ed.get("name", "Enemy")
            s.actor_id = ed.get("id", s.name)
            s.update_hp(ed.get("hp", 100), ed.get("max_hp", 100))
            self.enemy_team.append(s)
        
        self.floating_texts = []
        self.projectiles = []
        self.particles = []
        self.event_queue = []
        self.event_timer = 0
        self.battle_ended = False
        self.end_banner = None
        self.end_banner_text = None
        
    def process_event(self, event):
        # We push events to a queue instead of processing immediately 
        # so we can control timing (e.g., wait for projectile to hit before showing damage)
        if event.get("type") in ["attack", "skill", "end_battle", "status_tick"]:
            self.event_queue.append(event)
        else:
            # Immediate resolution for internal events or specific text updates
            self.handle_event(event)
            
    def handle_event(self, event):
        etype = event.get("type")
        attacker = self.get_stick_by_id(event.get("attacker"))
        target = self.get_stick_by_id(event.get("target"))

        if etype == "status_tick" and target:
            target.set_action("hit", 5) # Small flinch
            text = event.get("text", "")
            color = event.get("color", "white")
            self.add_floating_text(target, text, color)

            # Spawn some status particles
            if color == "purple": # Poison
                self.particles.append(ParticleSystem(self.canvas, target.x, target.y - 20, "purple", count=5, p_type="heal"))
            elif color == "orange": # Burn
                self.particles.append(ParticleSystem(self.canvas, target.x, target.y - 20, "orange", count=5, p_type="explosion"))
            elif color == "cyan": # Freeze
                self.particles.append(ParticleSystem(self.canvas, target.x, target.y - 20, "cyan", count=5, p_type="explosion"))

        elif etype == "attack" and attacker:
            attacker.set_action("attack", 20)
        elif etype == "hit" and target:
            target.set_action("hit", 10)
            target.update_hp(event.get("hp", 0), target.max_hp)
            
            dmg = event.get("damage", 0)
            color = event.get("color", "red")
            text = f"-{dmg}"
            is_crit = event.get("crit", False)
            if is_crit:
                text = "⚡暴发 " + text
                color = "orange"
                
            # Add screen shake for heavy damage or crit
            if is_crit or dmg > target.max_hp * 0.2:
                self.particles.append(ParticleSystem(self.canvas, target.x, target.y - 40, "red", count=8, p_type="explosion"))
            
            self.add_floating_text(target, text, color, is_crit)
        elif etype == "skill" and attacker and target:
            attacker.set_action("attack", 30)
            color = event.get("color", "orange")
            
            # create projectile
            def on_projectile_hit(hx, hy):
                self.particles.append(ParticleSystem(self.canvas, hx, hy, color, count=15, p_type="explosion"))
                hit_event = event.get("hit_event")
                if hit_event:
                    self.handle_event(hit_event)
                    
            start_x, start_y = attacker.x + (attacker.dir * 20), attacker.y - 40
            tar_x, tar_y = target.x, target.y - 40
            self.projectiles.append(Projectile(self.canvas, start_x, start_y, tar_x, tar_y, color, speed=15, on_hit_callback=on_projectile_hit))
            self.add_floating_text(attacker, event.get("skill_name", "Skill"), "yellow")

        elif etype == "heal" and target:
            target.update_hp(event.get("hp", 0), target.max_hp)
            amt = event.get("amount", 0)
            self.particles.append(ParticleSystem(self.canvas, target.x, target.y, "#32CD32", count=20, p_type="heal"))
            self.add_floating_text(target, f"+{amt}", "#32CD32")
        elif etype == "text" and target:
            if event.get("text") == "闪避!":
                target.set_action("dodge", 15)
            self.add_floating_text(target, event.get("text", ""), event.get("color", "white"))
        elif etype == "end_battle":
            self.battle_ended = True
            is_victory = event.get("is_victory", True)
            self.draw_battle_result(is_victory)

    def draw_battle_result(self, is_victory):
        w, h = self.width, self.height
        self.end_banner = self.canvas.create_rectangle(0, h/2 - 50, w, h/2 + 50, fill="#111", outline="", stipple="gray50")
        
        text = "🔥 战斗胜利 🔥" if is_victory else "💀 战斗失败 💀"
        color = "#eab308" if is_victory else "#ef4444"
        self.end_banner_text = self.canvas.create_text(w/2, h/2, text=text, fill=color, font=("Microsoft YaHei", 36, "bold"))

    def add_floating_text(self, stick, text, color="red", is_crit=False):
        x = stick.x
        y = stick.y - 150
        x += random.randint(-40, 40)
        y += random.randint(-20, 20)
        self.floating_texts.append(FloatingText(self.canvas, x, y, text, color, is_crit=is_crit))

    def step(self):
        # Process queued events
        if self.event_queue and self.event_timer <= 0:
            next_evt = self.event_queue.pop(0)
            self.handle_event(next_evt)
            # Add delay before next event if needed, e.g. for animations to play out
            if next_evt.get("type") in ["attack", "skill"]:
                self.event_timer = 20 # wait 20 frames before processing next major action
            elif next_evt.get("type") == "status_tick":
                self.event_timer = 10 # wait 10 frames before processing next major action
                
        if self.event_timer > 0:
            self.event_timer -= 1
            
        for p in self.player_team: p.step()
        for e in self.enemy_team: e.step()
        
        active_texts = []
        for ft in self.floating_texts:
            if ft.step():
                ft.delete()
            else:
                active_texts.append(ft)
        self.floating_texts = active_texts
        
        active_projs = []
        for pj in self.projectiles:
            if pj.step():
                pj.delete()
            else:
                active_projs.append(pj)
        self.projectiles = active_projs
        
        active_parts = []
        for pt in self.particles:
            if pt.step():
                pt.delete()
            else:
                active_parts.append(pt)
        self.particles = active_parts
