## 背景 / 为什么现在做

`apps/api` 当前已经完成 FastAPI app 外壳、统一 `code/data/msg/error` 响应、全局异常处理、`X-Request-ID` 和 `/health` 基础入口；仓库里也已经拆出若干后端基建 issue，包括 #27 DB/Alembic 骨架、#28 本地 db/env、#38 健康/就绪检查、#39 事件只读 API、#40 插件配置 API、#41 审批授权 API、#42 运行时可观测 API、#43 Native WebSocket。

这些 issue 多数是单资源或单通道骨架，且很多明确“不接入真实存储/业务流程”。如果不在当前阶段收住 `apps/api` 的基建汇合边界，后续容易出现三个漂移：

- REST 资源、WebSocket 通知、审计和持久化各自定义 envelope / id / cursor / error 语义。
- API 直接长出业务逻辑或私有 DB 访问，破坏 `apps/api -> packages/quant/core` 的边界。
- 前端契约、OpenAPI、测试 fixture 和后续 worker/scheduler 接入点互相等待，导致每个 endpoint issue 都重复补基础设施。

本 issue 用来把 `apps/api` 当前基建方向收敛成一条可执行的后端基线，不替代 #39-#43 的具体 endpoint 开发。

## 当前想收住的不确定性

`apps/api` 在 0 到 1 阶段应如何从“HTTP 外壳”过渡为“统一 API 基建层”：既能承接 REST 快照、Native WebSocket 通知、core persistence/repository、审计/错误/请求追踪和契约生成，又不把核心领域逻辑塞进 FastAPI app。

## 本 issue 想解决什么

- 明确 `apps/api` 与 `packages/quant/core` 的依赖边界：API 只组合 DTO、route、service port 和 response，不定义 ORM model、不拥有 migration、不直接实现事件/插件/审批领域状态机。
- 建立 API 基建汇合清单：统一 pagination/cursor、resource id、request/correlation/causation id、错误码、Not Implemented、mask/secret reference、OpenAPI schema 输出和测试 fixture 约定。
- 给 #39-#43 这些资源骨架 issue 定义共同接入面：路由注册、DTO 组织、mock/sample provider、未来 repository adapter 注入、WebSocket topic envelope 与 REST refresh 的关系。
- 确定 API 测试 harness 的最低基线：FastAPI route tests、schema/envelope tests、敏感字段不泄露 tests、WebSocket mock broadcast tests、未来 DB 接入时的 migration/repository smoke tests。
- 输出一个短设计记录或开发规范入口，放在仓库合适位置，供后续后端 issue 引用，避免每个 issue 重复解释边界。

## 明确不解决什么

- 不实现 #39-#43 中任何具体 endpoint 的业务字段全集或真实数据接入。
- 不创建业务表，不实现 `events`、`plugins`、`approvals`、`audit_logs` 的字段级 DDL。
- 不实现 worker、scheduler、Event Bus、AgentRuntime 或真实插件 registry。
- 不实现真实交易、真实 executor、生产级鉴权、多租户权限或 Policy Gate 放行逻辑。
- 不引入 Socket.IO、消息持久化回放、Redis Streams 或生产 outbox。

## 当前已知上下文

- `README.md`：明确 `apps/api` 是 FastAPI API 入口，`packages/quant/core` 承载共享配置、数据库、错误和领域基础能力。
- `docs/README.md`：设计真相来源在 `docs/design/`。
- `docs/design/01-tech-stack-and-project-structure.md`：`apps/api` 负责 HTTP/WebSocket/管理接口，复杂业务逻辑应调用 core/agent，不直接实现。
- `docs/design/02-core-architecture-and-runtime.md`：Event、EventEnvelope、topic、Decision/Policy Gate、Persistence/Audit 是主链路基础。
- `docs/design/04-database-and-persistence-design.md`：PostgreSQL、SQLAlchemy 2.x、Alembic 位于 core 边界；API DTO 不复用 ORM model；插件不直接持有 DB session。
- `docs/design/08-api-and-websocket-design.md`：REST 是状态真源访问入口，WebSocket 只做通知；统一响应 envelope；敏感信息不得明文返回。
- `apps/api/src/quantagent/api/`：已有 `main.py`、`responses.py`、`middleware.py`、`exceptions.py`、`routers/health.py`、`routers/debug.py` 和基础测试。
- 相关 issues：#27、#28、#38、#39、#40、#41、#42、#43。

