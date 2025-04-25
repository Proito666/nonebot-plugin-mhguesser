import random
import json
import difflib
from pypinyin import lazy_pinyin
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from nonebot.adapters import Event
from .config import plugin_config

class MonsterGuesser:
    def __init__(self):
        self.games: Dict[str, Dict] = {} 
        self.data_path = Path(__file__).parent / "resources/data/monsters.json"
        self.monsters = self._load_data()
        self.max_attempts = plugin_config.mhguesser_max_attempts
        self.monster_names = [m["name"] for m in self.monsters]  # 预加载怪物名称列表
        self.pinyin_monsters = [''.join(lazy_pinyin(monster)) for monster in self.monster_names] # 预加载怪物名称拼音列表

    def _load_data(self) -> List[Dict]:
        with open(self.data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def get_session_id(self, event) -> str:
        return f"group_{event.group_id}" if event.message_type == "group" else f"user_{event.user_id}"

    def get_game(self, event: Event) -> Optional[Dict]:
        return self.games.get(self.get_session_id(event))
    
    def start_new_game(self, event: Event) -> Dict:
        session_id = self.get_session_id(event)
        self.games[session_id] = {
            "monster": random.choice(self.monsters),
            "guesses": [],
            "start_time": datetime.now()
        }
        return self.games[session_id]
    
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
        
    def find_similar_monsters(self, name: str, n: int = 3) -> List[str]:
        # 使用difflib找到相似的怪物名称
        difflib_matches = difflib.get_close_matches(
            name, 
            self.monster_names,
            n=n,
            cutoff=0.6  #相似度阈值（0-1之间）
        )
        # 通过拼音精确匹配读音一样的怪物名称
        name_pinyin = ''.join(lazy_pinyin(name))  # 转换输入名称为拼音
        pinyin_matches = [self.monster_names[i] for i, pinyin in enumerate(self.pinyin_monsters) if pinyin == name_pinyin]
        
        all_matches = list(set(pinyin_matches + difflib_matches))
        return all_matches

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
        try:
            self.games.pop(self.get_session_id(event))
        except (AttributeError, KeyError):
            pass