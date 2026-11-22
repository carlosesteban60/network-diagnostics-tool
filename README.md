# Network Diagnostics Tool (Course 605346 - Phase 1)

A multithreaded Python command-line client-server network diagnostics application built using raw TCP sockets.

## Team Members
| Student 1 | Multithreaded Server (`server.py`) | Yassin |
| Student 2 | Reachability Client (`ping_client.py`) | Mohammad |
| Student 3 | Latency Client (`echo_client.py`) | Haitham |
| Student 4 | Server Activity Client (`stats_client.py`) | Husam |

## Setup Instructions
- **Requirements:** Python 3.8 or higher. No third-party packages are needed (see `requirements.txt`).
- Clone or extract the repository and open a terminal inside the project directory.

## Example Commands
1. **Start the Server (Terminal 1):**
   ```bash
   python3 server.py --host 127.0.0.1 --port 5050