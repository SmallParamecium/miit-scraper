"""命令行入口模块。

提供 miit-scraper 的命令行接口，串联完整爬取流程：
fetcher（列表页获取） -> parser（详情页解析） -> exporter（数据输出）
"""

import sys
from pathlib import Path

# 允许直接运行 python cli.py 时正确解析包内相对导入
if __name__ == "__main__":
    _src_dir = Path(__file__).resolve().parent.parent
    if str(_src_dir) not in sys.path:
        sys.path.insert(0, str(_src_dir))
    __package__ = "miit_scraper"

import argparse

from . import __version__
from .fetcher import fetch_article_list
from .parser import fetch_and_parse_article
from .exporter import save_raw_json, save_markdown
from .models import Article


def main(argv: list[str] | None = None) -> None:
    """CLI 主入口。

    Args:
        argv: 命令行参数列表，None 则使用 sys.argv[1:]
    """
    parser = argparse.ArgumentParser(
        prog="miit-scraper",
        description="爬取工信部时政要闻文章，输出 JSON 和 Markdown 格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  miit-scraper                          # 爬取最新 10 篇文章
  miit-scraper --count 20               # 爬取 20 篇
  miit-scraper --no-detail              # 仅列表，不抓取详情页
  miit-scraper --output-dir data/md --raw-dir data/json
        """,
    )
    parser.add_argument(
        "-c", "--count",
        type=int,
        default=10,
        metavar="N",
        help="爬取文章数量（默认 10）",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        metavar="DIR",
        help="Markdown 输出目录（默认 output/）",
    )
    parser.add_argument(
        "--raw-dir",
        default="raw",
        metavar="DIR",
        help="原始 JSON 输出目录（默认 raw/）",
    )
    parser.add_argument(
        "--no-detail",
        action="store_true",
        help="不抓取详情页，仅保存列表抓取的元数据",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"miit-scraper {__version__}",
    )

    args = parser.parse_args(argv)

    # Step 1: 获取文章列表
    print(f"正在获取 {args.count} 篇文章列表...")
    try:
        result = fetch_article_list(page=1, page_size=args.count)
    except Exception as e:
        print(f"错误: 获取文章列表失败 - {e}", file=sys.stderr)
        sys.exit(1)
        return  # 测试中 sys.exit 被 mock 时的防护

    articles = result.articles
    print(f"获取到 {len(articles)} 篇文章（总计 {result.total} 篇）")

    if not args.no_detail:
        # Step 2: 逐篇抓取详情页
        print("正在抓取文章详情页...")
        enriched: list[Article] = []
        for i, article in enumerate(articles, 1):
            url = article.url or article.article_id
            print(f"  [{i}/{len(articles)}] {article.title[:40]}...", end=" ", flush=True)
            try:
                detail = fetch_and_parse_article(url)
                enriched.append(detail)
                print("✓")
            except Exception as e:
                print(f"✗ ({e})")
                # 失败时保留原始列表数据
                enriched.append(article)
        articles = enriched
    else:
        print("跳过详情页抓取（--no-detail）")

    # Step 3: 导出数据
    print(f"正在导出数据到 {args.raw_dir}/ 和 {args.output_dir}/ ...")
    try:
        json_files = save_raw_json(articles, output_dir=args.raw_dir)
        md_files = save_markdown(articles, output_dir=args.output_dir)
    except Exception as e:
        print(f"错误: 文件导出失败 - {e}", file=sys.stderr)
        sys.exit(1)
        return  # 测试中 sys.exit 被 mock 时的防护

    print(f"完成! JSON: {len(json_files)} 个文件 -> {Path(args.raw_dir).resolve()}")
    print(f"      Markdown: {len(md_files)} 个文件 -> {Path(args.output_dir).resolve()}")


if __name__ == "__main__":
    main()
