"""
agent/canonical_guard.py
Read-only enforcement for Track A.

The agent layer is strictly read-only against canonical tables.
Provides:
  - canonical_read_only — decorator for regular and async functions
  - CanonicalWriteForbidden — HTTP 403 exception
  - require_read_only — FastAPI dependency hook

Decorator rejects async generators at decoration time (they cannot be wrapped
by this pattern). For async generators, apply read-only enforcement at the
router level instead.
"""

from __future__ import annotations

import functools
import inspect
from typing import Any, Callable

from fastapi import HTTPException, Request, status


class CanonicalWriteForbidden(HTTPException):
    """Raised when a write attempt is made against canonical state."""

    def __init__(self, detail: str = "canonicalWrite is disabled on this endpoint"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


def _reject_if_write(kwargs: dict) -> None:
    """Raise if kwargs signal a write attempt."""
    if kwargs.get("write") is True:
        raise CanonicalWriteForbidden("Write flag detected")
    if kwargs.get("canonical_write") is True:
        raise CanonicalWriteForbidden("canonical_write flag detected")


def canonical_read_only(func: Callable) -> Callable:
    """
    Decorator: reject any invocation that signals a write.

    Works for regular functions and async coroutines.
    Raises TypeError at decoration time for async generators, which cannot
    be wrapped safely by this pattern.
    """
    if inspect.isasyncgenfunction(func):
        raise TypeError(
            "canonical_read_only cannot decorate an async generator. "
            "Apply read-only enforcement at the router level instead."
        )

    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            _reject_if_write(kwargs)
            return await func(*args, **kwargs)
        return async_wrapper

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        _reject_if_write(kwargs)
        return func(*args, **kwargs)

    return sync_wrapper


async def require_read_only(request: Request) -> None:
    """
    FastAPI dependency: read-only enforcement hook.

    Currently a no-op reserved for future write-signal rejection middleware.
    """
    return None


if __name__ == "__main__":
    @canonical_read_only
    def read_op(x: int) -> int:
        return x * 2

    assert read_op(5) == 10

    try:
        read_op(5, write=True)
        raise AssertionError("Expected CanonicalWriteForbidden")
    except CanonicalWriteForbidden:
        pass

    try:
        read_op(5, canonical_write=True)
        raise AssertionError("Expected CanonicalWriteForbidden")
    except CanonicalWriteForbidden:
        pass

    import asyncio

    @canonical_read_only
    async def async_read_op(x: int) -> int:
        return x + 1

    assert asyncio.run(async_read_op(9)) == 10

    async def run_reject():
        try:
            await async_read_op(9, write=True)
            raise AssertionError("Expected CanonicalWriteForbidden")
        except CanonicalWriteForbidden:
            pass

    asyncio.run(run_reject())

    # Async generators must be rejected at decoration time
    try:
        @canonical_read_only
        async def gen():
            yield 1
        raise AssertionError("Expected TypeError for async generator")
    except TypeError:
        pass

    print("canonical_guard.py OK")