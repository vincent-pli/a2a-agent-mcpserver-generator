from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    field_serializer,
    model_validator,
)

from mcp import types


class CardParsed(BaseModel):
    name: str
    tools: list[types.Tool]
    
