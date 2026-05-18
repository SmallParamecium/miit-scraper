"""文章详情页解析模块。

负责抓取单篇文章的 HTML 页面，清洗提取正文内容。

详情页结构（2026年5月实测）：
- 直接 GET 请求页面 URL（需带 Referer 头）
- 正文容器：div#con_con > p 标签
- 元数据通过 <meta name="..." content="..."> 标签提供：
  - ArticleTitle → 标题
  - PubDate → 发布日期（如 2026-05-18 10:19）
  - ContentSource → 来源（如 新华社）
  - Description → 摘要
  - Keywords → 关键词
  - ColumnName → 栏目名称
"""

import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional

from .models import Article

BASE_URL = "https://www.miit.gov.cn"

META_FIELD_MAP = {
    "ArticleTitle": "title",
    "PubDate": "pub_date_raw",
    "ContentSource": "source",
    "Description": "description",
    "Keywords": "keywords_raw",
    "ColumnName": "column",
    "SiteName": "site_name",
    "Url": "rel_url",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.miit.gov.cn/xwfb/szyw/",
}


def parse_article_html(html: str) -> dict:
    """从文章详情页 HTML 中提取结构化内容。

    Args:
        html: 详情页 HTML 源码

    Returns:
        包含 content_text, source, publish_date, keywords, description, title 的字典
        字段说明：
          - title: 从 meta ArticleTitle 解析的文章标题（可为空字符串）
          - content_text: 从 div#con_con 提取的纯文本正文
          - source: 文章来源（meta ContentSource）
          - publish_date: datetime 对象，若解析失败则为 None
          - keywords: 关键词列表（以逗号分隔）
          - description: 文章摘要
          - pub_date_raw: meta 中的原始日期字符串
          - column: 所属栏目名称
    """
    soup = BeautifulSoup(html, "html.parser")

    # ---------- 1. 提取 meta 元数据 ----------
    meta_data: dict[str, str] = {}
    for meta_tag in soup.find_all("meta"):
        name = meta_tag.get("name", "")
        content = meta_tag.get("content", "")
        if name in META_FIELD_MAP:
            meta_data[META_FIELD_MAP[name]] = content.strip()

    # ---------- 2. 提取正文 ----------
    content_parts: list[str] = []
    con_div = soup.find("div", id="con_con")
    if con_div:
        # 移除 script 和 style 标签
        for tag in con_div.find_all(["script", "style"]):
            tag.decompose()
        # 提取所有 p 标签文本
        for p in con_div.find_all("p"):
            text = p.get_text(separator=" ", strip=True)
            if text:
                content_parts.append(text)
    content_text = "\n\n".join(content_parts)

    # ---------- 3. 解析发布日期 ----------
    pub_date_raw = meta_data.get("pub_date_raw", "")
    publish_date: Optional[datetime] = None
    if pub_date_raw:
        # 尝试多种格式：2026-05-18 10:19 或 2026-05-18
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                publish_date = datetime.strptime(pub_date_raw[:16], fmt)
                break
            except ValueError:
                continue

    # ---------- 4. 解析关键词 ----------
    keywords_raw = meta_data.get("keywords_raw", "")
    keywords = [kw.strip() for kw in keywords_raw.split(",") if kw.strip()]

    # ---------- 5. 标题以 meta ArticleTitle 为准 ----------
    title = meta_data.get("title", "")

    return {
        "title": title,
        "content_text": content_text,
        "source": meta_data.get("source", ""),
        "publish_date": publish_date,
        "keywords": keywords,
        "description": meta_data.get("description", ""),
        "pub_date_raw": pub_date_raw,
        "column": meta_data.get("column", ""),
    }


def fetch_and_parse_article(url: str) -> Article:
    """获取并解析单篇文章。

    构建完整的绝对 URL，请求详情页 HTML，
    调用 parse_article_html() 提取结构化内容，
    填充并返回 Article 对象。

    Args:
        url: 文章详情页 URL（可以是相对路径或完整 URL）

    Returns:
        填充了完整内容的 Article 对象

    Raises:
        requests.RequestException: 网络请求失败
        ValueError: 响应内容无效
    """
    # 补全相对 URL
    if not url.startswith("http"):
        full_url = BASE_URL + url
    else:
        full_url = url

    resp = requests.get(full_url, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    if not resp.text:
        raise ValueError(f"详情页返回空内容: {full_url}")

    parsed = parse_article_html(resp.text)

    # 从 URL 中提取 article_id
    article_id = ""
    # URL 格式: .../art_{uuid}.html
    parts = full_url.rstrip("/").split("/")
    if parts:
        last_part = parts[-1]
        if last_part.endswith(".html"):
            article_id = last_part[:-5]
        else:
            article_id = last_part

    return Article(
        article_id=article_id,
        title=parsed["title"],
        publish_date=parsed["publish_date"],
        url=full_url,
        source=parsed["source"],
        content_text=parsed["content_text"],
    )
