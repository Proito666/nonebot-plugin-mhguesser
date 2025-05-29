from nonebot import on_message, get_driver, require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from nonebot.adapters import Event
from nonebot.matcher import Matcher
from nonebot.rule import Rule
require("nonebot_plugin_alconna")
require("nonebot_plugin_uninfo")
require("nonebot_plugin_htmlrender")

from nonebot_plugin_uninfo import Uninfo
from nonebot_plugin_alconna import UniMessage, Image, on_alconna
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
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_alconna", "nonebot_plugin_uninfo"
    ),
    type="application",
    config=Config,
)
game = MonsterGuesser()
driver = get_driver()

def is_playing() -> Rule:
    async def _checker(uninfo: Uninfo) -> bool:
        return bool(game.get_game(uninfo))
    return Rule(_checker)

start_cmd = on_alconna("mhstart", aliases={"怪物猎人开始"})
guess_matcher = on_message(rule=is_playing(), priority=15，block=False))

@start_cmd.handle()
async def handle_start(uninfo: Uninfo, matcher: Matcher):
    if game.get_game(uninfo):
        await matcher.finish("游戏已在进行中！")
    
    game.start_new_game(uninfo)
    await matcher.send(f"游戏开始！你有{game.max_attempts}次猜测机会，直接输入怪物名即可")

async def handle_end(uninfo: Uninfo):
    monster = game.get_game(uninfo)["monster"]
    game.end_game(uninfo)
    img = await render_correct_answer(monster)
    await UniMessage(Image(raw=img)).send()

@guess_matcher.handle()
async def handle_guess(uninfo: Uninfo, event: Event):
    guess_name = event.get_plaintext().strip()
    if guess_name in ("", "结束", "mhstart"):
        if guess_name == "结束":
            await handle_end(uninfo)
        return
    # 检查游戏状态
    game_data = game.get_game(uninfo)
    if not game_data:
        return
    # 检查重复猜测
    if any(g["name"] == guess_name for g in game_data["guesses"]):
        await UniMessage.text(f"已经猜过【{guess_name}】了，请尝试其他怪物").send()
        return
        
    correct, guessed, comparison = game.guess(uninfo, guess_name)
    
    if correct:
        game.end_game(uninfo)
        img = await render_correct_answer(guessed)
        await UniMessage([
            "猜对了！正确答案：",
            Image(raw=img)
        ]).send()
        return
    
    if not guessed:
        similar = game.find_similar_monsters(guess_name)
        if not similar:
            return
        err_msg = f"未找到怪物【{guess_name}】！\n尝试以下结果：" + "、".join(similar)
        await guess_matcher.finish(err_msg)
            
    
    attempts_left = game.max_attempts - len(game_data["guesses"])
    # 检查尝试次数
    if attempts_left <= 0:
        monster = game_data["monster"]
        game.end_game(uninfo)
        img = await render_correct_answer(monster)
        await UniMessage([
            "尝试次数已用尽！正确答案：",
            Image(raw=img)
        ]).send()
        return
    
    img = await render_guess_result(guessed, comparison, attempts_left)
    await UniMessage(Image(raw=img)).send()
    