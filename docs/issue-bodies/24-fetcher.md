> ⚠️ 本 Issue 为回溯补写，内容基于完成后的代码和 spec 文档反向整理。

# Issue #2: 文章列表页 API 爬取 — fetcher.py

## 背景 / 为什么现在做

Issue #1 定义了数据模型。第二步需要获取数据源——从工信部网站拉取时政要闻文章列表。工信部使用大汉版通（大汉 CMS）的 `jpaas-publish-server` 接口动态加载列表内容，返回的是 JSON 包裹的 HTML 片段，而非标准 RESTful API。

如果不先收住 API 调用细节和 HTML 解析逻辑，后续 parser 和 cli 模块都会依赖歧义的数据格式。

## 当前想收住的不确定性

- CMS API 端点 URL 及其固定参数是什么？
- API 返回的 JSON 结构与 HTML 片段如何映射到 `Article` 模型？
- 分页机制（`pageNo`/`pageSize`）与 total 计数如何获取？
- User-Agent / Referer 等反爬头如何设置？

## 已收敛的推荐方案

本 Issue 按以下口径实现：

- 发送 GET 请求到 CMS API，携带从页面源码中提取的 6 个固定参数
- 用 BeautifulSoup 解析 `data.html` 字段中的 `<li class="cf">` 列表
- 从 `<a>` 标签提取 title/href，从 `<span>` 提取发布日期
- 返回 `ArticleList` 对象（封装分页信息）

## 方案权衡记录

### 1. API 发现方式：逆向 vs 官方文档

**推荐：方案 A（逆向工程）。**

方案 A：从浏览器 Network 面板捕获 API 请求，提取固定参数。

优点：
- 参数真实可用
- 无需猜测 CMS 内部逻辑
缺点：
- 工信部可能更换 CMS 或修改参数名，需持续维护

方案 B：查找官方 CMS 文档。

优点：规范
缺点：大汉版通无公开文档

方案 C：直接解析列表页 HTML。

优点：最简单
缺点：列表页静态 HTML 不包含完整文章列表（由 JS 动态加载）

### 2. HTML 解析方式：BeautifulSoup vs lxml vs regex

**推荐：方案 A（BeautifulSoup + lxml 解析器）。**

方案 A：BeautifulSoup(`html`, `"html.parser"`)。

优点：
- 对 CMS 可能产生的畸形 HTML 容错性高
- 选择器语法直观（`soup.select("ul li.cf")`）
- Python 生态标准库
缺点：
- 速度不如纯 lxml

方案 B：直接 lxml + XPath。

优点：更快
缺点：语法不如 CSS 选择器直观

方案 C：正则表达式。

优点：无依赖
缺点：HTML 结构稍有变化即失效

### 3. 分页 total 处理

**推荐：方案 A（从 HTML 片段中提取 "共 X 条"）。**

方案 A：正则匹配分页区域中的 `共\s*(\d+)\s*条`。

优点：真实 total 值
缺点：CMS 不保证分页区域始终存在

方案 B：不获取 total，设为 0。

优点：零额外逻辑
缺点：cli 和 exporter 无法判断是否有更多页

方案 C：持续请求下一页直到返回空。

优点：总能获取完整数据
缺点：时间复杂度不确定

## 本 Issue 想解决什么

- [x] 定位 CMS API 端点（`/api-gateway/jpaas-publish-server/front/page/build/unit`）
- [x] 提取固定参数（webId、tplSetId、pageType、tagId、pageId、parseType）
- [x] 设置 HTTP Headers（User-Agent、Referer、Accept）
- [x] 用 BeautifulSoup 解析 `data.html` 中的 `<li class="cf">` 元素
- [x] 从 `<a>` 标签提取 title、href，从 `<span>` 提取日期
- [x] 从 URL 提取 article_id
- [x] 补全相对 URL 为绝对 URL
- [x] 封装为 `fetch_article_list(page, page_size) -> ArticleList`
- [x] 实现 `_extract_total_count()` 提取总记录数

## 明确不解决什么

- 不做多页并发请求（asyncio）
- 不做请求重试 / 指数退避
- 不做 CMS 变更自动适配
- 不处理 IP 封禁策略
- 不做 SEO-friendly 静态页面抓取

## 当前已知上下文

- `src/miit_scraper/fetcher.py`：API 请求 + HTML 解析
- `src/miit_scraper/models.py`：Article、ArticleList 数据模型
- API 端点于 2026 年 5 月实测可用

## 前置依赖

- Issue #1: models.py 已完成（Article、ArticleList dataclass）

## 子任务树

- [x] 在浏览器中 Capturing Network 请求，定位 CMS API
- [x] 提取 6 个固定查询参数
- [x] 实现 `_fetch_api_response(page, page_size)` 发送 HTTP GET
- [x] 实现 `_parse_article_html(html_fragment)` 用 BeautifulSoup 解析
- [x] 实现 `_extract_total_count()` 正则提取 total
- [x] 实现 `fetch_article_list()` 主入口
- [x] 编写 `tests/test_fetcher.py` 单元测试
- [x] 实际运行验证→数据正确

## 验收口径

### 必须成立

- `fetch_article_list(page=1, page_size=5)` 返回 ArticleList 含 5 篇文章
- 每篇文章的 title、url、article_id 非空
- 相对 URL（如 `/xwfb/szyw/art/...`）被补全为 `https://www.miit.gov.cn/xwfb/szyw/art/...`
- 发布日期解析正确（`datetime.strptime("2026-05-17", "%Y-%m-%d")`）
- API 返回非 success 响应时抛出 `ValueError`

### 明确不成立

- 不应出现 HTML 标签残留（如未 strip 的空白字符）
- 不应出现 400/403/500 等 HTTP 错误被静默吞掉
- article_id 不应包含 `.html` 后缀

### 失败信号

- API 参数（webId 等）失效导致 403
- HTML 结构变化导致 `soup.select("ul li.cf")` 返回空
- 从测试环境运行时被反爬拦截

## Harness / 验证要求

参见 `tests/test_fetcher.py`：

- [x] 测试 `_parse_article_html` 对示例 HTML 片段的解析（含完整字段、缺失日期、缺失 URL）
- [x] 测试 `_fetch_api_response` mock 场景（正常响应、API 失败、网络异常）
- [x] 集成测试：实际请求 CMS API，验证至少返回 1 篇文章
- [x] 测试 `_extract_total_count` 对有/无分页信息的 HTML