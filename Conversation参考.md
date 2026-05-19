## 关联事项

Closes / Relates to #52

## 背景与问题

当前 `apps/web` 已完成基础应用壳、一级路由、`MainLayout` 和多个占位页面。Events、Runtime、Approvals、Plugins、Settings、Skills、Tools、Industries 等页面仍主要通过 `PlaceholderPanel` 表达页面内容。

后续页面会逐步接入 API Client、TanStack Query、列表、筛选和详情入口。如果页面级 loading / empty 状态继续由各 route 分散实现，容易出现以下问题：

- loading / empty 的布局、文案层级和 CTA 行为不一致
- 可访问性语义缺失或实现分叉
- 后续真实数据接入时，每个页面重复处理空态和加载态
- `PlaceholderPanel` 被误用为页面状态组件，职责边界变模糊

因此，本 PR 先为页面级 Loading / Empty 状态建立 OpenSpec 真源，后续在同一 PR 中追加实现。

## 当前提交范围

本次提交仅包含 OpenSpec change，不包含 Web 实现代码。

新增 change：

- `openspec/changes/web-page-status-components/proposal.md`
- `openspec/changes/web-page-status-components/design.md`
- `openspec/changes/web-page-status-components/tasks.md`
- `openspec/changes/web-page-status-components/specs/web-page-status-components/spec.md`

该 change 固定以下决策：

- 组件命名为 `PageLoading` / `PageEmpty`
- 组件放在 `apps/web/src/app/components/`
- 样式补充到 `apps/web/src/styles/pages.css`
- Events 页面作为首个验证点
- 使用 `/events?state=loading|empty` 提供受控预览
- `PageLoading` 需要具备明确的可访问 loading 语义
- `PageEmpty` 支持标题、说明和可选 CTA
- 无效 `state` 查询参数回退到现有 Events overview
- 不接入真实 API、Query hooks、WebSocket、contracts 或 mock 数据层

## 后续将在本 PR 追加

后续实现提交将覆盖：

- 新增 `PageLoading`
- 新增 `PageEmpty`
- 补充页面级状态样式
- 在 Events 页面接入 loading / empty 预览
- 确认其他占位页面行为不变
- 运行 Web lint / build 验证

## 明确非目标

本 PR 不处理：

- 真实 Event Inbox
- API Client / TanStack Query 接入
- WebSocket 或 contracts 生成类型
- error / forbidden / retry / permission 状态
- 表格、筛选、分页或详情入口
- 所有页面迁移
- 新增测试基础设施
- 新 UI 库或视觉重绘

## 验证

当前阶段已验证：

- [x] `openspec validate web-page-status-components --type change --strict --json`

实现阶段待验证：

- [ ] `cd apps/web && bun run lint`
- [ ] `cd apps/web && bun run build`
- [ ] 手动验证 `/events`
- [ ] 手动验证 `/events?state=loading`
- [ ] 手动验证 `/events?state=empty`
- [ ] 手动验证 `/events?state=unknown`
- [ ] 确认 Runtime、Approvals、Plugins、Settings、Skills、Tools、Industries 页面行为不变

## 风险与控制

- 当前提交只建立 OpenSpec 真源，尚未交付用户可见功能。
- 查询参数预览会在后续实现中进入页面行为，但它只表达 UI 预览状态，不作为业务状态真源。
- `PageEmpty` 的 CTA 由调用方传入，组件只负责布局，不承载业务动作。
- `PageLoading` 只覆盖页面级或主内容区 loading，不覆盖表格行、按钮、卡片等局部 skeleton。
- 如本地依赖缺失导致 Web build 无法运行，后续实现提交会在 PR 中记录具体未验证原因。

## Review 重点

请重点 review：

- OpenSpec 是否准确收住 #52 的范围
- `PageLoading` / `PageEmpty` 的边界是否足够清晰
- Events 查询参数预览是否适合作为首个验证方式
- 非目标是否排除了真实数据接入和 UI 过度扩张
- 后续实现任务是否足够可执行
