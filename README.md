# mcp-config-shape-diff

Compare two JSON snapshots containing `{ "before": { "mcpServers": { ... } }, "after": { "mcpServers": { ... } } }`. Python 3.11+, standard library only.

```console
python mcp_config_shape_diff.py fixtures/example.json
{"servers":[{"server":"added","status":"added"},{"server":"local","status":"changed","command_present_changed":false,"url_present_changed":false,"transport_changed":false,"cwd_present_changed":false,"args_count_before":1,"args_count_after":2,"env_key_count_before":1,"env_key_count_after":2,"env_key_set_changed":true},{"server":"remote","status":"unchanged","command_present_changed":false,"url_present_changed":false,"transport_changed":false,"cwd_present_changed":false,"args_count_before":0,"args_count_after":0,"env_key_count_before":0,"env_key_count_after":0,"env_key_set_changed":false}]
```

Exit codes: 0 no structural differences; 1 additions, removals or structural differences; 2 invalid input or I/O. Use `-` to read stdin. Reads at most 256 KiB, writes at most 32 KiB, rejects duplicate keys and non-finite numbers. The only arbitrary input text in output is server names. It never emits command/URL/path values, arguments, env key names, or values.

This compares shape only. Changed values with the same structure are deliberately not detected. It does not validate a client schema, establish semantic equivalence, or guarantee behavior for any MCP client. Transport uses explicit `type` (`local`/`stdio` or `http`/`sse`) when recognized, otherwise infers from command/url presence.

Missing and empty `args` are both counted as zero; missing and empty `env` are both treated as an empty key set. The report intentionally does not distinguish those cases.

## 中文

本工具比较两个 JSON 快照的结构。要求 Python 3.11+，只用标准库。输入通过 `python mcp_config_shape_diff.py 文件.json` 或 `python mcp_config_shape_diff.py -`（标准输入）。退出码：0 无结构差异；1 有新增、删除或结构差异；2 输入或 I/O 错误。仅服务器名称会作为输入文本出现在结果中，不输出命令、URL、路径、参数、环境变量名或值。

它只比较结构；结构相同但值改变时不会检测。它不验证客户端 schema、不判断语义等价，也不保证任何 MCP 客户端行为。transport 优先采用明确且已识别的 `type`，否则根据 command/url 是否存在推断。缺失与空 `args` 都计为 0；缺失与空 `env` 都按空键集合处理，报告不区分这两种情况。

## Sources

- [VS Code issue #340161](https://github.com/microsoft/vscode/issues/340161): documents migration gaps and differing environment interpolation contexts; supports treating cwd/env as client-dependent structural facts.
- [OpenCode issue #30677](https://github.com/anomalyco/opencode/issues/30677): requested per-server cwd for local MCP configuration; issue closed by PR #30676 on 2026-06-11.
- [Copilot SDK MCP documentation](https://github.com/microsoft/copilot-sdk/blob/main/docs/features/mcp.md): documents local command/args/env and remote URL examples, as well as local/stdio and HTTP/SSE categories.

## License

MIT, Copyright (c) 2026 maomao-1937.
