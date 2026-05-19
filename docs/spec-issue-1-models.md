# spec-issue-1: 数据模型定义（models.py）

> 关联 Issue: [#22](https://github.com/SmallParamecium/miit-scraper/issues/22)
> 实现文件: `src/miit_scraper/models.py`

## 目标

定义爬取全流程中共享的核心数据结构，确保各模块间数据传递一致、可序列化。

## 范围

- `Article` — 单篇文章完整信息
- `ArticleList` — 文章列表+分页信息
- 两者均为 `dataclass`，无副作用、无外部依赖

## 数据结构

### Article

```python
@dataclass
class Article:
    article_id: str                          # 唯一标识（含 articlexxx.html 前缀）
    title: str                               # 文章标题
    publish_date: Optional[datetime] = None   # 发布日期
    url: str = ""                            # 详情页完整 URL
    source: str = ""                         # 文章来源（如"工业和信息化部"）
    content_html: str = ""                   # 原始 HTML 正文（当前未使用）
    content_text: str = ""                   # 清洗后的纯文本正文
    attachments: dict[str, str] = field(default_factory=dict)  # 附件名 → URL
```

### ArticleList

```python
@dataclass
class ArticleList:
    total: int = 0
    articles: list[Article] = field(default_factory=list)
    page: int = 1
    page_size: int = 10
```

## 工厂方法

### `Article.from_api_item(data: dict) -> Article`

从 CMS API（大汉版通）列表接口返回的 JSON 项构造 `Article` 实例。

- 只提取 `id`、`title`、`url` 三个字段
- `publish_date` 设为 `None`（列表接口的日期格式与详情页不同，需后续解析）
- `content_*` 字段留空，需调用 `fetch_and_parse_article()` 填充

### `Article.to_dict() -> dict`

将 `Article` 转为字典，排除空字段以减小 JSON 体积。

- `publish_date` 序列化为 ISO 8601 字符串
- `attachments` 仅非空时包含
- 不序列化 `content_html`（原始 HTML 体积过大）

## 设计决策

1. **`article_id` 包含 `art_` 前缀** — 从 URL 中提取完整文件名（如 `art_0b816246f57f4866af5fad7efc87040a`），方便与文件系统中的 JSON/MD 文件名对应
2. **`content_html` 保留但默认不序列化** — 为可能的附件链接提取或 HTML 格式导出预留扩展点
3. **`attachments` 使用 `dict[str, str]`** — 文件名到 URL 的一对一映射，简单直观

## 限制

- `publish_date` 使用 `datetime` 对象，序列化时丢失时区信息（假设北京时间）
- `article_id` 的提取依赖 URL 格式 `.../art_{uuid}.html`，若 CMS 变更需同步修改

## 测试覆盖

参见 `tests/test_models.py`:

- `Article` 构造与字段默认值
- `from_api_item()` 正常/空数据/缺失字段
- `to_dict()` 序列化完整性
- `ArticleList` 构造与默认值