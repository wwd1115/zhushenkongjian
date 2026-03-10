import json
import os

class LeaderboardSystem:
    def __init__(self):
        self.file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "leaderboard.json")
        self.records = []
        self.load()
        
    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.records = json.load(f)
            except Exception:
                self.records = []
                
    def save(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.records, f, ensure_ascii=False, indent=4)
            
    def update_record(self, name, score, details=""):
        # find if exists, update if higher
        for r in self.records:
            if r["name"] == name:
                if score > r["score"]:
                    r["score"] = score
                    r["details"] = details
                # sort and save
                self.records.sort(key=lambda x: x["score"], reverse=True)
                self.save()
                return
        self.records.append({"name": name, "score": score, "details": details})
        self.records.sort(key=lambda x: x["score"], reverse=True)
        self.save()
        
    def get_top(self, n=10):
        return self.records[:n]
