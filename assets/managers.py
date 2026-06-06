import json
import os

# ============================================================================
# MANAGERS
# ============================================================================

class ScoreManager:
    """Manages scores, high scores, and game difficulty"""
    SCORE_FILE = "highscore.json"
    
    def __init__(self):
        self.score = 0
        data = self.load_data()
        self.high_score = data.get("high_score", 0)
        self.recent_scores = data.get("recent_scores", [])
        self.last_mode = data.get("last_mode", "NORMAL")
    
    def load_data(self):
        """Load all score data from file"""
        if os.path.exists(self.SCORE_FILE):
            try:
                with open(self.SCORE_FILE, 'r') as f: 
                    return json.load(f)
            except: 
                pass
        return {}
    
    def save_data(self):
        """Save all score data to file"""
        data = {
            "high_score": self.high_score,
            "recent_scores": self.recent_scores,
            "last_mode": self.last_mode
        }
        with open(self.SCORE_FILE, 'w') as f: 
            json.dump(data, f)
    
    def add_point(self):
        """Add one point to current score"""
        self.score += 1
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_data()
    
    def save_game_score(self):
        """Save current game score to recent scores"""
        self.recent_scores.insert(0, self.score)
        if len(self.recent_scores) > 3:
            self.recent_scores = self.recent_scores[:3]
        self.save_data()
    
    def reset(self): 
        """Reset current game score"""
        self.score = 0
    
    def get_medal(self):
        """Get medal type based on score"""
        if self.score >= 40: 
            return "platinum"
        elif self.score >= 30: 
            return "gold"
        elif self.score >= 20: 
            return "silver"
        elif self.score >= 10: 
            return "bronze"
        return None
