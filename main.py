import sys
import os

# 确保能找到其他模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game import Game
from gui_main import GUI

def main():
    game = Game()
    app = GUI(game)
    app.start()

if __name__ == "__main__":
    main()
