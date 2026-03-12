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
        
        # Tabs and Drawer state
        self.current_tab = "all" # "all", "bloodline", "cultivation", "skill"
        self.tabs = [
            {"id": "all", "label": "🌌 核心枢纽", "x": 0, "y": 0, "w": 120},
            {"id": "bloodline", "label": "🧬 血统进化", "x": 0, "y": 0, "w": 120},
            {"id": "cultivation", "label": "☯️ 功法推演", "x": 0, "y": 0, "w": 120},
            {"id": "skill", "label": "💡 技能烙印", "x": 0, "y": 0, "w": 120}
        ]
        self.is_stat_panel_open = False
        self.stat_drawer_anim = 0.0 # 0.0 (closed) to 1.0 (open)

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
        # To avoid lag, we draw a large static background instead of many small lines for the grid
        self.canvas.create_rectangle(-2000, -2000, 2000, 2000, fill=self.colors["bg"], outline="")
        
        # Grid Background (Optimized: We draw a large grid that can move with the camera)
        grid_size = 60
        # Draw grid covering a much wider area than the screen to allow panning without redraws
        # The movable tag will shift these lines naturally.
        pad = 2000
        for i in range(-pad, pad, grid_size):
            self.canvas.create_line(i + self.cam_x, -pad, i + self.cam_x, pad, fill=self.colors["grid"], dash=(2, 4), tags="movable")
        for i in range(-pad, pad, grid_size):
            self.canvas.create_line(-pad, i + self.cam_y, pad, i + self.cam_y, fill=self.colors["grid"], dash=(2, 4), tags="movable")
        
        cx = self.width / 2 + self.cam_x
        cy = self.height / 2 + self.cam_y

        # Helper to determine if a node should be visible
        def is_visible(node):
            # 1. Filter by Tab
            if self.current_tab != "all":
                if self.current_tab == "bloodline" and "bloodline" not in node.content_type:
                    return False
                if self.current_tab == "cultivation" and "cultivation" not in node.content_type:
                    return False
                if self.current_tab == "skill" and node.content_type != "skill":
                    return False

            if node.content_type == "category":
                return False # Hide arbitrary roots to save space

            if not node.parent_ids or any("root" in pid for pid in node.parent_ids):
                return True

            for p_id in node.parent_ids:
                p_node = self.nodes.get(p_id)
                if p_node and p_node.is_unlocked:
                    return True
            return False

        visible_nodes = [n for n in self.nodes.values() if is_visible(n)]

        # Group nodes
        bl_bases = [n for n in visible_nodes if n.content_type == "bloodline_base"]
        c_bases = [n for n in visible_nodes if n.content_type == "cultivation_base"]
        skills = [n for n in visible_nodes if n.content_type == "skill"]
        
        # Layout spacing adjustments based on view
        if self.current_tab == "all":
            # Compact view (all)
            bl_x_offset = -250
            bl_x_spacing = 150
            bl_y_spacing = 200

            c_x_offset = 250
            c_x_spacing = 150
            c_y_spacing = 200

            skill_cols = 4
            skill_y_start = 250
            skill_x_spacing = 160
            skill_y_spacing = 100
            child_y_dist = 90
        else:
            # Expanded view (specific tab)
            # When viewing a specific tab, we spread them out more widely
            bl_x_offset = -150 if len(bl_bases) > 1 else 0
            bl_x_spacing = 250
            bl_y_spacing = 250

            c_x_offset = -150 if len(c_bases) > 1 else 0
            c_x_spacing = 250
            c_y_spacing = 250

            skill_cols = 6
            skill_y_start = 180
            skill_x_spacing = 180
            skill_y_spacing = 120
            child_y_dist = 110

        # Layout: God Sphere at center (0,0) relative to camera

        # Bloodlines
        for i, base in enumerate(bl_bases):
            # Only apply alternating offset if there are multiple bases to spread them nicely
            x_idx = (i % 2) if len(bl_bases) > 1 else 0
            base.x = bl_x_offset - x_idx * bl_x_spacing

            if self.current_tab == "bloodline":
                base.x = (i - (len(bl_bases)-1)/2.0) * bl_x_spacing # Distribute evenly if focused

            base.y = -100 + (i // 2) * bl_y_spacing

            # Trace children
            child_y_offset = child_y_dist
            def position_children(parent_id, px, py):
                nonlocal child_y_offset
                children = [n for n in visible_nodes if parent_id in n.parent_ids]
                for c in children:
                    c.x = px
                    c.y = py + child_y_offset
                    child_y_offset += child_y_dist
                    position_children(c.id, c.x, c.y)
            position_children(base.id, base.x, base.y)

        # Cultivations
        for i, base in enumerate(c_bases):
            x_idx = (i % 2) if len(c_bases) > 1 else 0
            base.x = c_x_offset + x_idx * c_x_spacing

            if self.current_tab == "cultivation":
                 base.x = (i - (len(c_bases)-1)/2.0) * c_x_spacing

            base.y = -100 + (i // 2) * c_y_spacing

            child_y_offset = child_y_dist
            def position_children(parent_id, px, py):
                nonlocal child_y_offset
                children = [n for n in visible_nodes if parent_id in n.parent_ids]
                for c in children:
                    c.x = px
                    c.y = py + child_y_offset
                    child_y_offset += child_y_dist
                    position_children(c.id, c.x, c.y)
            position_children(base.id, base.x, base.y)

        # Skills
        for i, skill in enumerate(skills):
            r = i // skill_cols
            c = i % skill_cols
            skill.x = (c - skill_cols/2 + 0.5) * skill_x_spacing
            skill.y = skill_y_start + r * skill_y_spacing

        # Connections
        # Cache visible set for O(1) lookups
        visible_set = {n.id for n in visible_nodes}

        def draw_circuit_line(x1, y1, x2, y2, color, dash_pattern=None):
            # Draw an orthogonal "circuit-board" style line to avoid chaotic spiderweb diagonals
            mid_y = (y1 + y2) / 2
            pts = [x1, y1, x1, mid_y, x2, mid_y, x2, y2]
            if dash_pattern:
                self.canvas.create_line(pts, fill=color, width=2, dash=dash_pattern, tags="movable")
            else:
                self.canvas.create_line(pts, fill=color, width=2, tags="movable")

        # Draw main trunks for categories to avoid 50 lines going directly to the center sphere
        drawn_trunks = set()

        for node in visible_nodes:
            for p_id in node.parent_ids:
                if p_id in visible_set:
                    p_node = self.nodes.get(p_id)
                    col = self.colors["unlocked"] if (node.is_unlocked and p_node.is_unlocked) else self.colors["locked"]
                    draw_circuit_line(cx+p_node.x, cy+p_node.y, cx+node.x, cy+node.y, col)
                elif "root" in p_id:
                    col = self.colors["unlocked"] if node.is_unlocked else self.colors["locked"]

                    # Group connections by their hidden root to avoid starburst "spiderweb" to the center
                    if "skill" in p_id:
                        trunk_x, trunk_y = cx, cy + 120
                        if "skill" not in drawn_trunks:
                            draw_circuit_line(cx, cy, trunk_x, trunk_y, self.colors["unlocked"], dash_pattern=(4,2))
                            drawn_trunks.add("skill")
                        draw_circuit_line(trunk_x, trunk_y, cx+node.x, cy+node.y, col, dash_pattern=(4,2))
                    elif "bl_root" in p_id:
                        trunk_x, trunk_y = cx, cy - 120
                        if "bl_root" not in drawn_trunks:
                            draw_circuit_line(cx, cy, trunk_x, trunk_y, self.colors["unlocked"], dash_pattern=(4,2))
                            drawn_trunks.add("bl_root")
                        draw_circuit_line(trunk_x, trunk_y, cx+node.x, cy+node.y, col, dash_pattern=(4,2))
                    elif "cult_root" in p_id:
                        trunk_x, trunk_y = cx, cy - 120
                        if "cult_root" not in drawn_trunks:
                            draw_circuit_line(cx, cy, trunk_x, trunk_y, self.colors["unlocked"], dash_pattern=(4,2))
                            drawn_trunks.add("cult_root")
                        draw_circuit_line(trunk_x, trunk_y, cx+node.x, cy+node.y, col, dash_pattern=(4,2))
                    else:
                        draw_circuit_line(cx, cy, cx+node.x, cy+node.y, col, dash_pattern=(4,2))

        # Draw God Sphere strictly at center, drawn after lines so it covers them
        self.draw_god_sphere(cx, cy)

        # Draw Nodes as clean Tech Panels instead of Circles
        box_w, box_h = 60, 25
        # We no longer cull nodes by screen bounds during draw_all because the native canvas.move
        # handles off-screen rendering natively much faster than python can rebuild them every frame.
        for node in visible_nodes:
            nx, ny = cx + node.x, cy + node.y

            col = self.get_color_for_node(node)
            
            # Outer Glow
            self.canvas.create_rectangle(nx-box_w-3, ny-box_h-3, nx+box_w+3, ny+box_h+3, fill="", outline=col, width=1, dash=(2,2), tags="movable")
            
            # Inner Box
            tgs = (f"node_{node.id}", "movable")
            node.ui_circle = self.canvas.create_rectangle(nx-box_w, ny-box_h, nx+box_w, ny+box_h, fill="#0f172a", outline=col, width=2, tags=tgs)
            
            # Content Icon + Name (Side-by-side or stacked inside box)
            if "bloodline" in node.content_type: icon = "🧬"
            elif "cultivation" in node.content_type: icon = "☯️"
            elif node.content_type == "skill": icon = "💡"
            else: icon = "🔗"
            
            # Truncate very long names for the box
            display_name = node.name.replace("\\n", " ") # Remove explicit newlines if any
            
            self.canvas.create_text(nx, ny-6, text=f"{icon} {display_name}", fill=col, font=("Microsoft YaHei", 9, "bold"), tags=tgs, width=110, justify="center")
            
            # Optional cost text at bottom of box
            cost = node.data.get("cost", "") if node.data else ""
            if cost != "":
                self.canvas.create_text(nx, ny+10, text=f"💎 {cost}", fill="#eab308", font=("Consolas", 8), tags=tgs)

        # Draw Tabs Menu
        self.draw_tabs()

        self.draw_stat_panel()

    def draw_tabs(self):
        tab_h = 40
        # Glassmorphism panel at the top
        self.canvas.create_rectangle(0, 0, self.width, tab_h+10, fill="#0f172a", stipple="gray50", outline="")
        self.canvas.create_line(0, tab_h+10, self.width, tab_h+10, fill=self.colors["unlocked"], width=2, dash=(4,2))

        # Calculate center offset for tabs
        total_w = sum(t["w"] + 10 for t in self.tabs) - 10
        start_x = (self.width - total_w) / 2

        curr_x = start_x
        for tab in self.tabs:
            tab["x"] = curr_x
            tab["y"] = 10

            is_active = self.current_tab == tab["id"]
            bg_col = self.colors["unlocked"] if is_active else self.colors["panel_bg"]
            text_col = "#020617" if is_active else self.colors["text"]

            tag = f"tab_{tab['id']}"

            # Draw tab polygon (sci-fi angled shape)
            pts = [
                curr_x, 10 + tab_h,
                curr_x + 10, 10,
                curr_x + tab["w"] - 10, 10,
                curr_x + tab["w"], 10 + tab_h
            ]
            self.canvas.create_polygon(pts, fill=bg_col, outline=self.colors["unlocked"], width=2, tags=(tag,))
            self.canvas.create_text(curr_x + tab["w"]/2, 10 + tab_h/2, text=tab["label"], fill=text_col, font=("Microsoft YaHei", 11, "bold"), tags=(tag,))

            curr_x += tab["w"] + 10

    def draw_god_sphere(self, cx, cy):
        pulse = math.sin(self.tick * 0.1) * 8
        r = 60 + pulse
        self.god_glow = self.canvas.create_oval(cx-r-15, cy-r-15, cx+r+15, cy+r+15, fill="", outline=self.colors["unlocked"], width=2, dash=(4, 4), tags="movable")
        self.god_sphere = self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="#020617", outline=self.colors["unlocked"], width=5, tags="movable")
        self.god_text = self.canvas.create_text(cx, cy, text="主神 Core", fill=self.colors["unlocked"], font=("Microsoft YaHei", 16, "bold"), tags="movable")

    def draw_stat_panel(self):
        if not self.player_stats: return
        w, h = 280, 480

        # Calculate drawer X position based on animation state
        # Open: self.width - w, Closed: self.width
        drawer_w = w + 20
        offset_x = self.width - (drawer_w * self.stat_drawer_anim)
        x, y = offset_x, 60

        # Draw toggle button (attached to the left side of the drawer)
        toggle_w, toggle_h = 40, 60
        tx, ty = x - toggle_w, y + 20
        self.canvas.create_polygon(tx+10, ty, tx+toggle_w, ty, tx+toggle_w, ty+toggle_h, tx+10, ty+toggle_h, tx, ty+toggle_h/2, fill=self.colors["panel_bg"], outline=self.colors["purchasable"], tags="stat_toggle")

        toggle_icon = ">>" if self.is_stat_panel_open else "<<"
        self.canvas.create_text(tx + toggle_w/2 + 5, ty + toggle_h/2, text=toggle_icon, fill=self.colors["unlocked"], font=("Consolas", 14, "bold"), tags="stat_toggle")

        # If fully closed and not animating, don't draw the rest of the panel
        if self.stat_drawer_anim < 0.01:
             return

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
        pulse = math.sin(self.tick * 0.1) * 8
        r = 60 + pulse
        if getattr(self, "god_sphere", None) and getattr(self, "god_text", None):
            # To update the pulse size without redrawing the whole screen,
            # we read the current center from the text coordinate (which moves with drag)
            coords = self.canvas.coords(self.god_text)
            if coords:
                cx, cy = coords[0], coords[1]
                self.canvas.coords(self.god_sphere, cx-r, cy-r, cx+r, cy+r)
                self.canvas.coords(self.god_glow, cx-r-15, cy-r-15, cx+r+15, cy+r+15)

        # Animate stat drawer
        target_anim = 1.0 if self.is_stat_panel_open else 0.0
        if abs(self.stat_drawer_anim - target_anim) > 0.01:
            self.stat_drawer_anim += (target_anim - self.stat_drawer_anim) * 0.2
            self.draw_all()

    def on_press(self, event):
        self.drag_start_x, self.drag_start_y = event.x, event.y
        self.is_dragging = False
    def on_drag(self, event):
        dx, dy = event.x - self.drag_start_x, event.y - self.drag_start_y
        if abs(dx) > 5 or abs(dy) > 5: self.is_dragging = True
        self.cam_x += dx; self.cam_y += dy
        self.drag_start_x, self.drag_start_y = event.x, event.y

        # Performance optimization: Shift objects natively instead of destroying/recreating thousands of items
        # To avoid moving fixed UI elements like tabs and stat panels, we tag movable items in draw_all.
        self.canvas.move("movable", dx, dy)
        
    def on_click(self, event):
        if self.is_dragging: return
        items = self.canvas.find_withtag("current")
        if not items: return
        tags = self.canvas.gettags(items[0])
        for tag in tags:
            if tag.startswith("tab_"):
                tab_id = tag[len("tab_"):]
                self.current_tab = tab_id
                self.cam_x = 0
                self.cam_y = 0
                self.draw_all()
                return
            elif tag == "stat_toggle":
                self.is_stat_panel_open = not self.is_stat_panel_open
                return
            elif tag.startswith("node_"):
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
