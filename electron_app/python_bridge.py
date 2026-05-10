#!/usr/bin/env python3
"""Python bridge for Electron IPC communication.
Handles requests from Electron main process via command line arguments.
"""

import sys
import json
import os
from datetime import datetime

# Add project root to path
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(pathlib.Path(__file__).resolve().parents[1], '.env'))

from tradingyourmodel.dataflows.y_finance import (
    get_fundamentals,
    get_stock_stats_indicators_window
)
from tradingyourmodel.llm.clients.openrouter_client import (
    get_bull_comment,
    get_bear_comment,
)
import yfinance as yf


def handle_get_fundamentals(symbol):
    """Get stock fundamentals."""
    try:
        result = get_fundamentals(symbol.upper())
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def handle_get_indicator(symbol, indicator, curr_date=None, look_back_days=30):
    """Get stock indicator data."""
    try:
        if curr_date is None:
            curr_date = datetime.now().strftime('%Y-%m-%d')
        result = get_stock_stats_indicators_window(
            symbol.upper(), indicator, curr_date, look_back_days
        )
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def handle_model_request(symbol, indicators, model_type):
    """Get LLM bull/bear comment."""
    try:
        # Get latest close price
        ticker = yf.Ticker(symbol.upper())
        hist = ticker.history(period='1d')
        close_price = None
        if not hist.empty:
            close_price = float(hist['Close'].iloc[-1])

        # Gather indicator data
        today = datetime.now().strftime('%Y-%m-%d')
        indicator_results = []
        for ind in indicators:
            try:
                res = get_stock_stats_indicators_window(symbol.upper(), ind, today, 30)
                indicator_results.append(f"{ind}: {res}")
            except Exception:
                indicator_results.append(f"{ind}: Error fetching data")

        # Prepare extra info string for LLM
        extra_info = " | ".join(indicator_results)

        # Call LLM
        if model_type == "bull":
            comment = get_bull_comment(symbol.upper(), indicators, close_price, extra_info)
        else:
            comment = get_bear_comment(symbol.upper(), indicators, close_price, extra_info)

        return {"success": True, "data": comment}
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    """Handle command-line request."""
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No command provided"}))
        sys.exit(1)

    command = sys.argv[1]
    result = None

    try:
        if command == "get_fundamentals":
            if len(sys.argv) < 3:
                raise ValueError("Symbol required")
            result = handle_get_fundamentals(sys.argv[2])

        elif command == "get_indicator":
            if len(sys.argv) < 4:
                raise ValueError("Symbol and indicator required")
            symbol = sys.argv[2]
            indicator = sys.argv[3]
            curr_date = sys.argv[4] if len(sys.argv) > 4 else None
            look_back = int(sys.argv[5]) if len(sys.argv) > 5 else 30
            result = handle_get_indicator(symbol, indicator, curr_date, look_back)

        elif command == "model_bull":
            if len(sys.argv) < 4:
                raise ValueError("Symbol and indicators required")
            symbol = sys.argv[2]
            indicators = json.loads(sys.argv[3])
            result = handle_model_request(symbol, indicators, "bull")

        elif command == "model_bear":
            if len(sys.argv) < 4:
                raise ValueError("Symbol and indicators required")
            symbol = sys.argv[2]
            indicators = json.loads(sys.argv[3])
            result = handle_model_request(symbol, indicators, "bear")

        else:
            result = {"success": False, "error": f"Unknown command: {command}"}

    except Exception as e:
        result = {"success": False, "error": str(e)}

    print(json.dumps(result))


if __name__ == '__main__':
    main()