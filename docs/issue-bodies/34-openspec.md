> ⚠️ 本 Issue 为回溯补写，内容基于完成后的代码和 spec 文档反向整理。

# Chore: 补建 OpenSpec 文档 — 将现有代码的设计决策落成 spec 文档

## 背景 / 为什么现在做

项目采用 **spec-driven 开发** 范式：先写 spec 定义范围 → 再写代码实现 → 代码与 spec 保持一致。但在实际开发中，Issue #1~#4 是先写完代码再补 spec 文档（因为项目启动时对工信部 CMS 结构和反爬策略缺乏了解，需要探索性开发）。

现在代码已稳定，#1~#4 的设计决策需要正式落为 spec 文档，以便：
- 未来重构时有明确的设计参考
- 新贡献者理解各模块的设计意图
- 代码 review 时有 spec 作为「真理源」

## 当前想收住的不确定性

- spec 文档应包含哪些内容？
- spec 文档的存放位置和命名规范？
- spec 与 Issue body 的关系（是否重复）？

## 已收敛的推荐方案

创建 4 份 OpenSpec 文档，放置于 `docs/` 目录：

| 文件 | 对应模块 | 关联 Issue |
|---|---|---|
| `docs/spec-issue-1-models.md` | 数据模型定义 | #22 |
| `docs/spec-issue-2-fetcher.md` | 列表页 API 爬取 | #24 |
| `docs/spec-issue-3-parser.md` | 详情页解析 | #26 |
| `docs/spec-issue-4-cli.md` | CLI + 导出 | #28 |

每份 spec 包含：目标、范围、数据结构/API、设计决策、限制、测试覆盖。

## 方案权衡记录

### Spec 格式：OpenSpec vs ADR (Architecture Decision Records)

**推荐：方案 A（OpenSpec）。**

方案 A：一份 spec 对应一个 Issue/模块，包含「目标 → 范围 → 设计 → 测试」。

优点：
- 与 spec-driven 开发流程天然匹配
- 一份 spec 完整描述一个模块
缺点：
- 模块边界模糊时 spec 会交叉引用

方案 B：ADR（每个设计决策一个文件）。

优点：决策粒度更细
缺点：文件过多，且与本项目 Issue-based 流程不匹配

### 存放位置：docs/ vs .openspec/

**推荐：方案 A（docs/）。**

方案 A：`docs/spec-issue-*.md`。

优点：
- 与项目文档统一管理
- GitHub 自动渲染 docs/ 目录文件
缺点：
- 与 Issue 和 PR 不在同一视图中

方案 B：`.openspec/`。

优点：名称明确（OpenSpec）
缺点：点开头的隐藏目录不直观

## 本 Issue 想解决什么

- [x] 创建 `docs/spec-issue-1-models.md`
- [x] 创建 `docs/spec-issue-2-fetcher.md`
- [x] 创建 `docs/spec-issue-3-parser.md`
- [x] 创建 `docs/spec-issue-4-cli.md`
- [x] 确保 spec 与当前代码实现一致

## 明确不解决什么

- 不重写代码（仅补文档）
- 不创建 Issue #5+ 的 spec（未来 Issue 独立处理）
- 不创建 Issue template / PR template（后续 CI/CD 优化）

## 当前已知上下文

- `docs/spec-issue-1-models.md`：数据模型 spec
- `docs/spec-issue-2-fetcher.md`：列表爬取 spec
- `docs/spec-issue-3-parser.md`：详情解析 spec
- `docs/spec-issue-4-cli.md`：CLI + 导出 spec
- 4 份 spec 与当前代码完全一致

## 前置依赖

- Issue #22~#28 全部已完成（spec 描述的对象）

## 子任务树

- [x] 编写 `docs/spec-issue-1-models.md`
- [x] 编写 `docs/spec-issue-2-fetcher.md`
- [x] 编写 `docs/spec-issue-3-parser.md`
- [x] 编写 `docs/spec-issue-4-cli.md`
- [x] 交叉检查 spec 与代码实现的一致性
- [x] 在 README 中添加 spec 文档链接

## 验收口径

### 必须成立

- 4 份 spec 文档均存在且路径为 `docs/spec-issue-*.md`
- 每份 spec 包含：目标、范围、数据结构、设计决策、限制、测试覆盖
- spec 中描述的数据结构与代码中实际 dataclass 字段一致
- spec 中描述的 API 端点与 `fetcher.py` 中的实际 URL 一致
- spec 中描述的 CLI 参数与 `cli.py` 中的 argparse 定义一致

### 明确不成立

- spec 不应包含过时的设计（如已被删除的字段）
- spec 不应描述未实现的功能（不超前于代码）

### 失败信号

- 代码变动后 spec 未同步更新（spec rot）
- 新贡献者误以为 spec 是权威源，但 spec 已过时

## Harness / 验证要求

- [x] 人工审查 4 份 spec 与代码一致性
- [x] 确保所有 spec 提到的字段在代码中可找到
- [x] 确保所有 spec 提到的函数签名与代码一致