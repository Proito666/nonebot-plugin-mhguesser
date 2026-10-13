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

# gamekee 图片防盗链所需的请求头（CDN 对无 Referer 的请求返回 567）
_GAMEKEE_HEADERS = {
    "Referer": "https://www.gamekee.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}


async def _render_pic(html: str) -> bytes:
    """将 HTML 渲染为 PNG 图片字节。

    htmlrender 0.8+ 顶层 render_html 不再支持自定义请求头，而 gamekee
    图片依赖 Referer 防盗链，因此通过 PlaywrightAccess 能力租用带请求头
    的页面手动截图。
    """
    playwright = get_default_application().extensions.playwright
    async with playwright.page(
        viewport={"width": width, "height": height},
        device_scale_factor=2.0,
        extra_http_headers=_GAMEKEE_HEADERS,
        user_agent=_GAMEKEE_HEADERS["User-Agent"],
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
