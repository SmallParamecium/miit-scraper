"""命令行入口模块。

提供 miit-scraper 的命令行接口。
"""


# TODO: Issue #4 实现 - CLI 入口与完整流程串联
# 目标：
# 1. 使用 argparse 提供命令行参数
#    --count N: 爬取文章数量（默认 10）
#    --output-dir: 输出目录（默认 output/）
#    --raw-dir: 原始数据目录（默认 raw/）
# 2. 调用 fetcher -> parser -> exporter 完整流程
# 3. 提供 --help 和 --version


def main() -> None:
    """CLI 主入口。

    Raises:
        NotImplementedError: 功能尚未实现
    """
    raise NotImplementedError("CLI 入口将在 Issue #4 中实现")


if __name__ == "__main__":
    main()