"""OpenRouter client for LLM model analysis.

Provides two simple helper functions that send a POST request to the OpenRouter
API to obtain a *Bull* and *Bear* comment for a given stock symbol and a list of
technical indicators. The implementation is intentionally lightweight – it
focuses on constructing the request payload, handling the API key, and returning
the raw text response.

The client expects the environment variable ``OPENROUTER_API_KEY`` to be set.
If the variable is missing, the functions raise a clear ``RuntimeError`` so the
caller can handle the situation (e.g., fallback to a placeholder response).

Both functions share the same underlying request logic; the only difference is
the ``system`` prompt that guides the model to produce a bullish or bearish
analysis.
"""

import os
import json
import urllib.request
from typing import List

# OpenRouter endpoint – using the chat completions API
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

def _get_api_key() -> str:
    """Retrieve the OpenRouter API key from the environment.

    Returns
    -------
    str
        The API key.
    Raises
    ------
    RuntimeError
        If the ``OPENROUTER_API_KEY`` variable is not defined.
    """
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY environment variable not set")
    return key

def _post(payload: dict) -> str:
    """Send a JSON payload to OpenRouter and return the assistant's reply.

    Parameters
    ----------
    payload: dict
        The JSON body as defined by the OpenRouter chat completions API.

    Returns
    -------
    str
        The content of the assistant's message.
    """
    # Ensure the model field is present before serialising the payload
    model = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
    payload.setdefault("model", model)
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {_get_api_key()}",
            "HTTP-Referer": "https://github.com/ezhong08/TradingYourModel",
        },
    )
    with urllib.request.urlopen(req) as resp:
        resp_data = json.load(resp)
    # Extract the assistant message content
    return resp_data["choices"][0]["message"]["content"].strip()

def _build_prompt(symbol: str, indicators: List[str], sentiment: str, close_price: float = None, extra_info: str = None) -> str:
    """Create a prompt describing the request.

    Parameters
    ----------
    symbol: str
        Stock ticker symbol.
    indicators: List[str]
        List of indicator names selected by the user.
    sentiment: str
        Either "bull" or "bear" – determines the tone of the analysis.
    """
    ind_list = ", ".join(indicators) if indicators else "none"
    price_part = f" The latest close price is {close_price:.2f}." if close_price is not None else ""
    extra_part = f" Additional indicator data: {extra_info}." if extra_info else ""
    return (
        f"You are a financial analyst. Provide a concise {sentiment.upper()} "
        f"comment for the stock {symbol.upper()} based on the following technical "
        f"indicators: {ind_list}.{price_part}{extra_part} Only return the comment without any extra "
        "explanations."
    )

def get_bull_comment(symbol: str, indicators: List[str], close_price: float = None, extra_info: str = None) -> str:
    """Return a bullish comment for the given symbol and indicators.

    This function builds a system prompt that asks the model to act bullish.
    """
    system_prompt = "You are a bullish financial analyst."
    user_prompt = _build_prompt(symbol, indicators, "bull", close_price, extra_info)
    payload = {
        # "model" will be injected in _post() from the OPENROUTER_MODEL env var if not provided
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    return _post(payload)

def get_bear_comment(symbol: str, indicators: List[str], close_price: float = None, extra_info: str = None) -> str:
    """Return a bearish comment for the given symbol and indicators.
    """
    system_prompt = "You are a bearish financial analyst."
    user_prompt = _build_prompt(symbol, indicators, "bear", close_price, extra_info)
    payload = {
        # "model" will be injected in _post() from the OPENROUTER_MODEL env var if not provided
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    return _post(payload)
