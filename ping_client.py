"""
ping_client.py (Student 2)
Reachability client that sends a PING request to the diagnostics server
and reports Reachable, No response, or a connection error.
"""

import argparse
import socket

from protocol import recv_json, send_json, validate_port


def check_reachability(host: str, port: int, timeout: float) -> None:
    """Connect to the server, send PING, and print reachability status."""
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            sock.settimeout(timeout)
            send_json(sock, {"type": "PING"})
            reply = recv_json(sock)

            if reply.get("status") == "OK" and reply.get("message") == "PONG":
                print("Reachable")
            else:
                print(f"Unexpected response from server: {reply}")
    except (socket.timeout, TimeoutError):
        print("No response")
    except socket.gaierror:
        print(f"Connection error: Could not resolve hostname '{host}'.")
    except ConnectionRefusedError:
        print(f"Connection error: Connection refused by {host}:{port}.")
    except OSError as exc:
        print(f"Connection error: {exc}")


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the reachability client."""
    parser = argparse.ArgumentParser(
        description="Reachability Client (PING)",
        epilog="Example: python ping_client.py --host 127.0.0.1 --port 5050",
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
    check_reachability(host=args.host, port=args.port, timeout=args.timeout)