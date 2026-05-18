"""输出导出模块。

负责将爬取的文章数据输出为不同格式：
- 原始 JSON（raw/ 目录）
- 格式化 Markdown（output/ 目录）
"""

import json
from pathlib import Path

from .models import Article


# TODO: Issue #3 实现 - 文章数据输出
# 目标：
# 1. 将原始文章数据保存为 JSON（raw/ 目录）
# 2. 将文章内容格式化为 Markdown（output/ 目录）
# 3. Markdown 格式包含：标题、日期、来源、正文、附件链接


def save_raw_json(articles: list[Article], output_dir: str = "raw") -> None:
    """将文章原始数据保存为 JSON 文件。

    Args:
        articles: 文章列表
        output_dir: 输出目录

    Raises:
        NotImplementedError: 功能尚未实现
    """
    raise NotImplementedError("JSON 输出将在 Issue #3 中实现")


def save_markdown(articles: list[Article], output_dir: str = "output") -> None:
    """将文章格式化保存为 Markdown 文件。

    Args:
        articles: 文章列表
        output_dir: 输出目录

    Raises:
        NotImplementedError: 功能尚未实现
    """
    raise NotImplementedError("Markdown 输出将在 Issue #3 中实现")