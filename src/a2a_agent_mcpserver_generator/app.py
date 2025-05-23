import asyncio
import urllib.parse
import asyncclick as click
from a2a_agent_mcpserver_generator.utils import parse_card, generate_server_conf
from a2a_agent_mcpserver_generator.types import CardParsed
from a2a_agent_mcpserver_generator.server_generator import generate_server_file
from a2a_agent_mcpserver_generator.config_generator import generate_pyproject, generate_env_file, generate_README
from a2a_agent_mcpserver_generator.dockerfile_generator import generate_docker_files
from pathlib import Path
from dotenv import load_dotenv
import os
import logging
from a2a.client import A2ACardResolver
from a2a.types import AgentCard
import httpx
import json


log = logging.getLogger("a2a_agent_mcpserver_generator")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
load_dotenv()

@click.command()
@click.option('--agent', default='http://localhost:10000')
@click.option('--output', default='./a2a-mcp-server')
@click.option('--name', default='a2a-agent-mcpserver')
@click.option('--history', default=False)
@click.option('--use_push_notifications', default=False)
@click.option('--push_notification_receiver', default='http://localhost:5000')
async def main(
    agent,
    output,
    name,
    history,
    use_push_notifications: bool,
    push_notification_receiver: str,
) -> None:
    log.info('🚀 A2A agent to MCP Server Generator')
    log.info('Configuration:')
    log.info(f'- Agent address: {agent}')
    log.info(f'- Output Directory: {output}')
    log.info(f'- Server Name: {name}')

    # Load agent.json
    try:
        async with httpx.AsyncClient() as httpx_client:
            card_resolver = A2ACardResolver(httpx_client=httpx_client, base_url=agent)
            card: AgentCard = await card_resolver.get_agent_card()
    except Exception as e:
        log.error(f"failed to get agent card from address: {agent}")
        log.error(e)
        return

    # Parse agent.json
    card_parsed: CardParsed = parse_card(card)
    if len(card_parsed.tools) == 0:
        log.error('No tools were generated from the agent card. The capabilities might not contain valid skills.')
        return

    card_str = card.model_dump_json(exclude_none=True)
    card_parsed_str = card_parsed.model_dump_json(exclude_none=True)
    notification_receiver_port = None
    if card.capabilities.pushNotifications:    
        push_notification_receiver = os.getenv("PUSH_NOTIFICATION_RECEIVER")
        notif_receiver_parsed = urllib.parse.urlparse(push_notification_receiver)
        notification_receiver_port = notif_receiver_parsed.port

    log.info(f'Creating output directory {output}')
    Path(output).mkdir(exist_ok=True)

    # Generate all the files
    log.info("Generating server files...")
    server_code = generate_server_file(card_str, card_parsed_str)
    pyproject_code = generate_pyproject(f"mcp-server-{card.name}", card.description)
    env_file = generate_env_file()
    dockerfile = generate_docker_files(notification_receiver_port)
    readme_file = generate_README()
    init_file = " "
    absolute_path = os.path.abspath(output)
    client_conf = { "mcpServers": { name: generate_server_conf(absolute_path) } }

    sourcecode = {
        Path(output)/"src/a2a_mcp_server/server.py": server_code,
        Path(output)/"pyproject.toml": pyproject_code,
        Path(output)/".env.example": env_file,
        Path(output)/"Dockerfile": dockerfile,
        Path(output)/"README.md": readme_file,
        Path(output)/"src/a2a_mcp_server/__init__.py": init_file
    }

    log.info("Writing files to output directory...")
    for file_path, content in sourcecode.items():
        dir_path = os.path.dirname(file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        with open(file_path, 'w') as f:
            f.write(content)

    log.info(f'✅ MCP server generated successfully in "{output}"')
    log.info(f'📚 Generated {len(card_parsed.tools)} tools from agent')
    log.info('Next steps:')
    log.info('🟢 Local run:')
    log.info(f'1. cd {output}')
    log.info('2. cp .env.example .env (and edit with your params)')
    log.info('3. uv run .')
    log.info('4. Config the mcp client:')
    log.info(f'   To add the MCP server manually, add the following config to your MCP config-file:\n {json.dumps(client_conf, indent=2)}')


    log.info("Compelte!")



def run():
    asyncio.run(main())

if __name__ == '__main__':
    asyncio.run(main())

    










