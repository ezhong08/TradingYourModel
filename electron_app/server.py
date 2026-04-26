#!/usr/bin/env python3
"""Simple HTTP server to expose TradingYourModel dataflows to Electron app."""

import sys
import json
from dotenv import load_dotenv
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta

# Add project root directory to sys.path for imports
import pathlib
# Resolve the directory two levels up (project root) and prepend it to sys.path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

# Load environment variables from .env at project root
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
import json


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/fundamentals/'):
            symbol = self.path.split('/')[-1]
            try:
                result = get_fundamentals(symbol.upper())
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(result.encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"Error: {e}".encode())

        elif self.path.startswith('/indicator/'):
            parts = self.path.split('/')
            symbol = parts[2]
            indicator = parts[3] if len(parts) > 3 else 'rsi'
            try:
                today = datetime.now().strftime('%Y-%m-%d')
                result = get_stock_stats_indicators_window(symbol.upper(), indicator, today, 30)
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(result.encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"Error: {e}".encode())

        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_POST(self):
        # Expect JSON body with {symbol, indicators}
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode()
        try:
            data = json.loads(body)
        except Exception:
            self.send_response(400)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
        if self.path == '/model/bull' or self.path == '/model/bear':
            try:
                # Get latest close price
                symbol = data.get('symbol', '').upper()
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='1d')
                close_price = None
                if not hist.empty:
                    close_price = hist['Close'].iloc[-1]
                # Get LLM comment with close price
                if self.path == '/model/bull':
                    comment = get_bull_comment(symbol, data.get('indicators', []), close_price)
                else:
                    comment = get_bear_comment(symbol, data.get('indicators', []), close_price)

                # Gather indicator data for the selected indicators
                symbol = data.get('symbol', '').upper()
                indicators = data.get('indicators', [])
                today = datetime.now().strftime('%Y-%m-%d')
                indicator_results = []
                for ind in indicators:
                    try:
                        res = get_stock_stats_indicators_window(symbol, ind, today, 30)
                        indicator_results.append(f"{ind}: {res}")
                    except Exception as ie:
                        indicator_results.append(f"{ind}: Error fetching data")
                # Prepare extra info string for LLM
                extra_info = " | ".join(indicator_results)
                # Call LLM with extra indicator info
                if self.path == '/model/bull':
                    comment = get_bull_comment(symbol, indicators, close_price, extra_info)
                else:
                    comment = get_bear_comment(symbol, indicators, close_price, extra_info)
                # Return only the comment without indicator data
                full_response = comment # + "\n\nIndicator Data:\n" + "\n".join(indicator_results)
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(full_response.encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"Error: {e}".encode())
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server(port=8765):
    server = HTTPServer(('localhost', port), RequestHandler)
    print(f"TradingYourModel API server running on http://localhost:{port}")
    server.serve_forever()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    run_server(args.port)