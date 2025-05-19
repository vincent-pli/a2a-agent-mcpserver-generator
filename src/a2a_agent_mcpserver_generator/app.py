import asyncio
import urllib.parse
import asyncclick as click
from a2a_agent_mcpserver_generator.utils import parse_card
from a2a_agent_mcpserver_generator.types import CardParsed
from a2a_agent_mcpserver_generator.server_generator import generate_server_file
from a2a_agent_mcpserver_generator.config_generator import generate_pyproject, generate_env_file
from a2a_agent_mcpserver_generator.dockerfile_generator import generate_docker_files
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from pathlib import Path
from dotenv import load_dotenv
import os
from a2a.client import A2ACardResolver
from a2a.types import AgentCard
import httpx


load_dotenv()

@click.command()
@click.option('--agent', default='http://localhost:10000')
@click.option('--output', default='./mcp-server')
@click.option('--name', default='a2a-agent-mcp-server')
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
    # Load agent.json
    async with httpx.AsyncClient() as httpx_client:
        card_resolver = A2ACardResolver(httpx_client=httpx_client, base_url=agent)
        card: AgentCard = await card_resolver.get_agent_card()

    # Parse agent.json
    card_parsed: CardParsed = parse_card(card)
    if len(card_parsed.tools) == 0:
        print('Warning: No agent tools were generated from the agent card. The spec might not contain valid skills.')

    card_str = card.model_dump_json(exclude_none=True)
    card_parsed_str = card_parsed.model_dump_json(exclude_none=True)
    notification_receiver_port = None
    if card.capabilities.pushNotifications:    
        push_notification_receiver = os.getenv("PUSH_NOTIFICATION_RECEIVER")
        notif_receiver_parsed = urllib.parse.urlparse(push_notification_receiver)
        notification_receiver_port = notif_receiver_parsed.port

    print(f'Info: Creating output directory {output}')
    Path(output).mkdir(exist_ok=True)

    # Generate all the files
    print("Generating server files...")
    server_code = generate_server_file(card_str, card_parsed_str)
    pyproject_code = generate_pyproject(f"mcp-server-{card.name}", card.description)
    env_file = generate_env_file()
    dockerfile = generate_docker_files(notification_receiver_port)

    sourcecode = {
        Path(output)/"server.py": server_code,
        Path(output)/"pyproject.toml": pyproject_code,
        Path(output)/".env.example": env_file,
        Path(output)/"Dockerfile": dockerfile
    }

    for file_path, content in sourcecode.items():
        with open(file_path, 'w') as f:
            f.write(content)


    print("Compelte!")


def run():
    asyncio.run(main())

if __name__ == '__main__':
    asyncio.run(main())

    










