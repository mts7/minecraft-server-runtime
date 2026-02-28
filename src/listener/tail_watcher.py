import subprocess  # nosec[B404]
import threading
import time
from typing import Generator

from src.listener.event_router import route_event
from src.utility.deduplicator import MessageDeduplicator
from src.utility.server_discovery import discover_servers


def tail_log(path: str) -> Generator[str, None, None]:
    """Generator that yields lines from a log file as they are appended."""
    print(f"[tail] Watching {path}")
    proc = subprocess.Popen(  # nosec[B603]
        ["/usr/bin/tail", "-n", "0", "-F", path],
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    if proc.stdout:
        for line in proc.stdout:
            yield line.rstrip("\n")


def watch_server(name: str, log_path: str):
    """Watch a server's log file and route events, with deduplication."""
    deduplicator = MessageDeduplicator(window_seconds=30)

    for line in tail_log(log_path):
        if deduplicator.is_unique(line):
            route_event(name, line)


def main():
    """Main function to start watching all discovered servers."""
    servers = discover_servers()
    for uuid, info in servers.items():
        thread = threading.Thread(
            target=watch_server,
            args=(info["name"], info["log_file"]),
            daemon=True
        )
        thread.start()
        print(f"Started watching server {info['name']}")

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Stopping log watchers...")


if __name__ == "__main__":
    main()
