import random
import json
import difflib
from pypinyin import lazy_pinyin
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from nonebot_plugin_uninfo import Uninfo
from .config import plugin_config


class MonsterGuesser:
    def __init__(self):
        self.games: Dict[str, Dict] = {}
        self.data_path = Path(__file__).parent / "resources/data/monsters.json"
        self.monsters = self._load_data()
        self.max_attempts = plugin_config.mhguesser_max_attempts
        self.monster_names = [m["name"] for m in self.monsters]  # 预加载怪物名称列表
        self.pinyin_monsters = [''.join(lazy_pinyin(monster)) for monster in self.monster_names]  # 预加载怪物名称拼音列表

        # 游戏作品发售顺序映射
        self.game_order = {
            "怪物猎人": 1, "怪物猎人G": 2, "怪物猎人P": 3, "怪物猎人2": 4, "怪物猎人P2": 5,
            "怪物猎人P2G": 6, "怪物猎人3": 7, "怪物猎人P3": 8, "怪物猎人3G": 9, "怪物猎人4": 10,
            "怪物猎人4G": 11, "怪物猎人X": 12, "怪物猎人XX": 13, "怪物猎人世界": 14, "怪物猎人世界冰原": 15,
            "怪物猎人崛起": 16, "怪物猎人崛起曙光": 17, "怪物猎人荒野": 18
        }

    def _load_data(self) -> List[Dict]:
        with open(self.data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_session_id(self, uninfo) -> str:
        return f"{uninfo.scope}_{uninfo.self_id}_{uninfo.scene_path}"

    def get_game(self, uninfo: Uninfo) -> Optional[Dict]:
        return self.games.get(self.get_session_id(uninfo))

    def start_new_game(self, uninfo: Uninfo) -> Dict:
        session_id = self.get_session_id(uninfo)
        self.games[session_id] = {
            "monster": random.choice(self.monsters),
            "guesses": [],
            "start_time": datetime.now()
        }
        return self.games[session_id]

    def guess(self, uninfo: Uninfo, name: str) -> Tuple[bool, Optional[Dict], Dict]:
        game = self.get_game(uninfo)
        if not game or len(game["guesses"]) >= self.max_attempts:
            raise ValueError("游戏已结束")

        guessed = next((m for m in self.monsters if m["name"] == name), None)
        if not guessed:
            return False, None, {}

        game["guesses"].append(guessed)
        current = game["monster"]

        # 比较初登场作品的顺序
        guess_debut_order = self.game_order.get(guessed["debut"], 999)
        current_debut_order = self.game_order.get(current["debut"], 999)
        debut_comparison = "same"
        if guess_debut_order < current_debut_order:
            debut_comparison = "earlier"
        elif guess_debut_order > current_debut_order:
            debut_comparison = "later"

        comparison = {
            "species": guessed["species"] == current["species"],
            "debut": guessed["debut"] == current["debut"],
            "debut_order": debut_comparison,
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
            cutoff=0.6  # 相似度阈值（0-1之间）
        )
        # 通过拼音精确匹配读音一样的怪物名称
        name_pinyin = ''.join(lazy_pinyin(name))  # 转换输入名称为拼音
        pinyin_matches = [self.monster_names[i] for i, pinyin in enumerate(self.pinyin_monsters) if
                          pinyin == name_pinyin]

        all_matches = list(dict.fromkeys(pinyin_matches + difflib_matches))
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

    def end_game(self, uninfo: Uninfo):
        try:
            self.games.pop(self.get_session_id(uninfo))
        except (AttributeError, KeyError):
            pass
