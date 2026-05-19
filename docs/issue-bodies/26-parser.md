> ⚠️ 本 Issue 为回溯补写，内容基于完成后的代码和 spec 文档反向整理。

# Issue #3: 文章详情页解析 — parser.py

## 背景 / 为什么现在做

Issue #2 完成了列表页爬取，获取到文章的标题、URL、发布日期。但完整爬虫需要提取文章**正文内容**、来源、关键词等元数据。这些信息仅存在于详情页 HTML 中。

工信部详情页结构（2026 年 5 月实测）：
- 元数据通过 `<meta name="ArticleTitle" content="...">` 等标签提供
- 正文在 `div#con_con > p` 标签中
- 需要携带 Referer 头请求（否则可能被拦截或返回空白）

如果不统一详情页解析逻辑，每个调用方都需要自己处理 HTML 解析、日期格式兼容、URL 补全等细节。

## 当前想收住的不确定性

- 详情页 `<meta>` 标签有哪些字段？如何映射到 Article？
- 正文提取的 DOM 选择器是什么？
- 日期格式是否统一（`2026-05-18 10:19` vs `2026-05-18`）？
- URL 补全和 article_id 提取是否需要重复实现？

## 已收敛的推荐方案

本 Issue 按以下口径实现：

- `parse_article_html(html)` 纯函数：接收 HTML 字符串返回结构化 dict
- `fetch_and_parse_article(url)` 高级函数：GET 请求 → 解析 → Article
- meta 字段映射通过 `META_FIELD_MAP` 字典统一管理
- 日期兼容多种格式（`%Y-%m-%d %H:%M` 和 `%Y-%m-%d`）

## 方案权衡记录

### 1. 正文提取方式：CSS Selector vs XPath vs 全文清洗

**推荐：方案 A（`div#con_con > p` 文本提取）。**

方案 A：用 BeautifulSoup 定位 `div#con_con`，提取所有 `<p>` 标签文本。

优点：
- 精准定位正文容器
- 避开导航、侧边栏等非内容 DOM
- 移除 script/style 标签防污染
缺点：
- 如果 CMS 改用 `<div>` 而非 `<p>` 包裹段落，需适配

方案 B：用 `html2text` 将整页转为 Markdown。

优点：一行代码
缺点：混入导航/页脚/JS 等噪音

方案 C：`soup.get_text()` 全页文本。

优点：最简单
缺点：包含大量非文章内容，后续清洗逻辑复杂

### 2. meta 标签提取策略

**推荐：方案 A（`META_FIELD_MAP` 字典映射）。**

方案 A：`{"ArticleTitle": "title", "PubDate": "pub_date_raw", ...}` 映射字典。

优点：
- 语义清晰
- 新增 meta 字段只需加一行映射
- 原始值保留在 `meta_data` 中不被覆盖
缺点：
- 工信部改名 `ArticleTitle` → `Title` 时需同步修改

方案 B：直接用 `soup.find("meta", {"name": "ArticleTitle"})`。

优点：零映射
缺点：每个字段都要写单独的查找逻辑

方案 C：全部 meta 标签一次性收集。

优点：覆盖未知字段
缺点：产生大量无用数据

### 3. 日期解析策略

**推荐：方案 A（尝试多种格式 + 回退 None）。**

方案 A：`datetime.strptime(pub_date_raw[:16], fmt)` 遍历格式列表。

优点：
- 兼容 `2026-05-18 10:19` 和 `2026-05-18`
- 解析失败不抛异常，返回 None
缺点：
- 未知格式会被丢弃（可控风险）

方案 B：用 `dateutil.parser.parse()`。

优点：自动识别所有格式
缺点：引入额外依赖（python-dateutil）

## 本 Issue 想解决什么

- [x] 实现 `parse_article_html(html)` 纯解析函数
- [x] 定义 `META_FIELD_MAP` meta 标签字段映射表
- [x] 提取 meta：ArticleTitle、PubDate、ContentSource、Description、Keywords
- [x] 从 `div#con_con > p` 提取正文纯文本
- [x] 日期多格式兼容解析（`%Y-%m-%d %H:%M` / `%Y-%m-%d`）
- [x] 关键词列表解析（逗号分隔 → `list[str]`）
- [x] 实现 `fetch_and_parse_article(url)` 完整流程
- [x] URL 补全为绝对 URL
- [x] 从 URL 提取 article_id

## 明确不解决什么

- 不做附件下载（PDF/Word 链接提取但不下载）
- 不做图片提取和本地化
- 不做 HTML 原文保留（仅保存 content_text 纯文本）
- 不做文章内链追踪
- 不做内容去重

## 当前已知上下文

- `src/miit_scraper/parser.py`：详情页请求 + 解析
- `src/miit_scraper/models.py`：Article dataclass
- 详情页 DOM 结构于 2026 年 5 月实测

## 前置依赖

- Issue #1: models.py 已完成
- Issue #2: fetcher.py 已完成（提供文章 URL）

## 子任务树

- [x] 分析详情页 HTML 结构（meta 标签、正文容器）
- [x] 实现 `META_FIELD_MAP` 字段映射
- [x] 实现 `parse_article_html(html)` 纯解析函数
- [x] 实现日期解析逻辑（多格式兼容）
- [x] 实现关键词列表解析
- [x] 实现 `fetch_and_parse_article(url)` 高级入口
- [x] URL 补全逻辑
- [x] article_id 提取
- [x] 编写 `tests/test_parser.py` 单元测试
- [x] 实际抓取文章验证正文完整性

## 验收口径

### 必须成立

- `parse_article_html(详情页HTML)` 返回的 dict 包含 title、content_text、source、publish_date、keywords
- 正文 `content_text` 非空（对真实文章）
- meta `ArticleTitle` 内容映射为 `title` 字段
- meta `ContentSource` 内容映射为 `source` 字段
- `2026-05-18 10:19` 格式日期正确解析为 datetime
- `2026-05-18` 格式日期也能正常解析
- `div#con_con` 中的 `<script>` `<style>` 标签被移除
- `fetch_and_parse_article(相对URL)` 自动补全为绝对 URL

### 明确不成立

- 正文中不应包含 `<div#con_con>` 以外的页面元素文本
- 日期解析失败时不应抛异常，应返回 None
- 不应在正文中包含 script/style 标签内容

### 失败信号

- 工信部详情页改版（`div#con_con` 改为其他 ID）
- meta 标签重命名导致全部元数据缺失
- 反爬加重（需要 Cookie 或 JS 渲染）

## Harness / 验证要求

参见 `tests/test_parser.py`：

- [x] `parse_article_html` 对示例详情页 HTML 的解析（含所有 meta 字段、正文、日期）
- [x] 测试关键词解析（单个、多个、空字符串）
- [x] 测试日期多格式兼容
- [x] 测试 script/style 标签被移除
- [x] 测试缺少某些 meta 标签时的容错
- [x] 集成测试：实际请求一篇真实文章