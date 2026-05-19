# Spec: 列表页 API 获取 (Issue #2)

**版本**: 0.1.0
**关联 Issue**: [#2](https://github.com/SmallParamecium/miit-scraper/issues/2)
**模块**: `src/miit_scraper/fetcher.py`

---

## 概述

通过大汉版通 CMS 的 jpaas-publish-server API 获取工信部时政要闻文章列表。API 返回 JSON 包裹的 HTML 片段，需二次解析提取结构化数据。

---

## 1. API 端点契约

### 1.1 端点信息

| 属性 | 值 |
|------|-----|
| 基础 URL | `https://www.miit.gov.cn` |
| API 路径 | `/api-gateway/jpaas-publish-server/front/page/build/unit` |
| 请求方法 | `GET` |
| Content-Type | `application/json` |

### 1.2 固定参数

| 参数 | 值 | 说明 |
|------|-----|------|
| `parseType` | `"buildstatic"` | 解析类型 |
| `webId` | `"8d828e408d90447786ddbe128d495e9e"` | 站点 ID |
| `tplSetId` | `"209741b2109044b5b7695700b2bec37e"` | 模板集 ID |
| `pageType` | `"column"` | 页面类型 |
| `tagId` | `"右侧内容"` | 标签 ID |
| `pageId` | `"6333578be1d646aabc3e0e79406688c9"` | 页面 ID |

### 1.3 动态参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `pageNo` | `int` | 页码，从 1 开始 |
| `pageSize` | `int` | 每页数量 |

### 1.4 请求头

```
User-Agent: Chrome/120.0 (Windows NT 10.0; Win64; x64)
Referer: https://www.miit.gov.cn/xwdt/szyw/
Accept: application/json, text/javascript, */*; q=0.01
```

---

## 2. 响应处理

### 2.1 响应格式

```json
{
  "success": true,
  "data": {
    "html": "<ul>...</ul>"
  }
}
```

### 2.2 HTML 片段结构

```html
<li class="cf">
  <a class="fl" href="/xwfb/szyw/art/2026/art_xxx.html"
     target="_blank" title="文章标题">
    <i></i>文章标题
  </a>
  <span class="fr">2026-05-17</span>
</li>
```

### 2.3 解析规则

| 字段 | CSS 选择器 | 提取逻辑 |
|------|-----------|----------|
| 标题 | `a.fl` | 优先 `title` 属性，回退为元素文本 |
| URL | `a.fl[href]` | 相对路径补全为 `BASE_URL + href` |
| 日期 | `span.fr` | `strptime(date_str, "%Y-%m-%d")` |
| article_id | URL | 取最后一个 `/` 后的部分，去掉 `.html` 后缀 |

---

## 3. 函数契约

### 3.1 `fetch_article_list(page=1, page_size=10) -> ArticleList`

**主入口**：调用 API → 解析 HTML → 返回分页结果。

**异常**:
- `requests.RequestException`: 网络错误
- `ValueError`: API 返回 `success: false` 或 HTML 片段为空

### 3.2 `_fetch_api_response(page, page_size) -> dict`

**私有函数**：发送 HTTP 请求，返回原始 JSON。

**超时**: 30 秒

### 3.3 `_parse_article_html(html_fragment) -> list[Article]`

**私有函数**：从 HTML 片段解析文章列表。

**边界条件**:
- CSS 选择器匹配不到时返回空列表
- 日期解析失败时 `publish_date=None`

### 3.4 `_extract_total_count(html_fragment) -> int`

**私有函数**：从分页信息提取总记录数。

**规则**:
- 正则匹配 `共 X 条`
- 匹配不到返回 `0`

---

## 4. 错误处理

| 场景 | 行为 |
|------|------|
| 网络超时 | 抛出 `requests.RequestException` |
| API 返回 `success: false` | 抛出 `ValueError` |
| HTML 片段为空 | 抛出 `ValueError` |
| 日期格式异常 | `publish_date=None`，不中断流程 |
| 分页信息缺失 | `total=0` |

---

## 5. 测试覆盖

| 测试 | 覆盖内容 |
|------|----------|
| `test_fetch_api_response_success` | 正常 API 响应 |
| `test_fetch_api_response_failure` | API 错误码 |
| `test_fetch_api_response_network_error` | 网络异常 |
| `test_parse_html_single` | 单篇文章解析 |
| `test_parse_html_multiple` | 多篇文章解析 |
| `test_parse_html_no_articles` | 空 HTML |
| `test_parse_html_missing_fields` | 字段缺失回退 |
| `test_fetch_article_list_integration` | 完整流程 |
| `test_relative_url_resolution` | 相对 URL 补全 |
| `test_extract_total_count` | 总数提取 |

**文件**: `tests/test_fetcher.py` (10 tests)