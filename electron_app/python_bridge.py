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
    get_recommendation,
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


def handle_model_recommend(symbol, indicators, close_price, indicator_data, fundamental_info, bull_comment, bear_comment):
    """Get LLM recommendation (fact-check + buy/sell/hold) based on all data."""
    try:
        result = get_recommendation(
            symbol.upper(),
            indicators,
            close_price,
            indicator_data,
            fundamental_info,
            bull_comment,
            bear_comment,
        )
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def handle_model_request(symbol, indicators, model_type, include_fundamental=False):
    """Get LLM bull/bear comment, returning auxiliary data for recommendation step."""
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

        # Fetch fundamentals if checkbox is checked
        fundamental_info = None
        if include_fundamental:
            try:
                fundamental_info = get_fundamentals(symbol.upper())
            except Exception:
                fundamental_info = "Error fetching fundamentals"

        # Call LLM
        if model_type == "bull":
            comment = get_bull_comment(symbol.upper(), indicators, close_price, extra_info, fundamental_info)
        else:
            comment = get_bear_comment(symbol.upper(), indicators, close_price, extra_info, fundamental_info)

        # Return a JSON object with comment + auxiliary data so the frontend
        # can pass everything to the recommendation step without re-fetching.
        result_data = json.dumps({
            "comment": comment,
            "close_price": close_price,
            "indicator_data": extra_info,
            "fundamental_info": fundamental_info,
        })
        return {"success": True, "data": result_data}
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
            include_fundamental = sys.argv[4].lower() == 'true' if len(sys.argv) > 4 else False
            result = handle_model_request(symbol, indicators, "bull", include_fundamental)

        elif command == "model_bear":
            if len(sys.argv) < 4:
                raise ValueError("Symbol and indicators required")
            symbol = sys.argv[2]
            indicators = json.loads(sys.argv[3])
            include_fundamental = sys.argv[4].lower() == 'true' if len(sys.argv) > 4 else False
            result = handle_model_request(symbol, indicators, "bear", include_fundamental)

        elif command == "model_recommend":
            # args: symbol, indicators_json, close_price, indicator_data, fundamental_info, bull_comment, bear_comment
            if len(sys.argv) < 8:
                raise ValueError("Symbol, indicators, close_price, indicator_data, fundamental_info, bull_comment, bear_comment required")
            symbol = sys.argv[2]
            indicators = json.loads(sys.argv[3])
            close_price = float(sys.argv[4]) if sys.argv[4] != 'None' else None
            indicator_data = sys.argv[5] if sys.argv[5] != 'None' else None
            fundamental_info = sys.argv[6] if sys.argv[6] != 'None' else None
            bull_comment = sys.argv[7] if sys.argv[7] != 'None' else None
            bear_comment = sys.argv[8] if len(sys.argv) > 8 and sys.argv[8] != 'None' else None

            result = handle_model_recommend(
                symbol, indicators, close_price, indicator_data,
                fundamental_info, bull_comment, bear_comment
            )

        else:
            result = {"success": False, "error": f"Unknown command: {command}"}

    except Exception as e:
        result = {"success": False, "error": str(e)}

    print(json.dumps(result))


if __name__ == '__main__':
    main()