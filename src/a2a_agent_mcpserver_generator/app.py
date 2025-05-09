import asyncio
import urllib.parse
import asyncclick as click
from common.client import A2ACardResolver
from common.types import AgentCard
from a2a_agent_mcpserver_generator.utils import parse_card
from a2a_agent_mcpserver_generator.types import CardParsed
from a2a_agent_mcpserver_generator.server_generator import generate_server_file
from a2a_agent_mcpserver_generator.config_generator import generate_pyproject, generate_env_file
from a2a_agent_mcpserver_generator.dockerfile_generator import generate_docker_files
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from common.utils.push_notification_auth import PushNotificationReceiverAuth
from pathlib import Path



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
    card_resolver = A2ACardResolver(agent)
    card: AgentCard = card_resolver.get_agent_card()

    # Parse agent.json
    card_parsed: CardParsed = parse_card(card)
    if len(card_parsed.tools) == 0:
        print('Warning: No agent tools were generated from the agent card. The spec might not contain valid skills.')

    card_str = card.model_dump_json()
    card_parsed_str = card_parsed.model_dump_json()

    print(f'Info: Creating output directory {output}')
    Path(output).mkdir(exist_ok=True)

    # Generate all the files
    print("Generating server files...")
    server_code = generate_server_file(card_str, card_parsed_str)
    pyproject_code = generate_pyproject(f"mcp-server-{card.name}", card.description)
    env_file = generate_env_file()
    dockerfile, dockerIgnoreFile = generate_docker_files()



    










