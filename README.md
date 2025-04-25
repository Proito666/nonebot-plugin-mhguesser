<div align="center">

# nonebot-plugin-mhguesser

_✨ <怪物猎人猜BOSS> ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/Proito666/nonebot-plugin-mhguesser" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot_plugin_mhguesser">
  <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/nonebot_plugin_mhguesser">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">
</div>


 [`怪物猎人：猜猜BOSS`](https://mhguesser.netlify.app/) 的nonebot插件简单实现

## 💿 安装
<details>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-mhguesser

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-mhguesser
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-mhguesser
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-mhguesser
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-mhguesser
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_mhguesser"]

</details>

## ⚙️ 配置

在 nonebot2 项目的 env 文件中添加配置

| 配置项 | 必填 | 类型 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| mhguesser_max_attempts | 否 | int | 10 | 最大尝试次数 |

## 🎉 使用
mhstart: 开始游戏

直接输入怪物名称进行猜测，若玩家猜测的怪物某项数据与答案怪物相同，对应的信息框将变为绿色。

结束：结束游戏


