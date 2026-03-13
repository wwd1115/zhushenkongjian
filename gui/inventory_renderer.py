import tkinter as tk
import math

class InventoryRenderer:
    def __init__(self, canvas):
        self.canvas = canvas
        self.width = 0
        self.height = 0
        self.player_data = None
        
        # Grid settings
        self.grid_cols = 5
        self.cell_size = 50
        self.padding = 10
        self.grid_start_x = 0
        self.grid_start_y = 0
        
        # Colors
        self.colors = {
            "bg": "#111111",
            "panel": "#222222",
            "text": "#E0E0E0",
            "highlight": "#444444",
            "border": "#555555",
            
            # Quality colors
            "普通": "#FFFFFF",
            "稀有": "#00AAFF",
            "史诗": "#AA00FF",
            "传说": "#FFAA00",
            
            # Button
            "btn_bg": "#333333",
            "btn_hover": "#555555"
        }
        
        self.selected_item_index = None
        self.selected_item_type = None # "inventory" or "equipment"
        self.on_action_callback = None
        
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_hover)
        
        self.hovered_element = None
        self.buttons = [] # Store button hitboxes
        self.item_hitboxes = [] # Store item hitboxes
        self.tab_hitboxes = [] # Store tab hitboxes
        
        self.tabs = ["全部", "武器", "防具", "饰品", "道具"]
        self.active_tab = "全部"
        
        # Type mapping
        self.tab_mapping = {
            "全部": ["weapon", "armor", "accessory", "consumable", "material", "quest"],
            "武器": ["weapon"],
            "防具": ["armor"],
            "饰品": ["accessory"],
            "道具": ["consumable", "material", "quest"]
        }
        
    def setup(self, width, height, player_data, on_action_callback):
        self.width = width
        self.height = height
        self.player_data = player_data
        self.on_action_callback = on_action_callback
        self.selected_item_index = None
        self.selected_item_type = None
        self.draw()
        
    def update_data(self, player_data):
        self.player_data = player_data
        self.selected_item_index = None
        self.selected_item_type = None
        self.draw()
        
    def draw(self):
        self.canvas.delete("all")
        if not self.player_data:
            return
            
        # Background
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill=self.colors["bg"], outline="")
        
        # Split screen: Left = Character (40%), Right = Inventory (60%)
        split_x = int(self.width * 0.4)
        
        self.draw_character_sheet(0, 0, split_x, self.height)
        self.draw_inventory_panel(split_x, 0, self.width - split_x, self.height)
        
    def draw_character_sheet(self, x, y, w, h):
        pad = 15
        p = self.player_data
        
        # Panel Background
        self.canvas.create_rectangle(x + pad, y + pad, x + w - pad, y + h - pad, 
                                     fill=self.colors["panel"], outline=self.colors["border"])
                                     
        # Name and Level
        cy = y + pad + 20
        self.canvas.create_text(x + w//2, cy, text=f"{p.get('name', '???')} - Lv.{p.get('level', 1)}", 
                                fill=self.colors["text"], font=("Microsoft YaHei", 16, "bold"))
                                
        # HP / MP
        cy += 30
        hp_text = f"HP: {p.get('hp', 0)} / {p.get('max_hp', 0)}"
        mp_text = f"MP: {p.get('mp', 0)} / {p.get('max_mp', 0)}"
        self.canvas.create_text(x + w//2, cy, text=f"{hp_text}    {mp_text}", 
                                fill="#FF5555", font=("Microsoft YaHei", 12))
                                
        # Attributes
        cy += 30
        attrs = [
            ("力量 (STR)", p.get('str', 0)),
            ("敏捷 (AGI)", p.get('agi', 0)),
            ("智力 (INT)", p.get('int', 0)),
            ("体质 (CON)", p.get('con', 0)),
            ("感知 (PER)", p.get('per', 0)),
            ("魅力 (CHA)", p.get('cha', 0)),
        ]
        
        cx1, cx2 = x + w//4, x + w*3//4
        for i, (name, val) in enumerate(attrs):
            dx = cx1 if i % 2 == 0 else cx2
            dy = cy + (i // 2) * 25
            self.canvas.create_text(dx, dy, text=f"{name}: {val}", 
                                    fill=self.colors["text"], font=("Microsoft YaHei", 11))
                                    
        # Other stats
        cy += 80
        self.canvas.create_text(x + w//2, cy, text=f"当前积分: {p.get('points', 0)}   自由属性点: {p.get('free_stats', 0)}", 
                                fill="#FFFF55", font=("Microsoft YaHei", 12))
                                
        # Equipment Slots
        cy += 40
        self.canvas.create_line(x + pad*2, cy, x + w - pad*2, cy, fill=self.colors["border"])
        cy += 20
        self.canvas.create_text(x + w//2, cy, text="--- 当前装备 ---", fill=self.colors["text"], font=("Microsoft YaHei", 12, "bold"))
        
        cy += 30
        equipments = [
            ("Weapon", "武器", p.get("equipment", {}).get("weapon")),
            ("Armor", "防具", p.get("equipment", {}).get("armor")),
            ("Accessory", "饰品", p.get("equipment", {}).get("accessory")),
            ("Pet", "出战灵宠", p.get("active_pet", None))
        ]
        
        slot_w, slot_h = w - pad*4, 50
        for slot_key, slot_name, item in equipments:
            self._draw_equipment_slot(x + pad*2, cy, slot_w, slot_h, slot_key, slot_name, item)
            cy += slot_h + 10
            
    def _draw_equipment_slot(self, x, y, w, h, slot_key, slot_name, item):
        is_selected = (self.selected_item_type == "equipment" and self.selected_item_index == slot_key)
        bg = self.colors["highlight"] if is_selected else self.colors["btn_bg"]
        outline = self.colors["border"]
        
        if item:
            quality = item.get("quality", "普通")
            outline = self.colors.get(quality, self.colors["border"])
            
        self.canvas.create_rectangle(x, y, x + w, y + h, fill=bg, outline=outline, width=2)
        self.canvas.create_text(x + w//2, y + 10, text=slot_name, fill="#888888", font=("Microsoft YaHei", 9))
        
        if item:
            name = item.get("name", "Unknown")
            lvl = item.get("level", 1)
            self.canvas.create_text(x + w//2, y + h//2 + 5, text=f"Lv.{lvl} {name}", fill=outline, font=("Microsoft YaHei", 11))
        else:
            self.canvas.create_text(x + w//2, y + h//2 + 5, text="[ 空 ]", fill="#555555", font=("Microsoft YaHei", 11))
            
        self.item_hitboxes.append({
            "rect": (x, y, x + w, y + h),
            "type": "equipment",
            "index": slot_key,
            "item": item
        })
        
    def draw_inventory_panel(self, x, y, w, h):
        pad = 15
        # Panel Background
        self.canvas.create_rectangle(x + pad, y + pad, x + w - pad, y + h - pad, 
                                     fill=self.colors["panel"], outline=self.colors["border"])
                                     
        self.canvas.create_text(x + w//2, y + pad + 20, text="--- 背包物品 ---", 
                                fill=self.colors["text"], font=("Microsoft YaHei", 14, "bold"))
                                
        # === Draw Tabs ===
        tab_y = y + pad + 50
        tab_w = (w - pad*4) // len(self.tabs)
        tab_x_start = x + (w - (tab_w * len(self.tabs))) // 2
        
        self.tab_hitboxes = []
        for i, tab_name in enumerate(self.tabs):
            tx = tab_x_start + i * tab_w
            is_active = (self.active_tab == tab_name)
            t_bg = self.colors["highlight"] if is_active else self.colors["panel"]
            t_fg = "#FFFFFF" if is_active else "#888888"
            
            self.canvas.create_rectangle(tx, tab_y, tx + tab_w, tab_y + 30, fill=t_bg, outline=self.colors["border"])
            self.canvas.create_text(tx + tab_w//2, tab_y + 15, text=tab_name, fill=t_fg, font=("Microsoft YaHei", 12))
            self.tab_hitboxes.append({"rect": (tx, tab_y, tx + tab_w, tab_y + 30), "name": tab_name})
                                
        # Available grid area
        grid_width = w - pad*4
        self.cell_size = min(60, grid_width // self.grid_cols)
        
        self.grid_start_x = x + (w - (self.cell_size * self.grid_cols)) // 2
        self.grid_start_y = tab_y + 40
        
        full_inventory = self.player_data.get("inventory", [])
        
        # Filter inventory based on active tab
        allowed_types = self.tab_mapping[self.active_tab]
        filtered_inventory = []
        for i, item in enumerate(full_inventory):
            if item.get("type", "unknown") in allowed_types:
                filtered_inventory.append((i, item)) # Store original index alongside item
        
        self.item_hitboxes = [h_box for h_box in self.item_hitboxes if h_box["type"] != "inventory"]
        
        # Total slots to show (at least 30)
        total_slots = max(30, math.ceil(len(filtered_inventory) / self.grid_cols) * self.grid_cols)
        if total_slots % self.grid_cols != 0:
            total_slots += self.grid_cols - (total_slots % self.grid_cols)
            
        for idx in range(total_slots):
            row = idx // self.grid_cols
            col = idx % self.grid_cols
            
            cx = self.grid_start_x + col * self.cell_size
            cy = self.grid_start_y + row * self.cell_size
            
            if idx < len(filtered_inventory):
                orig_index, item = filtered_inventory[idx]
            else:
                orig_index, item = None, None
                
            is_selected = (self.selected_item_type == "inventory" and self.selected_item_index == orig_index)
            
            bg = self.colors["highlight"] if is_selected else self.colors["bg"]
            outline = self.colors["border"]
            
            if item:
                quality = item.get("quality", "普通")
                outline = self.colors.get(quality, self.colors["border"])
                
            line_width = 2 if item else 1
            if is_selected:
                line_width = 3
                
            self.canvas.create_rectangle(cx + 2, cy + 2, cx + self.cell_size - 2, cy + self.cell_size - 2, 
                                         fill=bg, outline=outline, width=line_width)
                                         
            if item:
                # Icon shorthand
                name = item.get("name", "X")
                short_name = name[0] # First char
                self.canvas.create_text(cx + self.cell_size//2, cy + self.cell_size//2, 
                                        text=short_name, fill=outline, font=("Microsoft YaHei", 14, "bold"))
                                        
                self.item_hitboxes.append({
                    "rect": (cx + 2, cy + 2, cx + self.cell_size - 2, cy + self.cell_size - 2),
                    "type": "inventory",
                    "index": orig_index,
                    "item": item
                })
                
        # Draw details panel if an item is selected
        self._draw_details_panel(x + pad, y + h - 180, w - pad*2, 160)
        
    def _draw_details_panel(self, x, y, w, h):
        self.canvas.create_rectangle(x, y, x + w, y + h, fill="#1A1A1A", outline=self.colors["border"])
        self.buttons = []
        
        selected_item = None
        if self.selected_item_type == "equipment":
            selected_item = self.player_data.get("equipment", {}).get(self.selected_item_index)
        elif self.selected_item_type == "inventory":
            inventory = self.player_data.get("inventory", [])
            if self.selected_item_index is not None and self.selected_item_index < len(inventory):
                selected_item = inventory[self.selected_item_index]
                
        if not selected_item:
            self.canvas.create_text(x + w//2, y + h//2, text="点击物品查看详情", fill="#666666", font=("Microsoft YaHei", 12))
            return
            
        quality = selected_item.get("quality", "普通")
        color = self.colors.get(quality, self.colors["text"])
        
        name = selected_item.get("name", "Unknown")
        lvl = selected_item.get("level", 1)
        itype = selected_item.get("type", "unknown")
        req_lvl = selected_item.get("level_req", 1)
        
        # Item Header
        self.canvas.create_text(x + 15, y + 10, text=f"[{quality}] {name} (Lv.{lvl}) [需求等级: {req_lvl}]", fill=color, font=("Microsoft YaHei", 14, "bold"), anchor="nw", width=w-30)
        self.canvas.create_text(x + 15, y + 35, text=f"类型: {itype}", fill="#888888", font=("Microsoft YaHei", 10), anchor="nw")
        
        # Stats desc
        st = selected_item.get('stats', {})
        
        stat_items = []
        if selected_item.get("attack", 0) > 0: stat_items.append(f"攻击力: {selected_item['attack']}")
        if selected_item.get("defense", 0) > 0: stat_items.append(f"防御力: {selected_item['defense']}")
        if selected_item.get("heal", 0) > 0: stat_items.append(f"生命恢复: {selected_item['heal']}")
        
        stat_names = {"str": "力量", "agi": "敏捷", "int": "智力", "con": "体质", "per": "感知", "cha": "魅力"}
        for k, v in st.items():
            if v != 0:
                name = stat_names.get(k, k.upper())
                stat_items.append(f"{name}: +{v}")
                
        # Draw stats in a 2-column grid
        sy = y + 55
        col1_x = x + 15
        col2_x = x + w//2 + 5
        
        for i, text in enumerate(stat_items):
            cx = col1_x if i % 2 == 0 else col2_x
            cy = sy + (i // 2) * 20
            self.canvas.create_text(cx, cy, text=f"✧ {text}", fill="#00e5ff", font=("Microsoft YaHei", 10), anchor="nw")
        
        # Buttons
        btn_y = y + h - 45
        if self.selected_item_type == "inventory":
            if itype in ["weapon", "armor", "accessory"]:
                self._draw_button(x + 15, btn_y, 80, 30, "装备", f"equip_{self.selected_item_index}")
            elif itype == "consumable":
                self._draw_button(x + 15, btn_y, 80, 30, "使用", f"use_{self.selected_item_index}")
                
            self._draw_button(x + 105, btn_y, 80, 30, "丢弃", f"drop_{self.selected_item_index}")
            
        elif self.selected_item_type == "equipment":
            if self.selected_item_index == "Pet":
                self._draw_button(x + 15, btn_y, 80, 30, "休息", "rest_pet")
            else:
                self._draw_button(x + 15, btn_y, 80, 30, "卸下", f"unequip_{self.selected_item_index}")
            
    def _draw_button(self, x, y, w, h, text, action_id):
        is_hover = (self.hovered_element == f"btn_{action_id}")
        bg = self.colors["btn_hover"] if is_hover else self.colors["btn_bg"]
        
        self.canvas.create_rectangle(x, y, x+w, y+h, fill=bg, outline=self.colors["border"], tags=f"btn_{action_id}")
        self.canvas.create_text(x+w//2, y+h//2, text=text, fill=self.colors["text"], font=("Microsoft YaHei", 11), tags=f"btn_{action_id}")
        
        self.buttons.append({
            "rect": (x, y, x+w, y+h),
            "id": action_id
        })
        
    def _pt_in_rect(self, x, y, rect):
        rx1, ry1, rx2, ry2 = rect
        return rx1 <= x <= rx2 and ry1 <= y <= ry2
        
    def on_hover(self, event):
        x, y = event.x, event.y
        new_hover = None
        
        # Check buttons
        for btn in self.buttons:
            if self._pt_in_rect(x, y, btn["rect"]):
                new_hover = f"btn_{btn['id']}"
                break
                
        if new_hover != self.hovered_element:
            self.hovered_element = new_hover
            self.draw() # Redraw for hover effects
            
    def on_click(self, event):
        x, y = event.x, event.y
        
        # Check tabs
        for tab in self.tab_hitboxes:
            if self._pt_in_rect(x, y, tab["rect"]):
                self.active_tab = tab["name"]
                self.selected_item_type = None
                self.selected_item_index = None
                self.draw()
                return
                
        # Check buttons first
        for btn in self.buttons:
            if self._pt_in_rect(x, y, btn["rect"]):
                if self.on_action_callback:
                    self.on_action_callback(btn["id"])
                return
                
        # Check items
        for item in self.item_hitboxes:
            if self._pt_in_rect(x, y, item["rect"]):
                if item["item"]:
                    self.selected_item_type = item["type"]
                    self.selected_item_index = item["index"]
                    self.draw()
                return

        # Clicked empty space
        self.selected_item_type = None
        self.selected_item_index = None
        self.draw()
