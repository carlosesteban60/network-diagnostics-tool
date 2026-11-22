"""
server.py (Student 1)
Multithreaded TCP Diagnostics Server supporting PING, ECHO, and STATS commands
with thread-safe request counting and timestamped file logging.
"""

import argparse
from datetime import datetime, timezone
import json
import socket
import threading
import time
from typing import Any, Dict, Tuple

from protocol import recv_json, send_json, validate_port


class DiagnosticsServer:
    """Concurrent TCP server for network reachability, latency, and stats."""

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.start_time = time.monotonic()
        self.completed_requests = 0
        self.lock = threading.Lock()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_filename = f"diagnostics_server_{timestamp}.log"
        self._init_log_file()

    def _init_log_file(self) -> None:
        """Create the timestamped log file and write a startup header."""
        try:
            with open(self.log_filename, "w", encoding="utf-8") as log_file:
                log_file.write(
                    f"# Diagnostics Server Log - Started {datetime.now(timezone.utc).isoformat()}\n"
                )
        except OSError as exc:
            print(f"[ERROR] Could not initialize log file '{self.log_filename}': {exc}")
            raise

    def log_event(self, client_addr: Tuple[str, int], command: str, outcome: str) -> None:
        """Safely append a timestamped request record to the log file."""
        ts = datetime.now(timezone.utc).isoformat()
        entry = f"[{ts}] client={client_addr[0]}:{client_addr[1]} command={command} outcome={outcome}\n"
        try:
            with self.lock:
                with open(self.log_filename, "a", encoding="utf-8") as log_file:
                    log_file.write(entry)
        except OSError as exc:
            print(f"[ERROR] Failed to write to log file: {exc}")

    def process_request(self, request: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """Process a single parsed command dictionary and return (response, outcome)."""
        cmd = str(request.get("type", "")).upper()

        if cmd == "PING":
            with self.lock:
                self.completed_requests += 1
            return {"status": "OK", "type": "PING", "message": "PONG"}, "SUCCESS (PONG)"

        if cmd == "ECHO":
            req_id = request.get("id", "")
            message = request.get("message", "")
            with self.lock:
                self.completed_requests += 1
            return (
                {
                    "status": "OK",
                    "type": "ECHO",
                    "id": req_id,
                    "message": message,
                },
                f"SUCCESS (id={req_id})",
            )

        if cmd == "STATS":
            with self.lock:
                count_snapshot = self.completed_requests
                self.completed_requests += 1
            uptime = round(time.monotonic() - self.start_time, 2)
            return (
                {
                    "status": "OK",
                    "type": "STATS",
                    "uptime_seconds": uptime,
                    "completed_requests": count_snapshot,
                },
                f"SUCCESS (uptime={uptime}s, completed={count_snapshot})",
            )

        return (
            {"status": "ERROR", "message": f"Unsupported command '{cmd}'"},
            f"ERROR (Unsupported command '{cmd}')",
        )

    def handle_client(self, conn: socket.socket, addr: Tuple[str, int]) -> None:
        """Handle all requests from a connected client in a dedicated thread."""
        with conn:
            while True:
                try:
                    request = recv_json(conn)
                except ConnectionError:
                    break
                except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                    self.log_event(addr, "MALFORMED", f"ERROR ({exc})")
                    break
                except OSError as exc:
                    self.log_event(addr, "SOCKET_ERROR", f"ERROR ({exc})")
                    break

                cmd = str(request.get("type", "UNKNOWN")).upper()
                response, outcome = self.process_request(request)
                self.log_event(addr, cmd, outcome)
                print(f"[{addr[0]}:{addr[1]}] {cmd} -> {outcome}")

                try:
                    send_json(conn, response)
                except OSError as exc:
                    self.log_event(addr, cmd, f"SEND_FAILED ({exc})")
                    break

    def start(self) -> None:
        """Bind to the configured TCP socket and spawn a thread per client."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                server_sock.bind((self.host, self.port))
            except OSError as exc:
                print(f"[ERROR] Failed to bind to {self.host}:{self.port} -> {exc}")
                return

            server_sock.listen()
            print(f"[*] Diagnostics Server listening on {self.host}:{self.port}")
            print(f"[*] Logging requests to: {self.log_filename}")
            print("[*] Press Ctrl+C to stop the server.\n")

            try:
                while True:
                    conn, addr = server_sock.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(conn, addr),
                        daemon=True,
                    )
                    client_thread.start()
            except KeyboardInterrupt:
                print("\n[*] Server shutting down cleanly.")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the diagnostics server."""
    parser = argparse.ArgumentParser(
        description="Multithreaded Network Diagnostics Server",
        epilog="Example: python server.py --host 127.0.0.1 --port 5050",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="IP address or hostname to bind to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=validate_port,
        default=5050,
        help="TCP port to listen on (1-65535, default: 5050)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    server = DiagnosticsServer(host=args.host, port=args.port)
    server.start()