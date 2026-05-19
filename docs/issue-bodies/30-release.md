> ⚠️ 本 Issue 为回溯补写，内容基于完成后的代码和 spec 文档反向整理。

# Issue #0: v0.1.0 Release — 核心功能完成，发布首个正式版本

## 背景 / 为什么现在做

Issue #1~#4 已完成全部核心功能（models、fetcher、parser、cli + exporter），同时修复了 ImportError bug（#32）和补建了 OpenSpec 文档（#34）。项目功能已闭环：

- 从工信部 CMS API 获取时政要闻文章列表
- 解析文章详情页 HTML，提取正文和元数据
- 以 JSON + Markdown 双格式输出
- CLI 命令行工具可用

现在需要标记首个正式版本 v0.1.0，创建 CHANGELOG、更新 README，并通过 GitHub Release 发布。

## 当前想收住的不确定性

首个版本应包含哪些内容？版本号策略是什么？CHANGELOG 格式？

## 已收敛的推荐方案

- 版本号 `0.1.0`（Semantic Versioning）
- CHANGELOG 采用 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 格式
- GitHub Release 附带 release notes

## 方案权衡记录

略（Release Issue 不涉及技术方案选型）。

## 本 Issue 想解决什么

- [x] 定义版本号 `0.1.0`
- [x] 撰写 CHANGELOG.md（v0.1.0 内容）
- [x] 更新 README.md（功能列表、快速开始、项目结构）
- [x] 在 GitHub 上创建 v0.1.0 Release
- [x] 打 git tag `v0.1.0`

## 明确不解决什么

- 不引入 v0.2.0 新功能规划（后续 Issue 独立处理）
- 不发布到 PyPI（当前仅 GitHub Release）
- 不做自动化 CI/CD 发布管道

## 当前已知上下文

- `CHANGELOG.md`：v0.1.0 变更记录
- `README.md`：项目介绍、快速开始、技术栈
- 代码仓库：github.com/SmallParamecium/miit-scraper

## 前置依赖

- Issue #22: models.py 已完成
- Issue #24: fetcher.py 已完成
- Issue #26: parser.py 已完成
- Issue #28: cli.py + exporter.py 已完成
- Issue #32: ImportError bug 已修复
- Issue #34: OpenSpec 文档已补建
- 所有测试通过（58 个单元测试）

## 子任务树

- [x] 确认全部 Issue 已关闭
- [x] 确认所有测试通过：`uv run pytest tests/ -v`
- [x] 撰写 `CHANGELOG.md`
- [x] 更新 `README.md`
- [x] 打 tag `git tag -a v0.1.0 -m "v0.1.0: 首个正式版本"`
- [x] Push tag: `git push origin v0.1.0`
- [x] 在 GitHub 创建 Release，附 CHANGELOG 内容

## 验收口径

### 必须成立

- `uv run miit-scraper --count 3` 可成功运行并输出 6 个文件
- `uv run pytest tests/ -v` 全部 58 个测试通过
- `git tag -l "v0.1.0"` 显示 tag 存在
- GitHub Release 页面可见 v0.1.0
- CHANGELOG.md 记录完整的 v0.1.0 变更内容
- README.md 包含正确的项目结构图和快速开始指令

### 明确不成立

- 不应有未关闭的核心 Issue 被遗漏
- CHANGELOG 不应使用非标格式

### 失败信号

- 核心功能在新环境执行失败
- 测试覆盖率骤降
- 文档与实际代码不一致

## Harness / 验证要求

- [x] `uv run pytest tests/ -v` 全部通过（58 tests passed）
- [x] `uv run miit-scraper --count 3` 端到端验证成功
- [x] `gh release view v0.1.0` 可查看 Release 信息