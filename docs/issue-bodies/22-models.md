>
> ⚠️ 本 Issue 为回溯补写，内容基于完成后的代码和 spec 文档反向整理。

# Issue #1: 项目初始化 — uv 配置、目录结构、数据模型定义

## 背景 / 为什么现在做

`miit-scraper` 项目从零启动，需要一个可维护的 Python 项目骨架：包管理器（uv）、类型安全的领域模型（dataclass）、标准 `src/` 布局。这三个基础元素决定了后续所有模块——fetcher、parser、cli、exporter——的实现方式。

如果模型先行不明确，后续模块会各自发明 Article 字段和序列化方式，导致：
- fetcher 返回的 dict 与 parser 返回的 dict 字段名不一致
- exporter 需要兼容多种输入格式
- 测试断言反复调整

因此，Issue #1 必须先收住数据模型和项目骨架。

## 当前想收住的不确定性

`Article` 和 `ArticleList` 应该包含哪些字段？类型签名是什么？序列化格式（`to_dict()`）如何统一？

## 已收敛的推荐方案

本 Issue 按以下 MVP 口径进入开发：

- 使用 `uv` 管理依赖和虚拟环境，`pyproject.toml` 定义项目元数据
- `src/miit_scraper/` 标准布局，`src/` 作为包根目录
- `Article` 和 `ArticleList` 使用 `dataclass` 定义，类型安全且可序列化
- `Article.to_dict()` 作为唯一的序列化入口
- `Article.from_api_item()` 为 fetcher 场景的工厂方法

## 方案权衡记录

### 1. 包管理器选型：uv vs pip vs poetry

**推荐：方案 A（uv）。**

方案 A：使用 `uv`。

优点：
- Python 官方推荐的下一代包管理器，速度快 10-100x
- 自动管理 Python 解释器（`.python-version`）
- lock 文件（`uv.lock`）跨平台可复现
缺点：
- 新工具，生态插件不如 pip 成熟

方案 B：使用 pip + venv。

优点：无需安装额外工具
缺点：依赖解析慢，lock 文件需手动维护

方案 C：使用 poetry。

优点：成熟的 lock 方案
缺点：用户明确要求「使用 uv 替代 pip」

### 2. 数据模型：dataclass vs Pydantic vs NamedTuple

**推荐：方案 A（dataclass）。**

方案 A：`dataclass` + 手动 `to_dict()`。

优点：
- 轻量无额外依赖
- 类型安全（`Optional[datetime]`、`dict[str, str]`）
- 可设默认值（`url=""`、`content_text=""`）
缺点：
- 无自动验证（当前阶段不需要）

方案 B：Pydantic BaseModel。

优点：自动验证和序列化
缺点：引入重型依赖，爬虫项目过度设计

方案 C：NamedTuple / dict。

优点：零样板
缺点：无类型提示、字段易拼错、IDE 无补全

### 3. 目录布局：src/ vs flat

**推荐：方案 A（src/ 布局）。**

方案 A：`src/miit_scraper/`。

优点：
- 防止意外导入未安装的包
- 测试时强制使用已安装的包路径
- Python 生态主流标准
缺点：
- 需要显式 `pip install -e .`

方案 B：`miit_scraper/` 平铺。

优点：简单
缺点：开发和测试行为不一致

## 本 Issue 想解决什么

- [x] 创建 `pyproject.toml`，使用 uv 管理依赖
- [x] 定义 `Article` dataclass（article_id、title、publish_date、url、source、content_html、content_text、attachments）
- [x] 定义 `ArticleList` dataclass（total、articles、page、page_size）
- [x] `Article.to_dict()` JSON 序列化方法
- [x] `Article.from_api_item()` 工厂方法
- [x] `src/miit_scraper/` 目录结构
- [x] `.gitignore`、`.python-version` 配置

## 明确不解决什么

- 不做数据库 ORM 模型（SQLAlchemy）
- 不做字段级验证（Pydantic validators）
- 不引入 Pydantic / attrs
- 不定义 fetcher/parser 的业务逻辑

## 当前已知上下文

- `pyproject.toml`：项目元数据、依赖声明（requests、beautifulsoup4、lxml）
- `src/miit_scraper/__init__.py`：导出 `__version__`
- `src/miit_scraper/models.py`：Article、ArticleList 定义

## 前置依赖

无。Issue #1 是项目起点。

## 子任务树

- [x] 初始化 uv 项目（`uv init`）
- [x] 配置 `pyproject.toml`（依赖、entry point）
- [x] 创建 `src/miit_scraper/` 目录和 `__init__.py`
- [x] 实现 `models.py`：Article + ArticleList dataclass
- [x] 实现 `Article.to_dict()` 和 `Article.from_api_item()`
- [x] 测试 `models.py`（`tests/test_models.py`）
- [x] 配置 `.gitignore` 和 `.python-version`
- [x] 安装依赖并验证 `uv run python -c "from miit_scraper.models import Article"`

## 验收口径

### 必须成立

- `from miit_scraper.models import Article, ArticleList` 可正确导入
- `Article(article_id="test", title="测试")` 创建实例成功
- `article.to_dict()` 返回字典格式正确，`publish_date` 为 None 时不包含该字段
- `Article.from_api_item({"id": "123", "title": "新闻", "url": "/page.html"})` 创建正确
- `ArticleList(articles=[...], total=5).total` 为 5

### 明确不成立

- 不应出现 Pydantic / attrs 依赖
- Article 不应包含数据库相关字段（如 `id`、`created_at`）
- `to_dict()` 不应返回 `content_html`（避免 JSON 膨胀）

### 失败信号

- fetcher/parser 各自定义不同结构的 Article dict
- exporter 需要适配多种 Article 表示形式
- 新增字段时需要在多处修改序列化逻辑

## Harness / 验证要求

参见 `tests/test_models.py`：

- [x] Article 创建与默认值
- [x] `Article.from_api_item()` 字段映射
- [x] `Article.to_dict()` 序列化（含/不含 publish_date、含/不含 attachments）
- [x] `ArticleList` 默认值（total=0、articles=[]）
- [x] 类型注解完整性（mypy 通过）