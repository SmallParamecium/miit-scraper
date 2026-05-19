# Spec: 数据模型定义 (Issue #1)

**版本**: 0.1.0
**关联 Issue**: [#1](https://github.com/SmallParamecium/miit-scraper/issues/1)
**模块**: `src/miit_scraper/models.py`

---

## 概述

定义爬取工信部时政要闻所需的核心数据结构。使用 Python `@dataclass` 实现不可变风格的纯数据容器。

---

## 1. Article 数据模型

### 1.1 字段契约

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `article_id` | `str` | ✅ | - | 文章唯一标识符，从 URL 提取（如 `art_0b816246f57f...`） |
| `title` | `str` | ✅ | - | 文章标题 |
| `publish_date` | `Optional[datetime]` | ❌ | `None` | 发布日期，解析失败时为 None |
| `url` | `str` | ❌ | `""` | 文章详情页 URL（完整或相对路径） |
| `source` | `str` | ❌ | `""` | 文章来源（如"工业和信息化部"、"新华社"） |
| `content_html` | `str` | ❌ | `""` | 原始 HTML 正文（保留标签） |
| `content_text` | `str` | ❌ | `""` | 清洗后纯文本正文（去除 HTML 标签） |
| `attachments` | `dict[str, str]` | ❌ | `{}` | 附件映射：文件名 → URL |

### 1.2 类方法

#### `from_api_item(data: dict) -> Article`

从 API 列表接口返回的 JSON 项构造 **骨架 Article**（content 字段为空）。

**输入**:
```json
{"id": "456", "title": "时政要闻标题", "url": "/xwdt/szyw/abc/123.html"}
```

**输出**: `Article` 实例，仅有 `article_id`、`title`、`url` 字段填充。

**边界条件**:
- `data` 缺少任何字段时不抛异常，使用空字符串/None 回退。
- `publish_date` 始终为 `None`（需后续抓取详情页填充）。

#### `to_dict() -> dict`

将 Article 转换为 JSON 可序列化字典。

**输出示例**:
```json
{
  "article_id": "789",
  "title": "测试标题",
  "url": "https://example.com",
  "source": "工信部",
  "content_text": "这是正文内容"
}
```

**规则**:
- `publish_date` 非 None 时输出 ISO 8601 格式：`2026-05-18T10:19:00`
- `attachments` 空字典时不输出该字段
- `content_html` 不输出（仅序列化 `content_text`）

---

## 2. ArticleList 数据模型

### 2.1 字段契约

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `total` | `int` | ❌ | `0` | 总文章数 |
| `articles` | `list[Article]` | ❌ | `[]` | 文章对象列表 |
| `page` | `int` | ❌ | `1` | 当前页码 |
| `page_size` | `int` | ❌ | `10` | 每页数量 |

### 2.2 行为
- 纯数据容器，无额外方法。
- `total=0` 表示无法确定总数（API 不明确返回时）。

---

## 3. 错误处理

| 场景 | 行为 |
|------|------|
| `from_api_item` 收到空 dict | 返回所有字段为默认值的 Article |
| `from_api_item` 收到不规则数据 | 不抛异常，使用 `.get()` 安全回退 |
| `to_dict` 日期为 None | 不输出 `publish_date` 字段 |

---

## 4. 测试覆盖

| 测试 | 覆盖内容 |
|------|----------|
| `test_create_article_minimal` | 最小字段创建 |
| `test_from_api_item` | API 数据构造 |
| `test_to_dict` | 字典序列化 |
| `test_to_dict_with_attachments` | 含附件的序列化 |
| `test_create_empty` | 空 ArticleList |
| `test_create_with_articles` | 含文章的 ArticleList |

**文件**: `tests/test_models.py` (6 tests)