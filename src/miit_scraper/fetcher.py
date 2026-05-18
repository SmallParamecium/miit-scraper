"""列表页 API 请求模块。

负责从工信部时政要闻列表 API 获取文章列表数据。
"""

import requests
from .models import Article, ArticleList


API_URL = "https://www.miit.gov.cn/xwdt/szyw/"

# TODO: Issue #2 实现 - API 探测与列表页解析
# 目标：发现实际的列表 API endpoint，解析返回的 JSON 获取最新 N 篇文章
# 包含：URL、标题、发布日期等基础信息


def fetch_article_list(page: int = 1, page_size: int = 10) -> ArticleList:
    """获取文章列表。

    Args:
        page: 页码
        page_size: 每页数量

    Returns:
        ArticleList 对象

    Raises:
        NotImplementedError: 功能尚未实现
    """
    raise NotImplementedError("列表页 API 解析将在 Issue #2 中实现")