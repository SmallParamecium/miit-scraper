"""数据模型单元测试。"""

import pytest
from miit_scraper.models import Article, ArticleList


class TestArticle:
    """Article 数据模型测试。"""

    def test_create_article_minimal(self):
        """测试创建最小属性 Article。"""
        article = Article(article_id="123", title="测试文章")
        assert article.article_id == "123"
        assert article.title == "测试文章"
        assert article.url == ""
        assert article.content_text == ""
        assert article.attachments == {}

    def test_from_api_item(self):
        """测试从 API JSON 数据构造 Article。"""
        data = {"id": "456", "title": "时政要闻标题", "url": "/xwdt/szyw/abc/123.html"}
        article = Article.from_api_item(data)
        assert article.article_id == "456"
        assert article.title == "时政要闻标题"
        assert article.url == "/xwdt/szyw/abc/123.html"
        assert article.publish_date is None

    def test_to_dict(self):
        """测试转换为字典。"""
        article = Article(
            article_id="789",
            title="测试标题",
            url="https://example.com",
            source="工信部",
            content_text="这是正文内容",
        )
        result = article.to_dict()
        assert result["article_id"] == "789"
        assert result["title"] == "测试标题"
        assert result["source"] == "工信部"
        assert result["content_text"] == "这是正文内容"

    def test_to_dict_with_attachments(self):
        """测试含附件的字典转换。"""
        article = Article(
            article_id="x1",
            title="带附件文章",
            attachments={"通知.pdf": "https://example.com/1.pdf"},
        )
        result = article.to_dict()
        assert result["attachments"] == {"通知.pdf": "https://example.com/1.pdf"}


class TestArticleList:
    """ArticleList 数据模型测试。"""

    def test_create_empty(self):
        """测试创建空 ArticleList。"""
        al = ArticleList()
        assert al.total == 0
        assert al.articles == []
        assert al.page == 1
        assert al.page_size == 10

    def test_create_with_articles(self):
        """测试创建包含文章的 ArticleList。"""
        articles = [
            Article(article_id="1", title="文章1"),
            Article(article_id="2", title="文章2"),
        ]
        al = ArticleList(total=2, articles=articles, page=1, page_size=10)
        assert al.total == 2
        assert len(al.articles) == 2