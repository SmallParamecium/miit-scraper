# Changelog

所有涉及本项目的显著变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [0.1.0] - 2026-05-19

### 新增

- 核心数据模型：`Article` 和 `ArticleList` dataclass（#22）
- 列表页 API 爬取：通过大汉版通 CMS 接口获取工信部时政要闻文章列表（#24）
- 详情页解析：从文章 HTML 中提取 meta 元数据和纯文本正文（#26）
- CLI 命令行入口：支持 `--count`、`--output-dir`、`--raw-dir`、`--no-detail`、`--version`（#28）
- 数据导出：每篇文章生成 JSON 原始数据文件和 Markdown 正文文件（#28）
- 使用 uv 管理 Python 依赖和虚拟环境
- 共 58 个单元测试（pytest），覆盖 models / fetcher / parser / exporter / cli 五个模块
- 4 份 OpenSpec 文档（docs/spec-issue-*.md）