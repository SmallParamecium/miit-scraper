# Spec: CLI 命令行入口 + 导出 (Issue #4)

**版本**: 0.1.0
**关联 Issue**: [#4](https://github.com/SmallParamecium/miit-scraper/issues/4)
**模块**: `src/miit_scraper/cli.py` + `src/miit_scraper/exporter.py`

---

## 概述

提供 miit-scraper 的命令行接口，串联完整爬取流程：列表获取 → 详情解析 → 数据导出。同时定义了 JSON / Markdown 两种输出格式的契约。

---

## 1. CLI 接口

### 1.1 命令

```
usage: miit-scraper [-h] [-c N] [--output-dir DIR] [--raw-dir DIR]
                    [--no-detail] [-v]
```

### 1.2 参数

| 参数 | 简写 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--count` | `-c` | `int` | `10` | 爬取文章数量 |
| `--output-dir` | - | `str` | `"output"` | Markdown 输出目录 |
| `--raw-dir` | - | `str` | `"raw"` | JSON 输出目录 |
| `--no-detail` | - | `flag` | `False` | 仅列表，不抓取详情页 |
| `--version` | `-v` | `flag` | - | 显示版本号 |

### 1.3 执行流程

```
Step 1: fetch_article_list(page=1, page_size=count)
    ↓
Step 2: [if not --no-detail] 逐篇 fetch_and_parse_article(url)
    ↓
Step 3: save_raw_json(articles, raw-dir) + save_markdown(articles, output-dir)
```

### 1.4 运行方式支持

| 方式 | 命令 | 备注 |
|------|------|------|
| 已安装包 | `uv run miit-scraper` | 推荐 |
| 直接运行 | `python src/miit_scraper/cli.py` | try/except 回退导入 |

### 1.5 错误处理

| 阶段 | 错误 | 行为 |
|------|------|------|
| 列表获取 | 网络/API 错误 | 打印错误到 stderr，退出码 1 |
| 详情抓取 | 单篇失败 | 打印 `✗ (error)`，保留列表数据继续 |
| 导出 | 文件写入失败 | 打印错误到 stderr，退出码 1 |

---

## 2. Exporter 导出模块

### 2.1 `save_raw_json(articles, output_dir="raw") -> list[Path]`

每篇文章输出一个 JSON 文件，调用 `article.to_dict()` 序列化。

**文件名**: `{article_id}.json`

**异常**: `OSError` 时抛出

### 2.2 `save_markdown(articles, output_dir="output") -> list[Path]`

每篇文章输出一个 Markdown 文件。

**文件名**: `{article_id}.md`

**Markdown 模板**:
```markdown
# 文章标题

*发布日期：yyyy-mm-dd*
*来源：xxx*
*原文链接：[url](url)*

---

正文内容（多段落以换行分隔）

## 附件
- [文件名](URL)
```

**规则**:
- 元数据仅在字段非空时输出
- 正文为空时跳过
- 附件为空时跳过附件段
- 文件编码: UTF-8

---

## 3. 测试覆盖

### CLI 测试 (`tests/test_cli.py`)

| 测试 | 覆盖内容 |
|------|----------|
| `test_version` | --version 输出 |
| `test_help` | --help 输出 |
| `test_basic_flow` | 默认参数完整流程 |
| `test_no_detail_flag` | --no-detail 跳过详情 |
| `test_custom_output_dir` | 自定义输出目录 |
| `test_list_fetch_error` | 列表获取失败退出码 1 |
| `test_detail_fetch_partial_failure` | 部分详情失败继续 |
| `test_export_error` | 导出失败退出码 1 |
| `test_custom_count` | 自定义爬取数量 |

### Exporter 测试 (`tests/test_exporter.py`)

| 测试 | 覆盖内容 |
|------|----------|
| `test_save_raw_json` | JSON 文件输出 |
| `test_save_raw_json_empty` | 空列表输入 |
| `test_save_markdown` | Markdown 文件输出 |
| `test_save_markdown_with_attachments` | 含附件的 Markdown |
| `test_save_markdown_no_content` | 无正文的 Markdown |
| `test_save_markdown_empty` | 空列表输入 |

**文件**: `tests/test_cli.py` (9 tests) + `tests/test_exporter.py` (6 tests)