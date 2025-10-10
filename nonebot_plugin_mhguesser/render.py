from pathlib import Path
from typing import Dict, Optional
from jinja2 import Environment, FileSystemLoader
from nonebot_plugin_htmlrender import html_to_pic

env = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "resources/templates"),
    autoescape=True,
    enable_async=True
)
width=400
height=300

async def render_guess_result(
    guessed_monster: Optional[Dict],
    comparison: Dict,
    attempts_left: int
) -> bytes:
    template = env.get_template("guess.html")
    html = await template.render_async(
        attempts_left=attempts_left,
        guessed_monster=guessed_monster,
        comparison=comparison,
        width=width
    )
    return await html_to_pic(html, viewport={"width": width, "height": height})

async def render_correct_answer(monster: Dict) -> bytes:
    template = env.get_template("correct.html")
    html = await template.render_async(monster=monster, width=width)
    return await html_to_pic(html, viewport={"width": width, "height": height})
