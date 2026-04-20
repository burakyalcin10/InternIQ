"""Helpers for optional LangSmith tracing."""

from __future__ import annotations

import os
from contextlib import nullcontext
from typing import Any

import langsmith as ls


def _is_truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def is_langsmith_enabled() -> bool:
    """Return True when tracing is configured and explicitly enabled."""
    tracing_enabled = (
        _is_truthy(os.getenv("LANGSMITH_TRACING"))
        or _is_truthy(os.getenv("LANGCHAIN_TRACING_V2"))
    )
    api_key = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")
    return tracing_enabled and bool(api_key)


def get_langsmith_project(default: str = "InternIQ") -> str:
    """Resolve the LangSmith project name from env vars."""
    return (
        os.getenv("LANGSMITH_PROJECT")
        or os.getenv("LANGCHAIN_PROJECT")
        or default
    )


def tracing_context(project_name: str, tags: list[str] | None = None, metadata: dict[str, Any] | None = None):
    """Return a LangSmith tracing context manager or a no-op context."""
    if not is_langsmith_enabled():
        return nullcontext()

    return ls.tracing_context(
        enabled=True,
        project_name=project_name,
        tags=tags or [],
        metadata=metadata or {},
    )


def runnable_config(tags: list[str] | None = None, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build LangChain/LangGraph runnable config for tags and metadata."""
    config: dict[str, Any] = {}
    if tags:
        config["tags"] = tags
    if metadata:
        config["metadata"] = metadata
    return config
