from gui.enhancement_hub import EnhancementRenderer

class DummyCanvas:
    def __init__(self):
        self.lines = []
    def delete(self, *args): pass
    def create_rectangle(self, *args, **kwargs): return 1
    def create_line(self, *args, **kwargs):
        self.lines.append((args, kwargs))
        return 1
    def create_oval(self, *args, **kwargs): return 1
    def create_text(self, *args, **kwargs): return 1
    def create_polygon(self, *args, **kwargs): return 1
    def find_withtag(self, *args): return []
    def gettags(self, *args): return []
    def coords(self, *args): return [0, 0]
    def move(self, *args): pass
    def bind(self, *args): pass

class DummyApp:
    def __init__(self):
        self.after = lambda *args: None
    def bind(self, *args): pass

class DummyGame:
    def __init__(self, p):
        self.player = p

from scenes.main_god_space import MainGodSpace
from classes.player import Player

p = Player("Test")
p.bloodline = None
m = MainGodSpace(DummyGame(p))
nodes, unlocked = m._generate_enhancement_nodes()

hub = EnhancementRenderer(DummyCanvas())
hub.width = 800
hub.height = 600
hub.nodes = {}
for n in nodes:
    from gui.enhancement_hub import Node
    if n["type"] != "stat":
        hub.nodes[n["id"]] = Node(n["id"], n["name"], n["type"], n.get("data", {}), n["x"], n["y"], n.get("parents", []))

hub.current_tab = "bloodline"
hub.update_unlocks(unlocked)

for args, kwargs in hub.canvas.lines:
    if "dash" in kwargs:
        if kwargs["dash"] == (4, 2):
            print("ROOT DASH LINE:", args)
    else:
        print("SOLID LINE:", args)
