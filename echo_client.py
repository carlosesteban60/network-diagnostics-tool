"""
echo_client.py (Student 3)
Latency client that sends multiple ECHO requests with unique identifiers,
matches replies, computes min/avg/max RTT, and reports timeouts separately.
"""

import argparse
import socket
import time
from typing import List
import uuid

from protocol import recv_json, send_json, validate_port


def measure_latency(
    host: str, port: int, count: int, message: str, timeout: float
) -> None:
    """Send 'count' ECHO requests and display RTT statistics and timeouts."""
    if count < 1:
        print("[ERROR] --count must be at least 1.")
        return

    rtts_ms: List[float] = []
    timeouts = 0

    try:
        sock = socket.create_connection((host, port), timeout=timeout)
    except socket.gaierror:
        print(f"Connection error: Could not resolve hostname '{host}'.")
        return
    except ConnectionRefusedError:
        print(f"Connection error: Connection refused by {host}:{port}.")
        return
    except (socket.timeout, TimeoutError):
        print(f"Connection timed out while connecting to {host}:{port}.")
        return
    except OSError as exc:
        print(f"Connection error: {exc}")
        return

    with sock:
        sock.settimeout(timeout)
        print(f"Sending {count} ECHO requests to {host}:{port}...\n")

        for seq in range(1, count + 1):
            req_id = f"req-{seq}-{uuid.uuid4().hex[:6]}"
            payload = {"type": "ECHO", "id": req_id, "message": message}

            try:
                start = time.perf_counter()
                send_json(sock, payload)
                reply = recv_json(sock)
                elapsed_ms = (time.perf_counter() - start) * 1000.0

                if (
                    reply.get("status") == "OK"
                    and reply.get("id") == req_id
                    and reply.get("message") == message
                ):
                    rtts_ms.append(elapsed_ms)
                    print(
                        f"[{seq}/{count}] id={req_id} -> Reply matched | RTT = {elapsed_ms:.3f} ms"
                    )
                else:
                    print(f"[{seq}/{count}] id={req_id} -> Mismatched reply: {reply}")
            except (socket.timeout, TimeoutError):
                timeouts += 1
                print(f"[{seq}/{count}] id={req_id} -> Request timed out")
            except OSError as exc:
                print(f"[{seq}/{count}] id={req_id} -> Socket error: {exc}")
                break

    print("\n--- Latency Summary ---")
    print(f"Sent: {count} | Successful: {len(rtts_ms)} | Timeouts: {timeouts}")
    if rtts_ms:
        min_rtt = min(rtts_ms)
        avg_rtt = sum(rtts_ms) / len(rtts_ms)
        max_rtt = max(rtts_ms)
        print(
            f"RTT (ms): Min = {min_rtt:.3f} ms | Avg = {avg_rtt:.3f} ms | Max = {max_rtt:.3f} ms"
        )
    else:
        print("RTT (ms): No successful replies to calculate statistics.")


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the latency client."""
    parser = argparse.ArgumentParser(
        description="Latency Client (ECHO)",
        epilog="Example: python echo_client.py --host 127.0.0.1 --port 5050 --count 5",
    )
    parser.add_argument("--host", required=True, help="Target server IP or hostname")
    parser.add_argument(
        "--port", type=validate_port, required=True, help="Target server TCP port"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of ECHO requests to send (default: 5)",
    )
    parser.add_argument(
        "--message",
        default="Hello Network Diagnostics",
        help="Payload text to echo (default: 'Hello Network Diagnostics')",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=2.0,
        help="Per-request timeout in seconds (default: 2.0)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    measure_latency(
        host=args.host,
        port=args.port,
        count=args.count,
        message=args.message,
        timeout=args.timeout,
    )