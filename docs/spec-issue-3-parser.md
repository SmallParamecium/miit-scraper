# Spec: 详情页解析 (Issue #3)

**版本**: 0.1.0
**关联 Issue**: [#3](https://github.com/SmallParamecium/miit-scraper/issues/3)
**模块**: `src/miit_scraper/parser.py`

---

## 概述

抓取并解析工信部文章详情页，从 HTML 源码中提取：标题、正文、发布时间、来源、关键词、摘要等结构化内容。

---

## 1. 详情页结构（2026年5月实测）

### 1.1 Meta 元数据

通过 `<meta name="..." content="...">` 标签提供结构化元数据：

| meta name | 映射字段 | 示例值 |
|-----------|----------|--------|
| `ArticleTitle` | `title` | 工业和信息化部发布... |
| `PubDate` | `pub_date_raw` | 2026-05-18 10:19 |
| `ContentSource` | `source` | 新华社 |
| `Description` | `description` | 文章摘要文本 |
| `Keywords` | `keywords_raw` | 工信部,政策,通信 |
| `ColumnName` | `column` | 时政要闻 |
| `SiteName` | `site_name` | 工业和信息化部 |
| `Url` | `rel_url` | /xwfb/szyw/art/2026/art_xxx.html |

### 1.2 正文容器

- CSS 选择器: `div#con_con`
- 子元素: `<p>` 标签（每个段落一个）
- 预处理: 移除 `<script>` 和 `<style>` 标签
- 拼接: `"\n\n"` 作为段落分隔符

---

## 2. 函数契约

### 2.1 `parse_article_html(html: str) -> dict`

**纯函数**：从 HTML 源码提取结构化内容，不涉及网络请求。

**返回值**:
```python
{
    "title": str,           # 标题 (ArticleTitle)
    "content_text": str,    # 纯文本正文
    "source": str,          # 来源 (ContentSource)
    "publish_date": Optional[datetime],  # 发布日期
    "keywords": list[str],  # 关键词列表
    "description": str,     # 摘要
    "pub_date_raw": str,    # 原始日期字符串
    "column": str,          # 栏目名称
}
```

**日期解析规则**:
- 优先格式: `%Y-%m-%d %H:%M`（取前16字符）
- 回退格式: `%Y-%m-%d`
- 均失败: `publish_date=None`

**关键词解析规则**:
- 按 `,` 分割
- 每条 `strip()` 去空白
- 跳过空字符串
- 无关键词时返回空列表 `[]`

### 2.2 `fetch_and_parse_article(url: str) -> Article`

**网络+解析**: 请求详情页 → 解析内容 → 返回完整 Article。

**URL 处理**:
- 相对路径（以 `/` 开头）→ 补全为 `https://www.miit.gov.cn + url`
- 完整 URL → 直接使用

**请求配置**:
- 超时: 30 秒
- Referer: `https://www.miit.gov.cn/xwfb/szyw/`

---

## 3. 错误处理

| 场景 | 行为 |
|------|------|
| 网络超时/错误 | 抛出 `requests.RequestException` |
| 响应内容为空 | 抛出 `ValueError("详情页返回空内容: ...")` |
| meta 标签缺失 | 对应字段为空字符串，不抛异常 |
| div#con_con 不存在 | `content_text=""` |
| 日期格式无法解析 | `publish_date=None` |
| URL 中无 article_id | `article_id=""` |

---

## 4. 数据流

```
URL → HTTP GET → HTML 源码
                      ↓
              parse_article_html()
                      ↓
              dict {title, content_text, source, publish_date, ...}
                      ↓
              Article 构造 → 返回
```

---

## 5. 测试覆盖

| 测试 | 覆盖内容 |
|------|----------|
| `test_parse_meta_fields` | Meta 标签提取 |
| `test_parse_content` | 正文提取（多段落） |
| `test_parse_date_format_1` | `%Y-%m-%d %H:%M` 格式 |
| `test_parse_date_format_2` | `%Y-%m-%d` 格式 |
| `test_parse_no_date` | 无日期标签 |
| `test_parse_keywords` | 关键词解析（逗号分隔） |
| `test_parse_no_con_con` | 无正文容器 |
| `test_parse_empty_html` | 空 HTML |
| `test_fetch_and_parse_relative_url` | 相对 URL 补全 + 完整流程 |
| `test_fetch_and_parse_network_error` | 网络错误 |

**文件**: `tests/test_parser.py` (10 tests)