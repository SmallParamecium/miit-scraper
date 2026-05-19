"""tests for miit_scraper.exporter"""

import json
import tempfile
from datetime import datetime
from pathlib import Path

from miit_scraper.exporter import save_raw_json, save_markdown
from miit_scraper.models import Article


class TestSaveRawJson:
    """save_raw_json 单元测试"""

    def test_saves_one_file_per_article(self):
        articles = [
            Article(article_id="art_001", title="文章一", publish_date=datetime(2026, 5, 10)),
            Article(article_id="art_002", title="文章二", publish_date=datetime(2026, 5, 11)),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = save_raw_json(articles, output_dir=tmpdir)
            assert len(paths) == 2
            assert (Path(tmpdir) / "art_001.json").exists()
            assert (Path(tmpdir) / "art_002.json").exists()

    def test_saved_json_structure(self):
        articles = [
            Article(
                article_id="art_abc",
                title="测试标题",
                url="https://www.miit.gov.cn/test.html",
                source="信息中心",
                content_text="正文内容",
                publish_date=datetime(2026, 5, 15),
            ),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = save_raw_json(articles, output_dir=tmpdir)
            data = json.loads(Path(paths[0]).read_text(encoding="utf-8"))
            assert data["article_id"] == "art_abc"
            assert data["title"] == "测试标题"
            assert data["url"] == "https://www.miit.gov.cn/test.html"
            assert data["source"] == "信息中心"
            assert data["content_text"] == "正文内容"
            assert "publish_date" in data

    def test_empty_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = save_raw_json([], output_dir=tmpdir)
            assert paths == []

    def test_creates_output_dir(self):
        articles = [Article(article_id="x", title="t")]
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = str(Path(tmpdir) / "nested" / "json")
            paths = save_raw_json(articles, output_dir=subdir)
            assert len(paths) == 1
            assert Path(subdir).is_dir()

    def test_article_with_attachments(self):
        articles = [
            Article(
                article_id="att_01",
                title="带附件",
                attachments={"file.pdf": "https://www.miit.gov.cn/files/file.pdf"},
            ),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = save_raw_json(articles, output_dir=tmpdir)
            data = json.loads(Path(paths[0]).read_text(encoding="utf-8"))
            assert data["attachments"] == {"file.pdf": "https://www.miit.gov.cn/files/file.pdf"}


class TestSaveMarkdown:
    """save_markdown 单元测试"""

    def test_saves_one_file_per_article(self):
        articles = [
            Article(article_id="a1", title="标题1"),
            Article(article_id="a2", title="标题2"),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = save_markdown(articles, output_dir=tmpdir)
            assert len(paths) == 2
            assert (Path(tmpdir) / "a1.md").exists()
            assert (Path(tmpdir) / "a2.md").exists()

    def test_markdown_structure(self):
        articles = [
            Article(
                article_id="md_01",
                title="标题测试",
                source="工信部",
                url="https://www.miit.gov.cn/art_01.html",
                content_text="这是正文内容",
                publish_date=datetime(2026, 5, 18),
            ),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = save_markdown(articles, output_dir=tmpdir)
            content = Path(paths[0]).read_text(encoding="utf-8")

            assert "# 标题测试" in content
            assert "**发布日期**：2026-05-18" in content
            assert "**来源**：工信部" in content
            assert "**原文链接**：" in content
            assert "https://www.miit.gov.cn/art_01.html" in content
            assert "---" in content
            assert "这是正文内容" in content

    def test_no_date_no_source(self):
        """无日期无来源时不崩溃"""
        articles = [Article(article_id="minimal", title="最小文章")]
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = save_markdown(articles, output_dir=tmpdir)
            content = Path(paths[0]).read_text(encoding="utf-8")
            assert "# 最小文章" in content
            # 不应包含发布日期/来源行
            assert "**发布日期**" not in content
            assert "**来源**" not in content

    def test_with_attachments(self):
        articles = [
            Article(
                article_id="att_md",
                title="附件测试",
                attachments={
                    "附件1.pdf": "https://example.com/a.pdf",
                    "图片.png": "https://example.com/b.png",
                },
            ),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = save_markdown(articles, output_dir=tmpdir)
            content = Path(paths[0]).read_text(encoding="utf-8")
            assert "## 附件" in content
            assert "[附件1.pdf](https://example.com/a.pdf)" in content
            assert "[图片.png](https://example.com/b.png)" in content

    def test_empty_content_text(self):
        articles = [
            Article(article_id="no_content", title="无正文", source="工信部"),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = save_markdown(articles, output_dir=tmpdir)
            content = Path(paths[0]).read_text(encoding="utf-8")
            assert "# 无正文" in content
            # 仍应有来源元数据
            assert "**来源**：工信部" in content

    def test_empty_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = save_markdown([], output_dir=tmpdir)
            assert paths == []

    def test_creates_output_dir(self):
        articles = [Article(article_id="x", title="t")]
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = str(Path(tmpdir) / "a" / "b")
            paths = save_markdown(articles, output_dir=subdir)
            assert len(paths) == 1
            assert Path(subdir).is_dir()