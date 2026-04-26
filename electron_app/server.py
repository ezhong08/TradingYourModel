#!/usr/bin/env python3
"""Simple HTTP server to expose TradingYourModel dataflows to Electron app."""

import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])

from tradingyourmodel.dataflows.y_finance import (
    get_fundamentals,
    get_stock_stats_indicators_window
)


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
