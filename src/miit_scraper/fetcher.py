"""列表页 API 请求模块。

通过工信部 CMS（大汉版通）的 jpaas-publish-server 接口获取时政要闻文章列表。

API 端点: /api-gateway/jpaas-publish-server/front/page/build/unit
返回 JSON 包裹的 HTML 片段，需 BeautifulSoup 二次解析提取文章信息。
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional
from .models import Article, ArticleList

# API 端点配置
BASE_URL = "https://www.miit.gov.cn"
API_URL = f"{BASE_URL}/api-gateway/jpaas-publish-server/front/page/build/unit"

# 从页面源码中提取的固定参数
API_PARAMS = {
    "parseType": "buildstatic",
    "webId": "8d828e408d90447786ddbe128d495e9e",
    "tplSetId": "209741b2109044b5b7695700b2bec37e",
    "pageType": "column",
    "tagId": "右侧内容",
    "pageId": "6333578be1d646aabc3e0e79406688c9",
}

# HTTP 请求头（模拟浏览器）
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": f"{BASE_URL}/xwdt/szyw/",
    "Accept": "application/json, text/javascript, */*; q=0.01",
}


def _fetch_api_response(page: int = 1, page_size: int = 10) -> dict:
    """调用 jpaas-publish-server API 获取原始响应。

    Args:
        page: 页码（从 1 开始）
        page_size: 每页数量

    Returns:
        API 返回的 JSON 字典 (data.html 中包含文章列表 HTML 片段)

    Raises:
        requests.RequestException: 网络请求失败
        ValueError: API 返回错误响应
    """
    params = {
        **API_PARAMS,
        "pageNo": page,
        "pageSize": page_size,
    }
    resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if not data.get("success"):
        raise ValueError(f"API 返回失败: {data.get('message', '未知错误')}")

    return data


def _parse_article_html(html_fragment: str) -> list[Article]:
    """从 API 返回的 HTML 片段中解析文章列表。

    HTML 结构示例:
        <li class="cf">
            <a class="fl" href="/xwfb/szyw/art/2026/art_xxx.html"
               target="_blank" title="文章标题">
                <i></i>文章标题
            </a>
            <span class="fr">2026-05-17</span>
        </li>

    Args:
        html_fragment: data.html 字段中的 HTML 字符串

    Returns:
        Article 对象列表
    """
    soup = BeautifulSoup(html_fragment, "html.parser")
    articles: list[Article] = []

    for li in soup.select("ul li.cf"):
        a_tag = li.select_one("a.fl")
        span_tag = li.select_one("span.fr")

        if not a_tag:
            continue

        # 提取标题：优先使用 title 属性，否则使用文本
        title = a_tag.get("title", "").strip() or a_tag.get_text(strip=True)

        # 提取相对 URL
        href = a_tag.get("href", "").strip()

        # 补全为绝对 URL
        if href and not href.startswith("http"):
            full_url = BASE_URL + href
        else:
            full_url = href

        # 提取发布日期
        publish_date: Optional[datetime] = None
        if span_tag:
            date_str = span_tag.get_text(strip=True)
            try:
                publish_date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                pass

        # 从 URL 中提取 article_id（如 art_0b816246f57f4866af5fad7efc87040a）
        article_id = ""
        if href:
            # URL 格式: /xwfb/szyw/art/2026/art_{uuid}.html
            parts = href.rstrip("/").split("/")
            if parts:
                last_part = parts[-1]
                if last_part.endswith(".html"):
                    article_id = last_part[:-5]  # 去掉 .html 后缀
                else:
                    article_id = last_part

        article = Article(
            article_id=article_id,
            title=title,
            publish_date=publish_date,
            url=full_url,
        )
        articles.append(article)

    return articles


def fetch_article_list(page: int = 1, page_size: int = 10) -> ArticleList:
    """获取时政要闻文章列表。

    调用工信部 CMS API，解析返回的 HTML 片段，
    提取文章标题、URL、发布日期，封装为 ArticleList。

    Args:
        page: 页码（从 1 开始）
        page_size: 每页数量

    Returns:
        ArticleList 对象，包含文章列表和分页信息

    Raises:
        requests.RequestException: 网络请求失败
        ValueError: API 返回错误或 HTML 解析失败
    """
    data = _fetch_api_response(page=page, page_size=page_size)
    html_fragment = data.get("data", {}).get("html", "")

    if not html_fragment:
        raise ValueError("API 返回的 HTML 片段为空")

    articles = _parse_article_html(html_fragment)

    # API 不直接返回 total，通过解析 HTML 获取（或设默认值）
    # 尝试从 HTML 中提取总记录数
    total = _extract_total_count(html_fragment)

    return ArticleList(
        total=total,
        articles=articles,
        page=page,
        page_size=page_size,
    )


def _extract_total_count(html_fragment: str) -> int:
    """尝试从 HTML 片段中提取总记录数。

    CMS 可能在分页区域包含总记录数信息。
    目前 API 返回不明确提供 total，返回已解析的文章数作为 fallback。

    Args:
        html_fragment: API 返回的 HTML 片段

    Returns:
        总记录数（如果无法确定则返回 0）
    """
    soup = BeautifulSoup(html_fragment, "html.parser")
    # 尝试查找分页信息中的总记录数
    page_div = soup.select_one("div.page")
    if page_div:
        text = page_div.get_text()
        # 尝试匹配 "共 X 条" 或 "共 X 页"
        import re
        m = re.search(r"共\s*(\d+)\s*条", text)
        if m:
            return int(m.group(1))
    return 0