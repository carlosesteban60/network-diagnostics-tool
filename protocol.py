"""
protocol.py
Shared TCP networking helpers and CLI argument validators for the
Network Diagnostics Tool.
"""

import argparse
import json
import socket
from typing import Any, Dict


def validate_port(port_str: str) -> int:
    """Validate that a CLI port argument is an integer between 1 and 65535."""
    try:
        port = int(port_str)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid port '{port_str}': must be an integer."
        ) from exc

    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError(
            f"Invalid port '{port}': must be between 1 and 65535."
        )
    return port


def send_json(sock: socket.socket, payload: Dict[str, Any]) -> None:
    """Serialize a dictionary as newline-delimited UTF-8 JSON and send it."""
    raw_data = (json.dumps(payload) + "\n").encode("utf-8")
    sock.sendall(raw_data)


def recv_json(sock: socket.socket, buffer_size: int = 4096) -> Dict[str, Any]:
    """Read bytes from a TCP socket until a newline and parse the JSON object."""
    chunks = []
    while True:
        chunk = sock.recv(buffer_size)
        if not chunk:
            raise ConnectionError("Connection closed by remote host.")
        chunks.append(chunk)
        if b"\n" in chunk:
            break

    line = b"".join(chunks).split(b"\n", 1)[0].decode("utf-8")
    return json.loads(line)