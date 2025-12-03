import os
import subprocess  # nosec[B404]
import threading
import time
from typing import Generator

from event_router import route_event

SERVERS_BASE = "/servers"


def discover_servers():
    servers = {}
    for uuid in get_uuids():
        server_dir = os.path.join(SERVERS_BASE, uuid)
        if not os.path.isdir(server_dir):
            continue

        name = read_server_name(os.path.join(server_dir, "server.properties"))
        log_file = os.path.join(server_dir, "logs/latest.log")

        servers[uuid] = {
            "name": name,
            "log_file": log_file,
        }

    return servers


def get_uuids() -> list[str]:
    return [
        entry
        for entry in os.listdir(SERVERS_BASE)
        if os.path.isdir(os.path.join(SERVERS_BASE, entry))
    ]


def read_server_name(properties_path: str) -> str:
    name = "Unknown"
    try:
        with open(properties_path, "r") as f:
            for line in f:
                if line.startswith("server-name="):
                    name = line.split("=", 1)[1].strip()
                    break
    except FileNotFoundError:
        pass

    return name


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
