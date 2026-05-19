> ⚠️ 本 Issue 为回溯补写，内容基于完成后的代码和 spec 文档反向整理。

# Issue #4: CLI 入口 + 数据导出 — cli.py + exporter.py

## 背景 / 为什么现在做

Issue #1~#3 分别完成了模型、列表爬取、详情页解析三个独立模块。还需要一个串联入口将三个模块编排为完整流程，并将结果持久化输出到文件。

当前缺失的能力：
- 命令行参数解析（爬取数量、输出目录、是否抓取详情）
- 三步流程编排（fetch list → parse detail → export）
- 容错降级（单篇文章解析失败不中断整体流程）
- 格式化输出（JSON 原始数据 + Markdown 可读文档）

如果没有统一的 CLI 和 exporter，用户需要手动编写脚本调用各模块，无法作为独立工具使用。

## 当前想收住的不确定性

- CLI 参数集：`--count`、`--no-detail`、`--output-dir`、`--raw-dir`、`--version`
- 输出格式：JSON 存原始数据，Markdown 存可读文档，各占一个目录
- 容错策略：单篇详情页抓取失败时，保留列表页的元数据继续输出
- 文件命名规则（`<article_id>.json` / `<article_id>.md`）
- 入口点（`miit-scraper` 命令 vs `python -m miit_scraper`）

## 已收敛的推荐方案

本 Issue 按以下口径实现：

- `miit-scraper` CLI 命令（通过 `pyproject.toml` 的 `[project.scripts]` 注册）
- `argparse` 提供 5 个参数（count、no-detail、output-dir、raw-dir、version）
- `exporter.py`：`save_raw_json()` → 每篇一个 JSON 文件；`save_markdown()` → 每篇一个 MD 文件
- `cli.py`：串联 fetch → parse → export，单篇异常不中断流程

## 方案权衡记录

### 1. CLI 框架选型：argparse vs click vs typer

**推荐：方案 A（argparse）。**

方案 A：标准库 `argparse`。

优点：
- 零额外依赖
- Python 标准库，交付重量最轻
缺点：
- 语法冗长（相对 click）

方案 B：click。

优点：装饰器语法简洁
缺点：引入额外依赖

方案 C：typer。

优点：类型提示自动生成 CLI
缺点：依赖 typer + rich，过度设计

### 2. 输出格式：JSON + Markdown vs 数据库

**推荐：方案 A（JSON + Markdown 双输出）。**

方案 A：每篇文章两个文件（`.json` + `.md`）。

优点：
- JSON 保持原始结构，方便二次处理
- Markdown 可读，可直接在编辑器中查看
- 无需外部服务（数据库）
缺点：
- 文件数量较多（N 篇文章 = 2N 个文件）

方案 B：单 JSON 文件（所有文章合并）。

优点：单文件
缺点：大文件不易增量更新

方案 C：SQLite 数据库。

优点：查询方便
缺点：引入额外依赖，不能直接在 Git 中查看 diff

### 3. 容错策略：中断 vs 继续

**推荐：方案 A（单篇失败继续，保留元数据）。**

方案 A：详情页请求失败时 catch 异常，保留列表获取的原始 Article 对象。

优点：
- 不会因一篇反爬/404 中断全部抓取
- 输出完整性最大化
缺点：
- 部分文章缺少正文（仅含标题/日期/URL）

方案 B：任意一篇失败即整体退出。

优点：保证数据一致性
缺点：脆弱，一点异常即全体失败

### 4. 入口点：--version 开关

**推荐：方案 A（支持 `-v` / `--version`）。**

方案 A：argparse 的 `action="version"` 直接支持。

优点：一行代码
缺点：需维护 `__version__` 与 `pyproject.toml` 同步

## 本 Issue 想解决什么

