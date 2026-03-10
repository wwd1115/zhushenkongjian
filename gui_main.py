import customtkinter as ctk
import queue
import threading
import sys

# 设置主题
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class GUI(ctk.CTk):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.title("主神空间 - 无限轮回")
        self.geometry("900x600")
        
        # 布局：左侧信息区，右侧控制区
        self.grid_columnconfigure(0, weight=3) # 左侧宽
        self.grid_columnconfigure(1, weight=1) # 右侧窄
        self.grid_rowconfigure(0, weight=1)
        
        # --- 左侧主文本区 ---
        self.text_frame = ctk.CTkFrame(self)
        self.text_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.text_frame.grid_rowconfigure(0, weight=1)
        self.text_frame.grid_columnconfigure(0, weight=1)
        
        self.textbox = ctk.CTkTextbox(self.text_frame, font=("Consolas", 14), wrap="word")
        self.textbox.grid(row=0, column=0, sticky="nsew")
        self.textbox.configure(state="disabled") # 默认不可编辑
        
        # 配置颜色 tag
        self.textbox.tag_config("red", foreground="red")
        self.textbox.tag_config("green", foreground="lightgreen")
        self.textbox.tag_config("cyan", foreground="cyan")
        self.textbox.tag_config("yellow", foreground="yellow")
        self.textbox.tag_config("white", foreground="white")
        
        # --- 左侧战斗区 (默认隐藏) ---
        self.combat_frame = ctk.CTkFrame(self)
        self.combat_frame.grid_rowconfigure(0, weight=1)
        self.combat_frame.grid_columnconfigure(0, weight=1)
        
        import tkinter as tk
        from gui.combat_canvas import CombatRenderer
        self.canvas = tk.Canvas(self.combat_frame, bg="#1E1E1E", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.combat_renderer = CombatRenderer(self.canvas)
        self.is_in_combat = False
        
        # --- 左侧强化大厅区 (默认隐藏) ---
        self.hub_frame = ctk.CTkFrame(self)
        self.hub_frame.grid_rowconfigure(0, weight=1)
        self.hub_frame.grid_columnconfigure(0, weight=1)
        
        from gui.enhancement_hub import EnhancementRenderer
        self.hub_canvas = tk.Canvas(self.hub_frame, bg="#111111", highlightthickness=0)
        self.hub_canvas.grid(row=0, column=0, sticky="nsew")
        self.hub_renderer = EnhancementRenderer(self.hub_canvas)
        self.is_in_hub = False
        
        # --- 左侧探索地图区 (默认隐藏) ---
        self.map_frame = ctk.CTkFrame(self)
        self.map_frame.grid_rowconfigure(0, weight=1)
        self.map_frame.grid_columnconfigure(0, weight=1)
        
        from gui.map_renderer import MapRenderer
        self.map_canvas = tk.Canvas(self.map_frame, bg="#000000", highlightthickness=0)
        self.map_canvas.grid(row=0, column=0, sticky="nsew")
        self.map_renderer = MapRenderer(self.map_canvas)
        self.is_in_map = False
        
        # --- 左侧背包与属性区 (默认隐藏) ---
        self.inventory_frame = ctk.CTkFrame(self)
        self.inventory_frame.grid_rowconfigure(0, weight=1)
        self.inventory_frame.grid_columnconfigure(0, weight=1)
        
        from gui.inventory_renderer import InventoryRenderer
        self.inv_canvas = tk.Canvas(self.inventory_frame, bg="#111111", highlightthickness=0)
        self.inv_canvas.grid(row=0, column=0, sticky="nsew")
        self.inv_renderer = InventoryRenderer(self.inv_canvas)
        self.is_in_inventory = False
        
        # --- 全局特效层 (默认隐藏) ---
        self.fx_frame = ctk.CTkFrame(self)
        self.fx_frame.grid_rowconfigure(0, weight=1)
        self.fx_frame.grid_columnconfigure(0, weight=1)
        
        from gui.fx_renderer import FXRenderer
        self.fx_canvas = tk.Canvas(self.fx_frame, bg="#000000", highlightthickness=0)
        self.fx_canvas.grid(row=0, column=0, sticky="nsew")
        self.fx_renderer = FXRenderer(self.fx_canvas)
        
        # --- 右侧侧边栏 (属性 & 按钮) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=250)
        self.sidebar_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        self.sidebar_frame.grid_rowconfigure(1, weight=1) # 按钮区填充
        
        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="人物状态\n等待游戏开始...", font=("Microsoft YaHei", 12), justify="left")
        self.status_label.grid(row=0, column=0, padx=10, pady=10, sticky="nwe")
        
        self.buttons_frame = ctk.CTkScrollableFrame(self.sidebar_frame)
        self.buttons_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # 队列用于跨线程通信：游戏逻辑向主线程抛出请求
        self.event_queue = queue.Queue()
        self.input_queue = queue.Queue() # 用于将玩家的点击回传给游戏逻辑
        
        # 游戏引擎跑在独立线程，防止阻塞UI
        self.game_thread = threading.Thread(target=self.run_game_logic, daemon=True)
        
        # 定时器消费队列
        self.process_queue()
        
    def start(self):
        self.game_thread.start()
        self.mainloop()
        
    def run_game_logic(self):
        # 替换 display 模块的实现以接入 GUI
        import utils.display as disp
        disp.set_gui_mode(self)
        
        try:
            self.game.start()
        except Exception as e:
            import traceback
            err_trace = traceback.format_exc()
            self.log_error(f"游戏逻辑线程发生异常: {e}\n{err_trace}")
            if disp.GUI_INSTANCE:
                disp.GUI_INSTANCE.gui_print(f"\n[致命错误] 游戏逻辑线程发生异常: {e}\n详情请见 error_log.txt。", "red")

    def clear_text(self):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")

    def print_text(self, text, color="white"):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", text + "\n", color)
        self.textbox.configure(state="disabled")
        self.textbox.see("end")
        
    def clear_buttons(self):
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()
            
    def update_sidebar(self, text):
        self.status_label.configure(text=text)
        
    def add_button(self, text, callback, val):
        # Prevent text clipping by hiding default text, and packing a custom wrapping label inside it, or just relying on CTk word wrap if available
        # According to CTk docs, we can try using standard left anchoring and removing height constraints.
        btn = ctk.CTkButton(self.buttons_frame, text=text, command=lambda v=val: callback(v), 
                            anchor="w")
        btn._text_label.configure(wraplength=220, justify="left") # Force text wrapping if it exceeds sidebar width
        btn.pack(pady=5, padx=5, fill="x")

    def process_queue(self):
        try:
            while True:
                msg = self.event_queue.get_nowait()
                msg_type = msg.get("type")
                
                try:
                    if msg_type == "print":
                        self.print_text(msg["text"], msg.get("color", "white"))
                    elif msg_type == "clear":
                        self.clear_text()
                    elif msg_type == "menu":
                        self.clear_buttons()
                        options = msg["options"]
                        for key, val in options.items():
                            self.add_button(f"[{key}] {val}", self._on_button_click, key)
                    elif msg_type == "update_status":
                        self.update_sidebar(msg["text"])
                    elif msg_type == "text_input":
                        self.clear_buttons()
                        # 弹出一个原生 CTk 对话框要求输入
                        dialog = ctk.CTkInputDialog(text=msg.get("prompt", "请输入:"), title="系统提示")
                        user_input = dialog.get_input()
                        if user_input is None: 
                            # 取消时默认返回空字符串或者0
                            user_input = ""
                        self.input_queue.put(user_input)
                    elif msg_type == "start_visual_combat":
                        self.text_frame.grid_remove()
                        if hasattr(self, 'map_frame'): self.map_frame.grid_remove()
                        if hasattr(self, 'hub_frame'): self.hub_frame.grid_remove()
                        if hasattr(self, 'inventory_frame'): self.inventory_frame.grid_remove()
                    
                        self.combat_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
                        self.combat_frame.tkraise()
                        self.update_idletasks()
                    
                        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
                        if w <= 1: w, h = 600, 600
                        # Team data format: [{"id": "p1", "name": "Player", "hp": 100, "max_hp": 100}, ...]
                        self.combat_renderer.setup_teams(w, h, msg["p_team"], msg["e_team"])
                        self.is_in_combat = True
                    elif msg_type == "end_visual_combat":
                        self.combat_frame.grid_remove()
                        self.is_in_combat = False
                    
                        if getattr(self, 'is_in_map', False):
                            self.map_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
                            self.map_frame.tkraise()
                        elif getattr(self, 'is_in_hub', False):
                            self.hub_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
                            self.hub_frame.tkraise()
                        elif getattr(self, 'is_in_inventory', False):
                            self.inventory_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
                            self.inventory_frame.tkraise()
                        else:
                            self.text_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
                            self.text_frame.tkraise()
                    elif msg_type == "start_enhancement_hub":
                        self.text_frame.grid_remove()
                        self.hub_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
                        self.update_idletasks()
                        w, h = self.hub_canvas.winfo_width(), self.hub_canvas.winfo_height()
                        if w <= 1: w, h = 600, 600
                    
                        def on_node_clicked(node_id, can_purchase):
                            self.input_queue.put({"action": "node_click", "node_id": node_id, "can_purchase": can_purchase})
                            self.clear_buttons()
                            lbl = ctk.CTkLabel(self.buttons_frame, text="处理节点...")
                            lbl.pack(pady=10)
                        
                        self.hub_renderer.setup(w, h, msg["nodes"], msg["unlocked"], on_node_clicked, msg.get("player_stats"))
                        self.is_in_hub = True
                    elif msg_type == "update_enhancement_hub":
                        self.hub_renderer.update_unlocks(msg["unlocked"], msg.get("player_stats"))
                    elif msg_type == "end_enhancement_hub":
                        self.hub_frame.grid_remove()
                        self.text_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
                        self.is_in_hub = False
                    elif msg_type == "start_map_exploration":
                        self.text_frame.grid_remove()
                        self.hub_frame.grid_remove()
                        self.inventory_frame.grid_remove()
                        self.map_frame.grid_remove()
                        
                        # Show FX frame first
                        self.fx_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
                        self.fx_frame.tkraise()
                        self.update_idletasks()
                        
                        def launch_map(m_data=msg["map_data"], p_x=msg["player_x"], p_y=msg["player_y"]):
                            self.fx_frame.grid_remove()
                            self.map_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
                            self.update_idletasks()
                            w, h = self.map_canvas.winfo_width(), self.map_canvas.winfo_height()
                            if w <= 1: w, h = 600, 600
                        
                            def on_move_clicked(cx, cy):
                                self.input_queue.put({"action": "move", "x": cx, "y": cy})
                                self.clear_buttons()
                                lbl = ctk.CTkLabel(self.buttons_frame, text="移动中...")
                                lbl.pack(pady=10)
                            
                            self.map_renderer.setup(w, h, m_data, p_x, p_y, on_move_clicked)
                            self.is_in_map = True
                            
                        self.fx_renderer.start_vortex(duration_ms=1500, on_complete=launch_map)
                    elif msg_type == "update_map_pos":
                        self.map_renderer.update_map(msg["map_data"])
                        self.map_renderer.update_player_pos(msg["x"], msg["y"])
                    elif msg_type == "end_map_exploration":
                        self.map_frame.grid_remove()
                        self.text_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
                        self.is_in_map = False
                    elif msg_type == "start_visual_inventory":
                        self.text_frame.grid_remove()
                        self.inventory_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
                        self.update_idletasks()
                        w, h = self.inv_canvas.winfo_width(), self.inv_canvas.winfo_height()
                        if w <= 1: w, h = 600, 600
                    
                        def on_inv_action(action_id):
                            self.input_queue.put({"action": action_id})
                            self.clear_buttons()
                            lbl = ctk.CTkLabel(self.buttons_frame, text="处理中...")
                            lbl.pack(pady=10)
                        
                        self.inv_renderer.setup(w, h, msg["player_data"], on_inv_action)
                        self.is_in_inventory = True
                    elif msg_type == "update_visual_inventory":
                        self.inv_renderer.update_data(msg["player_data"])
                    elif msg_type == "end_visual_inventory":
                        self.inventory_frame.grid_remove()
                        self.text_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
                        self.is_in_inventory = False
                    elif msg_type == "combat_event":
                        self.combat_renderer.process_event(msg["event"])
                except Exception as e:
                    import traceback
                    err_msg = traceback.format_exc()
                    self.log_error(f"由于执行 {msg_type} 消息导致 GUI 错误:\n{err_msg}")
                    if hasattr(self, 'text_frame'):
                        self.text_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
                        self.text_frame.tkraise()
                    self.print_text(f"[GUI 错误] 队列消息 '{msg_type}' 处理失败, 请查看 error_log.txt", "red")
        except queue.Empty:
            pass
            
        try:
            if self.is_in_combat:
                self.combat_renderer.step()
            if self.is_in_hub:
                self.hub_renderer.step()
        except Exception as e:
            import traceback
            err_msg = traceback.format_exc()
            self.log_error(f"GUI 渲染帧更新失败:\n{err_msg}")
            if hasattr(self, 'text_frame'):
                self.text_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
                self.text_frame.tkraise()
            self.print_text(f"[GUI 渲染错误] 帧更新失败, 详情请查看 error_log.txt", "red")
            self.is_in_combat = False
            self.is_in_hub = False
            
        self.after(50, self.process_queue)
        
    def log_error(self, message):
        """将错误写入 error_log.txt"""
        import datetime
        try:
            with open("error_log.txt", "a", encoding="utf-8") as f:
                f.write(f"\n[{datetime.datetime.now()}] {message}\n" + "-"*50 + "\n")
        except:
            pass
        
    def _on_button_click(self, val):
        self.input_queue.put(val)
        # 点击后禁用按钮，防止连点
        self.clear_buttons()
        # 显示加载状态
        lbl = ctk.CTkLabel(self.buttons_frame, text="处理中...")
        lbl.pack(pady=10)

    # 供游戏逻辑线程调用的接口
    def gui_print(self, text, color="white"):
        self.event_queue.put({"type": "print", "text": text, "color": color})

    def gui_clear(self):
        self.event_queue.put({"type": "clear"})
        
    def gui_update_status(self, text):
        self.event_queue.put({"type": "update_status", "text": text})

    def gui_get_input(self, options=None, is_hub=False, is_map=False, is_inv=False):
        if options is None:
            # 对话确认框
            options = {"ENTER": "继续 / 确认"}
        
        self.event_queue.put({"type": "menu", "options": options})
        # 阻塞游戏线程，等待主线程 UI 队列返回结果
        return self.input_queue.get()
        
    def gui_get_text_input(self, prompt="请输入:"):
        self.event_queue.put({"type": "text_input", "prompt": prompt})
        # 阻塞游戏线程等待文本
        return self.input_queue.get()

    def gui_start_visual_combat(self, p_team, e_team):
        self.event_queue.put({
            "type": "start_visual_combat",
            "p_team": p_team,
            "e_team": e_team
        })
        
    def gui_end_visual_combat(self):
        self.event_queue.put({"type": "end_visual_combat"})
        
    def gui_start_enhancement_hub(self, nodes, unlocked_ids, player_stats=None):
        self.event_queue.put({
            "type": "start_enhancement_hub",
            "nodes": nodes,
            "unlocked": unlocked_ids,
            "player_stats": player_stats
        })
        
    def gui_update_enhancement_hub(self, unlocked_ids, player_stats=None):
        self.event_queue.put({
            "type": "update_enhancement_hub",
            "unlocked": unlocked_ids,
            "player_stats": player_stats
        })
        
    def gui_end_enhancement_hub(self):
        self.event_queue.put({"type": "end_enhancement_hub"})

    def gui_start_map_exploration(self, map_data, px, py):
        self.event_queue.put({
            "type": "start_map_exploration",
            "map_data": map_data,
            "player_x": px,
            "player_y": py
        })
        
    def gui_update_map_pos(self, px, py, map_data):
        self.event_queue.put({
            "type": "update_map_pos",
            "x": px,
            "y": py,
            "map_data": map_data
        })
        
    def gui_end_map_exploration(self):
        self.event_queue.put({"type": "end_map_exploration"})
        
    def gui_start_visual_inventory(self, player_data):
        self.event_queue.put({
            "type": "start_visual_inventory",
            "player_data": player_data
        })
        
    def gui_update_visual_inventory(self, player_data):
        self.event_queue.put({
            "type": "update_visual_inventory",
            "player_data": player_data
        })
        
    def gui_end_visual_inventory(self):
        self.event_queue.put({"type": "end_visual_inventory"})
        
    def gui_combat_event(self, event):
        self.event_queue.put({"type": "combat_event", "event": event})

if __name__ == "__main__":
    from game import Game
    game_instance = Game()
    app = GUI(game_instance)
    app.start()