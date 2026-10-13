from pathlib import Path
from typing import Dict, Optional

from jinja2 import Environment, FileSystemLoader
from nonebot_plugin_htmlrender import get_default_application

env = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "resources/templates"),
    autoescape=True,
    enable_async=True
)
width = 400
height = 300

_GAMEKEE_HEADERS = {
    "Referer": "https://www.gamekee.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

async def _render_pic(html: str) -> bytes:
    playwright = get_default_application().extensions.playwright
    async with playwright.page(
        viewport={"width": width, "height": height},
        device_scale_factor=2.0,
        extra_http_headers=_GAMEKEE_HEADERS,
    ) as page:
        await page.set_content(html, wait_until="load")
        return await page.screenshot(full_page=True, type="png")


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
    return await _render_pic(html)


async def render_correct_answer(monster: Dict) -> bytes:
    template = env.get_template("correct.html")
    html = await template.render_async(monster=monster, width=width)
    return await _render_pic(html)
