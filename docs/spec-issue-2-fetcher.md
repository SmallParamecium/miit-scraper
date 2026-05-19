# spec-issue-2: 列表页 API 抓取模块（fetcher.py）

> 关联 Issue: [#24](https://github.com/SmallParamecium/miit-scraper/issues/24)
> 实现文件: `src/miit_scraper/fetcher.py`

## 目标

调用工信部 CMS（大汉版通）的 jpaas-publish-server 接口获取时政要闻文章列表，将返回的 HTML 片段解析为 `Article` 对象。

## 范围

- 构造 API 请求参数（固定参数 + 动态 `pageNo` / `pageSize`）
- HTTP GET 请求 + 响应状态校验
- BeautifulSoup 解析 HTML 片段提取文章信息
- 返回 `ArticleList`（含分页信息）

## API 端点

```
GET https://www.miit.gov.cn/api-gateway/jpaas-publish-server/front/page/build/unit
```

### 固定参数（从页面源码中提取）

| 参数 | 值 |
|------|-----|
| `parseType` | `buildstatic` |
| `webId` | `8d828e408d90447786ddbe128d495e9e` |
| `tplSetId` | `209741b2109044b5b7695700b2bec37e` |
| `pageType` | `column` |
| `tagId` | `右侧内容` |
| `pageId` | `6333578be1d646aabc3e0e79406688c9` |

### 动态参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `pageNo` | int | 页码，从 1 开始 |
| `pageSize` | int | 每页数量，默认 10 |

### 响应结构

```json
{
  "success": true,
  "data": {
    "html": "<ul><li class='cf'><a class='fl' ...>...</a><span class='fr'>2026-05-17</span></li>...</ul>"
  }
}
```

## HTML 解析结构

API 返回 `data.html` 为 HTML 片段，每个 `<li class="cf">` 对应一篇文章：

```html
<li class="cf">
    <a class="fl" href="/xwfb/szyw/art/2026/art_uuid.html"
       target="_blank" title="文章标题">
        文章标题
    </a>
    <span class="fr">2026-05-17</span>
</li>
```

### CSS 选择器

| 目标 | 选择器 | 说明 |
|------|--------|------|
| 文章条目 | `ul li.cf` | 每个 li 是一篇文章 |
| 标题/链接 | `a.fl` | title 属性优先，fallback 为 text |
| 发布日期 | `span.fr` | 格式 `YYYY-MM-DD` |

## 公开接口

### `fetch_article_list(page: int, page_size: int) -> ArticleList`

```python
def fetch_article_list(page: int = 1, page_size: int = 10) -> ArticleList
```

- 调用 `_fetch_api_response()` → 获取 JSON
- 调用 `_parse_article_html()` → 提取 Article 列表
- 调用 `_extract_total_count()` → 尝试提取总数（fallback 为 0）
- 返回 `ArticleList(total, articles, page, page_size)`

**异常：**
- `requests.RequestException` — 网络错误
- `ValueError` — API 返回 `success != true` 或 HTML 为空

## 内部函数

### `_fetch_api_response(page, page_size) -> dict`

- 合并固定参数和动态参数
- 设置 headers（User-Agent 模拟 Chrome，Referer 设为栏目页）
- 检查 `success` 字段

### `_parse_article_html(html_fragment: str) -> list[Article]`

- BeautifulSoup 解析，选择器 `ul li.cf`
- URL 补全：相对路径 → `https://www.miit.gov.cn` + 相对路径
- `article_id` 提取：从 URL 末尾提取文件名（去掉 `.html`）
- 日期解析：`datetime.strptime(date_str, "%Y-%m-%d")`

### `_extract_total_count(html_fragment: str) -> int`

- 尝试从 `div.page` 文本中匹配 `共 X 条`
- 匹配不到返回 0

## 设计决策

1. **固定参数从页面源码提取** — CMS 无公开 API 文档，参数通过浏览器 DevTools 抓包获取，`webId` / `tplSetId` / `pageId` 等均为站点唯一标识
2. **HTML 片段解析而非 JSON 列表** — CMS 返回的是渲染好的 HTML 片段而非结构化数据，需 BeautifulSoup 二次解析
3. **日期格式仅支持 `YYYY-MM-DD`** — 列表页 span.fr 的日期格式，不支持其他格式
4. **total 字段可选** — `_extract_total_count()` 可能返回 0，调用方不应依赖此值进行翻页计算

## 限制

- **API 参数依赖页面结构** — 若工信部 CMS 升级或更换系统，固定参数可能失效
- **HTML 结构依赖** — 依赖 `li.cf` / `a.fl` / `span.fr` 选择器，页面改版会导致解析失败
- **无分页信息** — API 不返回 `total`、`has_next` 等标准分页字段，`total` 通过正则从 HTML 提取（不可靠）
- **单线程** — 不涉及并发，每次请求耗时约 2-5 秒

## 测试覆盖

参见 `tests/test_fetcher.py`:

- API 正常响应 → 正确解析 Article 列表
- API 返回 `success: false` → 抛出 ValueError
- HTML 片段为空 → 抛出 ValueError
- HTML 无 `li.cf` → 返回空列表
- URL 补全逻辑（相对 → 绝对）
- `_extract_total_count()` 有/无分页信息
- 网络超时/异常处理