"""parser.py 单元测试。

测试详情页 HTML 解析、meta 元数据提取、正文清洗、异常处理。
使用 mock 模拟网络请求。
"""

import pytest
from unittest.mock import Mock, patch, ANY
from datetime import datetime

from miit_scraper.models import Article
from miit_scraper.parser import parse_article_html, fetch_and_parse_article

# ---------- Mock 完整详情页 HTML（模拟实际页面结构） ----------

MOCK_DETAIL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>习近平就推动哲学社会科学高质量发展作出重要指示</title>
    <meta name="SiteName" content="中华人民共和国工业和信息化部">
    <meta name="SiteDomain" content="www.miit.gov.cn">
    <meta name="SiteIDCode" content="bm07000001">
    <meta name="ColumnName" content="时政要闻">
    <meta name="ColumnType" content="时政要闻">
    <meta name="ArticleTitle" content="习近平就推动哲学社会科学高质量发展作出重要指示">
    <meta name="PubDate" content="2026-05-18 10:19">
    <meta name="ContentSource" content="新华社">
    <meta name="Keywords" content="哲学,社会科学,中国,党,创新">
    <meta name="Author" content="">
    <meta name="Description" content="习近平就推动哲学社会科学高质量发展作出重要指示强调">
    <meta name="Url" content="/xwfb/szyw/art/2026/art_test123.html">
</head>
<body>
    <div class="ccontent center" id="con_con">
        <p style="text-align: center;">
            <strong>习近平就推动哲学社会科学高质量发展作出重要指示强调</strong>
        </p>
        <p style="text-indent: 2em;">
            新华社北京5月17日电 中共中央总书记、国家主席、中央军委主席习近平
            近日就推动哲学社会科学高质量发展作出重要指示指出。
        </p>
        <p style="text-indent: 2em;">
            习近平强调，新征程上，要以新时代中国特色社会主义思想为指导，
            加快构建中国哲学社会科学自主知识体系。
        </p>
        <script>console.log('should be removed');</script>
        <style>.hidden { display: none; }</style>
    </div>
</body>
</html>
"""

MOCK_DETAIL_HTML_NO_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta name="ArticleTitle" content="测试标题">
    <meta name="PubDate" content="2026-05-18">
    <meta name="ContentSource" content="新华社">
</head>
<body>
    <div id="con_con">
        <!-- 正文为空 -->
    </div>
</body>
</html>
"""

MOCK_DETAIL_HTML_NO_META = """
<!DOCTYPE html>
<html>
<body>
    <div id="con_con">
        <p>只有正文，没有meta数据。</p>
    </div>
</body>
</html>
"""


