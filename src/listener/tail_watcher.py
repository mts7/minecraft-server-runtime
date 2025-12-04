import subprocess  # nosec[B404]
import threading
import time
from typing import Generator

from event_router import route_event

from src.utility.server_discovery import discover_servers


def tail_log(path: str) -> Generator[str, None, None]:
    print(f"[tail] Watching {path}")
    proc = subprocess.Popen(  # nosec[B603]
        ["/usr/bin/tail", "-n", "0", "-F", path],
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    for line in proc.stdout:
        yield line.rstrip("\n")


def watch_server(name: str, log_path: str):
    for line in tail_log(log_path):
        route_event(name, line)


def main():
    servers = discover_servers()
    for uuid, info in servers.items():
        threading.Thread(
            target=watch_server,
            args=(info["name"], info["log_file"]),
            daemon=True
        ).start()

    while True:
        time.sleep(10)


if __name__ == "__main__":
    main()
