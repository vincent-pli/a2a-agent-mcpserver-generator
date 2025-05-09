from common.types import AgentCard
from a2a_agent_mcpserver_generator.types import CardParsed
from mcp import types

def parse_card(card: AgentCard) -> CardParsed:
    tools: list[types.Tool] = []
    for skill in card.skills:
        tool = types.Tool(
            name = skill.id + "__" + skill.name,
            description=skill.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "task promot"
                    }
                }
            },
        )
        tools.append(tool)

    
    return CardParsed(
        name=card.name,
        tools=tool
        )






