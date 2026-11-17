# 使用说明

`mcp-config-shape-diff` 比较两个 MCP 配置 JSON 快照的结构事实，不输出配置值。需要 Python 3.11+，无需第三方依赖。

## 输入与运行

顶层必须且只能含 `before`、`after` 两键，每侧必须且只能含 `mcpServers`：

```json
{"before":{"mcpServers":{"local":{"command":"node","args":["server.js"]}}},"after":{"mcpServers":{"local":{"command":"node","args":["server.js","--safe"]}}}}
```

```console
python mcp_config_shape_diff.py fixtures/example.json
python mcp_config_shape_diff.py - < snapshot.json
```

退出码：`0` 无结构差异；`1` 有新增、删除或结构差异；`2` 输入无效或 I/O 错误。输入上限 256 KiB，输出上限 32 KiB。拒绝重复键、非有限数、非 UTF-8、超限内容及网络/设备路径。错误仅输出固定 `E_INPUT`。

按服务器名排序报告新增、删除或共有服务器的结构差异：command/url/cwd 存在性、transport 类别、args 数量、env 键数量及键集合是否变化。配置值不会回显，唯一可回显的输入文本是服务器名。transport 精确归一化 `local`/`stdio` 为 `stdio`，`http`/`sse` 为 `remote`；否则根据 command/url 存在性推断，无法判断时为 `unknown`。缺失与空 args 均计为零；缺失与空 env 均视为空键集合，不予区分。

## 边界

结构相同但值改变时不会检测。本工具不验证客户端 schema、不判断语义等价，也不保证任何 MCP 客户端的接受或运行行为。
