def generate_server_file(card_str: str, card_parsed_str: str):
        server_code = f'''
from dotenv import load_dotenv
from pydantic import BaseModel
import os
import httpx
import urllib
from mcp.server.lowlevel import NotificationOptions, Server
from mcp import types
from uuid import uuid4
import mcp.server.stdio
from mcp.server.models import InitializationOptions
from a2a.types import (
    AgentCard,
    SendMessageResponse,
    GetTaskResponse,
    SendMessageSuccessResponse,
    Task,
    TaskState,
    SendMessageRequest,
    MessageSendParams,
    GetTaskRequest,
    TaskQueryParams,
    SendStreamingMessageRequest,
    JSONRPCErrorResponse,
    Message,
    SendStreamingMessageResponse,
    TaskStatusUpdateEvent,
    TaskArtifactUpdateEvent,
    Artifact,
)
from a2a.client import A2AClient
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from typing import Any
import asyncio


load_dotenv()
CARD = '{card_str}'
CARD_PARSED = '{card_parsed_str}'

class CardParsed(BaseModel):
    name: str
    tools: list[types.Tool]

def create_send_message_payload(
    text: str, task_id: str | None = None, context_id: str | None = None
) -> dict[str, Any]:
    """Helper function to create the payload for sending a task."""
    payload: dict[str, Any] = {{
        'message': {{
            'role': 'user',
            'parts': [{{'type': 'text', 'text': text}}],
            'messageId': uuid4().hex,
        }},
    }}

    if task_id:
        payload['message']['taskId'] = task_id

    if context_id:
        payload['message']['contextId'] = context_id
    return payload

def merge_artifact(original: Artifact, new_comming: Artifact) -> Artifact:
    assert original.artifactId == new_comming.artifactId
    original.parts.extend(new_comming.parts)
    return original

class MCPRuntime:
    def __init__(self) -> None:
        self.card = AgentCard.model_validate_json(CARD)
        self.card_parsed = CardParsed.model_validate_json(CARD_PARSED)
        self.server: Server = None
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
        # TODO Auth maybe

        try:
            yield {{"client": "fake"}}
        finally:
            pass


runtime = MCPRuntime()
server = Server("a2a-mcp-server", lifespan=ServerLifespan(runtime=runtime))

@server.list_tools()
async def handle_list_tool() -> list[types.Tool]:
    return runtime.card_parsed.tools

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    prompt = arguments["prompt"]
    ctx = server.request_context
    async with httpx.AsyncClient() as httpx_client:
        client = await A2AClient.get_client_from_agent_card_url(
            httpx_client, runtime.card.url
        )   

        task_id = uuid4().hex
        context_id = uuid4().hex
        message = create_send_message_payload(text=prompt, task_id=task_id, context_id=context_id)
        
        res: Artifact | Message = None
        if runtime.card.capabilities.streaming:
            request = SendStreamingMessageRequest(
                params=MessageSendParams(**message)
            )        
            stream_response: SendStreamingMessageResponse = client.send_message_streaming(request)
            
            task_status: TaskStatusUpdateEvent = None
            async for chunk in stream_response:
                if isinstance(chunk.root, JSONRPCErrorResponse):
                    return [types.TextContent(
                        type='text',
                        text=chunk.root.model_dump_json(exclude_none=True)
                    )]

                if isinstance(chunk.root.result, TaskStatusUpdateEvent):
                    task_status = chunk.root.result
                    notification_msg = ''.join(part.root.text for part in task_status.status.message.parts) if task_status.status.message else ""
                    await ctx.session.send_log_message(
                        level="info",
                        data=f"Task: {{task_id}} is '{{task_status.status.state}}' with message: {{notification_msg}}",
                        logger="notification_stream",
                        related_request_id=ctx.request_id,
                    )
                    if task_status.status.state == TaskState.input_required:
                        res = task_status.status.message

                if isinstance(chunk.root.result, TaskArtifactUpdateEvent):
                    event = chunk.root.result
                    if not event.append:
                        res = event.artifact
                    else:
                        res = merge_artifact(res, event.artifact)
                
        else:
            request = SendMessageRequest(
                params=MessageSendParams(**message)
            )
            response: SendMessageResponse = await client.send_message(request)
            if isinstance(response.root, JSONRPCErrorResponse):
                return [types.TextContent(
                    type='text',
                    text=response.root.model_dump_json(exclude_none=True)
                )]
            
            if isinstance(response.root, SendMessageSuccessResponse):
                if isinstance(response.root.result, Message):
                    res = response.root.result
                
                if isinstance(response.root.result, Task):
                    task: Task = response.root.result
                    while task.status.state != TaskState.completed:
                        get_request = GetTaskRequest(params=TaskQueryParams(id=task.id))
                        get_response: GetTaskResponse = await client.get_task(get_request)
                        if isinstance(get_response.root, JSONRPCErrorResponse):
                            return [types.TextContent(
                                type='text',
                                text=get_response.root.model_dump_json(exclude_none=True)
                            )]
                        
                        task = get_response.root.result
                        notification_msg = ''.join(part.root.text for part in task_status.status.message.parts) if task_status.status.message else ""
                        await ctx.session.send_log_message(
                            level="info",
                            data=f"Task: {{task_id}} is '{{task_status.status.state}}' with message: {{notification_msg}}",
                            logger="notification_stream",
                            related_request_id=ctx.request_id,
                        )
                        await asyncio.sleep(1)

                    res = task.status.message

    result_text = "".join(part.root.text for part in res.parts)
    return [types.TextContent(
        type='text',
        text=result_text
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
                    experimental_capabilities={{}},
                ),
            ),
        )

def start():
    asyncio.run(run())

if __name__ == '__main__':
    asyncio.run(run())

'''
        return server_code