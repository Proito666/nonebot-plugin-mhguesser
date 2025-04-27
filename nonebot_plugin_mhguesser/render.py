from pathlib import Path
from typing import Dict, Optional
from jinja2 import Environment, FileSystemLoader
from nonebot_plugin_htmlrender import md_to_pic

env = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "resources/templates"),
    autoescape=True
)

async def render_guess_result(
    guessed_monster: Optional[Dict],
    comparison: Dict,
    attempts_left: int
) -> bytes:
    # 属性高亮处理
    attributes = guessed_monster.get("attributes", "")
    attributes_html = ""
    if attributes:
        for attr in attributes.split("/"):
            if attr in comparison["attributes"]["common"]:
                attributes_html += f'<span class="attr-match">{attr}</span> '
            else:
                attributes_html += f'{attr} '

    html = env.get_template("guess.html").render(
        monster_name=guessed_monster["name"],
        attempts_left=attempts_left,
        species=guessed_monster["species"],
        species_correct=comparison["species"],
        debut=guessed_monster["debut"],
        debut_correct=comparison["debut"],
        baseId=guessed_monster["baseId"],
        baseId_correct=comparison["baseId"],
        variants=guessed_monster["variants"],
        variants_correct=comparison["variants"],
        variantType=guessed_monster["variantType"],
        variantType_correct=comparison["variantType"],
        size=guessed_monster['size'],
        size_class=comparison["size"],
        attributes=attributes_html,
        iconUrl=guessed_monster["iconUrl"],
        has_match=bool(comparison["attributes"]["common"])
    )
    return await md_to_pic(html, width=600)

async def render_correct_answer(monster: Dict) -> bytes:
    if not monster:
        return await md_to_pic("错误：怪物数据不存在", width=600)
    
    return await md_to_pic(
        env.get_template("correct.html").render(
            name=monster.get("name", "未知怪物"),
            species=monster.get("species", ""),
            debut=monster.get("debut", ""),
            variantType=monster.get("variantType", ""),
            baseId=monster.get("baseId", 0),
            size=monster.get("size", ""),
            attributes=monster.get("attributes", ""),
            variants=monster.get("variants", 0),
            iconUrl=monster.get("iconUrl", "")
        ),
        width=600
    )