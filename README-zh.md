# A2A Agent 到 MCP 服务器 🤖
这是一个命令行工具，可以从一行命令的 a2a 代理生成 Model Context Protocol（MCP）服务器代码。这个工具可以帮助你快速创建一个 MCP 服务器，用来作为 LLMs（大语言模型）和 a2a 代理之间的桥梁。
English | [简体中文](./README-zh.md)

## 特性 ✨
- 自动工具生成：将 a2a 代理的每个 `技能` 转换为一个 MCP 工具
- 传输选项：仅支持 stdio，如果要使用 sse 可以借助 mcp-proxy
- 完整的项目设置：生成运行 MCP 服务器所需的所有文件
- 简易配置：生成的服务器采用基于环境的简单配置

## 前置条件
- Python 3.13+
- `uv` (可选，但建议) 或 `pip`

## 环境设置 🔧
首先，你需要启动一个 a2a 代理：
https://github.com/google/a2a-python/tree/main/examples
```
uv run a2a-agent-mcpserver-generator --agent http://0.0.0.0:10000
```
## 安装 📦
```bash
uv pip install a2a-agent-mcpserver-generator
```
## 使用 🚀
```
uv run a2a-agent-mcpserver-generator --help
使用方法：a2a-agent-mcpserver-generator [选项]
选项:
  --agent TEXT
  --output TEXT
  --name TEXT
  --history BOOLEAN
  --use_push_notifications BOOLEAN
  --push_notification_receiver TEXT
  --help                          显示此消息并退出。
```
## E2E 示例
建议使用 [mcpclihost](https://github.com/vincent-pli/mcp-cli-host) 作为 MCP 主机进行尝试。
这个工具(`mcpclihost`)可以同时支持 Azure Openai 和 deepseek
你可以像这样添加生成的 MCP 服务器配置：
```
{
  "mcpServers": {
    "a2a-mcp": {
      "command": "uv",
      "args": [
        "--project",
        "/Users/lipeng/workspaces/github.com/vincent-pli/a2a-agent-mcpserver-generator/a2a-mcp-server",
        "run",
        "a2a-agent-mcpserver"
      ]
    }
  }
}
```
向 `~/.mcp.json`（`mcpclihost` 的默认 MCP 服务器配置路径）添加上述内容，然后试试看。

## 许可协议

这个项目采用 Apache 2.0 许可协议 - 详情请见[LICENSE](LICENSE)文件。