import tkinter as tk
import math

class Node:
    def __init__(self, c_id, name, content_type, data, x, y, parent_ids=None):
        self.id = c_id
        self.name = name
        self.content_type = content_type # "bloodline", "skill", "stats"
        self.data = data
        self.x = x
        self.y = y
        self.parent_ids = parent_ids or []
        self.is_unlocked = False
        
        self.ui_circle = None
        self.ui_text = None

class EnhancementRenderer:
    def __init__(self, canvas):
        self.canvas = canvas
        self.width = 0
        self.height = 0
        self.nodes = {}
        self.player_stats = None
        
        # Center "Main God" pulsing sphere
        self.god_sphere = None
        self.god_glow = None
        self.tick = 0
        
        # Camera & Drag
        self.cam_x = 0
        self.cam_y = 0
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_dragging = False
        
        self.on_node_click = None
        
        # Bindings
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_click)
        
        self.colors = {
            "unlocked": "#eab308", # Rich Gold
            "purchasable": "#38bdf8", # Sci-fi Blue
            "locked": "#334155", # Slate
            "bg": "#0f172a", # Deep galaxy background
            "panel_bg": "#1e293b", # Panel slate
            "text": "#f8fafc", # Bright text
            "stat_bar": "#10b981", # Emerald green
            "grid": "#334155" # Grid lines
        }

    def setup(self, width, height, node_list, unlocked_ids, click_callback, player_stats=None):
        self.width = width
        self.height = height
        self.on_node_click = click_callback
        self.player_stats = player_stats
        
        # Exclude stats from galaxy planet view
        self.nodes = {n["id"]: Node(
            n["id"], n["name"], n["type"], n.get("data", {}), n["x"], n["y"], n.get("parents", [])
        ) for n in node_list if n["type"] != "stat"}
        
        for k, v in self.nodes.items():
            if k in unlocked_ids:
                v.is_unlocked = True
                
        self.cam_x = 0
        self.cam_y = 0
        self.draw_all()

    def update_unlocks(self, unlocked_ids, player_stats=None):
        if player_stats:
            self.player_stats = player_stats
        for k, v in self.nodes.items():
            v.is_unlocked = (k in unlocked_ids)
        self.draw_all()
        
    def get_color_for_node(self, node):
        if node.is_unlocked: return self.colors["unlocked"]
        can_p = True
        for p_id in node.parent_ids:
            p_node = self.nodes.get(p_id)
            if p_node and not p_node.is_unlocked:
                can_p = False; break
        return self.colors["purchasable"] if (can_p or not node.parent_ids) else self.colors["locked"]

    def draw_all(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill=self.colors["bg"], outline="")
        
        # Grid Background
        for i in range(0, int(self.width), 60):
            self.canvas.create_line(i, 0, i, self.height, fill=self.colors["grid"], dash=(2, 4))
        for i in range(0, int(self.height), 60):
            self.canvas.create_line(0, i, self.width, i, fill=self.colors["grid"], dash=(2, 4))
        
        # Override all node X/Y to form a clean double-column vertical list layout
        bl_nodes = [n for n in self.nodes.values() if "bloodline" in n.content_type or n.name == "核心血统树"]
        sk_nodes = [n for n in self.nodes.values() if n.content_type == "skill" or n.name == "因果技能网"]
        
        # Sort them basically by parent depth or name
        def layout_nodes(node_list, start_x, start_y):
            y_offset = start_y
            for n in node_list:
                n.x = start_x
                n.y = y_offset
                y_offset += 80 # Vertical spacing
                
        # We will dynamically override their x, y based on this list, ignoring the messy ones from main_god_space
        layout_nodes(bl_nodes, -150, -self.height/2 + 80)
        layout_nodes(sk_nodes, 150, -self.height/2 + 80)
        
        cx = self.width / 2 + self.cam_x
        cy = self.height / 2 + self.cam_y
        
        # Draw God Sphere (Now at the top center)
        self.draw_god_sphere(cx, cy - self.height/2 + 60)
        
        # Connections (Only draw parent lines if they make sense now, or just vertical lines)
        for node in self.nodes.values():
            for p_id in node.parent_ids:
                p_node = self.nodes.get(p_id)
                if p_node:
                    col = self.colors["unlocked"] if (node.is_unlocked and p_node.is_unlocked) else self.colors["locked"]
                    self.canvas.create_line(cx+p_node.x, cy+p_node.y, cx+node.x, cy+node.y, fill=col, width=2)

        # Draw Nodes as clean Tech Panels instead of Circles
        box_w, box_h = 60, 25
        for node in self.nodes.values():
            nx, ny = cx + node.x, cy + node.y
            col = self.get_color_for_node(node)
            
            # Outer Glow
            self.canvas.create_rectangle(nx-box_w-3, ny-box_h-3, nx+box_w+3, ny+box_h+3, fill="", outline=col, width=1, dash=(2,2))
            
            # Inner Box
            node.ui_circle = self.canvas.create_rectangle(nx-box_w, ny-box_h, nx+box_w, ny+box_h, fill="#0f172a", outline=col, width=2, tags=(f"node_{node.id}",))
            
            # Content Icon + Name (Side-by-side or stacked inside box)
            icon = "🧬" if "bloodline" in node.content_type else ("💡" if node.content_type == "skill" else "🔗")
            
            # Truncate very long names for the box
            display_name = node.name.replace("\\n", " ") # Remove explicit newlines if any
            
            self.canvas.create_text(nx, ny-6, text=f"{icon} {display_name}", fill=col, font=("Microsoft YaHei", 9, "bold"), tags=(f"node_{node.id}",), width=110, justify="center")
            
            # Optional cost text at bottom of box
            cost = node.data.get("cost", "") if node.data else ""
            if cost != "":
                self.canvas.create_text(nx, ny+10, text=f"💎 {cost}", fill="#eab308", font=("Consolas", 8), tags=(f"node_{node.id}",))

        self.draw_god_sphere(cx, cy)
        self.draw_stat_panel()

    def draw_god_sphere(self, cx, cy):
        pulse = math.sin(self.tick * 0.1) * 8
        r = 60 + pulse
        self.god_glow = self.canvas.create_oval(cx-r-15, cy-r-15, cx+r+15, cy+r+15, fill="", outline=self.colors["unlocked"], width=2, dash=(4, 4))
        self.god_sphere = self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="#020617", outline=self.colors["unlocked"], width=5)
        self.canvas.create_text(cx, cy, text="主神 Core", fill=self.colors["unlocked"], font=("Microsoft YaHei", 16, "bold"))

    def draw_stat_panel(self):
        if not self.player_stats: return
        w, h = 280, 480
        x, y = self.width - w - 20, 20
        # Glassmorphism-like Background
        self.canvas.create_rectangle(x, y, x+w, y+h, fill=self.colors["panel_bg"], outline=self.colors["purchasable"], width=1)
        
        # Tech corners
        d = 15
        for px, py in [(x, y), (x+w, y), (x, y+h), (x+w, y+h)]:
            dx = d if px == x else -d
            dy = d if py == y else -d
            self.canvas.create_line(px, py+dy, px, py, px+dx, py, fill=self.colors["purchasable"], width=3)
            
        self.canvas.create_text(x+w/2, y+30, text="✨ 轮回者本源重构 ✨", fill=self.colors["unlocked"], font=("Microsoft YaHei", 13, "bold"))
        self.canvas.create_line(x+20, y+50, x+w-20, y+50, fill=self.colors["locked"], dash=(4, 2))
        
        stats_info = [("str", "力量 (STR)"), ("agi", "敏捷 (AGI)"), ("int", "智力 (INT)"),
                      ("con", "体质 (CON)"), ("per", "感知 (PER)"), ("cha", "魅力 (CHA)")]
        sy = y + 75
        for key, label in stats_info:
            val = self.player_stats.get(key, 10)
            self.canvas.create_text(x+20, sy, text=label, fill=self.colors["text"], font=("Microsoft YaHei", 10, "bold"), anchor="w")
            self.canvas.create_text(x+w-50, sy, text=f"{val:03d}", fill=self.colors["unlocked"], font=("Consolas", 12, "bold"), anchor="e")
            
            # Segmented Progress Bar
            bar_w = w - 80
            segments = 15
            seg_w = bar_w / segments
            progress_segs = min(segments, int((val / 200.0) * segments))
            
            for i in range(segments):
                sx = x + 20 + i * (seg_w)
                color = self.colors["stat_bar"] if i < progress_segs else self.colors["locked"]
                self.canvas.create_rectangle(sx, sy+15, sx+seg_w-2, sy+22, fill=color, outline="")
            
            # High-tech Plus button
            btn_x, btn_y, btn_r = x+w-25, sy+6, 14
            tag = f"statbtn_{key}"
            self.canvas.create_rectangle(btn_x-btn_r, btn_y-btn_r, btn_x+btn_r, btn_y+btn_r, fill=self.colors["bg"], outline=self.colors["unlocked"], width=1, tags=tag)
            self.canvas.create_text(btn_x, btn_y, text="＋", fill=self.colors["unlocked"], font=("Microsoft YaHei", 12, "bold"), tags=tag)
            
            sy += 55
            
        self.canvas.create_line(x+20, y+h-50, x+w-20, y+h-50, fill=self.colors["locked"], dash=(4, 2))
        pts = self.player_stats.get('points', 0)
        self.canvas.create_text(x+w/2, y+h-25, text=f"极光积分: {pts:,}", fill=self.colors["stat_bar"], font=("Consolas", 13, "bold"))

    def step(self):
        self.tick += 1
        cx, cy = self.width / 2 + self.cam_x, self.height / 2 + self.cam_y
        pulse = math.sin(self.tick * 0.1) * 8
        r = 60 + pulse
        if self.god_sphere:
            self.canvas.coords(self.god_sphere, cx-r, cy-r, cx+r, cy+r)
            self.canvas.coords(self.god_glow, cx-r-15, cy-r-15, cx+r+15, cy+r+15)
            
    def on_press(self, event):
        self.drag_start_x, self.drag_start_y = event.x, event.y
        self.is_dragging = False
    def on_drag(self, event):
        dx, dy = event.x - self.drag_start_x, event.y - self.drag_start_y
        if abs(dx) > 5 or abs(dy) > 5: self.is_dragging = True
        self.cam_x += dx; self.cam_y += dy
        self.drag_start_x, self.drag_start_y = event.x, event.y
        self.draw_all()
        
    def on_click(self, event):
        if self.is_dragging: return
        items = self.canvas.find_withtag("current")
        if not items: return
        tags = self.canvas.gettags(items[0])
        for tag in tags:
            if tag.startswith("node_"):
                node_id = tag[len("node_"):]
                if self.on_node_click:
                    node = self.nodes.get(node_id)
                    self.on_node_click(node_id, self.get_color_for_node(node) != self.colors["locked"])
                return
            elif tag.startswith("statbtn_"):
                stat_key = tag[len("statbtn_"):]
                if self.on_node_click:
                    self.on_node_click(f"stat_{stat_key}", True)
                return
