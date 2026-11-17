# 研究记录

- [VS Code issue #340161](https://github.com/microsoft/vscode/issues/340161) 记录配置迁移限制，以及不同上下文对环境变量引用的处理差异。这说明 cwd/env 结构值得关注，但不构成通用客户端规则。
- [OpenCode issue #30677](https://github.com/anomalyco/opencode/issues/30677) 请求为本地 MCP 配置增加可选 cwd；issue 活动记录显示该需求由 PR #30676 于 2026-06-11 完成。
- [Copilot SDK MCP 文档](https://github.com/microsoft/copilot-sdk/blob/main/docs/features/mcp.md) 展示本地 command/args/env 与远端 url 示例，并区分 local/stdio 和 HTTP/SSE。

这些资料用于说明诊断动机，不证明本工具档案适用于所有客户端。工具仅比较有限结构事实，不启动服务器、不读取环境变量、不展开变量，也不输出配置值。它不做 schema 校验或语义等价判断。
