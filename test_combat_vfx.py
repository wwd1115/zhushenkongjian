import time
import threading
from game import Game
from gui_main import GUI
from classes.player import Player
from classes.enemy import Enemy
from classes.teammate import Teammate
from utils.combat_calc import CombatSystem

def test_combat():
    game = Game()
    app = GUI(game)
    
    # Mock player and enemy
    player = Player("Test Player")
    player.hp = 100
    player.max_hp = 100
    player.mp = 50
    player.max_mp = 50
    player.agi = 15
    player.skills = [
        {"name": "Fireball", "mp_cost": 10, "effect": "atk_up", "type": "active", "desc": "Deal heavy fire dmg"},
        {"name": "Ice Lance", "mp_cost": 15, "effect": "atk_up", "type": "active", "desc": "Deal ice dmg"},
        {"name": "Heal", "mp_cost": 20, "effect": "heal_100", "type": "active", "desc": "Restore 100 HP"}
    ]
    
    t1 = Teammate("Warrior Bob", hp=150, attack=25, defense=5, agi=8)
    t1.hp = t1.max_hp = 150
    t1.attack = 25
    t1.agi = 8
    
    t2 = Teammate("Archer Alice", hp=80, attack=35, defense=2, agi=20)
    t2.hp = t2.max_hp = 80
    t2.attack = 35
    t2.agi = 20
    
    player.teammates = [t1, t2]
    
    e1 = Enemy("Skeleton Grunt", hp=100, attack=15, speed=12)
    e2 = Enemy("Skeleton Captain", hp=200, attack=30, speed=10)
    e3 = Enemy("Skeleton Mage", hp=80, attack=40, speed=18)
    
    # We hijack the game start to just trigger our combat
    def custom_game_start():
        import utils.display as disp
        disp.set_gui_mode(app)
        
        # Give GUI time to show up
        time.sleep(1)
        
        cs = CombatSystem(player, [e1, e2, e3])
        cs.start_combat()
        
    app.game_thread = threading.Thread(target=custom_game_start, daemon=True)
    app.start()

if __name__ == "__main__":
    test_combat()
