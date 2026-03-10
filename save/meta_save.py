import json
import os

class MetaSaveSystem:
    def __init__(self):
        self.file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "meta_save.json")
        self.marks = 0
        self.unlocked_perks = []
        self.load()
        
    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.marks = data.get("marks", 0)
                    self.unlocked_perks = data.get("unlocked_perks", [])
            except Exception:
                self.marks = 0
                self.unlocked_perks = []
                
    def save(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        data = {
            "marks": self.marks,
            "unlocked_perks": self.unlocked_perks
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
