from nonebot import on_message, get_driver, require
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Event
from nonebot.matcher import Matcher
from nonebot.rule import Rule
from nonebot.typing import T_State
require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import UniMessage, Image, on_alconna
import logging
from .config import Config

from .game import MonsterGuesser
from .render import render_guess_result, render_correct_answer

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-mhguesser",
    description="怪物猎人猜BOSS游戏",
    usage="""指令:
mhstart - 开始游戏
结束 - 结束游戏
直接输入怪物名猜测""",
    homepage="https://github.com/Proito666/nonebot-plugin-mhguesser",
    supported_adapters={"~onebot.v11"},
    type="application",
    config=Config,
)

game = MonsterGuesser()
logger = logging.getLogger(__name__)
driver = get_driver()

def is_playing() -> Rule:
    async def _checker(event: Event, state: T_State) -> bool:
        return bool(game.get_game(event))
    return Rule(_checker)

def is_end_command() -> Rule:
    async def _checker(event: Event, state: T_State) -> bool:
        return event.get_plaintext().strip() == "结束"
    return Rule(_checker)

start_cmd = on_alconna("mhstart", aliases={"怪物猎人开始"})
end_cmd = on_message(rule=is_end_command() & is_playing())
guess_matcher = on_message(rule=is_playing(), priority=15)

@start_cmd.handle()
async def handle_start(event: Event, matcher: Matcher):
    if game.get_game(event):
        await matcher.finish("游戏已在进行中！")
    
    game.start_new_game(event)
    await matcher.send(f"游戏开始！你有{game.max_attempts}次猜测机会，直接输入怪物名即可")

@end_cmd.handle()
async def handle_end(event: Event):
    monster = game.get_game(event)["monster"]
    game.end_game(event)
    img = await render_correct_answer(monster)
    await UniMessage(Image(raw=img)).send()

@guess_matcher.handle()
async def handle_guess(event: Event):
    # 检查游戏状态
    game_data = game.get_game(event)
    if not game_data:
        return
    guess_name = event.get_plaintext().strip()
    if not guess_name or guess_name in ("结束", "mhstart"):
        return
    # 检查重复猜测
    if any(g["name"] == guess_name for g in game_data["guesses"]):
        await UniMessage.text(f"已经猜过【{guess_name}】了，请尝试其他怪物").send()
        return
        
    guess_name = event.get_plaintext().strip()
    correct, guessed, comparison = game.guess(event, guess_name)
    
    if correct:
        game.end_game(event)
        img = await render_correct_answer(guessed)
        await UniMessage([
            "猜对了！正确答案：",
            Image(raw=img)
        ]).send()
        return
    
    if not guessed:
        await guess_matcher.finish("怪物名称不正确，请重新输入")
    
    attempts_left = game.max_attempts - len(game_data["guesses"])
    # 检查尝试次数
    if attempts_left <= 0:
        monster = game_data["monster"]
        game.end_game(event)
        img = await render_correct_answer(monster)
        await UniMessage([
            "尝试次数已用尽！正确答案：",
            Image(raw=img)
        ]).send()
        return
    
    img = await render_guess_result(guessed, comparison, attempts_left)
    await UniMessage(Image(raw=img)).send()
    