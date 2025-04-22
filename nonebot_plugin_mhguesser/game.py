import random
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from nonebot.adapters import Event
from .config import plugin_config

class MonsterGuesser:
    def __init__(self):
        self.games: Dict[str, Dict] = {}  # {group_id: game_data}
        self.data_path = Path(__file__).parent / "resources/data/monsters.json"
        self.monsters = self._load_data()
        self.max_attempts = plugin_config.mhguesser_max_attempts
    
    def _load_data(self) -> List[Dict]:
        with open(self.data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def get_game(self, event: Event) -> Optional[Dict]:
        group_id = getattr(event, "group_id", "private")
        return self.games.get(group_id)
    
    def start_new_game(self, event: Event) -> Dict:
        group_id = getattr(event, "group_id", "private")
        self.games[group_id] = {
            "monster": random.choice(self.monsters),
            "guesses": [],
            "start_time": datetime.now()
        }
        return self.games[group_id]
    
    def guess(self, event: Event, name: str) -> Tuple[bool, Optional[Dict], Dict]:
        game = self.get_game(event)
        if not game or len(game["guesses"]) >= self.max_attempts:
            raise ValueError("游戏已结束")

        guessed = next((m for m in self.monsters if m["name"] == name), None)
        if not guessed:
            return False, None, {}

        game["guesses"].append(guessed)
        current = game["monster"]

        comparison = {
            "species": guessed["species"] == current["species"],
            "debut": guessed["debut"] == current["debut"],
            "baseId": guessed["baseId"] == current["baseId"],
            "variants": guessed["variants"] == current["variants"],
            "variantType": guessed["variantType"] == current["variantType"],
            "size": "higher" if guessed["size"] > current["size"] 
                    else "lower" if guessed["size"] < current["size"] 
                    else "same",
            "attributes": self._compare_attributes(
                guessed["attributes"], 
                current["attributes"]
            )
        }
        return guessed["name"] == current["name"], guessed, comparison
        
    def _compare_attributes(self, guess_attr: str, target_attr: str) -> Dict:
        guess_attrs = guess_attr.split("/") if guess_attr else []
        target_attrs = target_attr.split("/") if target_attr else []
        common = set(guess_attrs) & set(target_attrs)
        return {
            "guess": guess_attr,
            "target": target_attr,
            "common": list(common) if common else []
        }
    
    def end_game(self, event: Event):
        group_id = getattr(event, "group_id", "private")
        self.games.pop(group_id, None)