## 前置依赖

不阻塞，可以先推进为 review-needed 的基建收敛 issue。

实现时需要关注 #27 是否已落地：如果 core DB/Alembic package 尚未实现，本 issue 只能定义 API 到 core 的 provider/port 边界和测试替身，不能要求真实 repository 或 migration 通过。

## 需要先讨论或确认的问题

- 是否采用 `apps/api` 内部 `services/` + `schemas/` + `routers/` 的三层组织，还是提前把 DTO/ports 下沉到 `packages/quant/core` 或 `packages/contracts`？
- `trace_id`、`correlation_id`、`causation_id` 的生成责任在 API middleware、core runtime，还是由上游调用方传入并校验？
- OpenAPI 输出文件是否在本阶段纳入 CI/脚本，还是先仅保证 FastAPI runtime schema 正确？
- API 基建文档应放在 `docs/design/`、`docs/openspec/changes/`，还是 repo 根的开发规范入口中？
- 对 #39-#43 的 mock/sample data，是否统一用 fixture provider，还是各 router 暂时自带样例？

## 子任务树

- 梳理 `apps/api` 现状与 #27/#38-#43 的重叠边界，形成一页后端 API 基建方向说明。
- 定义 API 共享约定：envelope、pagination/cursor、request id、trace/correlation/causation id、错误码、Not Implemented、敏感字段 mask 和 secret reference。
- 定义 route/DTO/service/provider 的目录与依赖规则，明确 API 不直接拥有 ORM model、migration、领域状态机和插件 runtime。
- 定义 mock/sample provider 与未来 repository adapter 的替换点，让 #39-#43 可以先返回稳定形状，后续再接 core persistence。
- 定义 REST 快照与 WebSocket topic envelope 的配合规则：WebSocket 只通知，页面状态恢复必须走 REST refresh，`seq/cursor` 只预留不承诺持久回放。
- 补充最小验证清单，覆盖 route envelope、validation error、OpenAPI schema、敏感字段不泄露、WebSocket topic mock、生产环境禁用 debug/test-only 入口。

## 验收口径

### 必须成立

- 有一个可被后续后端 issue 引用的 API 基建说明或开发规范入口，明确 `apps/api`、`packages/quant/core`、`packages/contracts` 的职责边界。
- #39-#43 可以按该说明实现，不需要各自重新决定 pagination、DTO 组织、错误结构、mock provider、id/cursor/envelope 语义。
- 说明中明确 API DTO 与 ORM model 解耦，API 不拥有 migration，真实存储通过 core 提供的 repository/storage port 接入。
- 说明中明确 WebSocket 不作为业务状态真源，断线/初始化状态恢复必须通过 REST snapshot。
- 验证要求不依赖真实交易、真实凭证、生产数据库或外部网络服务。

### 明确不成立

- 不声称后端业务闭环已经完成。
- 不声称事件、插件、审批、可观测、WebSocket endpoint 已全部实现。
- 不声称数据库 schema、repository、audit log 或 Event Bus 已经可用于生产。
- 不声称 Policy Gate、真实 executor 或 live trading 已接入。

### 失败信号

- 后续 endpoint issue 仍然各自定义 response、pagination、id、错误码或 mock 数据组织方式。
- `apps/api` 直接新增 ORM model、migration 或核心领域状态机。
- WebSocket 被实现成页面状态真源，REST snapshot 变成可选项。
- 敏感字段、prompt、secret 或私有策略在 API/日志/test fixture 中明文出现。

## Harness / 验证要求

- FastAPI route tests：继续使用 `TestClient` 验证统一 envelope、request id、validation error 和 production/debug 行为。
- Schema tests：至少验证 OpenAPI 中新增资源 DTO 不直接暴露 ORM/internal-only 字段。
- Security/safety tests：针对插件配置、审批 payload 或错误详情，验证 secret/masked 字段不会明文泄露。
- WebSocket tests：仅使用 mock broadcast 验证 topic subscribe/notification envelope，不要求持久化 replay。
- Persistence 接入前只做 import/provider smoke；#27 落地后再增加 migration/repository smoke，不在本 issue 强制真实 PostgreSQL 通过。
