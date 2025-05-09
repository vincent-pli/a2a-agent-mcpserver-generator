def generate_server_file(card_str: str, card_parsed_str: str):
        server_code = f'''

from common.types import AgentCard
from a2a_agent_mcpserver_generator.types import CardParsed
from dotenv import load_dotenv
import os
import urllib
from common.client import A2AClient
from common.types import SendTaskResponse
from mcp.server.lowlevel import NotificationOptions, Server
from mcp import types
from uuid import uuid4
import mcp.server.stdio
from mcp.server.models import InitializationOptions


load_dotenv()
CARD = {card_str}
CARD_PARSED = {card_parsed_str}

class MCPRuntime:
    def __init__(self) -> None:
        self.card = AgentCard.model_validate_json(CARD)
        self.card_parsed = CardParsed.model_validate_json(CARD_PARSED)
        self.server = None
        self.is_debug = False
        self.is_connectd = False
        if self.card.capabilities.pushNotifications:    
            push_notification_receiver = os.getenv("PUSH_NOTIFICATION_RECEIVER")
            notif_receiver_parsed = urllib.parse.urlparse(push_notification_receiver)
            self.notification_receiver_host = notif_receiver_parsed.hostname
            self.notification_receiver_port = notif_receiver_parsed.port


class ServerLifespan:
    def __init__(self, runtime: MCPRuntime):
        self.runtime = runtime
    
    def __call__(
        self, 
        server: Server
    ) -> AsyncIterator[dict]:
        return self._lifespan_context(server)
    
    @asynccontextmanager
    async def _lifespan_context(
        self, 
        server: Server
    ) -> AsyncIterator[dict]:
        """Manage server startup and shutdown lifecycle."""
        # Initialize resources on startup
        # Notification server 
        # TODO, need send notification to client when get the notification from remote agent
        if self.runtime.card.capabilities.pushNotifications:
            from hosts.cli.push_notification_listener import (
                PushNotificationListener,
            )

            notification_receiver_auth = PushNotificationReceiverAuth()
            await notification_receiver_auth.load_jwks(
                f'{{self.runtime.card.url}}/.well-known/jwks.json'
            )

            push_notification_listener = PushNotificationListener(
                host=self.runtime.notification_receiver_host,
                port=self.runtime.notification_receiver_port,
                notification_receiver_auth=notification_receiver_auth,
            )
            push_notification_listener.start()

        # Client
        client = A2AClient(agent_card=self.runtime.card)
        # Auth maybe TODO
        try:
            yield {{"client": client}}
        finally:
            pass


runtime = MCPRuntime()
server = Server("example-server", lifespan=ServerLifespan(runtime=runtime))

@server.list_tools()
async def handle_list_tool() -> list[types.Tool]:
    return runtime.card_parsed.tools

@server.call_tool()
async def handle_call_tool(prompt: str) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    ctx = server.request_context
    client: A2AClient = ctx.lifespan_context["client"]
    taskId = uuid4().hex
    sessionId = uuid4().hex

    message = {{
        'role': 'user',
        'parts': [
            {{
                'type': 'text',
                'text': prompt,
            }}
        ],
    }}
    payload = {{
        'id': taskId,
        'sessionId': sessionId,
        'acceptedOutputModes': ['text'],
        'message': message,
    }}

    if runtime.card.capabilities.pushNotifications:
        payload['pushNotification'] = {{
            'url': f'http://{{runtime.notification_receiver_host}}:{{runtime.notification_receiver_port}}/notify',
            'authentication': {{
                'schemes': ['bearer'],å
            }},
        }}
    
    # donot consider stream not, maybe later TODO
    if runtime.card.capabilities.streaming:
        pass
    taskResult: SendTaskResponse = await client.send_task(payload)

    return [types.TextContent(
        type='text',
        text=taskResult.model_dump_json(exclude_none=True)
    )]

@server.set_logging_level()
async def set_logging_level(level: types.LoggingLevel):
    if level == "debug":
        runtime.is_debug = True
        

async def run():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=runtime.card_parsed.name,
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={{å}},
                ),
            ),
        )

if __name__ == '__main__':
    asyncio.run(run())

'''
        return server_code