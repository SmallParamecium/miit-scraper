"""输出导出模块。

负责将爬取的文章数据输出为不同格式：
- 原始 JSON（raw/ 目录）
- 格式化 Markdown（output/ 目录）
"""

import json
from pathlib import Path

from .models import Article


def save_raw_json(articles: list[Article], output_dir: str = "raw") -> list[Path]:
    """将文章原始数据保存为 JSON 文件，每篇文章一个文件。

    Args:
        articles: 文章列表
        output_dir: 输出目录

    Returns:
        已写入的文件路径列表

    Raises:
        OSError: 文件写入失败
    """
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []

    for article in articles:
        filename = f"{article.article_id}.json"
        file_path = root / filename
        data = article.to_dict()
        file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        saved.append(file_path)

    return saved


def save_markdown(articles: list[Article], output_dir: str = "output") -> list[Path]:
    """将文章格式化保存为 Markdown 文件，每篇文章一个文件。

    Markdown 格式:
        - 一级标题：文章标题
        - 元数据行（斜体）：发布日期、来源、原文链接
        - 分隔线
        - 正文内容
        - 附件链接（如有）

    Args:
        articles: 文章列表
        output_dir: 输出目录

    Returns:
        已写入的文件路径列表

    Raises:
        OSError: 文件写入失败
    """
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []

    for article in articles:
        filename = f"{article.article_id}.md"
        file_path = root / filename

        lines: list[str] = []
        # 标题
        lines.append(f"# {article.title}")
        lines.append("")

        # 元数据
        meta_parts: list[str] = []
        if article.publish_date:
            meta_parts.append(f"**发布日期**：{article.publish_date.strftime('%Y-%m-%d')}")
        if article.source:
            meta_parts.append(f"**来源**：{article.source}")
        if article.url:
            meta_parts.append(f"**原文链接**：[{article.url}]({article.url})")
        if meta_parts:
            for part in meta_parts:
                lines.append(f"*{part}*")
            lines.append("")

        # 分隔线
        lines.append("---")
        lines.append("")

        # 正文
        if article.content_text:
            lines.append(article.content_text)
            lines.append("")

        # 附件
        if article.attachments:
            lines.append("## 附件")
            lines.append("")
            for name, url in article.attachments.items():
                lines.append(f"- [{name}]({url})")
            lines.append("")

        file_path.write_text("\n".join(lines), encoding="utf-8")
        saved.append(file_path)

    return saved