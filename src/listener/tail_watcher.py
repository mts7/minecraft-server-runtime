import subprocess  # nosec[B404]
import time
from typing import Generator

from event_router import route_event
from server_discovery import discover_servers


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


def update_watched_tails(watched_tails: dict[str, Generator[str, None, None]]):
    """
    Perform one iteration of server discovery and tailing.

    - Adds new servers
    - Removes deleted servers
    - Yields new log lines to route_event
    """
    servers = discover_servers()
    current_uuids = set(servers.keys())
    watched_uuids = set(watched_tails.keys())

    # Start new tail generators
    for uuid in current_uuids - watched_uuids:
        info = servers[uuid]
        print(f"[tail] Starting watcher for {info['name']} ({uuid})")
        watched_tails[uuid] = tail_log(info["log_file"])

    # Remove deleted servers
    for uuid in watched_uuids - current_uuids:
        print(f"[tail] Stopping watcher for {uuid}")
        del watched_tails[uuid]

    # Read lines from active tails
    for uuid, gen in watched_tails.items():
        info = servers[uuid]
        try:
            while True:
                line = next(gen)
                route_event(info["name"], line)
        except StopIteration:
            pass


def main():
    watched_tails: dict[str, Generator[str, None, None]] = {}
    while True:
        update_watched_tails(watched_tails)
        time.sleep(1)


if __name__ == "__main__":
    main()
