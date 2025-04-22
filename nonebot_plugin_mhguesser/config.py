from nonebot import get_plugin_config
from pydantic import BaseModel, Field

class Config(BaseModel):
    mhguesser_max_attempts: int = Field(10, alias="怪物猎人最大尝试次数")

plugin_config = get_plugin_config(Config)