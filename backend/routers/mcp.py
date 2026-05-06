"""MCP Router - InternIQ MCP demonstration endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

from services.mcp_bridge import run_interniq_mcp_demo

router = APIRouter()


class McpDemoRequest(BaseModel):
    listing_id: int
    cv_text: str = ""


@router.post("/mcp/demo")
async def run_mcp_demo(req: McpDemoRequest):
    """Run the InternIQ MCP stdio demo flow for a selected listing."""
    return await run_interniq_mcp_demo(req.listing_id, req.cv_text)
