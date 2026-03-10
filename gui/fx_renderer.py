import tkinter as tk
import math
import random
import time

class FXRenderer:
    def __init__(self, canvas):
        self.canvas = canvas
        self.width = int(canvas.winfo_width())
        self.height = int(canvas.winfo_height())
        if self.width <= 1: self.width = 600
        if self.height <= 1: self.height = 600
        
        self.particles = []
        self.is_playing = False
        self.tick = 0
        self.duration = 0
        self.on_complete = None
        self.fx_type = None
        
    def start_vortex(self, duration_ms=1500, on_complete=None):
        self.canvas.delete("all")
        self.width = int(self.canvas.winfo_width())
        self.height = int(self.canvas.winfo_height())
        if self.width <= 1: self.width = 600
        if self.height <= 1: self.height = 600
        
        # Black background
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill="#000000", tags="bg")
        
        self.particles = []
        cx, cy = self.width // 2, self.height // 2
        
        for _ in range(150):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(50, max(self.width, self.height))
            speed = random.uniform(0.05, 0.15)
            size = random.uniform(2, 6)
            color = random.choice(["#3b82f6", "#8b5cf6", "#ec4899", "#ffffff"])
            
            p_id = self.canvas.create_oval(0, 0, 0, 0, fill=color, outline="")
            
            self.particles.append({
                "id": p_id,
                "angle": angle,
                "dist": dist,
                "speed": speed,
                "size": size,
                "cx": cx,
                "cy": cy
            })
            
        self.is_playing = True
        self.tick = 0
        self.duration = duration_ms // 30 # roughly 30ms per frame
        self.on_complete = on_complete
        self.fx_type = "vortex"
        self._step_vortex()
        
    def _step_vortex(self):
        if not self.is_playing: return
        
        self.tick += 1
        progress = self.tick / self.duration
        
        for p in self.particles:
            # Swirl inward and spin faster as it gets closer
            p["angle"] += p["speed"] + (progress * 0.2)
            p["dist"] *= 0.92  # pull in
            
            # If pulled too close, shoot it back out or hide it
            if p["dist"] < 5:
                p["dist"] = max(self.width, self.height) * 1.5
                
            x = p["cx"] + math.cos(p["angle"]) * p["dist"]
            y = p["cy"] + math.sin(p["angle"]) * p["dist"]
            s = p["size"] * (1.0 if progress < 0.8 else (1.0 - progress) * 5) # fade small at end
            
            self.canvas.coords(p["id"], x-s, y-s, x+s, y+s)
            
        # Draw central white hole expanding at the very end
        if progress > 0.8:
            hole_r = (progress - 0.8) * 5 * min(self.width, self.height)
            self.canvas.delete("hole")
            self.canvas.create_oval(self.particles[0]["cx"]-hole_r, self.particles[0]["cy"]-hole_r,
                                    self.particles[0]["cx"]+hole_r, self.particles[0]["cy"]+hole_r,
                                    fill="#FFFFFF", outline="", tags="hole")
        
        if self.tick >= self.duration:
            self.is_playing = False
            self.canvas.delete("all")
            if self.on_complete:
                self.on_complete()
        else:
            self.canvas.after(30, self._step_vortex)
