# A2A Agent to MCP server 🤖

A command-line tool that generates Model Context Protocol (MCP) server code from a oneline a2a agent. This tool helps you quickly create an MCP server that acts as a bridge between LLMs (Large Language Models) and the a2a agent.

English | [简体中文](./README-zh.md)

## Features ✨

- Automatic Tool Generation: Converts each `skills` of the a2a agent into an MCP tool
- Transport Options: Only supports stdio, for sse you can leveral mcp-proxy
- Complete Project Setup: Generates all necessary files to run an MCP server
- Easy Configuration: Simple environment-based configuration for the generated server

## Prerequisites

- Python 3.13+
- `uv` (optional, but recommended) or `pip`

## Environment Setup 🔧
Firstly, you need to start up a a2a agent:
https://github.com/google/a2a-python/tree/main/examples

```
uv run a2a-agent-mcpserver-generator --agent http://0.0.0.0:10000
```

## Installation 📦

```bash
uv pip install a2a-agent-mcpserver-generator
```

## Usage 🚀
```
uv run a2a-agent-mcpserver-generator --help
Usage: a2a-agent-mcpserver-generator [OPTIONS]

Options:
  --agent TEXT
  --output TEXT
  --name TEXT
  --history BOOLEAN
  --use_push_notifications BOOLEAN
  --push_notification_receiver TEXT
  --help                          Show this message and exit.
```

## E2E example

Suggest use [mcpclihost](https://github.com/vincent-pli/mcp-cli-host) as MCP host to take a try.
This tool(`mcpclihost`) could support both Azure Openai and deepseek

You can add generated MCP server congiguration like this:
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
to the `~/.mcp.json`(default mcp server configuration path of `mcpclihost`), then take a try


## License 📄

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.
