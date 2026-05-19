"""tests for miit_scraper.cli"""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

from miit_scraper.cli import main
from miit_scraper.models import Article, ArticleList


class TestCliHelpAndVersion:
    """--help 和 --version 测试"""

    def test_version(self, capsys):
        with patch("sys.exit") as mock_exit:
            main(["--version"])
            captured = capsys.readouterr()
            assert "miit-scraper" in captured.out
            mock_exit.assert_called_once_with(0)

    def test_help(self, capsys):
        with patch("sys.exit") as mock_exit:
            main(["--help"])
            captured = capsys.readouterr()
            assert "爬取工信部时政要闻文章" in captured.out
            assert "--count" in captured.out
            assert "--no-detail" in captured.out
            assert "--output-dir" in captured.out
            assert "--raw-dir" in captured.out
            mock_exit.assert_called_once_with(0)


class TestCliArgs:
    """命令行参数测试"""

    def test_default_count(self):
        with patch("miit_scraper.cli.fetch_article_list") as mock_fetch, \
             patch("miit_scraper.cli.fetch_and_parse_article") as mock_parse, \
             patch("miit_scraper.cli.save_raw_json") as mock_raw, \
             patch("miit_scraper.cli.save_markdown") as mock_md:

            mock_fetch.return_value = ArticleList(total=0, articles=[], page=1, page_size=10)
            mock_raw.return_value = []
            mock_md.return_value = []

            main([])
            mock_fetch.assert_called_once_with(page=1, page_size=10)

    def test_custom_count(self):
        with patch("miit_scraper.cli.fetch_article_list") as mock_fetch, \
             patch("miit_scraper.cli.fetch_and_parse_article") as mock_parse, \
             patch("miit_scraper.cli.save_raw_json") as mock_raw, \
             patch("miit_scraper.cli.save_markdown") as mock_md:

            mock_fetch.return_value = ArticleList(total=0, articles=[], page=1, page_size=5)
            mock_raw.return_value = []
            mock_md.return_value = []

            main(["--count", "5"])
            mock_fetch.assert_called_once_with(page=1, page_size=5)

    def test_no_detail_flag(self):
        with patch("miit_scraper.cli.fetch_article_list") as mock_fetch, \
             patch("miit_scraper.cli.fetch_and_parse_article") as mock_parse, \
             patch("miit_scraper.cli.save_raw_json") as mock_raw, \
             patch("miit_scraper.cli.save_markdown") as mock_md:

            mock_fetch.return_value = ArticleList(
                total=1, articles=[
                    Article(article_id="id1", title="测试", url="http://test.com")
                ], page=1, page_size=10,
            )
            mock_raw.return_value = []
            mock_md.return_value = []

            main(["--no-detail"])
            # 不应调用详情页抓取
            mock_parse.assert_not_called()
            # 但仍然导出
            mock_raw.assert_called_once()
            mock_md.assert_called_once()

    def test_custom_dirs(self):
        with patch("miit_scraper.cli.fetch_article_list") as mock_fetch, \
             patch("miit_scraper.cli.fetch_and_parse_article") as mock_parse, \
             patch("miit_scraper.cli.save_raw_json") as mock_raw, \
             patch("miit_scraper.cli.save_markdown") as mock_md:

            mock_fetch.return_value = ArticleList(
                total=1, articles=[
                    Article(article_id="x", title="t", url="http://x.com")
                ], page=1, page_size=10,
            )
            mock_parse.return_value = Article(article_id="x", title="t")
            mock_raw.return_value = []
            mock_md.return_value = []

            main(["--output-dir", "my_output", "--raw-dir", "my_raw"])
            mock_raw.assert_called_once()
            assert mock_raw.call_args[1]["output_dir"] == "my_raw"
            mock_md.assert_called_once()
            assert mock_md.call_args[1]["output_dir"] == "my_output"

    def test_short_count_arg(self):
        with patch("miit_scraper.cli.fetch_article_list") as mock_fetch, \
             patch("miit_scraper.cli.fetch_and_parse_article") as mock_parse, \
             patch("miit_scraper.cli.save_raw_json") as mock_raw, \
             patch("miit_scraper.cli.save_markdown") as mock_md:

            mock_fetch.return_value = ArticleList(total=0, articles=[], page=1, page_size=3)
            mock_raw.return_value = []
            mock_md.return_value = []

            main(["-c", "3"])
            mock_fetch.assert_called_once_with(page=1, page_size=3)


class TestCliErrors:
    """错误处理测试"""

    def test_fetch_list_failure(self, capsys):
        with patch("miit_scraper.cli.fetch_article_list") as mock_fetch, \
             patch("sys.exit") as mock_exit:

            mock_fetch.side_effect = ValueError("网络错误")

            main(["--count", "5"])
            captured = capsys.readouterr()
            assert "获取文章列表失败" in captured.err
            mock_exit.assert_called_once_with(1)

    def test_export_failure(self, capsys):
        with patch("miit_scraper.cli.fetch_article_list") as mock_fetch, \
             patch("miit_scraper.cli.fetch_and_parse_article") as mock_parse, \
             patch("miit_scraper.cli.save_raw_json") as mock_raw, \
             patch("sys.exit") as mock_exit:

            mock_fetch.return_value = ArticleList(
                total=1, articles=[
                    Article(article_id="id1", title="测试", url="http://t.com")
                ], page=1, page_size=10,
            )
            mock_parse.return_value = Article(article_id="id1", title="测试")
            mock_raw.side_effect = OSError("写入失败")

            main(["--count", "1"])
            captured = capsys.readouterr()
            assert "文件导出失败" in captured.err
            mock_exit.assert_called_once_with(1)

    def test_parse_detail_failure_continues(self, capsys):
        """单篇详情页解析失败不应阻断整体流程"""
        with patch("miit_scraper.cli.fetch_article_list") as mock_fetch, \
             patch("miit_scraper.cli.fetch_and_parse_article") as mock_parse, \
             patch("miit_scraper.cli.save_raw_json") as mock_raw, \
             patch("miit_scraper.cli.save_markdown") as mock_md:

            art1 = Article(article_id="id1", title="文章1", url="http://a.com")
            art2 = Article(article_id="id2", title="文章2", url="http://b.com")

            mock_fetch.return_value = ArticleList(
                total=2, articles=[art1, art2], page=1, page_size=10,
            )
            # 第一篇成功，第二篇失败
            mock_parse.side_effect = [
                Article(article_id="id1", title="文章1", content_text="正文1"),
                RuntimeError("502 Bad Gateway"),
            ]
            mock_raw.return_value = []
            mock_md.return_value = []

            main(["--count", "2"])
            captured = capsys.readouterr()
            # 应看到错误但继续
            assert "502" in captured.out

            # 应导出了两篇（第二篇使用原始列表数据）
            assert mock_raw.call_count == 1
            called_articles = mock_raw.call_args[0][0]
            assert len(called_articles) == 2