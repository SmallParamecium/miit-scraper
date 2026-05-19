# miit-scraper

爬取工业和信息化部（工信部）时政要闻文章，输出格式化 Markdown。

## 项目状态

✅ 核心功能已实现 — Issues #1~#4 已完成，进入完善阶段。

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

采用 spec-driven 开发，每个 Issue 对应 `docs/` 下的 spec 文档：

| Issue | 内容 | 状态 |
|-------|------|------|
| #1 | 项目初始化：uv 配置、目录结构、数据模型 | ✅ Closed |
| #2 | 列表页 API 请求模块 (fetcher.py) | ✅ Closed |
| #3 | 文章详情页爬取 (parser.py) | ✅ Closed |
| #4 | CLI 入口 + 数据导出 (exporter.py + cli.py) | ✅ Closed |
| #11 | 修复 cli.py ImportError + .gitignore | ✅ Closed |
| #12 | 补充 OpenSpec 文档 | ✅ Closed |
