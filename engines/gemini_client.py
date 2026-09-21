"""
engines/gemini_client.py
Wrapper around the google-genai SDK for gemini-3.8-flash.

Environment:
  - GEMINI_API_KEY: required (mounted from Secret Manager in production)
  - MODEL_NAME: optional override (default: gemini-3.8-flash)
"""

from __future__ import annotations

import os
from typing import AsyncIterator, Optional

try:
    from google import genai
    from google.genai import types
except ImportError as e:
    raise ImportError(
        "google-genai package not installed. Run: pip install google-genai"
    ) from e


_DEFAULT_MODEL = "gemini-3.8-flash"


class GeminiClientError(RuntimeError):
    """Raised when the Gemini client cannot be initialized or fails."""


class GeminiClient:
    """
    Async-capable wrapper for gemini-3.8-flash.
    """

    def __init__(self, api_key: Optional[str] = None):
        key = api_key or os.environ.get("GEMINI_API_KEY", "").strip()
        if not key:
            raise GeminiClientError(
                "GEMINI_API_KEY is not set. Set it in the environment "
                "or pass it explicitly to GeminiClient(api_key=...)."
            )
        self._client = genai.Client(api_key=key)
        self._model = os.environ.get("MODEL_NAME", _DEFAULT_MODEL)

    @property
    def model(self) -> str:
        return self._model

    async def generate(
        self,
        system_instruction: str,
        user_prompt: str,
        max_output_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        """Generate text in a single round trip."""
        try:
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    max_output_tokens=max_output_tokens,
                    temperature=temperature,
                ),
            )
            return response.text or ""
        except Exception as e:
            raise GeminiClientError(f"Generation failed: {e}") from e

    async def stream(
        self,
        system_instruction: str,
        user_prompt: str,
        max_output_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream generated text as an async iterator of chunks."""
        try:
            async for chunk in await self._client.aio.models.generate_content_stream(
                model=self._model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    max_output_tokens=max_output_tokens,
                    temperature=temperature,
                ),
            ):
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            raise GeminiClientError(f"Streaming failed: {e}") from e


if __name__ == "__main__":
    assert _DEFAULT_MODEL == "gemini-3.8-flash"

    original = os.environ.pop("GEMINI_API_KEY", None)
    try:
        try:
            GeminiClient()
            raise AssertionError("Expected GeminiClientError for missing key")
        except GeminiClientError:
            pass
    finally:
        if original:
            os.environ["GEMINI_API_KEY"] = original

    try:
        client = GeminiClient(api_key="test-key-not-real")
        assert client.model == _DEFAULT_MODEL
    except Exception as e:
        raise AssertionError(f"Construction failed: {e}")

    print("gemini_client.py OK")