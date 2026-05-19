"""fetcher.py 单元测试。

测试 API 响应解析、HTML 片段提取、Article 对象构建。
使用 mock 避免真实网络请求。
"""

import pytest
import json
from unittest.mock import Mock, patch
from datetime import datetime

from miit_scraper.models import Article, ArticleList
from miit_scraper.fetcher import (
    _parse_article_html,
    _extract_total_count,
    fetch_article_list,
)

# ---------- mock HTML 片段（模拟 API 返回的 data.html） ----------

MOCK_HTML_FRAGMENT = """
<div id="右侧内容">
  <div class="page-content">
    <ul>
        <li class="cf">
            <a class="fl" href="/xwfb/szyw/art/2026/art_abc123.html"
               target="_blank" title="测试文章标题一">
                <i></i>测试文章标题一
            </a>
            <span class="fr">2026-05-17</span>
        </li>
        <li class="cf">
            <a class="fl" href="/xwfb/szyw/art/2026/art_def456.html"
               target="_blank" title="测试文章标题二">
                <i></i>测试文章标题二
            </a>
            <span class="fr">2026-05-16</span>
        </li>
        <li class="cf border-line">
            <a class="fl" href="/xwfb/szyw/art/2026/art_ghi789.html"
               target="_blank" title="测试文章标题三">
                <i></i>测试文章标题三
            </a>
            <span class="fr">2026-05-15</span>
        </li>
    </ul>
  </div>
</div>
"""

MOCK_API_RESPONSE = {
    "roles": None,
    "permissions": None,
    "code": "200",
    "success": True,
    "data": {"html": MOCK_HTML_FRAGMENT},
}

MOCK_API_RESPONSE_FAILURE = {
    "success": False,
    "code": "200",
    "message": "参数错误",
}


class TestParseArticleHtml:
    """测试 HTML 片段解析"""

    def test_parse_basic(self):
        """基本解析：3 篇文章"""
        articles = _parse_article_html(MOCK_HTML_FRAGMENT)
        assert len(articles) == 3

    def test_parse_title(self):
        """解析标题"""
        articles = _parse_article_html(MOCK_HTML_FRAGMENT)
        assert articles[0].title == "测试文章标题一"
        assert articles[1].title == "测试文章标题二"

    def test_parse_url_absolute(self):
        """相对 URL 补全为绝对 URL"""
        articles = _parse_article_html(MOCK_HTML_FRAGMENT)
        assert articles[0].url == "https://www.miit.gov.cn/xwfb/szyw/art/2026/art_abc123.html"

    def test_parse_article_id(self):
        """从 URL 提取 article_id"""
        articles = _parse_article_html(MOCK_HTML_FRAGMENT)
        assert articles[0].article_id == "art_abc123"
        assert articles[1].article_id == "art_def456"

    def test_parse_date(self):
        """解析发布日期"""
        articles = _parse_article_html(MOCK_HTML_FRAGMENT)
        assert articles[0].publish_date == datetime(2026, 5, 17)
        assert articles[1].publish_date == datetime(2026, 5, 16)

    def test_parse_empty_html(self):
        """空 HTML"""
        articles = _parse_article_html("")
        assert articles == []

    def test_parse_no_li(self):
        """HTML 中无 li.cf 元素"""
        articles = _parse_article_html("<div><p>无文章</p></div>")
        assert articles == []

    def test_parse_title_fallback_to_text(self):
        """title 属性为空时 fallback 到文本内容"""
        html = """
        <ul><li class="cf">
            <a class="fl" href="/test.html">纯文本标题</a>
            <span class="fr">2026-05-17</span>
        </li></ul>
        """
        articles = _parse_article_html(html)
        assert articles[0].title == "纯文本标题"

    def test_parse_invalid_date(self):
        """日期格式无效时不抛异常，date 为 None"""
        html = """
        <ul><li class="cf">
            <a class="fl" href="/test.html" title="标题">标题</a>
            <span class="fr">无效日期</span>
        </li></ul>
        """
        articles = _parse_article_html(html)
        assert articles[0].publish_date is None


class TestExtractTotalCount:
    """测试提取总记录数"""

    def test_no_page_div(self):
        """无分页信息时返回 0"""
        assert _extract_total_count(MOCK_HTML_FRAGMENT) == 0

    def test_with_total(self):
        """有 '共 X 条' 信息"""
        html = '<div class="page">共 123 条</div>'
        assert _extract_total_count(html) == 123


class TestFetchArticleList:
    """测试完整的 fetch_article_list 函数（mock 网络请求）"""

    @patch("miit_scraper.fetcher.requests.get")
    def test_success(self, mock_get):
        """正常请求并解析"""
        mock_resp = Mock()
        mock_resp.json.return_value = MOCK_API_RESPONSE
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        result = fetch_article_list(page=1, page_size=10)
        assert isinstance(result, ArticleList)
        assert len(result.articles) == 3
        assert result.page == 1
        assert result.page_size == 10
        assert result.articles[0].title == "测试文章标题一"

    @patch("miit_scraper.fetcher.requests.get")
    def test_api_failure(self, mock_get):
        """API 返回 success=False"""
        mock_resp = Mock()
        mock_resp.json.return_value = MOCK_API_RESPONSE_FAILURE
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        with pytest.raises(ValueError, match="API 返回失败"):
            fetch_article_list()

    @patch("miit_scraper.fetcher.requests.get")
    def test_empty_html(self, mock_get):
        """API 返回空 HTML"""
        mock_resp = Mock()
        mock_resp.json.return_value = {
            "success": True,
            "data": {"html": ""},
        }
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        with pytest.raises(ValueError, match="HTML 片段为空"):
            fetch_article_list()