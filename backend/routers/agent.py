"""Agent Router — LLM-as-MCP-host chat endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel

from services.mcp_agent import run_agent

router = APIRouter()


class AgentChatRequest(BaseModel):
    message: str


@router.post("/agent/chat")
async def agent_chat(req: AgentChatRequest):
    """Run the MCP AI agent: LLM decides which tools to call, executes them via
    the InternIQ MCP server, and returns a synthesized natural-language answer."""
    return await run_agent(req.message.strip())
