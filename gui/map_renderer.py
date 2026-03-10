import tkinter as tk
import math
import time

class MapRenderer:
    def __init__(self, canvas):
        self.canvas = canvas
        self.width = 0
        self.height = 0
        self.map_data = []
        self.player_x = 0
        self.player_y = 0
        self.cell_size = 70
        self.cam_x = 0
        self.cam_y = 0
        
        self.on_move_intent = None
        self.canvas.bind("<Button-1>", self.on_click)
        
        self.pulse_time = 0.0
        self.is_running = True
        self.animate()
        
    def setup(self, width, height, map_data, player_x, player_y, move_callback):
        self.width = width
        self.height = height
        self.map_data = map_data
        self.player_x = player_x
        self.player_y = player_y
        self.on_move_intent = move_callback
        self.draw_map()
        
    def update_player_pos(self, x, y):
        self.player_x = x
        self.player_y = y
        self.draw_map()
        
    def update_map(self, map_data):
        self.map_data = map_data
        self.draw_map()
        
    def draw_map(self):
        self.canvas.delete("all")
        if not self.map_data: return
            
        rows = len(self.map_data)
        cols = len(self.map_data[0]) if rows > 0 else 0
        
        self.cam_x = int(self.width/2 - (self.player_x * self.cell_size + self.cell_size/2))
        self.cam_y = int(self.height/2 - (self.player_y * self.cell_size + self.cell_size/2))
        
        # 1. Background Grid (Cyberpunk space theme)
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill="#050a10", outline="")
        
        for i in range(0, self.width, 100):
            self.canvas.create_line(i, 0, i, self.height, fill="#0a1a2f")
        for i in range(0, self.height, 100):
            self.canvas.create_line(0, i, self.width, i, fill="#0a1a2f")

        # 2. Draw Rooms
        for r in range(rows):
            for c in range(cols):
                room = self.map_data[r][c]
                if not room: continue
                    
                x1 = self.cam_x + c * self.cell_size
                y1 = self.cam_y + r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                padx, pady = 4, 4
                
                # Room Styling
                if not room.get("visited", False):
                    bg = "#111111"
                    outline = "#1a1a1a"
                    width = 1
                else:
                    r_type = room.get("type")
                    bg = "#1a1a2e"
                    outline = "#3a4a6e"
                    width = 2
                    
                    if r_type == "boss":
                        bg = "#2e0a0a"
                        outline = "#ff4444"
                    elif r_type == "event":
                        bg = "#2e2e0a"
                        outline = "#ffff44"
                    elif r_type == "treasure":
                        bg = "#2e200a"
                        outline = "#ffd700"
                    elif r_type == "start":
                        bg = "#0a2e0a"
                        outline = "#44ff44"
                
                # Rounder rect emulation
                self.canvas.create_rectangle(x1+padx, y1+pady, x2-padx, y2-pady, fill=bg, outline=outline, width=width, tags=(f"cell_{r}_{c}",))
                
                # Glow for special unvisited/special rooms
                if room.get("visited", False) and not room.get("cleared", False):
                    if room.get("type") == "boss":
                        self.canvas.create_oval(x1+10, y1+10, x2-10, y2-10, outline="#ff0000", width=1)
                    
                # Icons
                if room.get("visited", False):
                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2
                    is_cleared = room.get("cleared", False)
                    
                    if room["type"] == "enemy" and not is_cleared:
                        self.canvas.create_text(cx, cy, text="⚔️", fill="#ff4444", font=("Arial", 22, "bold"))
                    elif room["type"] == "boss" and not is_cleared:
                        self.canvas.create_text(cx, cy, text="👹", fill="#ff0000", font=("Arial", 28, "bold"))
                    elif room["type"] == "treasure" and not is_cleared:
                        self.canvas.create_text(cx, cy, text="💎", fill="#ffd700", font=("Arial", 22, "bold"))
                    elif room["type"] == "event" and not is_cleared:
                        self.canvas.create_text(cx, cy, text="⚖️", fill="#ffff44", font=("Arial", 22, "bold"))
                    elif room["type"] == "start":
                        self.canvas.create_text(cx, cy, text="🛰️", fill="#44ff44", font=("Arial", 20, "bold"))
                    elif is_cleared and room["type"] != "start":
                        self.canvas.create_oval(cx-3, cy-3, cx+3, cy+3, fill="#3a4a6e", outline="")

        # 3. Draw Player Marker (Pulsing)
        px = self.cam_x + self.player_x * self.cell_size + self.cell_size/2
        py = self.cam_y + self.player_y * self.cell_size + self.cell_size/2
        
        pulse = math.sin(self.pulse_time) * 5 + 15
        self.canvas.create_oval(px-pulse, py-pulse, px+pulse, py+pulse, outline="#00e5ff", width=2, tags="player_pulse")
        self.canvas.create_oval(px-10, py-10, px+10, py+10, fill="#00e5ff", outline="white", width=2, tags="player")

    def animate(self):
        if not self.is_running: return
        self.pulse_time += 0.2
        # Only update pulse if in canvas
        try:
            items = self.canvas.find_withtag("player_pulse")
            if items:
                px = self.cam_x + self.player_x * self.cell_size + self.cell_size/2
                py = self.cam_y + self.player_y * self.cell_size + self.cell_size/2
                pulse = math.sin(self.pulse_time) * 5 + 15
                self.canvas.coords(items[0], px-pulse, py-pulse, px+pulse, py+pulse)
        except: pass
        self.canvas.after(50, self.animate)

    def on_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        c = int((x - self.cam_x) // self.cell_size)
        r = int((y - self.cam_y) // self.cell_size)
        
        if self.map_data and 0 <= r < len(self.map_data) and 0 <= c < len(self.map_data[0]):
            dx, dy = abs(self.player_x - c), abs(self.player_y - r)
            if (dx == 1 and dy == 0) or (dx == 0 and dy == 1):
                if self.on_move_intent:
                    self.on_move_intent(c, r)

