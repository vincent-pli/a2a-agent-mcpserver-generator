def generate_pyproject(name: str, description: str):
    pyproject_code = f'''
[project]
name = "a2a-mcp-server"
version = "0.1.0"
description = "{description}"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "a2a-sdk",
    "mcp[cli]>=1.8.0",
    "pydantic>=2.11.4",
]

[project.scripts]
a2a-agent-mcpserver-generator = "a2a_mcp_server.server:start"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv.sources]
a2a-sdk = {{ git = "https://github.com/google/a2a-python" }}

'''
    return pyproject_code


def generate_env_file():
    env_file_content = '''
PUSH_NOTIFICATION_RECEIVER=http://localhost:5000
# TODO add auth stuff here
'''
    return env_file_content

def generate_README():
    readme_file_content = '''
# A2A agents mcpserver generator

Generate MCP server based in the A2A agent
'''
    return readme_file_content