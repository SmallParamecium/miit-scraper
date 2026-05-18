"""文章详情页解析模块。

负责抓取单篇文章的 HTML 页面，清洗提取正文内容。
"""

from bs4 import BeautifulSoup

from .models import Article


# TODO: Issue #3 实现 - 文章详情页抓取与正文提取
# 目标：
# 1. 根据 Article.url 请求详情页 HTML
# 2. 使用 BeautifulSoup + lxml 解析并提取正文、来源、日期
# 3. 清洗 HTML 标签，保留纯文本
# 4. 检测并收集附件链接（PDF/Word 等）


def parse_article_html(html: str) -> dict:
    """从文章详情页 HTML 中提取结构化内容。

    Args:
        html: 详情页 HTML 源码

    Returns:
        包含 content_text, source, publish_date, attachments 的字典

    Raises:
        NotImplementedError: 功能尚未实现
    """
    raise NotImplementedError("文章详情页解析将在 Issue #3 中实现")


def fetch_and_parse_article(url: str) -> Article:
    """获取并解析单篇文章。

    Args:
        url: 文章详情页 URL

    Returns:
        填充了完整内容的 Article 对象

    Raises:
        NotImplementedError: 功能尚未实现
    """
    raise NotImplementedError("文章详情页抓取将在 Issue #3 中实现")