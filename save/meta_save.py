import json
import os
import sys

class MetaSaveSystem:
    def __init__(self):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(__file__))
        self.file_path = os.path.join(base_dir, "data", "meta_save.json")
        self.marks = 0
        self.unlocked_perks = []
        self.achievements = []
        self.load()
        
    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.marks = data.get("marks", 0)
                    self.unlocked_perks = data.get("unlocked_perks", [])
                    self.achievements = data.get("achievements", [])
            except Exception:
                self.marks = 0
                self.unlocked_perks = []
                
    def save(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        data = {
            "marks": self.marks,
            "unlocked_perks": self.unlocked_perks,
            "achievements": self.achievements
        }
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
    def add_marks(self, amount):
        self.marks += amount
        self.save()
        
    def spend_marks(self, amount):
        if self.marks >= amount:
            self.marks -= amount
            self.save()
            return True
        return False
