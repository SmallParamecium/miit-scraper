# miit-scraper Spec 文档索引

**版本**: 0.1.0 | **仓库**: [SmallParamecium/miit-scraper](https://github.com/SmallParamecium/miit-scraper)

---

## Spec 文档列表

| # | 文件 | Issue | 模块 | 类型 |
|---|------|-------|------|------|
| 1 | `spec-issue-1-models.md` | [#1](https://github.com/SmallParamecium/miit-scraper/issues/1) | 数据模型 | feature |
| 2 | `spec-issue-2-fetcher.md` | [#2](https://github.com/SmallParamecium/miit-scraper/issues/2) | 列表 API | feature |
| 3 | `spec-issue-3-parser.md` | [#3](https://github.com/SmallParamecium/miit-scraper/issues/3) | 详情解析 | feature |
| 4 | `spec-issue-4-cli.md` | [#4](https://github.com/SmallParamecium/miit-scraper/issues/4) | CLI + 导出 | feature |
| 5 | `spec-issue-11-fix-import-and-gitignore.md` | [#11](https://github.com/SmallParamecium/miit-scraper/issues/11) | CLI + .gitignore | bugfix |

---

## 模块架构

```
┌─────────────────┐
│   CLI (cli.py)   │  ← 入口，串联流程
└────────┬────────┘
         │
    ┌────▼────┐
    │ Fetcher  │  ← API 请求 + HTML 片段解析
    └────┬────┘
         │
    ┌────▼────┐
    │ Parser   │  ← 详情页抓取 + 正文提取
    └────┬────┘
         │
    ┌────▼────┐
    │ Exporter │  ← JSON / Markdown 输出
    └────┬────┘
         │
    ┌────▼────┐
    │ Models   │  ← Article / ArticleList
    └─────────┘
```

---

## 数据流

```
API 端点 → Fetcher → ArticleList
                          ↓
                    Parser (逐篇)
                          ↓
              完整 Article 列表
                          ↓
                    Exporter
                    ↓         ↓
                  JSON      Markdown
```

---

## 每个 Spec 文档结构

所有 spec 遵循统一结构：

1. **概述** — 功能说明
2. **契约** — 输入/输出/参数/格式
3. **错误处理** — 异常场景与行为
4. **数据流** — 处理流程（如适用）
5. **测试覆盖** — 测试清单