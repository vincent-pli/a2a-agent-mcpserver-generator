def generate_pyproject(name: str, description: str):
    pyproject_code = f'''
[project]
name = {name}
version = "0.1.0"
description = {description}
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "a2a-sdk",
    "mcp[cli]>=1.8.0",
    "pydantic>=2.11.4",
]

[project.scripts]
a2a-agent-mcpserver-generator = "a2a_agent_mcpserver_generator:main"

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