class TestParseArticleHtml:
    """测试 parse_article_html() 函数"""

    def test_parse_title(self):
        """从 meta ArticleTitle 提取标题"""
        result = parse_article_html(MOCK_DETAIL_HTML)
        assert result["title"] == "习近平就推动哲学社会科学高质量发展作出重要指示"

    def test_parse_source(self):
        """从 meta ContentSource 提取来源"""
        result = parse_article_html(MOCK_DETAIL_HTML)
        assert result["source"] == "新华社"

    def test_parse_publish_date(self):
        """解析发布日期为 datetime"""
        result = parse_article_html(MOCK_DETAIL_HTML)
        assert isinstance(result["publish_date"], datetime)
        assert result["publish_date"] == datetime(2026, 5, 18, 10, 19)

    def test_parse_keywords(self):
        """解析关键词列表"""
        result = parse_article_html(MOCK_DETAIL_HTML)
        assert result["keywords"] == ["哲学", "社会科学", "中国", "党", "创新"]

    def test_parse_description(self):
        """提取文章描述"""
        result = parse_article_html(MOCK_DETAIL_HTML)
        assert "习近平" in result["description"]

    def test_parse_content_text(self):
        """提取正文纯文本"""
        result = parse_article_html(MOCK_DETAIL_HTML)
        assert "习近平" in result["content_text"]
        assert "新华社北京5月17日电" in result["content_text"]
        # 不应包含 script 内容
        assert "console.log" not in result["content_text"]
        # 不应包含 style 内容
        assert ".hidden" not in result["content_text"]

    def test_parse_column(self):
        """提取栏目名称"""
        result = parse_article_html(MOCK_DETAIL_HTML)
        assert result["column"] == "时政要闻"

    def test_parse_empty_content(self):
        """正文为空的页面"""
        result = parse_article_html(MOCK_DETAIL_HTML_NO_CONTENT)
        assert result["content_text"] == ""
        assert result["title"] == "测试标题"

    def test_parse_no_meta(self):
        """无 meta 标签的页面"""
        result = parse_article_html(MOCK_DETAIL_HTML_NO_META)
        assert result["title"] == ""
        assert result["source"] == ""
        assert result["keywords"] == []
        assert result["publish_date"] is None
        assert "只有正文，没有meta数据" in result["content_text"]

    def test_parse_empty_html(self):
        """空 HTML 输入"""
        result = parse_article_html("")
        assert result["title"] == ""
        assert result["content_text"] == ""
        assert result["publish_date"] is None

    def test_parse_date_only(self):
        """发布日期仅有日期（无具体时间）"""
        result = parse_article_html(MOCK_DETAIL_HTML_NO_CONTENT)
        assert isinstance(result["publish_date"], datetime)
        assert result["publish_date"] == datetime(2026, 5, 18)

    def test_parse_invalid_date(self):
        """无效日期字符串"""
        html = """
        <html><head>
            <meta name="ArticleTitle" content="测试">
            <meta name="PubDate" content="无效日期格式">
        </head><body><div id="con_con"><p>正文</p></div></body></html>
        """
        result = parse_article_html(html)
        assert result["publish_date"] is None


class TestFetchAndParseArticle:
    """测试 fetch_and_parse_article() 函数（mock 网络请求）"""

    @patch("miit_scraper.parser.requests.get")
    def test_success(self, mock_get):
        """正常请求并解析文章详情"""
        mock_resp = Mock()
        mock_resp.text = MOCK_DETAIL_HTML
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        article = fetch_and_parse_article(
            "/xwfb/szyw/art/2026/art_test123.html"
        )

        assert isinstance(article, Article)
        assert article.article_id == "art_test123"
        assert article.title == "习近平就推动哲学社会科学高质量发展作出重要指示"
        assert article.source == "新华社"
        assert article.publish_date == datetime(2026, 5, 18, 10, 19)
        assert "习近平" in article.content_text
        assert article.url.startswith("https://www.miit.gov.cn")

    @patch("miit_scraper.parser.requests.get")
    def test_relative_url_completion(self, mock_get):
        """相对 URL 自动补全为绝对 URL"""
        mock_resp = Mock()
        mock_resp.text = MOCK_DETAIL_HTML
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        article = fetch_and_parse_article("/xwfb/szyw/art/2026/art_abc.html")
        assert article.url == "https://www.miit.gov.cn/xwfb/szyw/art/2026/art_abc.html"

        # 验证 requests.get 被调用时使用的 URL
        mock_get.assert_called_with(
            "https://www.miit.gov.cn/xwfb/szyw/art/2026/art_abc.html",
            headers=ANY,
            timeout=30,
        )

    @patch("miit_scraper.parser.requests.get")
    def test_absolute_url_preserved(self, mock_get):
        """绝对 URL 保持不变"""
        mock_resp = Mock()
        mock_resp.text = MOCK_DETAIL_HTML
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        abs_url = "https://www.miit.gov.cn/xwfb/szyw/art/2026/art_test.html"
        article = fetch_and_parse_article(abs_url)
        assert article.url == abs_url

    @patch("miit_scraper.parser.requests.get")
    def test_empty_response(self, mock_get):
        """服务器返回空内容"""
        mock_resp = Mock()
        mock_resp.text = ""
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        with pytest.raises(ValueError, match="返回空内容"):
            fetch_and_parse_article("/xwfb/szyw/art/2026/empty.html")