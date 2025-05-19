# from common.types import AgentCard
from a2a.types import AgentCard
from a2a_agent_mcpserver_generator.types import CardParsed
from mcp import types


def parse_card(card: AgentCard) -> CardParsed:
    tools: list[types.Tool] = []
    for skill in card.skills:
        tool = types.Tool(
            name = skill.id,
            description=skill.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The complete task description"
                    }
                }
            },
        )
        tools.append(tool)

    
    return CardParsed(
        name=card.name,
        tools=tools
        )






