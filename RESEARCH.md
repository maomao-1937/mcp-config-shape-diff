# Research / 研究记录

## English

Question: can a small offline tool help review MCP configuration migrations without exposing configuration values? Public reports indicate launch context and interpolation can differ among clients. VS Code issue #340161 describes migration handling and client-specific environment lookup behavior. OpenCode issue #30677 requests an optional `cwd` on local server config; the issue records closure through PR #30676. Copilot SDK documentation shows local `command`, `args`, `env` and remote `url` examples, and distinguishes local/stdio from HTTP/SSE.

The tool therefore reports presence/count/set facts, not values. Its transport category is a deliberately narrow normalization, not an MCP-wide schema. These sources motivate the diagnostic; they do not prove this profile is accepted by every client.

## 中文

问题：能否在不暴露配置值的情况下，帮助审查 MCP 配置迁移？公开问题显示启动上下文和变量插值可能因客户端而异。VS Code #340161 记录迁移处理和客户端各自的环境变量查找行为；OpenCode #30677 请求为本地服务器配置增加可选 cwd，记录通过 PR #30676 关闭；Copilot SDK 文档示例列出本地 `command`、`args`、`env` 及远端 `url`，并区分 local/stdio 与 HTTP/SSE。

因此工具只报告存在性、数量和键集合是否变化，不报告值。transport 是有限归一化，不代表 MCP 全局 schema。资料仅说明设计动机，不证明所有客户端都接受此输入档案。
