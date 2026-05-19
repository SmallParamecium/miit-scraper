# miit-scraper

爬取工业和信息化部（工信部）时政要闻文章，输出格式化 Markdown。

## 项目状态

🚧 开发中 — 当前处于 Issue #1 项目初始化阶段。

## 功能

- 从 https://www.miit.gov.cn/xwdt/szyw/ 获取最新时政要闻
- 提取文章全文正文内容
- 输出原始 JSON（`raw/` 目录）
- 输出格式化 Markdown（`output/` 目录）

## 快速开始

```bash
# 安装依赖
uv sync

# 运行测试
uv run pytest tests/ -v

# 运行爬虫（待实现）
uv run miit-scraper
```

## 项目结构

```
miit-scraper/
├── src/miit_scraper/      # 源代码
│   ├── __init__.py
│   ├── models.py          # 数据模型（Article, ArticleList）
│   ├── fetcher.py         # 列表页 API 请求
│   ├── parser.py          # 文章详情页解析
│   ├── exporter.py        # JSON / Markdown 输出
│   └── cli.py             # 命令行入口
├── tests/                 # 单元测试
├── raw/                   # 原始 JSON 输出
├── output/                # Markdown 输出
├── docs/                  # 文档
└── pyproject.toml
```

## 技术栈

- Python >= 3.10
- [uv](https://github.com/astral-sh/uv) — 包管理器
- requests — HTTP 请求
- BeautifulSoup4 + lxml — HTML 解析

## Issues

采用 spec-driven 开发，每个环节通过 GitHub Issue 追踪：

| Issue | 内容 |
|-------|------|
| #1 | 项目初始化：uv 配置、目录结构、数据模型 |
| #2 | 列表页 API 解析 |
| #3 | 文章抓取与输出 |
| #4 | CLI 入口 + 测试完善 |