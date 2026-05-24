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
import sys
import json
import urllib.request
from typing import List, Optional

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

def _build_prompt(symbol: str, indicators: List[str], sentiment: str, close_price: float = None, extra_info: str = None, fundamental_info: str = None) -> str:
    """Create a prompt describing the request.

    Parameters
    ----------
    symbol: str
        Stock ticker symbol.
    indicators: List[str]
        List of indicator names selected by the user.
    sentiment: str
        Either "bull" or "bear" – determines the tone of the analysis.
    close_price: float, optional
        Latest close price.
    extra_info: str, optional
        Additional technical indicator data.
    fundamental_info: str, optional
        Stock fundamental data.
    """
    ind_list = ", ".join(indicators) if indicators else "none"
    price_part = f" The latest close price is {close_price:.2f}." if close_price is not None else ""
    extra_part = f" Additional indicator data: {extra_info}." if extra_info else ""
    fundamental_part = f" Company fundamentals: {fundamental_info}." if fundamental_info else ""
    return (
        f"You are a financial analyst. Provide a concise {sentiment.upper()} "
        f"comment for the stock {symbol.upper()} based on the following technical "
        f"indicators: {ind_list}.{price_part}{extra_part}{fundamental_part} Only return the comment without any extra "
        "explanations."
    )

def get_bull_comment(symbol: str, indicators: List[str], close_price: float = None, extra_info: str = None, fundamental_info: str = None) -> str:
    """Return a bullish comment for the given symbol and indicators.

    This function builds a system prompt that asks the model to act bullish.
    """
    system_prompt = "You are a bullish financial analyst."
    user_prompt = _build_prompt(symbol, indicators, "bull", close_price, extra_info, fundamental_info)
    # sys.stderr.write(user_prompt + "\n")
    payload = {
        # "model" will be injected in _post() from the OPENROUTER_MODEL env var if not provided
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    return _post(payload)

def get_bear_comment(symbol: str, indicators: List[str], close_price: float = None, extra_info: str = None, fundamental_info: str = None) -> str:
    """Return a bearish comment for the given symbol and indicators.
    """
    system_prompt = "You are a bearish financial analyst."
    user_prompt = _build_prompt(symbol, indicators, "bear", close_price, extra_info, fundamental_info)
    payload = {
        # "model" will be injected in _post() from the OPENROUTER_MODEL env var if not provided
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    return _post(payload)


def get_recommendation(
    symbol: str,
    indicators: List[str],
    close_price: float = None,
    indicator_data: str = None,
    fundamental_info: str = None,
    bull_comment: str = None,
    bear_comment: str = None,
) -> str:
    """Fact-check the bull and bear comments and produce a final buy/sell/hold recommendation.

    Parameters
    ----------
    symbol: str
        Stock ticker symbol.
    indicators: List[str]
        List of indicator names selected by the user.
    close_price: float, optional
        Latest close price.
    indicator_data: str, optional
        Raw technical indicator data.
    fundamental_info: str, optional
        Stock fundamental data.
    bull_comment: str, optional
        The bullish analysis from the LLM.
    bear_comment: str, optional
        The bearish analysis from the LLM.

    Returns
    -------
    str
        The recommendation (fact-check analysis + buy/sell/hold decision).
    """
    system_prompt = (
        "You are a neutral, impartial financial analyst. Your task is to:\n"
        "1. Review the bullish and bearish analyses provided.\n"
        "2. Fact-check each claim against the actual technical indicator data "
        "and company fundamentals (if provided).\n"
        "3. Point out any logical errors, exaggerations, or unsupported statements.\n"
        "4. Based on all available evidence, make a final recommendation: "
        "BUY, SELL, or HOLD.\n\n"
        "Output format:\n"
        "=== Fact Check ===\n"
        "[Bullet points with fact-checking findings]\n\n"
        "=== Recommendation ===\n"
        "[BUY/SELL/HOLD] - [Brief reason for the decision]"
    )

    ind_list = ", ".join(indicators) if indicators else "none"
    price_part = f"The latest close price is {close_price:.2f}." if close_price is not None else ""
    indicator_part = f"\n\nTechnical indicator data:\n{indicator_data}" if indicator_data else ""
    fundamental_part = f"\n\nCompany fundamentals:\n{fundamental_info}" if fundamental_info else ""
    bull_part = f"\n\nBullish analysis:\n{bull_comment}" if bull_comment else ""
    bear_part = f"\n\nBearish analysis:\n{bear_comment}" if bear_comment else ""

    user_prompt = (
        f"Stock: {symbol.upper()}\n"
        f"Selected indicators: {ind_list}\n"
        f"{price_part}"
        f"{indicator_part}"
        f"{fundamental_part}"
        f"{bull_part}"
        f"{bear_part}"
    )

    sys.stderr.write(f"\n=== Recommendation prompt ===\n{user_prompt}\n")

    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    return _post(payload)