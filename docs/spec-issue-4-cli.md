# spec-issue-4: CLI 入口与数据导出（cli.py + exporter.py）

> 关联 Issue: [#28](https://github.com/SmallParamecium/miit-scraper/issues/28)
> 实现文件: `src/miit_scraper/cli.py`, `src/miit_scraper/exporter.py`

## 目标

提供命令行入口，串联完整爬取流程：fetcher（列表）→ parser（详情）→ exporter（输出），并支持 JSON 和 Markdown 两种导出格式。

## 范围

- **cli.py** — argparse CLI 参数解析、流程编排、用户交互输出
- **exporter.py** — 将 `Article` 列表导出为 JSON / Markdown 文件

## CLI 接口

### 入口点

```toml
[project.scripts]
miit-scraper = "miit_scraper.cli:main"
```

需支持两种运行方式：
1. `uv run miit-scraper` — 通过 entry point（包导入模式）
2. `python src/miit_scraper/cli.py` — 直接运行脚本（`__name__ == "__main__"` 模式）

### 命令行参数

```
miit-scraper [-h] [-c N] [--output-dir DIR] [--raw-dir DIR] [--no-detail] [-v]
```

| 参数 | 短参数 | 类型 | 默认值 | 说明 |
|------|--------|------|--------|------|
| `--count` | `-c` | int | 10 | 爬取文章数量 |
| `--output-dir` | — | str | `output` | Markdown 输出目录 |
| `--raw-dir` | — | str | `raw` | 原始 JSON 输出目录 |
| `--no-detail` | — | flag | False | 不抓取详情页，仅保存列表元数据 |
| `--version` | `-v` | flag | — | 显示版本号并退出 |

### 流程编排

```
main()
 ├── Step 1: fetch_article_list(page=1, page_size=args.count)
 │    └── 失败 → 打印错误 → sys.exit(1)
 ├── Step 2: [--no-detail=False] 循环 fetch_and_parse_article(url)
 │    ├── 成功 → 添加到 enriched 列表
 │    └── 失败 → 打印警告 → 回退使用列表数据
 └── Step 3: save_raw_json() + save_markdown()
      └── 失败 → 打印错误 → sys.exit(1)
```

关键行为：
- **详情页故障容错** — 单篇解析失败不中断整体流程，用列表元数据降级
- **进度显示** — `[1/10] 文章标题... ✓/✗`
- **最终摘要** — 显示输出文件数量和绝对路径

## 导出模块（exporter.py）

### `save_raw_json(articles: list[Article], output_dir: str) -> list[Path]`

```python
def save_raw_json(articles: list[Article], output_dir: str = "raw") -> list[Path]
```

- 每篇文章保存为一个独立 JSON 文件
- 文件名：`{article_id}.json`
- 内容：`Article.to_dict()` 序列化结果
- 自动创建输出目录（`mkdir(parents=True, exist_ok=True)`）
- 编码：UTF-8，缩进：2 空格，`ensure_ascii=False`

### `save_markdown(articles: list[Article], output_dir: str) -> list[Path]`

```python
def save_markdown(articles: list[Article], output_dir: str = "output") -> list[Path]
```

- 每篇文章保存为一个独立 Markdown 文件
- 文件名：`{article_id}.md`
- 格式结构：

```markdown
# {title}

*{发布日期、来源、原文链接}*

---

{content_text}

## 附件
- [附件名](URL)
```

- 元数据仅当字段非空时才输出
- 附件列表仅当 `attachments` 非空时才输出
- 编码：UTF-8

## 设计决策

1. **每篇文章独立文件** — 便于版本控制（Git diff 精确到单篇）和增量处理
2. **JSON + Markdown 双输出** — JSON 用于程序化处理 / 数据管道，Markdown 用于人工阅读
3. **`--no-detail` 加速模式** — 仅列表爬取可快速获取最新文章元数据，跳过每篇详情页的 2-5 秒网络开销
4. **条目级失败隔离** — 详情页抓取中单篇失败不影响其他文章，用初始列表数据降级保留基本信息

## 限制

- **无并发** — 详情页逐篇串行抓取，10 篇文章约耗时 20-50 秒
- **无增量去重** — 每次运行全量抓取并覆盖已有文件
- **无日志系统** — 使用 `print()` 输出进度，无结构化日志
- **无配置文件** — 所有配置通过命令行参数传递

## 测试覆盖

### cli.py（`tests/test_cli.py`）

- `--version` / `--help` 输出
- 默认参数 / 自定义 `--count` / `--no-detail` / 自定义目录
- 列表获取失败 → sys.exit(1)
- 导出失败 → sys.exit(1)
- 详情页解析失败 → 继续处理并降级

### exporter.py（`tests/test_exporter.py`）

- JSON 文件内容验证（`Article.to_dict()` 序列化）
- Markdown 文件格式验证（含/不含元数据、日期格式、附件）
- 空文章列表 → 返回空列表
- 目录自动创建
- 附件为空时 Markdown 不包含附件 section