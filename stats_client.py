"""
stats_client.py (Student 4)
Server activity client that retrieves and displays server uptime and
completed request count.
"""

import argparse
import socket

from protocol import recv_json, send_json, validate_port


def fetch_stats(host: str, port: int, timeout: float) -> None:
    """Request STATS from the server and display uptime and request count."""
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            sock.settimeout(timeout)
            send_json(sock, {"type": "STATS"})
            reply = recv_json(sock)

            if reply.get("status") == "OK":
                uptime = reply.get("uptime_seconds", 0.0)
                completed = reply.get("completed_requests", 0)
                print("--- Server Activity Stats ---")
                print(f"Server Uptime      : {uptime} seconds")
                print(f"Completed Requests : {completed}")
            else:
                print(f"Server returned an error: {reply}")
    except (socket.timeout, TimeoutError):
        print("Connection timed out while waiting for server stats.")
    except socket.gaierror:
        print(f"Connection error: Could not resolve hostname '{host}'.")
    except ConnectionRefusedError:
        print(f"Connection error: Connection refused by {host}:{port}.")
    except OSError as exc:
        print(f"Connection error: {exc}")


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the server activity client."""
    parser = argparse.ArgumentParser(
        description="Server Activity Client (STATS)",
        epilog="Example: python stats_client.py --host 127.0.0.1 --port 5050",
    )
    parser.add_argument("--host", required=True, help="Target server IP or hostname")
    parser.add_argument(
        "--port", type=validate_port, required=True, help="Target server TCP port"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=3.0,
        help="Socket timeout in seconds (default: 3.0)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    fetch_stats(host=args.host, port=args.port, timeout=args.timeout)