- [x] 创建 `cli.py`：argparse CLI 入口
- [x] 5 个命令行参数：`-c/--count`、`--no-detail`、`--output-dir`、`--raw-dir`、`-v/--version`
- [x] 流程编排：fetch list → (optional) parse detail → export
- [x] 容错降级：单篇解析失败时保留列表数据
- [x] 进度输出（`[i/总数] 标题... ✓/✗`）
- [x] 创建 `exporter.py`：`save_raw_json()` 和 `save_markdown()`
- [x] JSON 格式：`article.to_dict()` → `indent=2, ensure_ascii=False`
- [x] Markdown 格式：标题 + 元数据 + 分隔线 + 正文 + 附件
- [x] `pyproject.toml` 中注册 `[project.scripts]` 入口点
- [x] 支持 `python -m miit_scraper.cli` 和 `miit-scraper` 两种运行方式

## 明确不解决什么

- 不做增量爬取（每次都全量重新抓取）
- 不做并发抓取详情页（单线程顺序）
- 不做 HTML 到 Markdown 的富文本转换
- 不做 `--format csv` 等其他输出格式
- 不做进度条动画（只输出文本进度）

## 当前已知上下文

- `src/miit_scraper/cli.py`：argparse + 流程编排
- `src/miit_scraper/exporter.py`：JSON / Markdown 导出
- `src/miit_scraper/__init__.py`：`__version__`
- `pyproject.toml`：`[project.scripts]` 入口点注册

## 前置依赖

- Issue #1: models.py 已完成
- Issue #2: fetcher.py 已完成
- Issue #3: parser.py 已完成

## 子任务树

- [x] 实现 `exporter.py`：`save_raw_json()` 和 `save_markdown()`
- [x] JSON 输出格式：`indent=2, ensure_ascii=False`
- [x] Markdown 输出格式：标题/元数据/分隔线/正文/附件
- [x] 实现 `cli.py`：argparse 参数定义
- [x] 流程编排：fetch list → parse detail → export
- [x] 单篇容错：try/catch 保底
- [x] 进度输出
- [x] `pyproject.toml` 注册 `miit-scraper` 命令
- [x] 编写 `tests/test_exporter.py` 和 `tests/test_cli.py`
- [x] 端到端验证：`miit-scraper --count 3`

## 验收口径

### 必须成立

- `miit-scraper --help` 输出帮助信息，包含所有参数
- `miit-scraper -v` 输出版本号
- `miit-scraper --count 3` 在 `output/` 生成 3 个 `.md` 文件，`raw/` 生成 3 个 `.json` 文件
- `miit-scraper --no-detail` 跳过详情页抓取
- Markdown 文件包含 `# 标题`、斜体元数据行、`---` 分隔线、正文内容
- JSON 文件包含 `article_id`、`title`、`url`、`publish_date`、`content_text` 等字段
- 单篇文章详情页请求失败时，整体流程继续，该篇输出仅含列表级元数据

### 明确不成立

- 不应在 `--no-detail` 模式下请求详情页
- 不应在 `--count 0` 时崩溃（应优雅输出 0 个文件）
- JSON/Markdown 文件名不应包含 `.html` 后缀
- Markdown 文件不应包含 HTML 标签

### 失败信号

- 详情页全部失败时，仍成功输出列表级 JSON 和 MD
- 输出目录为相对路径时，文件创建到正确路径
- 网络完全断开时给出明确错误信息而非堆栈溢出

## Harness / 验证要求

参见 `tests/test_cli.py` 和 `tests/test_exporter.py`：

- [x] CLI:`--help` 输出验证
- [x] CLI:`--version` 输出验证
- [x] CLI:完整流程集成测试（mock fetcher + parser）
- [x] CLI:单篇解析失败容错测试
- [x] CLI:`--no-detail` 模式验证
- [x] CLI:`--output-dir` 和 `--raw-dir` 参数验证
- [x] Exporter: JSON 文件内容验证（含/不含 publish_date、含/不含 attachments）
- [x] Exporter: Markdown 文件格式验证
- [x] Exporter: 空文章列表处理
- [x] Exporter: 目录自动创建
- [x] 端到端真实运行：`miit-scraper --count 2` 检查输出文件