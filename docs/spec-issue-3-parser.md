# spec-issue-3: 详情页解析模块（parser.py）

> 关联 Issue: [#26](https://github.com/SmallParamecium/miit-scraper/issues/26)
> 实现文件: `src/miit_scraper/parser.py`

## 目标

抓取单篇文章的详情页 HTML，通过 `<meta>` 标签提取元数据，通过 CSS 选择器提取正文内容的纯文本。

## 范围

- 构建完整请求 URL，带 Referer 头 GET 请求详情页
- 解析 HTML 中的 `<meta name="..." content="...">` 元数据
- 针对 `div#con_con` 容器提取 `<p>` 标签纯文本正文
- 返回填充了完整内容的 `Article` 对象

## 请求配置

```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.miit.gov.cn/xwfb/szyw/",
}
```

- Refere 必须设为栏目页，否则 CMS 可能返回 403
- 超时 30 秒

## `<meta>` 元数据映射

`META_FIELD_MAP` 将 HTML meta 的 `name` 属性映射到内部字段：

| meta name | 内部字段 | 示例值 |
|-----------|---------|--------|
| `ArticleTitle` | `title` | `2026年1-4月电子信息制造业运行情况` |
| `PubDate` | `pub_date_raw` | `2026-05-18 10:19` |
| `ContentSource` | `source` | `工业和信息化部运行监测协调局` |
| `Description` | `description` | 文章摘要 |
| `Keywords` | `keywords_raw` | `电子信息,制造业,运行情况` |
| `ColumnName` | `column` | `时政要闻` |
| `SiteName` | `site_name` | `工业和信息化部` |
| `Url` | `rel_url` | 相对 URL |

## 正文提取

```python
con_div = soup.find("div", id="con_con")
```

- 目标容器：`div#con_con`
- 提取所有 `<p>` 标签文本，用空行分隔（`"\n\n"`）
- 提取前移除 `<script>` 和 `<style>` 标签

## 公开接口

### `parse_article_html(html: str) -> dict`

```python
def parse_article_html(html: str) -> dict
```

- 输入：详情页完整 HTML 源码
- 输出：包含 `title`, `content_text`, `source`, `publish_date`, `keywords`, `description`, `pub_date_raw`, `column` 的字典

**日期解析策略：**

```python
for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
    try:
        publish_date = datetime.strptime(pub_date_raw[:16], fmt)
        break
    except ValueError:
        continue
```

- 优先尝试 `2026-05-18 10:19` 格式
- 回退尝试 `2026-05-18` 格式
- 解析失败 → `publish_date = None`

**关键词解析：**
- 以逗号 `,` 分隔 `keywords_raw`
- 去除空白后返回 `list[str]`

### `fetch_and_parse_article(url: str) -> Article`

```python
def fetch_and_parse_article(url: str) -> Article
```

- 输入：文章 URL（支持相对路径和完整 URL）
- 补全相对 URL → 绝对 URL
- HTTP GET → `parse_article_html()` 解析
- 从 URL 提取 `article_id`（去掉 `.html` 后缀）
- 返回填充了所有字段的 `Article` 对象

**异常：**
- `requests.RequestException` — 网络错误
- `ValueError` — 响应正文为空

## 设计决策

1. **meta 优先于 DOM** — 标题/来源/日期优先从 `<meta>` 提取（结构化、准确），正文从 `div#con_con` 提取
2. **标题以 `ArticleTitle` meta 为准** — 不取 `<h1>` 或 `<title>` 标签，因为 meta 最为规范
3. **article_id 从 URL 提取** — 保持与 fetcher 模块一致的提取逻辑
4. **正文按段落分隔** — 使用 `"\n\n"` 连接各 `<p>` 标签文本，适合 Markdown 渲染

## 限制

- **页面结构依赖** — 正文选择器 `div#con_con` 是硬编码的，若工信部改版需更新
- **meta 标签依赖** — 标题/来源/日期依赖 `<meta>` 标签存在，若缺失则返回空字符串
- **日期格式有限** — 仅支持两种日期格式，其他格式会被静默丢弃
- **附件提取未实现** — 当前不提取正文中的附件链接

## 测试覆盖

参见 `tests/test_parser.py`:

- 完整 HTML 页面 → 正确提取 title/source/date/content
- 含 `PubDate` 格式 `YYYY-MM-DD HH:MM` → 正确解析
- 含 `PubDate` 格式 `YYYY-MM-DD` → 正确解析
- `div#con_con` 为空 → content_text 为空字符串
- 无 meta 标签 → 所有字段为空（不抛异常）
- URL 补全逻辑（相对 → 绝对）
- `article_id` 提取逻辑
- 网络超时/异常